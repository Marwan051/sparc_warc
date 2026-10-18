import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch


AVAILABLE = importlib.util.find_spec("numpy") is not None


def make_reranker(batch_size=4):
    """Build an OnnxReranker without touching the real 570 MB model."""
    from retrieval.reranker import OnnxReranker, RerankerConfig
    with patch.object(OnnxReranker, "ensure_loaded", lambda self: None):
        return OnnxReranker(RerankerConfig(model_dir=Path("."), batch_size=batch_size))


@unittest.skipUnless(AVAILABLE, "install requirements/rag-agent.txt for reranker tests")
class SigmoidTests(unittest.TestCase):
    def test_maps_logits_into_zero_one(self):
        import numpy as np
        from retrieval.reranker import sigmoid
        result = sigmoid(np.array([-10.0, 0.0, 10.0]))
        self.assertAlmostEqual(float(result[1]), 0.5, places=6)
        self.assertLess(float(result[0]), 1e-3)
        self.assertGreater(float(result[2]), 1 - 1e-3)

    def test_handles_extreme_logits_without_overflow(self):
        import numpy as np
        from retrieval.reranker import sigmoid
        result = sigmoid(np.array([-1000.0, 1000.0]))
        self.assertTrue(np.all(np.isfinite(result)))
        self.assertAlmostEqual(float(result[0]), 0.0, places=6)
        self.assertAlmostEqual(float(result[1]), 1.0, places=6)

    def test_rejects_non_finite(self):
        import numpy as np
        from retrieval.reranker import sigmoid
        with self.assertRaises(ValueError):
            sigmoid(np.array([np.nan]))


@unittest.skipUnless(AVAILABLE, "install requirements/rag-agent.txt for reranker tests")
class ValidateLogitsTests(unittest.TestCase):
    def test_flattens_single_column(self):
        import numpy as np
        from retrieval.reranker import validate_logits
        result = validate_logits(np.array([[1.0], [2.0]]), 2)
        self.assertEqual(result.shape, (2,))

    def test_rejects_wrong_shape(self):
        import numpy as np
        from retrieval.reranker import validate_logits
        with self.assertRaises(ValueError):
            validate_logits(np.zeros((2, 3)), 2)

    def test_rejects_wrong_count(self):
        import numpy as np
        from retrieval.reranker import validate_logits
        with self.assertRaises(ValueError):
            validate_logits(np.zeros(3), 2)

    def test_rejects_non_finite(self):
        import numpy as np
        from retrieval.reranker import validate_logits
        with self.assertRaises(ValueError):
            validate_logits(np.array([np.inf, 0.0]), 2)


@unittest.skipUnless(AVAILABLE, "install requirements/rag-agent.txt for reranker tests")
class OnnxRerankerTests(unittest.TestCase):
    def test_score_empty_returns_empty(self):
        reranker = make_reranker()
        self.assertEqual(reranker.score([]).shape, (0,))

    def test_score_batches_and_preserves_order(self):
        import numpy as np
        reranker = make_reranker(batch_size=4)
        sizes = []
        counter = {"i": 0}

        def fake_run_batch(pairs):
            sizes.append(len(pairs))
            start = counter["i"]
            counter["i"] += len(pairs)
            return np.arange(start, start + len(pairs), dtype=np.float32)

        reranker._run_batch = fake_run_batch
        pairs = [(f"q{i}", f"p{i}") for i in range(10)]
        result = reranker.score(pairs)
        self.assertEqual(sizes, [4, 4, 2])
        self.assertEqual(len(result), 10)
        # sigmoid is monotonic, so input order is preserved in the scores
        self.assertTrue(np.all(np.diff(result) >= 0))

    def test_score_rejects_bad_pairs(self):
        reranker = make_reranker()
        with self.assertRaises(TypeError):
            reranker.score([("q", "p", "x")])
        with self.assertRaises(TypeError):
            reranker.score([("q", 1)])

    def test_tokenize_passes_query_and_passage_separately(self):
        reranker = make_reranker()
        captured = {}

        class FakeTokenizer:
            def __call__(self, queries, passages, **kwargs):
                captured["queries"] = queries
                captured["passages"] = passages
                return {
                    "input_ids": [[1, 2]],
                    "attention_mask": [[1, 1]],
                    "token_type_ids": [[0, 0]],
                }

        reranker._tokenizer = FakeTokenizer()
        reranker._input_names = {"input_ids", "attention_mask"}
        inputs = reranker._tokenize([("banking", "the law")])
        self.assertEqual(captured["queries"], ["banking"])
        self.assertEqual(captured["passages"], ["the law"])
        self.assertEqual(set(inputs), {"input_ids", "attention_mask"})


if __name__ == "__main__":
    unittest.main()
