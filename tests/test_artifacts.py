"""Fingerprints, zip membership, cache reuse, and the HDFS command sequence."""

import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest
import zipfile

from jobs import artifacts


class ArtifactTests(unittest.TestCase):
    def test_venv_fingerprint_concatenates_the_same_inputs_in_the_same_order(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            requirements = root / "requirements"
            requirements.mkdir()
            (requirements / "base.txt").write_bytes(b"base\n")
            venv = root / ".venv"
            (venv / "bin").mkdir(parents=True)
            (venv / "pyvenv.cfg").write_text("home=/usr\n")
            python = venv / "bin" / "python"
            python.write_text(
                "#!" + sys.executable + "\n"
                + """
import pathlib
counter = pathlib.Path(__file__).with_suffix('.count')
seen = int(counter.read_text()) if counter.exists() else 0
counter.write_text(str(seen + 1))
if seen:
    print('3.13.0')
    print('/venv/bin/python')
else:
    print('A==1')
    print('B==2')
"""
            )
            python.chmod(0o755)

            expected = hashlib.sha256()
            expected.update(b"base\n")
            expected.update(b"home=/usr\n")
            expected.update(b"A==1\nB==2\n")
            expected.update(b"3.13.0\n/venv/bin/python\n")

            self.assertEqual(
                artifacts.venv_fingerprint("ingest", venv, root, os.environ),
                expected.hexdigest(),
            )

    def test_tree_fingerprint_matches_the_shell_pipeline(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sub").mkdir()
            (root / "a.txt").write_text("a")
            (root / "b.txt").write_text("b")
            (root / "sub" / "c.txt").write_text("c")
            (root / "ignored.jar").write_text("not a jar here")
            command = (
                f"find {shlex.quote(str(root))} -type f -print0 "
                "| sort -z | xargs -0 sha256sum | sha256sum | cut -d' ' -f1"
            )
            shell = subprocess.run(
                ["bash", "-c", command], text=True, capture_output=True,
                check=True, env=os.environ,
            ).stdout.strip()
            self.assertEqual(
                artifacts.tree_fingerprint(root, os.environ),
                shell,
            )

    def test_tree_fingerprint_maxdepth_one_selects_jars_only(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "a.jar").write_text("a")
            (root / "b.txt").write_text("b")
            command = (
                f"find {shlex.quote(str(root))} -maxdepth 1 -name '*.jar' -type f -print0 "
                "| sort -z | xargs -0 sha256sum | sha256sum | cut -d' ' -f1"
            )
            shell = subprocess.run(
                ["bash", "-c", command], text=True, capture_output=True,
                check=True, env=os.environ,
            ).stdout.strip()
            self.assertEqual(
                artifacts.tree_fingerprint(root, os.environ, maxdepth_one=True),
                shell,
            )

    def test_project_zip_contains_code_and_skips_caches_and_scripts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "jobs" / "__pycache__").mkdir(parents=True)
            (root / "jobs" / "a.py").write_text("a")
            (root / "jobs" / "__pycache__" / "a.pyc").write_bytes(b"cache")
            (root / "jobs" / "b.pyc").write_bytes(b"cache")
            (root / "db").mkdir()
            (root / "db" / "c.py").write_text("c")
            (root / "scripts").mkdir()
            (root / "scripts" / "d.py").write_text("d")
            destination = root / "project_code.zip"
            artifacts.write_project_zip(root, destination)
            with zipfile.ZipFile(destination) as archive:
                self.assertEqual(set(archive.namelist()), {"jobs/a.py", "db/c.py"})

    def test_venv_archive_is_reused_when_the_cache_file_exists(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            venv = root / "venv"
            (venv / "bin").mkdir(parents=True)
            python = venv / "bin" / "python"
            python.write_text(
                "#!" + sys.executable + "\n"
                + """
import pathlib, sys
pathlib.Path(sys.argv[sys.argv.index('-o') + 1]).write_bytes(b'archive')
"""
            )
            python.chmod(0o755)
            build = root / "build"
            build.mkdir()
            task = root / "pack-test"
            task.mkdir()

            archive = artifacts.ensure_venv_archive(
                venv, "fingerprint", build, task, os.environ,
            )
            self.assertEqual(archive.read_bytes(), b"archive")
            first = archive.stat().st_mtime_ns
            again = artifacts.ensure_venv_archive(
                venv, "fingerprint", build, task, os.environ,
            )
            self.assertEqual(again, archive)
            self.assertEqual(again.stat().st_mtime_ns, first)

    def test_hdfs_publish_uses_a_temporary_name_then_moves(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            log = root / "hdfs.log"
            binary = root / "hdfs"
            binary.write_text(
                "#!" + sys.executable + "\n"
                + """
import json, os, sys
open(os.environ['HDFS_LOG'], 'a').write(json.dumps(sys.argv[1:]) + '\\n')
arguments = sys.argv[2:]
if arguments[:2] == ['-test', '-e']:
    sys.exit(0 if os.environ.get('HDFS_EXISTS') == '1' else 1)
if arguments[0] == '-mv' and os.environ.get('HDFS_FAIL_MV') == '1':
    sys.exit(1)
sys.exit(0)
"""
            )
            binary.chmod(0o755)
            environment = dict(os.environ, HDFS_LOG=str(log))
            source = root / "source.tar.gz"
            source.write_bytes(b"source")
            task = root / "pack-test"
            task.mkdir()

            self.assertTrue(artifacts.publish_hdfs(
                str(binary), source, "/apps/venv.tar.gz", "/apps", task, environment,
            ))
            calls = [json.loads(line) for line in log.read_text().splitlines()]
            self.assertEqual(calls[0], ["dfs", "-test", "-e", "/apps/venv.tar.gz"])
            self.assertEqual(calls[1], ["dfs", "-mkdir", "-p", "/apps"])
            self.assertEqual(
                calls[2],
                ["dfs", "-put", str(source), "/apps/venv.tar.gz.upload-pack-test"],
            )
            self.assertEqual(
                calls[3],
                ["dfs", "-mv", "/apps/venv.tar.gz.upload-pack-test", "/apps/venv.tar.gz"],
            )

    def test_hdfs_publish_stops_when_the_destination_exists(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            log = root / "hdfs.log"
            binary = root / "hdfs"
            binary.write_text(
                "#!" + sys.executable + "\n"
                + """
import json, os, sys
open(os.environ['HDFS_LOG'], 'a').write(json.dumps(sys.argv[1:]) + '\\n')
sys.exit(0 if sys.argv[2:4] == ['-test', '-e'] else 1)
"""
            )
            binary.chmod(0o755)
            environment = dict(os.environ, HDFS_LOG=str(log), HDFS_EXISTS="1")
            self.assertTrue(artifacts.publish_hdfs(
                str(binary), root / "source", "/apps/venv.tar.gz", "/apps",
                root / "pack-test", environment,
            ))
            self.assertEqual(
                [json.loads(line) for line in log.read_text().splitlines()],
                [["dfs", "-test", "-e", "/apps/venv.tar.gz"]],
            )

    def test_unset_or_empty_use_hdfs_cache_means_enabled(self):
        self.assertTrue(artifacts.hdfs_enabled({}))
        self.assertTrue(artifacts.hdfs_enabled({"USE_HDFS_CACHE": ""}))
        self.assertFalse(artifacts.hdfs_enabled({"USE_HDFS_CACHE": "0"}))

    def test_hdfs_apps_dir_requires_user_unless_overridden(self):
        self.assertEqual(
            artifacts.hdfs_apps_dir({"USER": "alice"}),
            "/user/alice/apps/spark",
        )
        self.assertEqual(
            artifacts.hdfs_apps_dir({"HDFS_APPS_DIR": "/custom"}),
            "/custom",
        )
        with self.assertRaises(Exception):
            artifacts.hdfs_apps_dir({})


if __name__ == "__main__":
    unittest.main()
