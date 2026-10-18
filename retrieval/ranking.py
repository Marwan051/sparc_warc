from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from retrieval.reranker import OnnxReranker
    from retrieval.store import SearchHit, SearchQuery


def build_reranker_inputs(
    queries: list[SearchQuery],
    candidate_groups: list[list[SearchHit]],
) -> list[tuple[str, str]]:
    if len(queries) != len(candidate_groups):
        raise RuntimeError(
            "The number of queries does not equal the number of candidate groups: "
            f"{len(queries)} queries, {len(candidate_groups)} candidate groups"
        )
    pairs = []

    for query, group in zip(queries, candidate_groups):
        for hit in group:
            pairs.append((query.query, hit.text))

    return pairs


def validate_reranker_scores(
    scores: Sequence[float] | np.ndarray,
    expected_count: int,
) -> np.ndarray:
    flat_scores = np.array(scores).flatten()
    if len(flat_scores) != expected_count:
        raise RuntimeError(
            f"expected {expected_count} reranker scores, got {len(flat_scores)}"
        )
    if not np.all(np.isfinite(flat_scores)):
        raise RuntimeError("Not all scores are finite")

    return flat_scores

def attach_reranker_scores(candidate_groups: list[list[SearchHit]],
                           scores: Sequence[float] | np.ndarray) -> None:
    flat = validate_reranker_scores(scores, sum(len(g) for g in candidate_groups))
    i = 0
    for group in candidate_groups:
        for hit in group:
            hit.reranker_score = float(flat[i])
            i += 1

def sort_and_limit_hits(groups: list[list[SearchHit]], top_k: int) -> list[list[SearchHit]]:
    result: list[list[SearchHit]] = []
    for group in groups:
        if any(hit.reranker_score is None for hit in group):
            raise RuntimeError("unscored hit reached ranking")
        ranked = sorted(
            group,
            key=lambda hit: (
                -hit.reranker_score,
                -hit.similarity,
                hit.page_id,
                hit.chunk_index,
            ),
        )
        result.append(ranked[:top_k])
    return result

def rerank_query_groups(
    queries: list[SearchQuery],
    candidate_groups: list[list[SearchHit]],
    reranker: OnnxReranker,
    top_k: int,
) -> list[list[SearchHit]]:
    pairs = build_reranker_inputs(queries, candidate_groups)
    scores = reranker.score(pairs)
    attach_reranker_scores(candidate_groups, scores)
    return sort_and_limit_hits(candidate_groups, top_k)
