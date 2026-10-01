import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class LauncherTests(unittest.TestCase):
    def test_dry_run_never_packages_or_submits(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            for command in ('spark-submit', 'zip', 'hdfs'):
                executable = Path(directory) / command
                executable.write_text('#!/bin/sh\nexit 99\n')
                executable.chmod(0o755)
            env = dict(os.environ, PATH=directory+':'+os.environ['PATH'], DRY_RUN='1',
                       VENV_DIR=str(Path(sys.executable).absolute().parent.parent),
                       MAX_ACCEPTED_ARTICLES='17')
            result = subprocess.run(
                ['bash', str(root / 'scripts/run_ingestion.sh')], cwd=directory,
                env=env, text=True, capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('"target_articles": 17', result.stdout)
