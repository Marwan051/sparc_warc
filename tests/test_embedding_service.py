"""Embedding worker/commit contract, without Spark or a live database."""

import hashlib
import importlib.util
import unittest
from unittest.mock import MagicMock, patch


@unittest.skipUnless(importlib.util.find_spec("pgvector"), "install embedding worker dependencies")
class EmbeddingServiceTests(unittest.TestCase):
    def test_worker_result_can_be_committed(self):
        import numpy as np

        from db.embeddings import commit_batch
        from embeddings.pipeline import process_batch

        text = "A short test chunk"
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        task = {"items": [{"page_id": 7, "chunk_index": 2, "text": text,
                            "text_hash": text_hash}],
                "max_length": 256, "result_bytes": 1024 * 1024}
        vector = np.zeros((1, 1024), dtype=np.float32)
        vector[0, 0] = 1
        with patch("embeddings.generate_embeddings", return_value=vector):
            row = process_batch(task)["rows"][0]
        self.assertEqual(row["text"], text)

        conn = MagicMock()
        cur = conn.cursor.return_value.__enter__.return_value
        cur.fetchone.side_effect = [(text_hash, True), (text_hash,)]
        cfg = {"chunking_version": "test-v1", "embedding_model": "test-model",
               "embedding_version": "test-version"}
        with patch("db.embeddings.register_vector"), patch("db.embeddings.execute_values") as insert:
            commit_batch(conn, cfg, [row])
        insert.assert_called_once()

    def test_worker_rejects_missing_vectors(self):
        import numpy as np

        from embeddings.pipeline import process_batch

        task = {"items": [{"page_id": 7, "chunk_index": 2, "text": "chunk", "text_hash": "unused"}],
                "max_length": 256, "result_bytes": 1024 * 1024}
        with patch("embeddings.generate_embeddings", return_value=np.empty((0, 1024))):
            with self.assertRaisesRegex(ValueError, "different number of vectors"):
                process_batch(task)
