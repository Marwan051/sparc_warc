"""Exercise the CSV export without writing to a live database or HGFS."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


TABLES = ("websites", "authors", "pages", "metadata", "content",
          "chunk_materializations", "article_chunks", "chunk_analyses", "chunk_embeddings")


class ExportCsvTests(unittest.TestCase):
    def test_exports_enrichment_tables_and_preserves_old_files_on_failure(self):
        script = Path(__file__).resolve().parents[1] / "scripts/export_csv.sh"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bin_dir = root / "bin"
            bin_dir.mkdir()
            fake_psql = bin_dir / "psql"
            fake_psql.write_text(f"#!{sys.executable}\n" + '''
import os, re, sys
sql = sys.argv[sys.argv.index('-c') + 1]
match = re.search(r'FROM (\\w+)', sql)
table = match.group(1)
if os.environ.get('EXPORT_FAIL_TABLE') == table:
    sys.exit(1)
if sql.startswith('COPY '):
    print('column')
    print(table)
else:
    print('1')
''')
            fake_psql.chmod(0o755)
            csv_dir = root / "export's csv dir"
            dest_dir = root / "destination"
            env = dict(os.environ, PATH=str(bin_dir) + os.pathsep + os.environ["PATH"],
                       PGPASSWORD="test")
            command = ["bash", str(script), str(csv_dir), str(dest_dir)]
            result = subprocess.run(command, env=env, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            for table in TABLES:
                self.assertEqual((csv_dir / f"{table}.csv").read_text(), f"column\n{table}\n")
                self.assertEqual((dest_dir / f"{table}.csv").read_text(), f"column\n{table}\n")

            (csv_dir / "websites.csv").write_text("existing export\n")
            env["EXPORT_FAIL_TABLE"] = "chunk_embeddings"
            failed = subprocess.run(command, env=env, text=True, capture_output=True)
            self.assertNotEqual(failed.returncode, 0)
            self.assertEqual((csv_dir / "websites.csv").read_text(), "existing export\n")
            self.assertFalse(list(csv_dir.glob(".export-*")))
