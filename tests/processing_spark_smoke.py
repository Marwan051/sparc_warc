"""Local Spark check of both executor functions, without database/provider calls.

Run from the project root: .venv/bin/python -m tests.processing_spark_smoke
Requires Java and a compatible PySpark installation; opens local Spark sockets.
"""

import os
import sys
from jobs.batching import run_waves
from tests.test_processing import source, task
from chunking.pipeline import process_batch as chunk_batch
from tagging.pipeline import process_batch as tag_batch


def main():
    os.environ.setdefault('PYSPARK_PYTHON',sys.executable)
    from pyspark.sql import SparkSession
    spark = (SparkSession.builder.master('local[3]').appName('processing-smoke')
             .config('spark.ui.enabled','false').config('spark.task.maxFailures','1')
             .config('spark.speculation','false').getOrCreate())
    try:
        materialized = []
        run_waves(spark,[task([source(i)]) for i in range(1,4)],chunk_batch,materialized.append,3)
        assert len(materialized) == 3
        tagging_tasks = []
        for result in materialized:
            document = result['documents'][0]
            assert len(document['chunks']) > 1
            items = [dict(page_id=document['page_id'],chunk_index=c['chunk_index'],text=c['chunk_text'],language='en',title='News')
                     for c in document['chunks'] if c['eligible']]
            tagging_tasks.append(task(items,backend='tests.fake_backend:FakeBackend',model='fake',batch_id=str(document['page_id'])))
        results = []
        run_waves(spark,tagging_tasks,tag_batch,results.append,3)
        assert len(results) == 3
        assert all(o['status'] == 'SUCCESS' for r in results for o in r['outcomes'])
        print('PASS: three Spark chunking tasks and three batch tagging tasks; no API calls')
    finally:
        spark.stop()


if __name__ == '__main__':
    main()
