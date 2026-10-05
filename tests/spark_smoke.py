"""Local Spark integration smoke: real HTTP, extraction, Lingua, and PostgreSQL.

Run with spark-submit --master 'local[3]' --driver-memory 512m
--conf spark.eventLog.enabled=false tests/spark_smoke.py.
Requires WARC_TEST_DSN, and uses an isolated disposable schema.
"""
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import uuid
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pyspark.sql import SparkSession
import psycopg2
from tests.test_ingestion import make_warc
from ingestion import pipeline as job
from db import db_handler as db


def timed_chunk(task):
    import time
    from ingestion import pipeline
    start = time.time()
    result = pipeline.process_file_chunk(task)
    result['stats']['wall_start'] = start
    result['stats']['wall_end'] = time.time()
    return result


def main():
    dsn = os.environ['WARC_TEST_DSN']
    data = {f'/file-{i}.warc.gz': make_warc(12)[0] for i in range(3)}
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            body = data.get(self.path)
            if body is None:
                self.send_error(404); return
            value = self.headers.get('Range')
            offset = int(value.split('=')[1].split('-')[0]) if value else 0
            self.send_response(206 if offset else 200)
            self.send_header('Content-Length', str(len(body)-offset))
            self.send_header('ETag', 'test-v1')
            if offset:
                self.send_header('Content-Range', f'bytes {offset}-{len(body)-1}/{len(body)}')
            self.end_headers()
            self.wfile.write(body[offset:])
        def log_message(self, *args): pass
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    schema = 'spark_smoke_' + uuid.uuid4().hex
    admin = psycopg2.connect(dsn); admin.autocommit = True
    with admin.cursor() as cur: cur.execute('CREATE SCHEMA ' + schema)
    def connect(): return psycopg2.connect(dsn, options='-c search_path='+schema)
    spark = SparkSession.builder.appName('WARC-v2-fixture-smoke').getOrCreate()
    spark.sparkContext.setLogLevel('ERROR')
    # Imported task functions must be available to the real Python workers.
    code_directory = tempfile.TemporaryDirectory()
    code_archive = Path(code_directory.name) / 'project_code.zip'
    root = Path(__file__).resolve().parents[1]
    with zipfile.ZipFile(code_archive, 'w') as archive:
        for package in ('ingestion', 'db', 'chunking', 'tagging', 'jobs'):
            for source in (root / package).rglob('*.py'):
                archive.write(source, source.relative_to(root))
    spark.sparkContext.addPyFile(str(code_archive))
    try:
        with patch.object(db, 'get_connection', side_effect=connect), patch.object(job, 'get_spark_session', return_value=spark), \
             patch.object(spark, 'stop'), patch.object(job, 'process_file_chunk', timed_chunk):
            urls = [f'http://127.0.0.1:{server.server_port}{path}' for path in data]
            settings = job.load_config()
            settings.update(target_articles=7, per_file_target=3, worker_max_candidates=2,
                            max_files_per_round=3, use_trafilatura=True)
            with patch.object(job, 'load_config', return_value=settings), patch.object(job, 'fetch_manifest', return_value=urls):
                started = time.monotonic()
                assert job.run_streaming_pipeline() == 0
            with connect() as conn, conn.cursor() as cur:
                cur.execute('SELECT inserted_count FROM ingest_runs')
                assert cur.fetchone()[0] == 7
                cur.execute('SELECT inserted_count FROM ingest_run_files ORDER BY ordinal')
                counts = [row[0] for row in cur.fetchall()]
                assert sum(counts) == 7 and max(counts) <= 3, counts
                cur.execute('SELECT stats FROM ingest_chunks ORDER BY committed_at')
                stats = [row[0] for row in cur.fetchall()]
            first_wave = stats[:3]
            assert max(s['wall_start'] for s in first_wave) < min(s['wall_end'] for s in first_wave), first_wave
            print('SPARK_SMOKE_RESULT ' + json.dumps(dict(
                articles=7, per_file=counts, parallel_workers=len({s['worker_pid'] for s in first_wave}),
                seconds=round(time.monotonic()-started, 2),
                worker_peak_rss_mib=[s['python_peak_rss_mib'] for s in first_wave])))
    finally:
        spark.stop()
        code_directory.cleanup()
        server.shutdown(); server.server_close()
        with admin.cursor() as cur: cur.execute('DROP SCHEMA ' + schema + ' CASCADE')
        admin.close()


if __name__ == '__main__': main()
