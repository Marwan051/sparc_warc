"""Resolve launcher settings with the same parsers used by the jobs."""

import os
import re
import sys


def resolve(stage, argv):
    if stage == "ingest":
        from ingestion.pipeline import load_config
        cfg = load_config(argv)
    elif stage in ("chunk", "tag", "embed"):
        from jobs.runtime import config
        cfg = config(stage, argv)
    else:
        raise ValueError(f"unknown stage: {stage}")

    def memory(name: str, default: str) -> str:
        value = os.environ.get(name, default)
        if not re.fullmatch(r"[1-9][0-9]*[kKmMgG]?", value):
            raise ValueError(f"{name} must be a positive Spark memory size")
        return value

    driver = memory("SPARK_DRIVER_MEMORY", "512m")
    if stage == "embed":
        executor_default = os.environ.get("SPARK_EXECUTOR_MEMORY", "512m")
        overhead_default = os.environ.get("SPARK_EXECUTOR_MEMORY_OVERHEAD", "1g")
        executor = memory("EMBEDDING_EXECUTOR_MEMORY", executor_default)
        overhead = memory("EMBEDDING_EXECUTOR_MEMORY_OVERHEAD", overhead_default)
    else:
        executor = memory("SPARK_EXECUTOR_MEMORY", "512m")
        overhead = memory("SPARK_EXECUTOR_MEMORY_OVERHEAD", "512m")
    return cfg["executor_instances"], cfg["dry_run"], driver, executor, overhead


def main():
    stage, *argv = sys.argv[1:]
    count, dry_run, driver, executor, overhead = resolve(stage, argv)
    print("\t".join((str(count), "1" if dry_run else "0", driver, executor, overhead)))


if __name__ == "__main__":
    main()
