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
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--executor-instances", type=positive)
    parser.add_argument("--chunking-version", default=CHUNKING_VERSION)
    parser.add_argument("--parallel-tasks", type=positive)
    parser.add_argument("--items-per-task", type=positive)
    parser.add_argument("--input-bytes", type=positive)
    parser.add_argument("--result-bytes", type=positive)
    if stage == "chunk":
        parser.add_argument("--document-limit", type=positive)
    else:
        if stage == "tag":
            parser.add_argument("--analysis-limit", type=positive)
            parser.add_argument("--retry-errors", action="store_true")
            parser.add_argument("--backend")
            parser.add_argument("--model")
            parser.add_argument("--analysis-version")
            parser.add_argument("--export-json")
        else:
            parser.add_argument("--embedding-limit", type=positive)
            parser.add_argument("--model")
            parser.add_argument("--max-length", type=positive)
            parser.add_argument("--embedding-batch-size", type=positive)
    result = vars(parser.parse_args(argv))
    if result["dry_run"] is None:
        dry_run = os.environ.get("DRY_RUN", "0")
        if dry_run not in ("0", "1"):
            raise ValueError("DRY_RUN must be 0 or 1")
        result["dry_run"] = dry_run == "1"
    if result["executor_instances"] is None:
        result["executor_instances"] = env_int("SPARK_EXECUTOR_INSTANCES", 2 if stage == "embed" else 3, minimum=1)
    for field, environment, default in (
        ("parallel_tasks", f"{stage.upper()}_MAX_PARALLEL_TASKS", result["executor_instances"]),
        ("items_per_task", f"{stage.upper()}_ITEMS_PER_TASK", 25 if stage == "chunk" else 10),
        ("input_bytes", f"{stage.upper()}_TASK_INPUT_BYTES", 2 * 1024 * 1024),
        ("result_bytes", f"{stage.upper()}_TASK_RESULT_BYTES", (4 if stage == "chunk" else 1) * 1024 * 1024),
    ):
        if result[field] is None:
            result[field] = env_int(environment, default, minimum=1)
    if stage == "tag":
        result["backend"] = result["backend"] or os.environ.get("TAGGING_BACKEND", "groq")
        if result["backend"] != "groq" and result["model"] is None and not os.environ.get("TAGGING_MODEL"):
            parser.error("a custom backend requires --model or TAGGING_MODEL")
        result["model"] = result["model"] or os.environ.get("TAGGING_MODEL", "qwen/qwen3.8-27b")
        result["analysis_version"] = result["analysis_version"] or os.environ.get("TAGGING_ANALYSIS_VERSION", "chunk-analysis-v2.4.1")
    if stage == "embed":
        result["model"] = result["model"] or os.environ.get("EMBEDDING_MODEL", "BAAI/bge-m3-int8")
        if result["max_length"] is None:
            result["max_length"] = env_int("EMBEDDING_MAX_LENGTH", 256, minimum=1)
        if result["embedding_batch_size"] is None:
            result["embedding_batch_size"] = env_int("EMBEDDING_BATCH_SIZE", 1, minimum=1)
    return result


def start_spark(stage, cfg):
    from pyspark.sql import SparkSession
    if stage not in ("ingest", "chunk", "tag", "embed"):
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
    if stage == "embed":
        builder = builder.config("spark.executorEnv.EMBEDDING_MODEL_DIR", "./embedding-model")
        builder = builder.config("spark.executorEnv.EMBEDDING_MAX_LENGTH", str(cfg["max_length"]))
        builder = builder.config("spark.executorEnv.EMBEDDING_BATCH_SIZE", str(cfg["embedding_batch_size"]))
        builder = builder.config("spark.executorEnv.EMBEDDING_INTRA_OP_THREADS", "1")
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
