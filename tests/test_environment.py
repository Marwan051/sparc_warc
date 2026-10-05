"""Dotenv defaults are shared, non-executable, and weaker than explicit env."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from jobs.environment import load_environment


class EnvironmentTests(unittest.TestCase):
    def test_defaults_quotes_existing_empty_values_and_no_shell_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / '.env'
            marker = Path(directory) / 'must-not-exist'
            path.write_text('PGHOST=db.internal\nPGPASSWORD="spaces # inside"\n'
                            'GROQ_API_KEY=file-key\nKEEP_EMPTY=file-value\n'
                            f'COMMAND=$(touch {marker})\n')
            with patch.dict(os.environ, {'GROQ_API_KEY':'explicit-key','KEEP_EMPTY':''}, clear=True):
                load_environment(path)
                self.assertEqual(os.environ['PGHOST'], 'db.internal')
                self.assertEqual(os.environ['PGPASSWORD'], 'spaces # inside')
                self.assertEqual(os.environ['GROQ_API_KEY'], 'explicit-key')
                self.assertEqual(os.environ['KEEP_EMPTY'], '')
                self.assertFalse(marker.exists())

    def test_missing_file_is_optional(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {}, clear=True):
            load_environment(Path(directory)/'absent')
            self.assertEqual(dict(os.environ), {})

    def test_all_launchers_load_project_file_from_another_directory(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)/'project'
            (project/'scripts').mkdir(parents=True)
            (project/'jobs').mkdir()
            for name in ('run_processing.sh','run_ingestion.sh','run_chunking.sh','run_tagging.sh'):
                shutil.copyfile(root/'scripts'/name, project/'scripts'/name)
            shutil.copyfile(root/'jobs/environment.py', project/'jobs/environment.py')
            (project/'.env').write_text('DRY_RUN=1\nMAX_ACCEPTED_ARTICLES=23\n'
                                       'CHUNK_ITEMS_PER_TASK=7\nTAG_ITEMS_PER_TASK=8\n'
                                       'GROQ_API_KEY=secret-that-must-not-be-printed\n')
            env = {'PATH':os.environ['PATH'], 'PYTHONPATH':str(root),
                   'VENV_DIR':str(Path(sys.executable).parent.parent)}
            cases = [('run_ingestion.sh', [], 'target_articles',23),
                     ('run_chunking.sh', [], 'items_per_task',7),
                     ('run_tagging.sh', ['--items-per-task','4'], 'items_per_task',4)]
            for name,args,key,expected in cases:
                result = subprocess.run(['bash',str(project/'scripts'/name),*args],
                                        cwd=directory,env=env,text=True,capture_output=True)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertEqual(json.loads(result.stdout)[key],expected)
                self.assertNotIn('secret-that-must-not-be-printed',result.stdout+result.stderr)
                self.assertFalse((project/'.build-tmp').exists())
            env['MAX_ACCEPTED_ARTICLES'] = '11'
            result = subprocess.run(['bash',str(project/'scripts/run_ingestion.sh')],
                                    cwd=directory,env=env,text=True,capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads(result.stdout)['target_articles'],11)
