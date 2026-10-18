import importlib.util
import unittest


AVAILABLE = all(importlib.util.find_spec(name) is not None for name in (
    "numpy", "pgvector", "pydantic",
))


def hit(page_id, chunk_index, text, similarity, query_id="q", reranker_score=None):
    from retrieval.models import Source
    from retrieval.store import SearchHit
    return SearchHit(
        page_id=page_id, chunk_index=chunk_index, text_hash="h", text=text,
        similarity=similarity, query_id=query_id, reranker_score=reranker_score,
        source=Source(page_id=page_id, url="u", title="t", publisher="p",
                      author="a", language="en", published_date="2026-01-01"),
    )


class FakeReranker:
    def __init__(self, scores):
        self.scores = list(scores)

    def score(self, pairs):
        import numpy as np
        if not pairs:
            return np.empty(0, dtype=np.float32)
        return np.asarray(self.scores, dtype=np.float32)


@unittest.skipUnless(AVAILABLE, "install requirements/rag-agent.txt for ranking tests")
class BuildInputsTests(unittest.TestCase):
    def test_builds_pairs_in_query_then_candidate_order(self):
        from retrieval.models import SearchQuery
        from retrieval.ranking import build_reranker_inputs
        queries = [SearchQuery(id="q1", query="first"), SearchQuery(id="q2", query="second")]
        groups = [[hit(1, 0, "a", 0.5), hit(1, 1, "b", 0.4)], [hit(2, 0, "c", 0.3)]]
        pairs = build_reranker_inputs(queries, groups)
        self.assertEqual(pairs, [("first", "a"), ("first", "b"), ("second", "c")])

    def test_mismatched_group_count_raises(self):
        from retrieval.models import SearchQuery
        from retrieval.ranking import build_reranker_inputs
        with self.assertRaises(RuntimeError):
            build_reranker_inputs([SearchQuery(id="q", query="x")], [])


@unittest.skipUnless(AVAILABLE, "install requirements/rag-agent.txt for ranking tests")
class ValidateScoresTests(unittest.TestCase):
    def test_returns_flat_array(self):
        import numpy as np
        from retrieval.ranking import validate_reranker_scores
        result = validate_reranker_scores([[0.1], [0.2]], 2)
        self.assertEqual(result.shape, (2,))

    def test_rejects_wrong_count(self):
        from retrieval.ranking import validate_reranker_scores
        with self.assertRaises(RuntimeError):
            validate_reranker_scores([0.1, 0.2, 0.3], 2)

    def test_rejects_non_finite(self):
        import numpy as np
        from retrieval.ranking import validate_reranker_scores
        with self.assertRaises(RuntimeError):
            validate_reranker_scores(np.array([np.nan, 0.0]), 2)
        with self.assertRaises(RuntimeError):
            validate_reranker_scores(np.array([np.inf, 0.0]), 2)


@unittest.skipUnless(AVAILABLE, "install requirements/rag-agent.txt for ranking tests")
class AttachScoresTests(unittest.TestCase):
    def test_assigns_scores_in_order_in_place(self):
        from retrieval.ranking import attach_reranker_scores
        first = hit(1, 0, "a", 0.5)
        second = hit(1, 1, "b", 0.4)
        groups = [[first, second]]
        attach_reranker_scores(groups, [0.2, 0.8])
        self.assertEqual(groups[0][0].reranker_score, 0.2)
        self.assertEqual(groups[0][1].reranker_score, 0.8)
        self.assertIs(groups[0][0], first)


@unittest.skipUnless(AVAILABLE, "install requirements/rag-agent.txt for ranking tests")
class SortAndLimitTests(unittest.TestCase):
    def test_orders_by_reranker_then_cosine_then_chunk(self):
        from retrieval.ranking import sort_and_limit_hits
        low_cosine_high_rerank = hit(2, 0, "b", 0.10, reranker_score=0.90)
        high_cosine_low_rerank = hit(1, 0, "a", 0.90, reranker_score=0.20)
        tie_a = hit(3, 0, "c", 0.50, reranker_score=0.50)
        tie_b = hit(1, 5, "d", 0.50, reranker_score=0.50)
        groups = [[high_cosine_low_rerank, low_cosine_high_rerank, tie_b, tie_a]]
        result = sort_and_limit_hits(groups, top_k=5)[0]
        self.assertEqual([h.chunk_id for h in result],
                         ["p2:c0", "p1:c5", "p3:c0", "p1:c0"])

    def test_limits_each_group_to_top_k(self):
        from retrieval.ranking import sort_and_limit_hits
        groups = [[
            hit(1, 0, "a", 0.1, reranker_score=0.9),
            hit(1, 1, "b", 0.2, reranker_score=0.8),
            hit(1, 2, "c", 0.3, reranker_score=0.7),
        ]]
        result = sort_and_limit_hits(groups, top_k=2)[0]
        self.assertEqual(len(result), 2)

    def test_unscored_hit_raises(self):
        from retrieval.ranking import sort_and_limit_hits
        with self.assertRaises(RuntimeError):
            sort_and_limit_hits([[hit(1, 0, "a", 0.5)]], top_k=5)

    def test_zero_score_is_valid(self):
        from retrieval.ranking import attach_reranker_scores, sort_and_limit_hits
        groups = [[hit(1, 0, "a", 0.5)]]
        attach_reranker_scores(groups, [0.0])
        self.assertEqual(sort_and_limit_hits(groups, top_k=5)[0][0].reranker_score, 0.0)


@unittest.skipUnless(AVAILABLE, "install requirements/rag-agent.txt for ranking tests")
class RerankQueryGroupsTests(unittest.TestCase):
    def test_low_cosine_high_reranker_moves_to_front(self):
        from retrieval.models import SearchQuery
        from retrieval.ranking import rerank_query_groups
        queries = [SearchQuery(id="q1", query="banking law")]
        groups = [[hit(1, 0, "sports", 0.82), hit(2, 0, "bank capital", 0.76)]]
        result = rerank_query_groups(queries, groups, FakeReranker([0.03, 0.97]), top_k=5)
        self.assertEqual(result[0][0].chunk_id, "p2:c0")

    def test_query_groups_are_ranked_independently(self):
        from retrieval.models import SearchQuery
        from retrieval.ranking import rerank_query_groups
        queries = [SearchQuery(id="q1", query="a"), SearchQuery(id="q2", query="b")]
        groups = [
            [hit(1, 0, "a0", 0.5), hit(1, 1, "a1", 0.4)],
            [hit(2, 0, "b0", 0.5), hit(2, 1, "b1", 0.4)],
        ]
        result = rerank_query_groups(queries, groups, FakeReranker([0.1, 0.9, 0.5, 0.4]), top_k=1)
        self.assertEqual(result[0][0].chunk_id, "p1:c1")
        self.assertEqual(result[1][0].chunk_id, "p2:c0")


if __name__ == "__main__":
    unittest.main()
