# Architecture

The pipeline separates parallel article processing from transactional database
writes. Spark workers download, extract, and classify; the driver schedules work
and owns all PostgreSQL writes.

[Usage and configuration](README.md) · [Validation results](VALIDATION.md)

## Data flow

```mermaid
flowchart LR
    M[CC-NEWS manifest] --> D[Driver: allocate quotas]
    D --> W[Up to 3 file tasks]
    S[WARC files over HTTP] --> W
    W --> E[Parse, extract, classify]
    E --> R[Bounded candidates and cursor]
    R --> C[Driver: commit chunk]
    C --> P[(PostgreSQL)]
    P --> D
    P --> L[Streaming RAG loader]
    P --> X[CSV export after run]
```

A **wave** is a bounded set of file tasks executed concurrently. A **chunk** is one
task's result: qualifying candidates, the next source offset, and processing
statistics. The driver waits for the wave to finish, commits its chunks, then
schedules the next wave from persisted state.

## Quota enforcement

The driver assigns each task a candidate allowance constrained by its file's
remaining quota. Allowances across the wave never exceed the remaining global
target. Workers may return fewer candidates when they reach EOF or a resource limit.

PostgreSQL decides which candidates are new using the unique WARC record ID and
`ON CONFLICT DO NOTHING RETURNING`. Only articles whose page, metadata, and content
commit successfully count toward quotas. Duplicates and rejected rows leave room
for subsequent waves. Per-file quotas apply within a run.

## Worker processing

Each task streams from a saved compressed offset and processes records through:

1. **Parsing:** FastWARC reads record boundaries; gzip validation checks integrity.
2. **Extraction:** decode HTML, preserve author/date metadata, then extract main
   content with trafilatura or fall back to selectolax.
3. **Filtering:** enforce size and word limits, classify with Lingua, and retain
   Arabic, English, or French articles that pass the script checks.
4. **Result assembly:** return candidates within the assigned count and byte limits,
   plus a cursor and counters. A candidate that would overflow the result buffer
   is revisited by the next task.

Python workers reuse a cached 20-language detector. Language samples cover the
beginning, middle, and end of the article. Saved provenance includes the source
file, WARC date, and extraction method; Arabic dialect is left unknown.

## Transactions and recovery

A session advisory lock allows **one ingestion coordinator per database**. The
driver reuses that connection and commits each chunk as one transaction containing
article rows, quota counters, file state, and a chunk receipt. `DB_BATCH_SIZE`
controls SQL batch size within that transaction.

If a commit acknowledgement is lost, a retry checks the receipt before inserting
again. Savepoints isolate malformed rows, with JSONL diagnostics written to
`dead_letter/` (configurable through `DEAD_LETTER_DIR`). Persistent failures stop
the run; failed chunks cannot advance the source cursor.

Resume restores persisted quotas and filtering settings and makes failed files
eligible for retry. Operational budgets may change. File states distinguish
`pending`, `quota_reached`, `eof`, and `failed`; run states distinguish `running`,
`complete`, `shortfall`, and `failed`.

Source checkpoints use compressed record boundaries. HTTP Range and available
source validators are checked; a server that ignores Range requires replay to the
saved boundary. Only validated EOF exhausts a source. Resume requires one WARC
record per gzip member. Legacy completed checkpoints are preserved, while legacy
partial offsets restart from zero.

## Memory bounds

Count limits are combined with byte limits. At the defaults, each task returns at
most 4 MiB of candidate JSON payload and a three-task wave returns approximately
12 MiB, plus serialization and result metadata. Decoded HTML is limited to 4 MiB;
an individual serialized article is limited to 1 MiB. Oversized records are skipped.

These are payload bounds, not total process-memory limits. HTML trees, language
models, Python, and the JVM require additional memory. Input/time budgets are
checked between records, so a record, lookahead, or replayed prefix can exceed them.

The launcher uses one core per executor, one native/model compute thread per
worker, fixed executor allocation, and a 64 MiB driver result limit. Chunk statistics
record Python peak RSS, processing time, bytes, and rejection counts. Full container
memory must be assessed through cluster metrics.

## Storage and deployment

| Tables | Responsibility |
|---|---|
| `websites`, `authors` | Shared article attributes |
| `pages`, `metadata`, `content` | Article identity, descriptive fields, and text |
| `ingest_runs`, `ingest_run_files` | Saved configuration, quotas, per-file progress |
| `ingest_chunks` | Commit receipts and task statistics |
| `ingest_files` | Source checkpoints shared across runs |
| `ingest_schema_versions` | Applied schema migrations |

The launcher packages Python dependencies and project modules for YARN. Environment
and Spark-jar fingerprints select reusable archives on HDFS; temporary uploads are
renamed into place. Code is packaged each launch. Shared archives are retained until
manual maintenance removes unused versions.

## Code map

| File | Responsibility |
|---|---|
| [stream_to_db.py](stream_to_db.py) | Configuration, scheduling, workers, progress, and run lifecycle |
| [db/db_handler.py](db/db_handler.py) | Schema, locking, inserts, and durable ingestion state |
| [parsers/parsers.py](parsers/parsers.py) | Streaming WARC parsing and gzip validation |
| [extractors/extractors.py](extractors/extractors.py) | Article text, metadata, and language detection |
| [utils.py](utils.py) | Encoding and language validation |
| [run_to_db.sh](run_to_db.sh) | Packaging and YARN submission |
| [rag_loader.py](rag_loader.py) | Streaming database documents and text chunks |
| [db_inspect.py](db_inspect.py), [export_csv.sh](export_csv.sh) | Inspection and post-run CSV export |

Extraction can leave residual site boilerplate. Downstream RAG processing may need
to filter repetitive footer or subscription text before indexing.
