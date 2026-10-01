"""Exercise real launcher packaging and relocated imports without starting YARN."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
build = root / '.build-tmp'
build.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(dir=build) as temporary:
    temporary = Path(temporary)
    submit = temporary / 'spark-submit'
    submit.write_text('''#!/usr/bin/env python3
import json,os,pathlib,subprocess,sys,tarfile,tempfile
args=sys.argv[1:]
archive=args[args.index('--archives')+1].split('#')[0]
code=args[args.index('--py-files')+1]
with tempfile.TemporaryDirectory(dir=os.environ['PACKAGE_TEST_TMP']) as unpacked:
    with tarfile.open(archive) as tar: tar.extractall(unpacked,filter='fully_trusted')
    env=dict(os.environ,PYTHONPATH=code)
    python=str(pathlib.Path(unpacked)/'bin/python')
    subprocess.run([python,'-c','from ingestion.extraction import detect_languages_batch; from ingestion.warc import ValidatedGzipStream; from db.db_handler import commit_chunk; import trafilatura; assert detect_languages_batch(["The government announced new measures to improve public transportation and reduce traffic in the city."]) == ["en"]; print("RELOCATED_WORKER_IMPORTS_OK")'],cwd=unpacked,env=env,check=True)
print('PACKAGING_OK '+json.dumps({'archive':archive,'arguments':args[:8]}))
''')
    submit.chmod(0o755)
    env = dict(os.environ, PATH=str(temporary)+':'+os.environ['PATH'], USE_HDFS_CACHE='0',
               PACKAGE_TEST_TMP=str(build), VENV_DIR=str(root/'.venv'))
    env.pop('DRY_RUN', None)
    subprocess.run(['bash',str(root/'scripts/run_ingestion.sh')],cwd=root,env=env,check=True)
