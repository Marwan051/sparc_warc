# spark_warc_v2 — How It All Works

Plain-language guide to the CC-NEWS → PostgreSQL → RAG pipeline.
Companion to `README.md` (operator manual) and `VALIDATION.md` (proof).

## The big picture

Common Crawl News publishes monthly lists (`warc.paths.gz`) of WARC files.
This project downloads those files, pulls out real news articles in Arabic,
English, and French, and stores them in PostgreSQL — ready for RAG.

Golden rule: **workers download and read; the driver writes to the database.**
The driver never touches WARC bytes. Workers never touch Postgres.

```
manifest → waves of ≤3 file-tasks (driver plans, Spark delivers)
         → workers stream + extract + classify
         → driver commits each chunk in one transaction
         → warcdb_csv/ → RAG
```

## How a run flows (simple version)

Think of the driver as a boss handing out work slips, one round ("wave") at a time.
Workers remember nothing — the driver's notebook (database) remembers everything.

1. **Check the notebook** (`load_run` + `load_run_files`): per file, where it
   stopped (byte cursor) and how many articles it already gave.
2. **Write up to 3 slips** (`_allocate_tasks`): each slip = file URL + byte
   offset to continue from + how many articles are still needed.
3. **Hand them out** (`parallelize(tasks).map(process_file_chunk).collect()`):
   one slip per worker, all at once; the driver waits for all three to return.
4. **File the results** (`commit_chunk` per chunk): save new articles, advance
   each file's cursor. Duplicates and rejects don't count toward quotas.

Repeat until every file gave its quota or ran out of file. A slip is just text
(URL + byte number) — the worker downloads the bytes itself over HTTP
(`Range: bytes=<cursor>-`). The driver only ever receives extracted text.

Exit codes: `0` target met · `1` failure · `2` sources can't fill the target.

## `stream_to_db.py` func by func (583 lines)

**Config**
- `_env_int` — reads an int env var, rejects garbage/negatives at startup.
- `_parse_num_files` — `NUM_FILES`: `all`/`0`/empty = whole manifest, else a
  positive int (default 15).
- `load_config` — builds all settings from env (quotas, worker budgets,
  filters, resume/dry-run). Guardrails: unknown `MAX_EXTRACTED_PER_ROUND`
  errors out, `MAX_FILES_PER_ROUND` clamped to 3 (your executor count),
  `MAX_ARTICLE_BYTES ≤ WORKER_MAX_RESULT_BYTES` enforced.

**Spark/network helpers**
- `get_spark_session` — session `CC-NEWS-Bounded-Ingest` (16 MiB direct-result
  cap, worker reuse; `SPARK_MASTER_URL` override for local tests).
- `_sleep_backoff` — 2s/4s/8s… capped 30s between retries.
- `_transient` — retryable? HTTP 408/429/5xx + timeouts/connection errors yes;
  404/bad config no.
- `fetch_manifest` — downloads `warc.paths.gz` for YEAR/MONTH, slices
  `[offset : offset+num_files]`, returns full data.commoncrawl.org URLs.
- `_content_total` — true file size from `Content-Range`/`Content-Length`, so
  resume spots "cursor beyond EOF".

**Worker side (runs on executors)**
- `_record_id` — dedup key: WARC record ID, or `gen-<hash>` fallback.
- `_candidate` — shapes one article dict (IDs, title/author/date, text,
  counts, language); strips NUL bytes Postgres rejects.
- `_process_file_once(task)` — the worker heart: ranged download, validate
  status/`Content-Range`/ETag/Last-Modified, walk records one by one
  (skip non-HTML/oversized → extract → drop short → Lingua detect → drop
  non-ar/en/fr → build candidate). Always returns a checkpoint
  (`next_offset` = exact record boundary). If the server ignores `Range`, it
  replays from 0 to the saved boundary.
- `process_file_chunk(task)` — retry wrapper (≤ `MAX_RETRIES` on transient
  errors) + stamps `python_peak_rss_mib`/`worker_host`/`worker_pid`. Permanent
  failure returns an error dict with the cursor unmoved — nothing skipped.

**Driver scheduling**
- `_allocate_tasks` — first ≤3 pending files; splits remaining global quota
  fairly (`ceil(remaining/slots_left)`), caps each by per-file remainder.
  `chunk_id = sha256(run + file + offset + wave)` makes retried commits
  idempotent.
- `_print_config` — `DRY_RUN` output.

**Progress display**
- `_bar_total` / `_make_progress_bar` — tqdm bar on stderr: global target if
  set, else `per_file × num_files`, else count-up. `NO_PROGRESS=1` disables
  bar and wave prints; missing tqdm falls back to wave prints.

**Resume/summary**
- `SEMANTIC_ENV` + `restore_run_config` — resume reloads manifest/quotas/
  filters and **errors** on conflicting overrides; only resource budgets may
  change mid-run.
- `_summary` — per-file counts/statuses, summed chunk counters, resume command.

**Main loop**
- `run_streaming_pipeline` — dry-run → lock one coordinator →
  new run or resume → wave loop (plan → scatter-gather → commit → report) →
  `complete`/`shortfall`/`failed`. `finally` closes bar, stops Spark, releases
  the lock.

## `db/db_handler.py` (425 lines) — driver only

- `_db_config` / `get_connection` — libpq env settings + local defaults.
- `connection_scope` — reuse the coordinator connection or open a short one;
  always rolls back strays and closes what it opened.
- `init_db` — creates tables + additive migrations.
- `extract_domain` — `https://www.bbc.com/x` → `bbc.com`.
- `acquire_coordinator_lock` — advisory lock: one ingestion job per month.
- `create_run` — one `ingest_runs` row (quotas + settings snapshot) + one
  `ingest_run_files` row per URL (cursor 0, `pending`, or verified old
  checkpoints).
- `load_run` / `load_run_files` — the notebook reads (global + per-file).
- `_insert_new_records` — dedup engine: `ON CONFLICT (warc_record_id)
  DO NOTHING RETURNING`; only new rows get metadata + content.
- `_write_diagnostic` / `_insert_isolated` — bad rows go to `dead_letter/`
  JSONL via savepoints; one bad row never kills its chunk.
- `resume_run` — `failed` files back to `pending`, run reopened.
- `commit_chunk` — idempotent (known chunk IDs return stored count), locks
  run + file rows, rejects stale cursors/over-quota chunks, inserts, advances
  cursor, sets `pending`/`eof`/`quota_reached`/`failed`. All or nothing.
- `finish_run` — stamps `complete`/`failed`/`shortfall`.
- `load/upsert_ingest_progress` — legacy shared checkpoint table.

Tables: `websites`/`authors` (deduped names) → `pages` (one row/article,
unique record ID) → `metadata` + `content` (details + text);
`ingest_runs`/`ingest_run_files`/`ingest_chunks` (quotas, cursors, receipts);
`ingest_files` (legacy checkpoints).

## `parsers/parsers.py` (84 lines)

- `ValidatedGzipStream` — checks gzip CRC/trailers and `Content-Length` as
  bytes flow (64 KiB sips, flat memory). Truncations raise instead of faking
  a clean EOF.
- `parse_warc_records_streaming` — FastWARC walk, one record at a time:
  non-HTML → `non_html` skip; over-limit HTML → `oversized_html` skip (reads
  limit+1 byte to prove it); else `{url, warc_date, charset, record_id,
  raw_bytes, start_offset}`.
- `parse_warc_stream_fastwarc` — alias for compatibility.

## `extractors/extractors.py` (279 lines)

- Script patterns + `get_lingua_detector` — Lingua brain (20 languages),
  built once per worker and reused.
- `_language_sample` — first 800 + middle 600 + last 600 chars (short texts
  whole), so English-chrome can't hide a foreign body.
- `detect_languages_batch` — code per text (`en`/`fr`/`ar`/`other`/…):
  rejects short/scriptless/low-confidence, >10% unsupported-script veto,
  Arabic revalidation against Persian/Urdu lookalikes.
- JSON-LD + `extract_publication_date` / `extract_date_from_text_fallback` /
  `extract_author` — author/date hunt: meta tags → JSON-LD → `<time>` →
  body-text regex, `"N/A"` if absent.
- `_trafilatura_text` — main-content extraction (no comments/tables).
- `extract_html_fields` — decode → read metadata before deleting junk tags →
  trafilatura if ≥ `min_words`, else selectolax body text → word floor →
  full field dict.

## Support files

- `utils.py` — `is_target_language` (ar/en/fr), encoding/mojibake checks,
  Arabic-script validation.
- `db_inspect.py` — counts, checkpoints, recent runs, article previews
  (`DB_INSPECT_SAMPLES/PREVIEW`).
- `rag_loader.py` — `iter_documents` (server-side streaming cursor),
  `iter_document_chunks` (800/100 split), `load_documents_distributed`
  (needs explicit limit).
- `run_to_db.sh` — validates config first, zips code, fingerprints +
  `venv-pack`s `.venv`, atomically publishes venv + Spark jars to HDFS, then
  `spark-submit --master yarn` (512m/512m/512m overhead, 1 core × 3).
- `export_csv.sh` — dumps the 5 article tables to `./warcdb_csv/`, prints
  counts, copies to `/mnt/hgfs/copy_path/warcdb_csv/`.
- `requirements.txt` (+`-dev`, `+rag`) — pinned ingest/test/RAG deps; cluster
  PySpark is reused, never pip-installed.

## Tests

- `tests/test_ingestion.py` — unit (quotas, resume, corruption, encodings,
  real Lingua) + PG integration in throwaway schemas (`WARC_TEST_DSN`).
- `tests/spark_smoke.py` — local `local[3]` end-to-end: 7 inserts, 3/file
  cap, overlapping workers.
- `tests/memory_probe.py` — 20 near-budget chunks, RSS growth <64 MiB.
- `tests/package_smoke.py` — real venv pack + relocated worker imports.
- `tests/test_launcher.py` — dry-run never packages/submits.
- `tests/test_rag_loader.py` — streaming laziness + eager-limit guard.

## Key settings (see README table)

`YEAR/MONTH` manifest · `NUM_FILES` (default 15) · `START_FILE_OFFSET` ·
`MAX_ACCEPTED_ARTICLES=0` (global target, 0 = unlimited) ·
`MAX_ACCEPTED_PER_FILE=0` (per-file cap) · `MAX_FILES_PER_ROUND=3` ·
`WORKER_MAX_CANDIDATES=100` · `WORKER_MAX_RESULT_BYTES=4MiB` ·
`WORKER_MAX_INPUT_BYTES=32MiB` · `WORKER_MAX_SECONDS=120` ·
`MAX_HTML_BYTES=4MiB` · `MAX_ARTICLE_BYTES=1MiB` · `MIN_WORD_COUNT=80` ·
`USE_TRAFILATURA=1` · `LINGUA_MIN_CONFIDENCE=0.5` · `DB_BATCH_SIZE=25` ·
`MAX_RETRIES=3` · `RESUME_RUN_ID` · `NO_PROGRESS` · `DRY_RUN`.

Example — 3 articles from every file: `NUM_FILES=all
MAX_ACCEPTED_ARTICLES=0 MAX_ACCEPTED_PER_FILE=3 ./run_to_db.sh`.
Duplicates/rejects never consume quota; short files contribute what they have.

## RAG notes

Trafilatura strips most site chrome, but ~5–10% of stored articles still carry
newsletter/subscribe/footer tails (measured on 2,678 rows). Storage impact is
nil; retrieval impact is real (duplicate footers crowd top-k, CTA text can leak
into answers). Mitigation: edge-anchored CTA strip + dropping boilerplate-heavy
tail chunks; sentence-level filtering is the stronger follow-up.

## Proven results (`VALIDATION.md`)

Local suite green; YARN: 10/10 single-file (`...0001 SUCCEEDED`, 9.3s) and
9/9 three-file 3/3/3 (`...0002 SUCCEEDED`, 10.6s) on worker1/2/3 with
eventlog-verified parallelism; 19 distinct articles, idempotent resume.
