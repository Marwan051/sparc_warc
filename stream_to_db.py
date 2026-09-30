"""Distributed, bounded-memory CC-NEWS ingestion into PostgreSQL.

Workers download, parse, extract, and classify. The driver is the single
transaction coordinator and counts only rows PostgreSQL actually inserts.
"""

import gzip
import hashlib
import json
import math
import resource
import re
import uuid
import os
import socket
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone


from db.db_handler import (
    acquire_coordinator_lock,
    commit_chunk,
    create_run,
    finish_run,
    init_db,
    load_run,
    load_run_files,
    resume_run,
)
from extractors.extractors import detect_languages_batch, extract_html_fields
from parsers.parsers import parse_warc_records_streaming, ValidatedGzipStream
from utils import is_target_language


def _env_int(name, default, *, minimum=0):
    raw = os.environ.get(name, str(default)).strip()
    try:
        value = int(raw)
    except ValueError as error:
        raise ValueError(f"{name} must be an integer, got {raw!r}") from error
    if value < minimum:
        raise ValueError(f"{name} must be at least {minimum}, got {value}")
    return value


def _parse_num_files(raw):
    text = ("15" if raw is None else raw).strip().lower()
    if text in ("", "all", "none", "0"):
        return None
    try:
        value = int(text)
    except ValueError as error:
        raise ValueError(f"NUM_FILES must be a positive integer or 'all', got {raw!r}") from error
    if value < 1:
        raise ValueError("NUM_FILES must be positive, 0, or 'all'")
    return value


def load_config():
    if "MAX_EXTRACTED_PER_ROUND" in os.environ:
        raise ValueError(
            "MAX_EXTRACTED_PER_ROUND was removed; use WORKER_MAX_CANDIDATES, "
            "WORKER_MAX_RESULT_BYTES, and WORKER_MAX_INPUT_BYTES"
        )
    year = os.environ.get("YEAR", "2026").strip()
    month = os.environ.get("MONTH", "05").strip().zfill(2)
    if not (year.isdigit() and len(year) == 4 and month.isdigit() and 1 <= int(month) <= 12):
        raise ValueError("YEAR/MONTH must identify a valid YYYY/MM manifest")
    config = {
        "year": year,
        "month": month,
        "manifest_id": f"{year}/{month}",
        "num_files": _parse_num_files(os.environ.get("NUM_FILES")),
        "start_file_offset": _env_int("START_FILE_OFFSET", 0),
        "target_articles": _env_int("MAX_ACCEPTED_ARTICLES", 0),
        "per_file_target": _env_int("MAX_ACCEPTED_PER_FILE", 0),
        "max_files_per_round": _env_int("MAX_FILES_PER_ROUND", 3, minimum=1),
        "worker_max_candidates": _env_int("WORKER_MAX_CANDIDATES", 100, minimum=1),
        "worker_max_result_bytes": _env_int("WORKER_MAX_RESULT_BYTES", 4 * 1024 * 1024, minimum=1024),
        "worker_max_input_bytes": _env_int("WORKER_MAX_INPUT_BYTES", 32 * 1024 * 1024, minimum=65536),
        "worker_max_seconds": _env_int("WORKER_MAX_SECONDS", 120, minimum=1),
        "max_html_bytes": _env_int("MAX_HTML_BYTES", 4 * 1024 * 1024, minimum=1024),
        "max_article_bytes": _env_int("MAX_ARTICLE_BYTES", 1024 * 1024, minimum=1024),
        "use_trafilatura": os.environ.get("USE_TRAFILATURA", "1") == "1",
        "lingua_min_confidence": float(os.environ.get("LINGUA_MIN_CONFIDENCE", "0.5")),
        "min_word_count": _env_int("MIN_WORD_COUNT", 80, minimum=1),
        "max_retries": _env_int("MAX_RETRIES", 3, minimum=1),
        "db_batch_size": _env_int("DB_BATCH_SIZE", 25, minimum=1),
        "resume_run_id": os.environ.get("RESUME_RUN_ID", "").strip(),
        "no_progress": os.environ.get("NO_PROGRESS", "0") == "1",
        "dry_run": os.environ.get("DRY_RUN", "0") == "1",
    }
    if not 0 <= config["lingua_min_confidence"] <= 1:
        raise ValueError("LINGUA_MIN_CONFIDENCE must be between 0 and 1")
    if os.environ.get("USE_TRAFILATURA", "1") not in ("0", "1"):
        raise ValueError("USE_TRAFILATURA must be 0 or 1")
    if config["max_files_per_round"] > 3:
        print("WARNING: MAX_FILES_PER_ROUND exceeds the cluster's three executors; using 3.")
        config["max_files_per_round"] = 3
    if config["max_article_bytes"] > config["worker_max_result_bytes"]:
        raise ValueError("MAX_ARTICLE_BYTES cannot exceed WORKER_MAX_RESULT_BYTES")
    return config


def get_spark_session():
    from pyspark.sql import SparkSession
    builder = (
        SparkSession.builder.appName("CC-NEWS-Bounded-Ingest")
        .config("spark.task.maxDirectResultSize", "16m")
        .config("spark.python.worker.reuse", "true")
    )
    if os.environ.get("SPARK_MASTER_URL"):
        builder = builder.master(os.environ["SPARK_MASTER_URL"])
    return builder.getOrCreate()


def _sleep_backoff(attempt):
    time.sleep(min(30, 2 ** (attempt + 1)))


def _transient(error):
    if isinstance(error, urllib.error.HTTPError):
        return error.code in (408, 429) or 500 <= error.code < 600
    return isinstance(error, (socket.timeout, TimeoutError, ConnectionError, urllib.error.URLError, OSError))


def fetch_manifest(config):
    url = (
        f"https://data.commoncrawl.org/crawl-data/CC-NEWS/"
        f"{config['year']}/{config['month']}/warc.paths.gz"
    )
    last_error = None
    for attempt in range(config["max_retries"]):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "spark-warc/2"})
            with urllib.request.urlopen(request, timeout=60) as response:
                paths = gzip.decompress(response.read()).decode("utf-8").splitlines()
            window = paths[config["start_file_offset"]:]
            selected = window if config["num_files"] is None else window[:config["num_files"]]
            return [f"https://data.commoncrawl.org/{path}" for path in selected]
        except Exception as error:
            last_error = error
            if attempt + 1 == config["max_retries"] or not _transient(error):
                raise
            _sleep_backoff(attempt)
    raise last_error


def _record_id(record, clean_text):
    if record.get("record_id"):
        return record["record_id"]
    basis = record.get("url", "") + clean_text[:500]
    return "gen-" + hashlib.sha256(basis.encode("utf-8", "ignore")).hexdigest()


def _candidate(record, fields, language, file_url):
    text = fields["clean_text"].replace("\x00", "")
    return {
        "record_id": _record_id(record, text),
        "url": record.get("url", "").replace("\x00", ""),
        "file_url": file_url,
        "warc_date": record.get("warc_date"),
        "title": str(fields.get("title") or "N/A").replace("\x00", ""),
        "author": str(fields.get("author") or "N/A").replace("\x00", ""),
        "published_date": str(fields.get("published_date") or "N/A").replace("\x00", ""),
        "cleaned_text": text,
        "word_count": fields.get("word_count", 0),
        "char_count": fields.get("char_count", len(text)),
        "links_count": fields.get("links_count", 0),
        "headings": fields.get("headings_sample", []),
        "language": language,
        "arabic_dialect": None,
        "extraction": fields.get("extraction", "selectolax"),
    }


def _content_total(response, offset, ranged):
    if ranged:
        content_range = response.headers.get("Content-Range", "")
        if "/" in content_range:
            total = content_range.rsplit("/", 1)[1]
            if total.isdigit():
                return int(total)
    length = response.headers.get("Content-Length")
    if length and length.isdigit():
        return offset + int(length) if ranged else int(length)
    return None


def _process_file_once(task):
    file_url = task["file_url"]
    start_offset = task["start_offset"]
    headers = {"User-Agent": "spark-warc/2"}
    if start_offset:
        headers["Range"] = f"bytes={start_offset}-"
    request = urllib.request.Request(file_url, headers=headers)
    started = time.monotonic()
    with urllib.request.urlopen(request, timeout=120) as response:
        status = getattr(response, "status", 200)
        if status not in (200, 206):
            raise IOError(f"unexpected HTTP status: {status}")
        ranged = start_offset > 0 and status == 206
        base_offset = start_offset if ranged else 0
        if ranged:
            content_range = response.headers.get("Content-Range", "")
            match = re.fullmatch(r"bytes (\d+)-(\d+)/(\d+)", content_range)
            if not match or int(match[1]) != start_offset or int(match[2]) != int(match[3]) - 1:
                raise IOError(f"unexpected Content-Range: {content_range!r}")
        etag = response.headers.get("ETag")
        modified = response.headers.get("Last-Modified")
        if task.get("etag") and etag and task["etag"] != etag:
            raise IOError("source ETag changed since the previous chunk")
        if task.get("last_modified") and modified and task["last_modified"] != modified:
            raise IOError("source Last-Modified changed since the previous chunk")
        total_size = _content_total(response, base_offset, ranged)
        if start_offset and total_size is not None and start_offset >= total_size:
            raise IOError("saved cursor lies at or beyond source size")
        length = response.headers.get("Content-Length", "")
        checked_stream = ValidatedGzipStream(response, int(length) if length.isdigit() else None)
        records = iter(parse_warc_records_streaming(
            checked_stream,
            max_html_bytes=task["max_html_bytes"],
            base_offset=base_offset,
        ))
        try:
            current = next(records)
        except StopIteration:
            return {
                "chunk_id": task["chunk_id"], "file_url": file_url,
                "start_offset": start_offset, "next_offset": base_offset + checked_stream.bytes_read,
                "candidates": [], "eof": True, "etag": etag,
                "last_modified": modified, "stats": {"records": 0}, "error": None,
            }

        candidates, result_bytes = [], 0
        found_start = start_offset == 0
        stats = {"records": 0, "non_html": 0, "oversized_html": 0,
                 "too_short_or_corrupt": 0, "language_rejected": 0,
                 "oversized_article": 0, "accepted_candidates": 0}
        seen = set()
        while current is not None:
            try:
                following = next(records)
                next_offset = following["start_offset"]
                clean_eof = False
                if next_offset <= current["start_offset"]:
                    raise IOError("WARC must have one record per gzip member for resumable offsets")
            except StopIteration:
                following = None
                next_offset = base_offset + checked_stream.bytes_read
                clean_eof = True
            if current["start_offset"] < start_offset:
                current = following
                continue
            if not found_start:
                if current["start_offset"] != start_offset:
                    raise IOError("saved cursor does not match a source record boundary")
                found_start = True
            stats["records"] += 1
            skip = current.get("skip")
            if skip:
                stats[skip] = stats.get(skip, 0) + 1
            else:
                try:
                    fields = extract_html_fields(current, task["min_word_count"], task["use_trafilatura"])
                except Exception:
                    fields = {}
                if not fields.get("clean_text") or fields.get("word_count", 0) < task["min_word_count"]:
                    stats["too_short_or_corrupt"] += 1
                else:
                    language = detect_languages_batch([fields["clean_text"]], task["lingua_min_confidence"])[0]
                    if not is_target_language(language):
                        stats["language_rejected"] += 1
                    else:
                        item = _candidate(current, fields, language, file_url)
                        encoded_size = len(json.dumps(item, ensure_ascii=False, default=str).encode("utf-8"))
                        if encoded_size > task["max_article_bytes"]:
                            stats["oversized_article"] += 1
                        elif item["record_id"] not in seen:
                            if result_bytes + encoded_size > task["max_result_bytes"]:
                                stats["result_bytes"] = result_bytes
                                stats["elapsed_seconds"] = round(time.monotonic() - started, 3)
                                return {
                                    "chunk_id": task["chunk_id"], "file_url": file_url,
                                    "start_offset": start_offset,
                                    # Revisit this qualifying record in the next bounded wave.
                                    "next_offset": current["start_offset"],
                                    "candidates": candidates, "eof": False,
                                    "etag": etag, "last_modified": modified,
                                    "stats": dict(stats, compressed_bytes_read=checked_stream.bytes_read), "error": None,
                                }
                            seen.add(item["record_id"])
                            candidates.append(item)
                            result_bytes += encoded_size
                            stats["accepted_candidates"] += 1
            elapsed = time.monotonic() - started
            consumed = (next_offset if next_offset is not None else current["start_offset"]) - start_offset
            stop = (
                len(candidates) >= task["candidate_limit"]
                or result_bytes >= task["max_result_bytes"]
                or consumed >= task["max_input_bytes"]
                or elapsed >= task["max_seconds"]
            )
            if stop or clean_eof:
                if next_offset is None:
                    raise IOError("cannot prove EOF because source size is unknown")
                stats["result_bytes"] = result_bytes
                stats["elapsed_seconds"] = round(elapsed, 3)
                return {
                    "chunk_id": task["chunk_id"], "file_url": file_url,
                    "start_offset": start_offset, "next_offset": next_offset,
                    "candidates": candidates, "eof": clean_eof,
                    "etag": etag, "last_modified": modified,
                    "stats": dict(stats, compressed_bytes_read=checked_stream.bytes_read), "error": None,
                }
            current = following
    raise IOError("stream ended without a checkpoint result")


def process_file_chunk(task):
    """Spark worker entry point with bounded retry and no external writes."""
    last_error = None
    for attempt in range(task["max_retries"]):
        try:
            result = _process_file_once(task)
            result["stats"]["python_peak_rss_mib"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)
            result["stats"]["worker_host"] = socket.gethostname()
            result["stats"]["worker_pid"] = os.getpid()
            result["stats"]["attempts"] = attempt + 1
            return result
        except Exception as error:
            last_error = error
            if attempt + 1 == task["max_retries"] or not _transient(error):
                break
            _sleep_backoff(attempt)
    return {
        "chunk_id": task["chunk_id"], "file_url": task["file_url"],
        "start_offset": task["start_offset"], "next_offset": task["start_offset"],
        "candidates": [], "eof": False, "etag": task.get("etag"),
        "last_modified": task.get("last_modified"), "stats": {},
        "error": f"{type(last_error).__name__}: {last_error}",
    }


def _allocate_tasks(config, run, files, wave):
    active = [f for f in files if f["status"] == "pending" and not f["eof"]]
    active = active[:config["max_files_per_round"]]
    if not active:
        return []
    remaining_total = None if run["target_articles"] == 0 else run["target_articles"] - run["inserted_count"]
    tasks = []
    if remaining_total is not None and remaining_total <= 0:
        return tasks
    for index, file_state in enumerate(active):
        slots_left = len(active) - index
        if remaining_total is None:
            allowance = config["worker_max_candidates"]
        else:
            allowance = min(config["worker_max_candidates"], max(1, math.ceil(remaining_total / slots_left)))
        if run["per_file_target"]:
            allowance = min(allowance, run["per_file_target"] - file_state["inserted_count"])
        if allowance <= 0:
            continue
        chunk_key = f"{run['run_id']}\0{file_state['file_url']}\0{file_state['next_offset']}\0{wave}"
        tasks.append({
            "chunk_id": hashlib.sha256(chunk_key.encode()).hexdigest(),
            "file_url": file_state["file_url"], "start_offset": file_state["next_offset"],
            "etag": file_state["etag"], "last_modified": file_state["last_modified"],
            "candidate_limit": allowance,
            "max_result_bytes": config["worker_max_result_bytes"],
            "max_input_bytes": config["worker_max_input_bytes"],
            "max_seconds": config["worker_max_seconds"],
            "max_html_bytes": config["max_html_bytes"],
            "max_article_bytes": config["max_article_bytes"],
            "min_word_count": config["min_word_count"],
            "use_trafilatura": config["use_trafilatura"],
            "lingua_min_confidence": config["lingua_min_confidence"],
            "max_retries": config["max_retries"],
        })
        if remaining_total is not None:
            remaining_total -= allowance
            if remaining_total <= 0:
                break
    return tasks


def _print_config(config):
    printable = {k: v for k, v in config.items() if k not in ("resume_run_id", "no_progress", "dry_run")}
    print(json.dumps(printable, indent=2, sort_keys=True))


def _bar_total(target, per_file, num_files):
    if target:
        return target
    if per_file and num_files:
        return per_file * num_files
    return None


def _make_progress_bar(target, initial, enabled):
    """tqdm bar on stderr; None when disabled or unavailable."""
    if not enabled:
        return None
    try:
        from tqdm import tqdm
    except Exception as error:
        print(f"Progress bar disabled ({error}).")
        return None
    try:
        return tqdm(total=target or None, initial=initial, unit=" articles",
                    desc="articles", dynamic_ncols=True)
    except Exception as error:
        print(f"Progress bar disabled ({error}).")
        return None


SEMANTIC_ENV = {
    "target_articles": "MAX_ACCEPTED_ARTICLES", "per_file_target": "MAX_ACCEPTED_PER_FILE",
    "year": "YEAR", "month": "MONTH", "num_files": "NUM_FILES",
    "start_file_offset": "START_FILE_OFFSET", "min_word_count": "MIN_WORD_COUNT",
    "use_trafilatura": "USE_TRAFILATURA", "lingua_min_confidence": "LINGUA_MIN_CONFIDENCE",
    "max_html_bytes": "MAX_HTML_BYTES", "max_article_bytes": "MAX_ARTICLE_BYTES",
}


def restore_run_config(config, run):
    stored = dict(run.get("config") or {})
    stored.update(target_articles=run["target_articles"], per_file_target=run["per_file_target"])
    year, month = run["manifest_id"].split("/")
    stored.update(year=year, month=month)
    for key, env in SEMANTIC_ENV.items():
        if key not in stored:
            continue
        if env in os.environ and config[key] != stored[key]:
            raise ValueError(f"{env} conflicts with persisted settings for RESUME_RUN_ID")
        config[key] = stored[key]
    config["manifest_id"] = run["manifest_id"]
    if config["max_article_bytes"] > config["worker_max_result_bytes"]:
        raise ValueError("WORKER_MAX_RESULT_BYTES must accommodate the run's MAX_ARTICLE_BYTES")
    return config


def _summary(run_id, config, conn):
    run = load_run(run_id, conn=conn)
    print(f"Run {run_id}: {run['status']}; committed {run['inserted_count']:,}/"
          f"{run['target_articles'] or 'unlimited'} new articles")
    for file in load_run_files(run_id, conn=conn):
        print(f"  {file['file_url']}: {file['inserted_count']:,} new; {file['status']}"
              + (f"; {file['last_error']}" if file['last_error'] else ""))
    with conn.cursor(name="chunk_summary") as cur:
        cur.execute("SELECT stats FROM ingest_chunks WHERE run_id=%s", (run_id,))
        # Bounded cursor fetches; avoid accumulating all per-chunk telemetry.
        totals = {}
        while True:
            rows = cur.fetchmany(100)
            if not rows:
                break
            for (stats,) in rows:
                for key, value in stats.items():
                    if isinstance(value, (int, float)) and key not in ("worker_pid", "python_peak_rss_mib", "attempts"):
                        totals[key] = totals.get(key, 0) + value
        print("Counters: " + json.dumps(totals, sort_keys=True))
    conn.rollback()
    print(f"Resume command: RESUME_RUN_ID={run_id} ./run_to_db.sh")


def run_streaming_pipeline():
    config = load_config()
    if config["dry_run"]:
        _print_config(config)
        return 0
    init_db()
    lock_conn = acquire_coordinator_lock(config["manifest_id"])
    spark = None
    run_id = None
    bar = None
    try:
        if config["resume_run_id"]:
            run = load_run(config["resume_run_id"], conn=lock_conn)
            restore_run_config(config, run)
            run_id = run["run_id"]
            resume_run(run_id, conn=lock_conn)
            print(f"Resuming run {run_id}: {run['inserted_count']} committed")
            resumed_files = load_run_files(run_id, conn=lock_conn)
            bar = _make_progress_bar(_bar_total(run["target_articles"], run["per_file_target"],
                                                len(resumed_files)),
                                     run["inserted_count"], not config["no_progress"])
        else:
            urls = fetch_manifest(config)
            if not urls:
                print("No WARC files were selected.")
                return 2
            persisted = {key: config[key] for key in SEMANTIC_ENV}
            run_id = create_run(config["manifest_id"], urls, config["target_articles"],
                                config["per_file_target"], persisted, conn=lock_conn)
            print(f"Created ingestion run {run_id}")
            bar = _make_progress_bar(_bar_total(config["target_articles"], config["per_file_target"],
                                                len(urls)),
                                     0, not config["no_progress"])
        print(f"Resume command: RESUME_RUN_ID={run_id} ./run_to_db.sh")
        wave = 0
        invocation = uuid.uuid4().hex
        while True:
            run = load_run(run_id, conn=lock_conn)
            files = load_run_files(run_id, conn=lock_conn)
            reached = run["target_articles"] and run["inserted_count"] >= run["target_articles"]
            tasks = [] if reached else _allocate_tasks(config, run, files, f"{invocation}:{wave}")
            if not tasks:
                failed = any(f["status"] == "failed" for f in files)
                status = "failed" if failed else ("complete" if reached or not run["target_articles"] else "shortfall")
                finish_run(run_id, status, conn=lock_conn)
                _summary(run_id, config, lock_conn)
                return {"complete": 0, "failed": 1, "shortfall": 2}[status]
            if spark is None:
                spark = get_spark_session()
                spark.sparkContext.setLogLevel("WARN")
            wave += 1
            results = spark.sparkContext.parallelize(tasks, len(tasks)).map(process_file_chunk).collect()
            wave_inserted = 0
            failed = False
            for result in results:
                if result.get("error"):
                    print(f"FAILED {result['file_url']}: {result['error']}")
                    failed = True
                for attempt in range(config["max_retries"]):
                    try:
                        inserted = commit_chunk(run_id, result, config["db_batch_size"], conn=lock_conn)
                        break
                    except Exception:
                        if attempt + 1 == config["max_retries"]:
                            raise
                        # Recover an uncertain commit by checking its persisted chunk ID.
                        lock_conn.close()
                        _sleep_backoff(attempt)
                        lock_conn = acquire_coordinator_lock(config["manifest_id"])
                wave_inserted += inserted
            if not config["no_progress"]:
                current = load_run(run_id, conn=lock_conn)
                wave_msg = (f"Wave {wave}: committed {current['inserted_count']:,}/"
                            f"{current['target_articles'] or 'unlimited'}; new={wave_inserted:,}; "
                            f"worker peak RSS MiB={[r['stats'].get('python_peak_rss_mib') for r in results]}")
                if bar is not None:
                    pending = sum(1 for f in load_run_files(run_id, conn=lock_conn)
                                  if f["status"] == "pending" and not f["eof"])
                    bar.update(wave_inserted)
                    bar.set_postfix({"wave": wave, "pending_files": pending,
                                     "rss_mib": [r["stats"].get("python_peak_rss_mib") for r in results]},
                                    refresh=False)
                    bar.write(wave_msg)
                    bar.refresh()
                else:
                    print(wave_msg)
            if failed:
                finish_run(run_id, "failed", conn=lock_conn)
                _summary(run_id, config, lock_conn)
                return 1
    except Exception:
        if run_id and not lock_conn.closed:
            try:
                finish_run(run_id, "failed", conn=lock_conn)
            except Exception:
                pass
        raise
    finally:
        try:
            if bar is not None:
                bar.close()
            if spark is not None:
                spark.stop()
        finally:
            lock_conn.close()


if __name__ == "__main__":
    try:
        sys.exit(run_streaming_pipeline())
    except Exception as error:
        stamp = datetime.now(timezone.utc).isoformat()
        print(f"[{stamp}] FATAL {type(error).__name__}: {error}", file=sys.stderr)
        sys.exit(1)
