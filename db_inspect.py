import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from db.db_handler import get_connection

TABLES = ("websites", "authors", "pages", "metadata", "content", "ingest_files", "ingest_runs", "ingest_run_files", "ingest_chunks")
SAMPLE_SIZE = int(os.environ.get("DB_INSPECT_SAMPLES", "5"))
PREVIEW_LENGTH = int(os.environ.get("DB_INSPECT_PREVIEW", "300"))


def print_counts(cur):
    print("=" * 90)
    print("TABLE COUNTS")
    print("=" * 90)
    for table in TABLES:
        cur.execute(f"SELECT COUNT(*) FROM {table};")
        print(f" {table:<12}: {cur.fetchone()[0]:,}")


def print_progress(cur):
    cur.execute(
        """
        SELECT manifest_id,
               COUNT(*) FILTER (WHERE complete) AS done,
               COUNT(*) AS total,
               COALESCE(SUM(bytes_done), 0) AS bytes
        FROM ingest_files GROUP BY manifest_id;
        """
    )
    rows = cur.fetchall()
    if not rows:
        print("No checkpoints yet.")
    print("-" * 90)
    print("CHECKPOINTS (ingest_files)")
    for manifest_id, done, total, nbytes in rows:
        print(f" {manifest_id}: {done}/{total} files complete, {nbytes:,} bytes")
    cur.execute(
        """SELECT run_id::text, manifest_id, status, inserted_count,
                  target_articles, per_file_target
           FROM ingest_runs ORDER BY created_at DESC LIMIT 10"""
    )
    print("-" * 90)
    print("RECENT INGESTION RUNS")
    for run_id, manifest, status, inserted, target, per_file in cur.fetchall():
        target_label = f"{target:,}" if target else "unlimited"
        per_file_label = f"{per_file:,}" if per_file else "unlimited"
        print(f" {run_id} {manifest} {status}: {inserted:,}/{target_label}, per-file={per_file_label}")

    cur.execute("""SELECT run_id::text,file_url,last_error FROM ingest_run_files
                   WHERE status='failed' ORDER BY updated_at DESC LIMIT 10""")
    for run_id, file_url, error in cur.fetchall():
        print(f" FAILED {run_id} {file_url}: {error}")


def print_previews(cur):
    cur.execute(
        """
        SELECT p.id, w.domain, m.language, m.title, c.cleaned_text
        FROM pages AS p
        JOIN websites AS w ON w.id = p.website_id
        JOIN metadata AS m ON m.page_id = p.id
        JOIN content AS c ON c.page_id = p.id
        ORDER BY p.id DESC LIMIT %s;
        """,
        (SAMPLE_SIZE,),
    )
    records = cur.fetchall()
    print("-" * 90)
    print(f"SAMPLE ROWS (latest {len(records)})")
    for page_id, domain, language, title, cleaned_text in records:
        preview = " ".join((cleaned_text or "").split())[:PREVIEW_LENGTH]
        if preview and len(preview) == PREVIEW_LENGTH:
            preview += "..."
        print(f" [{page_id}] ({language or 'N/A'}) {domain or 'N/A'} — {(title or 'N/A')[:60]}")
        print(f"       {preview or 'N/A'}")


def main():
    conn = get_connection()
    try:
        cur = conn.cursor()
        try:
            print_counts(cur)
            print_progress(cur)
            print_previews(cur)
        finally:
            cur.close()
    finally:
        conn.close()
    print("=" * 90)


if __name__ == "__main__":
    main()
