"""Deterministic evidence deduplication and adjacent-hit assembly."""

from __future__ import annotations

import hashlib

from retrieval.models import Evidence
from retrieval.store import SearchHit


def _unique(values):
    return list(dict.fromkeys(values))


def _merge_overlap(left: str, right: str) -> str:
    """Join chunks while removing their largest exact suffix/prefix overlap."""
    limit = min(len(left), len(right))
    overlap = 0
    for size in range(limit, 0, -1):
        if left[-size:] == right[:size]:
            overlap = size
            break
    separator = "" if overlap or not left or not right else "\n"
    return left + separator + right[overlap:]


def assemble_evidence(hits: list[SearchHit]) -> list[Evidence]:
    """Deduplicate hits, merge adjacent hits, then deduplicate exact blocks."""
    physical = {}
    for hit in hits:
        if hit.reranker_score is None:
            raise RuntimeError(f"unscored hit reached evidence assembly: {hit.chunk_id}")
        key = (hit.page_id, hit.chunk_index)
        if key not in physical:
            physical[key] = {
                "hit": hit,
                "query_ids": [hit.query_id],
                "similarity": hit.similarity,
                "reranker_score":hit.reranker_score
            }
        else:
            item = physical[key]
            item["query_ids"] = _unique(item["query_ids"] + [hit.query_id])
            item["similarity"] = max(item["similarity"], hit.similarity)
            item["reranker_score"] = max(item["reranker_score"],hit.reranker_score)

    runs = []
    current = None
    for (page_id, chunk_index), item in sorted(physical.items()):
        hit = item["hit"]
        if current is None or current["page_id"] != page_id or chunk_index != current["last_index"] + 1:
            if current is not None:
                runs.append(current)
            current = {
                "page_id": page_id,
                "last_index": chunk_index,
                "text": hit.text,
                "chunk_ids": [hit.chunk_id],
                "query_ids": list(item["query_ids"]),
                "reranker_score":item["reranker_score"],
                "similarity": item["similarity"],
                "sources": [hit.source],
            }
        else:
            current["last_index"] = chunk_index
            current["text"] = _merge_overlap(current["text"], hit.text)
            current["chunk_ids"].append(hit.chunk_id)
            current["query_ids"] = _unique(current["query_ids"] + item["query_ids"])
            current["similarity"] = max(current["similarity"], item["similarity"])
            current["reranker_score"] = max(current["reranker_score"],item["reranker_score"])
    if current is not None:
        runs.append(current)

    by_text = {}
    for run in runs:
        digest = hashlib.sha256(run["text"].encode()).hexdigest()
        if digest not in by_text:
            by_text[digest] = run
            continue
        existing = by_text[digest]
        existing["chunk_ids"] = _unique(existing["chunk_ids"] + run["chunk_ids"])
        existing["query_ids"] = _unique(existing["query_ids"] + run["query_ids"])
        existing["similarity"] = max(existing["similarity"], run["similarity"])
        existing["reranker_score"] = max(existing["reranker_score"],run["reranker_score"])
        source_keys = {(source.page_id, source.url) for source in existing["sources"]}
        existing["sources"].extend(
            source for source in run["sources"]
            if (source.page_id, source.url) not in source_keys
        )

    evidence = [Evidence(
        text=item["text"],
        chunk_ids=item["chunk_ids"],
        query_ids=item["query_ids"],
        reranker_score=item["reranker_score"],
        similarity=item["similarity"],
        sources=item["sources"],
    ) for item in by_text.values()]
    return sorted(evidence, key=lambda item: (-item.reranker_score,-item.similarity, item.chunk_ids[0]))

