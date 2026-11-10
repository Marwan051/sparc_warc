"""Airflow task helpers: shortfall handling and manifest month selection."""

import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from jobs.airflow_tasks import (
    ingestion_months,
    launch_stage,
    manifest_url,
    manifest_urls,
)
from jobs.errors import LaunchError


class LaunchStageTests(unittest.TestCase):
    @patch("jobs.airflow_tasks.launch")
    def test_success_returns_ok_result(self, launch):
        result = launch_stage("embed", embedding_limit=5)
        launch.assert_called_once_with("embed", embedding_limit=5)
        self.assertEqual(result["stage"], "embed")
        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(result["status"], "succeeded")

    @patch("jobs.airflow_tasks.launch")
    def test_exit_two_is_a_warning_not_a_failure(self, launch):
        launch.side_effect = LaunchError("ingest launcher exited with code 2", 2)
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = launch_stage("ingest", year=2026, month=11)
        self.assertEqual(result["exit_code"], 2)
        self.assertEqual(result["status"], "sources_exhausted")
        self.assertIn("SOURCES EXHAUSTED", stream.getvalue())

    @patch("jobs.airflow_tasks.launch")
    def test_other_failures_propagate(self, launch):
        launch.side_effect = LaunchError("ingest launcher exited with code 1", 1)
        with self.assertRaises(LaunchError):
            launch_stage("ingest")


class MonthTests(unittest.TestCase):
    def test_mid_month_processes_only_that_month(self):
        self.assertEqual(
            ingestion_months("2026-11-10T00:00:00+02:00"),
            [(2026, 11)],
        )

    def test_first_of_month_also_revisits_previous_month(self):
        self.assertEqual(
            ingestion_months("2026-11-01T00:00:00+02:00"),
            [(2026, 11), (2026, 10)],
        )

    def test_january_first_revisits_december(self):
        self.assertEqual(
            ingestion_months("2027-01-01T00:00:00+02:00"),
            [(2027, 1), (2026, 12)],
        )

    def test_manifest_urls_match_month_selection(self):
        self.assertEqual(
            manifest_url(2026, 9),
            "https://data.commoncrawl.org/crawl-data/CC-NEWS/2026/09/warc.paths.gz",
        )
        self.assertEqual(
            manifest_urls("2026-11-01T00:00:00+02:00"),
            [
                "https://data.commoncrawl.org/crawl-data/CC-NEWS/2026/11/warc.paths.gz",
                "https://data.commoncrawl.org/crawl-data/CC-NEWS/2026/10/warc.paths.gz",
            ],
        )


if __name__ == "__main__":
    unittest.main()
