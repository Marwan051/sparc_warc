# CC-NEWS WARC → PostgreSQL

Distributed article ingestion for Arabic, English, and French. Configure the job
with environment variables. Quotas count **new articles committed to PostgreSQL**;
duplicates, language rejects, and failed inserts do not consume the requested count.

## Run a bounded request

```bash
NUM_FILES=all MAX_ACCEPTED_ARTICLES=1000 MAX_ACCEPTED_PER_FILE=100 ./run_to_db.sh
```

This requests 1,000 new articles, with at most 100 from each file. A short file
contributes what it has; the job continues through the selected files. If there
are not enough qualifying new articles, it reports the shortfall and exits `2`.
The per-file setting is a maximum, not a promise that every file contributes that
many. A zero article quota means unlimited. `NUM_FILES` defaults to **15**;
`NUM_FILES=all`, `0`, or an explicitly empty value selects the remaining manifest.

Start with a small, genuinely capped smoke run:

```bash
NUM_FILES=1 MAX_ACCEPTED_ARTICLES=10 MAX_ACCEPTED_PER_FILE=10 ./run_to_db.sh
```

For the whole manifest without article caps:

```bash
NUM_FILES=all MAX_ACCEPTED_ARTICLES=0 MAX_ACCEPTED_PER_FILE=0 ./run_to_db.sh
```

## Setup

Requirements: Linux, matching Python versions on master/workers, the cluster's
Spark installation, Hadoop/YARN, PostgreSQL reachable from the driver, and `zip`.
The launcher is sized for three executors with one core each.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
export SPARK_HOME=/opt/spark
export PATH="$SPARK_HOME/bin:$PATH"
```

Use the cluster's `spark-submit`; do not install a mismatched PySpark into the
worker environment. `spark-submit` supplies its Python libraries to the driver
and workers. The launcher uses `.venv`; `VENV_DIR` can select another environment.
Workers need the same system Python interpreter path used by `venv-pack`.

Database settings use libpq environment variables:

```bash
export PGHOST=localhost PGPORT=5432 PGDATABASE=warcdb PGUSER=warc_user
# Supply the password through .pgpass, a PostgreSQL service, or PGPASSWORD.
```

Defaults are `localhost:5432`, database `warcdb`, user `warc_user`; no password is
hardcoded. The database and role must already exist, and the role needs permission
to create/alter the ingestion tables. Schema changes are additive and versioned.
Existing articles and completed legacy checkpoints are preserved. Legacy partial
checkpoints restart from zero because their byte offsets were not reliable.
New version-2 partial checkpoints resume from a verified record boundary, including
when a later invocation starts a new quota.

Check configuration without Spark, network access, database writes, or packaging:

```bash
DRY_RUN=1 MAX_ACCEPTED_ARTICLES=1000 ./run_to_db.sh
```

Dry run displays the supplied/default settings; it does not query a saved run.

## Architecture and quotas

1. The driver reads the manifest and creates a persistent run ID.
2. It assigns up to three file tasks per wave. Candidate allowances sum to at
   most the remaining global quota and respect each file's remaining quota.
3. Workers stream WARC records, extract article text, and classify language.
   Each reused Python worker caches one high-accuracy Lingua detector comparing
   20 languages. Filtering settings travel explicitly with each task.
4. Workers return bounded lists of qualifying candidates and the next record
   boundary. They never write to PostgreSQL.
5. The driver collects this bounded wave and commits each chunk's articles,
   metadata, counters, cursor, and receipt in one transaction. PostgreSQL's
   `ON CONFLICT DO NOTHING RETURNING` determines how many new articles count.
6. Duplicates and invalid rows leave quota available for later waves.

A session advisory lock permits one ingestion coordinator per database. The driver
reuses that connection for state reads and commits. Chunk IDs make retrying a lost
commit acknowledgement idempotent. Database batches are limited by `DB_BATCH_SIZE`,
but the entire chunk and its checkpoint commit together.

Malformed database rows are isolated with savepoints. Atomic JSONL diagnostics go
to `dead_letter/` (override with `DEAD_LETTER_DIR`). Persistent database/transport
failures stop the run. Failed chunks never advance the cursor or mark EOF.

## Resume

The job prints its run ID and resume command at startup and in its final summary:

```bash
RESUME_RUN_ID=<printed-run-id> ./run_to_db.sh
```

A resume reloads the original manifest, file selection, quotas, and filtering
settings; failed files become eligible for retry. Explicit conflicting overrides
fail with an error. Unset conflicting variables in your shell before resuming.
A new invocation without `RESUME_RUN_ID` starts a **new** quota.

Resource settings such as `WORKER_MAX_CANDIDATES`, `WORKER_MAX_RESULT_BYTES`,
`WORKER_MAX_INPUT_BYTES`, `WORKER_MAX_SECONDS`, concurrency, and database batch size
can be tuned on resume. HTML/article size limits are persisted filtering rules;
they cannot change midway through a run. The result budget must still accommodate
that run's article-size limit.

Files stopped by a per-file quota are distinct from files exhausted at real EOF.
Only verified EOF marks the shared source checkpoint complete. The parser checks
gzip CRC/trailers and HTTP lengths so truncated streams cannot become completed
checkpoints. Range responses and source validators are checked. If the server
ignores Range, the stream is replayed to the exact saved boundary.

CC-NEWS uses one WARC record per gzip member. A source with multiple records in
one member is rejected when record offsets do not advance, because those offsets
cannot safely support this resume scheme. Gzip validation adds a bounded streaming
validation pass; it does not buffer the source file.

## Configuration

All application settings are environment variables; no application CLI flags.
Byte limits below are integers in **bytes**.

| Variable | Default | Meaning |
|---|---:|---|
| `YEAR`, `MONTH` | `2026`, `05` | CC-NEWS manifest |
| `NUM_FILES` | `15` | Hard file-selection boundary; `all`/`0`/empty = remainder |
| `START_FILE_OFFSET` | `0` | Skip this many manifest entries |
| `MAX_ACCEPTED_ARTICLES` | `0` | Total new-article target; 0 = unlimited |
| `MAX_ACCEPTED_PER_FILE` | `0` | New-article cap per file in this run |
| `MAX_FILES_PER_ROUND` | `3` | Concurrent tasks, capped at 3 |
| `WORKER_MAX_CANDIDATES` | `100` | Candidate cap per task |
| `WORKER_MAX_RESULT_BYTES` | `4194304` | Candidate JSON payload budget (4 MiB) |
| `WORKER_MAX_INPUT_BYTES` | `33554432` | Compressed cursor-advance budget (32 MiB) |
| `WORKER_MAX_SECONDS` | `120` | Task time budget checked between records |
| `MAX_HTML_BYTES` | `4194304` | Maximum decoded HTML body (4 MiB) |
| `MAX_ARTICLE_BYTES` | `1048576` | Maximum serialized article (1 MiB) |
| `MIN_WORD_COUNT` | `80` | Minimum extracted article words |
| `USE_TRAFILATURA` | `1` | Main-content extraction before selectolax fallback |
| `LINGUA_MIN_CONFIDENCE` | `0.5` | Minimum language confidence |
| `DB_BATCH_SIZE` | `25` | Rows per SQL insertion batch within a chunk |
| `MAX_RETRIES` | `3` | Total attempts per download/commit |
| `NO_PROGRESS` | `0` | `1` hides tqdm bar (stderr) and per-wave prints; final summary remains |
| `RESUME_RUN_ID` | unset | Continue an existing run |
| `DRY_RUN` | `0` | `1` validates and prints config only |
| `SPARK_DRIVER_MEMORY` | `512m` | Driver JVM heap |
| `SPARK_EXECUTOR_MEMORY` | `512m` | Executor JVM heap |
| `SPARK_EXECUTOR_MEMORY_OVERHEAD` | `512m` | YARN overhead, including Python workers |
| `USE_HDFS_CACHE` | `1` | Share environment and Spark jars on HDFS |
| `HDFS_APPS_DIR` | `/user/$USER/apps/spark` | Shared artifact directory |

`MAX_EXTRACTED_PER_ROUND` is removed: supplying it gives a migration error pointing
to the worker budget settings. Use accepted-article quotas to bound an entire run.

## Memory and performance

Default waves carry at most approximately 12 MiB of candidate JSON payload, plus
serialization/metadata overhead. This is not a total-RAM limit: Spark's JVM, Python,
Lingua models, HTML trees, decoded bodies, and temporary JSON objects need additional
memory. The launcher uses one executor core and one model/native compute thread
per worker, disables dynamic allocation, and sets a 64 MiB driver result limit.

To reduce result buffers:

```bash
WORKER_MAX_CANDIDATES=25 WORKER_MAX_RESULT_BYTES=1048576 \
MAX_ACCEPTED_ARTICLES=1000 MAX_ACCEPTED_PER_FILE=100 ./run_to_db.sh
```

For less concurrency, set `MAX_FILES_PER_ROUND=1`. For container memory failures,
inspect YARN container diagnostics before changing executor memory/overhead. Increasing
JVM heap alone does not provide more room for the Python process.

Oversized HTML/articles are rejected with counters, not truncated into saved text.
Task input/time budgets are checked between records; one record, parser lookahead,
and network buffering can overshoot them. An ignored HTTP Range can require replaying
a long prefix. A 120-second socket timeout also bounds stalled reads separately.
Worker peak Python RSS, elapsed time, compressed bytes read, rejection counts, and
result payload bytes are persisted in `ingest_chunks.stats`. Python RSS does not
measure the complete YARN container: use YARN metrics/logs for that.

Artifacts are fingerprinted from installed packages, declared dependencies, Python,
and Spark jar contents. Uploads publish through temporary paths and atomic renames.
Older shared artifacts are not automatically pruned while jobs may still use them.
The project-code ZIP is recreated each launch. Clean old artifacts during maintenance
when no applications reference them.

## Extraction and downstream use

Extraction preserves JSON-LD author/date metadata before removing script elements,
accepts legitimate French accents, uses declared HTTP character encodings, and falls
back to selectolax body extraction when trafilatura cannot recover sufficient text.
Language samples cover the beginning, middle, and end without overlapping short
samples. Script checks reject unsupported-language bodies. Arabic dialect is stored
as unknown (`NULL`), rather than assuming MSA. New rows retain WARC date, source file,
and extraction method. Duplicate identity is the WARC record ID, not article URL.

```bash
.venv/bin/python db_inspect.py
.venv/bin/python -m pip install -r requirements-rag.txt
```

Use the streaming RAG API:

```python
from rag_loader import iter_documents, iter_document_chunks

for chunk in iter_document_chunks(iter_documents()):
    # Consume or index each chunk here.
    print(chunk.metadata["doc_id"])
```

The former `langchain.py` module is now `rag_loader.py`; update old imports. The eager
`load_documents_distributed(limit=...)` helper requires an explicit positive limit
(or `RAG_DOCUMENT_LIMIT`). `RAG_FETCH_BATCH_SIZE` defaults to 1000 rows. Streaming
consumption avoids retaining the entire corpus in Python memory.

## Validation

```bash
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m unittest discover -s tests -v
```

To enable real database tests, point `WARC_TEST_DSN` at a **disposable test database**.
Tests create/drop isolated schemas; the role must have schema-creation privileges.

```bash
WARC_TEST_DSN='host=localhost dbname=warc_test user=warc_test' \
.venv/bin/python -m unittest discover -s tests -v
```

The local Spark fixture smoke test uses real worker processes, HTTP streams,
language detection, and transactional inserts. It checks an exact target of seven,
a cap of three per file, and overlap of three tasks:

```bash
export PYSPARK_PYTHON="$PWD/.venv/bin/python"
export PYSPARK_DRIVER_PYTHON="$PYSPARK_PYTHON"
RAYON_NUM_THREADS=1 spark-submit --master 'local[3]' --driver-memory 512m \
  --conf spark.eventLog.enabled=false \
  --conf "spark.pyspark.python=$PYSPARK_PYTHON" \
  --conf "spark.pyspark.driver.python=$PYSPARK_DRIVER_PYTHON" tests/spark_smoke.py
```

This also requires `WARC_TEST_DSN`. It is a local integration test, not evidence of
YARN container health. After code/dependency changes, run the capped one-file smoke
above, then a three-file request (`NUM_FILES=3 MAX_ACCEPTED_ARTICLES=9
MAX_ACCEPTED_PER_FILE=3`). See `VALIDATION.md` for the checks actually performed.

Exit codes: **0** target reached (or uncapped selection finished), **1** operational
failure, **2** selected sources cannot fulfill the requested target. The final
summary includes committed counts, per-file statuses, rejection counters, and resume
command. Stop/failure before commit replays that chunk; successful chunks persist.
