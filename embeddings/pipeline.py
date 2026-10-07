"""Spark embedding service with driver-owned PostgreSQL reads and commits."""

import os
from contextlib import closing

from db import chunks, embeddings as embedding_store
from db.db_handler import init_db
from embeddings.embeddings import model_version
from jobs.batching import batches, run_waves, serialized_size
from jobs.runtime import cli, config, report, start_spark


def process_batch(task):
    import numpy as np
    from embeddings import generate_embeddings

    os.environ["EMBEDDING_MAX_LENGTH"] = str(task["max_length"])
    vectors = generate_embeddings([item["text"] for item in task["items"]])
    if len(vectors) != len(task["items"]):
        raise ValueError("embedding model returned a different number of vectors than input chunks")
    result_rows = []
    for item, vector in zip(task["items"], vectors):
        result_rows.append({"page_id": item["page_id"], "chunk_index": item["chunk_index"],
                            "text": item["text"], "text_hash": item["text_hash"],
                            "embedding": np.asarray(vector, dtype=np.float32).tolist()})
    result = {"rows": result_rows}
    if serialized_size(result) > task["result_bytes"]:
        raise ValueError("embedding result exceeds --result-bytes")
    return result


def run(argv=None):
    cfg = config("embed", argv)
    if cfg["dry_run"]:
        report(cfg)
        return 0
    cfg["embedding_model"] = cfg.pop("model")
    cfg["embedding_version"] = model_version(cfg["max_length"])
    init_db()
    conn = chunks.acquire_lock("embedding")
    spark = None
    try:
        spark = start_spark("embed", cfg)
        def commit(result):
            embedding_store.commit_batch(conn, cfg, result["rows"])
            report({"committed": len(result["rows"])})
        with closing(embedding_store.iter_pending(cfg, cfg["embedding_limit"])) as source:
            tasks = ({"items": batch, "max_length": cfg["max_length"],
                      "result_bytes": cfg["result_bytes"]}
                     for batch in batches(source, cfg["items_per_task"], cfg["input_bytes"]))
            run_waves(spark, tasks, process_batch, commit, cfg["parallel_tasks"])
        report(dict(embedding_store.counts(conn, cfg), embedding_model=cfg["embedding_model"],
                    embedding_version=cfg["embedding_version"]))
        return 0
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
