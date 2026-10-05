"""Shared infrastructure must preserve each job's execution policy."""

import sys
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from jobs.batching import execute_batch
from jobs.runtime import start_spark, config
from ingestion.pipeline import load_config


class RuntimeTests(unittest.TestCase):
    def test_executor_count_defaults_concurrency_and_allows_overrides(self):
        for count in (None, '1', '5'):
            env = {} if count is None else {'SPARK_EXECUTOR_INSTANCES': count}
            with self.subTest(count=count), patch.dict('os.environ', env, clear=True):
                expected = int(count or 3)
                self.assertEqual(load_config()['max_files_per_round'], expected)
                for stage in ('chunk', 'tag'):
                    self.assertEqual(config(stage, [])['parallel_tasks'], expected)
                    self.assertEqual(config(stage, ['--parallel-tasks', '7'])['parallel_tasks'], 7)
                with patch.dict('os.environ', {'MAX_FILES_PER_ROUND': '6', 'CHUNK_MAX_PARALLEL_TASKS': '4'}):
                    self.assertEqual(load_config()['max_files_per_round'], 6)
                    self.assertEqual(config('chunk', [])['parallel_tasks'], 4)
        for count in ('0', '-1', 'abc', '1.5', ''):
            with self.subTest(invalid=count), patch.dict('os.environ', {'SPARK_EXECUTOR_INSTANCES': count}, clear=True):
                with self.assertRaises(ValueError):
                    load_config()
                with self.assertRaises(ValueError):
                    config('chunk', [])

    def test_stage_specific_spark_settings(self):
        for stage in ('ingest', 'chunk', 'tag'):
            with self.subTest(stage=stage):
                builder = Mock()
                builder.appName.return_value = builder
                builder.config.return_value = builder
                builder.master.return_value = builder
                module = SimpleNamespace(SparkSession=SimpleNamespace(builder=builder))
                with patch.dict(sys.modules, {'pyspark.sql': module}), \
                     patch.dict('os.environ', {'SPARK_MASTER_URL': 'local[3]'}, clear=True):
                    result = start_spark(stage, {'backend': 'fake'})
                self.assertIs(result, builder.getOrCreate.return_value)
                builder.master.assert_called_once_with('local[3]')
                settings = dict(call.args for call in builder.config.call_args_list)
                self.assertEqual(settings['spark.python.worker.reuse'], 'true')
                if stage == 'ingest':
                    builder.appName.assert_called_once_with('CC-NEWS-Bounded-Ingest')
                    self.assertEqual(settings['spark.task.maxDirectResultSize'], '16m')
                    self.assertNotIn('spark.task.maxFailures', settings)
                    self.assertNotIn('spark.speculation', settings)
                    self.assertNotIn('spark.executorEnv.GROQ_API_KEY', settings)
                else:
                    self.assertEqual(settings['spark.task.maxFailures'], '1')
                    self.assertEqual(settings['spark.speculation'], 'false')

    def test_ingestion_batch_keeps_partition_count_and_order(self):
        spark = Mock()
        worker = Mock()
        tasks = [{'offset': 9}, {'offset': 3}]
        expected = [{'next_offset': 20}, {'next_offset': 10}]
        spark.sparkContext.parallelize.return_value.map.return_value.collect.return_value = expected
        self.assertIs(execute_batch(spark, tasks, worker), expected)
        spark.sparkContext.parallelize.assert_called_once_with(tasks, 2)
        spark.sparkContext.parallelize.return_value.map.assert_called_once_with(worker)
        self.assertEqual(execute_batch(spark, [], worker), [])
        self.assertEqual(spark.sparkContext.parallelize.call_count, 1)
