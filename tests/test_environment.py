"""Dotenv defaults are shared, non-executable, and weaker than explicit env."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from jobs.environment import load_environment


ROOT = Path(__file__).resolve().parents[1]


class EnvironmentTests(unittest.TestCase):
    def test_defaults_quotes_existing_empty_values_and_no_shell_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".env"
            marker = Path(directory) / "must-not-exist"
            path.write_text(
                'PGHOST=db.internal\nPGPASSWORD="spaces # inside"\n'
                'GROQ_API_KEY=file-key\nKEEP_EMPTY=file-value\n'
                f"COMMAND=$(touch {marker})\n"
            )
            with patch.dict(os.environ, {"GROQ_API_KEY": "explicit-key", "KEEP_EMPTY": ""}, clear=True):
                load_environment(path)
                self.assertEqual(os.environ["PGHOST"], "db.internal")
                self.assertEqual(os.environ["PGPASSWORD"], "spaces # inside")
                self.assertEqual(os.environ["GROQ_API_KEY"], "explicit-key")
                self.assertEqual(os.environ["KEEP_EMPTY"], "")
                self.assertFalse(marker.exists())

    def test_missing_file_is_optional(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {}, clear=True):
            load_environment(Path(directory) / "absent")
            self.assertEqual(dict(os.environ), {})

    def test_json_mode_reports_only_the_values_the_file_adds(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".env"
            marker = Path(directory) / "must-not-exist"
            path.write_text(
                'PGHOST=db.internal\nPGPASSWORD="spaces # inside"\n'
                'GROQ_API_KEY=file-key\nKEEP_EMPTY=file-value\n'
                f"COMMAND=$(touch {marker})\n"
            )
            environment = dict(
                os.environ,
                GROQ_API_KEY="explicit-key",
                KEEP_EMPTY="",
                PYTHONPATH=str(ROOT),
            )
            result = subprocess.run(
                [sys.executable, "-m", "jobs.environment", "--json", str(path)],
                env=environment,
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            added = json.loads(result.stdout)
            self.assertEqual(added["PGHOST"], "db.internal")
            self.assertEqual(added["PGPASSWORD"], "spaces # inside")
            self.assertNotIn("GROQ_API_KEY", added)
            self.assertNotIn("KEEP_EMPTY", added)
            self.assertFalse(marker.exists())

    def test_launcher_loads_the_project_file_from_another_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            environment = dict(
                os.environ,
                PYTHONPATH=str(ROOT),
                VENV_DIR=str(ROOT / ".venv"),
                EMBEDDING_VENV_DIR=str(ROOT / ".venv-embedding-onnx"),
                USE_HDFS_CACHE="0",
            )
            for name in ("DRY_RUN", "SPARK_EXECUTOR_INSTANCES", "EMBEDDING_BATCH_SIZE"):
                environment.pop(name, None)

            def launch(stage, *arguments):
                return subprocess.run(
                    [sys.executable, "-m", "jobs.launcher", stage, *arguments],
                    cwd=directory,
                    env=environment,
                    text=True,
                    capture_output=True,
                )

            result = launch(
                "ingest", "--dry-run", "--no-progress", "--max-accepted-articles", "23",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["target_articles"], 23)
            self.assertNotIn("GROQ_API_KEY", result.stdout + result.stderr)

            result = launch("embed", "--dry-run")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["embedding_batch_size"], 1)

            environment["EMBEDDING_BATCH_SIZE"] = "31"
            result = launch("embed", "--dry-run")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["embedding_batch_size"], 31)

            self.assertFalse((Path(directory) / ".build-tmp").exists())


if __name__ == "__main__":
    unittest.main()
