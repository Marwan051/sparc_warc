import importlib.util
import os
import json
import tempfile
import uuid
import subprocess
import threading
import unittest
from unittest.mock import patch, Mock

from jobs.batching import batches, run_waves
from jobs.runtime import config
from tagging.pipeline import process_batch as tag_batch


def source(page_id=1, text=None):
    return {"page_id": page_id, "text": text or "The government announced new public transport measures today. " * 40,
            "source": "https://example.com/news", "title": "News", "language": "en"}


def task(items, **kwargs):
    return dict(items=items, result_bytes=4*1024*1024, **kwargs)


class BatchTests(unittest.TestCase):
    def test_count_and_byte_bounds_and_oversize(self):
        items = [source(i, "a"*100) for i in range(5)]
        result = list(batches(items, 2, 1000))
        self.assertEqual([len(x) for x in result], [2,2,1])
        self.assertEqual([x for b in result for x in b], items)
        with self.assertRaises(ValueError):
            list(batches(items, 2, 50))

    def test_finished_batch_commits_before_slow_sibling_and_quota_stops_next_wave(self):
        committed = threading.Event()
        class RDD:
            def __init__(self, values): self.values = values
            def map(self, fn): self.fn = fn; return self
            def collect(self): return [self.fn(x) for x in self.values]
        spark = Mock()
        spark.sparkContext.parallelize.side_effect = lambda xs, n: RDD(xs)
        def worker(value):
            if value == 1:
                if not committed.wait(3): raise RuntimeError("commit was delayed")
            return {"value": value, "quota_exhausted": value == 0}
        rows = []
        def commit(result):
            rows.append(result['value'])
            committed.set()
        self.assertEqual(run_waves(spark, iter(range(6)), worker, commit, 3), (3, True))
        self.assertEqual(set(rows), {0,1,2})

    def test_failed_task_does_not_discard_successful_sibling(self):
        rows = []
        with patch('jobs.batching._execute', side_effect=lambda s,w,t: (_ for _ in ()).throw(ValueError('fail')) if t == 1 else {'n': t}):
            with self.assertRaisesRegex(ValueError, 'fail'):
                run_waves(None, [0,1,2,3], None, rows.append, 3)
        self.assertEqual({r['n'] for r in rows}, {0,2})

    def test_interrupt_drains_active_batches(self):
        rows = []
        with patch('jobs.batching._execute', side_effect=lambda s,w,t: {'n':t}), \
             patch('jobs.batching.as_completed', side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                run_waves(None, [0,1,2,3], None, rows.append, 3)
        self.assertEqual({r['n'] for r in rows}, {0,1,2})

    def test_backend_batch_and_quota_preserve_prior_outcome(self):
        items = [{"page_id": 1,"chunk_index": i,"text": text,"title":"","language":"en"}
                 for i,text in enumerate(['ok','error','quota','unreached'])]
        result = tag_batch(task(items, backend='tests.fake_backend:FakeBackend', model='fake', batch_id='b'))
        self.assertTrue(result['quota_exhausted'])
        self.assertEqual([o['status'] for o in result['outcomes']], ['SUCCESS','ERROR'])

    def test_cli_limits_and_dry_launcher(self):
        self.assertEqual(config('tag', ['--analysis-limit','7'])['analysis_limit'], 7)
        for script in ('run_chunking.sh','run_tagging.sh'):
            result = subprocess.run(['bash', 'scripts/'+script, '--dry-run'], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('"dry_run": true', result.stdout)


@unittest.skipUnless(importlib.util.find_spec('langchain_text_splitters'), 'install requirements/rag.txt')
class ChunkTests(unittest.TestCase):
    def test_indexing_hashes_and_filters(self):
        from chunking.pipeline import process_batch
        result = process_batch(task([source(1),source(2),source(3,'short'),source(4,'Read more » links')]))
        first,second,short,empty = result['documents']
        self.assertGreater(len(first['chunks']), 1)
        self.assertEqual([x['chunk_index'] for x in second['chunks']], list(range(len(second['chunks']))))
        self.assertFalse(short['chunks'][0]['eligible'])
        self.assertEqual(empty['chunks'], [])
        self.assertEqual(first, process_batch(task([source(1)]))['documents'][0])

    def test_metadata_is_not_mutated(self):
        from langchain_core.documents import Document
        from chunking.splitters import iter_document_chunks
        document = Document(page_content='text '*400, metadata={'doc_id':1})
        chunks = list(iter_document_chunks([document,document]))
        self.assertEqual(document.metadata, {'doc_id':1})
        self.assertEqual(sum(c.metadata['chunk_index'] == 0 for c in chunks), 2)

    def test_multilingual_cleaning_and_noise(self):
        from langchain_core.documents import Document
        from chunking.preprocessing import clean_article_text, noise_reason
        for text in ('أعلنت الحكومة عن تحسين النقل العام. ', 'Le gouvernement améliore les transports publics. ', 'The government improves public transport. '):
            self.assertEqual(clean_article_text(text+'Read more » links'), text.rstrip())
        for lang,text in [('ar','أعلنت الحكومة عن تحسين النقل العام. '),('fr','Le gouvernement améliore les transports publics. '),('en','The government improves public transport. ')]:
            self.assertIsNone(noise_reason(Document(page_content=text*15, metadata={'language':lang})))


@unittest.skipUnless(importlib.util.find_spec('langchain_groq'), 'install requirements/tagging-groq.txt')
class GroqTests(unittest.TestCase):
    def test_success_noise_invalid_retry_and_daily_quota(self):
        from tagging.backends.groq import GroqBackend
        from tagging.backends.groq_rules import ChunkAnalysis
        from tagging.contracts import AnalysisRequest
        request = AnalysisRequest(1,0,'Transport policy improved.','en','Title')
        with patch.dict(os.environ, {'GROQ_API_KEY':'fake','TAG_REQUEST_INTERVAL_SECONDS':'0'}), patch('tagging.backends.groq.time.sleep'):
            backend = GroqBackend('fake')
            try:
                chain = Mock()
                backend._chain = Mock(return_value=chain)
                chain.invoke.side_effect = [ChunkAnalysis(summary='Truncated',category='Other'), ChunkAnalysis(summary='Policy improved.',category='Politics',tags=['policy'])]
                batch = backend.analyze_batch([request])
                self.assertEqual(batch.outcomes[0].attempt_count, 2)
                self.assertEqual(batch.outcomes[0].status, 'SUCCESS')
                chain.invoke.side_effect = None
                chain.invoke.return_value = ChunkAnalysis(summary='NOT_ARTICLE: Navigation menu.',category='Other')
                self.assertEqual(backend.analyze_batch([request]).outcomes[0].status, 'NOISE')
                chain.invoke.side_effect = RuntimeError('tokens per day exceeded')
                result = backend.analyze_batch([request])
                self.assertTrue(result.quota_exhausted)
                self.assertEqual(result.outcomes, [])
            finally:
                backend.close()


@unittest.skipUnless(os.environ.get('WARC_TEST_DSN') and importlib.util.find_spec('langchain_text_splitters'), 'set WARC_TEST_DSN and install RAG dependencies')
class PersistenceTests(unittest.TestCase):
    def setUp(self):
        import psycopg2
        from db import db_handler, chunks, analyses
        self.db, self.chunks, self.analyses = db_handler, chunks, analyses
        self.schema = 'processing_test_' + uuid.uuid4().hex
        self.admin = psycopg2.connect(os.environ['WARC_TEST_DSN'])
        self.admin.autocommit = True
        with self.admin.cursor() as cur:
            cur.execute('CREATE SCHEMA ' + self.schema)
        def connect():
            return psycopg2.connect(os.environ['WARC_TEST_DSN'], options='-c search_path='+self.schema)
        self.connect = connect
        self.patches = [patch.object(module,'get_connection',side_effect=connect) for module in (db_handler,chunks,analyses)]
        for item in self.patches: item.start()
        self.conn = connect()
        db_handler.init_db(conn=self.conn)
        with self.conn, self.conn.cursor() as cur:
            for i in range(1,4):
                cur.execute("INSERT INTO pages(id,url) VALUES (%s,%s)", (i,f'https://example.com/{i}'))
                cur.execute("INSERT INTO content(page_id,cleaned_text) VALUES (%s,%s)", (i,source(i)['text']))
                cur.execute("INSERT INTO metadata(page_id,title,language) VALUES (%s,'News','en')", (i,))
        self.cfg = dict(chunking_version='test-v1',backend='fake',model='test',analysis_version='v1')

    def tearDown(self):
        self.conn.close()
        for item in reversed(self.patches): item.stop()
        with self.admin.cursor() as cur:
            cur.execute('DROP SCHEMA '+self.schema+' CASCADE')
        self.admin.close()

    def materialize(self):
        from chunking.pipeline import process_batch
        for result in process_batch(task([source(1),source(2),source(3)]))['documents']:
            self.chunks.commit_document(self.conn,'test-v1',result)

    def test_migration_repeat_materialization_drift_and_empty_receipt(self):
        from chunking.pipeline import process_batch
        self.db.init_db(conn=self.conn)
        self.materialize()
        initial = self.chunks.counts(self.conn,'test-v1')
        self.materialize()
        self.assertEqual(initial,self.chunks.counts(self.conn,'test-v1'))
        self.assertEqual(list(self.chunks.iter_pending_documents(self.conn,'test-v1')),[])
        drift = process_batch(task([source(1,'Changed body. '*100)]))['documents'][0]
        with self.assertRaisesRegex(ValueError,'drift'):
            self.chunks.commit_document(self.conn,'test-v1',drift)
        empty = process_batch(task([source(1,'Read more » links')]))['documents'][0]
        self.chunks.commit_document(self.conn,'empty-v1',empty)
        self.assertEqual(self.chunks.counts(self.conn,'empty-v1')['documents'],1)
        self.assertEqual(self.chunks.counts(self.conn,'empty-v1')['stored'],0)

    def test_batch_resume_retry_idempotency_export_and_versions(self):
        from dataclasses import asdict
        from tagging.contracts import AnalysisOutcome
        self.materialize()
        pending = list(self.analyses.iter_pending(self.cfg))
        keys = [(x['page_id'],x['chunk_index']) for x in pending]
        self.assertEqual(keys,sorted(keys))
        outcomes = [asdict(AnalysisOutcome(*keys[0],'SUCCESS',summary='Done.',category='Other',attempt_count=1)),
                    asdict(AnalysisOutcome(*keys[1],'ERROR',error='transient',attempt_count=2))]
        self.analyses.commit_batch(self.conn,self.cfg,'batch-1',outcomes)
        self.analyses.commit_batch(self.conn,self.cfg,'batch-1',outcomes)
        self.assertEqual(len(list(self.analyses.iter_pending(self.cfg))),len(pending)-2)
        self.assertEqual(len(list(self.analyses.iter_pending(self.cfg,retry_errors=True))),len(pending)-1)
        with self.conn.cursor() as cur:
            cur.execute('SELECT sum(attempt_count) FROM chunk_analyses')
            self.assertEqual(cur.fetchone()[0],3)
        self.conn.commit()
        outcomes[1].update(status='SUCCESS',summary='Recovered.',error=None,attempt_count=1)
        self.analyses.commit_batch(self.conn,self.cfg,'batch-2',[outcomes[1]])
        with tempfile.TemporaryDirectory() as directory:
            path = directory+'/results.json'
            self.analyses.export_json(self.cfg,path)
            with open(path) as stream: rows=json.load(stream)
            self.assertEqual(len(rows),2)
            self.assertEqual(rows[1]['summary'],'Recovered.')
            self.assertEqual(rows[0]['backend'],'fake')
        cfg = dict(self.cfg,model='new-model')
        self.assertEqual(len(list(self.analyses.iter_pending(cfg))),len(pending))

    def test_stage_locks(self):
        # Global advisory locks intentionally span schemas within a database.
        first = self.chunks.acquire_lock('chunking-test')
        try:
            with self.assertRaises(RuntimeError): self.chunks.acquire_lock('chunking-test')
            second = self.chunks.acquire_lock('tagging-test')
            second.close()
        finally:
            first.close()
