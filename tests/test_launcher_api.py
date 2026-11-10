"""Python API contract for the Spark job launcher."""

import unittest
from unittest.mock import patch

from jobs import launcher
from jobs.errors import LaunchError


class LauncherApiTests(unittest.TestCase):
    def test_keywords_become_existing_stage_arguments(self):
        with patch.object(launcher, "run", return_value=0) as run:
            result = launcher.launch(
                "ingest",
                year=2026,
                num_files=1,
                dry_run=True,
                use_trafilatura=False,
                no_progress=True,
            )

        self.assertEqual(result, 0)
        run.assert_called_once_with([
            "ingest",
            "--year", "2026",
            "--num-files", "1",
            "--dry-run",
            "--no-use-trafilatura",
            "--no-progress",
        ])

    def test_false_store_true_flag_is_omitted_and_none_is_omitted(self):
        with patch.object(launcher, "run", return_value=0) as run:
            launcher.launch("tag", retry_errors=False, backend=None, analysis_limit=5)

        run.assert_called_once_with(["tag", "--analysis-limit", "5"])

    def test_embedding_limit_maps_to_flag(self):
        with patch.object(launcher, "run", return_value=0) as run:
            launcher.launch("embed", embedding_limit=5)

        run.assert_called_once_with(["embed", "--embedding-limit", "5"])

    def test_success_returns_zero(self):
        with patch.object(launcher, "run", return_value=0):
            self.assertEqual(launcher.launch("chunk", document_limit=2), 0)

    def test_stage_failure_raises_for_task_frameworks(self):
        with patch.object(launcher, "run", return_value=17):
            with self.assertRaisesRegex(LaunchError, "chunk launcher exited with code 17") as caught:
                launcher.launch("chunk", document_limit=2)
        self.assertEqual(caught.exception.exit_code, 17)

    def test_unknown_stage_raises(self):
        with self.assertRaises(LaunchError) as caught:
            launcher.launch("unknown")
        self.assertEqual(caught.exception.exit_code, 2)

    def test_boolean_is_rejected_for_non_boolean_options(self):
        with self.assertRaisesRegex(TypeError, "executor_instances is not a boolean"):
            launcher.launch("chunk", executor_instances=True)
        with self.assertRaisesRegex(TypeError, "retry_errors is not a boolean"):
            launcher.launch("chunk", retry_errors=False)


if __name__ == "__main__":
    unittest.main()
