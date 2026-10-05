"""Bounded task packing and independent, concurrently submitted Spark jobs."""

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import islice


def serialized_size(value):
    return len(json.dumps(value, ensure_ascii=False).encode("utf-8"))


def batches(items, max_items, max_bytes):
    batch, size = [], 2
    for item in items:
        item_size = serialized_size(item) + 2
        if item_size + 2 > max_bytes:
            raise ValueError(f"page {item['page_id']} exceeds task input-byte limit ({max_bytes})")
        if batch and (len(batch) >= max_items or size + item_size > max_bytes):
            yield batch
            batch, size = [], 2
        batch.append(item)
        size += item_size
    if batch:
        yield batch


def run_waves(spark, tasks, worker, commit, parallelism):
    """One partition/job per task lets completed batches commit independently.

    A wave has at most parallelism Spark jobs. Drain successful siblings before
    reporting failure/quota; do not cancel siblings and discard paid responses.
    """
    tasks = iter(tasks)
    completed = 0
    with ThreadPoolExecutor(max_workers=parallelism) as pool:
        while True:
            wave = list(islice(tasks, parallelism))
            if not wave:
                return completed, False
            futures = [pool.submit(_execute, spark, worker, task) for task in wave]
            failure, stop = None, False
            committed = set()
            def save(future):
                nonlocal completed, stop, failure
                try:
                    result = future.result()
                    commit(result)
                    completed += 1
                    stop = stop or result.get("quota_exhausted", False)
                except Exception as error:
                    failure = failure or error
                committed.add(future)
            try:
                for future in as_completed(futures):
                    save(future)
            except KeyboardInterrupt:
                # Finish the small active wave so completed paid responses are
                # persisted. A second interrupt still allows a forced exit.
                for future in futures:
                    if future not in committed:
                        save(future)
                raise
            if failure:
                raise failure
            if stop:
                return completed, True


def execute_batch(spark, tasks, worker):
    """Execute an allocated batch with one partition per task, in input order.

    Allocation, quota accounting, and commit policy belong to the caller.
    """
    if not tasks:
        return []
    return spark.sparkContext.parallelize(tasks, len(tasks)).map(worker).collect()


def _execute(spark, worker, task):
    return execute_batch(spark, [task], worker)[0]
