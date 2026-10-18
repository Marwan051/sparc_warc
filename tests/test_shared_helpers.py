"""Shared plumbing preserves lazy reads, bounds, and resource ownership."""

import argparse
import importlib.util
import os
import unittest
from contextlib import ExitStack
from unittest.mock import MagicMock, Mock, patch

from jobs.batching import batch_tasks, check_result_size, serialized_size
from jobs.validation import env_int, integer, positive_int


class ValidationTests(unittest.TestCase):
    def test_integer_boundaries_and_invalid_input(self):
        self.assertEqual(positive_int(" 2 "), 2)
        self.assertEqual(integer("0", name="LIMIT"), 0)
        self.assertEqual(integer("1024", name="BYTES", minimum=1024), 1024)
        for raw in ("", "abc", "1.5", "0", "-1"):
            with self.subTest(raw=raw), self.assertRaises(argparse.ArgumentTypeError):
                positive_int(raw)
        with self.assertRaisesRegex(ValueError, "BYTES must be at least 1024"):
            integer(1023, name="BYTES", minimum=1024)
        with self.assertRaisesRegex(ValueError, "LIMIT must be an integer"):
            integer(None, name="LIMIT")

    def test_environment_defaults_and_validation(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(env_int("COUNT", 3, minimum=1), 3)
            for raw in ("", "bad", "0", "-1"):
                with self.subTest(raw=raw), patch.dict(os.environ, {"COUNT": raw}):
                    with self.assertRaisesRegex(ValueError, "COUNT"):
                        env_int("COUNT", 3, minimum=1)


class TaskTests(unittest.TestCase):
    def test_tasks_are_lazy_and_result_boundary_is_inclusive(self):
        consumed = []
        def source():
            for page in range(5):
                consumed.append(page)
                yield {"page_id": page}
        factory = Mock(side_effect=lambda items: {"items": items})
        tasks = batch_tasks(source(), {"items_per_task": 2, "input_bytes": 1000}, factory)
        self.assertEqual(consumed, [])
        self.assertEqual(len(next(tasks)["items"]), 2)
        self.assertEqual(factory.call_count, 1)
        self.assertLess(len(consumed), 5)
        self.assertEqual([len(t["items"]) for t in tasks], [2, 1])
        result = {"text": "مرحبا"}
        size = serialized_size(result)
        check_result_size(result, size, "too large")
        with self.assertRaisesRegex(ValueError, "too large"):
            check_result_size(result, size - 1, "too large")


@unittest.skipUnless(importlib.util.find_spec("psycopg2"), "install base database dependencies")
class ResourceTests(unittest.TestCase):
    def test_processing_session_closes_on_failure_and_interruption(self):
        from jobs.runtime import processing_session
        for error in (None, RuntimeError("worker or commit failure"), KeyboardInterrupt()):
            with self.subTest(error=error), ExitStack() as stack:
                conn, spark = Mock(), Mock()
                stack.enter_context(patch("db.db_handler.init_db"))
                lock = stack.enter_context(patch("db.chunks.acquire_lock", return_value=conn))
                stack.enter_context(patch("jobs.runtime.start_spark", return_value=spark))
                def run():
                    with processing_session("tag", {}) as resources:
                        self.assertEqual(resources, (conn, spark))
                        if error is not None:
                            raise error
                if error is None:
                    run()
                else:
                    with self.assertRaises(type(error)):
                        run()
                lock.assert_called_once_with("tagging")
                spark.stop.assert_called_once()
                conn.close.assert_called_once()

    def test_startup_and_shutdown_failures_release_connection(self):
        from jobs.runtime import processing_session
        for startup in (True, False):
            with self.subTest(startup=startup), ExitStack() as stack:
                conn, spark = Mock(), Mock()
                stack.enter_context(patch("db.db_handler.init_db"))
                stack.enter_context(patch("db.chunks.acquire_lock", return_value=conn))
                start = stack.enter_context(patch("jobs.runtime.start_spark", return_value=spark))
                if startup:
                    start.side_effect = RuntimeError("startup")
                else:
                    spark.stop.side_effect = RuntimeError("shutdown")
                with self.assertRaises(RuntimeError):
                    with processing_session("embed", {}):
                        pass
                conn.close.assert_called_once()
                self.assertEqual(spark.stop.call_count, 0 if startup else 1)

    def test_streaming_cursor_cleanup_and_creation_failure(self):
        from db.db_handler import streaming_cursor
        for failure in (None, "execute", "cursor", "close"):
            with self.subTest(failure=failure):
                conn, cur = Mock(), Mock()
                conn.cursor.return_value = cur
                if failure == "cursor":
                    conn.cursor.side_effect = RuntimeError("cursor")
                elif failure:
                    getattr(cur, failure).side_effect = RuntimeError(failure)
                def read():
                    with streaming_cursor("source", itersize=25, connection_factory=lambda: conn) as cursor:
                        self.assertEqual(cursor.itersize, 25)
                        cursor.execute("SELECT 1")
                if failure:
                    with self.assertRaises(RuntimeError):
                        read()
                else:
                    read()
                conn.close.assert_called_once()
                self.assertEqual(cur.close.call_count, 0 if failure == "cursor" else 1)

    def test_pending_readers_close_on_early_exit(self):
        from db import chunks, analyses
        cases = (
            (chunks, lambda: chunks.iter_pending_documents(Mock(), "v1"), (1, "text", "url", None, None), 25),
            (analyses, lambda: analyses.iter_pending({"backend": "fake", "model": "m", "analysis_version": "a", "chunking_version": "v1"}), (1, 0, "text", None, None), 30),
        )
        for module, create, row, size in cases:
            with self.subTest(module=module.__name__):
                conn, cursor = Mock(), Mock()
                cursor.__iter__ = Mock(return_value=iter([row, row]))
                conn.cursor.return_value = cursor
                with patch.object(module, "get_connection", return_value=conn):
                    reader = create()
                    conn.cursor.assert_not_called()
                    next(reader)
                    self.assertEqual(cursor.itersize, size)
                    reader.close()
                cursor.close.assert_called_once()
                conn.close.assert_called_once()

    def test_pipeline_dry_runs_do_not_acquire_resources(self):
        from chunking import pipeline as chunk
        from tagging import pipeline as tag
        modules = [chunk, tag]
        if importlib.util.find_spec("numpy"):
            from embeddings import pipeline as embed
            modules.append(embed)
        for module in modules:
            with self.subTest(module=module.__name__), \
                    patch.object(module, "config", return_value={"dry_run": True}), \
                    patch.object(module, "report"), patch.object(module, "processing_session") as session:
                self.assertEqual(module.run([]), 0)
                session.assert_not_called()

    def test_tagging_tasks_keep_unique_ids_and_quota_exit(self):
        from tagging import pipeline
        cfg = {"dry_run": False, "chunking_version": "v1", "analysis_limit": None,
               "retry_errors": False, "items_per_task": 1, "input_bytes": 1000,
               "result_bytes": 1000, "backend": "fake", "model": "m",
               "parallel_tasks": 2, "export_json": None}
        source = ({"page_id": page} for page in (1, 2))
        session = MagicMock()
        session.__enter__.return_value = (Mock(), Mock())
        submitted = []
        def execute(spark, tasks, worker, commit, parallelism):
            submitted.extend(tasks)
            return 2, True
        with patch.object(pipeline, "config", return_value=cfg), \
                patch.object(pipeline, "processing_session", return_value=session), \
                patch.object(pipeline.analyses, "iter_pending", return_value=source), \
                patch.object(pipeline.analyses, "counts", return_value={}), \
                patch.object(pipeline, "report"), \
                patch.object(pipeline, "run_waves", side_effect=execute):
            self.assertEqual(pipeline.run([]), 2)
        self.assertEqual(len({task["batch_id"] for task in submitted}), 2)
        for task in submitted:
            self.assertEqual((task["backend"], task["model"], task["result_bytes"]), ("fake", "m", 1000))
