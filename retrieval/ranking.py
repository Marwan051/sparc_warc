from typing import Sequence

import numpy as np

from retrieval.store import SearchHit, SearchQuery
from retrieval.reranker import OnnxReranker

def build_reranker_inputs(
    queries: list[SearchQuery],
    candidate_groups: list[list[SearchHit]],
) -> list[tuple[str, str]]:
    if len(queries) != len(candidate_groups):
        raise RuntimeError("The number of queries does not equal the number of candidate groups",
                            f"Num of queries: {len(queries)}, Num of candidate groups: {len(candidate_groups)}"
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
    if len(flat_scores) != expected_count :
        raise RuntimeError("The number of scores does not equal the expected count",
                            f"Num of queries: {len(scores)}, Num of candidate groups: {expected_count}"
                           )
    if not np.all(np.isfinite(flat_scores)):
        raise RuntimeError("Not all scores are finite")
    
    return flat_scores

def attach_reranker_scores(candidate_groups, scores) -> None:
    flat = validate_reranker_scores(scores, sum(len(g) for g in candidate_groups))
    i = 0
    for group in candidate_groups:
        for hit in group:
            hit.reranker_score = float(flat[i])
            i += 1

def sort_and_limit_hits(groups, top_k) -> list[list[SearchHit]]:
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
    raw = reranker.score(pairs)
    scores = validate_reranker_scores(raw, len(pairs))
    attach_reranker_scores(candidate_groups, scores)
    return sort_and_limit_hits(candidate_groups, top_k)
