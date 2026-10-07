"""Check worker imports outside the checkout using the launcher's ZIP layout."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class PackagingTests(unittest.TestCase):
    def test_worker_package_imports_without_optional_rag_dependencies(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / 'project_code.zip'
            subprocess.run(
                ['zip', '-qr', str(archive), 'ingestion', 'db', 'chunking', 'tagging', 'jobs', '-x',
                 '*/__pycache__/*', '*.pyc'], cwd=root, check=True,
            )
            code = '''
import importlib.abc
import runpy
import sys

class NoRagDependencies(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.startswith(('langchain', 'groq', 'transformers')):
            raise ImportError('Optional RAG dependency imported by ingestion')

sys.meta_path.insert(0, NoRagDependencies())
from ingestion import pipeline
from ingestion.extraction import detect_languages_batch
from ingestion.warc import ValidatedGzipStream
from db.db_handler import commit_chunk
import chunking
import db
import tagging
import jobs
assert '.zip/' in pipeline.__file__, pipeline.__file__
assert pipeline.process_file_chunk.__module__ == 'ingestion.pipeline'
entry_point = sys.argv[1]
sys.argv = [entry_point]
runpy.run_path(entry_point, run_name='__main__')
'''
            result = subprocess.run(
                [sys.executable, '-c', code, str(root / 'scripts/ingest.py')], cwd=directory,
                env=dict(os.environ, PYTHONPATH=str(archive), DRY_RUN='1', MAX_ACCEPTED_ARTICLES='17'),
                text=True, capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('"target_articles": 17', result.stdout)
