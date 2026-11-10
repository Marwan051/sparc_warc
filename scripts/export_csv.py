"""Export article and enrichment tables to CSV, then copy to the HGFS share.

Usage:
  python -m scripts.export_csv [csv_dir] [dest_dir]
  python -m scripts.export_csv --sample N [csv_dir] [dest_dir]
  python -m scripts.export_csv --rows N --seed 0.5 [csv_dir] [dest_dir]
  python -m scripts.export_csv --sample N --include-chunks
  python -m scripts.export_csv --sample N --zip
  python -m scripts.export_csv --sample N --zip-path /path/to/export.zip

Defaults: csv_dir=<project>/exports  dest_dir=/mnt/hgfs/copy_path/warcdb_csv
Connection settings come from PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD.

A full export writes all nine tables (including embeddings) as before. The
``--sample``/``--rows`` mode picks N random pages (articles) and exports the
article rows belonging to those pages (websites, authors, pages, metadata,
content). It skips chunking output and embeddings because those are not needed
for a plain article export; pass ``--include-chunks`` to add the chunk tables
(embeddings are still skipped). It writes to ``exports/sample-N`` by default and
does not copy to the HGFS share unless a destination is passed explicitly.
"""

import argparse
import csv
import os
from pathlib import Path
import shutil
import sys
import tempfile
import zipfile

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
ORDER_BY = {
    "websites": "id",
    "authors": "id",
    "pages": "id",
    "metadata": "page_id",
    "content": "page_id",
    "chunk_materializations": "page_id, chunking_version",
    "article_chunks": "page_id, chunking_version, chunk_index",
    "chunk_analyses": (
        "page_id, chunking_version, chunk_index, backend, model, analysis_version"
    ),
    "chunk_embeddings": (
        "page_id, chunking_version, chunk_index, embedding_model, embedding_version"
    ),
}
EMBEDDING_TABLES = ("chunk_embeddings",)
ARTICLE_TABLES = ("websites", "authors", "pages", "metadata", "content")
CHUNK_TABLES = ("chunk_materializations", "article_chunks", "chunk_analyses")
SAMPLE_TABLES = ARTICLE_TABLES
SAMPLE_TABLES_WITH_CHUNKS = ARTICLE_TABLES + CHUNK_TABLES
# Each filter restricts an exported table to the sampled page IDs staged in a
# temporary table. A join avoids sending thousands of IDs in every query, which
# makes PostgreSQL fall back to full table scans.
SAMPLE_FILTERS = {
    "websites": (
        "id IN (SELECT p.website_id FROM pages p "
        "JOIN export_page_ids e ON e.id = p.id)"
    ),
    "authors": (
        "id IN (SELECT p.author_id FROM pages p "
        "JOIN export_page_ids e ON e.id = p.id)"
    ),
    "pages": "id IN (SELECT id FROM export_page_ids)",
    "metadata": "page_id IN (SELECT id FROM export_page_ids)",
    "content": "page_id IN (SELECT id FROM export_page_ids)",
    "chunk_materializations": "page_id IN (SELECT id FROM export_page_ids)",
    "article_chunks": "page_id IN (SELECT id FROM export_page_ids)",
    "chunk_analyses": "page_id IN (SELECT id FROM export_page_ids)",
}
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


def _raise_csv_field_limit():
    """Allow very long content fields when counting local CSV records."""
    limit = sys.maxsize
    while True:
        try:
            csv.field_size_limit(limit)
            return
        except OverflowError:
            limit //= 10


_raise_csv_field_limit()


def _listing(directory):
    for path in sorted(directory.iterdir()):
        if path.is_file():
            print(f"  {path.stat().st_size:>10}  {path.name}")


def _sample_page_ids(cursor, count, seed=None):
    """Choose ``count`` random page IDs, optionally with a reproducible seed."""
    if seed is not None:
        cursor.execute("SELECT setseed(%s)", (seed,))
    print(f"Choosing {count} random pages...", flush=True)
    cursor.execute("SELECT id FROM pages ORDER BY random() LIMIT %s", (count,))
    return [row[0] for row in cursor.fetchall()]


def _stage_page_ids(cursor, page_ids):
    """Put sampled IDs in a temp table so COPY queries can join instead of IN."""
    cursor.execute("DROP TABLE IF EXISTS export_page_ids")
    cursor.execute("CREATE TEMP TABLE export_page_ids (id INT PRIMARY KEY)")
    cursor.execute(
        "INSERT INTO export_page_ids (id) SELECT unnest(%s::int[])", (page_ids,)
    )
    cursor.execute("ANALYZE export_page_ids")


def _copy_statement(table, filter_sql=None):
    query = f"SELECT * FROM {table}"
    if filter_sql is not None:
        query += f" WHERE {filter_sql}"
    query += f" ORDER BY {ORDER_BY[table]}"
    return f"COPY ({query}) TO STDOUT WITH CSV HEADER"


def _copy_tables(cursor, staging, tables, page_ids=None):
    for table in tables:
        filter_sql = SAMPLE_FILTERS[table] if page_ids is not None else None
        statement = _copy_statement(table, filter_sql)
        print(f"  exporting {table}...", flush=True)
        with open(staging / f"{table}.csv", "w", newline="") as handle:
            cursor.copy_expert(statement, handle)


def _count_rows(path):
    """Count CSV records locally (handles quoted newlines inside fields)."""
    with open(path, newline="") as handle:
        return max(sum(1 for _ in csv.reader(handle)) - 1, 0)


def _print_counts(csv_dir, tables):
    print("Row counts:")
    for table in tables:
        try:
            rows = f"{_count_rows(csv_dir / f'{table}.csv')} rows"
        except (csv.Error, OverflowError) as error:
            rows = f"count unavailable ({error})"
        print(f"  {table:<23} {rows}")


def _zip_tables(csv_dir, tables, zip_path):
    """Write the exported CSVs into one zip, replacing the old zip atomically."""
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = zip_path.with_name(f".{zip_path.name}.tmp")
    try:
        with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED) as archive:
            for table in tables:
                archive.write(
                    csv_dir / f"{table}.csv", arcname=f"{table}.csv"
                )
        os.replace(temporary, zip_path)
    finally:
        if temporary.exists():
            temporary.unlink()


def export(connection, csv_dir, dest_dir, sample=None, seed=None,
           include_chunks=False, zip_path=None):
    """Write tables into staging, move them in, then optionally copy to the share.

    ``sample`` is a number of random pages (articles), not rows per table.
    When set, only the sampled pages and their dependent rows are exported.
    Embeddings are always excluded when sampling. ``include_chunks`` adds the
    chunk tables; otherwise only article-level rows are exported. ``dest_dir``
    of ``None`` skips the share copy. ``zip_path`` also archives the CSVs.
    """
    if sample is None:
        tables = TABLES
    elif include_chunks:
        tables = SAMPLE_TABLES_WITH_CHUNKS
    else:
        tables = SAMPLE_TABLES
    csv_dir.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".export-", dir=csv_dir))
    try:
        with connection.cursor() as cursor:
            page_ids = None
            if sample is not None:
                page_ids = _sample_page_ids(cursor, sample, seed)
                if not page_ids:
                    raise RuntimeError("no pages available to sample")
                _stage_page_ids(cursor, page_ids)
                skipped = list(EMBEDDING_TABLES)
                if not include_chunks:
                    skipped.extend(CHUNK_TABLES)
                print(
                    f"Sampled {len(page_ids)} random pages; "
                    f"excluding: {', '.join(skipped)}",
                    flush=True,
                )
            _copy_tables(cursor, staging, tables, page_ids)

        # Nothing has touched the old export until every table succeeded.
        for table in tables:
            os.replace(staging / f"{table}.csv", csv_dir / f"{table}.csv")

        _print_counts(csv_dir, tables)
        _listing(csv_dir)

        if zip_path is not None:
            _zip_tables(csv_dir, tables, zip_path)
            print(f"Zipped {len(tables)} CSVs to {zip_path} "
                  f"({zip_path.stat().st_size} bytes)")

        if dest_dir is not None:
            dest_dir.mkdir(parents=True, exist_ok=True)
            for table in tables:
                shutil.copy2(csv_dir / f"{table}.csv", dest_dir / f"{table}.csv")
            print(f"Copied {len(tables)} CSVs to {dest_dir}:")
            _listing(dest_dir)
            if zip_path is not None:
                target = dest_dir / zip_path.name
                if target.resolve() != zip_path.resolve():
                    shutil.copy2(zip_path, target)
                    print(f"Copied zip to {target}")
                else:
                    print(f"Zip already in destination: {target}")
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def _connect(**settings):
    import psycopg2
    return psycopg2.connect(**settings)


def _parser():
    parser = argparse.ArgumentParser(
        description="Export article and enrichment tables to CSV."
    )
    parser.add_argument(
        "csv_dir",
        nargs="?",
        help="output directory (default: <project>/exports, or "
        "<project>/exports/sample-N when sampling)",
    )
    parser.add_argument(
        "dest_dir",
        nargs="?",
        help="optional copy destination (default: the HGFS share for full "
        "exports, no copy when sampling)",
    )
    parser.add_argument(
        "--sample",
        "--rows",
        dest="sample",
        type=int,
        metavar="N",
        help="export N randomly chosen pages and their rows, without embeddings",
    )
    parser.add_argument(
        "--seed",
        type=float,
        help="seed for reproducible random page selection",
    )
    parser.add_argument(
        "--include-chunks",
        action="store_true",
        help="also export chunk tables when sampling (embeddings stay excluded)",
    )
    parser.add_argument(
        "--zip",
        action="store_true",
        help="also write the exported CSVs to a .zip archive",
    )
    parser.add_argument(
        "--zip-path",
        type=Path,
        metavar="PATH",
        help="custom zip path (implies --zip; default: <csv_dir>.zip)",
    )
    return parser


def main(argv=None, connect=None):
    arguments = list(sys.argv[1:] if argv is None else argv)
    parser = _parser()
    args = parser.parse_args(arguments)

    if args.sample is not None and args.sample < 1:
        print("FATAL ValueError: --sample/--rows must be at least 1", file=sys.stderr)
        return 1

    if args.csv_dir:
        csv_dir = Path(args.csv_dir)
    elif args.sample is not None:
        csv_dir = PROJECT_ROOT / "exports" / f"sample-{args.sample}"
    else:
        csv_dir = PROJECT_ROOT / "exports"

    if args.dest_dir:
        dest_dir = Path(args.dest_dir)
    elif args.sample is not None:
        dest_dir = None
    else:
        dest_dir = DEFAULT_DEST

    zip_path = None
    if args.zip_path is not None:
        zip_path = args.zip_path
    elif args.zip:
        zip_path = csv_dir.parent / f"{csv_dir.name or 'export'}.zip"

    settings = _settings(os.environ)
    print(
        f"Exporting article and enrichment tables to {csv_dir} "
        f"(db: {settings['host']}:{settings['port']}/{settings['dbname']} "
        f"as {settings['user']})"
    )
    if args.sample is not None:
        seed_text = f", seed {args.seed}" if args.seed is not None else ""
        chunks_text = " with chunks" if args.include_chunks else ""
        print(f"Sampling {args.sample} random pages{chunks_text}{seed_text}")

    try:
        connection = (connect or _connect)(**settings)
        try:
            export(
                connection,
                csv_dir,
                dest_dir,
                sample=args.sample,
                seed=args.seed,
                include_chunks=args.include_chunks,
                zip_path=zip_path,
            )
        finally:
            connection.close()
    except Exception as error:
        print(f"FATAL {type(error).__name__}: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
