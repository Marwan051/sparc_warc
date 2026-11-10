"""Create the partial HNSW index for the active embedding version.

Exact search works without an index. Approximate search (RAG_APPROXIMATE_SEARCH=1)
needs an HNSW index whose predicate matches the query's version filters. Run
this once after a chunking or embedding version change, then again whenever
retrieval starts using a new version.
"""

import argparse
import hashlib
from pathlib import Path

from psycopg2 import sql

from db.db_handler import get_connection
from jobs.environment import load_environment
from retrieval.store import RetrievalConfig


def index_name(config: RetrievalConfig) -> str:
    identity = "|".join((
        config.chunking_version,
        config.embedding_model,
        config.embedding_version,
    ))
    digest = hashlib.sha256(identity.encode()).hexdigest()[:12]
    return f"idx_chunk_embeddings_active_{digest}"


PARTIAL_PREFIX = "idx_chunk_embeddings_active_"


def stale_indexes(conn, keep: str) -> list[str]:
    with conn.cursor() as cur:
        cur.execute(
            """SELECT c.relname
               FROM pg_class c
               JOIN pg_namespace n ON n.oid = c.relnamespace
               WHERE c.relkind = 'i'
                 AND n.nspname = current_schema()
                 AND c.relname LIKE %s
                 AND c.relname <> %s
               ORDER BY c.relname""",
            (PARTIAL_PREFIX + "%", keep),
        )
        return [row[0] for row in cur.fetchall()]


def drop_index(conn, name: str, dry_run: bool = False) -> None:
    statement = sql.SQL("DROP INDEX CONCURRENTLY IF EXISTS {}").format(sql.Identifier(name))
    if dry_run:
        print(statement.as_string(conn))
        return
    with conn.cursor() as cur:
        cur.execute(statement)


def ensure_index(conn, config: RetrievalConfig, dry_run: bool = False) -> tuple[str, bool]:
    """Create the index if it is missing. Returns (name, created)."""
    name = index_name(config)
    # CREATE INDEX CONCURRENTLY cannot run inside a transaction block.
    conn.rollback()
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(
            """SELECT i.indisvalid, opc.opcname
               FROM pg_index i
               JOIN pg_class c ON c.oid = i.indexrelid
               JOIN pg_namespace n ON n.oid = c.relnamespace
               JOIN pg_opclass opc ON opc.oid = i.indclass[0]
               WHERE c.relname = %s AND n.nspname = current_schema()""",
            (name,),
        )
        existing = cur.fetchone()
        if existing is not None and existing[0] and existing[1] == "vector_cosine_ops":
            return name, False
        statement = sql.SQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS {} ON chunk_embeddings "
            "USING hnsw (embedding vector_cosine_ops) "
            "WHERE chunking_version = {} AND embedding_model = {} "
            "AND embedding_version = {}"
        ).format(
            sql.Identifier(name),
            sql.Literal(config.chunking_version),
            sql.Literal(config.embedding_model),
            sql.Literal(config.embedding_version),
        )
        if dry_run:
            print(statement.as_string(conn))
            return name, False
        if existing is not None:
            # A failed concurrent build leaves an invalid index behind.
            cur.execute(sql.SQL("DROP INDEX CONCURRENTLY {}").format(sql.Identifier(name)))
        cur.execute(statement)
    return name, True


def main(argv=None):
    load_environment(Path(__file__).resolve().parents[1] / ".env")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="print the DDL without running it")
    parser.add_argument("--drop-stale", action="store_true",
                        help="drop partial indexes for other embedding versions")
    args = parser.parse_args(argv)
    config = RetrievalConfig.from_environment()
    conn = get_connection()
    try:
        name, created = ensure_index(conn, config, dry_run=args.dry_run)
        if args.drop_stale:
            for stale in stale_indexes(conn, name):
                drop_index(conn, stale, args.dry_run)
                print(f"drop {stale}" if args.dry_run else f"dropped {stale}")
    finally:
        conn.close()
    if args.dry_run:
        print(f"index: {name} (dry run)")
    elif created:
        print(f"created {name}")
    else:
        print(f"{name} already exists and is valid")


if __name__ == "__main__":
    main()
