# News RAG Pipeline

Stream Common Crawl News archives into PostgreSQL using Apache Spark. The pipeline
extracts article text and metadata, keeps Arabic, English, and French content, and
counts only newly committed articles toward your requested quotas.

[Architecture](docs/architecture.md) · [Module map](docs/module_map.md) ·
[Workflows](docs/workflows.md) · [Validation results](docs/validation.md) ·
[RAG API plan](docs/rag-api-plan.md) ·
[Airflow migration notes](docs/airflow-migration.md)

For parallel post-ingestion processing, use the independent
[Spark processing jobs](docs/processing.md):
`python -m jobs.launcher chunk`, `python -m jobs.launcher tag`, and
`python -m jobs.launcher embed`. These process bounded
batches with driver-owned PostgreSQL commits; tagging supports pluggable model
backends.

## Project layout

```text
ingestion/                Spark pipeline, WARC parsing, extraction, text validation
db/                       PostgreSQL persistence, document loading, inspection
chunking/                 Incremental text splitters
scripts/                  Ingestion, database inspection, and CSV export commands
tests/                    Unit tests and integration/smoke checks
docs/                     Architecture and recorded validation
exports/                  Existing CSV exports
requirements/             Base and optional feature dependency sets
```

Keep feature modules at the repository root and operational commands in
`scripts/`. Add `retrieval/` when its implementation is ready; there are no empty
placeholder packages. Package initializers stay lightweight so ingestion does not
require optional RAG dependencies. See the
[module boundaries](docs/architecture.md#module-boundaries) for extension guidance.

Start Spark stages with `python -m jobs.launcher <stage>` or call
`jobs.launcher.launch(stage, **options)` from Python. See the
[Python launcher API](docs/processing.md#python-api) for supported options and
failure behavior. Inspection and export use `python -m db.inspect` and
`python -m scripts.export_csv`. Import loading and splitting helpers come
directly from `db.documents` and `chunking.splitters`. `scripts/ingest.py` is the
entry point passed to Spark by the launcher.

The existing `db/db_handler.py` path is retained; the former `extractors`,
`parsers`, and `utils` implementations now live together under `ingestion/`.

## Setup

Run ingestion on the Spark master with HDFS and YARN available. The launcher uses
three executors by default with one core each; use `--executor-instances` or `SPARK_EXECUTOR_INSTANCES`
to choose a different fixed count per run. PostgreSQL must be reachable from the master;
workers need matching Python versions and the interpreter path used by the packed
virtual environment. The launcher itself uses only the Python standard library.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements/base.txt
export SPARK_HOME=/opt/spark
export PATH="$SPARK_HOME/bin:$PATH"
```

Use the cluster's `spark-submit`; it supplies PySpark. Set `VENV_DIR` to use a
virtual environment other than `.venv`.

Dependency files are grouped by use: `requirements/base.txt` for ingestion,
`requirements/rag.txt` for ingestion plus document/chunking support,
`requirements/tagging-groq.txt` for RAG plus Groq tagging,
`requirements/embeddings.txt` for the optional retrieval API and local ONNX use,
and `requirements/rag-agent.txt` for the standalone query agent without the
ingestion, Spark, or web-server dependencies.
The Spark embedding worker instead uses the dedicated `.venv-embedding-onnx`
prepared by [the embedding setup](docs/processing.md#embedding), keeping `.venv`
free of embedding-only dependencies.
`requirements/dev.txt` provides ingestion plus test dependencies. Install the tagging
and development files to run all optional processing unit tests.
`chunking/requirements.txt` delegates to `requirements/rag.txt` for compatibility;
dependency versions are maintained only under `requirements/`.

Generated worker environments, Spark JAR archives, and temporary packaging files
stay in `.build-tmp/` (ignored by Git).

The database and role must already exist. The application creates and migrates its
tables, so the role needs schema permissions. Connection defaults are:

```bash
export PGHOST=localhost PGPORT=5432
export PGDATABASE=warcdb PGUSER=warc_user PGPASSWORD=password
```

Override these environment variables for another database.
All four Spark stages load defaults from the project-root `.env`;
CLI flags override exported variables, which override `.env`. Install
`requirements/base.txt` for the dotenv loader. The `.env` file is Git-ignored.

The VMware host helpers
`cluster_up.sh` and `cluster_down.sh` start and stop
the VMs and Hadoop services; run them on the Debian host, not inside a VM.

## Run

Request 1,000 new articles, with a maximum of 100 from each source file:

```bash
python -m jobs.launcher ingest --num-files all --max-accepted-articles 1000 --max-accepted-per-file 100
```

Duplicates, rejected articles, and unsuccessful inserts do not consume quota.
Short files contribute what they have; processing continues through the selected
files until the total is reached or the sources are exhausted.

For a small smoke test:

```bash
python -m jobs.launcher ingest --num-files 1 --max-accepted-articles 10 --max-accepted-per-file 10
```

To validate configuration without submitting a job:

```bash
python -m jobs.launcher ingest --dry-run --max-accepted-articles 1000
```

The final summary reports committed counts, per-file status, rejection counters,
and a resume command. Exit codes are `0` for success, `1` for an operational failure,
and `2` when the selected sources cannot fulfill the target.

## Resume

```bash
python -m jobs.launcher ingest --resume-run-id <printed-run-id>
```

Resume restores the original file selection, quotas, and filtering settings.
Explicit CLI or exported-environment conflicts are rejected; changed `.env` defaults do not block resume. Resource budgets and concurrency can
be adjusted; article and HTML size limits remain fixed for that run. Dry run shows
supplied/default settings without loading a saved run.

An invocation without `RESUME_RUN_ID` starts a new quota and reuses verified source
checkpoints. A file stopped at its per-file cap remains available to later runs;
only a file read to EOF is marked exhausted.

## Airflow automation

The daily DAG is `ingestion_pipeline`. It runs
`probe → download_and_enter_db → chunk → tag → embed` with one active run and one
active task at a time. The probe checks the Common Crawl `warc.paths.gz` index for
the run's month(s), YARN, HDFS (unless `USE_HDFS_CACHE=0`), and PostgreSQL. Ingest
is retried three times; each post-ingestion stage is retried once. Ingest has a
24-hour execution timeout and chunk/tag/embed have 48-hour timeouts; these are hang
guards, not throughput targets.

Each task calls a thin wrapper in `jobs/airflow_tasks.py`, which invokes
`jobs.launcher`. Exit code `2` (sources exhausted before the quota) is logged as
`SOURCES EXHAUSTED` and treated as a successful ingest so the downstream stages can
still drain pending work. Other launcher failures remain task failures.

### Services and UI

Airflow is installed under `/home/spark-master/airflow-venv` with
`AIRFLOW_HOME=/home/spark-master/airflow`. Three systemd units run it:

```bash
sudo systemctl status airflow-scheduler airflow-dag-processor airflow-api-server --no-pager
```

The API server listens on `127.0.0.1:8080`. From your workstation, open an SSH
tunnel and browse to `http://localhost:8080`:

```bash
ssh -L 8080:127.0.0.1:8080 spark-master
```

Use the simple-auth credentials configured in
`/home/spark-master/airflow/airflow.env` (`AIRFLOW__CORE__SIMPLE_AUTH_MANAGER_USERS`).
The metadata database is PostgreSQL, not SQLite.

The CLI needs the same environment as the services. Prefix commands with:

```bash
set -a; . /home/spark-master/airflow/airflow.env; set +a
/home/spark-master/airflow-venv/bin/airflow <command>
```

### Operate the DAG

```bash
# Is the DAG importable?
airflow dags list-import-errors

# Recent runs and per-task state
airflow dags list-runs ingestion_pipeline -o table
airflow tasks states-for-dag-run ingestion_pipeline <run_id> -o table

# Pause/resume new scheduled runs (a running run is not stopped)
airflow dags pause ingestion_pipeline
airflow dags unpause ingestion_pipeline
```

Trigger a bounded smoke run from the CLI. These values override the DAG params
for that run only:

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

The same params are available in the Airflow trigger form. `num_files` accepts
`all` or a positive file count. The ingest limits apply to **each month the run
processes**, not to the run as a whole; `0` means unlimited.

### Backfill a month or year

Backfill dates create one DAG run per day in the range, so use a single
mid-month day when you want one ingest pass over a month. The end date is
exclusive in practice; use the next day:

```bash
# One run whose data interval falls in September 2026.
airflow backfill create \
  --dag-id ingestion_pipeline \
  --from-date 2026-09-15 \
  --to-date 2026-09-16 \
  --dag-run-conf '{"num_files":"all","max_accepted_articles":0,"max_accepted_per_file":0}'
```

For a whole year, create one single-day backfill per month (the DAG allows only
one active run, so they queue and execute in order):

```bash
for month in 01 02 03 04 05 06 07 08 09 10 11 12; do
  airflow backfill create \
    --dag-id ingestion_pipeline \
    --from-date "2025-$month-15" \
    --to-date "2025-$month-16" \
    --dag-run-conf '{"num_files":"all","max_accepted_articles":0,"max_accepted_per_file":0}'
done
```

The daily schedule processes the data interval's month, and also revisits the
previous month on the first day of a month. Use a backfill (or a manual trigger
with `--logical-date`) when you need a specific older month; there is no
`year`/`month` param on the DAG.

### Logs, retries, and recovery

Task logs are in
`/home/spark-master/airflow/logs/dag_id=ingestion_pipeline/run_id=<run_id>/task_id=<task_id>/`.
The UI log viewer shows the same stream. The launcher prints
`[launcher] <step>: <seconds>` lines before Spark starts, and each stage prints a
`PHASE SUMMARY <stage>` JSON line at the end.

Retry a failed task from the UI (Clear) or clear it from the CLI after fixing the
cause. Use the run's logical date as the start and end bound:

```bash
airflow tasks clear ingestion_pipeline \
  -s <logical_date> -e <logical_date> \
  -t download_and_enter_db -y
```

An ingest retry starts a new ingestion run ledger and re-applies its quota; it
does not resume the failed invocation's exact insertion count. Files already
committed are idempotent, but strict monthly caps are not preserved across
retries.

`scripts/supervise_ingest.py` still exists as a manual fallback, but it is not
started by Airflow. Do not run it at the same time as `ingestion_pipeline`: the
ingestion coordinator advisory lock lets only one ingest proceed.

### Airflow smoke test

```bash
airflow dags test airflow_smoke_test
```

This checks the Airflow runtime, `spark-submit`/`hdfs`/`yarn` visibility, the
project venv, the embedding model file, PostgreSQL readiness, and a launcher dry
run. It does not start Spark or touch the ingestion lock.

## Configuration

Ingestion accepts `--lower-kebab-case` flags for these variables (for example,
`--worker-max-candidates` for `WORKER_MAX_CANDIDATES`). Byte limits are integer
bytes. For shared precedence and processing flags, see
[configuration](docs/processing.md#configuration).

| Variable | Default | Purpose |
|---|---:|---|
| `YEAR` / `MONTH` | `2026` / `05` | Monthly CC-NEWS manifest |
| `NUM_FILES` | `all` | File limit; `all`, `0`, or empty selects the remainder |
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
| `SPARK_EXECUTOR_INSTANCES` | `3` | Fixed executor count per run; positive integer |
| `MAX_FILES_PER_ROUND` | executor count | Concurrent file tasks |
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
lookahead. See [memory bounds](docs/architecture.md#memory-bounds) for details.

Use `--no-progress` or `NO_PROGRESS=1` to hide the progress bar and wave output.
`USE_HDFS_CACHE=1`
shares packaged dependencies and Spark jars under `HDFS_APPS_DIR` (default:
`/user/$USER/apps/spark`). Set it to `0` for per-run uploads. The obsolete
`MAX_EXTRACTED_PER_ROUND` setting is rejected; use the worker budgets above.

## Inspect and export

After a run finishes:

```bash
python -m db.inspect
python -m scripts.export_csv
```

The export writes nine article and enrichment tables (including chunks,
analyses, and embeddings) to `exports/` under the project root and copies them
to `/mnt/hgfs/copy_path/warcdb_csv/`. Optional arguments override both directories:

```bash
python -m scripts.export_csv ./exports /path/to/destination
```

For a smaller, shareable export, sample random articles instead. This picks N
random pages and writes only the article-level rows (`websites`, `authors`,
`pages`, `metadata`, `content`) to `exports/sample-N` by default. It does not
export chunk tables or embeddings and does not copy to the HGFS share unless you
pass a destination explicitly:

```bash
python -m scripts.export_csv --sample 10000
python -m scripts.export_csv --sample 10000 ./exports/sample ./path/to/destination
python -m scripts.export_csv --sample 10000 --seed 0.5  # reproducible selection
```

Add `--include-chunks` to include chunk materializations, chunks, and chunk
analyses for the sampled pages (embeddings are still excluded).

Pass `--zip` to also archive the exported CSVs as `<csv_dir>.zip` (for example,
`exports/sample.zip`). The archive is copied to the destination as well when one
is given. Use `--zip-path` for a custom location:

```bash
python -m scripts.export_csv --sample 10000 --zip
python -m scripts.export_csv --sample 10000 --zip-path ./exports/articles.zip
```

`chunk_embeddings.csv` contains the full pgvector values and can be large.
Exporting during an embedding run captures only rows committed so far; rerun
after completion for a complete export.

## RAG integration

Install the optional dependencies with
`.venv/bin/python -m pip install -r requirements/rag.txt`, then consume documents
and chunks incrementally:

```python
from db.documents import iter_documents
from chunking.splitters import iter_document_chunks

for chunk in iter_document_chunks(iter_documents()):
    print(chunk.metadata["doc_id"])
```

### Ask the vector database

Create a dedicated agent environment, configure PostgreSQL and Groq, and point
to the same local BGE-M3 model files used to create the stored vectors. This
keeps both `.venv` and the packaged Spark worker environment unchanged:

```bash
python3 -m venv .venv-rag
.venv-rag/bin/python -m pip install -r requirements/rag-agent.txt
export GROQ_API_KEY=your-key
.venv-rag/bin/python scripts/ask.py "What happened, and why did it matter?"
```

The command always prints the retrieved evidence after the answer, including
chunk IDs, reranker and cosine scores, matched subqueries, sources, and full
chunk text. This diagnostic evidence is also printed when the agent reports
insufficient evidence.

The importable interface is asynchronous:

```python
from retrieval import answer

result = await answer("What happened, and why did it matter?")
print(result.answer)
```

The agent uses `openai/gpt-oss-120b` (override with `RAG_MODEL`) to create at most
three semantic queries, embeds them in one BGE-M3 batch, and runs exact cosine
searches concurrently. It runs that model at `RAG_REASONING_EFFORT=medium`: at
`low`, gpt-oss-120b ignores the answer-language rule and mirrors the evidence's
language (or drifts to an unrelated one), so `medium` is the lowest setting that
reliably answers in the question's language.

Two providers are supported and switching is one variable. Set
`RAG_MODEL=gemini-3.5-flash-lite` (plus `GEMINI_API_KEY`) to run on Google; the
provider is inferred from the model name (`gemini*`/`gemma*` → Google, otherwise
Groq). Set `RAG_PROVIDER=groq|gemini` to force a provider, and a blank `RAG_MODEL`
falls back to the provider default (`groq` → `openai/gpt-oss-120b`, `gemini` →
`gemini-3.5-flash-lite`). Both paths use `json_schema` structured output; the
Gemini client drops the `strict`/`additionalProperties` flags its API rejects.
Each query returns `RERANKER_CANDIDATE_K` (default `20`) cosine candidates, which
a BGE cross-encoder reranks before the best `TOP_K` per query are kept. Repeated
and identical evidence is deduplicated, and adjacent retrieved chunks are joined
without expanding to unranked neighbors. One targeted follow-up round is
permitted when evidence for part of the question is missing.

Download the reranker once into `.models/bge-reranker-v2-m3-int8`:

```bash
python scripts/download_quantized_reranker_model.py
```

The reranker runs locally in the `.venv-rag` process (not on Spark), because its
score depends on a query and a chunk together and cannot be precomputed. The
process holds both the BGE-M3 embedding model and the reranker ONNX graph in
memory, so allow for roughly two 570 MB-class graphs plus ONNX/tokenizer
overhead. Missing or corrupt model files stop the request with a clear error;
there is no silent fallback to cosine-only ranking.

`TOP_K` defaults to `5` per query, `RERANKER_CANDIDATE_K` to `20`, and
`RAG_DB_CONCURRENCY` to `3`, with `RERANKER_CANDIDATE_K >= TOP_K` enforced.
`RERANKER_MODEL_DIR`, `RERANKER_MAX_LENGTH`, `RERANKER_BATCH_SIZE`, and
`RERANKER_INTRA_OP_THREADS` tune the cross-encoder.
`RAG_MODEL`, `RAG_PROVIDER`, `RAG_REASONING_EFFORT`, `CHUNKING_VERSION`,
`EMBEDDING_MODEL`, and `EMBEDDING_VERSION` can override their detected defaults.
The `groq` provider uses strict `json_schema` structured output with
`openai/gpt-oss-120b`; the `gemini` provider uses `json_schema` with
`gemini-3.5-flash-lite` (see `requirements/rag-agent.txt`). Exact cosine search intentionally does not use
the current inner-product HNSW index; a cosine or normalized inner-product HNSW
retriever can replace the database search later without changing the agent.

`RAG_FETCH_BATCH_SIZE` defaults to 1,000 rows. The eager
`load_documents_distributed()` helper requires `limit=` or `RAG_DOCUMENT_LIMIT`.

## Tests

```bash
.venv/bin/python -m pip install -r requirements/dev.txt
.venv/bin/python -m unittest discover -s tests -v
```

Set `WARC_TEST_DSN` to a disposable PostgreSQL database to enable integration tests;
these create and drop isolated schemas. Optional RAG tests require the RAG
dependencies. See [validation results](docs/validation.md) for recorded local and YARN results
and the [test scripts](tests/) for Spark, memory, and packaging checks.
