"""Build the ``spark-submit`` command list for one stage."""

import os
from dataclasses import dataclass
from pathlib import Path

from jobs.errors import LaunchError


@dataclass(frozen=True)
class SparkPlan:
    """Everything the submission needs, resolved before building the command."""

    stage: str
    venv: Path
    archives: str
    py_files: Path
    executor_instances: int
    driver_memory: str
    executor_memory: str
    executor_memory_overhead: str
    user_args: tuple[str, ...] = ()
    extra_conf: tuple[str, ...] = ()


def submit_binary(stage, environ):
    if stage == "ingest":
        return "spark-submit"
    spark_home = environ.get("SPARK_HOME")
    if not spark_home:
        raise LaunchError("Set SPARK_HOME to the cluster Spark installation")
    return str(Path(spark_home) / "bin" / "spark-submit")


def submit_command(plan, environ):
    """Return ``[binary, argument, ...]`` in the measured shell order."""
    cores = environ.get("SPARK_EXECUTOR_CORES") or "1"
    am_memory = environ.get("SPARK_YARN_AM_MEMORY") or "512m"
    am_overhead = environ.get("SPARK_YARN_AM_MEMORY_OVERHEAD") or "384m"

    arguments = [
        "--master", "yarn",
        "--deploy-mode", "client",
        "--driver-memory", plan.driver_memory,
        "--executor-memory", plan.executor_memory,
        "--conf", f"spark.executor.memoryOverhead={plan.executor_memory_overhead}",
        "--conf", f"spark.executor.cores={cores}",
        "--conf", f"spark.yarn.am.memory={am_memory}",
        "--conf", f"spark.yarn.am.memoryOverhead={am_overhead}",
        "--conf", f"spark.executor.instances={plan.executor_instances}",
        "--conf", "spark.dynamicAllocation.enabled=false",
        "--conf", "spark.driver.maxResultSize=64m",
        "--conf", "spark.executorEnv.RAYON_NUM_THREADS=1",
        "--conf", "spark.executorEnv.OMP_NUM_THREADS=1",
        "--conf", "spark.executorEnv.OPENBLAS_NUM_THREADS=1",
        "--conf", f"spark.pyspark.driver.python={plan.venv / 'bin' / 'python'}",
        "--conf", "spark.pyspark.python=./environment/bin/python",
    ]
    for setting in plan.extra_conf:
        arguments += ["--conf", setting]
    if plan.stage != "ingest":
        arguments += [
            "--conf", "spark.speculation=false",
            "--conf", "spark.task.maxFailures=1",
        ]
    arguments += [
        "--archives", plan.archives,
        "--py-files", str(plan.py_files),
        f"scripts/{plan.stage}.py",
        *plan.user_args,
    ]
    return [submit_binary(plan.stage, environ), *arguments]


def is_help(arguments):
    return any(argument in ("--help", "-h") for argument in arguments)
