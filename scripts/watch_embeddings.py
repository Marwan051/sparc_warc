"""Read-only, version-aware progress monitor for embedding runs."""

import argparse
import os
from pathlib import Path
import time
from datetime import datetime

from chunking import CHUNKING_VERSION
from jobs.environment import load_environment
from jobs.runtime import env_int, positive


def read_counts(chunking_version, model, embedding_version):
    from db.db_handler import get_connection

    conn = get_connection()
    try:
        conn.set_session(readonly=True, autocommit=True)
        with conn.cursor() as cur:
            cur.execute("""SELECT
                (SELECT count(*) FROM article_chunks c
                    WHERE c.chunking_version=%s AND c.eligible),
                (SELECT count(*) FROM chunk_embeddings e
                    JOIN article_chunks c USING (page_id,chunking_version,chunk_index)
                    WHERE c.chunking_version=%s AND c.eligible
                      AND e.embedding_model=%s AND e.embedding_version=%s)""",
                (chunking_version, chunking_version, model, embedding_version))
            return cur.fetchone()
    finally:
        conn.close()


def remaining(eligible, embedded, run_limit=None, starting_embedded=None):
    pending = eligible - embedded
    if run_limit is None:
        return pending
    if embedded < starting_embedded:
        raise ValueError("current embedded count is below --starting-embedded")
    return min(pending, max(0, run_limit - (embedded - starting_embedded)))


def main(argv=None):
    load_environment(Path(__file__).resolve().parents[1] / ".env")
    parser = argparse.ArgumentParser(description="Print embedding progress every 10 seconds")
    parser.add_argument("--interval", type=positive, default=10, help="poll interval in seconds (default: 10)")
    parser.add_argument("--once", action="store_true", help="print one snapshot and exit")
    parser.add_argument("--run-limit", type=positive, help="--embedding-limit used for this run")
    parser.add_argument("--starting-embedded", type=int, help="embedded count before a limited run began")
    parser.add_argument("--model", default=None)
    parser.add_argument("--max-length", type=positive)
    parser.add_argument("--chunking-version", default=CHUNKING_VERSION)
    args = parser.parse_args(argv)
    if (args.run_limit is None) != (args.starting_embedded is None):
        parser.error("--run-limit and --starting-embedded must be supplied together")
    if args.starting_embedded is not None and args.starting_embedded < 0:
        parser.error("--starting-embedded cannot be negative")

    from embeddings.embeddings import model_version

    model = args.model if args.model is not None else os.environ.get("EMBEDDING_MODEL", "BAAI/bge-m3-int8")
    max_length = args.max_length if args.max_length is not None else env_int("EMBEDDING_MAX_LENGTH", 256, minimum=1)
    embedding_version = model_version(max_length)
    print(f"Watching {model} / {embedding_version} / {args.chunking_version}", flush=True)
    try:
        while True:
            eligible, embedded = read_counts(args.chunking_version, model, embedding_version)
            left = remaining(eligible, embedded, args.run_limit, args.starting_embedded)
            stamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
            label = "run_remaining" if args.run_limit is not None else "remaining"
            print(f"{stamp} eligible={eligible} embedded={embedded} "
                  f"{label}={left} corpus_pending={eligible - embedded}", flush=True)
            if args.once or left == 0:
                return 0
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("Stopped monitoring.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
