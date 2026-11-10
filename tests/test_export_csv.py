"""Exercise the CSV export without writing to a live database or HGFS."""

import csv
import os
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from scripts import export_csv


TABLES = export_csv.TABLES
SAMPLE_TABLES = export_csv.SAMPLE_TABLES


class FakeCursor:
    def __init__(self, connection):
        self.connection = connection
        self.table = None
        self.result = []

    def __enter__(self):
        return self

    def __exit__(self, *exception):
        return False

    def copy_expert(self, statement, stream):
        table = re.search(r"FROM (\w+)", statement).group(1)
        if self.connection.fail_table == table:
            raise RuntimeError("simulated export failure")
        self.connection.copies.append((table, statement))
        stream.write("column\n" + table + "\n")

    def execute(self, statement, params=None):
        self.connection.statements.append(statement)
        if statement.startswith("SELECT setseed"):
            self.connection.seeds.append(params[0])
            self.result = [(None,)]
            return
        if statement.startswith(("DROP TABLE", "CREATE TEMP", "ANALYZE")):
            self.result = [(None,)]
            return
        if statement.startswith("INSERT INTO export_page_ids"):
            self.connection.staged_ids = params[0]
            self.result = [(None,)]
            return
        if "ORDER BY random()" in statement:
            self.table = "pages"
            limit = params[0]
            self.result = [(page_id,) for page_id in self.connection.page_ids[:limit]]
            return
        self.table = re.search(r"FROM (\w+)", statement).group(1)
        self.result = [(self.connection.counts.get(self.table, 0),)]

    def fetchone(self):
        return self.result[0]

    def fetchall(self):
        return self.result


class FakeConnection:
    def __init__(self, fail_table=None):
        self.fail_table = fail_table
        self.counts = {table: 3 for table in TABLES}
        self.page_ids = [11, 22, 33, 44]
        self.statements = []
        self.copies = []
        self.seeds = []
        self.staged_ids = None
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
            self.assertEqual(len(connection.copies), len(TABLES))

    def test_sample_exports_random_pages_without_embeddings(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            csv_dir = root / "exports"
            dest_dir = root / "share"
            connection = FakeConnection()
            connection.page_ids = [11, 22, 33, 44]

            with patch.dict(os.environ, {}, clear=False):
                code = export_csv.main(
                    ["--sample", "3", "--seed", "0.5", str(csv_dir), str(dest_dir)],
                    connect=lambda **settings: connection,
                )

            self.assertEqual(code, 0)
            self.assertTrue(connection.closed)
            self.assertEqual(connection.seeds, [0.5])
            self.assertTrue(any("ORDER BY random() LIMIT" in s
                                for s in connection.statements))

            exported = sorted(p.name for p in csv_dir.glob("*.csv"))
            self.assertEqual(exported, sorted(f"{t}.csv" for t in SAMPLE_TABLES))
            self.assertNotIn("chunk_embeddings.csv", exported)
            self.assertNotIn("chunk_embeddings.csv",
                             [p.name for p in dest_dir.glob("*.csv")])
            for table in SAMPLE_TABLES:
                self.assertEqual((dest_dir / f"{table}.csv").read_text(),
                                 "column\n" + table + "\n")

            copied_tables = [table for table, _ in connection.copies]
            self.assertEqual(copied_tables, list(SAMPLE_TABLES))
            self.assertEqual(connection.staged_ids, [11, 22, 33])
            statements = {table: statement for table, statement in connection.copies}
            self.assertIn("id IN (SELECT id FROM export_page_ids)",
                          statements["pages"])
            self.assertIn("page_id IN (SELECT id FROM export_page_ids)",
                          statements["metadata"])
            self.assertIn("JOIN export_page_ids e ON e.id = p.id",
                          statements["websites"])

    def test_sample_can_include_chunk_tables_but_not_embeddings(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            csv_dir = root / "exports"
            connection = FakeConnection()

            with patch.dict(os.environ, {}, clear=False):
                code = export_csv.main(
                    ["--sample", "2", "--include-chunks", str(csv_dir)],
                    connect=lambda **settings: connection,
                )

            self.assertEqual(code, 0)
            self.assertEqual(
                sorted(p.name for p in csv_dir.glob("*.csv")),
                sorted(f"{t}.csv" for t in export_csv.SAMPLE_TABLES_WITH_CHUNKS),
            )
            self.assertNotIn("chunk_embeddings.csv",
                             [p.name for p in csv_dir.glob("*.csv")])

    def test_sample_defaults_to_its_own_folder_and_skips_the_share(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            connection = FakeConnection()

            with patch.object(export_csv, "PROJECT_ROOT", root):
                with patch.dict(os.environ, {}, clear=False):
                    code = export_csv.main(
                        ["--rows", "2"],
                        connect=lambda **settings: connection,
                    )

            self.assertEqual(code, 0)
            sample_dir = root / "exports" / "sample-2"
            self.assertEqual(
                sorted(p.name for p in sample_dir.glob("*.csv")),
                sorted(f"{t}.csv" for t in SAMPLE_TABLES),
            )
            self.assertFalse((root / "share").exists())

    def test_zip_option_archives_exported_tables_and_copies_zip(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            csv_dir = root / "exports" / "sample"
            dest_dir = root / "share"
            connection = FakeConnection()

            with patch.dict(os.environ, {}, clear=False):
                code = export_csv.main(
                    ["--sample", "2", "--zip", str(csv_dir), str(dest_dir)],
                    connect=lambda **settings: connection,
                )

            self.assertEqual(code, 0)
            zip_path = csv_dir.parent / "sample.zip"
            self.assertTrue(zip_path.is_file())
            self.assertTrue((dest_dir / "sample.zip").is_file())

            with zipfile.ZipFile(zip_path) as archive:
                self.assertEqual(
                    sorted(archive.namelist()),
                    sorted(f"{table}.csv" for table in SAMPLE_TABLES),
                )
                self.assertEqual(archive.read("pages.csv"), b"column\npages\n")

    def test_custom_zip_path(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            csv_dir = root / "exports"
            zip_path = root / "archives" / "articles.zip"
            connection = FakeConnection()

            with patch.dict(os.environ, {}, clear=False):
                code = export_csv.main(
                    ["--sample", "2", "--zip-path", str(zip_path), str(csv_dir)],
                    connect=lambda **settings: connection,
                )

            self.assertEqual(code, 0)
            self.assertTrue(zip_path.is_file())
            with zipfile.ZipFile(zip_path) as archive:
                self.assertIn("metadata.csv", archive.namelist())

    def test_row_count_handles_content_fields_over_the_default_limit(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "content.csv"
            with open(path, "w", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(["page_id", "cleaned_text"])
                writer.writerow([1, "x" * 200_000])

            self.assertEqual(export_csv._count_rows(path), 1)

    def test_sample_must_be_positive(self):
        connection = FakeConnection()

        with patch.dict(os.environ, {}, clear=False):
            code = export_csv.main(
                ["--sample", "0"],
                connect=lambda **settings: connection,
            )

        self.assertEqual(code, 1)
        self.assertFalse(connection.closed)

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
