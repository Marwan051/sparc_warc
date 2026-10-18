"""Spark materialization: bounded driver reads, pure executor transforms."""

import hashlib
from contextlib import closing
from db import chunks
from jobs.batching import batch_tasks, run_waves, check_result_size
from jobs.runtime import config, processing_session, report, cli


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
        check_result_size(result, task["result_bytes"],
                          "chunk result exceeds byte limit; reduce --items-per-task or increase --result-bytes")
    return result


def run(argv=None):
    cfg = config("chunk", argv)
    if cfg["dry_run"]:
        report(cfg)
        return 0
    with processing_session("chunk", cfg) as (conn, spark):
        def commit(result):
            for document in result["documents"]:
                chunks.commit_document(conn, cfg["chunking_version"], document)
            report({"committed_documents": len(result["documents"]),
                    "committed_chunks": sum(len(d["chunks"]) for d in result["documents"])})
        with closing(chunks.iter_pending_documents(conn, cfg["chunking_version"], cfg["document_limit"])) as source:
            tasks = batch_tasks(source, cfg, lambda batch: {
                "items": batch, "result_bytes": cfg["result_bytes"]})
            run_waves(spark, tasks, process_batch, commit, cfg["parallel_tasks"])
        report(chunks.counts(conn, cfg["chunking_version"]))
        return 0


def main():
    raise SystemExit(cli(run))


if __name__ == "__main__":
    main()
