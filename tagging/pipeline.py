"""Spark tagging with pluggable batch inference and driver-owned commits."""

import atexit
import uuid
from collections import Counter
from contextlib import closing
from dataclasses import asdict
from db import chunks, analyses
from db.db_handler import init_db
from jobs.batching import batches, run_waves, serialized_size
from jobs.runtime import config, start_spark, report, cli
from tagging.contracts import AnalysisRequest

_BACKENDS = {}


def process_batch(task):
    from tagging.backends import create_backend
    key = (task["backend"], task["model"])
    if key not in _BACKENDS:
        _BACKENDS[key] = create_backend(*key)
        atexit.register(_BACKENDS[key].close)
    requests = [AnalysisRequest(**item) for item in task["items"]]
    batch = _BACKENDS[key].analyze_batch(requests)
    expected = {(r.page_id, r.chunk_index) for r in requests}
    seen = set()
    for outcome in batch.outcomes:
        identity = (outcome.page_id, outcome.chunk_index)
        if identity not in expected or identity in seen or outcome.status not in ("SUCCESS", "NOISE", "ERROR"):
            raise ValueError("backend returned an invalid or duplicate outcome")
        seen.add(identity)
    if not batch.quota_exhausted and seen != expected:
        raise ValueError("backend omitted outcomes without signaling quota exhaustion")
    result = {"batch_id": task["batch_id"], "outcomes": [asdict(o) for o in batch.outcomes],
              "quota_exhausted": batch.quota_exhausted}
    if serialized_size(result) > task["result_bytes"]:
        raise ValueError("tagging result exceeds --result-bytes")
    return result


def run(argv=None):
    cfg = config("tag", argv)
    if cfg["dry_run"]:
        report(cfg)
        return 0
    init_db()
    conn = chunks.acquire_lock("tagging")
    spark = None
    try:
        spark = start_spark("tag", cfg)
        def commit(result):
            analyses.commit_batch(conn, cfg, result["batch_id"], result["outcomes"])
            report(dict(Counter(o["status"].lower() for o in result["outcomes"]),
                        batch_id=result["batch_id"], committed=len(result["outcomes"])))
        with closing(analyses.iter_pending(cfg, cfg["analysis_limit"], cfg["retry_errors"])) as source:
            tasks = ({"items": batch, "batch_id": uuid.uuid4().hex,
                      "backend": cfg["backend"], "model": cfg["model"], "result_bytes": cfg["result_bytes"]}
                     for batch in batches(source, cfg["items_per_task"], cfg["input_bytes"]))
            _, quota = run_waves(spark, tasks, process_batch, commit, cfg["parallel_tasks"])
        report(dict(analyses.counts(conn, cfg), quota_exhausted=quota))
        if cfg["export_json"]:
            analyses.export_json(cfg, cfg["export_json"])
        return 2 if quota else 0
    finally:
        try:
            if spark is not None:
                spark.stop()
        finally:
            conn.close()


def main():
    raise SystemExit(cli(run))


if __name__ == "__main__":
    main()
