"""Mark existing pages whose cleaned text duplicates an earlier page.

New ingestion skips duplicate text, but rows written before that check may still
exist. This script marks later rows by setting ``pages.duplicate_of``; it does
not delete rows, chunks, or embeddings. Run without ``--apply`` first to see the
count.

Duplicates are pages with the same ``text_hash`` and ``metadata.char_count`` at
or above the dedup threshold. The lowest page id in each group is kept.
"""

import argparse
from pathlib import Path

from db.db_handler import DEDUP_MIN_CHARS, get_connection
from jobs.environment import load_environment
from jobs.validation import positive_int


CREATE_CANDIDATES = """
CREATE TEMP TABLE dedupe_candidates ON COMMIT PRESERVE ROWS AS
SELECT id, keep_id
FROM (
    SELECT p.id,
           min(p.id) OVER (PARTITION BY p.text_hash) AS keep_id,
           row_number() OVER (PARTITION BY p.text_hash ORDER BY p.id) AS rn
    FROM pages p
    JOIN metadata m ON m.page_id = p.id
    WHERE p.duplicate_of IS NULL
      AND p.text_hash IS NOT NULL
      AND m.char_count >= %s
) ranked
WHERE rn > 1
"""

MARK_BATCH = """
WITH batch AS (
    DELETE FROM dedupe_candidates
    WHERE id IN (SELECT id FROM dedupe_candidates LIMIT %s)
    RETURNING id, keep_id
)
UPDATE pages p
SET duplicate_of = batch.keep_id, duplicate_reason = 'text_hash'
FROM batch
WHERE p.id = batch.id
RETURNING p.id
"""


def main(argv=None):
    load_environment(Path(__file__).resolve().parents[1] / ".env")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="mark duplicates (default: dry run)")
    parser.add_argument("--min-chars", type=positive_int, default=DEDUP_MIN_CHARS)
    parser.add_argument("--batch-size", type=positive_int, default=10000)
    args = parser.parse_args(argv)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(CREATE_CANDIDATES, (args.min_chars,))
            cur.execute("SELECT count(*) FROM dedupe_candidates")
            total = cur.fetchone()[0]
            if not args.apply:
                print(f"{total} duplicate pages would be marked (dry run)")
                conn.rollback()
                return
            cur.execute("CREATE INDEX ON dedupe_candidates (id)")
            conn.commit()
            marked = 0
            while True:
                cur.execute(MARK_BATCH, (args.batch_size,))
                rows = cur.fetchall()
                conn.commit()
                if not rows:
                    break
                marked += len(rows)
                print(f"marked {marked}/{total}", flush=True)
            cur.execute("DROP TABLE dedupe_candidates")
            conn.commit()
            print(f"marked {marked} duplicate pages")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
