"""Spark materialization: bounded driver reads, pure executor transforms."""

import hashlib
from contextlib import closing
from db import chunks
from db.db_handler import init_db
from jobs.batching import batches, run_waves, serialized_size
from jobs.runtime import config, start_spark, report, cli


def process_batch(task):
    from langchain_core.documents import Document
    from chunking.preprocessing import clean_article_text, noise_reason
    from chunking.splitters import iter_document_chunks
    result = {"documents": []}
    for source in task["items"]:
        document = Document(page_content=clean_article_text(source["text"]), metadata={
            "doc_id": source["page_id"], "source": source["source"],
            "title": source["title"], "language": source["language"],
        })
        rows = []
        for chunk in iter_document_chunks([document]):
            reason = noise_reason(chunk)
            rows.append({"chunk_index": chunk.metadata["chunk_index"], "chunk_text": chunk.page_content,
                         "text_hash": hashlib.sha256(chunk.page_content.encode()).hexdigest(),
                         "eligible": reason is None, "filter_reason": reason})
        result["documents"].append({"page_id": source["page_id"], "source_hash": chunks.source_hash(source), "chunks": rows})
        if serialized_size(result) > task["result_bytes"]:
            raise ValueError("chunk result exceeds byte limit; reduce --items-per-task or increase --result-bytes")
    return result


def run(argv=None):
    cfg = config("chunk", argv)
    if cfg["dry_run"]:
        report(cfg)
        return 0
    init_db()
    conn = chunks.acquire_lock("chunking")
    spark = None
    try:
        spark = start_spark("chunk", cfg)
        def commit(result):
            for document in result["documents"]:
                chunks.commit_document(conn, cfg["chunking_version"], document)
            report({"committed_documents": len(result["documents"]),
                    "committed_chunks": sum(len(d["chunks"]) for d in result["documents"])})
        with closing(chunks.iter_pending_documents(conn, cfg["chunking_version"], cfg["document_limit"])) as source:
            tasks = ({"items": batch, "result_bytes": cfg["result_bytes"]}
                     for batch in batches(source, cfg["items_per_task"], cfg["input_bytes"]))
            run_waves(spark, tasks, process_batch, commit, cfg["parallel_tasks"])
        report(chunks.counts(conn, cfg["chunking_version"]))
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
