"""Shared command configuration; Spark and optional backends are lazy imports."""

import argparse
import json
import os
import sys


def env_int(name, default, *, minimum=0):
    raw = os.environ.get(name, str(default)).strip()
    try:
        value = int(raw)
    except ValueError as error:
        raise ValueError(f"{name} must be an integer, got {raw!r}") from error
    if value < minimum:
        raise ValueError(f"{name} must be at least {minimum}, got {value}")
    return value


def positive(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be positive")
    return number


def config(stage, argv=None):
    from chunking import CHUNKING_VERSION
    parser = argparse.ArgumentParser(description=f"Spark {stage} job")
    parser.add_argument("--dry-run", action="store_true", default=os.environ.get("DRY_RUN") == "1")
    parser.add_argument("--chunking-version", default=CHUNKING_VERSION)
    parser.add_argument("--parallel-tasks", type=positive, default=os.environ.get(f"{stage.upper()}_MAX_PARALLEL_TASKS", str(env_int("SPARK_EXECUTOR_INSTANCES", 3, minimum=1))))
    parser.add_argument("--items-per-task", type=positive, default=os.environ.get(f"{stage.upper()}_ITEMS_PER_TASK", "25" if stage == "chunk" else "10"))
    parser.add_argument("--input-bytes", type=positive, default=os.environ.get(f"{stage.upper()}_TASK_INPUT_BYTES", str(2*1024*1024)))
    parser.add_argument("--result-bytes", type=positive, default=os.environ.get(f"{stage.upper()}_TASK_RESULT_BYTES", str((4 if stage == 'chunk' else 1)*1024*1024)))
    if stage == "chunk":
        parser.add_argument("--document-limit", type=positive)
    else:
        parser.add_argument("--analysis-limit", type=positive)
        parser.add_argument("--retry-errors", action="store_true")
        parser.add_argument("--backend", default=os.environ.get("TAGGING_BACKEND", "groq"))
        parser.add_argument("--model", default=os.environ.get("TAGGING_MODEL", "qwen/qwen3.8-27b"))
        parser.add_argument("--analysis-version", default=os.environ.get("TAGGING_ANALYSIS_VERSION", "chunk-analysis-v2.4.1"))
        parser.add_argument("--export-json")
    result = vars(parser.parse_args(argv))
    if stage == "tag" and result["backend"] != "groq":
        if "--model" not in (argv if argv is not None else sys.argv[1:]) and not os.environ.get("TAGGING_MODEL"):
            parser.error("a custom backend requires --model or TAGGING_MODEL")
    return result


def start_spark(stage, cfg):
    from pyspark.sql import SparkSession
    if stage not in ("ingest", "chunk", "tag"):
        raise ValueError(f"unknown Spark stage: {stage}")
    builder = (SparkSession.builder.appName("CC-NEWS-Bounded-Ingest" if stage == "ingest" else f"News-{stage}")
               .config("spark.python.worker.reuse", "true")
               .config("spark.redaction.regex", "(?i)secret|password|token|access[.]?key|api[._]?key")
               .config("spark.redaction.string.regex", "gsk_[A-Za-z0-9]+"))
    if stage == "ingest":
        # Preserve ingestion's existing Spark retry policy and result threshold.
        builder = builder.config("spark.task.maxDirectResultSize", "16m")
    else:
        builder = builder.config("spark.speculation", "false").config("spark.task.maxFailures", "1")
    if os.environ.get("SPARK_MASTER_URL"):
        builder = builder.master(os.environ["SPARK_MASTER_URL"])
    if stage == "tag" and cfg["backend"] == "groq":
        key = os.environ.get("GROQ_API_KEY", "")
        if not key:
            raise ValueError("GROQ_API_KEY is required for the Groq backend")
        builder = builder.config("spark.executorEnv.GROQ_API_KEY", key)
        interval = float(os.environ.get("TAG_REQUEST_INTERVAL_SECONDS", "1.5"))
        if interval < 0:
            raise ValueError("TAG_REQUEST_INTERVAL_SECONDS cannot be negative")
        builder = builder.config("spark.executorEnv.TAG_REQUEST_INTERVAL_SECONDS", str(interval))
        builder = builder.config("spark.executorEnv.TAG_PARALLELISM", str(cfg["parallel_tasks"]))
        for name in ("TAG_REQUESTS_PER_MINUTE", "TAG_TOKENS_PER_MINUTE"):
            if name in os.environ:
                value = positive(os.environ[name])
                builder = builder.config(f"spark.executorEnv.{name}", str(value))
    return builder.getOrCreate()


def cli(run):
    try:
        return run()
    except KeyboardInterrupt:
        print("Interrupted; committed batches are saved. Uncommitted tasks remain pending.", file=sys.stderr)
        return 130
    except Exception as error:
        message = str(error)
        key = os.environ.get("GROQ_API_KEY")
        if key:
            message = message.replace(key, "[REDACTED]")
        print(f"FATAL {type(error).__name__}: {message}", file=sys.stderr)
        return 1


def report(values):
    print(json.dumps(values, sort_keys=True), flush=True)
