"""The launcher preserves packaging, submission policy, and measured output."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from jobs import artifacts


ROOT = Path(__file__).resolve().parents[1]
BASELINE = json.loads((ROOT / "tests/fixtures/launch_baseline.json").read_text())


def make_venv(directory):
    """A stand-in environment: real Python for imports, stub for venv_pack."""
    binary = directory / "bin"
    binary.mkdir(parents=True, exist_ok=True)
    python = binary / "python"
    python.write_text(
        "#!" + sys.executable + "\n"
        + """
import os, pathlib, sys
arguments = sys.argv[1:]
if arguments[:2] == ['-m', 'venv_pack']:
    pathlib.Path(arguments[arguments.index('-o') + 1]).write_bytes(b'test archive')
elif arguments and arguments[0] == '-c' and any(
        name in arguments[1]
        for name in ('numpy', 'onnxruntime', 'transformers', 'pgvector')):
    pass
else:
    os.execv(sys.executable, [sys.executable] + arguments)
"""
    )
    python.chmod(0o755)
    (directory / "pyvenv.cfg").write_text("launcher-test=1\n")
    submit = binary / "spark-submit"
    submit.write_text(
        "#!" + sys.executable + "\n"
        + """
import json, sys, zipfile
arguments = sys.argv[1:]
with zipfile.ZipFile(arguments[arguments.index('--py-files') + 1]) as archive:
    names = archive.namelist()
print(json.dumps({'args': arguments, 'files': names}))
"""
    )
    submit.chmod(0o755)
    return directory


def run(arguments, cwd, environment):
    return subprocess.run(
        [sys.executable, "-m", "jobs.launcher", *arguments],
        cwd=cwd,
        env=environment,
        text=True,
        capture_output=True,
    )


class LauncherTests(unittest.TestCase):
    def test_all_stages_share_packaging_and_submission_policy(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            make_venv(work)
            environment = dict(
                os.environ,
                PATH=str(work / "bin") + os.pathsep + os.environ["PATH"],
                VENV_DIR=str(work),
                EMBEDDING_VENV_DIR=str(work),
                SPARK_HOME=str(work),
                USE_HDFS_CACHE="0",
                SPARK_EXECUTOR_INSTANCES="5",
                PYTHONPATH=str(ROOT),
            )
            environment.pop("DRY_RUN", None)
            created = []
            try:
                for stage, extra in (
                    ("ingest", []),
                    ("chunk", ["--document-limit", "2"]),
                    ("tag", ["--analysis-limit", "3"]),
                ):
                    with self.subTest(stage=stage):
                        result = run([stage, *extra], work, environment)
                        self.assertEqual(result.returncode, 0, result.stderr)
                        recorded = json.loads(result.stdout.splitlines()[-1])
                        arguments = recorded["args"]
                        created.append(Path(arguments[arguments.index("--archives") + 1].split("#")[0]))

                        self.assertIn("jobs/runtime.py", recorded["files"])
                        self.assertIn("jobs/batching.py", recorded["files"])
                        self.assertIn("scripts/" + stage + ".py", arguments)
                        self.assertEqual(arguments[arguments.index("--master") + 1], "yarn")
                        self.assertIn("spark.executor.instances=5", arguments)
                        self.assertIn("spark.dynamicAllocation.enabled=false", arguments)
                        if stage == "ingest":
                            self.assertNotIn("spark.task.maxFailures=1", arguments)
                            self.assertNotIn("spark.speculation=false", arguments)
                        else:
                            self.assertIn("spark.task.maxFailures=1", arguments)
                            self.assertIn("spark.speculation=false", arguments)
                            self.assertEqual(arguments[-len(extra):], extra)
                        self.assertEqual(created[-1].read_bytes(), b"test archive")

                result = run(
                    ["chunk", "--executor-instances", "2", "--parallel-tasks", "4"],
                    work,
                    environment,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                recorded = json.loads(result.stdout.splitlines()[-1])
                self.assertIn("spark.executor.instances=2", recorded["args"])
                created.append(Path(
                    recorded["args"][recorded["args"].index("--archives") + 1].split("#")[0]
                ))
            finally:
                for path in created:
                    if path.exists() and path.read_bytes() == b"test archive":
                        path.unlink()

    def test_dry_runs_match_the_measured_baseline(self):
        before = set((ROOT / ".build-tmp").glob("pack-*"))
        environment = dict(
            os.environ,
            VENV_DIR=str(ROOT / ".venv"),
            EMBEDDING_VENV_DIR=str(ROOT / ".venv-embedding-onnx"),
            USE_HDFS_CACHE="0",
        )
        for name in ("DRY_RUN", "SPARK_EXECUTOR_INSTANCES", "YEAR", "MONTH",
                     "NUM_FILES", "MAX_ACCEPTED_ARTICLES"):
            environment.pop(name, None)
        cases = {
            "ingest": ["--dry-run", "--no-progress", "--max-accepted-articles", "17"],
            "chunk": ["--dry-run"],
            "tag": ["--dry-run"],
            "embed": ["--dry-run"],
        }
        for stage, extra in cases.items():
            with self.subTest(stage=stage):
                result = run([stage, *extra], ROOT, environment)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout), BASELINE["dry_run"][stage])
        self.assertEqual(set((ROOT / ".build-tmp").glob("pack-*")), before)

    def test_venv_fingerprints_match_the_measured_baseline(self):
        environments = {
            "ingest": ROOT / ".venv",
            "chunk": ROOT / ".venv",
            "tag": ROOT / ".venv",
            "embed": ROOT / ".venv-embedding-onnx",
        }
        for stage, venv in environments.items():
            if not (venv / "bin" / "python").is_file():
                self.skipTest(f"missing {venv}")
            with self.subTest(stage=stage):
                self.assertEqual(
                    artifacts.venv_fingerprint(stage, venv, ROOT, os.environ),
                    BASELINE["venv_fingerprints"][stage],
                )

    def test_error_paths_and_codes(self):
        environment = dict(os.environ, VENV_DIR=str(ROOT / ".venv"))

        result = run([], ROOT, environment)
        self.assertEqual(result.returncode, 1)
        self.assertIn("expected ingest, chunk, tag, or embed", result.stderr)

        result = run(["bogus"], ROOT, environment)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout + result.stderr, "")

        result = run(["ingest", "--dry-run"], ROOT, dict(environment, VENV_DIR="/nonexistent"))
        self.assertEqual(result.returncode, 1)
        self.assertIn("Missing virtual environment", result.stderr)

        result = run(
            ["embed", "--dry-run"], ROOT,
            dict(environment, EMBEDDING_VENV_DIR="/nonexistent"),
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Missing virtual environment: /nonexistent", result.stderr)

        result = run(
            ["embed", "--help"], ROOT,
            dict(environment, EMBEDDING_VENV_DIR="/nonexistent"),
        )
        self.assertEqual(result.returncode, 1)

    def test_dry_run_never_packages_kills_spark_or_prints_secrets(self):
        before = set((ROOT / ".build-tmp").glob("pack-*"))
        with tempfile.TemporaryDirectory() as directory:
            for name in ("spark-submit", "hdfs", "zip"):
                executable = Path(directory) / name
                executable.write_text("#!/bin/sh\nexit 99\n")
                executable.chmod(0o755)
            environment = dict(
                os.environ,
                PATH=directory + os.pathsep + os.environ["PATH"],
                VENV_DIR=str(ROOT / ".venv"),
                EMBEDDING_VENV_DIR=str(ROOT / ".venv-embedding-onnx"),
                USE_HDFS_CACHE="0",
                GROQ_API_KEY="secret-that-must-not-be-printed",
            )
            environment.pop("DRY_RUN", None)
            environment.pop("SPARK_EXECUTOR_INSTANCES", None)

            result = run(["tag", "--dry-run"], ROOT, environment)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('"dry_run": true', result.stdout)
            self.assertNotIn("secret-that-must-not-be-printed", result.stdout + result.stderr)

            result = run(
                ["ingest", "--dry-run", "--no-progress", "--max-accepted-articles", "17"],
                ROOT,
                environment,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["target_articles"], 17)
        self.assertEqual(set((ROOT / ".build-tmp").glob("pack-*")), before)


if __name__ == "__main__":
    unittest.main()
