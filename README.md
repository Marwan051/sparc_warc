# CC-NEWS Article Ingestion

Stream Common Crawl News archives into PostgreSQL using Apache Spark. The pipeline
extracts article text and metadata, keeps Arabic, English, and French content, and
counts only newly committed articles toward your requested quotas.

[Architecture](ARCHITECTURE.md) · [Validation results](VALIDATION.md)

## Setup

Run ingestion on the Spark master with HDFS and YARN available. The launcher uses
three executors with one core each. PostgreSQL must be reachable from the master;
workers need matching Python versions and the interpreter path used by the packed
virtual environment. The launcher also requires `zip`.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
export SPARK_HOME=/opt/spark
export PATH="$SPARK_HOME/bin:$PATH"
```

Use the cluster's `spark-submit`; it supplies PySpark. Set `VENV_DIR` to use a
virtual environment other than `.venv`.

The database and role must already exist. The application creates and migrates its
tables, so the role needs schema permissions. Connection defaults are:

```bash
export PGHOST=localhost PGPORT=5432
export PGDATABASE=warcdb PGUSER=warc_user PGPASSWORD=password
```

Override these environment variables for another database. The VMware host helpers
[cluster_up.sh](cluster_up.sh) and [cluster_down.sh](cluster_down.sh) start and stop
the VMs and Hadoop services; run them on the Debian host, not inside a VM.

## Run

Request 1,000 new articles, with a maximum of 100 from each source file:

```bash
NUM_FILES=all MAX_ACCEPTED_ARTICLES=1000 MAX_ACCEPTED_PER_FILE=100 ./run_to_db.sh
```

Duplicates, rejected articles, and unsuccessful inserts do not consume quota.
Short files contribute what they have; processing continues through the selected
files until the total is reached or the sources are exhausted.

For a small smoke test:

```bash
NUM_FILES=1 MAX_ACCEPTED_ARTICLES=10 MAX_ACCEPTED_PER_FILE=10 ./run_to_db.sh
```

To validate configuration without submitting a job:

```bash
DRY_RUN=1 MAX_ACCEPTED_ARTICLES=1000 ./run_to_db.sh
```

The final summary reports committed counts, per-file status, rejection counters,
and a resume command. Exit codes are `0` for success, `1` for an operational failure,
and `2` when the selected sources cannot fulfill the target.

## Resume

```bash
RESUME_RUN_ID=<printed-run-id> ./run_to_db.sh
```

Resume restores the original file selection, quotas, and filtering settings.
Explicit conflicting overrides are rejected. Resource budgets and concurrency can
be adjusted; article and HTML size limits remain fixed for that run. Dry run shows
supplied/default settings without loading a saved run.

An invocation without `RESUME_RUN_ID` starts a new quota and reuses verified source
checkpoints. A file stopped at its per-file cap remains available to later runs;
only a file read to EOF is marked exhausted.

## Configuration

Application configuration uses environment variables. Byte limits are integer bytes.

| Variable | Default | Purpose |
|---|---:|---|
| `YEAR` / `MONTH` | `2026` / `05` | Monthly CC-NEWS manifest |
| `NUM_FILES` | `15` | File limit; `all`, `0`, or empty selects the remainder |
| `START_FILE_OFFSET` | `0` | Skip this many manifest entries |
| `MAX_ACCEPTED_ARTICLES` | `0` | Total new-article target; `0` means unlimited |
| `MAX_ACCEPTED_PER_FILE` | `0` | Per-file maximum within a run; `0` means unlimited |
| `MIN_WORD_COUNT` | `80` | Minimum extracted word count |
| `USE_TRAFILATURA` | `1` | Main-content extraction before selectolax fallback |
| `LINGUA_MIN_CONFIDENCE` | `0.5` | Minimum language confidence |
| `MAX_HTML_BYTES` | `4194304` | Decoded HTML limit: 4 MiB |
| `MAX_ARTICLE_BYTES` | `1048576` | Serialized article limit: 1 MiB |

### Resource controls

| Variable | Default | Purpose |
|---|---:|---|
| `MAX_FILES_PER_ROUND` | `3` | Concurrent file tasks, capped at three |
| `WORKER_MAX_CANDIDATES` | `100` | Candidates per task |
| `WORKER_MAX_RESULT_BYTES` | `4194304` | Candidate payload per task: 4 MiB |
| `WORKER_MAX_INPUT_BYTES` | `33554432` | Compressed cursor advance per task: 32 MiB |
| `WORKER_MAX_SECONDS` | `120` | Task time budget, checked between records |
| `DB_BATCH_SIZE` | `25` | SQL batch size within a chunk transaction |
| `MAX_RETRIES` | `3` | Total download/commit attempts |
| `SPARK_DRIVER_MEMORY` | `512m` | Driver JVM heap |
| `SPARK_EXECUTOR_MEMORY` | `512m` | Executor JVM heap |
| `SPARK_EXECUTOR_MEMORY_OVERHEAD` | `512m` | Container overhead, including Python |

Default waves return approximately 12 MiB of candidate payload at most. Total
memory also includes Python, JVMs, models, and HTML processing. Reduce concurrency
or result budgets to lower memory pressure; keep the result budget at least as
large as `MAX_ARTICLE_BYTES`. Input/time limits can overshoot by a record and parser
lookahead. See [memory bounds](ARCHITECTURE.md#memory-bounds) for details.

Set `NO_PROGRESS=1` to hide the progress bar and wave output. `USE_HDFS_CACHE=1`
shares packaged dependencies and Spark jars under `HDFS_APPS_DIR` (default:
`/user/$USER/apps/spark`). Set it to `0` for per-run uploads. The obsolete
`MAX_EXTRACTED_PER_ROUND` setting is rejected; use the worker budgets above.

## Inspect and export

After a run finishes:

```bash
.venv/bin/python db_inspect.py
./export_csv.sh
```

The export writes the five article tables to `./warcdb_csv/` and copies them to
`/mnt/hgfs/copy_path/warcdb_csv/`. Optional arguments override both directories:

```bash
./export_csv.sh ./warcdb_csv /path/to/destination
```

## RAG integration

Install the optional dependencies with
`.venv/bin/python -m pip install -r requirements-rag.txt`, then consume documents
and chunks incrementally:

```python
from rag_loader import iter_documents, iter_document_chunks

for chunk in iter_document_chunks(iter_documents()):
    print(chunk.metadata["doc_id"])
```

`RAG_FETCH_BATCH_SIZE` defaults to 1,000 rows. The eager
`load_documents_distributed()` helper requires `limit=` or `RAG_DOCUMENT_LIMIT`.

## Tests

```bash
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m unittest discover -s tests -v
```

Set `WARC_TEST_DSN` to a disposable PostgreSQL database to enable integration tests;
these create and drop isolated schemas. Optional RAG tests require the RAG
dependencies. See [VALIDATION.md](VALIDATION.md) for recorded local and YARN results
and the [test scripts](tests/) for Spark, memory, and packaging checks.
