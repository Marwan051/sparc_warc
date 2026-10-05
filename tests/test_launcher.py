import os
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class LauncherTests(unittest.TestCase):
    def test_all_launchers_share_packaging_and_preserve_submission_policy(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            bin_dir = temporary / 'bin'
            bin_dir.mkdir()
            # Exercise the real launcher and ZIP; replace only expensive venv
            # packing and external Spark submission with local recorders.
            python = bin_dir / 'python'
            python.write_text('#!' + sys.executable + '\n' + '''
import os,pathlib,sys
if sys.argv[1:3] == ['-m','venv_pack']:
    pathlib.Path(sys.argv[sys.argv.index('-o')+1]).write_bytes(b'test archive')
else:
    os.execv(sys.executable,[sys.executable]+sys.argv[1:])
''')
            python.chmod(0o755)
            (temporary / 'pyvenv.cfg').write_text('launcher-test=' + directory)
            submit = bin_dir / 'spark-submit'
            submit.write_text('#!' + sys.executable + '\n' + '''
import json,sys,zipfile
args=sys.argv[1:]
with zipfile.ZipFile(args[args.index('--py-files')+1]) as archive:
    names=archive.namelist()
print(json.dumps({'args':args,'files':names}))
''')
            submit.chmod(0o755)
            env = dict(os.environ, PATH=str(bin_dir)+':'+os.environ['PATH'],
                       VENV_DIR=directory, SPARK_HOME=directory, USE_HDFS_CACHE='0',
                       SPARK_EXECUTOR_INSTANCES='5')
            env.pop('DRY_RUN', None)
            archive_path = None
            try:
                for script, stage, extra in [('run_ingestion.sh','ingest',[]),
                                             ('run_chunking.sh','chunk',['--document-limit','2']),
                                             ('run_tagging.sh','tag',['--analysis-limit','3'])]:
                    with self.subTest(stage=stage):
                        result = subprocess.run(['bash', str(root/'scripts'/script), *extra],
                            cwd=directory, env=env, text=True, capture_output=True)
                        self.assertEqual(result.returncode, 0, result.stderr)
                        recorded = json.loads(result.stdout.splitlines()[-1])
                        args = recorded['args']
                        archive_path = Path(args[args.index('--archives')+1].split('#')[0])
                        self.assertIn('jobs/runtime.py', recorded['files'])
                        self.assertIn('jobs/batching.py', recorded['files'])
                        self.assertIn('scripts/'+stage+'.py', args)
                        self.assertEqual(args[args.index('--master')+1], 'yarn')
                        self.assertIn('spark.executor.instances=5', args)
                        self.assertIn('spark.dynamicAllocation.enabled=false', args)
                        if stage == 'ingest':
                            self.assertNotIn('spark.task.maxFailures=1', args)
                            self.assertNotIn('spark.speculation=false', args)
                        else:
                            self.assertIn('spark.task.maxFailures=1', args)
                            self.assertEqual(args[-2:], extra)
                        # Only this test's uniquely fingerprinted fake archive.
                        self.assertEqual(archive_path.read_bytes(), b'test archive')
                        archive_path.unlink()
                        archive_path = None
            finally:
                if archive_path is not None and archive_path.exists() and archive_path.read_bytes() == b'test archive':
                    archive_path.unlink()

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
