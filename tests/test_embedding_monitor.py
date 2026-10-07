"""Run-relative progress needs an explicit baseline for limited jobs."""

import unittest

from scripts.watch_embeddings import remaining


class EmbeddingMonitorTests(unittest.TestCase):
    def test_unlimited_run_tracks_all_pending_chunks(self):
        self.assertEqual(remaining(100, 25), 75)
        self.assertEqual(remaining(100, 100), 0)

    def test_limited_run_uses_count_before_job_started(self):
        self.assertEqual(remaining(100, 21, 50, 1), 30)
        self.assertEqual(remaining(100, 51, 50, 1), 0)
        self.assertEqual(remaining(40, 35, 50, 1), 5)
        with self.assertRaisesRegex(ValueError, "below --starting-embedded"):
            remaining(100, 0, 50, 1)
