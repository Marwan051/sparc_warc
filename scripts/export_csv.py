"""Export article and enrichment tables to CSV, then copy to the HGFS share.

Usage:
  python -m scripts.export_csv [csv_dir] [dest_dir]

Defaults: csv_dir=<project>/exports  dest_dir=/mnt/hgfs/copy_path/warcdb_csv
Connection settings come from PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD.
"""

import os
from pathlib import Path
import shutil
import sys
import tempfile

TABLES = (
    "websites",
    "authors",
    "pages",
    "metadata",
    "content",
    "chunk_materializations",
    "article_chunks",
    "chunk_analyses",
    "chunk_embeddings",
)
ORDER_BY = (
    "id",
    "id",
    "id",
    "page_id",
    "page_id",
    "page_id, chunking_version",
    "page_id, chunking_version, chunk_index",
    "page_id, chunking_version, chunk_index, backend, model, analysis_version",
    "page_id, chunking_version, chunk_index, embedding_model, embedding_version",
)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DEST = Path("/mnt/hgfs/copy_path/warcdb_csv")


def _settings(environ):
    return {
        "host": environ.get("PGHOST") or "localhost",
        "port": environ.get("PGPORT") or "5432",
        "dbname": environ.get("PGDATABASE") or "warcdb",
        "user": environ.get("PGUSER") or "warc_user",
        "password": environ.get("PGPASSWORD") or "password",
    }


def _listing(directory):
    for path in sorted(directory.iterdir()):
        if path.is_file():
            print(f"  {path.stat().st_size:>10}  {path.name}")


def export(connection, csv_dir, dest_dir):
    """Write every table into staging, move them in, then copy to the share."""
    csv_dir.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".export-", dir=csv_dir))
    try:
        with connection.cursor() as cursor:
            for table, order in zip(TABLES, ORDER_BY):
                statement = (
                    f"COPY (SELECT * FROM {table} ORDER BY {order}) "
                    "TO STDOUT WITH CSV HEADER"
                )
                with open(staging / f"{table}.csv", "w", newline="") as handle:
                    cursor.copy_expert(statement, handle)

        # Nothing has touched the old export until every table succeeded.
        for table in TABLES:
            os.replace(staging / f"{table}.csv", csv_dir / f"{table}.csv")

        print("Row counts:")
        with connection.cursor() as cursor:
            for table in TABLES:
                cursor.execute(f"SELECT count(*) FROM {table};")
                print(f"  {table:<23} {cursor.fetchone()[0]} rows")
        _listing(csv_dir)

        dest_dir.mkdir(parents=True, exist_ok=True)
        for table in TABLES:
            shutil.copy2(csv_dir / f"{table}.csv", dest_dir / f"{table}.csv")
        print(f"Copied {len(TABLES)} CSVs to {dest_dir}:")
        _listing(dest_dir)
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def _connect(**settings):
    import psycopg2
    return psycopg2.connect(**settings)


def main(argv=None, connect=None):
    arguments = list(sys.argv[1:] if argv is None else argv)
    csv_dir = Path(arguments[0]) if arguments else PROJECT_ROOT / "exports"
    dest_dir = Path(arguments[1]) if len(arguments) > 1 else DEFAULT_DEST
    settings = _settings(os.environ)
    print(
        f"Exporting article and enrichment tables to {csv_dir} "
        f"(db: {settings['host']}:{settings['port']}/{settings['dbname']} "
        f"as {settings['user']})"
    )

    try:
        connection = (connect or _connect)(**settings)
        try:
            export(connection, csv_dir, dest_dir)
        finally:
            connection.close()
    except Exception as error:
        print(f"FATAL {type(error).__name__}: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
