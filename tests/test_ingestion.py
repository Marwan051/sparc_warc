"""Run with python -m unittest discover -s tests -v.

Set WARC_TEST_DSN to a disposable database for PostgreSQL integration tests.
Each test creates and drops its own schema; production tables are untouched.
"""
import copy
import gzip
import io
import json
import os
import tempfile
import unittest
import uuid
from unittest.mock import patch

from warcio.warcwriter import WARCWriter
from warcio.statusandheaders import StatusAndHeaders
import psycopg2

import stream_to_db as job
from db import db_handler as db
from parsers.parsers import parse_warc_records_streaming, ValidatedGzipStream
from extractors.extractors import extract_html_fields, _language_sample
from utils import decode_and_validate


def make_warc(count=6, payload=None, content_type='text/html', http_encoding=None):
    output = io.BytesIO()
    writer = WARCWriter(output, gzip=True)
    offsets = []
    for i in range(count):
        offsets.append(output.tell())
        body = payload if payload is not None else ('<html><body><p>' + ('English article number %s. ' % i) * 100 + '</p></body></html>').encode()
        headers = [('Content-Type', content_type)]
        if http_encoding:
            headers.append(('Content-Encoding', http_encoding))
        record = writer.create_warc_record('https://example.com/article/' + str(i), 'response',
            payload=io.BytesIO(body), http_headers=StatusAndHeaders('200 OK', headers, protocol='HTTP/1.1'))
        writer.write_record(record)
        record.raw_stream.close()
    return output.getvalue(), offsets


class Response(io.BytesIO):
    def __init__(self, data, offset=0, ranged=True, size=True):
        super().__init__(data[offset:] if ranged else data)
        self.status = 206 if offset and ranged else 200
        self.headers = {'ETag': 'fixture-v1'}
        if size:
            self.headers['Content-Length'] = str(len(data) - offset if ranged else len(data))
        if self.status == 206:
            self.headers['Content-Range'] = f'bytes {offset}-{len(data)-1}/{len(data)}'


def config(**kwargs):
    with patch.dict(os.environ, {}, clear=True):
        result = job.load_config()
    result.update(kwargs)
    return result


def task(**kwargs):
    result = dict(file_url='https://example.com/test.warc.gz', start_offset=0,
                  chunk_id=uuid.uuid4().hex, candidate_limit=2, max_result_bytes=4*1024*1024,
                  max_input_bytes=32*1024*1024, max_seconds=120, max_html_bytes=2*1024*1024,
                  max_article_bytes=512*1024, min_word_count=10, max_retries=1,
                  use_trafilatura=False, lingua_min_confidence=.5)
    result.update(kwargs)
    return result


def worker(data, work=None, ranged=True, language='en', size=True):
    work = work or task()
    with patch.object(job.urllib.request, 'urlopen', return_value=Response(data, work['start_offset'], ranged, size)), \
         patch.object(job, 'detect_languages_batch', return_value=[language]):
        return job.process_file_chunk(work)


def candidate(record_id='one', **kwargs):
    result = dict(record_id=record_id, url='https://www.example.com/news', file_url='file-1',
                  cleaned_text='Article text', author='Author', language='en', headings=[], word_count=2)
    result.update(kwargs)
    return result


def chunk(candidates=None, start=0, end=100, eof=False, error=None, file='file-1'):
    return dict(chunk_id=uuid.uuid4().hex, file_url=file, start_offset=start, next_offset=end,
                candidates=[candidate()] if candidates is None else candidates, eof=eof,
                stats={}, error=error)


class UnitTests(unittest.TestCase):
    def test_defaults_and_validation(self):
        self.assertEqual(config()['num_files'], 15)
        self.assertIsNone(job._parse_num_files(''))
        for setting, value in [('MAX_ACCEPTED_ARTICLES', '-1'), ('MAX_FILES_PER_ROUND', '0'),
                               ('LINGUA_MIN_CONFIDENCE', 'nan'), ('MAX_RETRIES', '0'),
                               ('MAX_EXTRACTED_PER_ROUND', '50')]:
            with patch.dict(os.environ, {setting: value}, clear=True), self.assertRaises(ValueError):
                job.load_config()
        self.assertFalse(job._transient(job.urllib.error.HTTPError('x', 404, 'missing', {}, None)))
        self.assertTrue(job._transient(job.urllib.error.HTTPError('x', 503, 'unavailable', {}, None)))

    def test_allocations_respect_total_and_per_file(self):
        files = [dict(file_url=str(i), status='pending', eof=False, next_offset=0,
                      inserted_count=i, etag=None, last_modified=None) for i in range(3)]
        for total in (1, 2, 3, 7, 1000):
            run = dict(run_id='id', target_articles=total, inserted_count=0, per_file_target=4)
            tasks = job._allocate_tasks(config(), run, files, 0)
            self.assertLessEqual(sum(t['candidate_limit'] for t in tasks), total)
            for t in tasks:
                self.assertLessEqual(t['candidate_limit'], 4-int(t['file_url']))
        run['inserted_count'] = run['target_articles']
        self.assertEqual(job._allocate_tasks(config(), run, files, 0), [])

    def test_resume_restores_and_rejects_conflicting_filters(self):
        run = dict(manifest_id='2025/03', target_articles=7, per_file_target=3,
                   config=dict(min_word_count=123, use_trafilatura=False))
        with patch.dict(os.environ, {}, clear=True):
            restored = job.restore_run_config(config(), run)
        self.assertEqual((restored['year'], restored['month'], restored['min_word_count']), ('2025', '03', 123))
        with patch.dict(os.environ, {'MAX_ACCEPTED_ARTICLES': '9'}, clear=True), self.assertRaises(ValueError):
            job.restore_run_config(config(target_articles=9), run)

    def test_french_encoding_and_jsonld(self):
        prose = 'Les élèves français étudient les événements récents et découvrent une société développée. ' * 20
        html = ('<html><script type="application/ld+json">' + json.dumps({'@graph':[{'author':{'name':'Émile'}, 'datePublished':'2026-05-01'}]}) + '</script><body>' + prose + '</body></html>').encode()
        fields = extract_html_fields(dict(raw_bytes=html, url='https://example.com', warc_date=None), 10, False)
        self.assertEqual(fields['author'], 'Émile')
        self.assertEqual(fields['published_date'], '2026-05-01')
        self.assertIn('élèves', fields['clean_text'])
        self.assertEqual(decode_and_validate(prose.encode('cp1252'), 'cp1252')[1], 'success')

    def test_language_sample_has_no_overlap(self):
        text = ''.join(chr(0x1000+i) for i in range(2001))
        sample = _language_sample(text).replace(' ', '')
        self.assertEqual(len(sample), 2000)
        self.assertEqual(len(set(sample)), 2000)

    def test_small_chunks_advance_without_loss(self):
        data, offsets = make_warc()
        result = worker(data)
        self.assertEqual(result['next_offset'], offsets[2])
        second = worker(data, task(start_offset=result['next_offset']))
        third = worker(data, task(start_offset=second['next_offset']))
        self.assertEqual(len(result['candidates']+second['candidates']+third['candidates']), 6)
        self.assertTrue(third['eof'])
        self.assertEqual(third['next_offset'], len(data))

    def test_ignored_range_and_unknown_length(self):
        data, offsets = make_warc(4)
        result = worker(data, task(start_offset=offsets[2]), ranged=False, size=False)
        self.assertIsNone(result['error'])
        self.assertEqual(len(result['candidates']), 2)
        self.assertEqual(result['next_offset'], len(data))
        self.assertTrue(result['eof'])

    def test_empty_and_rejected_files_advance(self):
        data, _ = make_warc()
        result = worker(data, language='other')
        self.assertEqual(result['candidates'], [])
        self.assertTrue(result['eof'])
        self.assertEqual(result['next_offset'], len(data))
        result = worker(b'')
        self.assertTrue(result['eof'])

    def test_corrupt_or_truncated_gzip_never_marks_eof(self):
        data, _ = make_warc(2)
        corrupt = bytearray(data); corrupt[-6] ^= 255
        for broken in (data[:-15], bytes(corrupt), data+b'junk'):
            result = worker(broken, task(candidate_limit=100))
            self.assertTrue(result['error'])
            self.assertFalse(result['eof'])
            self.assertEqual(result['next_offset'], 0)
            self.assertEqual(result['candidates'], [])

    def test_oversize_decoded_http_body_is_skipped(self):
        data, _ = make_warc(1, payload=gzip.compress(b'x'*100000), http_encoding='gzip')
        result = worker(data, task(max_html_bytes=1024))
        self.assertIsNone(result['error'])
        self.assertEqual(result['stats']['oversized_html'], 1)
        self.assertEqual(result['candidates'], [])

    def test_result_budget_revisits_unreturned_record(self):
        data, offsets = make_warc(3)
        first = worker(data, task(candidate_limit=1))
        size = len(json.dumps(first['candidates'][0], ensure_ascii=False, default=str).encode())
        result = worker(data, task(candidate_limit=100, max_result_bytes=size+50, max_article_bytes=size+50))
        self.assertIsNone(result['error'])
        self.assertEqual(len(result['candidates']), 1)
        self.assertEqual(result['next_offset'], offsets[1])

    def test_changed_source_or_bad_range_is_rejected(self):
        data, offsets = make_warc(4)
        work = task(start_offset=offsets[1], etag='old-version')
        self.assertTrue(worker(data, work)['error'])
        response = Response(data, offsets[1])
        response.headers['Content-Range'] = 'bytes 1-10/100'
        with patch.object(job.urllib.request, 'urlopen', return_value=response):
            self.assertTrue(job.process_file_chunk(task(start_offset=offsets[1]))['error'])

    def test_long_non_html_sequence_checks_budget(self):
        data, offsets = make_warc(50, content_type='application/json')
        result = worker(data, task(max_input_bytes=100))
        self.assertFalse(result['eof'])
        self.assertEqual(result['candidates'], [])
        self.assertGreater(result['next_offset'], 0)
        self.assertLess(result['next_offset'], len(data))

    def test_truncated_http_transport(self):
        data, _ = make_warc(1)
        response = Response(data)
        response.headers['Content-Length'] = str(len(data)+20)
        with patch.object(job.urllib.request, 'urlopen', return_value=response):
            result = job.process_file_chunk(task())
        self.assertTrue(result['error'])
        self.assertFalse(result['eof'])

    def test_actual_language_detector(self):
        from extractors.extractors import detect_languages_batch
        texts = [
            'The government announced new measures to improve public transportation. Local officials said the changes would reduce traffic and make daily journeys easier for residents.',
            'Les élèves français étudient les événements récents et découvrent une société développée. Le gouvernement a annoncé de nouvelles mesures pour améliorer les transports publics.',
            'أعلنت الحكومة اليوم عن إجراءات جديدة لتحسين خدمات النقل العام في المدينة. وقال المسؤولون إن هذه الخطوات ستساهم في تخفيف الازدحام وتسهيل حركة المواطنين خلال ساعات العمل.',
            'El gobierno anunció nuevas medidas para mejorar el transporte público de la ciudad. Los funcionarios explicaron que los cambios reducirán el tráfico durante las horas de trabajo.',
            'دولت امروز اقدامات جدیدی را برای بهبود حمل و نقل عمومی اعلام کرد. مسئولان گفتند که این تغییرات به کاهش ترافیک و بهبود زندگی شهروندان کمک خواهد کرد.',
            'حکومت نے آج شہر میں عوامی نقل و حمل کو بہتر بنانے کے لیے نئے اقدامات کا اعلان کیا۔ حکام کا کہنا ہے کہ ان تبدیلیوں سے ٹریفک کم ہو گی اور شہریوں کو سہولت ملے گی۔',
        ]
        self.assertEqual(detect_languages_batch(texts), ['en','fr','ar','other','fa','ur'])


@unittest.skipUnless(os.environ.get('WARC_TEST_DSN'), 'set WARC_TEST_DSN to enable PostgreSQL tests')
class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.dsn = os.environ['WARC_TEST_DSN']
        self.schema = 'warc_test_' + uuid.uuid4().hex
        self.admin = psycopg2.connect(self.dsn)
        self.admin.autocommit = True
        with self.admin.cursor() as cur:
            cur.execute('CREATE SCHEMA ' + self.schema)
        def connect():
            return psycopg2.connect(self.dsn, options='-c search_path='+self.schema)
        self.connect = connect
        self.patch = patch.object(db, 'get_connection', side_effect=connect)
        self.patch.start()
        self.temp = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {'DEAD_LETTER_DIR':self.temp.name})
        self.env.start()
        db.init_db()
        self.run_id = db.create_run('2026/05', ['file-1', 'file-2'], 3, 2, {})

    def tearDown(self):
        self.patch.stop(); self.env.stop(); self.temp.cleanup()
        with self.admin.cursor() as cur:
            cur.execute('DROP SCHEMA ' + self.schema + ' CASCADE')
        self.admin.close()

    def test_exact_caps_duplicates_and_idempotent_receipt(self):
        first = chunk([candidate('a'), candidate('b')])
        self.assertEqual(db.commit_chunk(self.run_id, first, batch_size=1), 2)
        self.assertEqual(db.commit_chunk(self.run_id, first), 2)
        self.assertEqual(db.load_run(self.run_id)['inserted_count'], 2)
        duplicate = chunk([candidate('a')], file='file-2')
        self.assertEqual(db.commit_chunk(self.run_id, duplicate), 0)
        last = chunk([candidate('c')], file='file-2', start=100, end=200)
        self.assertEqual(db.commit_chunk(self.run_id, last), 1)
        self.assertEqual(db.load_run(self.run_id)['inserted_count'], 3)
        self.assertEqual(db.load_run_files(self.run_id)[0]['status'], 'quota_reached')

    def test_batch_duplicate_ids(self):
        result = chunk([candidate('a'), candidate('a')])
        self.assertEqual(db.commit_chunk(self.run_id, result), 1)

    def test_content_error_rolls_back_cursor_and_rows(self):
        original = db._insert_new_records
        def broken(cur, records):
            original(cur, records)
            raise RuntimeError('simulated write failure')
        with patch.object(db, '_insert_new_records', side_effect=broken), self.assertRaises(RuntimeError):
            db.commit_chunk(self.run_id, chunk())
        self.assertEqual(db.load_run(self.run_id)['inserted_count'], 0)
        self.assertEqual(db.load_run_files(self.run_id)[0]['next_offset'], 0)
        with self.connect() as conn, conn.cursor() as cur:
            cur.execute('SELECT count(*) FROM pages')
            self.assertEqual(cur.fetchone()[0], 0)

    def test_malformed_row_isolated(self):
        result = chunk([candidate('bad', url='not a URL'), candidate('good')])
        self.assertEqual(db.commit_chunk(self.run_id, result), 1)
        self.assertEqual(result['stats']['invalid_database_rows'], 1)
        self.assertEqual(len(os.listdir(self.temp.name)), 1)

    def test_uncertain_commit_recovered_after_reconnection(self):
        result = chunk()
        real = self.connect()
        class LostAcknowledgement:
            def __getattr__(self, name): return getattr(real, name)
            def commit(self):
                real.commit()
                raise psycopg2.OperationalError('lost commit acknowledgement')
        try:
            with self.assertRaises(psycopg2.OperationalError):
                db.commit_chunk(self.run_id, result, conn=LostAcknowledgement())
        finally:
            real.close()
        self.assertEqual(db.commit_chunk(self.run_id, result), 1)
        self.assertEqual(db.load_run(self.run_id)['inserted_count'], 1)

    def test_failed_file_retries_on_resume(self):
        result = chunk([], end=0, error='timeout')
        self.assertEqual(db.commit_chunk(self.run_id, result), 0)
        self.assertEqual(db.load_run_files(self.run_id)[0]['status'], 'failed')
        db.resume_run(self.run_id)
        self.assertEqual(db.load_run_files(self.run_id)[0]['status'], 'pending')
        self.assertEqual(db.commit_chunk(self.run_id, chunk()), 1)

    def test_stale_and_stalled_cursors_rejected(self):
        with self.assertRaises(ValueError): db.commit_chunk(self.run_id, chunk(start=5))
        with self.assertRaises(ValueError): db.commit_chunk(self.run_id, chunk([], end=0))

    def test_lock_excludes_second_coordinator(self):
        first = db.acquire_coordinator_lock('2026/05')
        try:
            with self.assertRaises(RuntimeError): db.acquire_coordinator_lock('2026/06')
        finally:
            first.close()

    def test_legacy_complete_preserved_partial_restarted(self):
        db.upsert_ingest_progress('2026/05', 'file-1', 99, 10, True)
        db.upsert_ingest_progress('2026/05', 'file-2', 88, 10, False)
        db.init_db()
        run = db.create_run('2026/05', ['file-1','file-2'], 5, 0, {})
        files = db.load_run_files(run)
        self.assertTrue(files[0]['eof'])
        self.assertEqual(files[1]['next_offset'], 0)

    def test_new_run_reuses_verified_partial_checkpoint(self):
        db.commit_chunk(self.run_id, chunk())
        later = db.create_run('2026/05', ['file-1'], 10, 0, {})
        self.assertEqual(db.load_run_files(later)[0]['next_offset'], 100)
        self.assertEqual(db.load_run(later)['inserted_count'], 0)

    def test_overquota_chunk_is_not_silently_discarded(self):
        with self.assertRaises(ValueError):
            db.commit_chunk(self.run_id, chunk([candidate('a'),candidate('b'),candidate('c')], eof=True))
        self.assertEqual(db.load_run_files(self.run_id)[0]['next_offset'], 0)

    def test_driver_shortfall_failure_and_resume(self):
        class RDD:
            def __init__(self, data): self.data = data
            def map(self, fn): return RDD([fn(row) for row in self.data])
            def collect(self): return self.data
        class Spark:
            def __init__(self): self.sparkContext = self
            def setLogLevel(self, level): pass
            def parallelize(self, data, size): return RDD(data)
            def stop(self): pass
        def failed_task(t):
            return dict(chunk_id=t['chunk_id'],file_url=t['file_url'],start_offset=t['start_offset'],
                        next_offset=t['start_offset'],candidates=[],stats={},eof=False,error='timeout')
        def eof_task(t):
            result = failed_task(t)
            result.update(next_offset=100,eof=True,error=None)
            return result
        with patch.object(job,'load_config',return_value=config(resume_run_id=self.run_id)), \
             patch.object(job,'get_spark_session',return_value=Spark()), \
             patch.object(job,'process_file_chunk',side_effect=failed_task):
            self.assertEqual(job.run_streaming_pipeline(),1)
        with patch.object(job,'load_config',return_value=config(resume_run_id=self.run_id)), \
             patch.object(job,'get_spark_session',return_value=Spark()), \
             patch.object(job,'process_file_chunk',side_effect=eof_task):
            self.assertEqual(job.run_streaming_pipeline(),2)


if __name__ == '__main__':
    unittest.main()
