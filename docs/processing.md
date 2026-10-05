# Spark chunking and tagging

Two independent YARN jobs materialize article chunks and analyze eligible chunks.
Both default to one concurrent Spark task per requested executor. PostgreSQL reads and writes stay
on the driver; executors receive bounded payloads and do not need DB credentials.

All three launchers (ingestion, chunking, tagging) delegate packaging and YARN
submission to `scripts/run_processing.sh`. Spark startup and task submission live
in `jobs/runtime.py` and `jobs/batching.py`. Ingestion retains its original Spark
retry settings, one-partition-per-file wave, ordered commits, quotas, and recovery
logic; only chunking/tagging use independent jobs with per-batch completion.

```text
PostgreSQL articles -> driver batches -> Spark cleaning/splitting -> article_chunks
article_chunks -> driver batches -> Spark analyzer backend -> chunk_analyses
```

## Run

From the project root, install the optional dependencies into the virtual
environment that the launchers package for YARN:

```bash
.venv/bin/python -m pip install -r requirements/rag.txt
./scripts/run_chunking.sh --document-limit 100

.venv/bin/python -m pip install -r requirements/tagging-groq.txt
export GROQ_API_KEY=your-key
./scripts/run_tagging.sh --analysis-limit 30
```

Export `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, and `PGPASSWORD` as for ingestion.
Set `SPARK_HOME` to the cluster Spark installation. All three shell launchers
automatically load the project-root `.env` using `python-dotenv`. Existing exported
or inline environment variables take precedence, followed by CLI options where
supported. Missing `.env` files are fine. Values are parsed as dotenv data, not
executed as shell commands. Direct Python module commands do not load `.env`.
The loader uses the existing `.venv` interpreter (or an externally supplied
`VENV_DIR`), so that bootstrap environment must contain `requirements/base.txt`.
The Groq key is delivered through executor environment configuration
with Spark redaction enabled; it is never included in source/environment archives
or command-line arguments. Use only a trusted cluster: redaction is not a secret
store and cluster administrators can access executor environments.

`--dry-run` validates arguments without opening Spark, PostgreSQL, or a provider
connection and without packaging. Both launchers support `--help`.

Omit limits to process all pending work. Rerun the same command to resume. The
chunking document limit counts pending documents, including documents that clean
to no chunks. The tagging limit counts scheduled chunks, including model errors.
`--retry-errors` makes previously failed analyses eligible. Terminal `SUCCESS`
and `NOISE` rows are skipped. Tagging does not implicitly run chunking.

```bash
./scripts/run_chunking.sh --items-per-task 25 --parallel-tasks 3
./scripts/run_tagging.sh --items-per-task 10 --parallel-tasks 3 --retry-errors
./scripts/run_tagging.sh --analysis-limit 5 --export-json results.json
```

Export writes all stored analyses for the selected chunking/backend/model/analysis
versions, including errors, in document/index order. It atomically replaces the
specified output file. Legacy JSON results are not imported.

## Batches, quotas, and recovery

Defaults are 25 documents per chunking task and 10 chunks per tagging task, with
three concurrent tasks by default. Input payloads are bounded to 2 MiB per task. Output
limits are 4 MiB for chunking and 1 MiB for tagging. Override with `--input-bytes`
and `--result-bytes`; a single oversized input or output fails explicitly. Reduce
batch count or increase byte limits to accommodate it. A document is never
partially materialized.

Environment equivalents are `CHUNK_ITEMS_PER_TASK`, `TAG_ITEMS_PER_TASK`,
`CHUNK_MAX_PARALLEL_TASKS`, `TAG_MAX_PARALLEL_TASKS`, and stage-prefixed
`*_TASK_INPUT_BYTES` / `*_TASK_RESULT_BYTES`. CLI arguments take precedence.

Set `SPARK_EXECUTOR_INSTANCES` to a positive integer to choose the fixed executor
count for any launcher (default 3). Spark dynamic allocation remains disabled.
Task concurrency defaults to this count; `--parallel-tasks` or the stage-specific
environment setting overrides it. Ingestion uses `MAX_FILES_PER_ROUND` instead.
For example, `SPARK_EXECUTOR_INSTANCES=5 ./scripts/run_chunking.sh` requests five
executors and runs up to five batches per wave. Higher concurrency increases
driver memory usage and simultaneous provider requests.

The driver submits each task as an independent single-partition Spark job. A
bounded wave has at most the configured number of parallel jobs, and each completed result is committed
before waiting for slower siblings. Database inserts use bulk values. Chunk
transactions cover one document, while tagging transactions cover one task batch.
Selection is ordered by document/index; parallel completion order is not.

Groq uses one sequential request stream per active task. A Groq task batch is not
a provider bulk API request. Set `TAG_REQUEST_INTERVAL_SECONDS` (default 1.5) to
pace each worker, or set `TAG_REQUESTS_PER_MINUTE` and `TAG_TOKENS_PER_MINUTE` to
your account's shared limits. The adapter divides throughput among configured
workers and conservatively estimates input tokens from UTF-8 bytes. This is
rate shaping, not a cross-process quota ledger: concurrent startup requests and
other applications sharing the account can still receive 429 responses. Workers
honor retry delays, use at most five explicit attempts, and disable SDK retries.

Daily quota exhaustion returns completed outcomes and stops later waves after
all active siblings finish. The blocked item remains pending. Exit codes are 0
for completion, 1 for failure, 2 for quota/long provider cooldown, and 130 for an
interrupt. A job can finish with recorded per-item ERROR rows; inspect the printed
counts and rerun with `--retry-errors`.

Ctrl+C drains and commits the current small wave before exiting; a second
interrupt can force an earlier exit. Each batch prints its committed counts,
while final corpus totals are queried once at the end of the run.

Speculation is disabled and Spark task retries are limited to one attempt.
Database outcomes are idempotent, but an external call cannot be committed
atomically with PostgreSQL. A failed task can repeat up to its batch size on
restart; a driver crash can repeat all uncommitted active batches (up to 30 calls
at defaults). Cumulative attempt counts cover committed outcomes, not calls lost
to a worker/driver crash. There is no exactly-once billing guarantee.

Stage-specific advisory locks prevent simultaneous coordinators of the same
kind, while ingestion, chunking, and tagging can run independently. Changes
committed after a job's source snapshot are picked up on the next invocation.

## Backend interface

`tagging.contracts.AnalyzerBackend` accepts a list of `AnalysisRequest` and returns
`BatchResult`, with one `AnalysisOutcome` per request. A quota stop may return a
partial batch. Implement `close()` to release model/client resources. The worker
validates outcome identities, duplicates, and statuses. Backends are initialized
once per reused Python worker and cached by backend/model identity.

The Groq adapter lives under `tagging/backends/`; deterministic cleaning and
splitting stay under `chunking/`. A future Transformers adapter can tokenize a
whole request list and run native model batches behind the same interface:

```bash
TAGGING_BACKEND=my_adapter:TransformersBackend \
TAGGING_MODEL=my-model \
TAGGING_ANALYSIS_VERSION=my-model-v1 \
./scripts/run_tagging.sh --items-per-task 8
```

Install custom adapters and their dependencies in `VENV_DIR` before packaging.
No Transformers model or GPU resource configuration is included in this change.
GPU scheduling and memory limits must be configured when adopting such a backend.

Chunk identity includes `chunking_version`, covering cleaning, splitting, and
eligibility rules. Analysis identity also includes backend, model, and
`analysis_version`. Change versions when those behaviors change. Completed
materializations are skipped; article text is assumed immutable after ingestion.
The storage API rejects incompatible content if explicitly rematerialized under
the same version, including missing/extra indexes and eligibility changes.

## Validation

```bash
.venv/bin/python -m unittest discover -s tests -v
WARC_TEST_DSN='dbname=disposable_test_db user=tester' \
  .venv/bin/python -m unittest tests.test_processing -v
.venv/bin/python -m tests.processing_spark_smoke
```

The smoke test runs three local Spark chunking jobs and three fake-backend tagging
jobs. It needs Java and local socket access, but consumes no Groq quota and writes
no article data. PostgreSQL tests create and drop isolated schemas in the supplied
test database. Full YARN validation requires the real cluster and worker network
access to the selected model provider.
