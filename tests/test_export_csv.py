"""Exercise the CSV export without writing to a live database or HGFS."""

import os
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

from scripts import export_csv


TABLES = export_csv.TABLES


class FakeCursor:
    def __init__(self, connection):
        self.connection = connection
        self.table = None

    def __enter__(self):
        return self

    def __exit__(self, *exception):
        return False

    def copy_expert(self, statement, stream):
        table = re.search(r"FROM (\w+)", statement).group(1)
        if self.connection.fail_table == table:
            raise RuntimeError("simulated export failure")
        stream.write("column\n" + table + "\n")

    def execute(self, statement):
        self.table = re.search(r"FROM (\w+)", statement).group(1)
        self.connection.statements.append(statement)

    def fetchone(self):
        return (self.connection.counts.get(self.table, 0),)


class FakeConnection:
    def __init__(self, fail_table=None):
        self.fail_table = fail_table
        self.counts = {table: 3 for table in TABLES}
        self.statements = []
        self.closed = False

    def cursor(self):
        return FakeCursor(self)

    def close(self):
        self.closed = True


class ExportCsvTests(unittest.TestCase):
    def test_exports_enrichment_tables_and_copies_them(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            csv_dir = root / "exports"
            dest_dir = root / "share"
            connection = FakeConnection()
            calls = []

            def connect(**settings):
                calls.append(settings)
                return connection

            with patch.dict(os.environ, {
                "PGHOST": "db.internal",
                "PGPORT": "6000",
                "PGDATABASE": "news",
                "PGUSER": "exporter",
                "PGPASSWORD": "super-secret",
            }, clear=False):
                code = export_csv.main([str(csv_dir), str(dest_dir)], connect=connect)

            self.assertEqual(code, 0)
            self.assertTrue(connection.closed)
            self.assertEqual(calls[0]["host"], "db.internal")
            self.assertEqual(calls[0]["port"], "6000")
            self.assertEqual(calls[0]["dbname"], "news")
            self.assertEqual(calls[0]["user"], "exporter")
            self.assertEqual(calls[0]["password"], "super-secret")

            for table in TABLES:
                expected = "column\n" + table + "\n"
                self.assertEqual((csv_dir / f"{table}.csv").read_text(), expected)
                self.assertEqual((dest_dir / f"{table}.csv").read_text(), expected)
            self.assertEqual(sorted(p.name for p in csv_dir.glob(".export-*")), [])
            self.assertEqual(len(connection.statements), len(TABLES))

    def test_failure_leaves_the_previous_export_alone(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            csv_dir = root / "exports"
            csv_dir.mkdir()
            previous = csv_dir / "websites.csv"
            previous.write_text("old export\n")
            connection = FakeConnection(fail_table="chunk_embeddings")

            with patch.dict(os.environ, {}, clear=False):
                code = export_csv.main(
                    [str(csv_dir), str(root / "share")],
                    connect=lambda **settings: connection,
                )

            self.assertEqual(code, 1)
            self.assertEqual(previous.read_text(), "old export\n")
            self.assertEqual(sorted(p.name for p in csv_dir.glob(".export-*")), [])
            self.assertFalse((root / "share").exists())
            self.assertTrue(connection.closed)

    def test_defaults_match_the_shell_script(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            connection = FakeConnection()
            calls = []

            def connect(**settings):
                calls.append(settings)
                return connection

            with patch.dict(os.environ, {}, clear=False):
                for name in ("PGHOST", "PGPORT", "PGDATABASE", "PGUSER", "PGPASSWORD"):
                    os.environ.pop(name, None)
                code = export_csv.main(
                    [str(root / "exports"), str(root / "share")],
                    connect=connect,
                )

            self.assertEqual(code, 0)
            self.assertEqual(calls[0], {
                "host": "localhost",
                "port": "5432",
                "dbname": "warcdb",
                "user": "warc_user",
                "password": "password",
            })


if __name__ == "__main__":
    unittest.main()
