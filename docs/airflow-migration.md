# Airflow migration: shell scripts → Python

**Status:** the migration is complete except for retiring the manual supervisor
(Phase 6), which is deliberately deferred until the DAG has run in production for a
while. The daily DAG, Python setup/download scripts, and PostgreSQL-backed Airflow
metadata database are live.

This document records what changed, what was intentionally left out, and how to
operate the result. For day-to-day commands, the [README runbook](../README.md#airflow-automation)
is the shorter reference.

---

## Background

The product is a searchable database of news articles. HTML pages arrive in large
compressed WARC archives from Common Crawl. Four Spark stages mutate the data in
order:

| Stage | Program | What it does |
|---|---|---|
| `ingest` | `ingestion/pipeline.py` | Picks WARC files from a CC-NEWS monthly index, extracts articles, filters by language/length, writes them to PostgreSQL. |
| `chunk` | `chunking/pipeline.py` | Splits each article's clean text into overlapping retrieval chunks. |
| `tag` | `tagging/pipeline.py` | Sends each chunk to an LLM (Groq by default) for structured labels/metadata. |
| `embed` | `embeddings/pipeline.py` | Converts each chunk into a normalized vector with the local INT8 ONNX model. |

`scripts/export_csv.py` is an on-demand debug/export tool, not part of the daily
chain.

A stage cannot be run as a bare `python <stage>/pipeline.py`. The Spark workers are
separate machines without the project's dependencies, so the glue code must:

1. Load `.env` and let CLI flags override exported variables and `.env` defaults.
2. Choose the stage virtual environment (`.venv` normally,
   `.venv-embedding-onnx` for `embed`).
3. Zip project source and pack the venv, fingerprinting both so unchanged
   artifacts are reused.
4. Publish archives and the embedding model to HDFS.
5. Assemble and run `spark-submit`.

All of that now lives in `jobs/launcher.py`. Every stage call goes through
`python -m jobs.launcher <stage>`, or `jobs.launcher.launch(stage, **options)`
from Python.

Terminology used below:

- **DAG** — an Airflow pipeline definition in `airflow/dags/`.
- **Probe** — a cheap readiness task that runs before ingest.
- **Exit code 2** — "the stage ran correctly but the selected sources ran out
  before the requested quota." It is not an operational crash.
- **Backfill** — an Airflow run created for a past logical date/range instead of
  the current schedule.
- **XCom** — Airflow's small-value handoff between tasks.

---

## What runs now

### Airflow topology

```text
probe → download_and_enter_db → chunk → tag → embed
```

The DAG id remains **`ingestion_pipeline`**. It was not renamed to
`news_pipeline`, to preserve existing run history and UI links.

`probe` checks:

- Common Crawl: a ranged request to each month's `warc.paths.gz` manifest. HTTP
  4xx counts as reachable (the manifest may not be published yet); HTTP 5xx and
  network errors fail the probe.
- YARN: `yarn node -list` must contain a `RUNNING` node.
- HDFS: `hdfs dfs -test -e /`, unless `USE_HDFS_CACHE=0`.
- PostgreSQL: `pg_isready` against the configured host/port.

Ingest processes the data interval's month. On the first day of a month it also
revisits the previous month, so late-published files are not missed. There are no
`year`/`month` DAG params; use a backfill or a manual trigger with a logical date
to target a specific month.

### Retries, timeouts, and exit 2

| Task | Retries | Delay | Execution timeout |
|---|---:|---:|---:|
| `probe` | 3 | 2 min | 2 min |
| `download_and_enter_db` | 3 | 5 min | 24 h |
| `chunk` / `tag` / `embed` | 1 | 5 min | 48 h |

The timeouts are hang guards, not throughput targets. An ingest can legitimately
run for hours; a dead YARN/HDFS run previously sat for days.

`jobs/airflow_tasks.launch_stage()` converts launcher exit code 2 into a warning
result (`status="sources_exhausted"`) and prints `SOURCES EXHAUSTED`. The task
succeeds so chunk/tag/embed can drain any existing backlog. Every other launcher
failure still fails the task.

An ingest retry starts a **new** ingestion run ledger and re-applies the quota. It
does not resume the failed invocation's exact insertion count. Already-committed
articles are idempotent, but strict monthly caps are not preserved across retries.

### DAG params

The trigger form exposes:

- `num_files` — `all` or a positive WARC file count.
- `max_accepted_articles` — per-month new-article cap; `0` is unlimited.
- `max_accepted_per_file` — per-file cap; `0` is unlimited.
- `chunk_max_documents`, `tag_max_chunks`, `embed_max_chunks` — per-stage limits;
  `0` is unlimited.

---

## Phase history

### Phase 1 — Port the launcher (completed 2026-11-01)

`jobs/launcher.py` reproduces the former shell sequence: `.env` loading, stage venv
selection, source zip, venv packing and fingerprint cache, embedding-model archive,
HDFS publishing, and `spark-submit` assembly. The launcher is standard-library-only;
`.env` reading, `venv_pack`, `tar`, `hdfs`, and `spark-submit` remain child
processes.

The old shell wrappers (`run_processing.sh`, `run_ingestion.sh`,
`run_chunking.sh`, `run_tagging.sh`, `run_embeddings.sh`) were deleted.

Verified: dry-run JSON, `--help`, and assembled `spark-submit` argv match the
captured shell baseline; a failed child's exit code is passed through; exported
variables win over `.env`; a second run reuses the cached venv archive; a real
one-file smoke ingest committed 10/10 articles and finished `SUCCEEDED` on YARN.

### Phase 2 — Port the utility scripts (completed 2026-11-01)

| Former | Now |
|---|---|
| `scripts/export_csv.sh` | `scripts/export_csv.py` |
| `scripts/inspect_db.sh` | `python -m db.inspect` |
| `scripts/watch_embeddings.sh` | `python -m scripts.watch_embeddings` |

`export_csv.py` keeps the nine-table COPY export, per-table `ORDER BY`, staging
directory plus atomic swap, row counts, and the optional HGFS copy. It also gained
sampling (`--sample N`), optional chunk tables (`--include-chunks`), and zip output
(`--zip` / `--zip-path`).

### Phase 3 — Port the one-off setup scripts (completed 2026-11-10)

| Former | Now |
|---|---|
| `scripts/setup_embedding_onnx_env.sh` | `scripts/setup_embedding_onnx_env.py` |
| `scripts/download_quantized_embedding_model.sh` | `scripts/download_quantized_embedding_model.py` |
| `scripts/download_quantized_reranker_model.sh` | `scripts/download_quantized_reranker_model.py` |
| `airflow/systemd/install.sh` | `airflow/systemd/install.py` |

Shared resume/retry/atomic-rename helpers live in `scripts/download_utils.py`. The
download scripts keep the pinned ONNX revisions, tokenizer/pooling layout, and
checksum verification. The reranker script verifies the model SHA-256 and a smoke
ranking. The embedding script reuses an already-complete target metadata directory
when the optional `.models/bge-m3` source metadata is absent, so reruns are
idempotent on a machine that only kept the quantized output.

Verified on this host:

- `setup_embedding_onnx_env.py`: pip install, `pip check`, and the "no torch /
  no sentence-transformers" guard pass.
- `download_quantized_embedding_model.py`: validates the existing 563 MiB INT8
  graph and prints the ONNX inputs/outputs.
- `download_quantized_reranker_model.py`: reuses the checksum-verified graph and
  validates ranking scores `[6.6368, -11.0271]`.
- All three `.sh` files and `airflow/systemd/install.sh` were deleted.

### Phase 4 — Move Airflow's metadata DB to PostgreSQL (completed)

Airflow runs three systemd units (`airflow-scheduler`, `airflow-dag-processor`,
`airflow-api-server`) with `AIRFLOW_HOME=/home/spark-master/airflow`. The metadata
database is PostgreSQL; `airflow db check` passes. The API server listens on
`127.0.0.1:8080`.

The units are installed by `airflow/systemd/install.py` after reviewing
`/home/spark-master/airflow/airflow.env`.

### Phase 5 — Build the DAG (completed 2026-11-10)

`airflow/dags/ingestion.py` is a real TaskFlow DAG with an `external_python` task
for each stage. `airflow dags list-import-errors` is clean and the task list is
`probe`, `download_and_enter_db`, `chunk`, `tag`, `embed`.

Deviations from the original plan:

- The DAG id stayed `ingestion_pipeline`, not `news_pipeline`.
- No `news_export` DAG was created; export remains an on-demand script.
- The probe checks all four dependencies, not just Common Crawl.
- Month/year are selected by backfill/logical date, not trigger params.
- `scripts/supervise_ingest.py` was **not** deleted in Phase 5.

### Phase 6 — Retire `supervise_ingest.py` (deferred)

The supervisor remains available as a manual fallback. It is not started by
Airflow and must not run concurrently with `ingestion_pipeline`: the ingestion
coordinator advisory lock allows only one ingest at a time.

Retire it only after the DAG has proven out over several real runs, including a
killed/failed ingest that Airflow retried successfully.

### Phase 7 — Docs and tests (current state)

The README now has an Airflow runbook (services, UI, trigger, backfill, logs,
recovery, smoke test). `docs/processing.md` documents the launcher cache/timing,
per-stage limits, and Python setup commands. `docs/validation.md` records the
launcher port and the current verification. `docs/module_map.md` covers the new
modules.

New/updated tests:

- `tests/test_preflight.py` — probe success, 4xx vs 5xx, YARN/HDFS/Postgres
  failures, and the summary.
- `tests/test_airflow_tasks.py` — exit-2 conversion, other failures propagate,
  month selection (mid-month, first-of-month, January), manifest URLs.
- `tests/test_download_utils.py` — atomic writes, Range resume, server ignoring
  Range, 4xx no-retry, transient retry, hashing/size helpers.
- Existing launcher, artifacts, processing, export, and shared-helper tests cover
  the caching, timing, per-stage limit, and export changes.

---

## Operations

### Services and UI

```bash
sudo systemctl status airflow-scheduler airflow-dag-processor airflow-api-server --no-pager
ssh -L 8080:127.0.0.1:8080 spark-master   # then http://localhost:8080
```

Use the simple-auth credentials in
`/home/spark-master/airflow/airflow.env` (`AIRFLOW__CORE__SIMPLE_AUTH_MANAGER_USERS`).
The CLI needs the same environment:

```bash
set -a; . /home/spark-master/airflow/airflow.env; set +a
/home/spark-master/airflow-venv/bin/airflow <command>
```

### Trigger

```bash
airflow dags trigger ingestion_pipeline --conf '{
  "num_files": "1",
  "max_accepted_articles": 10,
  "max_accepted_per_file": 10,
  "chunk_max_documents": 10,
  "tag_max_chunks": 10,
  "embed_max_chunks": 2
}'
```

### Backfill

Backfill dates create one run per day in the range. For one pass over a month, use
a single mid-month day and set the end date to the next day (the end is exclusive
in practice):

```bash
airflow backfill create \
  --dag-id ingestion_pipeline \
  --from-date 2026-09-15 \
  --to-date 2026-09-16 \
  --dag-run-conf '{"num_files":"all","max_accepted_articles":0,"max_accepted_per_file":0}'
```

For a year, create one single-day backfill per month; `max_active_runs=1` makes
them queue and run in order.

### Logs and recovery

Task logs:
`/home/spark-master/airflow/logs/dag_id=ingestion_pipeline/run_id=<run_id>/task_id=<task_id>/`.

The launcher writes `[launcher] <step>: <seconds>` timing lines to stderr before
Spark starts. Every stage ends with a `PHASE SUMMARY <stage>` JSON line.

Clear a failed task by its logical date:

```bash
airflow tasks clear ingestion_pipeline \
  -s <logical_date> -e <logical_date> \
  -t download_and_enter_db -y
```

### Smoke test

```bash
airflow dags test airflow_smoke_test
```

The smoke test verifies the Airflow runtime, `spark-submit`/`hdfs`/`yarn`
visibility, the project venv, the embedding model file, PostgreSQL readiness, and
a launcher dry run. It does not start Spark or touch the ingestion lock.

---

## Verification and known risks

Verified for this migration:

- DAG import is clean; `airflow tasks list ingestion_pipeline` shows all five
  tasks.
- `jobs.preflight.run` passes on this host when Common Crawl is responsive; a
  transient Common Crawl HTTP 503 correctly sent the probe to `up_for_retry`, and
  the retry succeeded.
- The three setup/download scripts run against the existing environments.
- Unit tests for preflight, Airflow task helpers, and download utilities pass.

Known risks / remaining measurements:

- **Common Crawl intermittently returns 503** to `urllib` requests for the
  manifest even when `curl` immediately returns 206. The probe retries, but a
  sustained 503 will delay ingest. This is the reason 4xx is distinguished from
  5xx.
- **Embedding throughput is not measured at scale.** The only evidence is two
  one-chunk runs at roughly 4.8 and 5.3 minutes, dominated by Spark/YARN startup.
  The 48-hour stage timeout is therefore a hang guard, not a validated throughput
  bound. Measure a sustained run before treating 48 hours as capacity.
- **Ingest retries re-apply the quota** and start a new run ledger; strict monthly
  caps are not preserved across retries.
- **The first live run after deployment was disrupted.** The
  `scheduled__2026-11-08T22:00:00+00:00` ingest task was terminated by SIGTERM after
  about 38 minutes; the cause was not conclusively identified. The new probe ran
  afterwards, hit a transient 503, retried, and succeeded, but the run was already
  failed because ingest had failed. The next scheduled run uses the new DAG. Clear
  or retry the failed task only after confirming the cluster and Common Crawl are
  healthy.
- **Supervisor coexistence.** Do not run `scripts/supervise_ingest.py` and the DAG
  at the same time.

---

## Command mapping

| Before | Now |
|---|---|
| `./scripts/run_ingestion.sh …` | `python -m jobs.launcher ingest …` |
| `./scripts/run_chunking.sh …` | `python -m jobs.launcher chunk …` |
| `./scripts/run_tagging.sh …` | `python -m jobs.launcher tag …` |
| `./scripts/run_embeddings.sh …` | `python -m jobs.launcher embed …` |
| `./scripts/export_csv.sh` | `python -m scripts.export_csv` |
| `./scripts/inspect_db.sh` | `python -m db.inspect` |
| `./scripts/watch_embeddings.sh` | `python -m scripts.watch_embeddings` |
| `bash scripts/setup_embedding_onnx_env.sh` | `python scripts/setup_embedding_onnx_env.py` |
| `bash scripts/download_quantized_embedding_model.sh` | `python scripts/download_quantized_embedding_model.py` |
| `bash scripts/download_quantized_reranker_model.sh` | `python scripts/download_quantized_reranker_model.py` |
| `bash airflow/systemd/install.sh` | `python airflow/systemd/install.py` |
| manual babysitting via `scripts/supervise_ingest.py` | Airflow `ingestion_pipeline` (supervisor retained as a manual fallback until Phase 6) |
