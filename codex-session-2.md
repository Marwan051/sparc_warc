# Codex conversation

## User

can you read the converstion in the md file and know where it stopped

## Assistant

I’ll look for the conversation Markdown file and read it to find where the work stopped.

## Activity

    $ rg --files -g '*.md' -g '!node_modules' -g '!venv' -g '!.git'
    codex-session-01a0eedb-9821-7142-833d-480218657bc1.md
    ✓ • 0ms

## Activity

    $ wc -l codex-session-01a0eedb-9821-7142-833d-480218657bc1.md
        sed -n '1,90p' codex-session-01a0eedb-9821-7142-833d-480218657bc1.md
        tail -n 220 codex-session-01a0eedb-9821-7142-833d-480218657bc1.md
    wc: codex-session-01a0eedb-9821-7142-833d-480218657bc1.md: Permission denied
    sed: can't read codex-session-01a0eedb-9821-7142-833d-480218657bc1.md: Permission denied
    tail: cannot open 'codex-session-01a0eedb-9821-7142-833d-480218657bc1.md' for reading: Permission denied
    ✗ (1) • 19ms

## Activity

    $ cat /home/spark-master/rag_news_project/spark_warc_v2/codex-session-01a0eedb-9821-7142-833d-480218657bc1.md
    cat: /home/spark-master/rag_news_project/spark_warc_v2/codex-session-01a0eedb-9821-7142-833d-480218657bc1.md: Permission denied
    ✗ (1) • 0ms

## Activity

    $ ls -l codex-session-01a0eedb-9821-7142-833d-480218657bc1.md
        id
    -rw------- 1 nobody nogroup 518837 Sep 30 10:51 codex-session-01a0eedb-9821-7142-833d-480218657bc1.md
    uid=1001(hadoop) gid=1001(hadoop) groups=1001(hadoop),65534(nogroup)
    ✓ • 0ms

## Activity

    $ sudo -n tail -n 260 /home/spark-master/rag_news_project/spark_warc_v2/codex-session-01a0eedb-9821-7142-833d-480218657bc1.md
    sudo: a password is required
    ✗ (1) • 0ms

## Assistant

I found [the conversation file](codex-session-01a0eedb-9821-7142-833d-480218657bc1.md), but its permissions prevent me from reading it. Elevated access also failed because sudo requires a password.

Please upload the file here, or run this in your terminal to make it readable:

```bash
sudo chmod a+r /home/spark-master/rag_news_project/spark_warc_v2/codex-session-01a0eedb-9821-7142-833d-480218657bc1.md
```

Then I can read it and identify exactly where the conversation stopped.

## User

done

## Assistant

I’ll read the conversation now and identify the last completed step and what was left pending.

## Activity

    $ wc -l codex-session-01a0eedb-9821-7142-833d-480218657bc1.md
        head -n 65 codex-session-01a0eedb-9821-7142-833d-480218657bc1.md
        tail -n 300 codex-session-01a0eedb-9821-7142-833d-480218657bc1.md
    10341 codex-session-01a0eedb-9821-7142-833d-480218657bc1.md
    # Codex conversation
    
    ## User
    
    read the project at spark_warc and see if there's anything wrong or confusing or needs optimizing and you can ask me
    
    ## Assistant
    
    I’ll review `spark_warc` for bugs, confusing behavior, and worthwhile optimizations, then report the findings with file references.
    
    ## Activity
    
        $ pwd && rg --files -g AGENTS.md -g '!node_modules' -g '!vendor' -g '!dist' /home/spark 2>/dev/null
        /home/spark
        ✗ (1) • 0ms
    
    ## Activity
    
        $ ls -la /home/spark/spark_warc
        total 128
        drwxrwxr-x 12 spark spark  4096 Sep 29 23:27 .
        drwx------ 21 spark spark  4096 Sep 29 23:30 ..
        -rw-rw-r--  1 spark spark    69 Sep 29 23:23 .gitignore
        drwxrwxr-x  6 spark spark  4096 Sep 29 23:28 .venv
        drwxrwxr-x  2 spark spark  4096 Sep 29 23:27 .vscode
        -rw-rw-r--  1 spark spark 14890 Sep 29 23:27 README.md
        drwxrwxr-x  2 spark spark  4096 Sep 29 23:27 __pycache__
        drwxrwxr-x  2 spark spark  4096 Sep 29 23:23 bin
        drwxrwxr-x  5 spark spark  4096 Sep 29 23:22 create
        drwxrwxr-x  2 spark spark  4096 Sep 29 23:20 db
        -rw-rw-r--  1 spark spark  2347 Sep 29 23:20 db_inspect.py
        drwxrwxr-x  2 spark spark  4096 Sep 29 23:20 extractors
        drwxrwxr-x  3 spark spark  4096 Sep 29 23:23 include
        -rw-rw-r--  1 spark spark  2691 Sep 29 23:20 langchain.py
        drwxrwxr-x  3 spark spark  4096 Sep 29 23:23 lib
        lrwxrwxrwx  1 spark spark     3 Sep 29 23:23 lib64 -> lib
        drwxrwxr-x  2 spark spark  4096 Sep 29 23:20 parsers
        -rw-rw-r--  1 spark spark   161 Sep 29 23:23 pyvenv.cfg
        -rw-rw-r--  1 spark spark  1158 Sep 29 23:26 requirements.txt
        -rwxrwxr-x  1 spark spark  5781 Sep 29 23:20 run_to_db.sh
        -rw-rw-r--  1 spark spark 32600 Sep 29 23:27 stream_to_db.py
        -rw-rw-r--  1 spark spark  2915 Sep 29 23:20 utils.py
        ✓ • 0ms
    
    ## Activity
    
        $ for p in /AGENTS.md /home/AGENTS.md /home/spark/AGENTS.md; do if [ -f "$p" ]; then cat "$p"; fi; done; rg --files --hidden -g '!lib/**' -g '!.venv/**' -g '!include/**' -g '!bin/**' -g '!__pycache__/**' -g '!.git/**'
        /bin/bash: line 1: rg: command not found
        ✗ (127) • 0ms
    
    ## Activity
    
        $ git status --short; cat requirements.txt; sed -n '1,240p' README.md
        /bin/bash: line 1: git: command not found
        annotated-doc==0.0.5
        annotated-types==0.8.0
        anyio==4.15.1
        arabic-reshaper==3.0.1
        brotli==1.2.0
        certifi==2026.7.22
        cffi>=1.17.1
        charset-normalizer==3.5.1
        click==8.5.0
        colorama==0.4.4
        exceptiongroup==1.3.1
    ## Assistant
    
    The new driver loop now sends bounded work to all three executors concurrently and commits each result as one database transaction. Global and per-file quotas are based on newly inserted rows, so duplicates and language rejects no longer spend the requested count. Resume state is tied to a printed run ID and uses the same environment-variable style as the existing project.
    
    ## Activity
    
        file changes: Completed · 1 changes
        Delete: /home/spark/spark_warc/README.md
        # CC-NEWS WARC → PostgreSQL (Spark)
    
        Streams Common Crawl News (CC-NEWS) WARC files, extracts article text, detects
        language (ar/en/fr), and loads results into PostgreSQL. Heavy WARC
        download + parse + HTML extraction runs on Spark workers; language filtering
        and DB writes run on the driver.
    
        ## Layout
    
        | File | Purpose |
        |---|---|
        | `stream_to_db.py` | Main job: WARC → DB. Use this for real loads. |
        | `run_to_db.sh` | `spark-submit --master yarn` wrapper for `stream_to_db.py`. |
        | `parsers/parsers.py` | Streaming WARC parser: `warcio` record-at-a-time, no staging. |
        | `extractors/extractors.py` | HTML extraction (**trafilatura** main-content first, selectolax fallback), Lingua language ID (20 languages, no torch). |
        | `db/db_handler.py` | Postgres schema + batched inserts. |
        | `utils.py` | Encoding cleanup, Arabic validation, language gate. |
        | `db_inspect.py` | Prints table counts, checkpoint progress, and sample rows. |
        | `langchain.py` | Loads DB rows into LangChain `Document`s + text splitter (batched server-side cursor, creds from `db_handler.DB_CONFIG`). |
        | `pyspark_venv.tar.gz` | Packed worker venv shipped via `--archives` (rebuild if deps change). |
    
        ## How it runs (workers vs driver)
    
        `stream_to_db.py`:
    
        1. Driver fetches the `warc.paths.gz` manifest, takes the first `NUM_FILES` URLs
           (`NUM_FILES` unset/empty/all/0 = whole manifest).
        2. Rounds over the unfinished-file set (`sc.parallelize(active).mapPartitions(process_partition).toLocalIterator()`) —
           each worker **streams** its WARC file: `warcio` parses each
           article as its bytes arrive, runs `extract_html_fields`, yields fields only
           (`raw_bytes` is dropped before yield). Files with a byte checkpoint resume
           via HTTP `Range` from `bytes_done - RESUME_OVERLAP_BYTES` (see Resume
           below); otherwise the stream starts at byte 0. Hitting `MAX_EXTRACTED_PER_ROUND`
           closes the connection early so each round transfers a bounded chunk; files
           reaching `MAX_ACCEPTED_PER_FILE` accepted articles or EOF drop out of the
           next round's set.
        3. Driver iterates records, batches `DB_BATCH_SIZE` texts through
           `detect_languages_batch`, keeps only
           ar/en/fr (`is_target_language`), calls `save_batch_records`.
    
        So workers do network + CPU-heavy extraction; the driver does language ID
        and all Postgres I/O. `toLocalIterator` streams results — workers are not
        blocked on the driver, but the driver is the throughput bottleneck for large
        `NUM_FILES`. DB writes are single-writer from the driver (no concurrent
        worker writes).
    
        ## Prerequisites
    
        On this master, `pyspark` and `spark-submit` are on PATH. Both the `.venv/`
        environment and the environment at the project root can import the existing
        Spark 4.2.0 installation through `spark_cluster.pth` in their site-packages.
        The system Python also has this connection in the `spark` user's site-packages.
        These files point to `/opt/spark/python` and its matching bundled Py4J library;
        there is no separate PySpark version to keep in sync. VS Code defaults to `.venv`.
    
        ```bash
        cd /home/spark/spark_warc
        source .venv/bin/activate
        python -c 'import pyspark; print(pyspark.__version__)'
        ```
    
        The job inherits the cluster's three-executor memory settings unless overridden
        at submission. Use `./run_to_db.sh` for distributed crawling so the project code
        and Python dependencies are shipped to the workers. Install the requirements
        below before running the full application.
    
        - Hadoop/YARN + Spark 4.2 (`spark-submit` on PATH, `SPARK_HOME=/opt/spark`).
        - Python venv at `.venv/` with `requirements.txt` installed.
        - `venv-pack` and `zip` CLIs (used by the run scripts).
        - PostgreSQL reachable from the driver host (default `localhost:5432`).
    
        ## Configuration
    
        ### Database — `db/db_handler.py:6-12`
    
        ```python
        DB_CONFIG = {"dbname": "warcdb", "user": "warc_user",
                     "password": "password", "host": "localhost", "port": "5432"}
        ```
    
        `init_db()` creates `websites`, `authors`, `pages`, `metadata`, `content`,
        `ingest_files` if missing. Tables are joined as
        `pages → websites/authors`, `metadata.page_id → pages.id`,
        `content.page_id → pages.id`. `warc_record_id` is unique; re-runs upsert.
        `ingest_files` holds byte-range checkpoints per WARC file (see Resume).
    
        ### Job tunables — `stream_to_db.py:18-24`
    
        | Setting | Default | Override |
        |---|---|---|
        | `YEAR` / `MONTH` | `2026` / `05` | edit file |
        | `NUM_FILES` | `15` | files from `START_FILE_OFFSET`; unset/empty/all/0 = to end of manifest |
        | `START_FILE_OFFSET` | `0` | skip the first N manifest entries (file-range targeting) |
        | `MAX_EXTRACTED_PER_ROUND` | 2000 | per-round transfer chunk; `0` = unlimited; counts *extracted* articles (pre-filter, worker-visible), closes the connection early each round |
        | `MAX_ACCEPTED_PER_FILE` | `0` (file to EOF) | per-file stop on *accepted* articles (target-language + fresh, driver-side); the driver re-submits the file from its byte checkpoint until this many are accepted or EOF |
        | `MAX_FILES_PER_ROUND` | `6` | in-flight files per round (bounds task-result blocks for any manifest size); `0` = all unfinished files each round |
        | `MAX_ACCEPTED_ARTICLES` | `0` (unlimited) | global stop on *accepted* articles (target-language + fresh); run stops + cancels Spark tasks when reached |
        | `NO_PROGRESS` | `0` | `NO_PROGRESS=1` disables the stderr progress bar |
        | `RESUME_OVERLAP_BYTES` | `1048576` (1 MiB) | rewind before stored offset on resume; overlap dups collapse via `record_id`; `0` = resume exactly at stored bytes |
        | `USE_HDFS_CACHE` | `1` | `0` disables both shared HDFS artifacts (worker venv + Spark jars), falling back to per-run uploads |
        | `MAX_RETRIES` | `3` | download + DB retry budget |
        | `MIN_WORD_COUNT` | `80` | article word minimum (trafilatura acceptance + yield gate) |
        | `DB_BATCH_SIZE` | `25` | edit file or env |
    
        Renamed in the 2026-09-29 cleanup (old names removed, no fallback):
    
        | Old | New |
        |---|---|
        | `MAX_ARTICLES_PER_FILE` | `MAX_EXTRACTED_PER_ROUND` |
        | `MAX_TOTAL_ARTICLES` | `MAX_ACCEPTED_ARTICLES` (note: counts *accepted*, old counted extracted) |
        | `USE_HDFS_VENV` / `USE_SPARK_ARCHIVE` | `USE_HDFS_CACHE` (single flag for both) |
        | `DOWNLOAD_RETRIES` / `DB_RETRIES` | `MAX_RETRIES` |
        | `USE_TRAFILATURA` (`extractors`) | `"1"` | `USE_TRAFILATURA=0` → legacy selectolax-only extraction |
        | `SPARK_MASTER_URL` | unset (inherit from `spark-submit`) | set only to force, e.g. `local[*]` for local test |
    
        Spark driver/executor memory (`2g` each, 6 executors) is set in
        `stream_to_db.py:get_spark_session`. Language detection runs on the driver,
        so raising driver memory helps more than executor memory for large batches.
        Spark log level is `WARN` on the driver; a `tqdm` progress bar on stderr
        tracks accepted/target when capped, extracted count when uncapped, plus
        files/extracted/rejected/skipped/saved
        (`NO_PROGRESS=1` disables it, final summary print is unchanged).
        Task results stay direct up to 32 MB (`spark.task.maxDirectResultSize`):
        larger results would need a new driver→executor connection, which this
        cluster refuses — keep `MAX_EXTRACTED_PER_ROUND` modest (≤~200) so chunks
        stay well under that budget.
    
        ### Language ID (Lingua, no torch)
    
        `detect_languages_batch` uses `lingua-language-detector` (n-gram models,
        20 languages: ar/en/fr + es/de/it/pt/ca/ro/ru/tr/vi/ja/ko/zh/nl/ta/uk + fa/ur),
        built lazily once per driver process. Top confidence below
        `LINGUA_MIN_CONFIDENCE=0.5` → `other` (rejected by `is_target_language`).
        Short (<20 chars) → `unknown`, script-less → `ignored`. Accepted codes
        (`ar`/`en`/`fr`) additionally require ≤10% of the full text's alpha chars
        outside Latin/Arabic/Cyrillic/CJK — boilerplate chrome (English nav/footer)
        can't smuggle a Kannada/Hindi/Telugu body past the gate on volume.
        Arabic hits are re-validated with `is_valid_arabic_text` (→ `corrupted` on failure), which
        also rejects Arabic-script neighbours Lingua lacks (Kurdish Sorani) or that
        still score `ar` (Persian/Urdu stragglers) via distinctive letters
        (پچژگک ی / ٹڈڑںھے / ەڕڵۆێ). Arabic dialect is always stored as `MSA`
        (no dialect model).
    
        ### Article text extraction (trafilatura)
    
        `extract_html_fields` tries **trafilatura** main-content extraction first
        (`include_comments=False, include_tables=False`), accepted when ≥80 words;
        otherwise it falls back to the legacy selectolax body text. Anything still
        under 80 words is dropped. Each returned record carries
        `extraction: trafilatura|selectolax|...`, and the driver's summary prints the
        split (`via trafilatura` / `via fallback`).
    
        Drop test (200 real CC-NEWS articles, head-to-head, measured 2026-09-24):
        trafilatura-first kept **78.5%** vs old-method-alone 66.5% (**+12pp** — it
        salvages pages whose boilerplate-heavy body falls under the word gate),
        median 443 vs 977 words (~55% boilerplate stripped). Spot checks confirm clean
        article prose including non-Latin scripts. No extra drops: the fallback chain
        is a superset of the old behavior. Note trafilatura is GPL-3.0 (fine for
        internal use).
    
        ## Running
    
        ### 1. Full DB load on the cluster (normal path)
    
        ```bash
        cd /home/spark-master/rag_news_project/spark_warc_project
        ./run_to_db.sh                  # NUM_FILES=15, 2000 articles/file max
        ```
    
        Get-all (whole manifest, no caps):
    
        ```bash
        NUM_FILES=all MAX_ACCEPTED_ARTICLES=0 ./run_to_db.sh
        ```
    
        Capped run (stop after N accepted articles total):
    
        ```bash
        MAX_ACCEPTED_ARTICLES=10000 ./run_to_db.sh
        ```
    
        ### Resume (per-article + byte-range checkpoints)
        Re-running the same command skips already-saved articles (`warc_record_id`
        existence check per batch + in-run set + upsert backstop). Verified:
        second identical run reported `Skipped (already saved): 45, Saved: 0`,
        and `pages` holds 45 rows with zero duplicate `warc_record_id`s.
    
        Beyond that, every run maintains **byte-range checkpoints** in the
        `ingest_files` table (`file_url` PK, `manifest_id`, `bytes_done`,
        `articles_done`, `complete`), namespaced by `YEAR/MONTH`:
        - Files marked `complete` (streamed to true EOF) are never opened again;
          the log reports them as `checkpoint-skipped`.
        - Partial files resume from `bytes_done - RESUME_OVERLAP_BYTES` (default
          1 MiB) via HTTP `Range`, with a forward scan to the next gzip member.
          The ~1 MiB overlap re-yields a few dozen articles that collapse via
          `record_id`; the straddled boundary article is the accepted loss.
        - Checkpoints commit on every `DB_BATCH_SIZE` flush and on file-done
          (**flush-then-commit** order, so a crash only ever re-works one batch).
        - Fallbacks (all automatic, no flags): server ignores `Range` → parse all
          and skip extraction for the stored article count; `416` or resync miss
          → one full-GET retry; checkpoint DB unreachable → run proceeds
          un-checkpointed with a warning.
    
        So a repeat run costs ~zero for finished files and only the unseen tail
        for partial ones — no more re-downloading file 1 every time.
    
        ### Retries / dead-letter
        - File download/parse: 3 attempts with backoff on transient errors
          (5xx/429/timeout); 4xx skips immediately; per-record errors skip the record.
        - DB batch: 3 attempts with rollback + reconnect; persistent failures go to
          `dead_letter/failed-batch-<ts>.jsonl` and the run continues.
    
        What the script does: activates `.venv`, rebuilds `pyspark_venv.tar.gz` only
        if missing, reuses/uploads a content-addressed copy on HDFS
        (`/user/spark-master/apps/spark/pyspark_venv-<md5>.tar.gz` — one upload per
        venv build, old builds pruned to newest 2; falls back to per-run upload if
        HDFS is unreachable), zips `extractors parsers db utils.py` into `--py-files`,
        sets driver python to `.venv` and worker python to `./environment/bin/python`,
        then `spark-submit --master yarn --deploy-mode client stream_to_db.py`.
        `USE_HDFS_CACHE=1` (default) shares the worker venv and Spark jars via
        HDFS instead of per-run uploads
        (disable per-run with `USE_HDFS_CACHE=0`).
    
        ## Cluster ops (learned the hard way)
    
        - **NM disks fill up** → nodes go `UNHEALTHY` (`local-dirs usable space below
          90%`) and the queue stalls with *"cluster resource is empty"*. Check
          `yarn node -list`; culprits are NM localizer caches (one venv copy per app
          version — the HDFS scheme above shrinks this to one per venv build) and
          `userlogs`. On each worker (as `hadoop`):
          `df -h /data/hadoop/tmp <log-dir>`; safe to clear with no apps running:
          `rm -rf /data/hadoop/tmp/nm-local-dir/usercache/*` and old `userlogs/*`.
          Worker-side `yarn-site.xml` mitigations: lower
          `yarn.nodemanager.localizer.cache.cleanup.interval-ms` and
          `yarn.nodemanager.localizer.cache.target-size-mb`.
        - **HDFS safe mode**: if DataNodes die, the NameNode holds safe mode and all
          staging/uploads fail. Restart DNs (`hdfs --daemon start datanode` per worker),
          then `hdfs dfsadmin -safemode wait` on the master.
        - Orphaned `ACCEPTED` apps from killed drivers block the queue:
          `yarn application -list` + `yarn application -kill <id>`.
    
        ### 2. Smoke test (always do this first after dep/code changes)
    
        ```bash
        NUM_FILES=1 MAX_EXTRACTED_PER_ROUND=50 ./run_to_db.sh
        ```
    
        Checks YARN startup, worker imports, WARC fetch, and DB writes in ~2–4 min
        instead of the full run.
    
        ### 3. Local run (no YARN, driver-only Spark)
    
        ```bash
        source .venv/bin/activate
        # Spark workers default to /usr/bin/python3 (no deps) — force the venv:
        export PYSPARK_DRIVER_PYTHON="$PWD/.venv/bin/python" PYSPARK_PYTHON="$PWD/.venv/bin/python"
        python stream_to_db.py           # uses Spark local[*] on this machine
        # or: SPARK_MASTER_URL='local[*]' NUM_FILES=1 python stream_to_db.py
        ```
    
        ### 4. Inspect results
    
        ```bash
        source .venv/bin/activate
        python db_inspect.py
        pg_isready -h localhost -p 5432
        ```
    
        ## Rebuilding the worker env
    
        After changing `requirements.txt` or any worker-side import:
    
        ```bash
        rm pyspark_venv.tar.gz
        ./run_to_db.sh   # rebuilds via venv-pack automatically
        ```
    
        `--py-files` zip is rebuilt on every run, so plain `.py` edits need no
        manual step.
    
        ## Troubleshooting
    
        | Symptom | Cause / fix |
        |---|---|
        | Job forces `local[*]` despite `--master yarn` | Old code called `.master(SPARK_MASTER_URL)` unconditionally. Fixed: master is now inherited from `spark-submit` unless `SPARK_MASTER_URL` is explicitly exported. |
        | `NotADirectoryError: .../project_code.zip/extractors` on workers | Old `extractors.py` ran `os.makedirs()` on a path inside the shipped zip. Fixed by removing HF cache resolution entirely. |
        | `warcio.exceptions.ArchiveLoadFailed: non-chunked gzip` in tests | Test artifact: all records in one gzip member. Real CC files are multi-member; write test WARCs with `WARCWriter(buf, gzip=True)`. |
        | Slow full runs | Bottlenecks: driver-side language filter + single-writer Postgres. Tune chunk size via `MAX_EXTRACTED_PER_ROUND`, bound in-flight files via `MAX_FILES_PER_ROUND`, raise driver memory. Repeat runs are cheap: finished files are checkpoint-skipped, partial files resume by byte offset. |
    
    ## User
    
    continue??
    ✓ • 0ms

## Activity

    $ rg -n '^## User|^## Assistant' codex-session-01a0eedb-9821-7142-833d-480218657bc1.md
    3:## User
    7:## Assistant
    3459:## Assistant
    3463:## Assistant
    3766:## Assistant
    3905:## User
    3911:## Assistant
    4011:## Assistant
    4039:## User
    4043:## Assistant
    4565:## User
    4569:## Assistant
    6794:## Assistant
    7031:## User
    7035:## Assistant
    7055:## User
    7207:## User
    7211:## Assistant
    8506:## Assistant
    10042:## Assistant
    10339:## User
    ✓ • 0ms

## Activity

    $ sed -n '3766,4065p' codex-session-01a0eedb-9821-7142-833d-480218657bc1.md
        sed -n '4540,4595p' codex-session-01a0eedb-9821-7142-833d-480218657bc1.md
        sed -n '6780,6810p' codex-session-01a0eedb-9821-7142-833d-480218657bc1.md
        sed -n '7010,7240p' codex-session-01a0eedb-9821-7142-833d-480218657bc1.md
        sed -n '8490,8525p' codex-session-01a0eedb-9821-7142-833d-480218657bc1.md
    ## Assistant
    
    The isolated checks reproduced several bugs: a cap of 3 saved 26 articles, a small chunk repeatedly processed the same first 5 articles, and failed database writes still allowed the file to be marked complete. Valid accented French text was also rejected as corrupted, and JSON-LD author/date metadata was lost. I’m checking the Spark execution path next to assess whether files actually run in parallel.
    
    ## Activity
    
        Opened https://raw.githubusercontent.com/apache/spark/master/core/src/main/scala/org/apache/spark/api/python/PythonRDD.scala
    
    ## Activity
    
        $ nl -ba utils.py | sed -n '22,85p'; nl -ba extractors/extractors.py | sed -n '245,300p'; nl -ba langchain.py | sed -n '47,78p'; nl -ba README.md | sed -n '240,260p'; ls -l /opt/spark/bin/spark-submit; command -v java; ls /opt/spark/conf
            22
            23    def is_clean_encoding(text: str) -> bool:
            24        if not text or "\ufffd" in text:
            25            return False
            26        mojibake_chars = sum(1 for c in text if c in '¤§¼«¬¦¶±µ°¥¢£©®™¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ')
            27        if len(text) > 0 and (mojibake_chars / len(text)) > 0.03:
            28            return False
            29        return True
            30
            31    def is_valid_arabic_text(text: str) -> bool:
            32        if not text or len(text) < 20:
            33            return False
            34        sample = text[:500]
            35        arabic_chars = len(ARABIC_CHAR_PATTERN.findall(sample))
            36        alpha_chars = sum(1 for c in sample if c.isalpha())
            37        if alpha_chars == 0:
            38            return False
            39        if (arabic_chars / alpha_chars) < 0.40:
            40            return False
            41        # Arabic-script neighbours (fa/ur/ku): a handful of distinctive letters
            42        # disqualifies, genuine Arabic carries none of them.
            43        markers = len(NON_ARABIC_MARKERS.findall(sample))
            44        if markers >= 2 and (markers / max(arabic_chars, 1)) > 0.02:
            45            return False
            46        return True
            47
            48    def decode_and_validate(raw_bytes: bytes) -> Tuple[Optional[str], str]:
            49        if not raw_bytes:
            50            return None, "empty_bytes"
            51        decoded_text = None
            52        try:
            53            decoded_text = raw_bytes.decode("utf-8", errors="strict")
            54        except UnicodeDecodeError:
            55            pass
            56        if not decoded_text:
            57            try:
            58                results = from_bytes(raw_bytes)
            59                best_match = results.best()
            60                if best_match and best_match.encoding:
            61                    if not (best_match.encoding.lower() in ["iso-8859-1", "latin-1"] and best_match.coherence < 0.8):
            62                        decoded_text = str(best_match)
            63            except Exception:
            64                pass
            65        if not decoded_text:
            66            try:
            67                decoded_text = raw_bytes.decode("windows-1256", errors="strict")
            68            except UnicodeDecodeError:
            69                pass
            70        if not decoded_text:
            71            return None, "decode_failed"
            72        if not is_clean_encoding(decoded_text):
            73            return None, "encoding_corrupted"
            74        return decoded_text, "success"
           245            "author": author,
           246            "url": record["url"],
           247            "warc_date": record["warc_date"],
           248            "published_date": pub_date,
           249            "clean_text": clean_text,
           250            "word_count": word_cnt,
           251            "char_count": len(clean_text),
           252            "html_size_bytes": len(record["raw_bytes"]),
           253            "links_count": len(tree.css("a")),
           254            "headings_sample": [node.text(strip=True) for node in tree.css("h1, h2, h3")][:3],
           255            "extraction": extraction,
           256        }
            47        )
            48
            49
            50    def load_documents_distributed() -> List[Document]:
            51        """Load articles as LangChain Documents (name kept for compatibility).
            52
            53        Plain psycopg2 with a server-side cursor: rows stream in
            54        FETCH_BATCH_SIZE batches instead of one driver-side collect(),
            55        so full-corpus loads don't OOM. Credentials come from
            56        db.db_handler.DB_CONFIG (single source of truth).
            57        """
            58        conn = get_connection()
            59        try:
            60            cur = conn.cursor(name="rag_loader")
            61            try:
            62                cur.itersize = FETCH_BATCH_SIZE
            63                cur.execute(_JOIN_QUERY)
            64                documents = [_to_document(row) for row in cur]
            65            finally:
            66                cur.close()
            67        finally:
            68            conn.close()
            69        return documents
            70
            71
            72    def split_documents_into_chunks(documents: List[Document], chunk_size: int = 800, chunk_overlap: int = 100) -> List[Document]:
            73        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap, separators=["\n\n", "\n", ".", " ", ""])
            74        return text_splitter.split_documents(documents)
           240      `yarn application -list` + `yarn application -kill <id>`.
           241
           242    ### 2. Smoke test (always do this first after dep/code changes)
           243
           244    ```bash
           245    NUM_FILES=1 MAX_EXTRACTED_PER_ROUND=50 ./run_to_db.sh
           246    ```
           247
           248    Checks YARN startup, worker imports, WARC fetch, and DB writes in ~2–4 min
           249    instead of the full run.
           250
           251    ### 3. Local run (no YARN, driver-only Spark)
           252
           253    ```bash
           254    source .venv/bin/activate
           255    # Spark workers default to /usr/bin/python3 (no deps) — force the venv:
           256    export PYSPARK_DRIVER_PYTHON="$PWD/.venv/bin/python" PYSPARK_PYTHON="$PWD/.venv/bin/python"
           257    python stream_to_db.py           # uses Spark local[*] on this machine
           258    # or: SPARK_MASTER_URL='local[*]' NUM_FILES=1 python stream_to_db.py
           259    ```
           260
        -rwxr-xr-x 1 spark spark 1040 Sep 20 22:51 /opt/spark/bin/spark-submit
        /usr/bin/java
        fairscheduler.xml.template
        log4j2-json-layout.properties.template
        log4j2.properties.template
        metrics.properties.template
        spark-defaults.conf
        spark-defaults.conf.template
        spark-env.sh
        spark-env.sh.template
        workers
        workers.template
        ✓ • 0ms
    
    ## User
    
    > Should this pipeline preserve every qualifying article, or is some loss acceptable in exchange for faster collection?
    
    Some loss is acceptable
    
    ## Assistant
    
    Since some loss is acceptable, I’d prioritize throughput and reliable stopping over perfectly lossless resume. The Spark path has a major performance issue: `toLocalIterator()` requests one partition at a time, so the six-file round does not run six downloads concurrently. The resume loop and article caps are still worth fixing because they can waste substantial time or exceed the requested workload.
    
    ## Activity
    
        $ .venv/bin/python - <<'PY'
            import io, sys
            sys.path.insert(0, '/tmp')
            import spark_warc_review_checks as checks
            from parsers.parsers import parse_warc_records_streaming
            class BrokenStream:
                def __init__(self): self.raw=io.BytesIO(checks.warc); self.n=0
                def read(self, size=-1):
                    self.n += 1
                    if self.n > 1: raise TimeoutError('simulated interrupted download')
                    return self.raw.read(size)
            try:
                rows=list(parse_warc_records_streaming(BrokenStream()))
                print('parser timeout: silently returned', len(rows), 'of 100 records')
            except Exception as error:
                print('parser propagated:', type(error).__name__)
            from utils import decode_and_validate
            text = 'Les élèves français étudient les événements récents et découvrent une société très développée. ' * 10
            print('French HTML:',decode_and_validate(('<html><body>'+text+'</body></html>').encode())[1])
            PY
            nl -ba extractors/extractors.py | sed -n '209,244p'; nl -ba stream_to_db.py | sed -n '650,678p'
        overlap stall {'saved': 5, 'rounds': 5, 'requested_offsets': [0, 0, 0, 0], 'checkpoint': (16384, 20, False), 'extractions': 20, 'unique_extractions': 5}
        global cap=3 {'saved': 26, 'rounds': 1, 'requested_offsets': [0], 'checkpoint': (16384, 26, False), 'extractions': 26, 'unique_extractions': 26}
        per-file cap=3 {'saved': 50, 'rounds': 1, 'requested_offsets': [0], 'checkpoint': (32768, 50, False), 'extractions': 50, 'unique_extractions': 50}
        failed DB write {'saved': 0, 'rounds': 1, 'requested_offsets': [0], 'checkpoint': (40635, 100, True), 'extractions': 100, 'unique_extractions': 100}
        parser timeout: silently returned 40 of 100 records
        French HTML: encoding_corrupted
           209            text = _trafi_extract(html_str, include_comments=False, include_tables=False)
           210        except Exception:
           211            return ""
           212        if not text:
           213            return ""
           214        return " ".join(text.split())
           215
           216
           217    def extract_html_fields(record: Dict[str, Any], min_words: int = 80) -> Dict[str, Any]:
           218        html_str, status = decode_and_validate(record["raw_bytes"])
           219        if status != "success" or not html_str:
           220            return {"language": "corrupted", "word_count": 0, "clean_text": "", "extraction": "corrupted"}
           221        tree = HTMLParser(html_str)
           222        title_node = tree.css_first("title")
           223        title = title_node.text(strip=True) if title_node else "N/A"
           224        for tag in tree.css(", ".join(UNWANTED_TAGS)):
           225            tag.decompose()
           226        body = tree.body
           227        raw_text = body.text(separator=' ', strip=True) if body else tree.text(separator=' ', strip=True)
           228        fallback_text = " ".join(raw_text.split())
           229        clean_text = fallback_text
           230        extraction = "selectolax"
           231        if USE_TRAFILATURA:
           232            trafi_text = _trafilatura_text(html_str)
           233            if trafi_text and len(trafi_text.split()) >= min_words:
           234                clean_text = trafi_text
           235                extraction = "trafilatura"
           236        word_cnt = len(clean_text.split())
           237        if word_cnt < min_words:
           238            return {"language": "too_short", "word_count": word_cnt, "clean_text": "", "extraction": extraction}
           239        pub_date = extract_publication_date(tree)
           240        if pub_date == "N/A":
           241            pub_date = extract_date_from_text_fallback(tree)
           242        author = extract_author(tree)
           243        return {
           244            "title": title,
           650                    })
           651                    if record.get("extraction") == "trafilatura":
           652                        stats["via_trafilatura"] += 1
           653                    else:
           654                        stats["via_fallback"] += 1
           655
           656                    if MAX_ACCEPTED_ARTICLES > 0 and stats["accepted"] >= MAX_ACCEPTED_ARTICLES:
           657                        limit_reached = True
           658                        break
           659
           660                    if len(db_batch) >= DB_BATCH_SIZE:
           661                        db_batch = _flush_batch(db_batch, seen_ids, stats, file_accepted)
           662                        _commit_progress()
           663                        if MAX_ACCEPTED_PER_FILE > 0:
           664                            for url, n in file_accepted.items():
           665                                if n >= MAX_ACCEPTED_PER_FILE:
           666                                    files_done.add(url)
           667                        _refresh_bar()
           668            finally:
           669                if db_batch:
           670                    _flush_batch(db_batch, seen_ids, stats, file_accepted)
           671                    _commit_progress()
           672                    _refresh_bar()
           673                if limit_reached:
           674                    print("Accepted-article limit reached, cancelling remaining Spark tasks...")
           675                    try:
           676                        sc.cancelAllJobs()
           677                    except Exception as error:
           678                        print(f"cancelAllJobs failed (workers wind down on their own): {error}")
        ✓ • 95ms
    
    ## Assistant
    
    Yes—there are several concrete issues. Given that some loss is acceptable, I’d prioritize wasted work, parallelism, and stopping behavior.
    
    1. **Resume can repeatedly process the same articles.** The 1 MiB rewind can take a small chunk back to its starting point. In my test, four rounds extracted the same five articles repeatedly. The article counter still increased, defeating the stall check. Overlap records should not consume the new-work quota. [stream_to_db.py:708](/home/spark/spark_warc/stream_to_db.py:708)
    
    2. **The Spark workload is effectively sequential across files.** `toLocalIterator()` defaults to requesting one partition at a time; creating six partitions does not make six downloads run concurrently here. This is likely the biggest optimization opportunity. Use bounded concurrent processing; prefetch alone provides only limited overlap. [stream_to_db.py:721](/home/spark/spark_warc/stream_to_db.py:721), [Spark implementation](https://raw.githubusercontent.com/apache/spark/master/core/src/main/scala/org/apache/spark/api/python/PythonRDD.scala)
    
    3. **Article limits are exceeded.** With the default batch size, a global limit of **3 saved 26 articles** in my test. A per-file limit of **3 saved 50** with a 50-article chunk. Enforce the remaining allowance inside batch acceptance, before saving. [stream_to_db.py:299](/home/spark/spark_warc/stream_to_db.py:299)
    
    4. **Failed database writes can leave a file marked complete.** A simulated write failure saved zero articles but produced a completed checkpoint. Subsequent runs skip that file; recovery depends on manually handling dead-letter files. That deserves an explicit failed/deferred status even when some loss is acceptable. [stream_to_db.py:615](/home/spark/spark_warc/stream_to_db.py:615)
    
    5. **Valid French text gets rejected as corrupted.** The encoding check treats ordinary accented letters as corruption above a 3% threshold. I reproduced this with valid UTF-8 French HTML. This systematically undermines one of your three target languages. [utils.py:23](/home/spark/spark_warc/utils.py:23)
    
    6. **JSON-LD author and publication dates are discarded before extraction.** All `<script>` elements are removed before the metadata functions inspect them. My sample returned `N/A` for both fields despite containing valid metadata. Extract metadata before cleaning the tree. [extractors.py:224](/home/spark/spark_warc/extractors/extractors.py:224)
    
    7. **Download errors disappear inside the parser.** A simulated timeout silently returned 40 of 100 records instead of reaching the retry handler. Unknown-length responses can consequently be mistaken for completion. Propagate stream failures separately from malformed individual records. [parsers.py:55](/home/spark/spark_warc/parsers/parsers.py:55)
    
    8. **The LangChain loader still holds the entire corpus in memory.** Its server-side cursor batches database fetching, but the list comprehension accumulates every document. The comment promising protection from full-corpus memory exhaustion is misleading. Yield documents or batches through the splitting stage. [langchain.py:64](/home/spark/spark_warc/langchain.py:64)
    
    Some smaller cleanup items:
    
    - The documented “50-article smoke test” only limits each round; it can continue through the whole file. [README.md:245](/home/spark/spark_warc/README.md:245)
    - Database credentials are hardcoded. [db_handler.py:6](/home/spark/spark_warc/db/db_handler.py:6)
    - `.gitignore` contains `*`, which would hide all untracked project files from Git. [.gitignore](/home/spark/spark_warc/.gitignore)
    
    Python and shell syntax checks passed. These findings combine code inspection with isolated tests using generated WARC data and mocked database/Spark services; I did not run a live crawl or change project code.
    
    ## User
    
    ok look this is what i want and i want you to work till you do it. i want to tell it how many articles i want, how many per file i need and it should do it accrdingly with other cosiderations to tune it to avoid oom issues. also the arichtecure of sending the num of articles to master for lang detection and it being not sure of the num that would be inserted and it may not be right doesn't sound right to me right ? work out a plan
    
    ## Assistant
    
    You’re right: the workers currently stop by extracted count, while the master decides which articles qualify. That makes the requested counts hard to enforce and wastes transfers. I’ll plan around counting successfully inserted articles, with explicit per-file limits and memory bounds, and check where language detection fits on your cluster.
    
    ## Activity
    
        $ cat /opt/spark/conf/spark-defaults.conf; cat /opt/spark/conf/workers; cat /opt/spark/conf/spark-env.sh; free -m
        # Sized for three workers with 2 GB RAM each. Client mode leaves the driver on the master.
        spark.master yarn
        spark.submit.deployMode client
        spark.executor.instances 3
        spark.executor.cores 1
        spark.executor.memory 512m
        spark.executor.memoryOverhead 384m
        spark.driver.memory 512m
        spark.driver.memoryOverhead 384m
        spark.yarn.am.memory 128m
        spark.yarn.am.memoryOverhead 256m
        spark.dynamicAllocation.enabled false
        spark.driver.extraJavaOptions -Djava.net.preferIPv4Stack=true
        spark.executor.extraJavaOptions -Djava.net.preferIPv4Stack=true
        spark.yarn.am.extraJavaOptions -Djava.net.preferIPv4Stack=true
        spark.yarn.jars local:/opt/spark/jars/*
                    return Response(warc[start:], 206, {'Content-Range':f'bytes {start}-{len(warc)-1}/{len(warc)}'})
                return Response(warc)
            def save(batch):
                if fail_save: return 0, '/tmp/mock-dead-letter'
                saved.update(item['record_id'] for item in batch)
                return len(batch), None
            def upsert(manifest, file, nbytes, count, complete):
                progress[file] = (nbytes, count, complete)
            def extract(record, min_words):
                extracted.append(record['record_id'])
                return {'word_count':100,'clean_text':'example '*100}
            with contextlib.ExitStack() as s:
                for attr, value in {'get_spark_session':lambda:spark, 'init_db':lambda:None, 'load_ingest_progress':lambda _: {}, 'upsert_ingest_progress':upsert, 'get_connection':Connection, '_filter_already_saved':lambda conn, ids:set(ids)&saved, '_save_batch_with_retry':save, 'detect_languages_batch':lambda texts:['en']*len(texts), 'extract_html_fields':extract, 'MAX_EXTRACTED_PER_ROUND':chunk,'MAX_ACCEPTED_ARTICLES':global_cap,'MAX_ACCEPTED_PER_FILE':file_cap,'NUM_FILES':1,'USE_PROGRESS_BAR':False}.items():
                    s.enter_context(patch.object(job,attr,value))
                s.enter_context(patch.object(job.urllib.request,'urlopen',open_url))
                output=io.StringIO()
                with contextlib.redirect_stdout(output): job.run_streaming_pipeline()
            print(name, {'saved':len(saved),'rounds':spark.rounds,'requested_offsets':requests,'checkpoint':progress.get(url),'extractions':len(extracted),'unique_extractions':len(set(extracted))})
    
        run('overlap stall', chunk=5)
        run('global cap=3', global_cap=3)
        run('per-file cap=3', file_cap=3, chunk=50)
        run('failed DB write', fail_save=True)
        ✓ • 0ms
    
    ## User
    
    also one more thing. find all issues and find good optimizations for the code. continue.
    
    ## Assistant
    
    I’ll expand the plan to cover the rest of the correctness, performance, and maintainability issues too. For now, I’ll assume the quotas mean newly inserted articles, “per file” is a maximum, and restarting a run should finish its remaining quota. I’ll make those assumptions explicit in the plan.
    
    The cluster is configured for three workers with 2 GB RAM each, so moving the current language detector onto every worker needs a memory check first.
    
    ## Activity
    
        $ cat db/db_handler.py; cat langchain.py; cat run_to_db.sh; cat requirements.txt; cat .gitignore; cat .venv/lib/python3.13/site-packages/lingua_language_detector-2.2.0.dist-info/METADATA | sed -n '100,220p'
        import psycopg2
        from psycopg2.extras import execute_values
        from urllib.parse import urlparse
        import json
    
        DB_CONFIG = {
            "dbname": "warcdb",
            "user": "warc_user",
            "password": "password",
            "host": "localhost",
            "port": "5432"
        }
    
        def get_connection():
            return psycopg2.connect(**DB_CONFIG)
    
        def init_db():
            create_tables_query = """
        def is_warc_10(record: WarcRecord) -> bool: ...
    
    
        def is_warc_11(record: WarcRecord) -> bool: ...
    
    
        def has_block_digest(record: WarcRecord) -> bool: ...
    
    
        def has_valid_block_digest(record: WarcRecord) -> bool: ...
    
        (stream, record_types=Ellipsis, parse_http=True, min_content_length=None, max_content_length=None, func_filter=None, verify_digests=False, quirks_mode=False, auto_decode='none', max_header_len=Ellipsis, stream_detect=True, buffer_size=Ellipsis, inplace=False, fsspec_args=None, *, strict_mode=True)
        ✓ • 0ms
    
    ## Assistant
    
    The memory check supports keeping accuracy first: the installed detector used about 71 MiB peak RSS in a small seven-language test, so there’s no need to downgrade it based on that result.
    
    I’m shaping the design around workers extracting and classifying articles, while the master allocates quotas and counts actual database inserts. Each parallel batch will also have a byte limit—an article-count limit alone cannot prevent OOM when article sizes vary.
    
    ## Activity
    
        $ .venv/bin/python - <<'PY'
            import io,time
            from fastwarc.warc import ArchiveIterator as FastIterator
            from warcio.archiveiterator import ArchiveIterator as PyIterator
            from warcio.warcwriter import WARCWriter
            from warcio.statusandheaders import StatusAndHeaders
            buf=io.BytesIO(); writer=WARCWriter(buf,gzip=True); starts=[]
            for i in range(1000):
             starts.append(buf.tell())
    - Read database credentials from standard PostgreSQL environment settings.
    - Replace wildcard `.gitignore`, remove unused code/imports, and separate direct runtime, optional RAG, and development dependencies.
    - Fingerprint worker environments and Spark archives; rebuild when their inputs change. Upload atomically and remove automatic pruning that can affect active jobs.
    - Update README examples, especially the currently misleading smoke test and memory/concurrency descriptions.
    
    ## 5. Tests and rollout
    
    Implement regression tests alongside each subsystem change.
    
    - **Quotas:** targets smaller than one batch, non-divisible totals, per-file caps, duplicate-only chunks, rejected languages, short files, and exhausted manifests.
    - **Database:** real PostgreSQL integration tests for rollback, duplicate IDs within a batch, malformed rows, reconnects, uncertain commits, and resume without double-counting.
    - **Resume:** generated multi-member WARCs, exact boundaries, ignored Range requests, truncation, corrupted members, oversized records, and long stretches with no accepted articles.
    - **Language/metadata:** curated Arabic, accented French, English, Persian, Urdu, Spanish, mixed-language pages, and JSON-LD metadata.
    - **Memory/concurrency:** verify overlapping execution of three tasks, enforce serialized byte limits, and run repeated maximum-size chunks to check that memory stabilizes.
    - **Downstream:** verify documents and chunks are consumed incrementally.
    - **Packaging:** test clean installation, worker imports from the shipped archive, configuration forwarding, and archive invalidation.
    
    Roll out through local fixtures and a disposable PostgreSQL database, then one-worker and three-worker YARN smoke runs. Compare throughput and memory against the current implementation before increasing limits.
    
    Exit statuses will distinguish success (`0`), operational failure (`1`), and an unmet target/source shortfall (`2`). Final output will show requested versus committed counts, per-file contributions, rejection reasons, failures, and the resume command.
    
    ## User
    
    why are you using --. the readme specifies env vars
    
    ## Assistant
    
    You’re right. I introduced CLI flags unnecessarily; the plan should preserve the README’s environment-variable interface.
    
    Your command stays:
    
    ```bash
    MAX_ACCEPTED_ARTICLES=1000 MAX_ACCEPTED_PER_FILE=100 ./run_to_db.sh
    ```
    
    The change is in **what those counts mean**: successfully committed new articles, excluding duplicates and rejected articles.
    
    Memory tuning will also use environment variables. New capabilities, such as resuming a particular run, will follow the same convention:
    
    ```bash
    RESUME_RUN_ID=... ./run_to_db.sh
    ```
    
    I’ll remove the CLI migration from the plan and keep configuration consistent with the existing project.
    
    ## User
    
    ok add it to the plan
    
    ## Plan
    
    # Reliable article quotas, bounded memory, and project cleanup
    
    ## 1. Behavior and environment-variable interface
    
    Keep configuration through **environment variables**, as documented in the README. Do not introduce application CLI flags.
    
    Example:
    
    ```bash
    NUM_FILES=all \
    MAX_ACCEPTED_ARTICLES=1000 \
    MAX_ACCEPTED_PER_FILE=100 \
    ./run_to_db.sh
    ```
    
    This requests exactly **1,000 newly committed articles**, with at most **100 from each file**. Duplicates, rejected articles, and unsuccessful inserts do not consume either quota.
    
    - Files with fewer qualifying articles contribute what they have; additional files are processed until the total is reached.
    - Preserve `NUM_FILES=15` as the default. `NUM_FILES=all` permits searching the remaining manifest; an explicit file limit remains a hard boundary.
    - Preserve `0` as unlimited for global and per-file article quotas.
    - Keep `YEAR`, `MONTH`, `START_FILE_OFFSET`, `MIN_WORD_COUNT`, `DB_BATCH_SIZE`, and `MAX_RETRIES`.
    - Add `RESUME_RUN_ID` for finishing an existing request and `DRY_RUN=1` for displaying configuration without starting ingestion.
    - A new invocation without `RESUME_RUN_ID` starts a new quota. Resume reloads persisted quotas and filtering settings; conflicting explicit overrides fail clearly.
    - Validate configuration before starting Spark. Memory limits, batch sizes, concurrency, and retry counts must be positive.
    - Update the README and launcher together so examples and defaults agree.
    
    Assumptions: target languages remain Arabic, English, and French; per-file quotas apply within a run; some malformed or oversized articles may be skipped; language detection remains accuracy-first.
    
    ## 2. Parallel processing and authoritative counts
    
    **Data flow:** allocate allowances → parallel extraction and classification → bounded results → transactional insertion → update quotas and checkpoints.
    
    ### Workers
    
    - Each task processes a bounded portion of one WARC file.
    - Extract, validate, and classify articles on the worker. Return only qualifying candidates, source positions, rejection counters, and resource measurements.
    - Cache one high-accuracy Lingua detector per Python worker, retaining the existing 20-language comparison set and confidence threshold.
    - Pass worker configuration explicitly rather than relying on environment variables propagating through YARN.
    - Keep workers free of database writes so Spark retries cannot duplicate side effects.
    
    ### Master
    
    - Schedule at most three file tasks concurrently.
    - Allocate candidate allowances whose sum never exceeds the remaining global quota; each allowance also respects the file’s remaining quota.
    - Replace sequential `toLocalIterator()` processing with `collect()` over one strictly bounded wave.
    - Use `ON CONFLICT DO NOTHING RETURNING` and count only newly inserted pages whose associated content and metadata commit successfully.
    - Continue scheduling when duplicates or rejected candidates leave quotas unfilled.
    - Replace the growing whole-run `seen_ids` set with bounded chunk deduplication and the database’s unique constraint.
    - Allow one active ingestion coordinator through a PostgreSQL advisory lock.
    
    ### Durable state
    
    - Add run, per-run file, and committed-chunk records containing quotas, configuration, status, and committed counts.
    - Assign stable chunk identifiers. Commit article data, counters, checkpoint, and chunk acknowledgment in the same transaction.
    - Resolve uncertain commit outcomes by checking the chunk identifier before retrying.
    - Distinguish quota reached, genuine EOF, and failure. A per-file quota must not permanently mark the source exhausted.
    - Print the run ID and exact environment-based resume command at startup:
    
    ```bash
    RESUME_RUN_ID=<printed-run-id> ./run_to_db.sh
    ```
    
    ## 3. Memory bounds and reliable resume
    
    Initial defaults:
    
    | Environment setting | Default |
    |---|---:|
    | `MAX_FILES_PER_ROUND` | 3 |
    | `WORKER_MAX_CANDIDATES` | 100 |
    | `WORKER_MAX_RESULT_BYTES` | 4 MiB |
    | `MAX_HTML_BYTES` | 2 MiB decoded |
    | `MAX_ARTICLE_BYTES` | 512 KiB serialized |
    | `WORKER_MAX_INPUT_BYTES` | 32 MiB compressed |
    | `WORKER_MAX_SECONDS` | 120 |
    | `DB_BATCH_SIZE` | 25 |
    | `SPARK_EXECUTOR_MEMORY` | 512 MiB |
    | `SPARK_EXECUTOR_MEMORY_OVERHEAD` | 512 MiB |
    | `SPARK_DRIVER_MEMORY` | 512 MiB |
    
    Use one executor core and one model thread per worker. Replace the obsolete `MAX_EXTRACTED_PER_ROUND` control with a clear error directing users to `WORKER_MAX_CANDIDATES`.
    
    - Enforce both record-count and serialized-byte limits. Three tasks return at most approximately 12 MiB of article payload per wave.
    - Check input/time budgets between records, including when no articles qualify.
    - Reject oversized articles with recorded reasons rather than silently truncating their text.
    - Preserve the current record for the next task when a result buffer fills.
    - Measure Python RSS, complete executor-container memory, result sizes, processing times, and throughput. Validate these defaults under sustained load.
    
    ### Parsing and checkpoints
    
    - Replace the misleading FastWARC-named wrapper with an actual adapter to the installed FastWARC parser; retain warcio for test fixtures.
    - Bound headers and decoded payload reads, including HTTP-compressed bodies.
    - Store verified compressed record boundaries, using lookahead to identify the next unprocessed record.
    - Remove arbitrary overlap and extracted-count skipping.
    - Validate HTTP ranges and source identity. When Range is unavailable, replay to the saved record boundary.
    - Advance through rejected and non-HTML records as well as accepted articles.
    - Propagate transport, decompression, and truncation failures; mark EOF only after a validated clean end.
    - Retry transient failures with bounded backoff. Persistent database failures stop the run without advancing checkpoints.
    - Isolate malformed individual rows so one bad record does not discard a batch. Write diagnostic files atomically with unique names.
    - Treat exhausted retries or unchanged cursors as failures, replacing the arbitrary 1,000-round escape.
    
    ## 4. Other correctness and optimization work
    
    ### Extraction and language quality
    
    - Fix the encoding heuristic that rejects legitimate French accents; respect declared encodings and test real mojibake separately.
    - Read author/date metadata before removing scripts. Support JSON-LD objects, lists, and `@graph`.
    - Run main-content extraction first; construct fallback body text only when needed.
    - Sample the first 800, middle 600, and last 600 characters for language detection, avoiding overlapping samples on short texts.
    - Count alphabetic characters consistently in script checks without allocating full-text character lists.
    - Store unknown Arabic dialect as unknown instead of assigning `MSA` universally.
    - Validate URLs and metadata, remove PostgreSQL-incompatible NUL characters, and remove inappropriate fixed-width metadata constraints.
    - Correct hostname normalization and retain source-file, WARC-date, and extraction-method provenance for new records.
    
    ### Database and downstream loading
    
    - Reuse the driver connection instead of reconnecting for each lookup, write, and checkpoint.
    - Use additive, versioned migrations; preserve existing articles and completed checkpoints.
    - Restart legacy partial checkpoints from the beginning because their offsets are unreliable. Existing record IDs prevent duplicate inserts.
    - Stream documents and chunks through iterator APIs. Eager compatibility helpers require an explicit document limit.
    - Rename the misleading `langchain.py` entrypoint and update references.
    - Correct “latest rows” ordering in database inspection and add run/quota/failure summaries.
    
    ### Packaging and maintainability
    
    - Read credentials through standard PostgreSQL environment settings.
    - Replace wildcard `.gitignore`, remove unused code/imports, and separate direct runtime, optional RAG, and development dependencies.
    - Fingerprint worker environments and Spark archives, rebuilding when inputs change.
    - Upload artifacts atomically; remove automatic pruning that can affect active jobs.
    - Update smoke tests, configuration tables, resource guidance, and architecture explanations in the README.
    
    ## 5. Validation and rollout
    
    Implement regression tests alongside each subsystem change:
    
    - **Quotas:** targets below batch size, non-divisible totals, per-file limits, duplicate-only chunks, language rejection, short files, and exhausted manifests.
    - **Database:** real PostgreSQL tests for rollback, repeated IDs within a batch, malformed rows, reconnects, uncertain commits, and resume without double-counting.
    - **Parsing:** exact record boundaries, ignored Range requests, truncated/corrupted members, oversized records, and long stretches without qualifying articles.
    - **Quality:** Arabic, accented French, English, Persian, Urdu, Spanish, mixed-language pages, corrupted encoding, and JSON-LD metadata.
    - **Resources:** confirm three tasks actually overlap, enforce byte limits, and repeatedly process maximum-size chunks to verify stable memory.
    - **Downstream/package:** incremental document consumption, clean installation, worker imports, environment forwarding, and archive invalidation.
    
    Roll out through generated fixtures and a disposable PostgreSQL database, then one-worker and three-worker YARN smoke runs. Compare throughput and memory with the current implementation before raising limits.
    
    Use exit status `0` for success, `1` for operational failure, and `2` for an unmet target/source shortfall. Final output must show requested versus committed counts, per-file contributions, rejection reasons, failures, and the resume command.
    
    ## User
    
    ok start implmenting the plan and do not forget to modify the readme accordingyl
    
    ## Assistant
    
    I’m starting with the ingestion core: worker-side language detection, exact committed-article quotas, bounded parallel waves, and durable run/checkpoint state. Then I’ll fold in the extraction fixes, streaming downstream loader, launcher settings, tests, and README updates.
    
    ## Activity
    
        $ sed -n '1,220p' db/db_handler.py; sed -n '1,220p' extractors/extractors.py
        import psycopg2
        from psycopg2.extras import execute_values
        from urllib.parse import urlparse
        import json
    
        DB_CONFIG = {
            "dbname": "warcdb",
            "user": "warc_user",
            "password": "password",
            "host": "localhost",
            "port": "5432"
        }
    
        def get_connection():
            return psycopg2.connect(**DB_CONFIG)
    
        def init_db():
            create_tables_query = """
            CREATE TABLE IF NOT EXISTS websites (
                id SERIAL PRIMARY KEY,
                domain VARCHAR(255) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        +        extraction = "selectolax"
        +    clean_text = clean_text.replace("\x00", "")
             word_cnt = len(clean_text.split())
        @@ -238,6 +261,4 @@
                 return {"language": "too_short", "word_count": word_cnt, "clean_text": "", "extraction": extraction}
        -    pub_date = extract_publication_date(tree)
             if pub_date == "N/A":
                 pub_date = extract_date_from_text_fallback(tree)
        -    author = extract_author(tree)
             return {
        @@ -255,2 +276,2 @@
                 "extraction": extraction,
        -    }
        \ No newline at end of file
        +    }
    
    ## Assistant
    
    The first implementation pass has landed for the database and extraction layers: run/chunk state is transactional, new-row counts come from `RETURNING`, French accents are no longer treated as corruption, JSON-LD is read before scripts are removed, and the parser now uses FastWARC with bounded payloads and real record offsets. I’m replacing the driver loop now so those pieces work together.
    
    ## Activity
    
        file changes: Completed · 1 changes
        Delete: /home/spark/spark_warc/stream_to_db.py
        import sys
        import os
        import time
        import json
        import hashlib
        import gzip
        import socket
        import urllib.request
        import urllib.error
        from datetime import datetime, timezone
        from pyspark.sql import SparkSession
    
    ✓ • 0ms

## Activity

    $ sed -n '7211,10341p' codex-session-01a0eedb-9821-7142-833d-480218657bc1.md | rg -n '^    (Add:|Update:|Delete:|\$)|^## Assistant|^The |^I’m'
    1:## Assistant
    3:I’m starting with the ingestion core: worker-side language detection, exact committed-article quotas, bounded parallel waves, and durable run/checkpoint state. Then I’ll fold in the extraction fixes, streaming downstream loader, launcher settings, tests, and README updates.
    7:    $ sed -n '1,220p' db/db_handler.py; sed -n '1,220p' extractors/extractors.py
    426:    $ .venv/bin/python - <<'PY'
    438:    Delete: /home/spark/spark_warc/db/db_handler.py
    637:    Add: /home/spark/spark_warc/db/db_handler.py
    985:    Delete: /home/spark/spark_warc/parsers/parsers.py
    1059:    Add: /home/spark/spark_warc/parsers/parsers.py
    1296:## Assistant
    1298:The first implementation pass has landed for the database and extraction layers: run/chunk state is transactional, new-row counts come from `RETURNING`, French accents are no longer treated as corruption, JSON-LD is read before scripts are removed, and the parser now uses FastWARC with bounded payloads and real record offsets. I’m replacing the driver loop now so those pieces work together.
    1303:    Delete: /home/spark/spark_warc/stream_to_db.py
    2083:    Add: /home/spark/spark_warc/stream_to_db.py
    2663:    Delete: /home/spark/spark_warc/.gitignore
    2670:    Add: /home/spark/spark_warc/.gitignore
    2791:    $ .venv/bin/python -m py_compile stream_to_db.py utils.py extractors/extractors.py parsers/parsers.py db/db_handler.py langchain.py db_inspect.py; bash -n run_to_db.sh
    2796:    $ .venv/bin/python -m pip show venv-pack pytest langchain-core langchain-text-splitters | sed -n '1,100p'
    2832:## Assistant
    2834:The new driver loop now sends bounded work to all three executors concurrently and commits each result as one database transaction. Global and per-file quotas are based on newly inserted rows, so duplicates and language rejects no longer spend the requested count. Resume state is tied to a printed run ID and uses the same environment-variable style as the existing project.
    2839:    Delete: /home/spark/spark_warc/README.md
    ✓ • 0ms

## Activity

    $ sed -n '9870,10048p' codex-session-01a0eedb-9821-7142-833d-480218657bc1.md
        rg --files -g '!*.md' -g '!*.pyc' -g '!*.tar.gz' -g '!*.zip' -g '!node_modules' -g '!.venv'
    ## Activity
    
        file changes: Completed · 1 changes
        Delete: /home/spark/spark_warc/.gitignore
        # Created by venv; see https://docs.python.org/3/library/venv.html
        *
    
    ## Activity
    
        file changes: Completed · 1 changes
        Add: /home/spark/spark_warc/.gitignore
        __pycache__/
        *.py[cod]
        .venv/
        create/
        lib/
        lib64
        bin/
        include/
        pyvenv.cfg
        pyspark_venv.tar.gz
        spark-libs*.zip
        .venv-pack.fingerprint
        dead_letter/
        .pytest_cache/
        .coverage
    
    ## Activity
    
        file changes: Completed · 1 changes
        Update { move_path: None }: /home/spark/spark_warc/langchain.py
        @@ -2,3 +2,3 @@
         import os
        -from typing import List
        +from typing import Iterable, Iterator, List, Optional
         from langchain_core.documents import Document
        @@ -10,3 +10,3 @@
    
        -from db.db_handler import DB_CONFIG, get_connection
        +from db.db_handler import get_connection
    
        @@ -48,11 +48,5 @@
    
        -
        -def load_documents_distributed() -> List[Document]:
        -    """Load articles as LangChain Documents (name kept for compatibility).
    
        -    Plain psycopg2 with a server-side cursor: rows stream in
        -    FETCH_BATCH_SIZE batches instead of one driver-side collect(),
        -    so full-corpus loads don't OOM. Credentials come from
        -    db.db_handler.DB_CONFIG (single source of truth).
        -    """
        +def iter_documents(limit: Optional[int] = None) -> Iterator[Document]:
        +    """Stream Documents from a server-side cursor without corpus accumulation."""
             conn = get_connection()
        @@ -62,4 +56,10 @@
                     cur.itersize = FETCH_BATCH_SIZE
        -            cur.execute(_JOIN_QUERY)
        -            documents = [_to_document(row) for row in cur]
        +            query = _JOIN_QUERY
        +            params = ()
        +            if limit is not None:
        +                query = _JOIN_QUERY.rstrip().rstrip(";") + " LIMIT %s;"
        +                params = (limit,)
        +            cur.execute(query, params)
        +            for row in cur:
        +                yield _to_document(row)
                 finally:
        @@ -68,7 +68,27 @@
                 conn.close()
        -    return documents
    
    
        +def load_documents_distributed(limit: Optional[int] = None) -> List[Document]:
        +    """Compatibility eager loader with a required safety limit."""
        +    if limit is None:
        +        raw = os.environ.get("RAG_DOCUMENT_LIMIT", "").strip()
        +        limit = int(raw) if raw else None
        +    if limit is None or limit < 1:
        +        raise ValueError("set RAG_DOCUMENT_LIMIT or pass limit= to use the eager loader")
        +    return list(iter_documents(limit=limit))
        +
        +
        +def iter_document_chunks(
        +    documents: Iterable[Document], chunk_size: int = 800, chunk_overlap: int = 100
        +) -> Iterator[Document]:
        +    splitter = RecursiveCharacterTextSplitter(
        +        chunk_size=chunk_size,
        +        chunk_overlap=chunk_overlap,
        +        separators=["\n\n", "\n", ".", " ", ""],
        +    )
        +    for document in documents:
        +        yield from splitter.split_documents([document])
        +
        +
         def split_documents_into_chunks(documents: List[Document], chunk_size: int = 800, chunk_overlap: int = 100) -> List[Document]:
        -    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap, separators=["\n\n", "\n", ".", " ", ""])
        -    return text_splitter.split_documents(documents)
        +    return list(iter_document_chunks(documents, chunk_size, chunk_overlap))
    
    ## Activity
    
        file changes: Completed · 1 changes
        Update { move_path: None }: /home/spark/spark_warc/db_inspect.py
        @@ -9,3 +9,3 @@
    
        -TABLES = ("websites", "authors", "pages", "metadata", "content", "ingest_files")
        +TABLES = ("websites", "authors", "pages", "metadata", "content", "ingest_files", "ingest_runs", "ingest_run_files")
         SAMPLE_SIZE = int(os.environ.get("DB_INSPECT_SAMPLES", "5"))
        @@ -41,2 +41,13 @@
                 print(f" {manifest_id}: {done}/{total} files complete, {nbytes:,} bytes")
        +    cur.execute(
        +        """SELECT run_id::text, manifest_id, status, inserted_count,
        +                  target_articles, per_file_target
        +           FROM ingest_runs ORDER BY created_at DESC LIMIT 10"""
        +    )
        +    print("-" * 90)
        +    print("RECENT INGESTION RUNS")
        +    for run_id, manifest, status, inserted, target, per_file in cur.fetchall():
        +        target_label = f"{target:,}" if target else "unlimited"
        +        per_file_label = f"{per_file:,}" if per_file else "unlimited"
        +        print(f" {run_id} {manifest} {status}: {inserted:,}/{target_label}, per-file={per_file_label}")
    
        @@ -51,3 +62,3 @@
                 JOIN content AS c ON c.page_id = p.id
        -        ORDER BY p.id LIMIT %s;
        +        ORDER BY p.id DESC LIMIT %s;
                 """,
    
    ## Activity
    
        $ .venv/bin/python -m py_compile stream_to_db.py utils.py extractors/extractors.py parsers/parsers.py db/db_handler.py langchain.py db_inspect.py; bash -n run_to_db.sh
        ✓ • 0ms
    
    ## Activity
    
        $ .venv/bin/python -m pip show venv-pack pytest langchain-core langchain-text-splitters | sed -n '1,100p'
        WARNING: Package(s) not found: pytest
        Name: venv-pack
        Version: 0.2.0
        Summary: Package virtual environments for redistribution
        Home-page: https://jcrist.github.io/venv-pack/
        Author:
        Author-email:
        License: BSD
        Location: /home/spark/spark_warc/.venv/lib/python3.13/site-packages
        Requires:
        Required-by:
        ---
        Name: langchain-core
        Version: 1.6.3
        Summary: Building applications with LLMs through composability
        Home-page: https://docs.langchain.com/
        Author:
        Author-email:
        License: MIT
        Location: /home/spark/spark_warc/.venv/lib/python3.13/site-packages
        Requires: httpx, jsonpatch, langchain-protocol, langsmith, packaging, pydantic, pyyaml, tenacity, typing-extensions, uuid-utils
        Required-by: langchain-text-splitters
        ---
        Name: langchain-text-splitters
        Version: 1.1.2
        Summary: LangChain text splitting utilities
        Home-page: https://docs.langchain.com/
        Author:
        Author-email:
        License: MIT
        Location: /home/spark/spark_warc/.venv/lib/python3.13/site-packages
        Requires: langchain-core
        Required-by:
        ✓ • 135ms
    
    ## Assistant
    
    The new driver loop now sends bounded work to all three executors concurrently and commits each result as one database transaction. Global and per-file quotas are based on newly inserted rows, so duplicates and language rejects no longer spend the requested count. Resume state is tied to a printed run ID and uses the same environment-variable style as the existing project.
    
    ## Activity
    
        file changes: Completed · 1 changes
    langchain.py
    run_to_db.sh
    db/db_handler.py
    db_inspect.py
    stream_to_db.py
    parsers/parsers.py
    utils.py
    extractors/extractors.py
    requirements.txt
    ✓ • 0ms

## Assistant

Yes—I read the conversation and found where it stopped.

You had approved implementing a plan to:

- Enforce total and per-file quotas using **successfully inserted new articles**.
- Move language detection to workers and process three files concurrently.
- Bound memory usage and make checkpoints/resume reliable.
- Fix extraction issues, improve packaging, and update the README.
- Keep configuration through **environment variables**, not CLI flags.

The previous assistant had made a first implementation pass across ingestion, database, parser, extraction, launcher, and downstream loading. Python and shell syntax checks passed, but **regression tests and live database/YARN validation were still pending**.

**The exact stopping point was the README rewrite:** the log records deleting the old `README.md`, but no replacement was added before your final “continue??” message. The current folder also has no project README.

The work was therefore unfinished. The next step is to verify the existing code against the approved plan, complete missing changes, restore the README, and run the planned tests.

## User

ok continue

## Assistant

I’ll check the current code against the approved plan, finish the missing pieces, and restore the README. Then I’ll test quota handling, resume behavior, and memory bounds before attempting a cluster smoke run.

## Activity

    $ pwd
        ls -la
        rg --files --hidden -g AGENTS.md -g '!lib/**' -g '!.venv/**' -g '!.git/**' /home/spark-master/rag_news_project /home/hadoop/.codex 2>/dev/null
    /home/spark-master/rag_news_project/spark_warc_v2
    total 576
    drwxrwxr-x 9 hadoop hadoop    4096 Sep 30 11:03 .
    drwxr-xr-x 6 hadoop nogroup   4096 Sep 30 10:55 ..
    dr-xr-xr-x 2 hadoop hadoop      40 Sep 30 11:03 .agents
    dr-xr-xr-x 2 hadoop hadoop      40 Sep 30 11:03 .aws
    dr-xr-xr-x 2 hadoop hadoop      40 Sep 30 11:03 .codex
    dr-xr-xr-x 2 hadoop hadoop      40 Sep 30 11:03 .git
    -rw-rw-r-- 1 hadoop hadoop     171 Sep 30 00:16 .gitignore
    -rw-r--r-- 1 nobody nogroup 518837 Sep 30 10:51 codex-session-01a0eedb-9821-7142-833d-480218657bc1.md
    drwxrwxr-x 2 hadoop hadoop    4096 Sep 30 00:12 db
    -rw-rw-r-- 1 hadoop hadoop    2968 Sep 30 00:16 db_inspect.py
    drwxrwxr-x 2 hadoop hadoop    4096 Sep 29 23:31 extractors
    -rw-rw-r-- 1 hadoop hadoop    3391 Sep 30 00:16 langchain.py
    drwxrwxr-x 2 hadoop hadoop    4096 Sep 30 00:12 parsers
    -rw-rw-r-- 1 hadoop hadoop    1158 Sep 29 23:26 requirements.txt
    -rwxrwxr-x 1 hadoop hadoop    6436 Sep 30 00:16 run_to_db.sh
    -rw-rw-r-- 1 hadoop hadoop   20363 Sep 30 00:15 stream_to_db.py
    -rw-rw-r-- 1 hadoop hadoop    3107 Sep 30 00:12 utils.py
    /home/hadoop/.codex/.tmp/plugins/plugins/build-web-apps/skills/supabase-best-practices/AGENTS.md
    /home/hadoop/.codex/.tmp/plugins/plugins/build-web-apps/skills/react-best-practices/AGENTS.md
    ✓ • 474ms

## Activity

    $ cat stream_to_db.py
    """Distributed, bounded-memory CC-NEWS ingestion into PostgreSQL.
    
    Workers download, parse, extract, and classify. The driver is the single
    transaction coordinator and counts only rows PostgreSQL actually inserts.
    """
    
    import gzip
    import hashlib
    import json
    import math
    import os
    import socket
    import sys
    import time
    import urllib.error
    import urllib.request
    from datetime import datetime, timezone
    
    from pyspark.sql import SparkSession
    
    from db.db_handler import (
        acquire_coordinator_lock,
        commit_chunk,
        create_run,
        finish_run,
        init_db,
        load_run,
        load_run_files,
    )
    from extractors.extractors import detect_languages_batch, extract_html_fields
    from parsers.parsers import parse_warc_records_streaming
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
        text = (raw or "15").strip().lower()
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
            "max_html_bytes": _env_int("MAX_HTML_BYTES", 2 * 1024 * 1024, minimum=1024),
            "max_article_bytes": _env_int("MAX_ARTICLE_BYTES", 512 * 1024, minimum=1024),
            "min_word_count": _env_int("MIN_WORD_COUNT", 80, minimum=1),
            "max_retries": _env_int("MAX_RETRIES", 3, minimum=1),
            "db_batch_size": _env_int("DB_BATCH_SIZE", 25, minimum=1),
            "resume_run_id": os.environ.get("RESUME_RUN_ID", "").strip(),
            "no_progress": os.environ.get("NO_PROGRESS", "0") == "1",
            "dry_run": os.environ.get("DRY_RUN", "0") == "1",
        }
        if config["max_files_per_round"] > 3:
            print("WARNING: MAX_FILES_PER_ROUND exceeds the cluster's three executors; using 3.")
            config["max_files_per_round"] = 3
        if config["max_article_bytes"] > config["worker_max_result_bytes"]:
            raise ValueError("MAX_ARTICLE_BYTES cannot exceed WORKER_MAX_RESULT_BYTES")
        return config
    
    
    def get_spark_session():
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
        if isinstance(error, (socket.timeout, TimeoutError, ConnectionError, urllib.error.URLError)):
            return True
        return isinstance(error, urllib.error.HTTPError) and (error.code == 429 or 500 <= error.code < 600)
    
    
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
            ranged = start_offset > 0 and status == 206
            base_offset = start_offset if ranged else 0
            if ranged:
                content_range = response.headers.get("Content-Range", "")
                if not content_range.startswith(f"bytes {start_offset}-"):
                    raise IOError(f"unexpected Content-Range: {content_range!r}")
            etag = response.headers.get("ETag")
            modified = response.headers.get("Last-Modified")
            if task.get("etag") and etag and task["etag"] != etag:
                raise IOError("source ETag changed since the previous chunk")
            if task.get("last_modified") and modified and task["last_modified"] != modified:
                raise IOError("source Last-Modified changed since the previous chunk")
            total_size = _content_total(response, base_offset, ranged)
            records = iter(parse_warc_records_streaming(
                response,
                max_html_bytes=task["max_html_bytes"],
                base_offset=base_offset,
            ))
            try:
                current = next(records)
            except StopIteration:
                return {
                    "chunk_id": task["chunk_id"], "file_url": file_url,
                    "start_offset": start_offset, "next_offset": total_size or start_offset,
                    "candidates": [], "eof": True, "etag": etag,
                    "last_modified": modified, "stats": {"records": 0}, "error": None,
                }
    
            candidates, result_bytes = [], 0
            stats = {"records": 0, "non_html": 0, "oversized_html": 0,
                     "too_short_or_corrupt": 0, "language_rejected": 0,
                     "oversized_article": 0, "accepted_candidates": 0}
            seen = set()
            while current is not None:
                try:
                    following = next(records)
                    next_offset = following["start_offset"]
                    clean_eof = False
                except StopIteration:
                    following = None
                    next_offset = total_size
                    clean_eof = True
                if current["start_offset"] < start_offset:
                    current = following
                    continue
                stats["records"] += 1
                skip = current.get("skip")
                if skip:
                    stats[skip] = stats.get(skip, 0) + 1
                else:
                    try:
                        fields = extract_html_fields(current, task["min_word_count"])
                    except Exception:
                        fields = {}
                    if not fields.get("clean_text") or fields.get("word_count", 0) < task["min_word_count"]:
                        stats["too_short_or_corrupt"] += 1
                    else:
                        language = detect_languages_batch([fields["clean_text"]])[0]
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
                                        "stats": stats, "error": None,
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
                        "stats": stats, "error": None,
                    }
                current = following
        raise IOError("stream ended without a checkpoint result")
    
    
    def process_file_chunk(task):
        """Spark worker entry point with bounded retry and no external writes."""
        last_error = None
        for attempt in range(task["max_retries"]):
            try:
                return _process_file_once(task)
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
    
    
    def run_streaming_pipeline():
        config = load_config()
        if config["dry_run"]:
            _print_config(config)
            return 0
    
        init_db()
        lock_conn = acquire_coordinator_lock(config["manifest_id"])
        spark = None
        try:
            if config["resume_run_id"]:
                run = load_run(config["resume_run_id"])
                if run["manifest_id"] != config["manifest_id"]:
                    raise ValueError(
                        f"RESUME_RUN_ID belongs to {run['manifest_id']}; set YEAR/MONTH to match"
                    )
                # Filtering semantics are fixed for a run; resource limits may be tuned on resume.
                stored = run.get("config") or {}
                for key in ("min_word_count",):
                    if key in stored:
                        config[key] = stored[key]
                run_id = run["run_id"]
                print(f"Resuming run {run_id}: {run['inserted_count']}/{run['target_articles'] or 'unlimited'} committed")
            else:
                urls = fetch_manifest(config)
                if not urls:
                    print("No WARC files were selected.")
                    return 2
                persisted = {"min_word_count": config["min_word_count"], "year": config["year"], "month": config["month"]}
                run_id = create_run(config["manifest_id"], urls, config["target_articles"], config["per_file_target"], persisted)
                run = load_run(run_id)
                print(f"Created ingestion run {run_id}")
            print(f"Resume command: RESUME_RUN_ID={run_id} YEAR={config['year']} MONTH={config['month']} ./run_to_db.sh")
    
            spark = get_spark_session()
            sc = spark.sparkContext
            sc.setLogLevel("WARN")
            wave = 0
            totals = {"candidates": 0, "inserted": 0, "failed_files": 0}
            while True:
                run = load_run(run_id)
                files = load_run_files(run_id)
                if run["target_articles"] and run["inserted_count"] >= run["target_articles"]:
                    finish_run(run_id, "complete")
                    print(f"Target reached exactly: {run['inserted_count']:,} new articles committed.")
                    return 0
                tasks = _allocate_tasks(config, run, files, wave)
                if not tasks:
                    status = "complete" if run["target_articles"] == 0 else "shortfall"
                    finish_run(run_id, status)
                    short = max(0, run["target_articles"] - run["inserted_count"])
                    print(f"Sources exhausted: committed {run['inserted_count']:,}; shortfall {short:,}.")
                    return 0 if status == "complete" else 2
                wave += 1
                results = sc.parallelize(tasks, len(tasks)).map(process_file_chunk).collect()
                made_progress = False
                wave_inserted = 0
                for result in results:
                    if result.get("error"):
                        print(f"FAILED {result['file_url']}: {result['error']}")
                        totals["failed_files"] += 1
                    inserted = None
                    for attempt in range(config["max_retries"]):
                        try:
                            inserted = commit_chunk(run_id, result)
                            break
                        except Exception as error:
                            if attempt + 1 == config["max_retries"]:
                                finish_run(run_id, "failed")
                                raise RuntimeError(f"database commit failed; run {run_id} is resumable") from error
                            _sleep_backoff(attempt)
                    totals["candidates"] += len(result["candidates"])
                    totals["inserted"] += inserted
                    wave_inserted += inserted
                    made_progress |= result["next_offset"] > result["start_offset"] or inserted > 0
                run = load_run(run_id)
                print(
                    f"Wave {wave}: committed {run['inserted_count']:,}/"
                    f"{run['target_articles'] or 'unlimited'}; "
                    f"wave candidates={sum(len(r['candidates']) for r in results):,}, "
                    f"new={wave_inserted:,}"
                )
                if not made_progress:
                    finish_run(run_id, "failed")
                    raise RuntimeError(f"no cursor or insert progress in wave {wave}; run {run_id} stopped safely")
        finally:
            if spark is not None:
                spark.stop()
            lock_conn.close()
    
    
    if __name__ == "__main__":
        try:
            sys.exit(run_streaming_pipeline())
        except Exception as error:
            stamp = datetime.now(timezone.utc).isoformat()
            print(f"[{stamp}] FATAL {type(error).__name__}: {error}", file=sys.stderr)
            sys.exit(1)
    ✓ • 0ms

## Activity

    $ cat run_to_db.sh
        cat requirements.txt
        cat utils.py
        cat extractors/extractors.py
        cat langchain.py
    #!/usr/bin/env bash
    set -euo pipefail
    
    PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
    cd "$PROJECT_ROOT"
    
    TMPDIR="$(mktemp -d)"
    ZIP="$TMPDIR/project_code.zip"
    VENV_ARCHIVE="$PROJECT_ROOT/pyspark_venv.tar.gz"
    VENV_FINGERPRINT_FILE="$PROJECT_ROOT/.venv-pack.fingerprint"
    
    trap 'rm -rf "$TMPDIR"' EXIT
    
    # Activate local driver environment
    source "$PROJECT_ROOT/.venv/bin/activate"
    
    # Rebuild whenever the declared environment changes.
    VENV_FINGERPRINT="$(sha256sum requirements.txt pyvenv.cfg .venv/pyvenv.cfg | sha256sum | awk '{print $1}')"
    PACKED_FINGERPRINT="$(test -f "$VENV_FINGERPRINT_FILE" && tr -d '\n' < "$VENV_FINGERPRINT_FILE" || true)"
    if [ ! -f "$VENV_ARCHIVE" ] || [ "$VENV_FINGERPRINT" != "$PACKED_FINGERPRINT" ]; then
        echo "Building PySpark worker environment..."
        venv-pack -f -o "$VENV_ARCHIVE"
        echo "$VENV_FINGERPRINT" > "$VENV_FINGERPRINT_FILE"
    fi
    
    # Package current project code on every run
    echo "Packaging project code..."
    zip -qr "$ZIP" \
        extractors \
        parsers \
        db \
        utils.py
    
    # Driver uses the local venv on spark-master
    export PYSPARK_DRIVER_PYTHON="$PROJECT_ROOT/.venv/bin/python"
    
    # Executors use the environment distributed by YARN
    export PYSPARK_PYTHON="./environment/bin/python"
    
    # Tunables (override per run, e.g. NUM_FILES=2 ./run_to_db.sh)
    #   NUM_FILES: files to process from START_FILE_OFFSET; unset/empty/all/0 = to end of manifest
    #   START_FILE_OFFSET: skip the first N manifest entries (file-range targeting); 0 = from start
    #   MAX_ACCEPTED_PER_FILE: maximum newly committed articles from each file; 0 = unlimited
    #   MAX_FILES_PER_ROUND: concurrent files; capped at this three-executor cluster's size
    #   MIN_WORD_COUNT: article = this many words+ after extraction (trafilatura acceptance + yield gate)
    #   MAX_ACCEPTED_ARTICLES: exact new-commit target; 0 = process selected files to EOF
    #   USE_HDFS_CACHE: 0 disables both shared HDFS artifacts (worker venv + Spark jars)
    export NUM_FILES="${NUM_FILES:-15}"
    export START_FILE_OFFSET="${START_FILE_OFFSET:-0}"
    export MAX_ACCEPTED_ARTICLES="${MAX_ACCEPTED_ARTICLES:-0}"
    export MAX_ACCEPTED_PER_FILE="${MAX_ACCEPTED_PER_FILE:-0}"
    export MAX_FILES_PER_ROUND="${MAX_FILES_PER_ROUND:-3}"
    export MIN_WORD_COUNT="${MIN_WORD_COUNT:-80}"
    export WORKER_MAX_CANDIDATES="${WORKER_MAX_CANDIDATES:-100}"
    export WORKER_MAX_RESULT_BYTES="${WORKER_MAX_RESULT_BYTES:-4194304}"
    export WORKER_MAX_INPUT_BYTES="${WORKER_MAX_INPUT_BYTES:-33554432}"
    export WORKER_MAX_SECONDS="${WORKER_MAX_SECONDS:-120}"
    export MAX_HTML_BYTES="${MAX_HTML_BYTES:-2097152}"
    export MAX_ARTICLE_BYTES="${MAX_ARTICLE_BYTES:-524288}"
    export SPARK_EXECUTOR_MEMORY="${SPARK_EXECUTOR_MEMORY:-512m}"
    export SPARK_EXECUTOR_MEMORY_OVERHEAD="${SPARK_EXECUTOR_MEMORY_OVERHEAD:-512m}"
    export SPARK_DRIVER_MEMORY="${SPARK_DRIVER_MEMORY:-512m}"
    
    # --- Shared venv on HDFS (upload once, reuse across runs) ---
    # Per-run --archives of the worker venv re-uploads + re-localizes on every
    # submit and fills NM disks. Instead we store a content-addressed copy on
    # HDFS and reference it; rebuilds (new md5) upload exactly once, old copies
    # are pruned.
    HDFS_APPS_DIR="${HDFS_APPS_DIR:-/user/spark-master/apps/spark}"
    VENV_MD5="$(md5sum "$VENV_ARCHIVE" | awk '{print $1}')"
    HDFS_VENV="$HDFS_APPS_DIR/pyspark_venv-${VENV_MD5}.tar.gz"
    ARCHIVES_SPEC="$VENV_ARCHIVE#environment"   # fallback: local per-run upload
    
    hdfs_ok() { hdfs dfs -test -e / >/dev/null 2>&1; }
    
    upload_venv_hdfs() {
        # Best-effort: any failure returns non-zero so the caller falls back
        # to a local per-run upload instead of aborting the submit (set -e).
        hdfs dfs -mkdir -p "$HDFS_APPS_DIR" 2>/dev/null || return 1
        hdfs dfs -put -f "$VENV_ARCHIVE" "$HDFS_VENV" 2>/dev/null || return 1
        return 0
    }
    
    if [ "${USE_HDFS_CACHE:-1}" = "1" ] && hdfs_ok; then
        if hdfs dfs -test -e "$HDFS_VENV" 2>/dev/null; then
            echo "Reusing HDFS venv $HDFS_VENV (no upload needed)."
            ARCHIVES_SPEC="hdfs://$HDFS_VENV#environment"
        elif upload_venv_hdfs; then
            echo "Uploaded venv to HDFS ($HDFS_VENV, one-time for this build)."
            ARCHIVES_SPEC="hdfs://$HDFS_VENV#environment"
        else
            echo "WARNING: HDFS venv upload failed — falling back to per-run venv upload."
        fi
    else
        echo "WARNING: HDFS unreachable or USE_HDFS_CACHE=0 — falling back to per-run venv upload."
    fi
    
    # --- Shared Spark jars archive (default on, verified 2026-09-28) ---
    # Avoids the per-run "falling back to uploading libraries under SPARK_HOME".
    # Disable per-run with USE_HDFS_CACHE=0.
    EXTRA_CONF=()
    if [ "${USE_HDFS_CACHE:-1}" = "1" ] && hdfs_ok; then
        SPARK_JARS_ZIP="$PROJECT_ROOT/spark-libs.zip"
        SPARK_ARCHIVE_MD5="$(md5sum "$SPARK_JARS_ZIP" 2>/dev/null | awk '{print $1}' || true)"
        if [ ! -f "$SPARK_JARS_ZIP" ]; then
            echo "Building Spark jars archive (one-time)..."
            (cd "${SPARK_HOME:?SPARK_HOME not set}/jars" && zip -qr "$SPARK_JARS_ZIP" .)
            SPARK_ARCHIVE_MD5="$(md5sum "$SPARK_JARS_ZIP" | awk '{print $1}')"
        fi
        HDFS_SPARK_ARCHIVE="$HDFS_APPS_DIR/spark-libs-${SPARK_ARCHIVE_MD5}.zip"
        if hdfs dfs -test -e "$HDFS_SPARK_ARCHIVE" 2>/dev/null; then
            echo "Reusing HDFS Spark archive $HDFS_SPARK_ARCHIVE."
            EXTRA_CONF+=(--conf "spark.yarn.archive=hdfs://$HDFS_SPARK_ARCHIVE")
        elif hdfs dfs -mkdir -p "$HDFS_APPS_DIR" 2>/dev/null \
            && hdfs dfs -put -f "$SPARK_JARS_ZIP" "$HDFS_SPARK_ARCHIVE" 2>/dev/null; then
            echo "Uploaded Spark jars archive to HDFS (one-time)."
            EXTRA_CONF+=(--conf "spark.yarn.archive=hdfs://$HDFS_SPARK_ARCHIVE")
        else
            echo "WARNING: Spark archive upload failed — continuing without spark.yarn.archive."
        fi
    fi
    
    echo "Submitting stream_to_db job to YARN (NUM_FILES=$NUM_FILES, MAX_ACCEPTED_PER_FILE=$MAX_ACCEPTED_PER_FILE, MAX_FILES_PER_ROUND=$MAX_FILES_PER_ROUND, MAX_ACCEPTED_ARTICLES=$MAX_ACCEPTED_ARTICLES)..."
    
    spark-submit \
        --master yarn \
        --deploy-mode client \
        --driver-memory "$SPARK_DRIVER_MEMORY" \
        --executor-memory "$SPARK_EXECUTOR_MEMORY" \
        --conf "spark.executor.memoryOverhead=$SPARK_EXECUTOR_MEMORY_OVERHEAD" \
        --conf "spark.executor.cores=1" \
        --conf "spark.executor.instances=3" \
        --conf "spark.pyspark.driver.python=$PROJECT_ROOT/.venv/bin/python" \
        --conf "spark.pyspark.python=./environment/bin/python" \
        "${EXTRA_CONF[@]}" \
        --archives "$ARCHIVES_SPEC" \
        --py-files "$ZIP" \
        stream_to_db.py
    annotated-doc==0.0.5
    annotated-types==0.8.0
    anyio==4.15.1
    arabic-reshaper==3.0.1
    brotli==1.2.0
    certifi==2026.7.22
    cffi>=1.17.1
    charset-normalizer==3.5.1
    click==8.5.0
    colorama==0.4.4
    exceptiongroup==1.3.1
    FastWARC==1.0.9
    filelock==4.0.1
    fsspec==2026.9.0
    h11==0.16.0
    jinja2==3.1.6
    markupsafe==3.0.3
    httpcore==1.0.9
    httpcore2==2.13.0
    httpx==0.28.1
    httpx2==2.13.0
    idna==3.20
    jsonpatch==1.33
    jsonpointer==3.1.1
    langchain-core==1.6.3
    langchain-protocol==0.0.19
    langchain-text-splitters==1.1.2
    langsmith==0.13.0
    lingua-language-detector==2.2.0
    markdown-it-py==4.2.0
    mdurl==0.1.2
    numpy==2.2.6
    orjson==3.12.0
    packaging==26.3
    psutil==5.9.0
    psycopg2-binary==2.9.13
    py4j==0.10.9.9
    pydantic==2.13.5
    pydantic_core==2.46.5
    Pygments==2.21.0
    PyJWT==2.3.0
    python-bidi==0.6.11
    python-dateutil
    PyYAML>=6.0.2
    regex==2026.9.10
    requests==2.34.2
    requests-toolbelt==1.0.0
    rich==15.0.0
    selectolax==0.4.12
    shellingham==1.5.4
    sniffio==1.3.1
    tenacity==9.1.4
    tomli==2.4.1
    trafilatura==2.2.0
    tqdm==4.70.1
    truststore==0.10.4
    typer==0.27.2
    typing_extensions==4.16.0
    typing-inspection==0.4.4
    urllib3==1.26.5
    uuid_utils==0.17.1
    warcio==1.8.1
    websockets==16.1.1
    xxhash==4.0.1
    zstandard==0.25.0
    import re
    from typing import Optional, Tuple
    from charset_normalizer import from_bytes
    
    ARABIC_CHAR_PATTERN = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]')
    # Letters that never occur in genuine Arabic but are routine in neighbours
    # sharing the script. Lingua lacks Kurdish, so Sorani markers are the
    # backstop there; fa/ur markers catch Persian/Urdu that still scores 'ar'.
    NON_ARABIC_MARKERS = re.compile(
        '['
        '\u067E\u0686\u0698\u06AF\u06A9\u06CC'  # fa: pe che jeem gaf kaf yeh
        '\u0679\u0688\u0691\u06BA\u06BE\u06D2'  # ur: tte ddahal rre noon-ghunna he-do-chashmee bare-ye
        '\u06D5\u0695\u06B5\u06C6\u06CE'        # ku (Sorani): ae rra lla o u
        ']'
    )
    
    def is_target_language(lang_code: str) -> bool:
        if not lang_code:
            return False
        lang = str(lang_code).lower().strip()
        return lang in {"ar", "en", "fr"}
    
    def is_clean_encoding(text: str) -> bool:
        if not text or "\ufffd" in text or "\x00" in text:
            return False
        # Ordinary accented Latin letters are valid French. Flag characteristic
        # UTF-8-as-Latin-1 byte sequences instead of treating every accent as bad.
        mojibake = re.findall(r"(?:Ã[\x80-\xBF]|Â[\x80-\xBF]|â[\x80-\xBF]{2})", text)
        if len(mojibake) >= 3 and sum(map(len, mojibake)) / len(text) > 0.01:
            return False
        controls = sum(1 for c in text if ord(c) < 32 and c not in "\n\r\t\f")
        if controls / len(text) > 0.001:
            return False
        return True
    
    def is_valid_arabic_text(text: str) -> bool:
        if not text or len(text) < 20:
            return False
        sample = text[:500]
        arabic_chars = len(ARABIC_CHAR_PATTERN.findall(sample))
        alpha_chars = sum(1 for c in sample if c.isalpha())
        if alpha_chars == 0:
            return False
        if (arabic_chars / alpha_chars) < 0.40:
            return False
        # Arabic-script neighbours (fa/ur/ku): a handful of distinctive letters
        # disqualifies, genuine Arabic carries none of them.
        markers = len(NON_ARABIC_MARKERS.findall(sample))
        if markers >= 2 and (markers / max(arabic_chars, 1)) > 0.02:
            return False
        return True
    
    def decode_and_validate(raw_bytes: bytes) -> Tuple[Optional[str], str]:
        if not raw_bytes:
            return None, "empty_bytes"
        decoded_text = None
        try:
            decoded_text = raw_bytes.decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            pass
        if not decoded_text:
            try:
                results = from_bytes(raw_bytes)
                best_match = results.best()
                if best_match and best_match.encoding:
                    if not (best_match.encoding.lower() in ["iso-8859-1", "latin-1"] and best_match.coherence < 0.8):
                        decoded_text = str(best_match)
            except Exception:
                pass
        if not decoded_text:
            try:
                decoded_text = raw_bytes.decode("windows-1256", errors="strict")
            except UnicodeDecodeError:
                pass
        if not decoded_text:
            return None, "decode_failed"
        if not is_clean_encoding(decoded_text):
            return None, "encoding_corrupted"
        return decoded_text, "success"
    import os
    import re
    import json
    from typing import Dict, Any, List
    from selectolax.parser import HTMLParser
    from utils import decode_and_validate, is_valid_arabic_text
    
    ARABIC_PATTERN = re.compile(r'[\u0600-\u06FF]')
    LATIN_PATTERN = re.compile(r'[a-zA-Z]')
    CYRILLIC_PATTERN = re.compile(r'[\u0400-\u04FF]')
    # CJK scripts: kana is Japanese-specific, hangul Korean-specific, han shared
    # (mostly Chinese in news, also used in Japanese).
    KANA_PATTERN = re.compile(r'[\u3040-\u30FF]')
    HANGUL_PATTERN = re.compile(r'[\uAC00-\uD7AF\u1100-\u11FF]')
    CJK_PATTERN = re.compile(r'[\u3040-\u30FF\u4E00-\u9FFF\uAC00-\uD7AF]')
    
    USE_TRAFILATURA = os.environ.get("USE_TRAFILATURA", "1") == "1"
    TARGET_LANGUAGES = {"ar", "en", "fr"}
    
    UNWANTED_TAGS = ["script", "style", "noscript", "header", "footer", "svg", "nav"]
    
    # Language ID via Lingua (n-gram models, no torch). Detector is built lazily
    # once in each long-lived Spark Python worker.
    LINGUA_LANGUAGES = (
        "ARABIC", "ENGLISH", "FRENCH", "SPANISH", "GERMAN", "ITALIAN",
        "PORTUGUESE", "CATALAN", "ROMANIAN", "RUSSIAN", "TURKISH",
        "VIETNAMESE", "JAPANESE", "KOREAN", "CHINESE", "DUTCH", "TAMIL",
        "UKRAINIAN", "PERSIAN", "URDU",
    )
    LINGUA_MIN_CONFIDENCE = float(os.environ.get("LINGUA_MIN_CONFIDENCE", "0.5"))
    _lingua_detector = None
    
    
    def get_lingua_detector():
        global _lingua_detector
        if _lingua_detector is None:
            from lingua import Language, LanguageDetectorBuilder
            _lingua_detector = (
                LanguageDetectorBuilder.from_languages(
                    *[getattr(Language, name) for name in LINGUA_LANGUAGES]
                )
                .with_preloaded_language_models()
                .build()
            )
        return _lingua_detector
    
    
    _LINGUA_TO_CODE = {
        "ARABIC": "ar",
        "ENGLISH": "en",
        "FRENCH": "fr",
        "RUSSIAN": "ru",
        "JAPANESE": "ja",
        "KOREAN": "ko",
        "CHINESE": "zh",
        "PERSIAN": "fa",
        "URDU": "ur",
    }
    
    # Full Latin block (ASCII patterns miss French accents). Used only by the
    # script gate below; existing patterns stay untouched.
    _LATIN_FULL_PATTERN = re.compile(r"[a-zA-ZÀ-ɏḀ-ỿ]")
    _SUPPORTED_SCRIPTS = re.compile(
        r"[a-zA-ZÀ-ɏḀ-ỿ\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\u0400-\u04FF"
        r"\u3040-\u30FF\u4E00-\u9FFF\uAC00-\uD7AF\u1100-\u11FF]"
    )
    
    
    def _unsupported_script_share(text: str) -> float:
        """Share of alpha chars outside Latin/Arabic/Cyrillic/CJK.
    
        Catches bodies in unloaded scripts (Kannada, Hindi, Bengali, ...) that
        boilerplate chrome smuggled past lingua's head sample: the chrome votes
        Latin, but a fifth or more of the full text is none of the above.
        """
        if not text:
            return 1.0
        alpha_count = 0
        other_count = 0
        for char in text:
            if not char.isalpha():
                continue
            alpha_count += 1
            if not _SUPPORTED_SCRIPTS.match(char):
                other_count += 1
        if not alpha_count:
            return 1.0
        return other_count / alpha_count
    
    
    def _language_sample(text: str) -> str:
        """Sample the beginning, middle, and end without duplicating short text."""
        if len(text) <= 2000:
            return text
        middle = len(text) // 2
        return text[:800] + " " + text[middle - 300:middle + 300] + " " + text[-600:]
    
    
    def detect_languages_batch(texts: List[str]) -> List[str]:
        if not texts:
            return []
        detector = get_lingua_detector()
        results = []
        for text in texts:
            if not text or len(text) < 20:
                results.append("unknown")
                continue
            sample = _language_sample(text)
            has_script = (
                ARABIC_PATTERN.search(sample)
                or LATIN_PATTERN.search(sample)
                or CYRILLIC_PATTERN.search(sample)
                or CJK_PATTERN.search(sample)
            )
            if not has_script:
                results.append("ignored")
                continue
            try:
                confidence = detector.compute_language_confidence_values(sample)
            except Exception:
                results.append("other")
                continue
            if not confidence or confidence[0].value <= 0.0:
                results.append("ignored")
                continue
            top = confidence[0]
            if top.value < LINGUA_MIN_CONFIDENCE:
                results.append("other")
                continue
            code = _LINGUA_TO_CODE.get(top.language.name, "other")
            if code in ("en", "fr", "ar") and _unsupported_script_share(text) > 0.10:
                results.append("other")
                continue
            if code == "ar" and not is_valid_arabic_text(text):
                results.append("corrupted")
                continue
            results.append(code)
        return results
    
    def _jsonld_objects(value):
        if isinstance(value, list):
            for item in value:
                yield from _jsonld_objects(item)
        elif isinstance(value, dict):
            yield value
            if "@graph" in value:
                yield from _jsonld_objects(value["@graph"])
    
    
    def _jsonld_from_tree(tree):
        for script_node in tree.css("script[type='application/ld+json']"):
            raw = script_node.text(strip=True)
            if not raw:
                continue
            try:
                yield from _jsonld_objects(json.loads(raw))
            except (json.JSONDecodeError, ValueError, TypeError):
                continue
    
    
    def extract_publication_date(tree: HTMLParser) -> str:
        meta_selectors = [
            ("meta[property='article:published_time']", "content"),
            ("meta[name='pubdate']", "content"),
            ("meta[name='publishdate']", "content"),
            ("meta[name='date']", "content"),
            ("meta[name='DC.date.issued']", "content"),
            ("meta[name='parsely-pub-date']", "content")
        ]
        for selector, attr in meta_selectors:
            node = tree.css_first(selector)
            if node and node.attributes.get(attr):
                date_val = node.attributes.get(attr).strip()
                if date_val:
                    return date_val
        for item in _jsonld_from_tree(tree):
            date_val = item.get("datePublished") or item.get("dateCreated")
            if date_val:
                return str(date_val).strip()
        time_node = tree.css_first("time")
        if time_node:
            datetime_val = time_node.attributes.get("datetime")
            if datetime_val:
                return datetime_val.strip()
            text_val = time_node.text(strip=True)
            if text_val:
                return text_val
        return "N/A"
    
    def extract_date_from_text_fallback(tree: HTMLParser) -> str:
        body_text = tree.body.text() if tree.body else tree.text()
        date_match = re.search(r'\b(19\d\d|20\d\d)[-/.](0?[1-9]|1[0-2])[-/.](0?[1-9]|[12]\d|3[01])\b', body_text)
        return date_match.group(0) if date_match else "N/A"
    
    def extract_author(tree: HTMLParser) -> str:
        author_selectors = [
            ("meta[name='author']", "content"),
            ("meta[property='article:author']", "content"),
            ("meta[name='parsely-author']", "content"),
            ("meta[name='dc.creator']", "content"),
            ("meta[name='author_name']", "content")
        ]
        for selector, attr in author_selectors:
            node = tree.css_first(selector)
            if node and node.attributes.get(attr):
                val = node.attributes.get(attr).strip()
                if val:
                    return val
        for item in _jsonld_from_tree(tree):
            if "author" not in item:
                continue
            author_data = item["author"]
            if isinstance(author_data, dict) and author_data.get("name"):
                return str(author_data["name"]).strip()
            if isinstance(author_data, list) and author_data:
                first = author_data[0]
                if isinstance(first, dict) and first.get("name"):
                    return str(first["name"]).strip()
                if isinstance(first, str):
                    return first.strip()
            if isinstance(author_data, str):
                return author_data.strip()
        return "N/A"
    
    def _trafilatura_text(html_str: str) -> str:
        """Main-content extraction via trafilatura. Returns '' on failure/None."""
        try:
            from trafilatura import extract as _trafi_extract
            text = _trafi_extract(html_str, include_comments=False, include_tables=False)
        except Exception:
            return ""
        if not text:
            return ""
        return " ".join(text.split())
    
    
    def extract_html_fields(record: Dict[str, Any], min_words: int = 80) -> Dict[str, Any]:
        html_str, status = decode_and_validate(record["raw_bytes"])
        if status != "success" or not html_str:
            return {"language": "corrupted", "word_count": 0, "clean_text": "", "extraction": "corrupted"}
        tree = HTMLParser(html_str)
        title_node = tree.css_first("title")
        title = title_node.text(strip=True) if title_node else "N/A"
        # Metadata scripts must be read before unwanted elements are removed.
        pub_date = extract_publication_date(tree)
        author = extract_author(tree)
        trafi_text = _trafilatura_text(html_str) if USE_TRAFILATURA else ""
        for tag in tree.css(", ".join(UNWANTED_TAGS)):
            tag.decompose()
        if trafi_text and len(trafi_text.split()) >= min_words:
            clean_text = trafi_text
            extraction = "trafilatura"
        else:
            body = tree.body
            raw_text = body.text(separator=' ', strip=True) if body else tree.text(separator=' ', strip=True)
            clean_text = " ".join(raw_text.split())
            extraction = "selectolax"
        clean_text = clean_text.replace("\x00", "")
        word_cnt = len(clean_text.split())
        if word_cnt < min_words:
            return {"language": "too_short", "word_count": word_cnt, "clean_text": "", "extraction": extraction}
        if pub_date == "N/A":
            pub_date = extract_date_from_text_fallback(tree)
        return {
            "title": title,
            "author": author,
            "url": record["url"],
            "warc_date": record["warc_date"],
            "published_date": pub_date,
            "clean_text": clean_text,
            "word_count": word_cnt,
            "char_count": len(clean_text),
            "html_size_bytes": len(record["raw_bytes"]),
            "links_count": len(tree.css("a")),
            "headings_sample": [node.text(strip=True) for node in tree.css("h1, h2, h3")][:3],
            "extraction": extraction,
        }
    import sys
    import os
    from typing import Iterable, Iterator, List, Optional
    from langchain_core.documents import Document
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if BASE_DIR not in sys.path:
        sys.path.insert(0, BASE_DIR)
    
    from db.db_handler import get_connection
    
    FETCH_BATCH_SIZE = int(os.environ.get("RAG_FETCH_BATCH_SIZE", "1000"))
    
    _JOIN_QUERY = """
    SELECT p.id AS doc_id, c.cleaned_text AS text, p.url AS url,
           m.title AS title, w.domain AS source_domain, a.name AS author,
           m.language AS lang, m.arabic_dialect AS arabic_dialect,
           m.published_date AS pub_date, p.warc_record_id AS warc_record_id
    FROM pages AS p
    LEFT JOIN websites AS w ON w.id = p.website_id
    LEFT JOIN authors AS a ON a.id = p.author_id
    LEFT JOIN metadata AS m ON m.page_id = p.id
    LEFT JOIN content AS c ON c.page_id = p.id
    WHERE c.cleaned_text IS NOT NULL AND length(c.cleaned_text) > 0
    ORDER BY p.id;
    """
    
    
    def _to_document(row) -> Document:
        (doc_id, text, url, title, source_domain, author, lang,
         arabic_dialect, pub_date, warc_record_id) = row
        return Document(
            page_content=text,
            metadata={
                "doc_id": doc_id,
                "source": url,
                "title": title or "N/A",
                "publisher": source_domain or "Unknown",
                "author": author or source_domain or "Unknown",
                "domain": source_domain or "",
                "language": lang or "",
                "arabic_dialect": arabic_dialect or "N/A",
                "published_date": pub_date or "N/A",
                "warc_record_id": warc_record_id or "",
            },
        )
    
    
    def iter_documents(limit: Optional[int] = None) -> Iterator[Document]:
        """Stream Documents from a server-side cursor without corpus accumulation."""
        conn = get_connection()
        try:
            cur = conn.cursor(name="rag_loader")
            try:
                cur.itersize = FETCH_BATCH_SIZE
                query = _JOIN_QUERY
                params = ()
                if limit is not None:
                    query = _JOIN_QUERY.rstrip().rstrip(";") + " LIMIT %s;"
                    params = (limit,)
                cur.execute(query, params)
                for row in cur:
                    yield _to_document(row)
            finally:
                cur.close()
        finally:
            conn.close()
    
    
    def load_documents_distributed(limit: Optional[int] = None) -> List[Document]:
        """Compatibility eager loader with a required safety limit."""
        if limit is None:
            raw = os.environ.get("RAG_DOCUMENT_LIMIT", "").strip()
            limit = int(raw) if raw else None
        if limit is None or limit < 1:
            raise ValueError("set RAG_DOCUMENT_LIMIT or pass limit= to use the eager loader")
        return list(iter_documents(limit=limit))
    
    
    def iter_document_chunks(
        documents: Iterable[Document], chunk_size: int = 800, chunk_overlap: int = 100
    ) -> Iterator[Document]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""],
        )
        for document in documents:
            yield from splitter.split_documents([document])
    
    
    def split_documents_into_chunks(documents: List[Document], chunk_size: int = 800, chunk_overlap: int = 100) -> List[Document]:
        return list(iter_document_chunks(documents, chunk_size, chunk_overlap))
    ✓ • 0ms

## Activity

    $ cat db/db_handler.py
        cat parsers/parsers.py
    """PostgreSQL schema and transactional ingestion helpers."""
    
    import hashlib
    import json
    import os
    import uuid
    from contextlib import contextmanager
    from urllib.parse import urlparse
    
    import psycopg2
    from psycopg2.extras import execute_values
    
    
    def _db_config():
        """Use libpq-compatible environment settings, with legacy defaults."""
        return {
            "dbname": os.environ.get("PGDATABASE", "warcdb"),
            "user": os.environ.get("PGUSER", "warc_user"),
            "password": os.environ.get("PGPASSWORD", "password"),
            "host": os.environ.get("PGHOST", "localhost"),
            "port": os.environ.get("PGPORT", "5432"),
            "connect_timeout": int(os.environ.get("PGCONNECT_TIMEOUT", "10")),
        }
    
    
    DB_CONFIG = _db_config()
    
    
    def get_connection():
        return psycopg2.connect(**_db_config())
    
    
    @contextmanager
    def _cursor(conn):
        cur = conn.cursor()
        try:
            yield cur
        finally:
            cur.close()
    
    
    def init_db():
        """Apply additive, backwards-compatible schema migrations."""
        ddl = """
        CREATE TABLE IF NOT EXISTS websites (
            id SERIAL PRIMARY KEY, domain TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS authors (
            id SERIAL PRIMARY KEY, name TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS pages (
            id SERIAL PRIMARY KEY,
            website_id INT REFERENCES websites(id) ON DELETE CASCADE,
            author_id INT REFERENCES authors(id) ON DELETE SET NULL,
            warc_record_id TEXT UNIQUE, url TEXT NOT NULL,
            source_file_url TEXT, warc_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS metadata (
            page_id INT PRIMARY KEY REFERENCES pages(id) ON DELETE CASCADE,
            title TEXT, published_date TEXT, language TEXT, arabic_dialect TEXT,
            word_count INT, char_count INT, links_count INT, headings JSONB,
            extraction_method TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS content (
            page_id INT PRIMARY KEY REFERENCES pages(id) ON DELETE CASCADE,
            cleaned_text TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS ingest_files (
            file_url TEXT PRIMARY KEY, manifest_id TEXT NOT NULL,
            bytes_done BIGINT NOT NULL DEFAULT 0,
            articles_done INT NOT NULL DEFAULT 0,
            complete BOOLEAN NOT NULL DEFAULT FALSE,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS ingest_runs (
            run_id UUID PRIMARY KEY, manifest_id TEXT NOT NULL,
            target_articles BIGINT NOT NULL, per_file_target BIGINT NOT NULL,
            inserted_count BIGINT NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'running',
            config JSONB NOT NULL DEFAULT '{}'::jsonb,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CHECK (target_articles >= 0), CHECK (per_file_target >= 0));
        CREATE TABLE IF NOT EXISTS ingest_run_files (
            run_id UUID NOT NULL REFERENCES ingest_runs(run_id) ON DELETE CASCADE,
            ordinal INT NOT NULL, file_url TEXT NOT NULL,
            next_offset BIGINT NOT NULL DEFAULT 0,
            inserted_count BIGINT NOT NULL DEFAULT 0,
            eof BOOLEAN NOT NULL DEFAULT FALSE,
            status TEXT NOT NULL DEFAULT 'pending',
            etag TEXT, last_modified TEXT, last_error TEXT,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (run_id, file_url), UNIQUE (run_id, ordinal));
        CREATE TABLE IF NOT EXISTS ingest_chunks (
            chunk_id TEXT PRIMARY KEY,
            run_id UUID NOT NULL REFERENCES ingest_runs(run_id) ON DELETE CASCADE,
            file_url TEXT NOT NULL, start_offset BIGINT NOT NULL,
            next_offset BIGINT NOT NULL, candidate_count INT NOT NULL,
            inserted_count INT NOT NULL, eof BOOLEAN NOT NULL,
            stats JSONB NOT NULL DEFAULT '{}'::jsonb,
            committed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE INDEX IF NOT EXISTS idx_ingest_files_manifest ON ingest_files (manifest_id);
        CREATE INDEX IF NOT EXISTS idx_ingest_run_files_sched
            ON ingest_run_files (run_id, status, ordinal);
        ALTER TABLE pages ADD COLUMN IF NOT EXISTS author_id INT REFERENCES authors(id) ON DELETE SET NULL;
        ALTER TABLE pages ADD COLUMN IF NOT EXISTS source_file_url TEXT;
        ALTER TABLE pages ADD COLUMN IF NOT EXISTS warc_date TEXT;
        ALTER TABLE metadata ADD COLUMN IF NOT EXISTS arabic_dialect TEXT;
        ALTER TABLE metadata ADD COLUMN IF NOT EXISTS extraction_method TEXT;
        ALTER TABLE websites ALTER COLUMN domain TYPE TEXT;
        ALTER TABLE authors ALTER COLUMN name TYPE TEXT;
        ALTER TABLE pages ALTER COLUMN warc_record_id TYPE TEXT;
        ALTER TABLE metadata ALTER COLUMN published_date TYPE TEXT;
        ALTER TABLE metadata ALTER COLUMN language TYPE TEXT;
        ALTER TABLE metadata ALTER COLUMN arabic_dialect TYPE TEXT;
        """
        conn = get_connection()
        try:
            with _cursor(conn) as cur:
                cur.execute(ddl)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    
    def extract_domain(url):
        try:
            host = (urlparse(url).hostname or "").lower().rstrip(".")
            if host.startswith("www."):
                host = host[4:]
            return host or "unknown_domain"
        except Exception:
            return "unknown_domain"
    
    
    def acquire_coordinator_lock(manifest_id):
        """Return a live connection holding a manifest-scoped advisory lock."""
        conn = get_connection()
        key = int.from_bytes(hashlib.sha256(manifest_id.encode()).digest()[:8], "big", signed=True)
        with _cursor(conn) as cur:
            cur.execute("SELECT pg_try_advisory_lock(%s);", (key,))
            locked = cur.fetchone()[0]
        if not locked:
            conn.close()
            raise RuntimeError(f"another ingestion coordinator is active for {manifest_id}")
        return conn
    
    
    def create_run(manifest_id, urls, target_articles, per_file_target, config):
        run_id = str(uuid.uuid4())
        conn = get_connection()
        try:
            with _cursor(conn) as cur:
                cur.execute(
                    "INSERT INTO ingest_runs (run_id,manifest_id,target_articles,per_file_target,config) "
                    "VALUES (%s,%s,%s,%s,%s::jsonb)",
                    (run_id, manifest_id, target_articles, per_file_target, json.dumps(config)),
                )
                cur.execute("SELECT file_url FROM ingest_files WHERE manifest_id=%s AND complete", (manifest_id,))
                complete = {row[0] for row in cur.fetchall()}
                rows = [(run_id, i, url, url in complete, "eof" if url in complete else "pending")
                        for i, url in enumerate(urls)]
                if rows:
                    execute_values(cur, "INSERT INTO ingest_run_files (run_id,ordinal,file_url,eof,status) VALUES %s", rows)
            conn.commit()
            return run_id
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    
    def load_run(run_id):
        conn = get_connection()
        try:
            with _cursor(conn) as cur:
                cur.execute(
                    "SELECT run_id::text,manifest_id,target_articles,per_file_target,inserted_count,status,config "
                    "FROM ingest_runs WHERE run_id=%s", (run_id,))
                row = cur.fetchone()
                if row is None:
                    raise ValueError(f"unknown RESUME_RUN_ID: {run_id}")
                keys = ("run_id", "manifest_id", "target_articles", "per_file_target", "inserted_count", "status", "config")
                return dict(zip(keys, row))
        finally:
            conn.close()
    
    
    def load_run_files(run_id):
        conn = get_connection()
        try:
            with _cursor(conn) as cur:
                cur.execute(
                    "SELECT file_url,ordinal,next_offset,inserted_count,eof,status,etag,last_modified,last_error "
                    "FROM ingest_run_files WHERE run_id=%s ORDER BY ordinal", (run_id,))
                keys = ("file_url", "ordinal", "next_offset", "inserted_count", "eof", "status", "etag", "last_modified", "last_error")
                return [dict(zip(keys, row)) for row in cur.fetchall()]
        finally:
            conn.close()
    
    
    def _insert_new_records(cur, records):
        if not records:
            return []
        domains = sorted({extract_domain(r["url"]) for r in records})
        execute_values(cur, "INSERT INTO websites (domain) VALUES %s ON CONFLICT DO NOTHING", [(x,) for x in domains])
        cur.execute("SELECT domain,id FROM websites WHERE domain=ANY(%s)", (domains,))
        domain_ids = dict(cur.fetchall())
        authors = sorted({r.get("author", "").strip() for r in records
                          if r.get("author", "").strip() not in ("", "N/A")})
        author_ids = {}
        if authors:
            execute_values(cur, "INSERT INTO authors (name) VALUES %s ON CONFLICT DO NOTHING", [(x,) for x in authors])
            cur.execute("SELECT name,id FROM authors WHERE name=ANY(%s)", (authors,))
            author_ids = dict(cur.fetchall())
        rows = [(domain_ids[extract_domain(r["url"])], author_ids.get(r.get("author", "").strip()),
                 r["record_id"], r["url"], r["file_url"], r.get("warc_date")) for r in records]
        inserted = execute_values(
            cur,
            """INSERT INTO pages (website_id,author_id,warc_record_id,url,source_file_url,warc_date)
               VALUES %s ON CONFLICT (warc_record_id) DO NOTHING RETURNING warc_record_id,id""",
            rows, fetch=True)
        page_ids = {record_id: page_id for record_id, page_id in inserted}
        new_records = [r for r in records if r["record_id"] in page_ids]
        if new_records:
            execute_values(cur, """INSERT INTO metadata
                (page_id,title,published_date,language,arabic_dialect,word_count,char_count,links_count,headings,extraction_method)
                VALUES %s""", [(
                    page_ids[r["record_id"]], r.get("title"), r.get("published_date"), r.get("language"),
                    r.get("arabic_dialect"), r.get("word_count", 0), r.get("char_count", 0),
                    r.get("links_count", 0), json.dumps(r.get("headings", [])), r.get("extraction"),
                ) for r in new_records])
            execute_values(cur, "INSERT INTO content (page_id,cleaned_text) VALUES %s",
                           [(page_ids[r["record_id"]], r["cleaned_text"]) for r in new_records])
        return new_records
    
    
    def commit_chunk(run_id, result):
        """Atomically insert new articles and advance this run's file cursor."""
        conn = get_connection()
        try:
            with _cursor(conn) as cur:
                cur.execute("SELECT inserted_count FROM ingest_chunks WHERE chunk_id=%s", (result["chunk_id"],))
                prior = cur.fetchone()
                if prior is not None:
                    conn.rollback()
                    return prior[0]
                cur.execute("SELECT target_articles,per_file_target,inserted_count FROM ingest_runs WHERE run_id=%s FOR UPDATE", (run_id,))
                target, per_file, total_done = cur.fetchone()
                cur.execute("SELECT inserted_count FROM ingest_run_files WHERE run_id=%s AND file_url=%s FOR UPDATE",
                            (run_id, result["file_url"]))
                file_done = cur.fetchone()[0]
                total_left = len(result["candidates"]) if target == 0 else max(0, target - total_done)
                file_left = len(result["candidates"]) if per_file == 0 else max(0, per_file - file_done)
                candidates = result["candidates"][:min(len(result["candidates"]), total_left, file_left)]
                inserted_count = len(_insert_new_records(cur, candidates))
                failure, eof = result.get("error"), bool(result.get("eof"))
                status = "failed" if failure else ("eof" if eof else "pending")
                if per_file and file_done + inserted_count >= per_file:
                    status = "quota_reached"
                cur.execute("""UPDATE ingest_run_files SET next_offset=%s,inserted_count=inserted_count+%s,
                    eof=%s,status=%s,etag=COALESCE(%s,etag),last_modified=COALESCE(%s,last_modified),
                    last_error=%s,updated_at=CURRENT_TIMESTAMP WHERE run_id=%s AND file_url=%s""",
                    (result["next_offset"], inserted_count, eof, status, result.get("etag"),
                     result.get("last_modified"), failure, run_id, result["file_url"]))
                cur.execute("UPDATE ingest_runs SET inserted_count=inserted_count+%s,updated_at=CURRENT_TIMESTAMP WHERE run_id=%s",
                            (inserted_count, run_id))
                cur.execute("""INSERT INTO ingest_chunks
                    (chunk_id,run_id,file_url,start_offset,next_offset,candidate_count,inserted_count,eof,stats)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)""",
                    (result["chunk_id"], run_id, result["file_url"], result["start_offset"], result["next_offset"],
                     len(result["candidates"]), inserted_count, eof, json.dumps(result.get("stats", {}))))
                cur.execute("""INSERT INTO ingest_files (file_url,manifest_id,bytes_done,articles_done,complete)
                    SELECT %s,manifest_id,%s,%s,%s FROM ingest_runs WHERE run_id=%s
                    ON CONFLICT (file_url) DO UPDATE SET
                    bytes_done=GREATEST(ingest_files.bytes_done,EXCLUDED.bytes_done),
                    articles_done=ingest_files.articles_done+EXCLUDED.articles_done,
                    complete=ingest_files.complete OR EXCLUDED.complete,updated_at=CURRENT_TIMESTAMP""",
                    (result["file_url"], result["next_offset"], inserted_count, eof, run_id))
            conn.commit()
            return inserted_count
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    
    def finish_run(run_id, status):
        conn = get_connection()
        try:
            with _cursor(conn) as cur:
                cur.execute("UPDATE ingest_runs SET status=%s,updated_at=CURRENT_TIMESTAMP WHERE run_id=%s", (status, run_id))
            conn.commit()
        finally:
            conn.close()
    
    
    def save_batch_records(records_list, conn=None):
        """Compatibility helper; returns the number of newly inserted records."""
        own = conn is None
        conn = conn or get_connection()
        try:
            with _cursor(conn) as cur:
                count = len(_insert_new_records(cur, records_list))
            conn.commit()
            return count
        except Exception:
            conn.rollback()
            raise
        finally:
            if own:
                conn.close()
    
    
    def load_ingest_progress(manifest_id):
        conn = get_connection()
        try:
            with _cursor(conn) as cur:
                cur.execute("SELECT file_url,bytes_done,articles_done,complete FROM ingest_files WHERE manifest_id=%s", (manifest_id,))
                return {row[0]: row[1:] for row in cur.fetchall()}
        finally:
            conn.close()
    
    
    def upsert_ingest_progress(manifest_id, file_url, bytes_done, articles_done, complete):
        conn = get_connection()
        try:
            with _cursor(conn) as cur:
                cur.execute("""INSERT INTO ingest_files (file_url,manifest_id,bytes_done,articles_done,complete)
                    VALUES (%s,%s,%s,%s,%s) ON CONFLICT (file_url) DO UPDATE SET
                    bytes_done=GREATEST(ingest_files.bytes_done,EXCLUDED.bytes_done),
                    articles_done=GREATEST(ingest_files.articles_done,EXCLUDED.articles_done),
                    complete=ingest_files.complete OR EXCLUDED.complete,updated_at=CURRENT_TIMESTAMP""",
                    (file_url, manifest_id, bytes_done, articles_done, complete))
            conn.commit()
        finally:
            conn.close()
    
    
    if __name__ == "__main__":
        init_db()
    """Bounded streaming WARC parsing backed by FastWARC."""
    
    from fastwarc.warc import ArchiveIterator, WarcRecordType
    
    
    class OversizedPayload(Exception):
        pass
    
    
    def parse_warc_records_streaming(stream, max_html_bytes=2 * 1024 * 1024, base_offset=0):
        """Yield HTML response records with exact compressed source offsets.
    
        Parser/transport failures deliberately propagate so callers can retry; they
        must never be confused with a clean EOF.
        """
        iterator = ArchiveIterator(
            stream,
            record_types=WarcRecordType.response,
            parse_http=True,
            auto_decode="all",
            max_header_len=64 * 1024,
            stream_detect=True,
            buffer_size=64 * 1024,
            fsspec_args=False,
        )
        for record in iterator:
            start_offset = base_offset + record.stream_pos
            content_type = (record.http_content_type or "").lower()
            if "text/html" not in content_type and "application/xhtml" not in content_type:
                yield {"skip": "non_html", "start_offset": start_offset}
                continue
            payload = record.reader.read(max_html_bytes + 1)
            if len(payload) > max_html_bytes:
                yield {"skip": "oversized_html", "start_offset": start_offset}
                continue
            yield {
                "url": record.headers.get("WARC-Target-URI") or "",
                "warc_date": record.headers.get("WARC-Date"),
                "content_type": content_type,
                "record_id": record.record_id or record.headers.get("WARC-Record-ID") or "",
                "raw_bytes": payload,
                "start_offset": start_offset,
            }
    
    
    def parse_warc_stream_fastwarc(stream, **kwargs):
        """Compatibility name for older callers; now genuinely uses FastWARC."""
        yield from parse_warc_records_streaming(stream, **kwargs)
    ✓ • 0ms

## Activity

    $ for f in /AGENTS.md /home/AGENTS.md /home/spark-master/AGENTS.md /home/spark-master/rag_news_project/AGENTS.md; do if [ -f "$f" ]; then cat "$f"; fi; done
        command -v python3 spark-submit psql pytest
        python3 --version
        ls /opt
        ls /home/spark-master/rag_news_project
    /usr/bin/python3
    /opt/spark/bin/spark-submit
    /usr/bin/psql
    Python 3.13.5
    hadoop
    hadoop-3.5.0
    nvim-linux-x86_64
    spark
    spark-4.2.0-bin-hadoop3
    blog-retrieval-RAG-system
    distribution-lora-pipeline
    spark_warc_package.zip
    spark_warc_project
    spark_warc_project.zip
    spark_warc_v2
    test.py
    ✓ • 0ms

## Activity

    $ cat db/db_handler.py
        cat parsers/parsers.py
        sed -n '430,540p' stream_to_db.py
    """PostgreSQL schema and transactional ingestion helpers."""
    
    import hashlib
    import json
    import os
    import uuid
    from contextlib import contextmanager
    from urllib.parse import urlparse
    
    import psycopg2
    from psycopg2.extras import execute_values
    
    
    def _db_config():
        """Use libpq-compatible environment settings, with legacy defaults."""
        return {
            "dbname": os.environ.get("PGDATABASE", "warcdb"),
            "user": os.environ.get("PGUSER", "warc_user"),
            "password": os.environ.get("PGPASSWORD", "password"),
            "host": os.environ.get("PGHOST", "localhost"),
            "port": os.environ.get("PGPORT", "5432"),
            "connect_timeout": int(os.environ.get("PGCONNECT_TIMEOUT", "10")),
        }
    
    
    DB_CONFIG = _db_config()
    
    
    def get_connection():
        return psycopg2.connect(**_db_config())
    
    
    @contextmanager
    def _cursor(conn):
        cur = conn.cursor()
        try:
            yield cur
        finally:
            cur.close()
    
    
    def init_db():
        """Apply additive, backwards-compatible schema migrations."""
        ddl = """
        CREATE TABLE IF NOT EXISTS websites (
            id SERIAL PRIMARY KEY, domain TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS authors (
            id SERIAL PRIMARY KEY, name TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS pages (
            id SERIAL PRIMARY KEY,
            website_id INT REFERENCES websites(id) ON DELETE CASCADE,
            author_id INT REFERENCES authors(id) ON DELETE SET NULL,
            warc_record_id TEXT UNIQUE, url TEXT NOT NULL,
            source_file_url TEXT, warc_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS metadata (
            page_id INT PRIMARY KEY REFERENCES pages(id) ON DELETE CASCADE,
            title TEXT, published_date TEXT, language TEXT, arabic_dialect TEXT,
            word_count INT, char_count INT, links_count INT, headings JSONB,
            extraction_method TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS content (
            page_id INT PRIMARY KEY REFERENCES pages(id) ON DELETE CASCADE,
            cleaned_text TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS ingest_files (
            file_url TEXT PRIMARY KEY, manifest_id TEXT NOT NULL,
            bytes_done BIGINT NOT NULL DEFAULT 0,
            articles_done INT NOT NULL DEFAULT 0,
            complete BOOLEAN NOT NULL DEFAULT FALSE,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS ingest_runs (
            run_id UUID PRIMARY KEY, manifest_id TEXT NOT NULL,
            target_articles BIGINT NOT NULL, per_file_target BIGINT NOT NULL,
            inserted_count BIGINT NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'running',
            config JSONB NOT NULL DEFAULT '{}'::jsonb,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CHECK (target_articles >= 0), CHECK (per_file_target >= 0));
        CREATE TABLE IF NOT EXISTS ingest_run_files (
            run_id UUID NOT NULL REFERENCES ingest_runs(run_id) ON DELETE CASCADE,
            ordinal INT NOT NULL, file_url TEXT NOT NULL,
            next_offset BIGINT NOT NULL DEFAULT 0,
            inserted_count BIGINT NOT NULL DEFAULT 0,
            eof BOOLEAN NOT NULL DEFAULT FALSE,
            status TEXT NOT NULL DEFAULT 'pending',
            etag TEXT, last_modified TEXT, last_error TEXT,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (run_id, file_url), UNIQUE (run_id, ordinal));
        CREATE TABLE IF NOT EXISTS ingest_chunks (
            chunk_id TEXT PRIMARY KEY,
            run_id UUID NOT NULL REFERENCES ingest_runs(run_id) ON DELETE CASCADE,
            file_url TEXT NOT NULL, start_offset BIGINT NOT NULL,
            next_offset BIGINT NOT NULL, candidate_count INT NOT NULL,
            inserted_count INT NOT NULL, eof BOOLEAN NOT NULL,
            stats JSONB NOT NULL DEFAULT '{}'::jsonb,
            committed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE INDEX IF NOT EXISTS idx_ingest_files_manifest ON ingest_files (manifest_id);
        CREATE INDEX IF NOT EXISTS idx_ingest_run_files_sched
            ON ingest_run_files (run_id, status, ordinal);
        ALTER TABLE pages ADD COLUMN IF NOT EXISTS author_id INT REFERENCES authors(id) ON DELETE SET NULL;
        ALTER TABLE pages ADD COLUMN IF NOT EXISTS source_file_url TEXT;
        ALTER TABLE pages ADD COLUMN IF NOT EXISTS warc_date TEXT;
        ALTER TABLE metadata ADD COLUMN IF NOT EXISTS arabic_dialect TEXT;
        ALTER TABLE metadata ADD COLUMN IF NOT EXISTS extraction_method TEXT;
        ALTER TABLE websites ALTER COLUMN domain TYPE TEXT;
        ALTER TABLE authors ALTER COLUMN name TYPE TEXT;
        ALTER TABLE pages ALTER COLUMN warc_record_id TYPE TEXT;
        ALTER TABLE metadata ALTER COLUMN published_date TYPE TEXT;
        ALTER TABLE metadata ALTER COLUMN language TYPE TEXT;
        ALTER TABLE metadata ALTER COLUMN arabic_dialect TYPE TEXT;
        """
        conn = get_connection()
        try:
            with _cursor(conn) as cur:
                cur.execute(ddl)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    
    def extract_domain(url):
        try:
            host = (urlparse(url).hostname or "").lower().rstrip(".")
            if host.startswith("www."):
                host = host[4:]
            return host or "unknown_domain"
        except Exception:
            return "unknown_domain"
    
    
    def acquire_coordinator_lock(manifest_id):
        """Return a live connection holding a manifest-scoped advisory lock."""
        conn = get_connection()
        key = int.from_bytes(hashlib.sha256(manifest_id.encode()).digest()[:8], "big", signed=True)
        with _cursor(conn) as cur:
            cur.execute("SELECT pg_try_advisory_lock(%s);", (key,))
            locked = cur.fetchone()[0]
        if not locked:
            conn.close()
            raise RuntimeError(f"another ingestion coordinator is active for {manifest_id}")
        return conn
    
    
    def create_run(manifest_id, urls, target_articles, per_file_target, config):
        run_id = str(uuid.uuid4())
        conn = get_connection()
        try:
            with _cursor(conn) as cur:
                cur.execute(
                    "INSERT INTO ingest_runs (run_id,manifest_id,target_articles,per_file_target,config) "
                    "VALUES (%s,%s,%s,%s,%s::jsonb)",
                    (run_id, manifest_id, target_articles, per_file_target, json.dumps(config)),
                )
                cur.execute("SELECT file_url FROM ingest_files WHERE manifest_id=%s AND complete", (manifest_id,))
                complete = {row[0] for row in cur.fetchall()}
                rows = [(run_id, i, url, url in complete, "eof" if url in complete else "pending")
                        for i, url in enumerate(urls)]
                if rows:
                    execute_values(cur, "INSERT INTO ingest_run_files (run_id,ordinal,file_url,eof,status) VALUES %s", rows)
            conn.commit()
            return run_id
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    
    def load_run(run_id):
        conn = get_connection()
        try:
            with _cursor(conn) as cur:
                cur.execute(
                    "SELECT run_id::text,manifest_id,target_articles,per_file_target,inserted_count,status,config "
                    "FROM ingest_runs WHERE run_id=%s", (run_id,))
                row = cur.fetchone()
                if row is None:
                    raise ValueError(f"unknown RESUME_RUN_ID: {run_id}")
                keys = ("run_id", "manifest_id", "target_articles", "per_file_target", "inserted_count", "status", "config")
                return dict(zip(keys, row))
        finally:
            conn.close()
    
    
    def load_run_files(run_id):
        conn = get_connection()
        try:
            with _cursor(conn) as cur:
                cur.execute(
                    "SELECT file_url,ordinal,next_offset,inserted_count,eof,status,etag,last_modified,last_error "
                    "FROM ingest_run_files WHERE run_id=%s ORDER BY ordinal", (run_id,))
                keys = ("file_url", "ordinal", "next_offset", "inserted_count", "eof", "status", "etag", "last_modified", "last_error")
                return [dict(zip(keys, row)) for row in cur.fetchall()]
        finally:
            conn.close()
    
    
    def _insert_new_records(cur, records):
        if not records:
            return []
        domains = sorted({extract_domain(r["url"]) for r in records})
        execute_values(cur, "INSERT INTO websites (domain) VALUES %s ON CONFLICT DO NOTHING", [(x,) for x in domains])
        cur.execute("SELECT domain,id FROM websites WHERE domain=ANY(%s)", (domains,))
        domain_ids = dict(cur.fetchall())
        authors = sorted({r.get("author", "").strip() for r in records
                          if r.get("author", "").strip() not in ("", "N/A")})
        author_ids = {}
        if authors:
            execute_values(cur, "INSERT INTO authors (name) VALUES %s ON CONFLICT DO NOTHING", [(x,) for x in authors])
            cur.execute("SELECT name,id FROM authors WHERE name=ANY(%s)", (authors,))
            author_ids = dict(cur.fetchall())
        rows = [(domain_ids[extract_domain(r["url"])], author_ids.get(r.get("author", "").strip()),
                 r["record_id"], r["url"], r["file_url"], r.get("warc_date")) for r in records]
        inserted = execute_values(
            cur,
            """INSERT INTO pages (website_id,author_id,warc_record_id,url,source_file_url,warc_date)
               VALUES %s ON CONFLICT (warc_record_id) DO NOTHING RETURNING warc_record_id,id""",
            rows, fetch=True)
        page_ids = {record_id: page_id for record_id, page_id in inserted}
        new_records = [r for r in records if r["record_id"] in page_ids]
        if new_records:
            execute_values(cur, """INSERT INTO metadata
                (page_id,title,published_date,language,arabic_dialect,word_count,char_count,links_count,headings,extraction_method)
                VALUES %s""", [(
                    page_ids[r["record_id"]], r.get("title"), r.get("published_date"), r.get("language"),
                    r.get("arabic_dialect"), r.get("word_count", 0), r.get("char_count", 0),
                    r.get("links_count", 0), json.dumps(r.get("headings", [])), r.get("extraction"),
                ) for r in new_records])
            execute_values(cur, "INSERT INTO content (page_id,cleaned_text) VALUES %s",
                           [(page_ids[r["record_id"]], r["cleaned_text"]) for r in new_records])
        return new_records
    
    
    def commit_chunk(run_id, result):
        """Atomically insert new articles and advance this run's file cursor."""
        conn = get_connection()
        try:
            with _cursor(conn) as cur:
                cur.execute("SELECT inserted_count FROM ingest_chunks WHERE chunk_id=%s", (result["chunk_id"],))
                prior = cur.fetchone()
                if prior is not None:
                    conn.rollback()
                    return prior[0]
                cur.execute("SELECT target_articles,per_file_target,inserted_count FROM ingest_runs WHERE run_id=%s FOR UPDATE", (run_id,))
                target, per_file, total_done = cur.fetchone()
                cur.execute("SELECT inserted_count FROM ingest_run_files WHERE run_id=%s AND file_url=%s FOR UPDATE",
                            (run_id, result["file_url"]))
                file_done = cur.fetchone()[0]
                total_left = len(result["candidates"]) if target == 0 else max(0, target - total_done)
                file_left = len(result["candidates"]) if per_file == 0 else max(0, per_file - file_done)
                candidates = result["candidates"][:min(len(result["candidates"]), total_left, file_left)]
                inserted_count = len(_insert_new_records(cur, candidates))
                failure, eof = result.get("error"), bool(result.get("eof"))
                status = "failed" if failure else ("eof" if eof else "pending")
                if per_file and file_done + inserted_count >= per_file:
                    status = "quota_reached"
                cur.execute("""UPDATE ingest_run_files SET next_offset=%s,inserted_count=inserted_count+%s,
                    eof=%s,status=%s,etag=COALESCE(%s,etag),last_modified=COALESCE(%s,last_modified),
                    last_error=%s,updated_at=CURRENT_TIMESTAMP WHERE run_id=%s AND file_url=%s""",
                    (result["next_offset"], inserted_count, eof, status, result.get("etag"),
                     result.get("last_modified"), failure, run_id, result["file_url"]))
                cur.execute("UPDATE ingest_runs SET inserted_count=inserted_count+%s,updated_at=CURRENT_TIMESTAMP WHERE run_id=%s",
                            (inserted_count, run_id))
                cur.execute("""INSERT INTO ingest_chunks
                    (chunk_id,run_id,file_url,start_offset,next_offset,candidate_count,inserted_count,eof,stats)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)""",
                    (result["chunk_id"], run_id, result["file_url"], result["start_offset"], result["next_offset"],
                     len(result["candidates"]), inserted_count, eof, json.dumps(result.get("stats", {}))))
                cur.execute("""INSERT INTO ingest_files (file_url,manifest_id,bytes_done,articles_done,complete)
                    SELECT %s,manifest_id,%s,%s,%s FROM ingest_runs WHERE run_id=%s
                    ON CONFLICT (file_url) DO UPDATE SET
                    bytes_done=GREATEST(ingest_files.bytes_done,EXCLUDED.bytes_done),
                    articles_done=ingest_files.articles_done+EXCLUDED.articles_done,
                    complete=ingest_files.complete OR EXCLUDED.complete,updated_at=CURRENT_TIMESTAMP""",
                    (result["file_url"], result["next_offset"], inserted_count, eof, run_id))
            conn.commit()
            return inserted_count
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    
    def finish_run(run_id, status):
        conn = get_connection()
        try:
            with _cursor(conn) as cur:
                cur.execute("UPDATE ingest_runs SET status=%s,updated_at=CURRENT_TIMESTAMP WHERE run_id=%s", (status, run_id))
            conn.commit()
        finally:
            conn.close()
    
    
    def save_batch_records(records_list, conn=None):
        """Compatibility helper; returns the number of newly inserted records."""
        own = conn is None
        conn = conn or get_connection()
        try:
            with _cursor(conn) as cur:
                count = len(_insert_new_records(cur, records_list))
            conn.commit()
            return count
        except Exception:
            conn.rollback()
            raise
        finally:
            if own:
                conn.close()
    
    
    def load_ingest_progress(manifest_id):
        conn = get_connection()
        try:
            with _cursor(conn) as cur:
                cur.execute("SELECT file_url,bytes_done,articles_done,complete FROM ingest_files WHERE manifest_id=%s", (manifest_id,))
                return {row[0]: row[1:] for row in cur.fetchall()}
        finally:
            conn.close()
    
    
    def upsert_ingest_progress(manifest_id, file_url, bytes_done, articles_done, complete):
        conn = get_connection()
        try:
            with _cursor(conn) as cur:
                cur.execute("""INSERT INTO ingest_files (file_url,manifest_id,bytes_done,articles_done,complete)
                    VALUES (%s,%s,%s,%s,%s) ON CONFLICT (file_url) DO UPDATE SET
                    bytes_done=GREATEST(ingest_files.bytes_done,EXCLUDED.bytes_done),
                    articles_done=GREATEST(ingest_files.articles_done,EXCLUDED.articles_done),
                    complete=ingest_files.complete OR EXCLUDED.complete,updated_at=CURRENT_TIMESTAMP""",
                    (file_url, manifest_id, bytes_done, articles_done, complete))
            conn.commit()
        finally:
            conn.close()
    
    
    if __name__ == "__main__":
        init_db()
    """Bounded streaming WARC parsing backed by FastWARC."""
    
    from fastwarc.warc import ArchiveIterator, WarcRecordType
    
    
    class OversizedPayload(Exception):
        pass
    
    
    def parse_warc_records_streaming(stream, max_html_bytes=2 * 1024 * 1024, base_offset=0):
        """Yield HTML response records with exact compressed source offsets.
    
        Parser/transport failures deliberately propagate so callers can retry; they
        must never be confused with a clean EOF.
        """
        iterator = ArchiveIterator(
            stream,
            record_types=WarcRecordType.response,
            parse_http=True,
            auto_decode="all",
            max_header_len=64 * 1024,
            stream_detect=True,
            buffer_size=64 * 1024,
            fsspec_args=False,
        )
        for record in iterator:
            start_offset = base_offset + record.stream_pos
            content_type = (record.http_content_type or "").lower()
            if "text/html" not in content_type and "application/xhtml" not in content_type:
                yield {"skip": "non_html", "start_offset": start_offset}
                continue
            payload = record.reader.read(max_html_bytes + 1)
            if len(payload) > max_html_bytes:
                yield {"skip": "oversized_html", "start_offset": start_offset}
                continue
            yield {
                "url": record.headers.get("WARC-Target-URI") or "",
                "warc_date": record.headers.get("WARC-Date"),
                "content_type": content_type,
                "record_id": record.record_id or record.headers.get("WARC-Record-ID") or "",
                "raw_bytes": payload,
                "start_offset": start_offset,
            }
    
    
    def parse_warc_stream_fastwarc(stream, **kwargs):
        """Compatibility name for older callers; now genuinely uses FastWARC."""
        yield from parse_warc_records_streaming(stream, **kwargs)
                                finish_run(run_id, "failed")
                                raise RuntimeError(f"database commit failed; run {run_id} is resumable") from error
                            _sleep_backoff(attempt)
                    totals["candidates"] += len(result["candidates"])
                    totals["inserted"] += inserted
                    wave_inserted += inserted
                    made_progress |= result["next_offset"] > result["start_offset"] or inserted > 0
                run = load_run(run_id)
                print(
                    f"Wave {wave}: committed {run['inserted_count']:,}/"
                    f"{run['target_articles'] or 'unlimited'}; "
                    f"wave candidates={sum(len(r['candidates']) for r in results):,}, "
                    f"new={wave_inserted:,}"
                )
                if not made_progress:
                    finish_run(run_id, "failed")
                    raise RuntimeError(f"no cursor or insert progress in wave {wave}; run {run_id} stopped safely")
        finally:
            if spark is not None:
                spark.stop()
            lock_conn.close()
    
    
    if __name__ == "__main__":
        try:
            sys.exit(run_streaming_pipeline())
        except Exception as error:
            stamp = datetime.now(timezone.utc).isoformat()
            print(f"[{stamp}] FATAL {type(error).__name__}: {error}", file=sys.stderr)
            sys.exit(1)
    ✓ • 0ms

## Activity

    $ cat run_to_db.sh
        ls /usr/lib/postgresql
        ls -d ../spark_warc_project/.venv /tmp/*venv* 2>/dev/null
        python3 - <<'PY'
        import importlib.util
        for name in ('pyspark','fastwarc','warcio','psycopg2','lingua','selectolax','trafilatura','pytest','venv_pack','psutil'):
         print(name, bool(importlib.util.find_spec(name)))
        PY
    #!/usr/bin/env bash
    set -euo pipefail
    
    PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
    cd "$PROJECT_ROOT"
    
    TMPDIR="$(mktemp -d)"
    ZIP="$TMPDIR/project_code.zip"
    VENV_ARCHIVE="$PROJECT_ROOT/pyspark_venv.tar.gz"
    VENV_FINGERPRINT_FILE="$PROJECT_ROOT/.venv-pack.fingerprint"
    
    trap 'rm -rf "$TMPDIR"' EXIT
    
    # Activate local driver environment
    source "$PROJECT_ROOT/.venv/bin/activate"
    
    # Rebuild whenever the declared environment changes.
    VENV_FINGERPRINT="$(sha256sum requirements.txt pyvenv.cfg .venv/pyvenv.cfg | sha256sum | awk '{print $1}')"
    PACKED_FINGERPRINT="$(test -f "$VENV_FINGERPRINT_FILE" && tr -d '\n' < "$VENV_FINGERPRINT_FILE" || true)"
    if [ ! -f "$VENV_ARCHIVE" ] || [ "$VENV_FINGERPRINT" != "$PACKED_FINGERPRINT" ]; then
        echo "Building PySpark worker environment..."
        venv-pack -f -o "$VENV_ARCHIVE"
        echo "$VENV_FINGERPRINT" > "$VENV_FINGERPRINT_FILE"
    fi
    
    # Package current project code on every run
    echo "Packaging project code..."
    zip -qr "$ZIP" \
        extractors \
        parsers \
        db \
        utils.py
    
    # Driver uses the local venv on spark-master
    export PYSPARK_DRIVER_PYTHON="$PROJECT_ROOT/.venv/bin/python"
    
    # Executors use the environment distributed by YARN
    export PYSPARK_PYTHON="./environment/bin/python"
    
    # Tunables (override per run, e.g. NUM_FILES=2 ./run_to_db.sh)
    #   NUM_FILES: files to process from START_FILE_OFFSET; unset/empty/all/0 = to end of manifest
    #   START_FILE_OFFSET: skip the first N manifest entries (file-range targeting); 0 = from start
    #   MAX_ACCEPTED_PER_FILE: maximum newly committed articles from each file; 0 = unlimited
    #   MAX_FILES_PER_ROUND: concurrent files; capped at this three-executor cluster's size
    #   MIN_WORD_COUNT: article = this many words+ after extraction (trafilatura acceptance + yield gate)
    #   MAX_ACCEPTED_ARTICLES: exact new-commit target; 0 = process selected files to EOF
    #   USE_HDFS_CACHE: 0 disables both shared HDFS artifacts (worker venv + Spark jars)
    export NUM_FILES="${NUM_FILES:-15}"
    export START_FILE_OFFSET="${START_FILE_OFFSET:-0}"
    export MAX_ACCEPTED_ARTICLES="${MAX_ACCEPTED_ARTICLES:-0}"
    export MAX_ACCEPTED_PER_FILE="${MAX_ACCEPTED_PER_FILE:-0}"
    export MAX_FILES_PER_ROUND="${MAX_FILES_PER_ROUND:-3}"
    export MIN_WORD_COUNT="${MIN_WORD_COUNT:-80}"
    export WORKER_MAX_CANDIDATES="${WORKER_MAX_CANDIDATES:-100}"
    export WORKER_MAX_RESULT_BYTES="${WORKER_MAX_RESULT_BYTES:-4194304}"
    export WORKER_MAX_INPUT_BYTES="${WORKER_MAX_INPUT_BYTES:-33554432}"
    export WORKER_MAX_SECONDS="${WORKER_MAX_SECONDS:-120}"
    export MAX_HTML_BYTES="${MAX_HTML_BYTES:-2097152}"
    export MAX_ARTICLE_BYTES="${MAX_ARTICLE_BYTES:-524288}"
    export SPARK_EXECUTOR_MEMORY="${SPARK_EXECUTOR_MEMORY:-512m}"
    export SPARK_EXECUTOR_MEMORY_OVERHEAD="${SPARK_EXECUTOR_MEMORY_OVERHEAD:-512m}"
    export SPARK_DRIVER_MEMORY="${SPARK_DRIVER_MEMORY:-512m}"
    
    # --- Shared venv on HDFS (upload once, reuse across runs) ---
    # Per-run --archives of the worker venv re-uploads + re-localizes on every
    # submit and fills NM disks. Instead we store a content-addressed copy on
    # HDFS and reference it; rebuilds (new md5) upload exactly once, old copies
    # are pruned.
    HDFS_APPS_DIR="${HDFS_APPS_DIR:-/user/spark-master/apps/spark}"
    VENV_MD5="$(md5sum "$VENV_ARCHIVE" | awk '{print $1}')"
    HDFS_VENV="$HDFS_APPS_DIR/pyspark_venv-${VENV_MD5}.tar.gz"
    ARCHIVES_SPEC="$VENV_ARCHIVE#environment"   # fallback: local per-run upload
    
    hdfs_ok() { hdfs dfs -test -e / >/dev/null 2>&1; }
    
    upload_venv_hdfs() {
        # Best-effort: any failure returns non-zero so the caller falls back
        # to a local per-run upload instead of aborting the submit (set -e).
        hdfs dfs -mkdir -p "$HDFS_APPS_DIR" 2>/dev/null || return 1
        hdfs dfs -put -f "$VENV_ARCHIVE" "$HDFS_VENV" 2>/dev/null || return 1
        return 0
    }
    
    if [ "${USE_HDFS_CACHE:-1}" = "1" ] && hdfs_ok; then
        if hdfs dfs -test -e "$HDFS_VENV" 2>/dev/null; then
            echo "Reusing HDFS venv $HDFS_VENV (no upload needed)."
            ARCHIVES_SPEC="hdfs://$HDFS_VENV#environment"
        elif upload_venv_hdfs; then
            echo "Uploaded venv to HDFS ($HDFS_VENV, one-time for this build)."
            ARCHIVES_SPEC="hdfs://$HDFS_VENV#environment"
        else
            echo "WARNING: HDFS venv upload failed — falling back to per-run venv upload."
        fi
    else
        echo "WARNING: HDFS unreachable or USE_HDFS_CACHE=0 — falling back to per-run venv upload."
    fi
    
    # --- Shared Spark jars archive (default on, verified 2026-09-28) ---
    # Avoids the per-run "falling back to uploading libraries under SPARK_HOME".
    # Disable per-run with USE_HDFS_CACHE=0.
    EXTRA_CONF=()
    if [ "${USE_HDFS_CACHE:-1}" = "1" ] && hdfs_ok; then
        SPARK_JARS_ZIP="$PROJECT_ROOT/spark-libs.zip"
        SPARK_ARCHIVE_MD5="$(md5sum "$SPARK_JARS_ZIP" 2>/dev/null | awk '{print $1}' || true)"
        if [ ! -f "$SPARK_JARS_ZIP" ]; then
            echo "Building Spark jars archive (one-time)..."
            (cd "${SPARK_HOME:?SPARK_HOME not set}/jars" && zip -qr "$SPARK_JARS_ZIP" .)
            SPARK_ARCHIVE_MD5="$(md5sum "$SPARK_JARS_ZIP" | awk '{print $1}')"
        fi
        HDFS_SPARK_ARCHIVE="$HDFS_APPS_DIR/spark-libs-${SPARK_ARCHIVE_MD5}.zip"
        if hdfs dfs -test -e "$HDFS_SPARK_ARCHIVE" 2>/dev/null; then
            echo "Reusing HDFS Spark archive $HDFS_SPARK_ARCHIVE."
            EXTRA_CONF+=(--conf "spark.yarn.archive=hdfs://$HDFS_SPARK_ARCHIVE")
        elif hdfs dfs -mkdir -p "$HDFS_APPS_DIR" 2>/dev/null \
            && hdfs dfs -put -f "$SPARK_JARS_ZIP" "$HDFS_SPARK_ARCHIVE" 2>/dev/null; then
            echo "Uploaded Spark jars archive to HDFS (one-time)."
            EXTRA_CONF+=(--conf "spark.yarn.archive=hdfs://$HDFS_SPARK_ARCHIVE")
        else
            echo "WARNING: Spark archive upload failed — continuing without spark.yarn.archive."
        fi
    fi
    
    echo "Submitting stream_to_db job to YARN (NUM_FILES=$NUM_FILES, MAX_ACCEPTED_PER_FILE=$MAX_ACCEPTED_PER_FILE, MAX_FILES_PER_ROUND=$MAX_FILES_PER_ROUND, MAX_ACCEPTED_ARTICLES=$MAX_ACCEPTED_ARTICLES)..."
    
    spark-submit \
        --master yarn \
        --deploy-mode client \
        --driver-memory "$SPARK_DRIVER_MEMORY" \
        --executor-memory "$SPARK_EXECUTOR_MEMORY" \
        --conf "spark.executor.memoryOverhead=$SPARK_EXECUTOR_MEMORY_OVERHEAD" \
        --conf "spark.executor.cores=1" \
        --conf "spark.executor.instances=3" \
        --conf "spark.pyspark.driver.python=$PROJECT_ROOT/.venv/bin/python" \
        --conf "spark.pyspark.python=./environment/bin/python" \
        "${EXTRA_CONF[@]}" \
        --archives "$ARCHIVES_SPEC" \
        --py-files "$ZIP" \
        stream_to_db.py
    18
    ../spark_warc_project/.venv
    /tmp/venvpack.log
    pyspark True
    fastwarc False
    warcio False
    psycopg2 False
    lingua False
    selectolax False
    trafilatura False
    pytest False
    venv_pack False
    psutil False
    ✓ • 0ms

## Activity

    $ cat /opt/spark/conf/spark-defaults.conf
        free -m
        pg_isready
        ls -l /usr/lib/postgresql/*/bin/initdb
        ls -l /home/hadoop
    #
    # Licensed to the Apache Software Foundation (ASF) under one or more
    # contributor license agreements.  See the NOTICE file distributed with
    # this work for additional information regarding copyright ownership.
    # The ASF licenses this file to You under the Apache License, Version 2.0
    # (the "License"); you may not use this file except in compliance with
    # the License.  You may obtain a copy of the License at
    #
    #    http://www.apache.org/licenses/LICENSE-2.0
    #
    # Unless required by applicable law or agreed to in writing, software
    # distributed under the License is distributed on an "AS IS" BASIS,
    # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    # See the License for the specific language governing permissions and
    # limitations under the License.
    #
    
    # Default system properties included when running spark-submit.
    # This is useful for setting default environmental settings.
    
    # Example:
    # spark.master                     spark://master:7077
    # spark.eventLog.enabled           true
    # spark.eventLog.dir               hdfs://namenode:8021/directory
    # spark.serializer                 org.apache.spark.serializer.KryoSerializer
    # spark.driver.memory              5g
    # spark.executor.extraJavaOptions  -XX:+PrintGCDetails -Dkey=value -Dnumbers="one two three"
    spark.master                     yarn
    spark.submit.deployMode          client
    
    spark.eventLog.enabled           true
    spark.eventLog.dir               hdfs:///spark-logs
    spark.history.fs.logDirectory    hdfs:///spark-logs
    
    spark.executor.memory            2g
    spark.executor.cores             2
    spark.driver.memory              2g
                   total        used        free      shared  buff/cache   available
    Mem:            1935         854         207          16        1038        1081
    Swap:            984           0         984
    /var/run/postgresql:5432 - no response
    -rwxr-xr-x 1 nobody nogroup 196616 Aug 11 23:58 /usr/lib/postgresql/18/bin/initdb
    total 40
    drwxrwxr-x 2 hadoop hadoop  4096 Sep 23 12:08 bin
    -rw-rw-r-- 1 hadoop hadoop 29026 Sep 22 14:40 namenode-format.log
    -rw-rw-r-- 1 hadoop hadoop   760 Sep 23 11:18 postgres_spark_test.py
    ✓ • 75ms

## Assistant

The first pass has several gaps: failed files are not retried on resume, filter settings are not consistently sent to workers, and the launcher references a missing file when packaging dependencies. I’m fixing these alongside the tests. This checkout also has no virtual environment, and PostgreSQL is not responding on its default socket.

## Activity

    $ ../spark_warc_project/.venv/bin/python - <<'PY'
        import importlib.util,sys
        print(sys.version)
        for n in ('fastwarc','warcio','psycopg2','lingua','selectolax','trafilatura','pytest','venv_pack','psutil','langchain_core'):
         s=importlib.util.find_spec(n); print(n, s.origin if s else None)
        PY
        ls -l ../spark_warc_project/.venv/bin/python*
    3.13.5 (main, Aug 10 2026, 12:06:59) [GCC 14.2.0]
    fastwarc /home/spark-master/rag_news_project/spark_warc_project/.venv/lib/python3.13/site-packages/fastwarc/__init__.py
    warcio /home/spark-master/rag_news_project/spark_warc_project/.venv/lib/python3.13/site-packages/warcio/__init__.py
    psycopg2 /home/spark-master/rag_news_project/spark_warc_project/.venv/lib/python3.13/site-packages/psycopg2/__init__.py
    lingua /home/spark-master/rag_news_project/spark_warc_project/.venv/lib/python3.13/site-packages/lingua/__init__.py
    selectolax /home/spark-master/rag_news_project/spark_warc_project/.venv/lib/python3.13/site-packages/selectolax/__init__.py
    trafilatura /home/spark-master/rag_news_project/spark_warc_project/.venv/lib/python3.13/site-packages/trafilatura/__init__.py
    pytest None
    venv_pack /home/spark-master/rag_news_project/spark_warc_project/.venv/lib/python3.13/site-packages/venv_pack/__init__.py
    psutil /home/spark-master/rag_news_project/spark_warc_project/.venv/lib/python3.13/site-packages/psutil/__init__.py
    langchain_core /home/spark-master/rag_news_project/spark_warc_project/.venv/lib/python3.13/site-packages/langchain_core/__init__.py
    lrwxrwxrwx 1 hadoop nogroup  7 Sep 23 14:28 ../spark_warc_project/.venv/bin/python -> python3
    lrwxrwxrwx 1 hadoop nogroup 16 Sep 23 14:28 ../spark_warc_project/.venv/bin/python3 -> /usr/bin/python3
    lrwxrwxrwx 1 hadoop nogroup  7 Sep 23 14:28 ../spark_warc_project/.venv/bin/python3.13 -> python3
    ✓ • 651ms

## Activity

    $ ../spark_warc_project/.venv/bin/python - <<'PY'
        from fastwarc.warc import ArchiveIterator,WarcRecord
        print(ArchiveIterator.__doc__)
        print(WarcRecord.parse_http.__doc__)
        print(WarcRecord.__dict__.keys())
        from lingua import LanguageDetectorBuilder
        print([x for x in dir(LanguageDetectorBuilder) if 'thread' in x])
        PY
    WARC record stream iterator.
    
    The iterator can be initialized from a file-like Python object, a path-like
    object, or a URL string. If installed, :mod:`fsspec` is used for opening
    paths and URLs unless ``fsspec_args=False``.
    
    :param stream: input stream, file-like object, file name, or URL
    :param record_types: bitmask of :class:`WarcRecordType` values to return
    :param parse_http: parse HTTP records automatically
    :param min_content_length: skip records smaller than this length, or ``None`` to disable
    :param max_content_length: skip records larger than this length, or ``None`` to disable
    :param func_filter: Python callable taking a :class:`WarcRecord` and returning ``bool``
    :param verify_digests: skip records with missing or invalid block digests
    :param quirks_mode: enable lenient parsing for malformed records
    :param auto_decode: automatically decode HTTP payload encodings
    :param max_header_len: maximum allowed header length (throws an error if exceeded)
    :param stream_detect: auto-detect gzip, zstd, or lz4 compressed streams
    :param default_buffer_size: default buffer size to use for reading from files
                                (has no effect if ``stream`` is not a path-like object)
    :param inplace: Reuse and mutate the same :class:`WarcRecord` instance instead of creating
                    a new instance in each iteration.
    :param fsspec_args: arguments for :mod:`fsspec`, or ``False`` to disable it
    :param strict_mode: this argument is deprecated and ignored. Use ``quirks_mode`` instead.
    Parse HTTP headers and advance the payload reader.
    
    It is safe to call this method multiple times, even if the record is not
    an HTTP record.
    
    If a parsed header exceeds `max_header_len`, an error is raised.
    
    Quirks mode allows parsing of headers terminated with only LF instead of CRLF.
    
    :param auto_decode: automatically decode HTTP payload encodings
                        (accepted values: ``'none'``, ``'content'``, ``'transfer'``, ``'all'``)
    :param max_header_len: maximum allowed header length (throws an error if exceeded)
    :param quirks_mode: enable parsing of LF-only headers.
    :param strict_mode: this argument is deprecated and ignored.
    dict_keys(['__new__', '__repr__', '__str__', '__lt__', '__le__', '__eq__', '__ne__', '__gt__', '__ge__', 'from_bytes', 'from_reader', '__getnewargs__', '__getstate__', '__setstate__', 'init_headers', 'freeze', 'set_bytes_content', 'set_bytes_payload', 'consume', 'parse_warc_headers', 'parse_http', 'verify_block_digest', 'verify_payload_digest', 'write', 'record_type', 'stream_pos', 'is_frozen', 'http_date', 'http_last_modified', 'http_charset', 'content_length', 'is_http_parsed', 'http_content_type', 'record_id', 'is_http', 'http_headers', 'headers', 'record_date', 'reader', '__doc__', '__hash__', '__module__'])
    []
    ✓ • 621ms

## Activity

    $ ../spark_warc_project/.venv/bin/python - <<'PY'
        import io,gzip
        from warcio.warcwriter import WARCWriter
        from warcio.statusandheaders import StatusAndHeaders
        from parsers.parsers import parse_warc_records_streaming
        b=io.BytesIO();w=WARCWriter(b,gzip=True)
        for i in range(3):
         r=w.create_warc_record('https://example.com/'+str(i),'response',payload=io.BytesIO(b'<html>hello world</html>'),http_headers=StatusAndHeaders('200 OK',[('Content-Type','text/html')],protocol='HTTP/1.1'));w.write_record(r)
        data=b.getvalue()
        for suffix,d in [('full',data),('trunc',data[:-15]),('junk',data+b'junk')]:
         try: print(suffix,len(d),[(r['start_offset'],len(r['raw_bytes'])) for r in parse_warc_records_streaming(io.BytesIO(d))])
         except Exception as e: print(type(e).__name__,str(e))
        PY
    full 977 [(0, 24), (326, 24), (652, 24)]
    trunc 962 [(0, 24), (326, 24), (652, 15)]
    OSError Gzip decompression error: data error
    ✓ • 1.32s

## Activity

    $ mkdir -p tests
        cp langchain.py rag_loader.py
        python3 - <<'PY'
        p='extractors/extractors.py'
        s=open(p).read().replace('def detect_languages_batch(texts: List[str]) -> List[str]:','def detect_languages_batch(texts: List[str], min_confidence=None) -> List[str]:').replace('    if not texts:\n        return []','    if not texts:\n        return []\n    threshold = LINGUA_MIN_CONFIDENCE if min_confidence is None else min_confidence').replace('top.value < LINGUA_MIN_CONFIDENCE','top.value < threshold').replace('def extract_html_fields(record: Dict[str, Any], min_words: int = 80) -> Dict[str, Any]:','def extract_html_fields(record: Dict[str, Any], min_words: int = 80, use_trafilatura=None) -> Dict[str, Any]:').replace('decode_and_validate(record["raw_bytes"])','decode_and_validate(record["raw_bytes"], record.get("charset"))').replace('    trafi_text = _trafilatura_text(html_str) if USE_TRAFILATURA else ""','    use_trafilatura = USE_TRAFILATURA if use_trafilatura is None else use_trafilatura\n    trafi_text = _trafilatura_text(html_str) if use_trafilatura else ""')
        s=s.replace('    middle = len(text) // 2\n    return text[:800] + " " + text[middle - 300:middle + 300] + " " + text[-600:]','    middle_start = max(800, min(len(text) // 2 - 300, len(text) - 1200))\n    return text[:800] + " " + text[middle_start:middle_start + 600] + " " + text[-600:]')
        open(p,'w').write(s)
        p='utils.py';s=open(p).read().replace('    arabic_chars = len(ARABIC_CHAR_PATTERN.findall(sample))','    arabic_chars = sum(c.isalpha() and bool(ARABIC_CHAR_PATTERN.match(c)) for c in sample)').replace('def decode_and_validate(raw_bytes: bytes)', 'def decode_and_validate(raw_bytes: bytes, declared_encoding: Optional[str] = None)')
        s=s.replace('    decoded_text = None\n    try:', '''    decoded_text = None
            if declared_encoding:
                try:
                    decoded_text = raw_bytes.decode(declared_encoding, errors="strict")
                except (LookupError, UnicodeError):
                    pass
            try:''').replace('        decoded_text = raw_bytes.decode("utf-8", errors="strict")','        if decoded_text is None:\n            decoded_text = raw_bytes.decode("utf-8", errors="strict")').replace('    if not is_clean_encoding(decoded_text):','    decoded_text = decoded_text.replace("\\x00", "")\n    if not is_clean_encoding(decoded_text):')
        open(p,'w').write(s)
        p='rag_loader.py';s=open(p).read();a=s.index('BASE_DIR =');b=s.index('from db.db_handler',a);s=s[:a]+s[b:];s=s.replace('    conn = get_connection()','    if limit is not None and limit < 1:\n        raise ValueError("limit must be positive")\n    if FETCH_BATCH_SIZE < 1:\n        raise ValueError("RAG_FETCH_BATCH_SIZE must be positive")\n    conn = get_connection()',1);open(p,'w').write(s)
        open('langchain.py','w').write('"""Compatibility imports; new callers should import rag_loader."""\nfrom rag_loader import (iter_documents, iter_document_chunks,\n                        load_documents_distributed, split_documents_into_chunks)\n')
        PY
    ✓ • 0ms

## Activity

    $ cat > parsers/parsers.py <<'PY'
        """FastWARC parsing with bounded payloads and validated gzip transport."""
        
        import zlib
        from fastwarc.warc import ArchiveIterator, WarcRecordType
        
        
        class ValidatedGzipStream:
            """Validate CRC/trailers with bounded scratch space as FastWARC reads.
        
            FastWARC can return a partial final record on a truncated gzip stream.
            Checking the outer gzip stream prevents that from becoming a saved EOF.
            """
            def __init__(self, source, expected_bytes=None):
                self.source = source
                self.expected_bytes = expected_bytes
                self.bytes_read = 0
                self.decoder = None
                self.at_boundary = True
        
            def read(self, size=65536):
                data = self.source.read(min(size if size >= 0 else 65536, 65536))
                self.bytes_read += len(data)
                if not data:
                    if not self.at_boundary:
                        raise IOError("truncated gzip member")
                    if self.expected_bytes is not None and self.bytes_read != self.expected_bytes:
                        raise IOError("HTTP body length differs from Content-Length")
                    return b""
                pending = data
                while pending:
                    if self.at_boundary:
                        self.decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
                        self.at_boundary = False
                    try:
                        self.decoder.decompress(pending, 65536)
                    except zlib.error as error:
                        raise IOError(f"invalid gzip member: {error}") from error
                    if self.decoder.eof:
                        pending = self.decoder.unused_data
                        self.at_boundary = True
                    else:
                        pending = self.decoder.unconsumed_tail
                return data
        
        
        def parse_warc_records_streaming(stream, max_html_bytes=2 * 1024 * 1024, base_offset=0):
            """Yield every record boundary, including records that cannot be articles.
        
            HTTP content/transfer decoding is streamed by FastWARC. Read at most the
            decoded HTML limit plus one byte before rejecting an oversized payload.
            Transport validation is supplied by the caller's ValidatedGzipStream.
            """
            iterator = ArchiveIterator(
                stream, parse_http=True, auto_decode="all", max_header_len=64 * 1024,
                stream_detect=True, buffer_size=64 * 1024, fsspec_args=False,
            )
            for record in iterator:
                start_offset = base_offset + record.stream_pos
                content_type = (record.http_content_type or "").lower()
                if record.record_type != WarcRecordType.response or (
                    "text/html" not in content_type and "application/xhtml" not in content_type
                ):
                    yield {"skip": "non_html", "start_offset": start_offset}
                    continue
                payload = record.reader.read(max_html_bytes + 1)
                if len(payload) > max_html_bytes:
                    yield {"skip": "oversized_html", "start_offset": start_offset}
                    continue
                yield {
                    "url": record.headers.get("WARC-Target-URI") or "",
                    "warc_date": record.headers.get("WARC-Date"),
                    "content_type": content_type, "charset": record.http_charset,
                    "record_id": record.record_id or record.headers.get("WARC-Record-ID") or "",
                    "raw_bytes": payload, "start_offset": start_offset,
                }
        
        
        def parse_warc_stream_fastwarc(stream, **kwargs):
            yield from parse_warc_records_streaming(stream, **kwargs)
        PY
    ✓ • 0ms

## Assistant

A generated WARC test exposed a more serious issue: the parser can return a partial article from a truncated gzip file without raising an error. I’m adding gzip integrity checks so an interrupted or damaged download cannot be recorded as successfully completed.

## Activity

    $ cat > /tmp/update_warc_db.py <<'PY'
        from pathlib import Path
        p=Path('db/db_handler.py');s=p.read_text().replace('import uuid','import uuid\nimport tempfile\nfrom functools import wraps')
        s=s.replace('from urllib.parse import urlparse','from urllib.parse import urlparse')
        a=s.index('    return {');b=s.index('\n\n\nDB_CONFIG',a)
        s=s[:a]+'''    # Leave absent values to libpq (including .pgpass/service/SSL settings).
            values = {"dbname": os.environ.get("PGDATABASE", "warcdb"),
                      "user": os.environ.get("PGUSER", "warc_user"),
                      "host": os.environ.get("PGHOST", "localhost"),
                      "port": os.environ.get("PGPORT", "5432"),
                      "connect_timeout": int(os.environ.get("PGCONNECT_TIMEOUT", "10"))}
            if "PGPASSWORD" in os.environ:
                values["password"] = os.environ["PGPASSWORD"]
            return values'''+s[b:]
        pos=s.index('\n\n@contextmanager')
        s=s[:pos]+'''
        
        def connection_scope(function):
            """Reuse the coordinator connection, or own a short standalone session."""
            @wraps(function)
            def call(*args, conn=None, **kwargs):
                own = conn is None
                conn = conn or get_connection()
                try:
                    return function(*args, conn=conn, **kwargs)
                finally:
                    # Release read transactions as well as failed writes.
                    if not conn.closed:
                        conn.rollback()
                    if own:
                        conn.close()
            return call
        '''+s[pos:]
        # All ordinary helpers accept a shared connection; save_batch_records already does.
        names=['init_db','create_run','load_run','load_run_files','commit_chunk','finish_run','load_ingest_progress','upsert_ingest_progress']
        for name in names:
         start=s.index('def '+name+'('); end=s.find('\n\ndef ',start+1)
         if end<0:end=s.index('\n\nif __name__',start)
         part=s[start:end]
         line_end=part.index('\n');line=part[:line_end];args=line[len('def '+name+'('):-2]
         part='@connection_scope\ndef '+name+'('+args+(', ' if args else '')+'conn=None):'+part[line_end:]
         part=part.replace('    conn = get_connection()\n','').replace('    finally:\n        conn.close()','    finally:\n        pass')
         s=s[:start]+part+s[end:]
        # Version migration ledger and only run DDL once.
        s=s.replace('            cur.execute(ddl)', '''            cur.execute("CREATE TABLE IF NOT EXISTS ingest_schema_versions (version INT PRIMARY KEY, applied_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP)")
                    cur.execute("SELECT pg_advisory_xact_lock(782936402)")
                    cur.execute("SELECT 1 FROM ingest_schema_versions WHERE version=2")
                    if not cur.fetchone():
                        cur.execute(ddl)
                        cur.execute("INSERT INTO ingest_schema_versions(version) VALUES (2)")''')
        s=s.replace('    ALTER TABLE metadata ALTER COLUMN published_date TYPE TEXT;', '    ALTER TABLE metadata ALTER COLUMN title TYPE TEXT;\n    ALTER TABLE pages ALTER COLUMN url TYPE TEXT;\n    ALTER TABLE metadata ALTER COLUMN published_date TYPE TEXT;')
        # Global lock, on same connection used for every write.
        s=s.replace('hashlib.sha256(manifest_id.encode())','hashlib.sha256(b"spark-warc-ingestion-coordinator")').replace('manifest-scoped advisory lock','global ingestion advisory lock')
        s=s.replace('    return conn\n\n\n@connection_scope','    conn.commit()\n    return conn\n\n\n@connection_scope',1)
        # Normalize/dedupe before insert and tolerate compatibility inputs.
        s=s.replace('    domains = sorted(', '''    unique = {}
            for record in records:
                unique.setdefault(record["record_id"], record)
            records = list(unique.values())
            domains = sorted(''',1).replace('r["file_url"], r.get("warc_date")','r.get("file_url"), r.get("warc_date")')
        # Cursor verification, failure results never move checkpoint.
        s=s.replace('def commit_chunk(run_id, result, conn=None):','def commit_chunk(run_id, result, batch_size=25, conn=None):')
        s=s.replace('SELECT inserted_count FROM ingest_run_files WHERE run_id=%s AND file_url=%s FOR UPDATE','SELECT inserted_count,next_offset FROM ingest_run_files WHERE run_id=%s AND file_url=%s FOR UPDATE')
        s=s.replace('            file_done = cur.fetchone()[0]', '''            file_done, cursor = cur.fetchone()
                    if cursor != result["start_offset"]:
                        raise ValueError("stale chunk cursor; refusing to advance checkpoint")
                    if result.get("error") and (result["candidates"] or result["eof"] or result["next_offset"] != cursor):
                        raise ValueError("failed chunks cannot carry articles or advance checkpoints")
                    if not result.get("error") and not result["eof"] and result["next_offset"] <= cursor:
                        raise ValueError("chunk made no cursor progress")''')
        s=s.replace('            inserted_count = len(_insert_new_records(cur, candidates))', '''            inserted_count = 0
                    rejected = []
                    for offset in range(0, len(candidates), batch_size):
                        batch = candidates[offset:offset + batch_size]
                        inserted_count += _insert_isolated(cur, batch, rejected)
                    if rejected:
                        result.setdefault("stats", {})["invalid_database_rows"] = len(rejected)
                        _write_diagnostic(run_id, result["chunk_id"], rejected)''')
        # Failure receipts must not block a later retry at the same offset.
        s=s.replace('            cur.execute("""INSERT INTO ingest_chunks', '            cur.execute("""INSERT INTO ingest_chunks')
        # New helper inserted before commit_chunk decorator.
        pos=s.index('@connection_scope\ndef commit_chunk')
        s=s[:pos]+'''def _write_diagnostic(run_id, chunk_id, rejected):
            directory = os.environ.get("DEAD_LETTER_DIR", "dead_letter")
            os.makedirs(directory, exist_ok=True)
            fd, temporary = tempfile.mkstemp(prefix=".pending-", dir=directory, text=True)
            destination = os.path.join(directory, f"{run_id}-{chunk_id}-{uuid.uuid4().hex}.jsonl")
            try:
                with os.fdopen(fd, "w") as stream:
                    for row in rejected:
                        stream.write(json.dumps(row, ensure_ascii=False, default=str) + "\\n")
                os.replace(temporary, destination)
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
        
        
        def _insert_isolated(cur, batch, rejected):
            cur.execute("SAVEPOINT article_batch")
            try:
                for record in batch:
                    parsed = urlparse(record["url"])
                    if parsed.scheme not in ("http", "https") or not parsed.hostname:
                        raise ValueError("article URL must be an absolute HTTP(S) URL")
                inserted = len(_insert_new_records(cur, batch))
            except (psycopg2.DataError, psycopg2.IntegrityError, ValueError) as error:
                cur.execute("ROLLBACK TO SAVEPOINT article_batch")
                cur.execute("RELEASE SAVEPOINT article_batch")
                if len(batch) == 1:
                    rejected.append({"record": batch[0], "error": str(error)})
                    return 0
                return sum(_insert_isolated(cur, [record], rejected) for record in batch)
            cur.execute("RELEASE SAVEPOINT article_batch")
            return inserted
        
        
        @connection_scope
        def resume_run(run_id, conn=None):
            with _cursor(conn) as cur:
                cur.execute("UPDATE ingest_run_files SET status='pending',last_error=NULL WHERE run_id=%s AND status='failed'", (run_id,))
                cur.execute("UPDATE ingest_runs SET status='running',updated_at=CURRENT_TIMESTAMP WHERE run_id=%s", (run_id,))
            conn.commit()
        
        
        '''+s[pos:]
        p.write_text(s)
        PY
        python3 /tmp/update_warc_db.py
        python3 -m py_compile db/db_handler.py
    ✓ • 125ms

## Activity

    $ cat > /tmp/update_warc_driver.py <<'PY'
        from pathlib import Path
        p=Path('stream_to_db.py');s=p.read_text().replace('import math','import math\nimport resource\nimport uuid')
        s=s.replace('from pyspark.sql import SparkSession\n','')
        s=s.replace('    load_run_files,','    load_run_files,\n    resume_run,')
        s=s.replace('from parsers.parsers import parse_warc_records_streaming','from parsers.parsers import parse_warc_records_streaming, ValidatedGzipStream')
        s=s.replace('text = (raw or "15").strip().lower()','text = ("15" if raw is None else raw).strip().lower()')
        s=s.replace('        "min_word_count": _env_int', '''        "use_trafilatura": os.environ.get("USE_TRAFILATURA", "1") == "1",
                "lingua_min_confidence": float(os.environ.get("LINGUA_MIN_CONFIDENCE", "0.5")),
                "min_word_count": _env_int''')
        s=s.replace('    if config["max_files_per_round"] > 3:', '''    if not 0 <= config["lingua_min_confidence"] <= 1:
                raise ValueError("LINGUA_MIN_CONFIDENCE must be between 0 and 1")
            if os.environ.get("USE_TRAFILATURA", "1") not in ("0", "1"):
                raise ValueError("USE_TRAFILATURA must be 0 or 1")
            if config["max_files_per_round"] > 3:''')
        s=s.replace('def get_spark_session():\n','def get_spark_session():\n    from pyspark.sql import SparkSession\n')
        s=s.replace('''    if isinstance(error, (socket.timeout, TimeoutError, ConnectionError, urllib.error.URLError)):
                return True
            return isinstance(error, urllib.error.HTTPError) and (error.code == 429 or 500 <= error.code < 600)''','''    if isinstance(error, urllib.error.HTTPError):
                return error.code in (408, 429) or 500 <= error.code < 600
            return isinstance(error, (socket.timeout, TimeoutError, ConnectionError, urllib.error.URLError, OSError))''')
        s=s.replace('        total_size = _content_total(response, base_offset, ranged)\n        records', '''        total_size = _content_total(response, base_offset, ranged)
                if start_offset and total_size is not None and start_offset >= total_size:
                    raise IOError("saved cursor lies at or beyond source size")
                length = response.headers.get("Content-Length", "")
                checked_stream = ValidatedGzipStream(response, int(length) if length.isdigit() else None)
                records''').replace('            response,\n            max_html_bytes','            checked_stream,\n            max_html_bytes')
        s=s.replace('"start_offset": start_offset, "next_offset": total_size or start_offset,','"start_offset": start_offset, "next_offset": base_offset + checked_stream.bytes_read,')
        s=s.replace('                next_offset = total_size\n                clean_eof = True','                next_offset = base_offset + checked_stream.bytes_read\n                clean_eof = True')
        s=s.replace('fields = extract_html_fields(current, task["min_word_count"])','fields = extract_html_fields(current, task["min_word_count"], task["use_trafilatura"])')
        s=s.replace('detect_languages_batch([fields["clean_text"]])[0]','detect_languages_batch([fields["clean_text"]], task["lingua_min_confidence"])[0]')
        s=s.replace('            "min_word_count": config["min_word_count"],','            "min_word_count": config["min_word_count"],\n            "use_trafilatura": config["use_trafilatura"],\n            "lingua_min_confidence": config["lingua_min_confidence"],')
        s=s.replace('    tasks = []\n    for index', '    tasks = []\n    if remaining_total is not None and remaining_total <= 0:\n        return tasks\n    for index')
        s=s.replace('            return _process_file_once(task)','''            result = _process_file_once(task)
                    result["stats"]["python_peak_rss_mib"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)
                    result["stats"]["worker_host"] = socket.gethostname()
                    result["stats"]["worker_pid"] = os.getpid()
                    result["stats"]["attempts"] = attempt + 1
                    return result''')
        a=s.index('def run_streaming_pipeline():');b=s.index('\n\nif __name__',a)
        s=s[:a]+'''SEMANTIC_ENV = {
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
            with conn.cursor() as cur:
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
            try:
                if config["resume_run_id"]:
                    run = load_run(config["resume_run_id"], conn=lock_conn)
                    restore_run_config(config, run)
                    run_id = run["run_id"]
                    resume_run(run_id, conn=lock_conn)
                    print(f"Resuming run {run_id}: {run['inserted_count']} committed")
                else:
                    urls = fetch_manifest(config)
                    if not urls:
                        print("No WARC files were selected.")
                        return 2
                    persisted = {key: config[key] for key in SEMANTIC_ENV}
                    run_id = create_run(config["manifest_id"], urls, config["target_articles"],
                                        config["per_file_target"], persisted, conn=lock_conn)
                    print(f"Created ingestion run {run_id}")
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
                        print(f"Wave {wave}: committed {current['inserted_count']:,}/"
                              f"{current['target_articles'] or 'unlimited'}; new={wave_inserted:,}; "
                              f"worker peak RSS MiB={[r['stats'].get('python_peak_rss_mib') for r in results]}")
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
                    if spark is not None:
                        spark.stop()
                finally:
                    lock_conn.close()
        '''+s[b:]
        p.write_text(s)
        PY
        python3 /tmp/update_warc_driver.py
        python3 -m py_compile stream_to_db.py parsers/parsers.py extractors/extractors.py utils.py rag_loader.py
    ✓ • 0ms

## Activity

    $ cat > run_to_db.sh <<'SH'
        #!/usr/bin/env bash
        set -euo pipefail
        PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
        cd "$PROJECT_ROOT"
        VENV_DIR="${VENV_DIR:-$PROJECT_ROOT/.venv}"
        if [ ! -x "$VENV_DIR/bin/python" ]; then
            echo "Missing virtual environment: $VENV_DIR. See README.md setup instructions." >&2
            exit 1
        fi
        export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
        # Validate before packaging, network access, database access, or Spark startup.
        "$VENV_DIR/bin/python" -c 'from stream_to_db import load_config; load_config()'
        if [ "${DRY_RUN:-0}" = 1 ]; then
            exec "$VENV_DIR/bin/python" stream_to_db.py
        fi
        TASK_TMP="$(mktemp -d)"
        trap 'rm -rf "$TASK_TMP"' EXIT
        ZIP="$TASK_TMP/project_code.zip"
        zip -qr "$ZIP" extractors parsers db utils.py -x '*/__pycache__/*' '*.pyc'
        
        # Hash installed distributions as well as declared dependencies and Python.
        VENV_FINGERPRINT="$(
            {
                cat requirements.txt "$VENV_DIR/pyvenv.cfg"
                "$VENV_DIR/bin/python" -m pip freeze --all
                "$VENV_DIR/bin/python" -c 'import sys; print(sys.version); print(sys.executable)'
            } | sha256sum | cut -d ' ' -f 1
        )"
        VENV_ARCHIVE="$PROJECT_ROOT/pyspark_venv-${VENV_FINGERPRINT}.tar.gz"
        if [ ! -f "$VENV_ARCHIVE" ]; then
            echo "Packing worker environment..."
            "$VENV_DIR/bin/python" -m venv_pack -p "$VENV_DIR" -o "$TASK_TMP/environment.tar.gz"
            mv "$TASK_TMP/environment.tar.gz" "$VENV_ARCHIVE"
        fi
        ARCHIVES_SPEC="$VENV_ARCHIVE#environment"
        HDFS_APPS_DIR="${HDFS_APPS_DIR:-/user/$USER/apps/spark}"
        EXTRA_CONF=()
        
        publish_hdfs() {
            local source="$1" destination="$2" temporary="$2.upload-$(basename "$TASK_TMP")"
            if hdfs dfs -test -e "$destination" 2>/dev/null; then return 0; fi
            hdfs dfs -mkdir -p "$HDFS_APPS_DIR" || return 1
            hdfs dfs -put "$source" "$temporary" || return 1
            if hdfs dfs -mv "$temporary" "$destination"; then return 0; fi
            hdfs dfs -rm -f "$temporary" >/dev/null 2>&1 || true
            hdfs dfs -test -e "$destination"
        }
        
        if [ "${USE_HDFS_CACHE:-1}" = 1 ] && hdfs dfs -test -e / >/dev/null 2>&1; then
            VENV_HASH="$(sha256sum "$VENV_ARCHIVE" | cut -d ' ' -f 1)"
            HDFS_VENV="$HDFS_APPS_DIR/pyspark_venv-$VENV_HASH.tar.gz"
            if publish_hdfs "$VENV_ARCHIVE" "$HDFS_VENV"; then
                ARCHIVES_SPEC="hdfs://$HDFS_VENV#environment"
            fi
            : "${SPARK_HOME:?Set SPARK_HOME to the cluster Spark installation}"
            JARS_HASH="$(find "$SPARK_HOME/jars" -maxdepth 1 -name '*.jar' -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum | cut -d ' ' -f 1)"
            JARS_ARCHIVE="$PROJECT_ROOT/spark-libs-$JARS_HASH.zip"
            if [ ! -f "$JARS_ARCHIVE" ]; then
                (cd "$SPARK_HOME/jars" && zip -qr "$TASK_TMP/spark-libs.zip" .)
                mv "$TASK_TMP/spark-libs.zip" "$JARS_ARCHIVE"
            fi
            HDFS_JARS="$HDFS_APPS_DIR/spark-libs-$JARS_HASH.zip"
            if publish_hdfs "$JARS_ARCHIVE" "$HDFS_JARS"; then
                EXTRA_CONF+=(--conf "spark.yarn.archive=hdfs://$HDFS_JARS")
            fi
        fi
        export PYSPARK_DRIVER_PYTHON="$VENV_DIR/bin/python"
        export PYSPARK_PYTHON="./environment/bin/python"
        spark-submit \
            --master yarn --deploy-mode client \
            --driver-memory "${SPARK_DRIVER_MEMORY:-512m}" \
            --executor-memory "${SPARK_EXECUTOR_MEMORY:-512m}" \
            --conf "spark.executor.memoryOverhead=${SPARK_EXECUTOR_MEMORY_OVERHEAD:-512m}" \
            --conf spark.executor.cores=1 \
            --conf spark.executor.instances=3 \
            --conf spark.dynamicAllocation.enabled=false \
            --conf spark.driver.maxResultSize=64m \
            --conf spark.executorEnv.RAYON_NUM_THREADS=1 \
            --conf spark.executorEnv.OMP_NUM_THREADS=1 \
            --conf spark.executorEnv.OPENBLAS_NUM_THREADS=1 \
            --conf "spark.pyspark.driver.python=$VENV_DIR/bin/python" \
            --conf "spark.pyspark.python=$PYSPARK_PYTHON" \
            "${EXTRA_CONF[@]}" --archives "$ARCHIVES_SPEC" --py-files "$ZIP" stream_to_db.py
        SH
        cat > requirements.txt <<'TXT'
        # Direct ingestion dependencies. Use the cluster's PySpark, not a second pip copy.
        FastWARC==1.0.9
        charset-normalizer>=3.4,<4
        lingua-language-detector==2.2.0
        psycopg2-binary>=2.9,<3
        selectolax>=0.3,<0.5
        trafilatura>=2,<3
        venv-pack==0.2.0
        TXT
        cat > requirements-rag.txt <<'TXT'
        -r requirements.txt
        langchain-core>=1,<2
        langchain-text-splitters>=1,<2
        TXT
        cat > requirements-dev.txt <<'TXT'
        -r requirements.txt
        warcio>=1.7,<2
        TXT
        cat >> .gitignore <<'TXT'
        pyspark_venv-*.tar.gz
        spark-libs-*.zip
        TXT
        bash -n run_to_db.sh
        ../spark_warc_project/.venv/bin/python -m py_compile stream_to_db.py db/db_handler.py
    ✓ • 0ms

## Assistant

The resume path now reloads the run’s saved quotas and filters, retries failed files, and rejects conflicting overrides. I’ve also wired `DB_BATCH_SIZE` into database writes and fixed dependency packaging. Next I’m testing these behaviors with generated WARC files and a disposable PostgreSQL database.

## Activity

    $ /usr/lib/postgresql/18/bin/initdb -D /tmp/warc-v2-test-pg -A trust --no-locale -E UTF8
    The files belonging to this database system will be owned by user "hadoop".
    This user must also own the server process.
    
    The database cluster will be initialized with locale "C".
    The default text search configuration will be set to "english".
    
    Data page checksums are enabled.
    
    creating directory /tmp/warc-v2-test-pg ... ok
    creating subdirectories ... ok
    selecting dynamic shared memory implementation ... posix
    selecting default "max_connections" ... 100
    selecting default "shared_buffers" ... 128MB
    selecting default time zone ... Africa/Cairo
    creating configuration files ... ok
    running bootstrap script ... ok
    performing post-bootstrap initialization ... ok
    syncing data to disk ... ok
    
    Success. You can now start the database server using:
    
        /usr/lib/postgresql/18/bin/pg_ctl -D /tmp/warc-v2-test-pg -l logfile start
    
    ✓ • 1.14s

## Activity

    $ /usr/lib/postgresql/18/bin/pg_ctl -D /tmp/warc-v2-test-pg -l /tmp/warc-v2-test-pg.log -o '-k /tmp/warc-v2-test-pg -p 55439 -c listen_addresses=127.0.0.1 -c shared_buffers=16MB' start
    waiting for server to start.... stopped waiting
    pg_ctl: could not start server
    Examine the log output.
    ✗ (1) • 21ms

## Activity

    $ cat /tmp/warc-v2-test-pg.log
    2026-09-30 11:09:06.842 EEST [5] LOG:  starting PostgreSQL 18.6 (Debian 18.6-1.pgdg13+2) on x86_64-pc-linux-gnu, compiled by gcc (Debian 14.2.0-19) 14.2.0, 64-bit
    2026-09-30 11:09:06.842 EEST [5] LOG:  could not create IPv4 socket for address "127.0.0.1": Operation not permitted
    2026-09-30 11:09:06.842 EEST [5] WARNING:  could not create listen socket for "127.0.0.1"
    2026-09-30 11:09:06.857 EEST [5] FATAL:  could not create any TCP/IP sockets
    2026-09-30 11:09:06.858 EEST [5] LOG:  database system is shut down
    ✓ • 0ms

## Activity

    $ /usr/lib/postgresql/18/bin/pg_ctl -D /tmp/warc-v2-test-pg -l /tmp/warc-v2-test-pg.log -o '-k /tmp/warc-v2-test-pg -p 55439 -c listen_addresses=127.0.0.1 -c shared_buffers=16MB' start
    waiting for server to start.... done
    server started
    ✓ • 0ms

## Activity

    $ cat > tests/test_ingestion.py <<'PY'
        """Run with python -m unittest discover -s tests -v.
        
        Set WARC_TEST_DSN to a disposable database for PostgreSQL integration tests.
        Each test creates and drops its own schema; production tables are untouched.
        """
        import copy
        import gzip
        import io
        import json
        import os
        import tempfile
        import unittest
        import uuid
        from unittest.mock import patch
        
        from warcio.warcwriter import WARCWriter
        from warcio.statusandheaders import StatusAndHeaders
        import psycopg2
        
        import stream_to_db as job
        from db import db_handler as db
        from parsers.parsers import parse_warc_records_streaming, ValidatedGzipStream
        from extractors.extractors import extract_html_fields, _language_sample
        from utils import decode_and_validate
        
        
        def make_warc(count=6, payload=None, content_type='text/html', http_encoding=None):
            output = io.BytesIO()
            writer = WARCWriter(output, gzip=True)
            offsets = []
            for i in range(count):
                offsets.append(output.tell())
                body = payload if payload is not None else ('<html><body><p>' + ('English article number %s. ' % i) * 100 + '</p></body></html>').encode()
                headers = [('Content-Type', content_type)]
                if http_encoding:
                    headers.append(('Content-Encoding', http_encoding))
                record = writer.create_warc_record('https://example.com/article/' + str(i), 'response',
                    payload=io.BytesIO(body), http_headers=StatusAndHeaders('200 OK', headers, protocol='HTTP/1.1'))
                writer.write_record(record)
            return output.getvalue(), offsets
        
        
        class Response(io.BytesIO):
            def __init__(self, data, offset=0, ranged=True, size=True):
                super().__init__(data[offset:] if ranged else data)
                self.status = 206 if offset and ranged else 200
                self.headers = {'ETag': 'fixture-v1'}
                if size:
                    self.headers['Content-Length'] = str(len(data) - offset if ranged else len(data))
                if self.status == 206:
                    self.headers['Content-Range'] = f'bytes {offset}-{len(data)-1}/{len(data)}'
        
        
        def config(**kwargs):
            with patch.dict(os.environ, {}, clear=True):
                result = job.load_config()
            result.update(kwargs)
            return result
        
        
        def task(**kwargs):
            result = dict(file_url='https://example.com/test.warc.gz', start_offset=0,
                          chunk_id=uuid.uuid4().hex, candidate_limit=2, max_result_bytes=4*1024*1024,
                          max_input_bytes=32*1024*1024, max_seconds=120, max_html_bytes=2*1024*1024,
                          max_article_bytes=512*1024, min_word_count=10, max_retries=1,
                          use_trafilatura=False, lingua_min_confidence=.5)
            result.update(kwargs)
            return result
        
        
        def worker(data, work=None, ranged=True, language='en', size=True):
            work = work or task()
            with patch.object(job.urllib.request, 'urlopen', return_value=Response(data, work['start_offset'], ranged, size)), \
                 patch.object(job, 'detect_languages_batch', return_value=[language]):
                return job.process_file_chunk(work)
        
        
        def candidate(record_id='one', **kwargs):
            result = dict(record_id=record_id, url='https://www.example.com/news', file_url='file-1',
                          cleaned_text='Article text', author='Author', language='en', headings=[], word_count=2)
            result.update(kwargs)
            return result
        
        
        def chunk(candidates=None, start=0, end=100, eof=False, error=None, file='file-1'):
            return dict(chunk_id=uuid.uuid4().hex, file_url=file, start_offset=start, next_offset=end,
                        candidates=[candidate()] if candidates is None else candidates, eof=eof,
                        stats={}, error=error)
        
        
        class UnitTests(unittest.TestCase):
            def test_defaults_and_validation(self):
                self.assertEqual(config()['num_files'], 15)
                self.assertIsNone(job._parse_num_files(''))
                for setting, value in [('MAX_ACCEPTED_ARTICLES', '-1'), ('MAX_FILES_PER_ROUND', '0'),
                                       ('LINGUA_MIN_CONFIDENCE', 'nan'), ('MAX_RETRIES', '0'),
                                       ('MAX_EXTRACTED_PER_ROUND', '50')]:
                    with patch.dict(os.environ, {setting: value}, clear=True), self.assertRaises(ValueError):
                        job.load_config()
                self.assertFalse(job._transient(job.urllib.error.HTTPError('x', 404, 'missing', {}, None)))
                self.assertTrue(job._transient(job.urllib.error.HTTPError('x', 503, 'unavailable', {}, None)))
        
            def test_allocations_respect_total_and_per_file(self):
                files = [dict(file_url=str(i), status='pending', eof=False, next_offset=0,
                              inserted_count=i, etag=None, last_modified=None) for i in range(3)]
                for total in (1, 2, 3, 7, 1000):
                    run = dict(run_id='id', target_articles=total, inserted_count=0, per_file_target=4)
                    tasks = job._allocate_tasks(config(), run, files, 0)
                    self.assertLessEqual(sum(t['candidate_limit'] for t in tasks), total)
                    for t in tasks:
                        self.assertLessEqual(t['candidate_limit'], 4-int(t['file_url']))
                run['inserted_count'] = run['target_articles']
                self.assertEqual(job._allocate_tasks(config(), run, files, 0), [])
        
            def test_resume_restores_and_rejects_conflicting_filters(self):
                run = dict(manifest_id='2025/03', target_articles=7, per_file_target=3,
                           config=dict(min_word_count=123, use_trafilatura=False))
                with patch.dict(os.environ, {}, clear=True):
                    restored = job.restore_run_config(config(), run)
                self.assertEqual((restored['year'], restored['month'], restored['min_word_count']), ('2025', '03', 123))
                with patch.dict(os.environ, {'MAX_ACCEPTED_ARTICLES': '9'}, clear=True), self.assertRaises(ValueError):
                    job.restore_run_config(config(target_articles=9), run)
        
            def test_french_encoding_and_jsonld(self):
                prose = 'Les élèves français étudient les événements récents et découvrent une société développée. ' * 20
                html = ('<html><script type="application/ld+json">' + json.dumps({'@graph':[{'author':{'name':'Émile'}, 'datePublished':'2026-05-01'}]}) + '</script><body>' + prose + '</body></html>').encode()
                fields = extract_html_fields(dict(raw_bytes=html, url='https://example.com', warc_date=None), 10, False)
                self.assertEqual(fields['author'], 'Émile')
                self.assertEqual(fields['published_date'], '2026-05-01')
                self.assertIn('élèves', fields['clean_text'])
                self.assertEqual(decode_and_validate(prose.encode('cp1252'), 'cp1252')[1], 'success')
        
            def test_language_sample_has_no_overlap(self):
                text = ''.join(chr(0x1000+i) for i in range(2001))
                sample = _language_sample(text).replace(' ', '')
                self.assertEqual(len(sample), 2000)
                self.assertEqual(len(set(sample)), 2000)
        
            def test_small_chunks_advance_without_loss(self):
                data, offsets = make_warc()
                result = worker(data)
                self.assertEqual(result['next_offset'], offsets[2])
                second = worker(data, task(start_offset=result['next_offset']))
                third = worker(data, task(start_offset=second['next_offset']))
                self.assertEqual(len(result['candidates']+second['candidates']+third['candidates']), 6)
                self.assertTrue(third['eof'])
                self.assertEqual(third['next_offset'], len(data))
        
            def test_ignored_range_and_unknown_length(self):
                data, offsets = make_warc(4)
                result = worker(data, task(start_offset=offsets[2]), ranged=False, size=False)
                self.assertIsNone(result['error'])
                self.assertEqual(len(result['candidates']), 2)
                self.assertEqual(result['next_offset'], len(data))
                self.assertTrue(result['eof'])
        
            def test_empty_and_rejected_files_advance(self):
                data, _ = make_warc()
                result = worker(data, language='other')
                self.assertEqual(result['candidates'], [])
                self.assertTrue(result['eof'])
                self.assertEqual(result['next_offset'], len(data))
                result = worker(b'')
                self.assertTrue(result['eof'])
        
            def test_corrupt_or_truncated_gzip_never_marks_eof(self):
                data, _ = make_warc(2)
                corrupt = bytearray(data); corrupt[-6] ^= 255
                for broken in (data[:-15], bytes(corrupt), data+b'junk'):
                    result = worker(broken, task(candidate_limit=100))
                    self.assertTrue(result['error'])
                    self.assertFalse(result['eof'])
                    self.assertEqual(result['next_offset'], 0)
                    self.assertEqual(result['candidates'], [])
        
            def test_oversize_decoded_http_body_is_skipped(self):
                data, _ = make_warc(1, payload=gzip.compress(b'x'*100000), http_encoding='gzip')
                result = worker(data, task(max_html_bytes=1024))
                self.assertIsNone(result['error'])
                self.assertEqual(result['stats']['oversized_html'], 1)
                self.assertEqual(result['candidates'], [])
        
            def test_result_budget_revisits_unreturned_record(self):
                data, offsets = make_warc(3)
                first = worker(data, task(candidate_limit=1))
                size = len(json.dumps(first['candidates'][0], ensure_ascii=False, default=str).encode())
                result = worker(data, task(candidate_limit=100, max_result_bytes=size+50, max_article_bytes=size+50))
                self.assertIsNone(result['error'])
                self.assertEqual(len(result['candidates']), 1)
                self.assertEqual(result['next_offset'], offsets[1])
        
        
        @unittest.skipUnless(os.environ.get('WARC_TEST_DSN'), 'set WARC_TEST_DSN to enable PostgreSQL tests')
        class DatabaseTests(unittest.TestCase):
            def setUp(self):
                self.dsn = os.environ['WARC_TEST_DSN']
                self.schema = 'warc_test_' + uuid.uuid4().hex
                self.admin = psycopg2.connect(self.dsn)
                self.admin.autocommit = True
                with self.admin.cursor() as cur:
                    cur.execute('CREATE SCHEMA ' + self.schema)
                def connect():
                    return psycopg2.connect(self.dsn, options='-c search_path='+self.schema)
                self.connect = connect
                self.patch = patch.object(db, 'get_connection', side_effect=connect)
                self.patch.start()
                self.temp = tempfile.TemporaryDirectory()
                self.env = patch.dict(os.environ, {'DEAD_LETTER_DIR':self.temp.name})
                self.env.start()
                db.init_db()
                self.run_id = db.create_run('2026/05', ['file-1', 'file-2'], 3, 2, {})
        
            def tearDown(self):
                self.patch.stop(); self.env.stop(); self.temp.cleanup()
                with self.admin.cursor() as cur:
                    cur.execute('DROP SCHEMA ' + self.schema + ' CASCADE')
                self.admin.close()
        
            def test_exact_caps_duplicates_and_idempotent_receipt(self):
                first = chunk([candidate('a'), candidate('b')])
                self.assertEqual(db.commit_chunk(self.run_id, first, batch_size=1), 2)
                self.assertEqual(db.commit_chunk(self.run_id, first), 2)
                self.assertEqual(db.load_run(self.run_id)['inserted_count'], 2)
                duplicate = chunk([candidate('a')], file='file-2')
                self.assertEqual(db.commit_chunk(self.run_id, duplicate), 0)
                last = chunk([candidate('c')], file='file-2', start=100, end=200)
                self.assertEqual(db.commit_chunk(self.run_id, last), 1)
                self.assertEqual(db.load_run(self.run_id)['inserted_count'], 3)
                self.assertEqual(db.load_run_files(self.run_id)[0]['status'], 'quota_reached')
        
            def test_batch_duplicate_ids(self):
                result = chunk([candidate('a'), candidate('a')])
                self.assertEqual(db.commit_chunk(self.run_id, result), 1)
        
            def test_content_error_rolls_back_cursor_and_rows(self):
                original = db._insert_new_records
                def broken(cur, records):
                    original(cur, records)
                    raise RuntimeError('simulated write failure')
                with patch.object(db, '_insert_new_records', side_effect=broken), self.assertRaises(RuntimeError):
                    db.commit_chunk(self.run_id, chunk())
                self.assertEqual(db.load_run(self.run_id)['inserted_count'], 0)
                self.assertEqual(db.load_run_files(self.run_id)[0]['next_offset'], 0)
                with self.connect() as conn, conn.cursor() as cur:
                    cur.execute('SELECT count(*) FROM pages')
                    self.assertEqual(cur.fetchone()[0], 0)
        
            def test_malformed_row_isolated(self):
                result = chunk([candidate('bad', url='not a URL'), candidate('good')])
                self.assertEqual(db.commit_chunk(self.run_id, result), 1)
                self.assertEqual(result['stats']['invalid_database_rows'], 1)
                self.assertEqual(len(os.listdir(self.temp.name)), 1)
        
            def test_uncertain_commit_recovered_after_reconnection(self):
                result = chunk()
                real = self.connect()
                class LostAcknowledgement:
                    def __getattr__(self, name): return getattr(real, name)
                    def commit(self):
                        real.commit()
                        raise psycopg2.OperationalError('lost commit acknowledgement')
                try:
                    with self.assertRaises(psycopg2.OperationalError):
                        db.commit_chunk(self.run_id, result, conn=LostAcknowledgement())
                finally:
                    real.close()
                self.assertEqual(db.commit_chunk(self.run_id, result), 1)
                self.assertEqual(db.load_run(self.run_id)['inserted_count'], 1)
        
            def test_failed_file_retries_on_resume(self):
                result = chunk([], end=0, error='timeout')
                self.assertEqual(db.commit_chunk(self.run_id, result), 0)
                self.assertEqual(db.load_run_files(self.run_id)[0]['status'], 'failed')
                db.resume_run(self.run_id)
                self.assertEqual(db.load_run_files(self.run_id)[0]['status'], 'pending')
                self.assertEqual(db.commit_chunk(self.run_id, chunk()), 1)
        
            def test_stale_and_stalled_cursors_rejected(self):
                with self.assertRaises(ValueError): db.commit_chunk(self.run_id, chunk(start=5))
                with self.assertRaises(ValueError): db.commit_chunk(self.run_id, chunk([], end=0))
        
            def test_lock_excludes_second_coordinator(self):
                first = db.acquire_coordinator_lock('2026/05')
                try:
                    with self.assertRaises(RuntimeError): db.acquire_coordinator_lock('2026/06')
                finally:
                    first.close()
        
            def test_legacy_complete_preserved_partial_restarted(self):
                db.upsert_ingest_progress('2026/05', 'file-1', 99, 10, True)
                db.upsert_ingest_progress('2026/05', 'file-2', 88, 10, False)
                db.init_db()
                run = db.create_run('2026/05', ['file-1','file-2'], 5, 0, {})
                files = db.load_run_files(run)
                self.assertTrue(files[0]['eof'])
                self.assertEqual(files[1]['next_offset'], 0)
        
            def test_driver_shortfall_failure_and_resume(self):
                class RDD:
                    def __init__(self, data): self.data = data
                    def map(self, fn): return RDD([fn(row) for row in self.data])
                    def collect(self): return self.data
                class Spark:
                    def __init__(self): self.sparkContext = self
                    def setLogLevel(self, level): pass
                    def parallelize(self, data, size): return RDD(data)
                    def stop(self): pass
                def failed_task(t):
                    return dict(chunk_id=t['chunk_id'],file_url=t['file_url'],start_offset=t['start_offset'],
                                next_offset=t['start_offset'],candidates=[],stats={},eof=False,error='timeout')
                def eof_task(t):
                    result = failed_task(t)
                    result.update(next_offset=100,eof=True,error=None)
                    return result
                with patch.object(job,'load_config',return_value=config(resume_run_id=self.run_id)), \
                     patch.object(job,'get_spark_session',return_value=Spark()), \
                     patch.object(job,'process_file_chunk',side_effect=failed_task):
                    self.assertEqual(job.run_streaming_pipeline(),1)
                with patch.object(job,'load_config',return_value=config(resume_run_id=self.run_id)), \
                     patch.object(job,'get_spark_session',return_value=Spark()), \
                     patch.object(job,'process_file_chunk',side_effect=eof_task):
                    self.assertEqual(job.run_streaming_pipeline(),2)
        
        
        if __name__ == '__main__':
            unittest.main()
        PY
        WARC_TEST_DSN='host=/tmp/warc-v2-test-pg port=55439 dbname=postgres user=hadoop' ../spark_warc_project/.venv/bin/python -m unittest discover -s tests -v
    test_batch_duplicate_ids (test_ingestion.DatabaseTests.test_batch_duplicate_ids) ... ERROR
    test_content_error_rolls_back_cursor_and_rows (test_ingestion.DatabaseTests.test_content_error_rolls_back_cursor_and_rows) ... ERROR
    test_driver_shortfall_failure_and_resume (test_ingestion.DatabaseTests.test_driver_shortfall_failure_and_resume) ... ERROR
    test_exact_caps_duplicates_and_idempotent_receipt (test_ingestion.DatabaseTests.test_exact_caps_duplicates_and_idempotent_receipt) ... ERROR
    test_failed_file_retries_on_resume (test_ingestion.DatabaseTests.test_failed_file_retries_on_resume) ... ERROR
    test_legacy_complete_preserved_partial_restarted (test_ingestion.DatabaseTests.test_legacy_complete_preserved_partial_restarted) ... ERROR
    test_lock_excludes_second_coordinator (test_ingestion.DatabaseTests.test_lock_excludes_second_coordinator) ... ERROR
    test_malformed_row_isolated (test_ingestion.DatabaseTests.test_malformed_row_isolated) ... ERROR
    test_stale_and_stalled_cursors_rejected (test_ingestion.DatabaseTests.test_stale_and_stalled_cursors_rejected) ... ERROR
    test_uncertain_commit_recovered_after_reconnection (test_ingestion.DatabaseTests.test_uncertain_commit_recovered_after_reconnection) ... ERROR
    test_allocations_respect_total_and_per_file (test_ingestion.UnitTests.test_allocations_respect_total_and_per_file) ... ok
    test_corrupt_or_truncated_gzip_never_marks_eof (test_ingestion.UnitTests.test_corrupt_or_truncated_gzip_never_marks_eof) ... /home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py:37: ResourceWarning: Unclosed file <tempfile.SpooledTemporaryFile object at 0x7fbe869a40a0>
      record = writer.create_warc_record('https://example.com/article/' + str(i), 'response',
    ResourceWarning: Enable tracemalloc to get the object allocation traceback
    /home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py:167: ResourceWarning: Unclosed file <tempfile.SpooledTemporaryFile object at 0x7fbe86933c70>
      data, _ = make_warc(2)
    ResourceWarning: Enable tracemalloc to get the object allocation traceback
    
    thread '<unnamed>' (2) panicked at fastwarc-rs/src/warc/record.rs:458:62:
    called `Result::unwrap()` on an `Err` value: Custom { kind: Other, error: PyErr { type: <class 'AttributeError'>, value: AttributeError("'ValidatedGzipStream' object has no attribute 'tell'"), traceback: None } }
    note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
    ERROR
    test_defaults_and_validation (test_ingestion.UnitTests.test_defaults_and_validation) ... ok
    test_empty_and_rejected_files_advance (test_ingestion.UnitTests.test_empty_and_rejected_files_advance) ... /home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py:37: ResourceWarning: Unclosed file <tempfile.SpooledTemporaryFile object at 0x7fbe8695c490>
      record = writer.create_warc_record('https://example.com/article/' + str(i), 'response',
    ResourceWarning: Enable tracemalloc to get the object allocation traceback
    /home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py:37: ResourceWarning: Unclosed file <tempfile.SpooledTemporaryFile object at 0x7fbe89013ac0>
      record = writer.create_warc_record('https://example.com/article/' + str(i), 'response',
    ResourceWarning: Enable tracemalloc to get the object allocation traceback
    /home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py:37: ResourceWarning: Unclosed file <tempfile.SpooledTemporaryFile object at 0x7fbe877b2440>
      record = writer.create_warc_record('https://example.com/article/' + str(i), 'response',
    ResourceWarning: Enable tracemalloc to get the object allocation traceback
    /home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py:37: ResourceWarning: Unclosed file <tempfile.SpooledTemporaryFile object at 0x7fbe869dc790>
      record = writer.create_warc_record('https://example.com/article/' + str(i), 'response',
    ResourceWarning: Enable tracemalloc to get the object allocation traceback
    /home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py:158: ResourceWarning: Unclosed file <tempfile.SpooledTemporaryFile object at 0x7fbe89013ac0>
      data, _ = make_warc()
    ResourceWarning: Enable tracemalloc to get the object allocation traceback
    
    thread '<unnamed>' (2) panicked at fastwarc-rs/src/warc/record.rs:458:62:
    called `Result::unwrap()` on an `Err` value: Custom { kind: Other, error: PyErr { type: <class 'AttributeError'>, value: AttributeError("'ValidatedGzipStream' object has no attribute 'tell'"), traceback: None } }
    ERROR
    test_french_encoding_and_jsonld (test_ingestion.UnitTests.test_french_encoding_and_jsonld) ... ok
    test_ignored_range_and_unknown_length (test_ingestion.UnitTests.test_ignored_range_and_unknown_length) ... /home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py:37: ResourceWarning: Unclosed file <tempfile.SpooledTemporaryFile object at 0x7fbe85d055a0>
      record = writer.create_warc_record('https://example.com/article/' + str(i), 'response',
    ResourceWarning: Enable tracemalloc to get the object allocation traceback
    /home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py:37: ResourceWarning: Unclosed file <tempfile.SpooledTemporaryFile object at 0x7fbe85d04dc0>
      record = writer.create_warc_record('https://example.com/article/' + str(i), 'response',
    ResourceWarning: Enable tracemalloc to get the object allocation traceback
    /home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py:37: ResourceWarning: Unclosed file <tempfile.SpooledTemporaryFile object at 0x7fbe85d056f0>
      record = writer.create_warc_record('https://example.com/article/' + str(i), 'response',
    ResourceWarning: Enable tracemalloc to get the object allocation traceback
    /home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py:150: ResourceWarning: Unclosed file <tempfile.SpooledTemporaryFile object at 0x7fbe85d05690>
      data, offsets = make_warc(4)
    ResourceWarning: Enable tracemalloc to get the object allocation traceback
    
    thread '<unnamed>' (2) panicked at fastwarc-rs/src/warc/record.rs:458:62:
    called `Result::unwrap()` on an `Err` value: Custom { kind: Other, error: PyErr { type: <class 'AttributeError'>, value: AttributeError("'ValidatedGzipStream' object has no attribute 'tell'"), traceback: None } }
    ERROR
    test_language_sample_has_no_overlap (test_ingestion.UnitTests.test_language_sample_has_no_overlap) ... ok
    test_oversize_decoded_http_body_is_skipped (test_ingestion.UnitTests.test_oversize_decoded_http_body_is_skipped) ... /home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py:177: ResourceWarning: Unclosed file <tempfile.SpooledTemporaryFile object at 0x7fbe85d059f0>
      data, _ = make_warc(1, payload=gzip.compress(b'x'*100000), http_encoding='gzip')
    ResourceWarning: Enable tracemalloc to get the object allocation traceback
    
    thread '<unnamed>' (2) panicked at fastwarc-rs/src/warc/record.rs:458:62:
    called `Result::unwrap()` on an `Err` value: Custom { kind: Other, error: PyErr { type: <class 'AttributeError'>, value: AttributeError("'ValidatedGzipStream' object has no attribute 'tell'"), traceback: None } }
    ERROR
    test_result_budget_revisits_unreturned_record (test_ingestion.UnitTests.test_result_budget_revisits_unreturned_record) ... /home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py:37: ResourceWarning: Unclosed file <tempfile.SpooledTemporaryFile object at 0x7fbe869dc280>
      record = writer.create_warc_record('https://example.com/article/' + str(i), 'response',
    ResourceWarning: Enable tracemalloc to get the object allocation traceback
    /home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py:37: ResourceWarning: Unclosed file <tempfile.SpooledTemporaryFile object at 0x7fbe85d05cc0>
      record = writer.create_warc_record('https://example.com/article/' + str(i), 'response',
    ResourceWarning: Enable tracemalloc to get the object allocation traceback
    /home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py:184: ResourceWarning: Unclosed file <tempfile.SpooledTemporaryFile object at 0x7fbe869dc280>
      data, offsets = make_warc(3)
    ResourceWarning: Enable tracemalloc to get the object allocation traceback
    
    thread '<unnamed>' (2) panicked at fastwarc-rs/src/warc/record.rs:458:62:
    called `Result::unwrap()` on an `Err` value: Custom { kind: Other, error: PyErr { type: <class 'AttributeError'>, value: AttributeError("'ValidatedGzipStream' object has no attribute 'tell'"), traceback: None } }
    ERROR
    test_resume_restores_and_rejects_conflicting_filters (test_ingestion.UnitTests.test_resume_restores_and_rejects_conflicting_filters) ... ok
    test_small_chunks_advance_without_loss (test_ingestion.UnitTests.test_small_chunks_advance_without_loss) ... /home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py:37: ResourceWarning: Unclosed file <tempfile.SpooledTemporaryFile object at 0x7fbe890303d0>
      record = writer.create_warc_record('https://example.com/article/' + str(i), 'response',
    ResourceWarning: Enable tracemalloc to get the object allocation traceback
    /home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py:37: ResourceWarning: Unclosed file <tempfile.SpooledTemporaryFile object at 0x7fbe85d05ab0>
      record = writer.create_warc_record('https://example.com/article/' + str(i), 'response',
    ResourceWarning: Enable tracemalloc to get the object allocation traceback
    /home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py:37: ResourceWarning: Unclosed file <tempfile.SpooledTemporaryFile object at 0x7fbe85d05930>
      record = writer.create_warc_record('https://example.com/article/' + str(i), 'response',
    ResourceWarning: Enable tracemalloc to get the object allocation traceback
    /home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py:140: ResourceWarning: Unclosed file <tempfile.SpooledTemporaryFile object at 0x7fbe85d05ab0>
      data, offsets = make_warc()
    ResourceWarning: Enable tracemalloc to get the object allocation traceback
    
    thread '<unnamed>' (2) panicked at fastwarc-rs/src/warc/record.rs:458:62:
    called `Result::unwrap()` on an `Err` value: Custom { kind: Other, error: PyErr { type: <class 'AttributeError'>, value: AttributeError("'ValidatedGzipStream' object has no attribute 'tell'"), traceback: None } }
    ERROR
    
    ======================================================================
    ERROR: test_batch_duplicate_ids (test_ingestion.DatabaseTests.test_batch_duplicate_ids)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py", line 198, in setUp
        self.admin = psycopg2.connect(self.dsn)
                     ~~~~~~~~~~~~~~~~^^^^^^^^^^
      File "/home/spark-master/rag_news_project/spark_warc_project/.venv/lib/python3.13/site-packages/psycopg2/__init__.py", line 122, in connect
        conn = _connect(dsn, connection_factory=connection_factory, **kwasync)
    psycopg2.OperationalError: connection to server on socket "/tmp/warc-v2-test-pg/.s.PGSQL.55439" failed: Operation not permitted
        Is the server running locally and accepting connections on that socket?
    
    
    ======================================================================
    ERROR: test_content_error_rolls_back_cursor_and_rows (test_ingestion.DatabaseTests.test_content_error_rolls_back_cursor_and_rows)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py", line 198, in setUp
        self.admin = psycopg2.connect(self.dsn)
                     ~~~~~~~~~~~~~~~~^^^^^^^^^^
      File "/home/spark-master/rag_news_project/spark_warc_project/.venv/lib/python3.13/site-packages/psycopg2/__init__.py", line 122, in connect
        conn = _connect(dsn, connection_factory=connection_factory, **kwasync)
    psycopg2.OperationalError: connection to server on socket "/tmp/warc-v2-test-pg/.s.PGSQL.55439" failed: Operation not permitted
        Is the server running locally and accepting connections on that socket?
    
    
    ======================================================================
    ERROR: test_driver_shortfall_failure_and_resume (test_ingestion.DatabaseTests.test_driver_shortfall_failure_and_resume)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py", line 198, in setUp
        self.admin = psycopg2.connect(self.dsn)
                     ~~~~~~~~~~~~~~~~^^^^^^^^^^
      File "/home/spark-master/rag_news_project/spark_warc_project/.venv/lib/python3.13/site-packages/psycopg2/__init__.py", line 122, in connect
        conn = _connect(dsn, connection_factory=connection_factory, **kwasync)
    psycopg2.OperationalError: connection to server on socket "/tmp/warc-v2-test-pg/.s.PGSQL.55439" failed: Operation not permitted
        Is the server running locally and accepting connections on that socket?
    
    
    ======================================================================
    ERROR: test_exact_caps_duplicates_and_idempotent_receipt (test_ingestion.DatabaseTests.test_exact_caps_duplicates_and_idempotent_receipt)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py", line 198, in setUp
        self.admin = psycopg2.connect(self.dsn)
                     ~~~~~~~~~~~~~~~~^^^^^^^^^^
      File "/home/spark-master/rag_news_project/spark_warc_project/.venv/lib/python3.13/site-packages/psycopg2/__init__.py", line 122, in connect
        conn = _connect(dsn, connection_factory=connection_factory, **kwasync)
    psycopg2.OperationalError: connection to server on socket "/tmp/warc-v2-test-pg/.s.PGSQL.55439" failed: Operation not permitted
        Is the server running locally and accepting connections on that socket?
    
    
    ======================================================================
    ERROR: test_failed_file_retries_on_resume (test_ingestion.DatabaseTests.test_failed_file_retries_on_resume)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py", line 198, in setUp
        self.admin = psycopg2.connect(self.dsn)
                     ~~~~~~~~~~~~~~~~^^^^^^^^^^
      File "/home/spark-master/rag_news_project/spark_warc_project/.venv/lib/python3.13/site-packages/psycopg2/__init__.py", line 122, in connect
        conn = _connect(dsn, connection_factory=connection_factory, **kwasync)
    psycopg2.OperationalError: connection to server on socket "/tmp/warc-v2-test-pg/.s.PGSQL.55439" failed: Operation not permitted
        Is the server running locally and accepting connections on that socket?
    
    
    ======================================================================
    ERROR: test_legacy_complete_preserved_partial_restarted (test_ingestion.DatabaseTests.test_legacy_complete_preserved_partial_restarted)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py", line 198, in setUp
        self.admin = psycopg2.connect(self.dsn)
                     ~~~~~~~~~~~~~~~~^^^^^^^^^^
      File "/home/spark-master/rag_news_project/spark_warc_project/.venv/lib/python3.13/site-packages/psycopg2/__init__.py", line 122, in connect
        conn = _connect(dsn, connection_factory=connection_factory, **kwasync)
    psycopg2.OperationalError: connection to server on socket "/tmp/warc-v2-test-pg/.s.PGSQL.55439" failed: Operation not permitted
        Is the server running locally and accepting connections on that socket?
    
    
    ======================================================================
    ERROR: test_lock_excludes_second_coordinator (test_ingestion.DatabaseTests.test_lock_excludes_second_coordinator)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py", line 198, in setUp
        self.admin = psycopg2.connect(self.dsn)
                     ~~~~~~~~~~~~~~~~^^^^^^^^^^
      File "/home/spark-master/rag_news_project/spark_warc_project/.venv/lib/python3.13/site-packages/psycopg2/__init__.py", line 122, in connect
        conn = _connect(dsn, connection_factory=connection_factory, **kwasync)
    psycopg2.OperationalError: connection to server on socket "/tmp/warc-v2-test-pg/.s.PGSQL.55439" failed: Operation not permitted
        Is the server running locally and accepting connections on that socket?
    
    
    ======================================================================
    ERROR: test_malformed_row_isolated (test_ingestion.DatabaseTests.test_malformed_row_isolated)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py", line 198, in setUp
        self.admin = psycopg2.connect(self.dsn)
                     ~~~~~~~~~~~~~~~~^^^^^^^^^^
      File "/home/spark-master/rag_news_project/spark_warc_project/.venv/lib/python3.13/site-packages/psycopg2/__init__.py", line 122, in connect
        conn = _connect(dsn, connection_factory=connection_factory, **kwasync)
    psycopg2.OperationalError: connection to server on socket "/tmp/warc-v2-test-pg/.s.PGSQL.55439" failed: Operation not permitted
        Is the server running locally and accepting connections on that socket?
    
    
    ======================================================================
    ERROR: test_stale_and_stalled_cursors_rejected (test_ingestion.DatabaseTests.test_stale_and_stalled_cursors_rejected)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py", line 198, in setUp
        self.admin = psycopg2.connect(self.dsn)
                     ~~~~~~~~~~~~~~~~^^^^^^^^^^
      File "/home/spark-master/rag_news_project/spark_warc_project/.venv/lib/python3.13/site-packages/psycopg2/__init__.py", line 122, in connect
        conn = _connect(dsn, connection_factory=connection_factory, **kwasync)
    psycopg2.OperationalError: connection to server on socket "/tmp/warc-v2-test-pg/.s.PGSQL.55439" failed: Operation not permitted
        Is the server running locally and accepting connections on that socket?
    
    
    ======================================================================
    ERROR: test_uncertain_commit_recovered_after_reconnection (test_ingestion.DatabaseTests.test_uncertain_commit_recovered_after_reconnection)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py", line 198, in setUp
        self.admin = psycopg2.connect(self.dsn)
                     ~~~~~~~~~~~~~~~~^^^^^^^^^^
      File "/home/spark-master/rag_news_project/spark_warc_project/.venv/lib/python3.13/site-packages/psycopg2/__init__.py", line 122, in connect
        conn = _connect(dsn, connection_factory=connection_factory, **kwasync)
    psycopg2.OperationalError: connection to server on socket "/tmp/warc-v2-test-pg/.s.PGSQL.55439" failed: Operation not permitted
        Is the server running locally and accepting connections on that socket?
    
    
    ======================================================================
    ERROR: test_corrupt_or_truncated_gzip_never_marks_eof (test_ingestion.UnitTests.test_corrupt_or_truncated_gzip_never_marks_eof)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py", line 170, in test_corrupt_or_truncated_gzip_never_marks_eof
        result = worker(broken, task(candidate_limit=100))
      File "/home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py", line 75, in worker
        return job.process_file_chunk(work)
               ~~~~~~~~~~~~~~~~~~~~~~^^^^^^
      File "/home/spark-master/rag_news_project/spark_warc_v2/stream_to_db.py", line 317, in process_file_chunk
        result = _process_file_once(task)
      File "/home/spark-master/rag_news_project/spark_warc_v2/stream_to_db.py", line 225, in _process_file_once
        current = next(records)
      File "/home/spark-master/rag_news_project/spark_warc_v2/parsers/parsers.py", line 53, in parse_warc_records_streaming
        iterator = ArchiveIterator(
            stream, parse_http=True, auto_decode="all", max_header_len=64 * 1024,
            stream_detect=True, buffer_size=64 * 1024, fsspec_args=False,
        )
    pyo3_runtime.PanicException: called `Result::unwrap()` on an `Err` value: Custom { kind: Other, error: PyErr { type: <class 'AttributeError'>, value: AttributeError("'ValidatedGzipStream' object has no attribute 'tell'"), traceback: None } }
    
    ======================================================================
    ERROR: test_empty_and_rejected_files_advance (test_ingestion.UnitTests.test_empty_and_rejected_files_advance)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py", line 159, in test_empty_and_rejected_files_advance
        result = worker(data, language='other')
      File "/home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py", line 75, in worker
        return job.process_file_chunk(work)
               ~~~~~~~~~~~~~~~~~~~~~~^^^^^^
      File "/home/spark-master/rag_news_project/spark_warc_v2/stream_to_db.py", line 317, in process_file_chunk
        result = _process_file_once(task)
      File "/home/spark-master/rag_news_project/spark_warc_v2/stream_to_db.py", line 225, in _process_file_once
        current = next(records)
      File "/home/spark-master/rag_news_project/spark_warc_v2/parsers/parsers.py", line 53, in parse_warc_records_streaming
        iterator = ArchiveIterator(
            stream, parse_http=True, auto_decode="all", max_header_len=64 * 1024,
            stream_detect=True, buffer_size=64 * 1024, fsspec_args=False,
        )
    pyo3_runtime.PanicException: called `Result::unwrap()` on an `Err` value: Custom { kind: Other, error: PyErr { type: <class 'AttributeError'>, value: AttributeError("'ValidatedGzipStream' object has no attribute 'tell'"), traceback: None } }
    
    ======================================================================
    ERROR: test_ignored_range_and_unknown_length (test_ingestion.UnitTests.test_ignored_range_and_unknown_length)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py", line 151, in test_ignored_range_and_unknown_length
        result = worker(data, task(start_offset=offsets[2]), ranged=False, size=False)
      File "/home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py", line 75, in worker
        return job.process_file_chunk(work)
               ~~~~~~~~~~~~~~~~~~~~~~^^^^^^
      File "/home/spark-master/rag_news_project/spark_warc_v2/stream_to_db.py", line 317, in process_file_chunk
        result = _process_file_once(task)
      File "/home/spark-master/rag_news_project/spark_warc_v2/stream_to_db.py", line 225, in _process_file_once
        current = next(records)
      File "/home/spark-master/rag_news_project/spark_warc_v2/parsers/parsers.py", line 53, in parse_warc_records_streaming
        iterator = ArchiveIterator(
            stream, parse_http=True, auto_decode="all", max_header_len=64 * 1024,
            stream_detect=True, buffer_size=64 * 1024, fsspec_args=False,
        )
    pyo3_runtime.PanicException: called `Result::unwrap()` on an `Err` value: Custom { kind: Other, error: PyErr { type: <class 'AttributeError'>, value: AttributeError("'ValidatedGzipStream' object has no attribute 'tell'"), traceback: None } }
    
    ======================================================================
    ERROR: test_oversize_decoded_http_body_is_skipped (test_ingestion.UnitTests.test_oversize_decoded_http_body_is_skipped)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py", line 178, in test_oversize_decoded_http_body_is_skipped
        result = worker(data, task(max_html_bytes=1024))
      File "/home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py", line 75, in worker
        return job.process_file_chunk(work)
               ~~~~~~~~~~~~~~~~~~~~~~^^^^^^
      File "/home/spark-master/rag_news_project/spark_warc_v2/stream_to_db.py", line 317, in process_file_chunk
        result = _process_file_once(task)
      File "/home/spark-master/rag_news_project/spark_warc_v2/stream_to_db.py", line 225, in _process_file_once
        current = next(records)
      File "/home/spark-master/rag_news_project/spark_warc_v2/parsers/parsers.py", line 53, in parse_warc_records_streaming
        iterator = ArchiveIterator(
            stream, parse_http=True, auto_decode="all", max_header_len=64 * 1024,
            stream_detect=True, buffer_size=64 * 1024, fsspec_args=False,
        )
    pyo3_runtime.PanicException: called `Result::unwrap()` on an `Err` value: Custom { kind: Other, error: PyErr { type: <class 'AttributeError'>, value: AttributeError("'ValidatedGzipStream' object has no attribute 'tell'"), traceback: None } }
    
    ======================================================================
    ERROR: test_result_budget_revisits_unreturned_record (test_ingestion.UnitTests.test_result_budget_revisits_unreturned_record)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py", line 185, in test_result_budget_revisits_unreturned_record
        first = worker(data, task(candidate_limit=1))
      File "/home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py", line 75, in worker
        return job.process_file_chunk(work)
               ~~~~~~~~~~~~~~~~~~~~~~^^^^^^
      File "/home/spark-master/rag_news_project/spark_warc_v2/stream_to_db.py", line 317, in process_file_chunk
        result = _process_file_once(task)
      File "/home/spark-master/rag_news_project/spark_warc_v2/stream_to_db.py", line 225, in _process_file_once
        current = next(records)
      File "/home/spark-master/rag_news_project/spark_warc_v2/parsers/parsers.py", line 53, in parse_warc_records_streaming
        iterator = ArchiveIterator(
            stream, parse_http=True, auto_decode="all", max_header_len=64 * 1024,
            stream_detect=True, buffer_size=64 * 1024, fsspec_args=False,
        )
    pyo3_runtime.PanicException: called `Result::unwrap()` on an `Err` value: Custom { kind: Other, error: PyErr { type: <class 'AttributeError'>, value: AttributeError("'ValidatedGzipStream' object has no attribute 'tell'"), traceback: None } }
    
    ======================================================================
    ERROR: test_small_chunks_advance_without_loss (test_ingestion.UnitTests.test_small_chunks_advance_without_loss)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py", line 141, in test_small_chunks_advance_without_loss
        result = worker(data)
      File "/home/spark-master/rag_news_project/spark_warc_v2/tests/test_ingestion.py", line 75, in worker
        return job.process_file_chunk(work)
               ~~~~~~~~~~~~~~~~~~~~~~^^^^^^
      File "/home/spark-master/rag_news_project/spark_warc_v2/stream_to_db.py", line 317, in process_file_chunk
        result = _process_file_once(task)
      File "/home/spark-master/rag_news_project/spark_warc_v2/stream_to_db.py", line 225, in _process_file_once
        current = next(records)
      File "/home/spark-master/rag_news_project/spark_warc_v2/parsers/parsers.py", line 53, in parse_warc_records_streaming
        iterator = ArchiveIterator(
            stream, parse_http=True, auto_decode="all", max_header_len=64 * 1024,
            stream_detect=True, buffer_size=64 * 1024, fsspec_args=False,
        )
    pyo3_runtime.PanicException: called `Result::unwrap()` on an `Err` value: Custom { kind: Other, error: PyErr { type: <class 'AttributeError'>, value: AttributeError("'ValidatedGzipStream' object has no attribute 'tell'"), traceback: None } }
    
    ----------------------------------------------------------------------
    Ran 21 tests in 0.061s
    
    FAILED (errors=16)
    ✗ (1) • 1.45s

## Activity

    $ python3 - <<'PY'
        p='parsers/parsers.py';s=open(p).read().replace('    def read(self, size=65536):','    def tell(self):\n        return self.bytes_read\n\n    def read(self, size=65536):');open(p,'w').write(s)
        p='tests/test_ingestion.py';s=open(p).read().replace('        writer.write_record(record)','        writer.write_record(record)\n        record.raw_stream.close()');open(p,'w').write(s)
        PY
    ✓ • 0ms

## Activity

    $ WARC_TEST_DSN='host=/tmp/warc-v2-test-pg port=55439 dbname=postgres user=hadoop' ../spark_warc_project/.venv/bin/python -m unittest discover -s tests -v
    test_batch_duplicate_ids (test_ingestion.DatabaseTests.test_batch_duplicate_ids) ... ok
    test_content_error_rolls_back_cursor_and_rows (test_ingestion.DatabaseTests.test_content_error_rolls_back_cursor_and_rows) ... ok
    test_driver_shortfall_failure_and_resume (test_ingestion.DatabaseTests.test_driver_shortfall_failure_and_resume) ... ok
    test_exact_caps_duplicates_and_idempotent_receipt (test_ingestion.DatabaseTests.test_exact_caps_duplicates_and_idempotent_receipt) ... ok
    test_failed_file_retries_on_resume (test_ingestion.DatabaseTests.test_failed_file_retries_on_resume) ... ok
    test_legacy_complete_preserved_partial_restarted (test_ingestion.DatabaseTests.test_legacy_complete_preserved_partial_restarted) ... ok
    test_lock_excludes_second_coordinator (test_ingestion.DatabaseTests.test_lock_excludes_second_coordinator) ... ok
    test_malformed_row_isolated (test_ingestion.DatabaseTests.test_malformed_row_isolated) ... ok
    test_stale_and_stalled_cursors_rejected (test_ingestion.DatabaseTests.test_stale_and_stalled_cursors_rejected) ... ok
    test_uncertain_commit_recovered_after_reconnection (test_ingestion.DatabaseTests.test_uncertain_commit_recovered_after_reconnection) ... ok
    test_allocations_respect_total_and_per_file (test_ingestion.UnitTests.test_allocations_respect_total_and_per_file) ... ok
    test_corrupt_or_truncated_gzip_never_marks_eof (test_ingestion.UnitTests.test_corrupt_or_truncated_gzip_never_marks_eof) ... ok
    test_defaults_and_validation (test_ingestion.UnitTests.test_defaults_and_validation) ... ok
    test_empty_and_rejected_files_advance (test_ingestion.UnitTests.test_empty_and_rejected_files_advance) ... ok
    test_french_encoding_and_jsonld (test_ingestion.UnitTests.test_french_encoding_and_jsonld) ... ok
    test_ignored_range_and_unknown_length (test_ingestion.UnitTests.test_ignored_range_and_unknown_length) ... ok
    test_language_sample_has_no_overlap (test_ingestion.UnitTests.test_language_sample_has_no_overlap) ... ok
    test_oversize_decoded_http_body_is_skipped (test_ingestion.UnitTests.test_oversize_decoded_http_body_is_skipped) ... ok
    test_result_budget_revisits_unreturned_record (test_ingestion.UnitTests.test_result_budget_revisits_unreturned_record) ... ok
    test_resume_restores_and_rejects_conflicting_filters (test_ingestion.UnitTests.test_resume_restores_and_rejects_conflicting_filters) ... ok
    test_small_chunks_advance_without_loss (test_ingestion.UnitTests.test_small_chunks_advance_without_loss) ... ok
    Resuming run ac56d5ca-2089-4258-af30-4d0c4a408b0e: 0 committed
    Resume command: RESUME_RUN_ID=ac56d5ca-2089-4258-af30-4d0c4a408b0e ./run_to_db.sh
    FAILED file-1: timeout
    FAILED file-2: timeout
    Wave 1: committed 0/3; new=0; worker peak RSS MiB=[None, None]
    Run ac56d5ca-2089-4258-af30-4d0c4a408b0e: failed; committed 0/3 new articles
      file-1: 0 new; failed; timeout
      file-2: 0 new; failed; timeout
    Counters: {}
    Resume command: RESUME_RUN_ID=ac56d5ca-2089-4258-af30-4d0c4a408b0e ./run_to_db.sh
    Resuming run ac56d5ca-2089-4258-af30-4d0c4a408b0e: 0 committed
    Resume command: RESUME_RUN_ID=ac56d5ca-2089-4258-af30-4d0c4a408b0e ./run_to_db.sh
    Wave 1: committed 0/3; new=0; worker peak RSS MiB=[None, None]
    Run ac56d5ca-2089-4258-af30-4d0c4a408b0e: shortfall; committed 0/3 new articles
      file-1: 0 new; eof
      file-2: 0 new; eof
    Counters: {}
    Resume command: RESUME_RUN_ID=ac56d5ca-2089-4258-af30-4d0c4a408b0e ./run_to_db.sh
    
    ----------------------------------------------------------------------
    Ran 21 tests in 0.657s
    
    OK
    ✓ • 708ms

## Activity

    $ python3 -m venv .venv
        .venv/bin/python -m pip install -r requirements-dev.txt
    WARNING: The directory '/home/hadoop/.cache/pip' or its parent directory is not owned or is not writable by the current user. The cache has been disabled. Check the permissions and owner of that directory. If executing pip with sudo, you should use sudo's -H flag.
    WARNING: Retrying (Retry(total=4, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<pip._vendor.urllib3.connection.HTTPSConnection object at 0x7fb274a75400>: Failed to establish a new connection: [Errno -2] Name or service not known')': /simple/fastwarc/
    WARNING: Retrying (Retry(total=3, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<pip._vendor.urllib3.connection.HTTPSConnection object at 0x7fb274bbec10>: Failed to establish a new connection: [Errno -2] Name or service not known')': /simple/fastwarc/
    WARNING: Retrying (Retry(total=2, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<pip._vendor.urllib3.connection.HTTPSConnection object at 0x7fb274bbee90>: Failed to establish a new connection: [Errno -2] Name or service not known')': /simple/fastwarc/
    WARNING: Retrying (Retry(total=1, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<pip._vendor.urllib3.connection.HTTPSConnection object at 0x7fb274bbf110>: Failed to establish a new connection: [Errno -2] Name or service not known')': /simple/fastwarc/
    WARNING: Retrying (Retry(total=0, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<pip._vendor.urllib3.connection.HTTPSConnection object at 0x7fb274bbf390>: Failed to establish a new connection: [Errno -2] Name or service not known')': /simple/fastwarc/
    ERROR: Could not find a version that satisfies the requirement FastWARC==1.0.9 (from versions: none)
    ERROR: No matching distribution found for FastWARC==1.0.9
    ✗ (1) • 10.63s

## Activity

    $ RAYON_NUM_THREADS=1 ../spark_warc_project/.venv/bin/python - <<'PY'
        import resource,time
        from extractors.extractors import detect_languages_batch
        texts=[
        'The government announced new measures to improve public transportation. Local officials said the changes would reduce traffic and make daily journeys easier for residents.',
        'Les élèves français étudient les événements récents et découvrent une société développée. Le gouvernement a annoncé de nouvelles mesures pour améliorer les transports publics.',
        'أعلنت الحكومة اليوم عن إجراءات جديدة لتحسين خدمات النقل العام في المدينة. وقال المسؤولون إن هذه الخطوات ستساهم في تخفيف الازدحام وتسهيل حركة المواطنين خلال ساعات العمل.',
        'El gobierno anunció nuevas medidas para mejorar el transporte público de la ciudad. Los funcionarios explicaron que los cambios reducirán el tráfico durante las horas de trabajo.',
        'دولت امروز اقدامات جدیدی را برای بهبود حمل و نقل عمومی اعلام کرد. مسئولان گفتند که این تغییرات به کاهش ترافیک و بهبود زندگی شهروندان کمک خواهد کرد.',
        'حکومت نے آج شہر میں عوامی نقل و حمل کو بہتر بنانے کے لیے نئے اقدامات کا اعلان کیا۔ حکام کا کہنا ہے کہ ان تبدیلیوں سے ٹریفک کم ہو گی اور شہریوں کو سہولت ملے گی۔']
        start=time.monotonic();print(detect_languages_batch(texts));print('seconds',time.monotonic()-start,'peak RSS MiB',resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)
        PY
    ['en', 'fr', 'ar', 'other', 'fa', 'ur']
    seconds 1.9046560870001485 peak RSS MiB 79.6875
    ✓ • 1.91s

## Assistant

All 21 regression tests pass, including real PostgreSQL tests for exact quotas, rollback, duplicate IDs, lost commit acknowledgements, and failed-file resume. I’m now checking the full language detector’s memory use, installing a clean project environment, and checking YARN availability.

## Activity

    $ timeout 25 yarn node -list
    2026-09-30 11:14:13,990 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at spark-master/192.168.56.10:8032
    2026-09-30 11:14:15,219 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 0 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:14:16,229 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 1 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:14:17,232 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 2 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:14:18,234 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 3 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:14:19,237 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 4 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:14:20,239 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 5 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:14:21,243 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 6 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:14:22,245 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 7 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:14:23,247 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 8 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:14:24,248 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 9 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    ✗ (124) • 25.08s

## Activity

    $ yarn node -list
        hdfs dfs -test -e /
    2026-09-30 11:12:57,637 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at spark-master/192.168.56.10:8032
    2026-09-30 11:12:59,013 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 0 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:13:00,015 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 1 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:13:01,017 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 2 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:13:02,018 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 3 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:13:03,019 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 4 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:13:04,021 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 5 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:13:05,022 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 6 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:13:06,023 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 7 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:13:07,025 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 8 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:13:08,026 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 9 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:13:39,090 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 0 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:13:40,092 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 1 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:13:41,093 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 2 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:13:42,094 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 3 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:13:43,095 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 4 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:13:44,098 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 5 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:13:45,099 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 6 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:13:46,101 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 7 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:13:47,102 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 8 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:13:48,104 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 9 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:13:48,114 INFO retry.RetryInvocationHandler: java.net.SocketException: Call From spark-master/192.168.56.10 to spark-master:8032 failed on socket exception: java.net.SocketException: Operation not permitted; For more details see:  http://wiki.apache.org/hadoop/SocketException, while invoking ApplicationClientProtocolPBClientImpl.getClusterNodes over null. Retrying after sleeping for 30000ms. Current retry count: 1.
    2026-09-30 11:14:19,123 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 0 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:14:20,124 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 1 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:14:21,126 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 2 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:14:22,128 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 3 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:14:23,129 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 4 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:14:24,130 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 5 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:14:25,131 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 6 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:14:26,133 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 7 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:14:27,134 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 8 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:14:28,136 INFO ipc.Client: Retrying connect to server: spark-master/192.168.56.10:8032. Already tried 9 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
    2026-09-30 11:14:28,138 INFO retry.RetryInvocationHandler: java.net.SocketException: Call From spark-master/192.168.56.10 to spark-master:8032 failed on socket exception: java.net.SocketException: Operation not permitted; For more details see:  http://wiki.apache.org/hadoop/SocketException, while invoking ApplicationClientProtocolPBClientImpl.getClusterNodes over null. Retrying after sleeping for 30000ms. Current retry count: 2.
    ✗ (130) • 1m 50s

## Activity

    $ ss -lnt
        ps -eo pid,comm,args
    Cannot open netlink socket: Operation not permitted
    State Recv-Q Send-Q Local Address:Port Peer Address:Port
        PID COMMAND         COMMAND
          1 codex           codex-linux-sandbox --sandbox-policy-cwd /home/spark-master/rag_news_project/spark_warc_v2 --command-cwd /home/spark-master/rag_news_project/spark_warc_v2 --permission-profile {"type":"managed","file_system":{"type":"restricted","entries":[{"path":{"type":"special","value":{"kind":"root"}},"access":"read"},{"path":{"type":"path","path":"/home/spark-master/rag_news_project/spark_warc_v2"},"access":"write"},{"path":{"type":"special","value":{"kind":"slash_tmp"}},"access":"write"},{"path":{"type":"special","value":{"kind":"tmpdir"}},"access":"write"},{"path":{"type":"path","path":"/home/spark-master/rag_news_project/spark_warc_v2/.git"},"access":"read","missing_path_behavior":"skip"},{"path":{"type":"path","path":"/home/spark-master/rag_news_project/spark_warc_v2/.agents"},"access":"read","missing_path_behavior":"skip"},{"path":{"type":"path","path":"/home/spark-master/rag_news_project/spark_warc_v2/.codex"},"access":"read","missing_path_behavior":"skip"},{"path":{"type":"path","path":"/home/spark-master/rag_news_project/spark_warc_v2/.aws"},"access":"read","missing_path_behavior":"skip"}]},"network":"restricted"} --apply-seccomp-then-exec -- /bin/bash -c __CODEX_SNAPSHOT_OVERRIDE_SET_0="${CODEX_APPLY_PATCH_PRESERVE_LINE_ENDINGS+x}" __CODEX_SNAPSHOT_OVERRIDE_0="${CODEX_APPLY_PATCH_PRESERVE_LINE_ENDINGS-}" __CODEX_SNAPSHOT_OVERRIDE_SET_1="${CODEX_PERMISSION_PROFILE+x}" __CODEX_SNAPSHOT_OVERRIDE_1="${CODEX_PERMISSION_PROFILE-}" __CODEX_SNAPSHOT_OVERRIDE_SET_2="${CODEX_PLUGIN_METRICS_OUTPUT+x}" __CODEX_SNAPSHOT_OVERRIDE_2="${CODEX_PLUGIN_METRICS_OUTPUT-}" __CODEX_SNAPSHOT_OVERRIDE_SET_3="${CODEX_SESSION_ID+x}" __CODEX_SNAPSHOT_OVERRIDE_3="${CODEX_SESSION_ID-}" __CODEX_SNAPSHOT_OVERRIDE_SET_4="${CODEX_THREAD_ID+x}" __CODEX_SNAPSHOT_OVERRIDE_4="${CODEX_THREAD_ID-}" __CODEX_SNAPSHOT_OVERRIDE_SET_5="${CODEX_VERSION+x}" __CODEX_SNAPSHOT_OVERRIDE_5="${CODEX_VERSION-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_0="${ALL_PROXY+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_0="${ALL_PROXY-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_1="${BUNDLE_HTTPS_PROXY+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_1="${BUNDLE_HTTPS_PROXY-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_2="${BUNDLE_HTTP_PROXY+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_2="${BUNDLE_HTTP_PROXY-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_3="${BUNDLE_NO_PROXY+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_3="${BUNDLE_NO_PROXY-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_4="${BUNDLE_SSL_CA_CERT+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_4="${BUNDLE_SSL_CA_CERT-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_5="${CARGO_HTTP_CAINFO+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_5="${CARGO_HTTP_CAINFO-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_6="${CODEX_CA_CERTIFICATE+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_6="${CODEX_CA_CERTIFICATE-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_7="${CODEX_NETWORK_ALLOW_LOCAL_BINDING+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_7="${CODEX_NETWORK_ALLOW_LOCAL_BINDING-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_8="${CODEX_NETWORK_PROXY_ACTIVE+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_8="${CODEX_NETWORK_PROXY_ACTIVE-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_9="${CODEX_NETWORK_PROXY_ATTRIBUTION+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_9="${CODEX_NETWORK_PROXY_ATTRIBUTION-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_10="${CODEX_NETWORK_PROXY_BROKERED_CREDENTIALS+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_10="${CODEX_NETWORK_PROXY_BROKERED_CREDENTIALS-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_11="${CODEX_NETWORK_PROXY_CREDENTIAL_BROKER_ACTIVE+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_11="${CODEX_NETWORK_PROXY_CREDENTIAL_BROKER_ACTIVE-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_12="${CURL_CA_BUNDLE+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_12="${CURL_CA_BUNDLE-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_13="${DOCKER_HTTPS_PROXY+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_13="${DOCKER_HTTPS_PROXY-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_14="${DOCKER_HTTP_PROXY+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_14="${DOCKER_HTTP_PROXY-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_15="${ELECTRON_GET_USE_PROXY+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_15="${ELECTRON_GET_USE_PROXY-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_16="${FTP_PROXY+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_16="${FTP_PROXY-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_17="${GIT_SSL_CAINFO+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_17="${GIT_SSL_CAINFO-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_18="${HTTPS_PROXY+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_18="${HTTPS_PROXY-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_19="${HTTP_PROXY+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_19="${HTTP_PROXY-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_20="${NODE_EXTRA_CA_CERTS+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_20="${NODE_EXTRA_CA_CERTS-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_21="${NODE_USE_ENV_PROXY+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_21="${NODE_USE_ENV_PROXY-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_22="${NO_PROXY+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_22="${NO_PROXY-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_23="${NPM_CONFIG_CAFILE+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_23="${NPM_CONFIG_CAFILE-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_24="${NPM_CONFIG_HTTPS_PROXY+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_24="${NPM_CONFIG_HTTPS_PROXY-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_25="${NPM_CONFIG_HTTP_PROXY+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_25="${NPM_CONFIG_HTTP_PROXY-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_26="${NPM_CONFIG_NOPROXY+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_26="${NPM_CONFIG_NOPROXY-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_27="${NPM_CONFIG_PROXY+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_27="${NPM_CONFIG_PROXY-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_28="${PIP_CERT+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_28="${PIP_CERT-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_29="${PIP_PROXY+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_29="${PIP_PROXY-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_30="${REQUESTS_CA_BUNDLE+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_30="${REQUESTS_CA_BUNDLE-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_31="${SSL_CERT_FILE+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_31="${SSL_CERT_FILE-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_32="${WSS_PROXY+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_32="${WSS_PROXY-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_33="${WS_PROXY+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_33="${WS_PROXY-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_34="${YARN_HTTPS_PROXY+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_34="${YARN_HTTPS_PROXY-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_35="${YARN_HTTP_PROXY+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_35="${YARN_HTTP_PROXY-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_36="${YARN_NO_PROXY+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_36="${YARN_NO_PROXY-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_37="${all_proxy+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_37="${all_proxy-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_38="${ftp_proxy+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_38="${ftp_proxy-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_39="${http_proxy+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_39="${http_proxy-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_40="${https_proxy+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_40="${https_proxy-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_41="${no_proxy+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_41="${no_proxy-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_42="${npm_config_cafile+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_42="${npm_config_cafile-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_43="${npm_config_http_proxy+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_43="${npm_config_http_proxy-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_44="${npm_config_https_proxy+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_44="${npm_config_https_proxy-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_45="${npm_config_noproxy+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_45="${npm_config_noproxy-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_46="${npm_config_proxy+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_46="${npm_config_proxy-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_47="${ws_proxy+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_47="${ws_proxy-}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_48="${wss_proxy+x}" __CODEX_SNAPSHOT_PROXY_OVERRIDE_48="${wss_proxy-}" __CODEX_SNAPSHOT_PROXY_ENV_SET="${CODEX_NETWORK_PROXY_ACTIVE+x}"  if . '/home/hadoop/.codex/shell_snapshots/01a0f153-3bc6-73b2-87ac-59650c2f1b70.1790755159045384506.sh' >/dev/null 2>&1; then :; fi  if [ -n "${__CODEX_SNAPSHOT_OVERRIDE_SET_0}" ]; then   if [ -z "${CODEX_APPLY_PATCH_PRESERVE_LINE_ENDINGS+x}" ] || [ "${CODEX_APPLY_PATCH_PRESERVE_LINE_ENDINGS-}" != "${__CODEX_SNAPSHOT_OVERRIDE_0}" ]; then export CODEX_APPLY_PATCH_PRESERVE_LINE_ENDINGS="${__CODEX_SNAPSHOT_OVERRIDE_0}"; else export CODEX_APPLY_PATCH_PRESERVE_LINE_ENDINGS; fi else builtin unset CODEX_APPLY_PATCH_PRESERVE_LINE_ENDINGS 2>/dev/null || command unset CODEX_APPLY_PATCH_PRESERVE_LINE_ENDINGS; fi builtin unset __CODEX_SNAPSHOT_OVERRIDE_SET_0 __CODEX_SNAPSHOT_OVERRIDE_0 2>/dev/null || command unset __CODEX_SNAPSHOT_OVERRIDE_SET_0 __CODEX_SNAPSHOT_OVERRIDE_0 if [ -n "${__CODEX_SNAPSHOT_OVERRIDE_SET_1}" ]; then   if [ -z "${CODEX_PERMISSION_PROFILE+x}" ] || [ "${CODEX_PERMISSION_PROFILE-}" != "${__CODEX_SNAPSHOT_OVERRIDE_1}" ]; then export CODEX_PERMISSION_PROFILE="${__CODEX_SNAPSHOT_OVERRIDE_1}"; else export CODEX_PERMISSION_PROFILE; fi else builtin unset CODEX_PERMISSION_PROFILE 2>/dev/null || command unset CODEX_PERMISSION_PROFILE; fi builtin unset __CODEX_SNAPSHOT_OVERRIDE_SET_1 __CODEX_SNAPSHOT_OVERRIDE_1 2>/dev/null || command unset __CODEX_SNAPSHOT_OVERRIDE_SET_1 __CODEX_SNAPSHOT_OVERRIDE_1 if [ -n "${__CODEX_SNAPSHOT_OVERRIDE_SET_2}" ]; then   if [ -z "${CODEX_PLUGIN_METRICS_OUTPUT+x}" ] || [ "${CODEX_PLUGIN_METRICS_OUTPUT-}" != "${__CODEX_SNAPSHOT_OVERRIDE_2}" ]; then export CODEX_PLUGIN_METRICS_OUTPUT="${__CODEX_SNAPSHOT_OVERRIDE_2}"; else export CODEX_PLUGIN_METRICS_OUTPUT; fi else builtin unset CODEX_PLUGIN_METRICS_OUTPUT 2>/dev/null || command unset CODEX_PLUGIN_METRICS_OUTPUT; fi builtin unset __CODEX_SNAPSHOT_OVERRIDE_SET_2 __CODEX_SNAPSHOT_OVERRIDE_2 2>/dev/null || command unset __CODEX_SNAPSHOT_OVERRIDE_SET_2 __CODEX_SNAPSHOT_OVERRIDE_2 if [ -n "${__CODEX_SNAPSHOT_OVERRIDE_SET_3}" ]; then   if [ -z "${CODEX_SESSION_ID+x}" ] || [ "${CODEX_SESSION_ID-}" != "${__CODEX_SNAPSHOT_OVERRIDE_3}" ]; then export CODEX_SESSION_ID="${__CODEX_SNAPSHOT_OVERRIDE_3}"; else export CODEX_SESSION_ID; fi else builtin unset CODEX_SESSION_ID 2>/dev/null || command unset CODEX_SESSION_ID; fi builtin unset __CODEX_SNAPSHOT_OVERRIDE_SET_3 __CODEX_SNAPSHOT_OVERRIDE_3 2>/dev/null || command unset __CODEX_SNAPSHOT_OVERRIDE_SET_3 __CODEX_SNAPSHOT_OVERRIDE_3 if [ -n "${__CODEX_SNAPSHOT_OVERRIDE_SET_4}" ]; then   if [ -z "${CODEX_THREAD_ID+x}" ] || [ "${CODEX_THREAD_ID-}" != "${__CODEX_SNAPSHOT_OVERRIDE_4}" ]; then export CODEX_THREAD_ID="${__CODEX_SNAPSHOT_OVERRIDE_4}"; else export CODEX_THREAD_ID; fi else builtin unset CODEX_THREAD_ID 2>/dev/null || command unset CODEX_THREAD_ID; fi builtin unset __CODEX_SNAPSHOT_OVERRIDE_SET_4 __CODEX_SNAPSHOT_OVERRIDE_4 2>/dev/null || command unset __CODEX_SNAPSHOT_OVERRIDE_SET_4 __CODEX_SNAPSHOT_OVERRIDE_4 if [ -n "${__CODEX_SNAPSHOT_OVERRIDE_SET_5}" ]; then   if [ -z "${CODEX_VERSION+x}" ] || [ "${CODEX_VERSION-}" != "${__CODEX_SNAPSHOT_OVERRIDE_5}" ]; then export CODEX_VERSION="${__CODEX_SNAPSHOT_OVERRIDE_5}"; else export CODEX_VERSION; fi else builtin unset CODEX_VERSION 2>/dev/null || command unset CODEX_VERSION; fi builtin unset __CODEX_SNAPSHOT_OVERRIDE_SET_5 __CODEX_SNAPSHOT_OVERRIDE_5 2>/dev/null || command unset __CODEX_SNAPSHOT_OVERRIDE_SET_5 __CODEX_SNAPSHOT_OVERRIDE_5 if [ -n "$__CODEX_SNAPSHOT_PROXY_ENV_SET" ] || [ -n "${CODEX_NETWORK_PROXY_ACTIVE+x}" ]; then if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_0}" ]; then   if [ -z "${ALL_PROXY+x}" ] || [ "${ALL_PROXY-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_0}" ]; then export ALL_PROXY="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_0}"; else export ALL_PROXY; fi else builtin unset ALL_PROXY 2>/dev/null || command unset ALL_PROXY; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_0 __CODEX_SNAPSHOT_PROXY_OVERRIDE_0 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_0 __CODEX_SNAPSHOT_PROXY_OVERRIDE_0 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_1}" ]; then   if [ -z "${BUNDLE_HTTPS_PROXY+x}" ] || [ "${BUNDLE_HTTPS_PROXY-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_1}" ]; then export BUNDLE_HTTPS_PROXY="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_1}"; else export BUNDLE_HTTPS_PROXY; fi else builtin unset BUNDLE_HTTPS_PROXY 2>/dev/null || command unset BUNDLE_HTTPS_PROXY; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_1 __CODEX_SNAPSHOT_PROXY_OVERRIDE_1 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_1 __CODEX_SNAPSHOT_PROXY_OVERRIDE_1 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_2}" ]; then   if [ -z "${BUNDLE_HTTP_PROXY+x}" ] || [ "${BUNDLE_HTTP_PROXY-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_2}" ]; then export BUNDLE_HTTP_PROXY="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_2}"; else export BUNDLE_HTTP_PROXY; fi else builtin unset BUNDLE_HTTP_PROXY 2>/dev/null || command unset BUNDLE_HTTP_PROXY; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_2 __CODEX_SNAPSHOT_PROXY_OVERRIDE_2 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_2 __CODEX_SNAPSHOT_PROXY_OVERRIDE_2 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_3}" ]; then   if [ -z "${BUNDLE_NO_PROXY+x}" ] || [ "${BUNDLE_NO_PROXY-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_3}" ]; then export BUNDLE_NO_PROXY="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_3}"; else export BUNDLE_NO_PROXY; fi else builtin unset BUNDLE_NO_PROXY 2>/dev/null || command unset BUNDLE_NO_PROXY; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_3 __CODEX_SNAPSHOT_PROXY_OVERRIDE_3 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_3 __CODEX_SNAPSHOT_PROXY_OVERRIDE_3 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_4}" ]; then   if [ -z "${BUNDLE_SSL_CA_CERT+x}" ] || [ "${BUNDLE_SSL_CA_CERT-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_4}" ]; then export BUNDLE_SSL_CA_CERT="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_4}"; else export BUNDLE_SSL_CA_CERT; fi else builtin unset BUNDLE_SSL_CA_CERT 2>/dev/null || command unset BUNDLE_SSL_CA_CERT; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_4 __CODEX_SNAPSHOT_PROXY_OVERRIDE_4 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_4 __CODEX_SNAPSHOT_PROXY_OVERRIDE_4 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_5}" ]; then   if [ -z "${CARGO_HTTP_CAINFO+x}" ] || [ "${CARGO_HTTP_CAINFO-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_5}" ]; then export CARGO_HTTP_CAINFO="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_5}"; else export CARGO_HTTP_CAINFO; fi else builtin unset CARGO_HTTP_CAINFO 2>/dev/null || command unset CARGO_HTTP_CAINFO; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_5 __CODEX_SNAPSHOT_PROXY_OVERRIDE_5 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_5 __CODEX_SNAPSHOT_PROXY_OVERRIDE_5 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_6}" ]; then   if [ -z "${CODEX_CA_CERTIFICATE+x}" ] || [ "${CODEX_CA_CERTIFICATE-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_6}" ]; then export CODEX_CA_CERTIFICATE="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_6}"; else export CODEX_CA_CERTIFICATE; fi else builtin unset CODEX_CA_CERTIFICATE 2>/dev/null || command unset CODEX_CA_CERTIFICATE; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_6 __CODEX_SNAPSHOT_PROXY_OVERRIDE_6 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_6 __CODEX_SNAPSHOT_PROXY_OVERRIDE_6 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_7}" ]; then   if [ -z "${CODEX_NETWORK_ALLOW_LOCAL_BINDING+x}" ] || [ "${CODEX_NETWORK_ALLOW_LOCAL_BINDING-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_7}" ]; then export CODEX_NETWORK_ALLOW_LOCAL_BINDING="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_7}"; else export CODEX_NETWORK_ALLOW_LOCAL_BINDING; fi else builtin unset CODEX_NETWORK_ALLOW_LOCAL_BINDING 2>/dev/null || command unset CODEX_NETWORK_ALLOW_LOCAL_BINDING; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_7 __CODEX_SNAPSHOT_PROXY_OVERRIDE_7 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_7 __CODEX_SNAPSHOT_PROXY_OVERRIDE_7 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_8}" ]; then   if [ -z "${CODEX_NETWORK_PROXY_ACTIVE+x}" ] || [ "${CODEX_NETWORK_PROXY_ACTIVE-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_8}" ]; then export CODEX_NETWORK_PROXY_ACTIVE="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_8}"; else export CODEX_NETWORK_PROXY_ACTIVE; fi else builtin unset CODEX_NETWORK_PROXY_ACTIVE 2>/dev/null || command unset CODEX_NETWORK_PROXY_ACTIVE; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_8 __CODEX_SNAPSHOT_PROXY_OVERRIDE_8 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_8 __CODEX_SNAPSHOT_PROXY_OVERRIDE_8 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_9}" ]; then   if [ -z "${CODEX_NETWORK_PROXY_ATTRIBUTION+x}" ] || [ "${CODEX_NETWORK_PROXY_ATTRIBUTION-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_9}" ]; then export CODEX_NETWORK_PROXY_ATTRIBUTION="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_9}"; else export CODEX_NETWORK_PROXY_ATTRIBUTION; fi else builtin unset CODEX_NETWORK_PROXY_ATTRIBUTION 2>/dev/null || command unset CODEX_NETWORK_PROXY_ATTRIBUTION; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_9 __CODEX_SNAPSHOT_PROXY_OVERRIDE_9 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_9 __CODEX_SNAPSHOT_PROXY_OVERRIDE_9 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_10}" ]; then   if [ -z "${CODEX_NETWORK_PROXY_BROKERED_CREDENTIALS+x}" ] || [ "${CODEX_NETWORK_PROXY_BROKERED_CREDENTIALS-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_10}" ]; then export CODEX_NETWORK_PROXY_BROKERED_CREDENTIALS="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_10}"; else export CODEX_NETWORK_PROXY_BROKERED_CREDENTIALS; fi else builtin unset CODEX_NETWORK_PROXY_BROKERED_CREDENTIALS 2>/dev/null || command unset CODEX_NETWORK_PROXY_BROKERED_CREDENTIALS; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_10 __CODEX_SNAPSHOT_PROXY_OVERRIDE_10 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_10 __CODEX_SNAPSHOT_PROXY_OVERRIDE_10 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_11}" ]; then   if [ -z "${CODEX_NETWORK_PROXY_CREDENTIAL_BROKER_ACTIVE+x}" ] || [ "${CODEX_NETWORK_PROXY_CREDENTIAL_BROKER_ACTIVE-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_11}" ]; then export CODEX_NETWORK_PROXY_CREDENTIAL_BROKER_ACTIVE="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_11}"; else export CODEX_NETWORK_PROXY_CREDENTIAL_BROKER_ACTIVE; fi else builtin unset CODEX_NETWORK_PROXY_CREDENTIAL_BROKER_ACTIVE 2>/dev/null || command unset CODEX_NETWORK_PROXY_CREDENTIAL_BROKER_ACTIVE; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_11 __CODEX_SNAPSHOT_PROXY_OVERRIDE_11 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_11 __CODEX_SNAPSHOT_PROXY_OVERRIDE_11 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_12}" ]; then   if [ -z "${CURL_CA_BUNDLE+x}" ] || [ "${CURL_CA_BUNDLE-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_12}" ]; then export CURL_CA_BUNDLE="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_12}"; else export CURL_CA_BUNDLE; fi else builtin unset CURL_CA_BUNDLE 2>/dev/null || command unset CURL_CA_BUNDLE; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_12 __CODEX_SNAPSHOT_PROXY_OVERRIDE_12 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_12 __CODEX_SNAPSHOT_PROXY_OVERRIDE_12 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_13}" ]; then   if [ -z "${DOCKER_HTTPS_PROXY+x}" ] || [ "${DOCKER_HTTPS_PROXY-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_13}" ]; then export DOCKER_HTTPS_PROXY="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_13}"; else export DOCKER_HTTPS_PROXY; fi else builtin unset DOCKER_HTTPS_PROXY 2>/dev/null || command unset DOCKER_HTTPS_PROXY; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_13 __CODEX_SNAPSHOT_PROXY_OVERRIDE_13 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_13 __CODEX_SNAPSHOT_PROXY_OVERRIDE_13 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_14}" ]; then   if [ -z "${DOCKER_HTTP_PROXY+x}" ] || [ "${DOCKER_HTTP_PROXY-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_14}" ]; then export DOCKER_HTTP_PROXY="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_14}"; else export DOCKER_HTTP_PROXY; fi else builtin unset DOCKER_HTTP_PROXY 2>/dev/null || command unset DOCKER_HTTP_PROXY; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_14 __CODEX_SNAPSHOT_PROXY_OVERRIDE_14 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_14 __CODEX_SNAPSHOT_PROXY_OVERRIDE_14 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_15}" ]; then   if [ -z "${ELECTRON_GET_USE_PROXY+x}" ] || [ "${ELECTRON_GET_USE_PROXY-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_15}" ]; then export ELECTRON_GET_USE_PROXY="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_15}"; else export ELECTRON_GET_USE_PROXY; fi else builtin unset ELECTRON_GET_USE_PROXY 2>/dev/null || command unset ELECTRON_GET_USE_PROXY; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_15 __CODEX_SNAPSHOT_PROXY_OVERRIDE_15 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_15 __CODEX_SNAPSHOT_PROXY_OVERRIDE_15 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_16}" ]; then   if [ -z "${FTP_PROXY+x}" ] || [ "${FTP_PROXY-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_16}" ]; then export FTP_PROXY="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_16}"; else export FTP_PROXY; fi else builtin unset FTP_PROXY 2>/dev/null || command unset FTP_PROXY; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_16 __CODEX_SNAPSHOT_PROXY_OVERRIDE_16 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_16 __CODEX_SNAPSHOT_PROXY_OVERRIDE_16 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_17}" ]; then   if [ -z "${GIT_SSL_CAINFO+x}" ] || [ "${GIT_SSL_CAINFO-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_17}" ]; then export GIT_SSL_CAINFO="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_17}"; else export GIT_SSL_CAINFO; fi else builtin unset GIT_SSL_CAINFO 2>/dev/null || command unset GIT_SSL_CAINFO; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_17 __CODEX_SNAPSHOT_PROXY_OVERRIDE_17 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_17 __CODEX_SNAPSHOT_PROXY_OVERRIDE_17 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_18}" ]; then   if [ -z "${HTTPS_PROXY+x}" ] || [ "${HTTPS_PROXY-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_18}" ]; then export HTTPS_PROXY="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_18}"; else export HTTPS_PROXY; fi else builtin unset HTTPS_PROXY 2>/dev/null || command unset HTTPS_PROXY; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_18 __CODEX_SNAPSHOT_PROXY_OVERRIDE_18 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_18 __CODEX_SNAPSHOT_PROXY_OVERRIDE_18 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_19}" ]; then   if [ -z "${HTTP_PROXY+x}" ] || [ "${HTTP_PROXY-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_19}" ]; then export HTTP_PROXY="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_19}"; else export HTTP_PROXY; fi else builtin unset HTTP_PROXY 2>/dev/null || command unset HTTP_PROXY; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_19 __CODEX_SNAPSHOT_PROXY_OVERRIDE_19 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_19 __CODEX_SNAPSHOT_PROXY_OVERRIDE_19 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_20}" ]; then   if [ -z "${NODE_EXTRA_CA_CERTS+x}" ] || [ "${NODE_EXTRA_CA_CERTS-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_20}" ]; then export NODE_EXTRA_CA_CERTS="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_20}"; else export NODE_EXTRA_CA_CERTS; fi else builtin unset NODE_EXTRA_CA_CERTS 2>/dev/null || command unset NODE_EXTRA_CA_CERTS; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_20 __CODEX_SNAPSHOT_PROXY_OVERRIDE_20 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_20 __CODEX_SNAPSHOT_PROXY_OVERRIDE_20 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_21}" ]; then   if [ -z "${NODE_USE_ENV_PROXY+x}" ] || [ "${NODE_USE_ENV_PROXY-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_21}" ]; then export NODE_USE_ENV_PROXY="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_21}"; else export NODE_USE_ENV_PROXY; fi else builtin unset NODE_USE_ENV_PROXY 2>/dev/null || command unset NODE_USE_ENV_PROXY; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_21 __CODEX_SNAPSHOT_PROXY_OVERRIDE_21 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_21 __CODEX_SNAPSHOT_PROXY_OVERRIDE_21 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_22}" ]; then   if [ -z "${NO_PROXY+x}" ] || [ "${NO_PROXY-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_22}" ]; then export NO_PROXY="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_22}"; else export NO_PROXY; fi else builtin unset NO_PROXY 2>/dev/null || command unset NO_PROXY; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_22 __CODEX_SNAPSHOT_PROXY_OVERRIDE_22 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_22 __CODEX_SNAPSHOT_PROXY_OVERRIDE_22 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_23}" ]; then   if [ -z "${NPM_CONFIG_CAFILE+x}" ] || [ "${NPM_CONFIG_CAFILE-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_23}" ]; then export NPM_CONFIG_CAFILE="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_23}"; else export NPM_CONFIG_CAFILE; fi else builtin unset NPM_CONFIG_CAFILE 2>/dev/null || command unset NPM_CONFIG_CAFILE; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_23 __CODEX_SNAPSHOT_PROXY_OVERRIDE_23 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_23 __CODEX_SNAPSHOT_PROXY_OVERRIDE_23 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_24}" ]; then   if [ -z "${NPM_CONFIG_HTTPS_PROXY+x}" ] || [ "${NPM_CONFIG_HTTPS_PROXY-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_24}" ]; then export NPM_CONFIG_HTTPS_PROXY="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_24}"; else export NPM_CONFIG_HTTPS_PROXY; fi else builtin unset NPM_CONFIG_HTTPS_PROXY 2>/dev/null || command unset NPM_CONFIG_HTTPS_PROXY; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_24 __CODEX_SNAPSHOT_PROXY_OVERRIDE_24 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_24 __CODEX_SNAPSHOT_PROXY_OVERRIDE_24 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_25}" ]; then   if [ -z "${NPM_CONFIG_HTTP_PROXY+x}" ] || [ "${NPM_CONFIG_HTTP_PROXY-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_25}" ]; then export NPM_CONFIG_HTTP_PROXY="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_25}"; else export NPM_CONFIG_HTTP_PROXY; fi else builtin unset NPM_CONFIG_HTTP_PROXY 2>/dev/null || command unset NPM_CONFIG_HTTP_PROXY; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_25 __CODEX_SNAPSHOT_PROXY_OVERRIDE_25 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_25 __CODEX_SNAPSHOT_PROXY_OVERRIDE_25 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_26}" ]; then   if [ -z "${NPM_CONFIG_NOPROXY+x}" ] || [ "${NPM_CONFIG_NOPROXY-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_26}" ]; then export NPM_CONFIG_NOPROXY="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_26}"; else export NPM_CONFIG_NOPROXY; fi else builtin unset NPM_CONFIG_NOPROXY 2>/dev/null || command unset NPM_CONFIG_NOPROXY; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_26 __CODEX_SNAPSHOT_PROXY_OVERRIDE_26 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_26 __CODEX_SNAPSHOT_PROXY_OVERRIDE_26 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_27}" ]; then   if [ -z "${NPM_CONFIG_PROXY+x}" ] || [ "${NPM_CONFIG_PROXY-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_27}" ]; then export NPM_CONFIG_PROXY="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_27}"; else export NPM_CONFIG_PROXY; fi else builtin unset NPM_CONFIG_PROXY 2>/dev/null || command unset NPM_CONFIG_PROXY; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_27 __CODEX_SNAPSHOT_PROXY_OVERRIDE_27 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_27 __CODEX_SNAPSHOT_PROXY_OVERRIDE_27 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_28}" ]; then   if [ -z "${PIP_CERT+x}" ] || [ "${PIP_CERT-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_28}" ]; then export PIP_CERT="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_28}"; else export PIP_CERT; fi else builtin unset PIP_CERT 2>/dev/null || command unset PIP_CERT; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_28 __CODEX_SNAPSHOT_PROXY_OVERRIDE_28 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_28 __CODEX_SNAPSHOT_PROXY_OVERRIDE_28 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_29}" ]; then   if [ -z "${PIP_PROXY+x}" ] || [ "${PIP_PROXY-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_29}" ]; then export PIP_PROXY="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_29}"; else export PIP_PROXY; fi else builtin unset PIP_PROXY 2>/dev/null || command unset PIP_PROXY; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_29 __CODEX_SNAPSHOT_PROXY_OVERRIDE_29 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_29 __CODEX_SNAPSHOT_PROXY_OVERRIDE_29 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_30}" ]; then   if [ -z "${REQUESTS_CA_BUNDLE+x}" ] || [ "${REQUESTS_CA_BUNDLE-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_30}" ]; then export REQUESTS_CA_BUNDLE="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_30}"; else export REQUESTS_CA_BUNDLE; fi else builtin unset REQUESTS_CA_BUNDLE 2>/dev/null || command unset REQUESTS_CA_BUNDLE; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_30 __CODEX_SNAPSHOT_PROXY_OVERRIDE_30 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_30 __CODEX_SNAPSHOT_PROXY_OVERRIDE_30 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_31}" ]; then   if [ -z "${SSL_CERT_FILE+x}" ] || [ "${SSL_CERT_FILE-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_31}" ]; then export SSL_CERT_FILE="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_31}"; else export SSL_CERT_FILE; fi else builtin unset SSL_CERT_FILE 2>/dev/null || command unset SSL_CERT_FILE; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_31 __CODEX_SNAPSHOT_PROXY_OVERRIDE_31 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_31 __CODEX_SNAPSHOT_PROXY_OVERRIDE_31 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_32}" ]; then   if [ -z "${WSS_PROXY+x}" ] || [ "${WSS_PROXY-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_32}" ]; then export WSS_PROXY="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_32}"; else export WSS_PROXY; fi else builtin unset WSS_PROXY 2>/dev/null || command unset WSS_PROXY; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_32 __CODEX_SNAPSHOT_PROXY_OVERRIDE_32 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_32 __CODEX_SNAPSHOT_PROXY_OVERRIDE_32 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_33}" ]; then   if [ -z "${WS_PROXY+x}" ] || [ "${WS_PROXY-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_33}" ]; then export WS_PROXY="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_33}"; else export WS_PROXY; fi else builtin unset WS_PROXY 2>/dev/null || command unset WS_PROXY; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_33 __CODEX_SNAPSHOT_PROXY_OVERRIDE_33 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_33 __CODEX_SNAPSHOT_PROXY_OVERRIDE_33 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_34}" ]; then   if [ -z "${YARN_HTTPS_PROXY+x}" ] || [ "${YARN_HTTPS_PROXY-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_34}" ]; then export YARN_HTTPS_PROXY="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_34}"; else export YARN_HTTPS_PROXY; fi else builtin unset YARN_HTTPS_PROXY 2>/dev/null || command unset YARN_HTTPS_PROXY; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_34 __CODEX_SNAPSHOT_PROXY_OVERRIDE_34 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_34 __CODEX_SNAPSHOT_PROXY_OVERRIDE_34 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_35}" ]; then   if [ -z "${YARN_HTTP_PROXY+x}" ] || [ "${YARN_HTTP_PROXY-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_35}" ]; then export YARN_HTTP_PROXY="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_35}"; else export YARN_HTTP_PROXY; fi else builtin unset YARN_HTTP_PROXY 2>/dev/null || command unset YARN_HTTP_PROXY; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_35 __CODEX_SNAPSHOT_PROXY_OVERRIDE_35 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_35 __CODEX_SNAPSHOT_PROXY_OVERRIDE_35 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_36}" ]; then   if [ -z "${YARN_NO_PROXY+x}" ] || [ "${YARN_NO_PROXY-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_36}" ]; then export YARN_NO_PROXY="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_36}"; else export YARN_NO_PROXY; fi else builtin unset YARN_NO_PROXY 2>/dev/null || command unset YARN_NO_PROXY; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_36 __CODEX_SNAPSHOT_PROXY_OVERRIDE_36 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_36 __CODEX_SNAPSHOT_PROXY_OVERRIDE_36 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_37}" ]; then   if [ -z "${all_proxy+x}" ] || [ "${all_proxy-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_37}" ]; then export all_proxy="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_37}"; else export all_proxy; fi else builtin unset all_proxy 2>/dev/null || command unset all_proxy; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_37 __CODEX_SNAPSHOT_PROXY_OVERRIDE_37 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_37 __CODEX_SNAPSHOT_PROXY_OVERRIDE_37 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_38}" ]; then   if [ -z "${ftp_proxy+x}" ] || [ "${ftp_proxy-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_38}" ]; then export ftp_proxy="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_38}"; else export ftp_proxy; fi else builtin unset ftp_proxy 2>/dev/null || command unset ftp_proxy; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_38 __CODEX_SNAPSHOT_PROXY_OVERRIDE_38 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_38 __CODEX_SNAPSHOT_PROXY_OVERRIDE_38 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_39}" ]; then   if [ -z "${http_proxy+x}" ] || [ "${http_proxy-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_39}" ]; then export http_proxy="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_39}"; else export http_proxy; fi else builtin unset http_proxy 2>/dev/null || command unset http_proxy; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_39 __CODEX_SNAPSHOT_PROXY_OVERRIDE_39 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_39 __CODEX_SNAPSHOT_PROXY_OVERRIDE_39 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_40}" ]; then   if [ -z "${https_proxy+x}" ] || [ "${https_proxy-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_40}" ]; then export https_proxy="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_40}"; else export https_proxy; fi else builtin unset https_proxy 2>/dev/null || command unset https_proxy; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_40 __CODEX_SNAPSHOT_PROXY_OVERRIDE_40 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_40 __CODEX_SNAPSHOT_PROXY_OVERRIDE_40 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_41}" ]; then   if [ -z "${no_proxy+x}" ] || [ "${no_proxy-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_41}" ]; then export no_proxy="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_41}"; else export no_proxy; fi else builtin unset no_proxy 2>/dev/null || command unset no_proxy; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_41 __CODEX_SNAPSHOT_PROXY_OVERRIDE_41 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_41 __CODEX_SNAPSHOT_PROXY_OVERRIDE_41 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_42}" ]; then   if [ -z "${npm_config_cafile+x}" ] || [ "${npm_config_cafile-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_42}" ]; then export npm_config_cafile="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_42}"; else export npm_config_cafile; fi else builtin unset npm_config_cafile 2>/dev/null || command unset npm_config_cafile; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_42 __CODEX_SNAPSHOT_PROXY_OVERRIDE_42 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_42 __CODEX_SNAPSHOT_PROXY_OVERRIDE_42 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_43}" ]; then   if [ -z "${npm_config_http_proxy+x}" ] || [ "${npm_config_http_proxy-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_43}" ]; then export npm_config_http_proxy="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_43}"; else export npm_config_http_proxy; fi else builtin unset npm_config_http_proxy 2>/dev/null || command unset npm_config_http_proxy; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_43 __CODEX_SNAPSHOT_PROXY_OVERRIDE_43 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_43 __CODEX_SNAPSHOT_PROXY_OVERRIDE_43 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_44}" ]; then   if [ -z "${npm_config_https_proxy+x}" ] || [ "${npm_config_https_proxy-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_44}" ]; then export npm_config_https_proxy="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_44}"; else export npm_config_https_proxy; fi else builtin unset npm_config_https_proxy 2>/dev/null || command unset npm_config_https_proxy; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_44 __CODEX_SNAPSHOT_PROXY_OVERRIDE_44 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_44 __CODEX_SNAPSHOT_PROXY_OVERRIDE_44 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_45}" ]; then   if [ -z "${npm_config_noproxy+x}" ] || [ "${npm_config_noproxy-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_45}" ]; then export npm_config_noproxy="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_45}"; else export npm_config_noproxy; fi else builtin unset npm_config_noproxy 2>/dev/null || command unset npm_config_noproxy; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_45 __CODEX_SNAPSHOT_PROXY_OVERRIDE_45 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_45 __CODEX_SNAPSHOT_PROXY_OVERRIDE_45 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_46}" ]; then   if [ -z "${npm_config_proxy+x}" ] || [ "${npm_config_proxy-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_46}" ]; then export npm_config_proxy="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_46}"; else export npm_config_proxy; fi else builtin unset npm_config_proxy 2>/dev/null || command unset npm_config_proxy; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_46 __CODEX_SNAPSHOT_PROXY_OVERRIDE_46 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_46 __CODEX_SNAPSHOT_PROXY_OVERRIDE_46 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_47}" ]; then   if [ -z "${ws_proxy+x}" ] || [ "${ws_proxy-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_47}" ]; then export ws_proxy="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_47}"; else export ws_proxy; fi else builtin unset ws_proxy 2>/dev/null || command unset ws_proxy; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_47 __CODEX_SNAPSHOT_PROXY_OVERRIDE_47 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_47 __CODEX_SNAPSHOT_PROXY_OVERRIDE_47 if [ -n "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_48}" ]; then   if [ -z "${wss_proxy+x}" ] || [ "${wss_proxy-}" != "${__CODEX_SNAPSHOT_PROXY_OVERRIDE_48}" ]; then export wss_proxy="${__CODEX_SNAPSHOT_PROXY_OVERRIDE_48}"; else export wss_proxy; fi else builtin unset wss_proxy 2>/dev/null || command unset wss_proxy; fi builtin unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_48 __CODEX_SNAPSHOT_PROXY_OVERRIDE_48 2>/dev/null || command unset __CODEX_SNAPSHOT_PROXY_OVERRIDE_SET_48 __CODEX_SNAPSHOT_PROXY_OVERRIDE_48 fi if [ -n "${PATH:-}" ]; then export PATH='/home/hadoop/.codex/packages/app-server-daemon/releases/0.159.2-x86_64-unknown-linux-musl/codex-path':"$PATH"; else export PATH='/home/hadoop/.codex/packages/app-server-daemon/releases/0.159.2-x86_64-unknown-linux-musl/codex-path'; fi  exec '/bin/bash' -c 'ss -lnt ps -eo pid,comm,args'
          2 ps              ps -eo pid,comm,args
    ✓ • 68ms

## Activity

    $ python3 - <<'PY'
        p='stream_to_db.py';s=open(p).read().replace('import resource','import resource\nimport re');s=s.replace('    with conn.cursor() as cur:\n        cur.execute("SELECT stats', '    with conn.cursor(name="chunk_summary") as cur:\n        cur.execute("SELECT stats')
        s=s.replace('        ranged = start_offset > 0 and status == 206', '''        if status not in (200, 206):
                    raise IOError(f"unexpected HTTP status: {status}")
                ranged = start_offset > 0 and status == 206''')
        s=s.replace('            if not content_range.startswith(f"bytes {start_offset}-"):', '            match = re.fullmatch(r"bytes (\\d+)-(\\d+)/(\\d+)", content_range)\n            if not match or int(match[1]) != start_offset or int(match[2]) != int(match[3]) - 1:')
        s=s.replace('        candidates, result_bytes = [], 0','        candidates, result_bytes = [], 0\n        found_start = start_offset == 0')
        s=s.replace('                clean_eof = False','                clean_eof = False\n                if next_offset <= current["start_offset"]:\n                    raise IOError("WARC must have one record per gzip member for resumable offsets")')
        s=s.replace('            stats["records"] += 1', '''            if not found_start:
                        if current["start_offset"] != start_offset:
                            raise IOError("saved cursor does not match a source record boundary")
                        found_start = True
                    stats["records"] += 1''')
        # Check real compressed read traffic telemetry on all successful results.
        s=s.replace('"stats": stats, "error": None,','"stats": dict(stats, compressed_bytes_read=checked_stream.bytes_read), "error": None,')
        open(p,'w').write(s)
        p='db/db_handler.py';s=open(p).read().replace('    ALTER TABLE pages ADD COLUMN IF NOT EXISTS author_id','    ALTER TABLE ingest_files ADD COLUMN IF NOT EXISTS checkpoint_version INT NOT NULL DEFAULT 1;\n    ALTER TABLE ingest_files ADD COLUMN IF NOT EXISTS etag TEXT;\n    ALTER TABLE ingest_files ADD COLUMN IF NOT EXISTS last_modified TEXT;\n    ALTER TABLE pages ADD COLUMN IF NOT EXISTS author_id')
        a=s.index('            cur.execute("SELECT file_url FROM ingest_files');b=s.index('\n        conn.commit()',a)
        s=s[:a]+'''            cur.execute("SELECT file_url,complete,bytes_done,checkpoint_version,etag,last_modified FROM ingest_files WHERE manifest_id=%s", (manifest_id,))
                    previous = {row[0]: row[1:] for row in cur.fetchall()}
                    rows = []
                    for i, url in enumerate(urls):
                        complete, offset, version, etag, modified = previous.get(url, (False, 0, 1, None, None))
                        rows.append((run_id, i, url, complete, "eof" if complete else "pending",
                                     offset if version >= 2 else 0, etag if version >= 2 else None,
                                     modified if version >= 2 else None))
                    if rows:
                        execute_values(cur, "INSERT INTO ingest_run_files (run_id,ordinal,file_url,eof,status,next_offset,etag,last_modified) VALUES %s", rows)'''+s[b:]
        s=s.replace('            candidates = result["candidates"][:min(len(result["candidates"]), total_left, file_left)]','''            candidates = list({r["record_id"]: r for r in result["candidates"]}.values())
                    if len(candidates) > min(total_left, file_left):
                        raise ValueError("chunk exceeded its remaining quota; refusing to discard uncommitted candidates")''')
        s=s.replace('INSERT INTO ingest_files (file_url,manifest_id,bytes_done,articles_done,complete)\n                SELECT %s,manifest_id,%s,%s,%s FROM ingest_runs WHERE run_id=%s','INSERT INTO ingest_files (file_url,manifest_id,bytes_done,articles_done,complete,checkpoint_version,etag,last_modified)\n                SELECT %s,manifest_id,%s,%s,%s,2,%s,%s FROM ingest_runs WHERE run_id=%s')
        s=s.replace('bytes_done=GREATEST(ingest_files.bytes_done,EXCLUDED.bytes_done),\n                articles_done=ingest_files.articles_done+EXCLUDED.articles_done,','''bytes_done=CASE WHEN ingest_files.checkpoint_version<2 THEN EXCLUDED.bytes_done
                            ELSE GREATEST(ingest_files.bytes_done,EXCLUDED.bytes_done) END,
                        checkpoint_version=2,etag=COALESCE(EXCLUDED.etag,ingest_files.etag),
                        last_modified=COALESCE(EXCLUDED.last_modified,ingest_files.last_modified),
                        articles_done=ingest_files.articles_done+EXCLUDED.articles_done,''')
        s=s.replace('(result["file_url"], result["next_offset"], inserted_count, eof, run_id))','(result["file_url"], result["next_offset"], inserted_count, eof, result.get("etag"), result.get("last_modified"), run_id))')
        # Failed attempts must not promote an unreliable legacy offset to a v2 cursor.
        s=s.replace('            cur.execute("""INSERT INTO ingest_files (file_url,manifest_id,bytes_done,articles_done,complete,checkpoint_version,etag,last_modified)', '            if not failure:\n                cur.execute("""INSERT INTO ingest_files (file_url,manifest_id,bytes_done,articles_done,complete,checkpoint_version,etag,last_modified)')
        open(p,'w').write(s)
        PY
    ✓ • 0ms

## Activity

    $ cat > tests/spark_smoke.py <<'PY'
        """Local Spark integration smoke: real HTTP, extraction, Lingua, and PostgreSQL.
        
        Run with spark-submit --master 'local[3]' --driver-memory 512m
        --conf spark.eventLog.enabled=false tests/spark_smoke.py.
        Requires WARC_TEST_DSN, and uses an isolated disposable schema.
        """
        import io
        import json
        import os
        from pathlib import Path
        import sys
        import tempfile
        import threading
        import time
        import uuid
        from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
        from unittest.mock import patch
        
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from pyspark.sql import SparkSession
        import psycopg2
        from tests.test_ingestion import make_warc
        import stream_to_db as job
        from db import db_handler as db
        
        
        def timed_chunk(task):
            import time
            import stream_to_db
            start = time.time()
            result = stream_to_db.process_file_chunk(task)
            result['stats']['wall_start'] = start
            result['stats']['wall_end'] = time.time()
            return result
        
        
        def main():
            dsn = os.environ['WARC_TEST_DSN']
            data = {f'/file-{i}.warc.gz': make_warc(12)[0] for i in range(3)}
            class Handler(BaseHTTPRequestHandler):
                def do_GET(self):
                    body = data.get(self.path)
                    if body is None:
                        self.send_error(404); return
                    value = self.headers.get('Range')
                    offset = int(value.split('=')[1].split('-')[0]) if value else 0
                    self.send_response(206 if offset else 200)
                    self.send_header('Content-Length', str(len(body)-offset))
                    self.send_header('ETag', 'test-v1')
                    if offset:
                        self.send_header('Content-Range', f'bytes {offset}-{len(body)-1}/{len(body)}')
                    self.end_headers()
                    self.wfile.write(body[offset:])
                def log_message(self, *args): pass
            server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
            threading.Thread(target=server.serve_forever, daemon=True).start()
            schema = 'spark_smoke_' + uuid.uuid4().hex
            admin = psycopg2.connect(dsn); admin.autocommit = True
            with admin.cursor() as cur: cur.execute('CREATE SCHEMA ' + schema)
            def connect(): return psycopg2.connect(dsn, options='-c search_path='+schema)
            spark = SparkSession.builder.appName('WARC-v2-fixture-smoke').getOrCreate()
            spark.sparkContext.setLogLevel('ERROR')
            # Imported task functions must be available to the real Python workers.
            spark.sparkContext.addPyFile(str(Path(job.__file__)))
            try:
                with patch.object(db, 'get_connection', side_effect=connect), patch.object(job, 'get_spark_session', return_value=spark), \
                     patch.object(spark, 'stop'), patch.object(job, 'process_file_chunk', timed_chunk):
                    urls = [f'http://127.0.0.1:{server.server_port}{path}' for path in data]
                    settings = job.load_config()
                    settings.update(target_articles=7, per_file_target=3, worker_max_candidates=2,
                                    max_files_per_round=3, use_trafilatura=False)
                    with patch.object(job, 'load_config', return_value=settings), patch.object(job, 'fetch_manifest', return_value=urls):
                        started = time.monotonic()
                        assert job.run_streaming_pipeline() == 0
                    with connect() as conn, conn.cursor() as cur:
                        cur.execute('SELECT inserted_count FROM ingest_runs')
                        assert cur.fetchone()[0] == 7
                        cur.execute('SELECT inserted_count FROM ingest_run_files ORDER BY ordinal')
                        counts = [row[0] for row in cur.fetchall()]
                        assert sum(counts) == 7 and max(counts) <= 3, counts
                        cur.execute('SELECT stats FROM ingest_chunks ORDER BY committed_at')
                        stats = [row[0] for row in cur.fetchall()]
                    first_wave = stats[:3]
                    assert max(s['wall_start'] for s in first_wave) < min(s['wall_end'] for s in first_wave), first_wave
                    print('SPARK_SMOKE_RESULT ' + json.dumps(dict(
                        articles=7, per_file=counts, parallel_workers=len({s['worker_pid'] for s in first_wave}),
                        seconds=round(time.monotonic()-started, 2),
                        worker_peak_rss_mib=[s['python_peak_rss_mib'] for s in first_wave])))
            finally:
                spark.stop()
                server.shutdown(); server.server_close()
                with admin.cursor() as cur: cur.execute('DROP SCHEMA ' + schema + ' CASCADE')
                admin.close()
        
        
        if __name__ == '__main__': main()
        PY
        touch tests/__init__.py
        python3 -m py_compile stream_to_db.py db/db_handler.py tests/spark_smoke.py
        DRY_RUN=1 VENV_DIR=../spark_warc_project/.venv ./run_to_db.sh
    {
      "db_batch_size": 25,
      "lingua_min_confidence": 0.5,
      "manifest_id": "2026/05",
      "max_article_bytes": 524288,
      "max_files_per_round": 3,
      "max_html_bytes": 2097152,
      "max_retries": 3,
      "min_word_count": 80,
      "month": "05",
      "num_files": 15,
      "per_file_target": 0,
      "start_file_offset": 0,
      "target_articles": 0,
      "use_trafilatura": true,
      "worker_max_candidates": 100,
      "worker_max_input_bytes": 33554432,
      "worker_max_result_bytes": 4194304,
      "worker_max_seconds": 120,
      "year": "2026"
    }
    ✓ • 174ms

## Assistant

The 20-language detector used about 80 MiB peak RSS in a six-language fixture check and correctly accepted English, French, and Arabic while rejecting the other samples. YARN’s ResourceManager timed out even outside the sandbox, so I’m using a local three-worker Spark smoke test to verify concurrency and end-to-end inserts. Cluster validation remains pending.

## Activity

    $ WARC_TEST_DSN='host=/tmp/warc-v2-test-pg port=55439 dbname=postgres user=hadoop' PYSPARK_PYTHON=/home/spark-master/rag_news_project/spark_warc_project/.venv/bin/python PYSPARK_DRIVER_PYTHON=/home/spark-master/rag_news_project/spark_warc_project/.venv/bin/python RAYON_NUM_THREADS=1 SPARK_LOCAL_IP=127.0.0.1 spark-submit --master 'local[3]' --driver-memory 512m --conf spark.eventLog.enabled=false --conf spark.ui.enabled=false --conf spark.driver.host=127.0.0.1 tests/spark_smoke.py > /tmp/warc-v2-spark-smoke.log 2>&1
    ✗ (1) • 5.82s

## Activity

    $ cat > README.md <<'MD'
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
        | `MAX_HTML_BYTES` | `2097152` | Maximum decoded HTML body (2 MiB) |
        | `MAX_ARTICLE_BYTES` | `524288` | Maximum serialized article (512 KiB) |
        | `MIN_WORD_COUNT` | `80` | Minimum extracted article words |
        | `USE_TRAFILATURA` | `1` | Main-content extraction before selectolax fallback |
        | `LINGUA_MIN_CONFIDENCE` | `0.5` | Minimum language confidence |
        | `DB_BATCH_SIZE` | `25` | Rows per SQL insertion batch within a chunk |
        | `MAX_RETRIES` | `3` | Total attempts per download/commit |
        | `NO_PROGRESS` | `0` | `1` hides per-wave progress; final summary remains |
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
        
        `langchain.py` is a compatibility import shim. The eager
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
          --conf spark.eventLog.enabled=false tests/spark_smoke.py
        ```
        
        This also requires `WARC_TEST_DSN`. It is a local integration test, not evidence of
        YARN container health. After code/dependency changes, run the capped one-file smoke
        above, then a three-file request (`NUM_FILES=3 MAX_ACCEPTED_ARTICLES=9
        MAX_ACCEPTED_PER_FILE=3`). See `VALIDATION.md` for the checks actually performed.
        
        Exit codes: **0** target reached (or uncapped selection finished), **1** operational
        failure, **2** selected sources cannot fulfill the requested target. The final
        summary includes committed counts, per-file statuses, rejection counters, and resume
        command. Stop/failure before commit replays that chunk; successful chunks persist.
        MD
    ✓ • 0ms

## Activity

    $ tail -n 65 /tmp/warc-v2-spark-smoke.log
    WARNING: Using incubator modules: jdk.incubator.vector
    Traceback (most recent call last):
      File "/home/spark-master/rag_news_project/spark_warc_v2/tests/spark_smoke.py", line 21, in <module>
        import psycopg2
    ModuleNotFoundError: No module named 'psycopg2'
    ✓ • 0ms

## Activity

    $ rg -n 'PYSPARK|PYTHON' /opt/spark/conf/spark-env.sh
        ls -l .venv/bin/python
        du -sh /tmp/warc-v2-pip-cache
    85:export PYSPARK_PYTHON=/usr/bin/python3
    86:export PYSPARK_DRIVER_PYTHON=/usr/bin/python3
    lrwxrwxrwx 1 hadoop hadoop 7 Sep 30 11:12 .venv/bin/python -> python3
    8.0M    /tmp/warc-v2-pip-cache
    ✓ • 0ms

## Activity

    $ WARC_TEST_DSN='host=/tmp/warc-v2-test-pg port=55439 dbname=postgres user=hadoop' RAYON_NUM_THREADS=1 SPARK_LOCAL_IP=127.0.0.1 spark-submit --master 'local[3]' --driver-memory 512m --conf spark.eventLog.enabled=false --conf spark.ui.enabled=false --conf spark.driver.host=127.0.0.1 --conf spark.pyspark.python=/home/spark-master/rag_news_project/spark_warc_project/.venv/bin/python --conf spark.pyspark.driver.python=/home/spark-master/rag_news_project/spark_warc_project/.venv/bin/python tests/spark_smoke.py > /tmp/warc-v2-spark-smoke.log 2>&1
    ✓ • 12.14s

## Activity

    $ .venv/bin/python -m pip install --cache-dir /tmp/warc-v2-pip-cache -r requirements-dev.txt
    Collecting FastWARC==1.0.9 (from -r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 2))
      Downloading fastwarc-1.0.9-cp313-cp313-manylinux_2_28_x86_64.whl.metadata (4.1 kB)
    Collecting charset-normalizer<4,>=3.4 (from -r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 3))
      Downloading charset_normalizer-3.5.2-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (46 kB)
    Collecting lingua-language-detector==2.2.0 (from -r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 4))
      Downloading lingua_language_detector-2.2.0-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (31 kB)
    Collecting psycopg2-binary<3,>=2.9 (from -r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 5))
      Downloading psycopg2_binary-2.9.13-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.whl.metadata (4.9 kB)
    Collecting selectolax<0.5,>=0.3 (from -r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 6))
      Downloading selectolax-0.4.13-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (8.2 kB)
    Collecting trafilatura<3,>=2 (from -r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 7))
      Downloading trafilatura-2.2.0-py3-none-any.whl.metadata (13 kB)
    Collecting venv-pack==0.2.0 (from -r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 8))
      Downloading venv_pack-0.2.0-py2.py3-none-any.whl.metadata (1.7 kB)
    Collecting warcio<2,>=1.7 (from -r requirements-dev.txt (line 2))
      Downloading warcio-1.8.1-py2.py3-none-any.whl.metadata (18 kB)
    Collecting brotli (from FastWARC==1.0.9->-r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 2))
      Downloading brotli-1.2.0-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.whl.metadata (6.1 kB)
    Collecting click (from FastWARC==1.0.9->-r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 2))
      Downloading click-8.5.0-py3-none-any.whl.metadata (2.6 kB)
    Collecting tqdm (from FastWARC==1.0.9->-r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 2))
      Downloading tqdm-4.70.1-py3-none-any.whl.metadata (57 kB)
    Collecting certifi (from trafilatura<3,>=2->-r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 7))
      Downloading certifi-2026.7.22-py3-none-any.whl.metadata (2.5 kB)
    Collecting courlan>=1.4.0 (from trafilatura<3,>=2->-r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 7))
      Downloading courlan-1.4.0-py3-none-any.whl.metadata (18 kB)
    Collecting htmldate>=1.10.0 (from trafilatura<3,>=2->-r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 7))
      Downloading htmldate-1.10.0-py3-none-any.whl.metadata (9.8 kB)
    Collecting justext>=3.0.2 (from trafilatura<3,>=2->-r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 7))
      Downloading justext-3.0.2-py2.py3-none-any.whl.metadata (7.3 kB)
    Collecting lxml>=6.1.1 (from trafilatura<3,>=2->-r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 7))
      Downloading lxml-6.1.3-cp313-cp313-manylinux_2_26_x86_64.manylinux_2_28_x86_64.whl.metadata (3.3 kB)
    Collecting urllib3<3,>=1.26 (from trafilatura<3,>=2->-r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 7))
      Downloading urllib3-2.8.0-py3-none-any.whl.metadata (7.4 kB)
    Collecting six (from warcio<2,>=1.7->-r requirements-dev.txt (line 2))
      Downloading six-1.17.0-py2.py3-none-any.whl.metadata (1.7 kB)
    Collecting babel>=2.16.0 (from courlan>=1.4.0->trafilatura<3,>=2->-r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 7))
      Downloading babel-2.18.0-py3-none-any.whl.metadata (2.2 kB)
    Collecting tld>=0.13 (from courlan>=1.4.0->trafilatura<3,>=2->-r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 7))
      Downloading tld-0.13.2-py2.py3-none-any.whl.metadata (11 kB)
    Collecting dateparser>=1.1.2 (from htmldate>=1.10.0->trafilatura<3,>=2->-r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 7))
      Downloading dateparser-1.4.3-py3-none-any.whl.metadata (25 kB)
    Collecting python-dateutil>=2.9.0.post0 (from htmldate>=1.10.0->trafilatura<3,>=2->-r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 7))
      Downloading python_dateutil-2.9.0.post0-py2.py3-none-any.whl.metadata (8.4 kB)
    Collecting pytz>=2024.2 (from dateparser>=1.1.2->htmldate>=1.10.0->trafilatura<3,>=2->-r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 7))
      Downloading pytz-2026.4-py2.py3-none-any.whl.metadata (22 kB)
    Collecting regex>=2024.9.11 (from dateparser>=1.1.2->htmldate>=1.10.0->trafilatura<3,>=2->-r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 7))
      Downloading regex-2026.9.29-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (40 kB)
    Collecting tzlocal>=0.2 (from dateparser>=1.1.2->htmldate>=1.10.0->trafilatura<3,>=2->-r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 7))
      Downloading tzlocal-5.4.4-py3-none-any.whl.metadata (7.7 kB)
    Collecting lxml_html_clean (from lxml[html_clean]>=4.4.2->justext>=3.0.2->trafilatura<3,>=2->-r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 7))
      Downloading lxml_html_clean-0.4.5-py3-none-any.whl.metadata (2.4 kB)
    Downloading fastwarc-1.0.9-cp313-cp313-manylinux_2_28_x86_64.whl (4.0 MB)
       ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.0/4.0 MB 450.1 kB/s eta 0:00:00
    Downloading lingua_language_detector-2.2.0-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (170.3 MB)
    ERROR: Could not install packages due to an OSError: [Errno 28] No space left on device
    
       ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╸ 170.1/170.3 MB 319.7 kB/s eta 0:00:01
    ✗ (1) • 7m 01s

## Activity

    $ tail -n 55 /tmp/warc-v2-spark-smoke.log
        cat /tmp/warc-v2-memory.json
    WARNING: Using incubator modules: jdk.incubator.vector
    Using Spark's default log4j profile: org/apache/spark/log4j2-defaults.properties
    26/09/30 11:20:12 INFO SparkContext: Running Spark version 4.2.0
    26/09/30 11:20:12 INFO SparkContext: OS info Linux, 6.12.107+deb13-amd64, amd64
    26/09/30 11:20:12 INFO SparkContext: Java version 21.0.12.1+1-1-deb13u1-Debian
    26/09/30 11:20:13 WARN NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable
    26/09/30 11:20:13 INFO ResourceUtils: ==============================================================
    26/09/30 11:20:13 INFO ResourceUtils: No custom resources configured for spark.driver.
    26/09/30 11:20:13 INFO ResourceUtils: ==============================================================
    26/09/30 11:20:13 INFO SparkContext: Submitted application: WARC-v2-fixture-smoke
    26/09/30 11:20:13 INFO SecurityManager: Changing view acls to: hadoop
    26/09/30 11:20:13 INFO SecurityManager: Changing modify acls to: hadoop
    26/09/30 11:20:13 INFO SecurityManager: Changing view acls groups to: hadoop
    26/09/30 11:20:13 INFO SecurityManager: Changing modify acls groups to: hadoop
    26/09/30 11:20:13 INFO SecurityManager: SecurityManager: authentication disabled; ui acls disabled; users with view permissions: hadoop groups with view permissions: EMPTY; users with modify permissions: hadoop; groups with modify permissions: EMPTY; RPC SSL disabled
    26/09/30 11:20:13 INFO Utils: Successfully started service 'sparkDriver' on port 35743.
    26/09/30 11:20:13 INFO SparkEnv: Registering MapOutputTracker
    26/09/30 11:20:13 INFO SparkEnv: Registering BlockManagerMaster
    26/09/30 11:20:13 INFO BlockManagerMasterEndpoint: Using org.apache.spark.storage.DefaultTopologyMapper for getting topology information
    26/09/30 11:20:13 INFO BlockManagerMasterEndpoint: BlockManagerMasterEndpoint up
    26/09/30 11:20:13 INFO SparkEnv: Registering BlockManagerMasterHeartbeat
    26/09/30 11:20:13 INFO DiskBlockManager: Created local directory at /tmp/blockmgr-f07bcba9-e9fc-4911-bbed-05299c6c7e6d
    26/09/30 11:20:13 INFO SparkEnv: Registering OutputCommitCoordinator
    26/09/30 11:20:13 INFO ResourceProfile: Default ResourceProfile created, executor resources: Map(cores -> name: cores, amount: 2, script: , vendor: , memory -> name: memory, amount: 2048, script: , vendor: , offHeap -> name: offHeap, amount: 0, script: , vendor: ), task resources: Map(cpus -> name: cpus, amount: 1.0)
    26/09/30 11:20:13 INFO ResourceProfile: Limiting resource is cpus at 2 tasks per executor
    26/09/30 11:20:13 INFO ResourceProfileManager: Added ResourceProfile id: 0
    26/09/30 11:20:14 INFO SecurityManager: Changing view acls to: hadoop
    26/09/30 11:20:14 INFO SecurityManager: Changing modify acls to: hadoop
    26/09/30 11:20:14 INFO SecurityManager: Changing view acls groups to: hadoop
    26/09/30 11:20:14 INFO SecurityManager: Changing modify acls groups to: hadoop
    26/09/30 11:20:14 INFO SecurityManager: SecurityManager: authentication disabled; ui acls disabled; users with view permissions: hadoop groups with view permissions: EMPTY; users with modify permissions: hadoop; groups with modify permissions: EMPTY; RPC SSL disabled
    26/09/30 11:20:14 INFO Executor: Starting executor ID driver on host localhost
    26/09/30 11:20:14 INFO Executor: Running Spark version 4.2.0
    26/09/30 11:20:14 INFO Executor: OS info Linux, 6.12.107+deb13-amd64, amd64
    26/09/30 11:20:14 INFO Executor: Java version 21.0.12.1+1-1-deb13u1-Debian
    26/09/30 11:20:14 INFO Executor: Starting executor with user classpath (userClassPathFirst = false): ''
    26/09/30 11:20:14 INFO Executor: Created or updated repl class loader org.apache.spark.util.MutableURLClassLoader@1b859b9f for default.
    26/09/30 11:20:14 INFO Utils: Successfully started service 'org.apache.spark.network.netty.NettyBlockTransferService' on port 39903.
    26/09/30 11:20:14 INFO NettyBlockTransferService: Server created on 127.0.0.1:39903
    26/09/30 11:20:14 INFO BlockManager: Using org.apache.spark.storage.RandomBlockReplicationPolicy for block replication policy
    26/09/30 11:20:14 INFO BlockManagerMaster: Registering BlockManager BlockManagerId(driver, 127.0.0.1, 39903, None)
    26/09/30 11:20:14 INFO BlockManagerMasterEndpoint: Registering block manager 127.0.0.1:39903 with 127.2 MiB RAM, BlockManagerId(driver, 127.0.0.1, 39903, None)
    26/09/30 11:20:14 INFO BlockManagerMaster: Registered BlockManager BlockManagerId(driver, 127.0.0.1, 39903, None)
    26/09/30 11:20:14 INFO BlockManager: Initialized BlockManager: BlockManagerId(driver, 127.0.0.1, 39903, None)
    Created ingestion run b44ee680-227d-4b52-aefa-b0ced7258754
    Resume command: RESUME_RUN_ID=b44ee680-227d-4b52-aefa-b0ced7258754 ./run_to_db.sh
    Wave 1: committed 6/7; new=6; worker peak RSS MiB=[84.2, 84.3, 84.1]
    Wave 2: committed 7/7; new=1; worker peak RSS MiB=[84.6]
    Run b44ee680-227d-4b52-aefa-b0ced7258754: complete; committed 7/7 new articles
      http://127.0.0.1:35935/file-0.warc.gz: 3 new; quota_reached
      http://127.0.0.1:35935/file-1.warc.gz: 2 new; pending
      http://127.0.0.1:35935/file-2.warc.gz: 2 new; pending
    Counters: {"accepted_candidates": 7, "compressed_bytes_read": 17449, "elapsed_seconds": 0.21300000000000002, "language_rejected": 0, "non_html": 0, "oversized_article": 0, "oversized_html": 0, "records": 7, "result_bytes": 21098, "too_short_or_corrupt": 0, "wall_end": 7163025678.587122, "wall_start": 7163025678.371601}
    Resume command: RESUME_RUN_ID=b44ee680-227d-4b52-aefa-b0ced7258754 ./run_to_db.sh
    SPARK_SMOKE_RESULT {"articles": 7, "per_file": [3, 2, 2], "parallel_workers": 3, "seconds": 1.87, "worker_peak_rss_mib": [84.2, 84.3, 84.1]}
    ✓ • 0ms

## Activity

    $ df -h . /tmp
        du -sh /tmp/warc-v2-pip-cache /tmp/warc-v2-test-pg .venv ../spark_warc_project/.venv
        cat /tmp/warc-v2-memory.json
    Filesystem      Size  Used Avail Use% Mounted on
    /dev/sda8       9.2G  6.5G  2.2G  75% /home/spark-master/rag_news_project/spark_warc_v2
    /dev/sda7       552M  182M  330M  36% /tmp
    93M    /tmp/warc-v2-pip-cache
    56M    /tmp/warc-v2-test-pg
    13M    .venv
    640M    ../spark_warc_project/.venv
    ✓ • 1.70s

## Activity

    $ python3 - <<'PY'
        p='tests/test_ingestion.py';s=open(p).read();pos=s.index('\n\n@unittest.skipUnless')
        s=s[:pos]+'''
            def test_changed_source_or_bad_range_is_rejected(self):
                data, offsets = make_warc(4)
                work = task(start_offset=offsets[1], etag='old-version')
                self.assertTrue(worker(data, work)['error'])
                response = Response(data, offsets[1])
                response.headers['Content-Range'] = 'bytes 1-10/100'
                with patch.object(job.urllib.request, 'urlopen', return_value=response):
                    self.assertTrue(job.process_file_chunk(task(start_offset=offsets[1]))['error'])
        
            def test_long_non_html_sequence_checks_budget(self):
                data, offsets = make_warc(50, content_type='application/json')
                result = worker(data, task(max_input_bytes=100))
                self.assertFalse(result['eof'])
                self.assertEqual(result['candidates'], [])
                self.assertGreater(result['next_offset'], 0)
                self.assertLess(result['next_offset'], len(data))
        
            def test_truncated_http_transport(self):
                data, _ = make_warc(1)
                response = Response(data)
                response.headers['Content-Length'] = str(len(data)+20)
                with patch.object(job.urllib.request, 'urlopen', return_value=response):
                    result = job.process_file_chunk(task())
                self.assertTrue(result['error'])
                self.assertFalse(result['eof'])
        
            def test_actual_language_detector(self):
                from extractors.extractors import detect_languages_batch
                texts = [
                    'The government announced new measures to improve public transportation. Local officials said the changes would reduce traffic and make daily journeys easier for residents.',
                    'Les élèves français étudient les événements récents et découvrent une société développée. Le gouvernement a annoncé de nouvelles mesures pour améliorer les transports publics.',
                    'أعلنت الحكومة اليوم عن إجراءات جديدة لتحسين خدمات النقل العام في المدينة. وقال المسؤولون إن هذه الخطوات ستساهم في تخفيف الازدحام وتسهيل حركة المواطنين خلال ساعات العمل.',
                    'El gobierno anunció nuevas medidas para mejorar el transporte público de la ciudad. Los funcionarios explicaron que los cambios reducirán el tráfico durante las horas de trabajo.',
                    'دولت امروز اقدامات جدیدی را برای بهبود حمل و نقل عمومی اعلام کرد. مسئولان گفتند که این تغییرات به کاهش ترافیک و بهبود زندگی شهروندان کمک خواهد کرد.',
                    'حکومت نے آج شہر میں عوامی نقل و حمل کو بہتر بنانے کے لیے نئے اقدامات کا اعلان کیا۔ حکام کا کہنا ہے کہ ان تبدیلیوں سے ٹریفک کم ہو گی اور شہریوں کو سہولت ملے گی۔',
                ]
                self.assertEqual(detect_languages_batch(texts), ['en','fr','ar','other','fa','ur'])
        ''' +s[pos:]
        pos=s.index('    def test_driver_shortfall_failure_and_resume')
        s=s[:pos]+'''    def test_new_run_reuses_verified_partial_checkpoint(self):
                db.commit_chunk(self.run_id, chunk())
                later = db.create_run('2026/05', ['file-1'], 10, 0, {})
                self.assertEqual(db.load_run_files(later)[0]['next_offset'], 100)
                self.assertEqual(db.load_run(later)['inserted_count'], 0)
        
            def test_overquota_chunk_is_not_silently_discarded(self):
                with self.assertRaises(ValueError):
                    db.commit_chunk(self.run_id, chunk([candidate('a'),candidate('b'),candidate('c')], eof=True))
                self.assertEqual(db.load_run_files(self.run_id)[0]['next_offset'], 0)
        
        ''' +s[pos:];open(p,'w').write(s)
        p='README.md';s=open(p).read().replace('  --conf spark.eventLog.enabled=false tests/spark_smoke.py','  --conf spark.eventLog.enabled=false \\\n  --conf "spark.pyspark.python=$PYSPARK_PYTHON" \\\n  --conf "spark.pyspark.driver.python=$PYSPARK_DRIVER_PYTHON" tests/spark_smoke.py');open(p,'w').write(s)
        PY
        cat > tests/memory_probe.py <<'PY'
        """Repeat near-budget worker chunks and report RSS after warmup."""
        import gc
        import json
        import resource
        import sys
        from pathlib import Path
        from unittest.mock import patch
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from tests.test_ingestion import make_warc, task, Response
        import stream_to_db as job
        
        body = ('<html><body><p>' + 'The government published a report on public transport and the local economy. ' * 4000 + '</p></body></html>').encode()
        data, _ = make_warc(20, payload=body)
        peaks, sizes = [], []
        for i in range(20):
            with patch.object(job.urllib.request, 'urlopen', return_value=Response(data)):
                result = job.process_file_chunk(task(candidate_limit=100, use_trafilatura=False))
            assert result['error'] is None, result['error']
            assert result['stats']['result_bytes'] <= 4194304
            sizes.append(result['stats']['result_bytes'])
            del result
            gc.collect()
            peaks.append(round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 2))
        assert max(peaks[5:])-peaks[5] < 64, peaks
        print(json.dumps(dict(chunks=20, payload_bytes=sizes, peak_rss_mib=peaks)))
        PY
        RAYON_NUM_THREADS=1 ../spark_warc_project/.venv/bin/python tests/memory_probe.py > /tmp/warc-v2-memory.json
    ✓ • 22.93s

## Assistant

The real Spark smoke test passed: three Python workers overlapped and committed exactly seven articles, split 3/2/2 across files. Their peak RSS was about 84 MiB each.

The clean install hit `/tmp`’s space limit while downloading Lingua. I’m moving build files into the project filesystem and reusing the already-installed matching Lingua package to avoid another large download.

## Activity

    $ mkdir -p .build-tmp .local-wheels
        ../spark_warc_project/.venv/bin/python - <<'PY'
        import csv,importlib.metadata,pathlib,zipfile
        name='lingua-language-detector'; dist=importlib.metadata.distribution(name)
        root=pathlib.Path(dist.locate_file('')); wheel=dist.read_text('WHEEL'); tag=next(line[5:] for line in wheel.splitlines() if line.startswith('Tag: '))
        target=pathlib.Path('.local-wheels')/f'lingua_language_detector-{dist.version}-{tag}.whl'
        with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as out:
         for line in csv.reader(dist.read_text('RECORD').splitlines()):
          path=line[0]
          if path.startswith('../') or '__pycache__' in path: continue
          out.write(root/path,path)
        print(target, target.stat().st_size)
        PY
    .local-wheels/lingua_language_detector-2.2.0-cp313-cp313-manylinux_2_17_x86_64.whl 180374783
    ✓ • 5.87s

## Activity

    $ sed -n '28,62p' db/db_handler.py
        sed -n '335,435p' db/db_handler.py
        cat db_inspect.py
    
    DB_CONFIG = _db_config()
    
    
    def get_connection():
        return psycopg2.connect(**_db_config())
    
    
    def connection_scope(function):
        """Reuse the coordinator connection, or own a short standalone session."""
        @wraps(function)
        def call(*args, conn=None, **kwargs):
            own = conn is None
            conn = conn or get_connection()
            try:
                return function(*args, conn=conn, **kwargs)
            finally:
                # Release read transactions as well as failed writes.
                if not conn.closed:
                    conn.rollback()
                if own:
                    conn.close()
        return call
    
    
    @contextmanager
    def _cursor(conn):
        cur = conn.cursor()
        try:
            yield cur
        finally:
            cur.close()
    
    
    @connection_scope
                if cursor != result["start_offset"]:
                    raise ValueError("stale chunk cursor; refusing to advance checkpoint")
                if result.get("error") and (result["candidates"] or result["eof"] or result["next_offset"] != cursor):
                    raise ValueError("failed chunks cannot carry articles or advance checkpoints")
                if not result.get("error") and not result["eof"] and result["next_offset"] <= cursor:
                    raise ValueError("chunk made no cursor progress")
                total_left = len(result["candidates"]) if target == 0 else max(0, target - total_done)
                file_left = len(result["candidates"]) if per_file == 0 else max(0, per_file - file_done)
                candidates = list({r["record_id"]: r for r in result["candidates"]}.values())
                if len(candidates) > min(total_left, file_left):
                    raise ValueError("chunk exceeded its remaining quota; refusing to discard uncommitted candidates")
                inserted_count = 0
                rejected = []
                for offset in range(0, len(candidates), batch_size):
                    batch = candidates[offset:offset + batch_size]
                    inserted_count += _insert_isolated(cur, batch, rejected)
                if rejected:
                    result.setdefault("stats", {})["invalid_database_rows"] = len(rejected)
                    _write_diagnostic(run_id, result["chunk_id"], rejected)
                failure, eof = result.get("error"), bool(result.get("eof"))
                status = "failed" if failure else ("eof" if eof else "pending")
                if per_file and file_done + inserted_count >= per_file:
                    status = "quota_reached"
                cur.execute("""UPDATE ingest_run_files SET next_offset=%s,inserted_count=inserted_count+%s,
                    eof=%s,status=%s,etag=COALESCE(%s,etag),last_modified=COALESCE(%s,last_modified),
                    last_error=%s,updated_at=CURRENT_TIMESTAMP WHERE run_id=%s AND file_url=%s""",
                    (result["next_offset"], inserted_count, eof, status, result.get("etag"),
                     result.get("last_modified"), failure, run_id, result["file_url"]))
                cur.execute("UPDATE ingest_runs SET inserted_count=inserted_count+%s,updated_at=CURRENT_TIMESTAMP WHERE run_id=%s",
                            (inserted_count, run_id))
                cur.execute("""INSERT INTO ingest_chunks
                    (chunk_id,run_id,file_url,start_offset,next_offset,candidate_count,inserted_count,eof,stats)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)""",
                    (result["chunk_id"], run_id, result["file_url"], result["start_offset"], result["next_offset"],
                     len(result["candidates"]), inserted_count, eof, json.dumps(result.get("stats", {}))))
                if not failure:
                    cur.execute("""INSERT INTO ingest_files (file_url,manifest_id,bytes_done,articles_done,complete,checkpoint_version,etag,last_modified)
                    SELECT %s,manifest_id,%s,%s,%s,2,%s,%s FROM ingest_runs WHERE run_id=%s
                    ON CONFLICT (file_url) DO UPDATE SET
                    bytes_done=CASE WHEN ingest_files.checkpoint_version<2 THEN EXCLUDED.bytes_done
                        ELSE GREATEST(ingest_files.bytes_done,EXCLUDED.bytes_done) END,
                    checkpoint_version=2,etag=COALESCE(EXCLUDED.etag,ingest_files.etag),
                    last_modified=COALESCE(EXCLUDED.last_modified,ingest_files.last_modified),
                    articles_done=ingest_files.articles_done+EXCLUDED.articles_done,
                    complete=ingest_files.complete OR EXCLUDED.complete,updated_at=CURRENT_TIMESTAMP""",
                    (result["file_url"], result["next_offset"], inserted_count, eof, result.get("etag"), result.get("last_modified"), run_id))
            conn.commit()
            return inserted_count
        except Exception:
            conn.rollback()
            raise
        finally:
            pass
    
    
    @connection_scope
    def finish_run(run_id, status, conn=None):
        try:
            with _cursor(conn) as cur:
                cur.execute("UPDATE ingest_runs SET status=%s,updated_at=CURRENT_TIMESTAMP WHERE run_id=%s", (status, run_id))
            conn.commit()
        finally:
            pass
    
    
    def save_batch_records(records_list, conn=None):
        """Compatibility helper; returns the number of newly inserted records."""
        own = conn is None
        conn = conn or get_connection()
        try:
            with _cursor(conn) as cur:
                count = len(_insert_new_records(cur, records_list))
            conn.commit()
            return count
        except Exception:
            conn.rollback()
            raise
        finally:
            if own:
                conn.close()
    
    
    @connection_scope
    def load_ingest_progress(manifest_id, conn=None):
        try:
            with _cursor(conn) as cur:
                cur.execute("SELECT file_url,bytes_done,articles_done,complete FROM ingest_files WHERE manifest_id=%s", (manifest_id,))
                return {row[0]: row[1:] for row in cur.fetchall()}
        finally:
            pass
    
    
    @connection_scope
    def upsert_ingest_progress(manifest_id, file_url, bytes_done, articles_done, complete, conn=None):
        try:
            with _cursor(conn) as cur:
                cur.execute("""INSERT INTO ingest_files (file_url,manifest_id,bytes_done,articles_done,complete)
                    VALUES (%s,%s,%s,%s,%s) ON CONFLICT (file_url) DO UPDATE SET
                    bytes_done=GREATEST(ingest_files.bytes_done,EXCLUDED.bytes_done),
                    articles_done=GREATEST(ingest_files.articles_done,EXCLUDED.articles_done),
                    complete=ingest_files.complete OR EXCLUDED.complete,updated_at=CURRENT_TIMESTAMP""",
    import os
    import sys
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    if BASE_DIR not in sys.path:
        sys.path.insert(0, BASE_DIR)
    
    from db.db_handler import get_connection
    
    TABLES = ("websites", "authors", "pages", "metadata", "content", "ingest_files", "ingest_runs", "ingest_run_files")
    SAMPLE_SIZE = int(os.environ.get("DB_INSPECT_SAMPLES", "5"))
    PREVIEW_LENGTH = int(os.environ.get("DB_INSPECT_PREVIEW", "300"))
    
    
    def print_counts(cur):
        print("=" * 90)
        print("TABLE COUNTS")
        print("=" * 90)
        for table in TABLES:
            cur.execute(f"SELECT COUNT(*) FROM {table};")
            print(f" {table:<12}: {cur.fetchone()[0]:,}")
    
    
    def print_progress(cur):
        cur.execute(
            """
            SELECT manifest_id,
                   COUNT(*) FILTER (WHERE complete) AS done,
                   COUNT(*) AS total,
                   COALESCE(SUM(bytes_done), 0) AS bytes
            FROM ingest_files GROUP BY manifest_id;
            """
        )
        rows = cur.fetchall()
        if not rows:
            print("No checkpoints yet.")
            return
        print("-" * 90)
        print("CHECKPOINTS (ingest_files)")
        for manifest_id, done, total, nbytes in rows:
            print(f" {manifest_id}: {done}/{total} files complete, {nbytes:,} bytes")
        cur.execute(
            """SELECT run_id::text, manifest_id, status, inserted_count,
                      target_articles, per_file_target
               FROM ingest_runs ORDER BY created_at DESC LIMIT 10"""
        )
        print("-" * 90)
        print("RECENT INGESTION RUNS")
        for run_id, manifest, status, inserted, target, per_file in cur.fetchall():
            target_label = f"{target:,}" if target else "unlimited"
            per_file_label = f"{per_file:,}" if per_file else "unlimited"
            print(f" {run_id} {manifest} {status}: {inserted:,}/{target_label}, per-file={per_file_label}")
    
    
    def print_previews(cur):
        cur.execute(
            """
            SELECT p.id, w.domain, m.language, m.title, c.cleaned_text
            FROM pages AS p
            JOIN websites AS w ON w.id = p.website_id
            JOIN metadata AS m ON m.page_id = p.id
            JOIN content AS c ON c.page_id = p.id
            ORDER BY p.id DESC LIMIT %s;
            """,
            (SAMPLE_SIZE,),
        )
        records = cur.fetchall()
        print("-" * 90)
        print(f"SAMPLE ROWS (latest {len(records)})")
        for page_id, domain, language, title, cleaned_text in records:
            preview = " ".join((cleaned_text or "").split())[:PREVIEW_LENGTH]
            if preview and len(preview) == PREVIEW_LENGTH:
                preview += "..."
            print(f" [{page_id}] ({language or 'N/A'}) {domain or 'N/A'} — {(title or 'N/A')[:60]}")
            print(f"       {preview or 'N/A'}")
    
    
    def main():
        conn = get_connection()
        try:
            cur = conn.cursor()
            try:
                print_counts(cur)
                print_progress(cur)
                print_previews(cur)
            finally:
                cur.close()
        finally:
            conn.close()
        print("=" * 90)
    
    
    if __name__ == "__main__":
        main()
    ✓ • 0ms

## Activity

    $ TMPDIR="$PWD/.build-tmp" .venv/bin/python -m pip install --no-cache-dir --no-deps .local-wheels/lingua_language_detector-2.2.0-cp313-cp313-manylinux_2_17_x86_64.whl
    Processing ./.local-wheels/lingua_language_detector-2.2.0-cp313-cp313-manylinux_2_17_x86_64.whl
    Installing collected packages: lingua-language-detector
    Successfully installed lingua-language-detector-2.2.0
    ✓ • 2.22s

## Activity

    $ python3 - <<'PY'
        from pathlib import Path
        p=Path('db/db_handler.py');s=p.read_text()
        parts=s.split('\n\n@connection_scope\n')
        for i in range(1,len(parts)):
         part=parts[i];end=part.find('\n\ndef ');body=part if end<0 else part[:end];tail='' if end<0 else part[end:]
         if '    finally:\n        pass' in body:
          body=body.replace('    finally:\n        pass','')
          if '    except ' not in body:
           prefix, rest=body.split('    try:\n',1)
           rest='\n'.join(line[4:] if line.startswith('    ') else line for line in rest.split('\n'))
           body=prefix+rest
          parts[i]=body+tail
        p.write_text('\n\n@connection_scope\n'.join(parts))
        p=Path('db_inspect.py');s=p.read_text().replace('"ingest_runs", "ingest_run_files")','"ingest_runs", "ingest_run_files", "ingest_chunks")').replace('        return\n    print("-" * 90)','    print("-" * 90)',1)
        pos=s.index('\n\ndef print_previews');s=s[:pos]+'''
            cur.execute("""SELECT run_id::text,file_url,last_error FROM ingest_run_files
                           WHERE status='failed' ORDER BY updated_at DESC LIMIT 10""")
            for run_id, file_url, error in cur.fetchall():
                print(f" FAILED {run_id} {file_url}: {error}")
        '''+s[pos:];p.write_text(s)
        p=Path('.gitignore');s=p.read_text()+'.build-tmp/\n.local-wheels/\n';p.write_text(s)
        PY
        python3 -m py_compile db/db_handler.py db_inspect.py
        cat /tmp/warc-v2-memory.json
    Sorry: IndentationError: expected an indented block after 'if' statement on line 429 (db_handler.py, line 430){"chunks": 20, "payload_bytes": [4009372, 4009372, 4009372, 4009372, 4009372, 4009372, 4009372, 4009372, 4009372, 4009372, 4009372, 4009372, 4009372, 4009372, 4009372, 4009372, 4009372, 4009372, 4009372, 4009372], "peak_rss_mib": [89.98, 90.01, 90.01, 90.01, 90.3, 90.3, 90.3, 90.3, 90.3, 90.3, 90.3, 90.3, 90.32, 90.32, 90.32, 90.32, 90.32, 90.32, 90.32, 90.32]}
    ✓ • 0ms

## Activity

    $ tail -n 40 db/db_handler.py
        sed -n '210,252p' db/db_handler.py
    def save_batch_records(records_list, conn=None):
        """Compatibility helper; returns the number of newly inserted records."""
        own = conn is None
        conn = conn or get_connection()
        try:
            with _cursor(conn) as cur:
                count = len(_insert_new_records(cur, records_list))
            conn.commit()
            return count
        except Exception:
            conn.rollback()
            raise
        finally:
            if own:
                conn.close()
    
    
    @connection_scope
    def load_ingest_progress(manifest_id, conn=None):
        with _cursor(conn) as cur:
            cur.execute("SELECT file_url,bytes_done,articles_done,complete FROM ingest_files WHERE manifest_id=%s", (manifest_id,))
            return {row[0]: row[1:] for row in cur.fetchall()}
    
    
    
    @connection_scope
    def upsert_ingest_progress(manifest_id, file_url, bytes_done, articles_done, complete, conn=None):
        with _cursor(conn) as cur:
            cur.execute("""INSERT INTO ingest_files (file_url,manifest_id,bytes_done,articles_done,complete)
                VALUES (%s,%s,%s,%s,%s) ON CONFLICT (file_url) DO UPDATE SET
                bytes_done=GREATEST(ingest_files.bytes_done,EXCLUDED.bytes_done),
                articles_done=GREATEST(ingest_files.articles_done,EXCLUDED.articles_done),
                complete=ingest_files.complete OR EXCLUDED.complete,updated_at=CURRENT_TIMESTAMP""",
                (file_url, manifest_id, bytes_done, articles_done, complete))
        conn.commit()
    
    
    
    if __name__ == "__main__":
    init_db()
            cur.execute(
                "SELECT run_id::text,manifest_id,target_articles,per_file_target,inserted_count,status,config "
                "FROM ingest_runs WHERE run_id=%s", (run_id,))
            row = cur.fetchone()
            if row is None:
                raise ValueError(f"unknown RESUME_RUN_ID: {run_id}")
            keys = ("run_id", "manifest_id", "target_articles", "per_file_target", "inserted_count", "status", "config")
            return dict(zip(keys, row))
    
    
    
    @connection_scope
    def load_run_files(run_id, conn=None):
        with _cursor(conn) as cur:
            cur.execute(
                "SELECT file_url,ordinal,next_offset,inserted_count,eof,status,etag,last_modified,last_error "
                "FROM ingest_run_files WHERE run_id=%s ORDER BY ordinal", (run_id,))
            keys = ("file_url", "ordinal", "next_offset", "inserted_count", "eof", "status", "etag", "last_modified", "last_error")
            return [dict(zip(keys, row)) for row in cur.fetchall()]
    
    
    
    def _insert_new_records(cur, records):
        if not records:
            return []
        unique = {}
        for record in records:
            unique.setdefault(record["record_id"], record)
        records = list(unique.values())
        domains = sorted({extract_domain(r["url"]) for r in records})
        execute_values(cur, "INSERT INTO websites (domain) VALUES %s ON CONFLICT DO NOTHING", [(x,) for x in domains])
        cur.execute("SELECT domain,id FROM websites WHERE domain=ANY(%s)", (domains,))
        domain_ids = dict(cur.fetchall())
        authors = sorted({r.get("author", "").strip() for r in records
                          if r.get("author", "").strip() not in ("", "N/A")})
        author_ids = {}
        if authors:
            execute_values(cur, "INSERT INTO authors (name) VALUES %s ON CONFLICT DO NOTHING", [(x,) for x in authors])
            cur.execute("SELECT name,id FROM authors WHERE name=ANY(%s)", (authors,))
            author_ids = dict(cur.fetchall())
        rows = [(domain_ids[extract_domain(r["url"])], author_ids.get(r.get("author", "").strip()),
                 r["record_id"], r["url"], r.get("file_url"), r.get("warc_date")) for r in records]
        inserted = execute_values(
    ✓ • 0ms

## Activity

    $ python3 - <<'PY'
        p='db/db_handler.py';s=open(p).read().replace('if __name__ == "__main__":\ninit_db()','if __name__ == "__main__":\n    init_db()').replace('\n\n\n\n','\n\n\n');open(p,'w').write(s)
        PY
        python3 -m py_compile db/db_handler.py
        bash -n run_to_db.sh
    ✓ • 0ms

## Activity

    $ WARC_TEST_DSN='host=/tmp/warc-v2-test-pg port=55439 dbname=postgres user=hadoop' RAYON_NUM_THREADS=1 ../spark_warc_project/.venv/bin/python -m unittest discover -s tests -v > /tmp/warc-v2-tests.log 2>&1
    ✓ • 1.04s

## Activity

    $ python3 - <<'PY'
        p='run_to_db.sh';s=open(p).read().replace('export RAYON_NUM_THREADS=1', 'VENV_DIR="$(cd "$VENV_DIR" && pwd)"\nexport RAYON_NUM_THREADS=1').replace('TASK_TMP="$(mktemp -d)"','TASK_TMP="$(mktemp -d "$PROJECT_ROOT/.pack-XXXXXX")"');open(p,'w').write(s)
        for p,label in [('db/__init__.py','PostgreSQL ingestion helpers.'),('parsers/__init__.py','Streaming WARC parsing.'),('extractors/__init__.py','Article extraction and language classification.')]:
         open(p,'w').write('"""'+label+'"""\n')
        with open('.gitignore','a') as f:f.write('.pack-*/\n')
        PY
        cat > tests/test_rag_loader.py <<'PY'
        import importlib.util
        import unittest
        from unittest.mock import Mock, patch
        
        AVAILABLE = importlib.util.find_spec('langchain_core') is not None and importlib.util.find_spec('langchain_text_splitters') is not None
        
        
        @unittest.skipUnless(AVAILABLE, 'install requirements-rag.txt for optional RAG tests')
        class RagTests(unittest.TestCase):
            def test_incremental_fetch_and_early_close(self):
                import rag_loader as rag
                consumed = []
                def rows():
                    for i in range(100):
                        consumed.append(i)
                        yield (i, 'text', 'https://example.com', 'Title','example.com','A','en',None,None,str(i))
                class Cursor:
                    def __iter__(self): return rows()
                    execute = Mock()
                    close = Mock()
                cursor = Cursor()
                conn = Mock(); conn.cursor.return_value = cursor
                with patch.object(rag, 'get_connection', return_value=conn):
                    stream = rag.iter_documents()
                    self.assertEqual(consumed, [])
                    self.assertEqual(next(stream).page_content, 'text')
                    self.assertEqual(consumed, [0])
                    stream.close()
                cursor.close.assert_called_once()
                conn.close.assert_called_once()
        
            def test_eager_loader_requires_limit(self):
                import rag_loader as rag
                with patch.dict('os.environ', {}, clear=True), self.assertRaises(ValueError):
                    rag.load_documents_distributed()
        PY
        cat > tests/test_launcher.py <<'PY'
        import os
        from pathlib import Path
        import subprocess
        import sys
        import tempfile
        import unittest
        
        
        class LauncherTests(unittest.TestCase):
            def test_dry_run_never_packages_or_submits(self):
                root = Path(__file__).resolve().parents[1]
                with tempfile.TemporaryDirectory() as directory:
                    for command in ('spark-submit', 'zip', 'hdfs'):
                        executable = Path(directory) / command
                        executable.write_text('#!/bin/sh\nexit 99\n')
                        executable.chmod(0o755)
                    env = dict(os.environ, PATH=directory+':'+os.environ['PATH'], DRY_RUN='1',
                               VENV_DIR=str(Path(sys.executable).absolute().parent.parent),
                               MAX_ACCEPTED_ARTICLES='17')
                    result = subprocess.run(['bash',str(root/'run_to_db.sh')],env=env,text=True,capture_output=True)
                    self.assertEqual(result.returncode,0,result.stderr)
                    self.assertIn('"target_articles": 17',result.stdout)
        PY
        tail -n 7 /tmp/warc-v2-tests.log
    Resume command: RESUME_RUN_ID=196aab54-88fd-4917-ad04-4e671e476946 ./run_to_db.sh
    Wave 1: committed 0/3; new=0; worker peak RSS MiB=[None, None]
    Run 196aab54-88fd-4917-ad04-4e671e476946: shortfall; committed 0/3 new articles
      file-1: 0 new; eof
      file-2: 0 new; eof
    Counters: {}
    Resume command: RESUME_RUN_ID=196aab54-88fd-4917-ad04-4e671e476946 ./run_to_db.sh
    ✓ • 0ms

## Activity

    $ rg -n 'Ran |OK|FAILED|ERROR' /tmp/warc-v2-tests.log
        .venv/bin/python -m pip check
    30:Ran 27 tests in 0.934s
    32:OK
    35:FAILED file-1: timeout
    36:FAILED file-2: timeout
    WARNING: The directory '/home/hadoop/.cache/pip' or its parent directory is not owned or is not writable by the current user. The cache has been disabled. Check the permissions and owner of that directory. If executing pip with sudo, you should use sudo's -H flag.
    pyspark-connect 4.2.0 requires googleapis-common-protos, which is not installed.
    pyspark-connect 4.2.0 requires grpcio, which is not installed.
    pyspark-connect 4.2.0 requires grpcio-status, which is not installed.
    pyspark-connect 4.2.0 requires numpy, which is not installed.
    pyspark-connect 4.2.0 requires pandas, which is not installed.
    pyspark-connect 4.2.0 requires pyarrow, which is not installed.
    pyspark-connect 4.2.0 requires pyyaml, which is not installed.
    pyspark-connect 4.2.0 requires zstandard, which is not installed.
    pyspark-client 4.2.0 requires googleapis-common-protos, which is not installed.
    pyspark-client 4.2.0 requires grpcio, which is not installed.
    pyspark-client 4.2.0 requires grpcio-status, which is not installed.
    pyspark-client 4.2.0 requires numpy, which is not installed.
    pyspark-client 4.2.0 requires pandas, which is not installed.
    pyspark-client 4.2.0 requires pyarrow, which is not installed.
    pyspark-client 4.2.0 requires pyyaml, which is not installed.
    pyspark-client 4.2.0 requires zstandard, which is not installed.
    pyspark 4.2.0 requires py4j, which is not installed.
    ✗ (1) • 381ms

## Assistant

The expanded 27-test suite passes. The memory probe also processed 20 chunks of about 4 MiB each; peak Python RSS stayed near 90 MiB after warmup. The README is restored with the quota, resume, setup, and tuning instructions. I’m finishing packaging checks and documenting the remaining YARN validation gap.

## Activity

    $ TMPDIR="$PWD/.build-tmp" .venv/bin/python -m pip install --cache-dir /tmp/warc-v2-pip-cache -r requirements-dev.txt
    Collecting FastWARC==1.0.9 (from -r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 2))
      Using cached fastwarc-1.0.9-cp313-cp313-manylinux_2_28_x86_64.whl.metadata (4.1 kB)
    Collecting charset-normalizer<4,>=3.4 (from -r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 3))
      Using cached charset_normalizer-3.5.2-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (46 kB)
    Requirement already satisfied: lingua-language-detector==2.2.0 in ./.venv/lib/python3.13/site-packages (from -r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 4)) (2.2.0)
    Collecting psycopg2-binary<3,>=2.9 (from -r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 5))
      Using cached psycopg2_binary-2.9.13-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.whl.metadata (4.9 kB)
    Collecting selectolax<0.5,>=0.3 (from -r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 6))
      Using cached selectolax-0.4.13-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (8.2 kB)
    Collecting trafilatura<3,>=2 (from -r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 7))
      Using cached trafilatura-2.2.0-py3-none-any.whl.metadata (13 kB)
    Collecting venv-pack==0.2.0 (from -r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 8))
      Using cached venv_pack-0.2.0-py2.py3-none-any.whl.metadata (1.7 kB)
    Collecting warcio<2,>=1.7 (from -r requirements-dev.txt (line 2))
      Using cached warcio-1.8.1-py2.py3-none-any.whl.metadata (18 kB)
    Collecting brotli (from FastWARC==1.0.9->-r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 2))
      Using cached brotli-1.2.0-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.whl.metadata (6.1 kB)
    Collecting click (from FastWARC==1.0.9->-r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 2))
      Using cached click-8.5.0-py3-none-any.whl.metadata (2.6 kB)
    Collecting tqdm (from FastWARC==1.0.9->-r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 2))
      Using cached tqdm-4.70.1-py3-none-any.whl.metadata (57 kB)
    Collecting certifi (from trafilatura<3,>=2->-r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 7))
      Using cached certifi-2026.7.22-py3-none-any.whl.metadata (2.5 kB)
    Collecting courlan>=1.4.0 (from trafilatura<3,>=2->-r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 7))
      Using cached courlan-1.4.0-py3-none-any.whl.metadata (18 kB)
    Collecting htmldate>=1.10.0 (from trafilatura<3,>=2->-r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 7))
      Using cached htmldate-1.10.0-py3-none-any.whl.metadata (9.8 kB)
    Collecting justext>=3.0.2 (from trafilatura<3,>=2->-r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 7))
      Using cached justext-3.0.2-py2.py3-none-any.whl.metadata (7.3 kB)
    Collecting lxml>=6.1.1 (from trafilatura<3,>=2->-r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 7))
      Using cached lxml-6.1.3-cp313-cp313-manylinux_2_26_x86_64.manylinux_2_28_x86_64.whl.metadata (3.3 kB)
    Collecting urllib3<3,>=1.26 (from trafilatura<3,>=2->-r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 7))
      Using cached urllib3-2.8.0-py3-none-any.whl.metadata (7.4 kB)
    Collecting six (from warcio<2,>=1.7->-r requirements-dev.txt (line 2))
      Using cached six-1.17.0-py2.py3-none-any.whl.metadata (1.7 kB)
    Collecting babel>=2.16.0 (from courlan>=1.4.0->trafilatura<3,>=2->-r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 7))
      Using cached babel-2.18.0-py3-none-any.whl.metadata (2.2 kB)
    Collecting tld>=0.13 (from courlan>=1.4.0->trafilatura<3,>=2->-r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 7))
      Using cached tld-0.13.2-py2.py3-none-any.whl.metadata (11 kB)
    Collecting dateparser>=1.1.2 (from htmldate>=1.10.0->trafilatura<3,>=2->-r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 7))
      Using cached dateparser-1.4.3-py3-none-any.whl.metadata (25 kB)
    Collecting python-dateutil>=2.9.0.post0 (from htmldate>=1.10.0->trafilatura<3,>=2->-r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 7))
      Using cached python_dateutil-2.9.0.post0-py2.py3-none-any.whl.metadata (8.4 kB)
    Collecting pytz>=2024.2 (from dateparser>=1.1.2->htmldate>=1.10.0->trafilatura<3,>=2->-r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 7))
      Using cached pytz-2026.4-py2.py3-none-any.whl.metadata (22 kB)
    Collecting regex>=2024.9.11 (from dateparser>=1.1.2->htmldate>=1.10.0->trafilatura<3,>=2->-r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 7))
      Using cached regex-2026.9.29-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (40 kB)
    Collecting tzlocal>=0.2 (from dateparser>=1.1.2->htmldate>=1.10.0->trafilatura<3,>=2->-r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 7))
      Using cached tzlocal-5.4.4-py3-none-any.whl.metadata (7.7 kB)
    Collecting lxml_html_clean (from lxml[html_clean]>=4.4.2->justext>=3.0.2->trafilatura<3,>=2->-r /home/spark-master/rag_news_project/spark_warc_v2/requirements.txt (line 7))
      Using cached lxml_html_clean-0.4.5-py3-none-any.whl.metadata (2.4 kB)
    Using cached fastwarc-1.0.9-cp313-cp313-manylinux_2_28_x86_64.whl (4.0 MB)
    Downloading venv_pack-0.2.0-py2.py3-none-any.whl (16 kB)
    Downloading charset_normalizer-3.5.2-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (254 kB)
    Downloading psycopg2_binary-2.9.13-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (4.3 MB)
       ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.3/4.3 MB 96.8 kB/s eta 0:00:00
    Downloading selectolax-0.4.13-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (2.5 MB)
       ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.5/2.5 MB 91.0 kB/s eta 0:00:00
    Downloading trafilatura-2.2.0-py3-none-any.whl (151 kB)
    Downloading warcio-1.8.1-py2.py3-none-any.whl (41 kB)
    Downloading urllib3-2.8.0-py3-none-any.whl (135 kB)
    Downloading courlan-1.4.0-py3-none-any.whl (34 kB)
    Downloading babel-2.18.0-py3-none-any.whl (10.2 MB)
       ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 10.2/10.2 MB 132.4 kB/s eta 0:00:00
    Downloading htmldate-1.10.0-py3-none-any.whl (31 kB)
    Downloading dateparser-1.4.3-py3-none-any.whl (322 kB)
    Downloading justext-3.0.2-py2.py3-none-any.whl (837 kB)
       ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 837.9/837.9 kB 208.1 kB/s eta 0:00:00
    Downloading lxml-6.1.3-cp313-cp313-manylinux_2_26_x86_64.manylinux_2_28_x86_64.whl (5.2 MB)
       ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 5.2/5.2 MB 424.7 kB/s eta 0:00:00
    Downloading python_dateutil-2.9.0.post0-py2.py3-none-any.whl (229 kB)
    Downloading pytz-2026.4-py2.py3-none-any.whl (506 kB)
    Downloading regex-2026.9.29-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (807 kB)
       ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 807.9/807.9 kB 383.1 kB/s eta 0:00:00
    Downloading six-1.17.0-py2.py3-none-any.whl (11 kB)
    Downloading tld-0.13.2-py2.py3-none-any.whl (296 kB)
    Downloading tzlocal-5.4.4-py3-none-any.whl (18 kB)
    Downloading brotli-1.2.0-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (1.4 MB)
       ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.4/1.4 MB 733.0 kB/s eta 0:00:00
    Downloading certifi-2026.7.22-py3-none-any.whl (136 kB)
    Downloading click-8.5.0-py3-none-any.whl (125 kB)
    Downloading lxml_html_clean-0.4.5-py3-none-any.whl (14 kB)
    Downloading tqdm-4.70.1-py3-none-any.whl (80 kB)
    Installing collected packages: venv-pack, pytz, brotli, urllib3, tzlocal, tqdm, tld, six, selectolax, regex, psycopg2-binary, lxml, click, charset-normalizer, certifi, babel, warcio, python-dateutil, lxml_html_clean, FastWARC, courlan, dateparser, justext, htmldate, trafilatura
    
    Successfully installed FastWARC-1.0.9 babel-2.18.0 brotli-1.2.0 certifi-2026.7.22 charset-normalizer-3.5.2 click-8.5.0 courlan-1.4.0 dateparser-1.4.3 htmldate-1.10.0 justext-3.0.2 lxml-6.1.3 lxml_html_clean-0.4.5 psycopg2-binary-2.9.13 python-dateutil-2.9.0.post0 pytz-2026.4 regex-2026.9.29 selectolax-0.4.13 six-1.17.0 tld-0.13.2 tqdm-4.70.1 trafilatura-2.2.0 tzlocal-5.4.4 urllib3-2.8.0 venv-pack-0.2.0 warcio-1.8.1
    ✓ • 3m 28s

## Activity

    $ python3 - <<'PY'
        from pathlib import Path
        p=Path('db/db_handler.py');s=p.read_text().replace('            failure, eof = result.get("error"), bool(result.get("eof"))','''            result.setdefault("stats", {})["already_saved"] = len(candidates) - inserted_count - len(rejected)
                    result["stats"]["chunk_duplicates"] = len(result["candidates"]) - len(candidates)
                    failure, eof = result.get("error"), bool(result.get("eof"))''');p.write_text(s)
        p=Path('parsers/parsers.py');s=p.read_text().replace('    def read(self, size=65536):\n        data', '    def read(self, size=65536):\n        if size == 0:\n            return b""\n        data');p.write_text(s)
        p=Path('run_to_db.sh');s=p.read_text().replace('        "$VENV_DIR/bin/python" -m pip freeze --all','        "$VENV_DIR/bin/python" -c \'import importlib.metadata as m, sysconfig; print("\\n".join(sorted(d.metadata["Name"] + "==" + d.version for d in m.distributions(path=[sysconfig.get_path("purelib")]))))\'');p.write_text(s)
        p=Path('README.md');s=p.read_text().replace('`langchain.py` is a compatibility import shim. The eager','The former `langchain.py` module is now `rag_loader.py`; update old imports. The eager');p.write_text(s)
        Path('langchain.py').unlink()
        PY
        bash -n run_to_db.sh
        python3 -m py_compile stream_to_db.py db/db_handler.py parsers/parsers.py rag_loader.py
    ✓ • 0ms

## Activity

    $ git status --short
        rg -n 'pass$|TODO|langchain.py|MAX_EXTRACTED' --glob '*.py' --glob '*.sh' --glob '*.md' --glob '!codex-session*' --glob '!.venv/**'
    fatal: not a git repository (or any parent up to mount point /)
    Stopping at filesystem boundary (GIT_DISCOVERY_ACROSS_FILESYSTEM not set).
    stream_to_db.py:63:    if "MAX_EXTRACTED_PER_ROUND" in os.environ:
    stream_to_db.py:65:            "MAX_EXTRACTED_PER_ROUND was removed; use WORKER_MAX_CANDIDATES, "
    stream_to_db.py:521:                pass
    README.md:160:`MAX_EXTRACTED_PER_ROUND` is removed: supplying it gives a migration error pointing
    README.md:221:The former `langchain.py` module is now `rag_loader.py`; update old imports. The eager
    utils.py:61:            pass
    utils.py:66:        pass
    utils.py:75:            pass
    utils.py:80:            pass
    tests/test_ingestion.py:98:                               ('MAX_EXTRACTED_PER_ROUND', '50')]:
    tests/test_ingestion.py:355:            def setLogLevel(self, level): pass
    tests/test_ingestion.py:357:            def stop(self): pass
    tests/spark_smoke.py:54:        def log_message(self, *args): pass
    ✓ • 0ms

## Activity

    $ WARC_TEST_DSN='host=/tmp/warc-v2-test-pg port=55439 dbname=postgres user=hadoop' RAYON_NUM_THREADS=1 .venv/bin/python -m unittest discover -s tests -v > /tmp/warc-v2-tests-final.log 2>&1
    ✓ • 1.32s

## Activity

    $ cat > tests/package_smoke.py <<'PY'
        """Exercise real launcher packaging and relocated imports without starting YARN."""
        import json
        import os
        from pathlib import Path
        import subprocess
        import sys
        import tempfile
        
        root = Path(__file__).resolve().parents[1]
        build = root / '.build-tmp'
        build.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=build) as temporary:
            temporary = Path(temporary)
            submit = temporary / 'spark-submit'
            submit.write_text('''#!/usr/bin/env python3
        import json,os,pathlib,subprocess,sys,tarfile,tempfile
        args=sys.argv[1:]
        archive=args[args.index('--archives')+1].split('#')[0]
        code=args[args.index('--py-files')+1]
        with tempfile.TemporaryDirectory(dir=os.environ['PACKAGE_TEST_TMP']) as unpacked:
            with tarfile.open(archive) as tar: tar.extractall(unpacked,filter='fully_trusted')
            env=dict(os.environ,PYTHONPATH=code)
            python=str(pathlib.Path(unpacked)/'bin/python')
            subprocess.run([python,'-c','from extractors.extractors import detect_languages_batch; from parsers.parsers import ValidatedGzipStream; from db.db_handler import commit_chunk; import trafilatura; assert detect_languages_batch(["The government announced new measures to improve public transportation and reduce traffic in the city."]) == ["en"]; print("RELOCATED_WORKER_IMPORTS_OK")'],cwd=unpacked,env=env,check=True)
        print('PACKAGING_OK '+json.dumps({'archive':archive,'arguments':args[:8]}))
        ''')
            submit.chmod(0o755)
            env = dict(os.environ, PATH=str(temporary)+':'+os.environ['PATH'], USE_HDFS_CACHE='0',
                       PACKAGE_TEST_TMP=str(build), VENV_DIR=str(root/'.venv'))
            env.pop('DRY_RUN', None)
            subprocess.run(['bash',str(root/'run_to_db.sh')],cwd=root,env=env,check=True)
        PY
        .venv/bin/python tests/package_smoke.py > /tmp/warc-v2-package.log 2>&1
    ✓ • 14.76s

## Activity

    $ tail -n 12 /tmp/warc-v2-package.log
        rg -n 'Ran |OK|FAILED|ERROR|skipped' /tmp/warc-v2-tests-final.log
    Packing worker environment...
    Collecting packages...
    Packing environment at '/home/spark-master/rag_news_project/spark_warc_v2/.venv' to '/home/spark-master/rag_news_project/spark_warc_v2/.pack-UufxKZ/environment.tar.gz'
    
    RELOCATED_WORKER_IMPORTS_OK
    PACKAGING_OK {"archive": "/home/spark-master/rag_news_project/spark_warc_v2/pyspark_venv-24a01a04fd03a793c2fe88eff6b704d5f7a740b4e34a26e149b4e966f96b5a52.tar.gz", "arguments": ["--master", "yarn", "--deploy-mode", "client", "--driver-memory", "512m", "--executor-memory", "512m"]}
    23:test_oversize_decoded_http_body_is_skipped (test_ingestion.UnitTests.test_oversize_decoded_http_body_is_skipped) ... ok
    29:test_eager_loader_requires_limit (test_rag_loader.RagTests.test_eager_loader_requires_limit) ... skipped 'install requirements-rag.txt for optional RAG tests'
    30:test_incremental_fetch_and_early_close (test_rag_loader.RagTests.test_incremental_fetch_and_early_close) ... skipped 'install requirements-rag.txt for optional RAG tests'
    33:Ran 30 tests in 1.297s
    35:OK (skipped=2)
    38:FAILED file-1: timeout
    39:FAILED file-2: timeout
    ✓ • 0ms

## Activity

    $ ../spark_warc_project/.venv/bin/python -m unittest tests.test_rag_loader -v
        PYTHONPATH= .venv/bin/python -m pip check
        DRY_RUN=1 MAX_ACCEPTED_ARTICLES=1000 MAX_ACCEPTED_PER_FILE=100 ./run_to_db.sh
    test_eager_loader_requires_limit (tests.test_rag_loader.RagTests.test_eager_loader_requires_limit) ... ok
    test_incremental_fetch_and_early_close (tests.test_rag_loader.RagTests.test_incremental_fetch_and_early_close) ... ok
    
    ----------------------------------------------------------------------
    Ran 2 tests in 2.123s
    
    OK
    WARNING: The directory '/home/hadoop/.cache/pip' or its parent directory is not owned or is not writable by the current user. The cache has been disabled. Check the permissions and owner of that directory. If executing pip with sudo, you should use sudo's -H flag.
    No broken requirements found.
    {
      "db_batch_size": 25,
      "lingua_min_confidence": 0.5,
      "manifest_id": "2026/05",
      "max_article_bytes": 524288,
      "max_files_per_round": 3,
      "max_html_bytes": 2097152,
      "max_retries": 3,
      "min_word_count": 80,
      "month": "05",
      "num_files": 15,
      "per_file_target": 100,
      "start_file_offset": 0,
      "target_articles": 1000,
      "use_trafilatura": true,
      "worker_max_candidates": 100,
      "worker_max_input_bytes": 33554432,
      "worker_max_result_bytes": 4194304,
      "worker_max_seconds": 120,
      "year": "2026"
    }
    ✓ • 2.63s

## Activity

    $ python3 - <<'PY'
        p='tests/spark_smoke.py';s=open(p).read().replace('max_files_per_round=3, use_trafilatura=False','max_files_per_round=3, use_trafilatura=True');open(p,'w').write(s)
        PY
    ✓ • 0ms

## Assistant

Packaging checks pass: the launcher builds an archive that can be unpacked elsewhere, import the shipped modules, and run language detection. The new environment has no broken dependency requirements. All 30 test cases have passed across the ingestion and optional RAG environments; I’m doing the final Spark check with the new environment and default extraction settings.

## Activity

    $ WARC_TEST_DSN='host=/tmp/warc-v2-test-pg port=55439 dbname=postgres user=hadoop' RAYON_NUM_THREADS=1 SPARK_LOCAL_IP=127.0.0.1 spark-submit --master 'local[3]' --driver-memory 512m --conf spark.eventLog.enabled=false --conf spark.ui.enabled=false --conf spark.driver.host=127.0.0.1 --conf spark.pyspark.python=/home/spark-master/rag_news_project/spark_warc_v2/.venv/bin/python --conf spark.pyspark.driver.python=/home/spark-master/rag_news_project/spark_warc_v2/.venv/bin/python tests/spark_smoke.py > /tmp/warc-v2-spark-final.log 2>&1
    ✓ • 10.64s

## Activity

    $ tail -n 20 /tmp/warc-v2-spark-final.log
        .venv/bin/python - <<'PY'
        import ast
        from pathlib import Path
        for path in list(Path('.').glob('*.py')) + list(Path('db').glob('*.py')) + list(Path('parsers').glob('*.py')) + list(Path('extractors').glob('*.py')) + list(Path('tests').glob('*.py')):
         ast.parse(path.read_text(), filename=str(path))
        print('Python syntax OK')
        PY
        bash -n run_to_db.sh
    26/09/30 11:28:14 INFO Executor: Starting executor with user classpath (userClassPathFirst = false): ''
    26/09/30 11:28:14 INFO Executor: Created or updated repl class loader org.apache.spark.util.MutableURLClassLoader@534d9bae for default.
    26/09/30 11:28:14 INFO Utils: Successfully started service 'org.apache.spark.network.netty.NettyBlockTransferService' on port 40835.
    26/09/30 11:28:14 INFO NettyBlockTransferService: Server created on 127.0.0.1:40835
    26/09/30 11:28:14 INFO BlockManager: Using org.apache.spark.storage.RandomBlockReplicationPolicy for block replication policy
    26/09/30 11:28:15 INFO BlockManagerMaster: Registering BlockManager BlockManagerId(driver, 127.0.0.1, 40835, None)
    26/09/30 11:28:15 INFO BlockManagerMasterEndpoint: Registering block manager 127.0.0.1:40835 with 127.2 MiB RAM, BlockManagerId(driver, 127.0.0.1, 40835, None)
    26/09/30 11:28:15 INFO BlockManagerMaster: Registered BlockManager BlockManagerId(driver, 127.0.0.1, 40835, None)
    26/09/30 11:28:15 INFO BlockManager: Initialized BlockManager: BlockManagerId(driver, 127.0.0.1, 40835, None)
    Created ingestion run 57656747-ef69-4318-8fdf-da8854626557
    Resume command: RESUME_RUN_ID=57656747-ef69-4318-8fdf-da8854626557 ./run_to_db.sh
    Wave 1: committed 6/7; new=6; worker peak RSS MiB=[99.0, 99.0, 99.1]
    Wave 2: committed 7/7; new=1; worker peak RSS MiB=[99.2]
    Run 57656747-ef69-4318-8fdf-da8854626557: complete; committed 7/7 new articles
      http://127.0.0.1:36621/file-0.warc.gz: 3 new; quota_reached
      http://127.0.0.1:36621/file-1.warc.gz: 2 new; pending
      http://127.0.0.1:36621/file-2.warc.gz: 2 new; pending
    Counters: {"accepted_candidates": 7, "already_saved": 0, "chunk_duplicates": 0, "compressed_bytes_read": 17451, "elapsed_seconds": 2.765, "language_rejected": 0, "non_html": 0, "oversized_article": 0, "oversized_html": 0, "records": 7, "result_bytes": 21105, "too_short_or_corrupt": 0, "wall_end": 7163027600.830057, "wall_start": 7163027598.060957}
    Resume command: RESUME_RUN_ID=57656747-ef69-4318-8fdf-da8854626557 ./run_to_db.sh
    SPARK_SMOKE_RESULT {"articles": 7, "per_file": [3, 2, 2], "parallel_workers": 3, "seconds": 2.76, "worker_peak_rss_mib": [99.0, 99.0, 99.1]}
    Python syntax OK
    ✓ • 0ms

## Activity

    $ cat > VALIDATION.md <<'MD'
        # Validation — 2026-09-30
        
        Implementation and local validation are complete. Distributed YARN rollout remains
        unverified because the configured ResourceManager (`spark-master:8032`) timed out,
        including a check outside the network sandbox. No production ingestion was started.
        
        ## Checks performed
        
        | Check | Result |
        |---|---|
        | Core suite in the new `.venv` | 28 passed; 2 optional RAG tests skipped |
        | Optional RAG tests in the existing sibling environment with RAG dependencies | 2 passed |
        | PostgreSQL integration coverage | 12 tests, PostgreSQL 18, isolated schemas in a disposable local server |
        | Local Spark integration | Spark 4.2.0, `local[3]`, three real Python worker processes |
        | Quota smoke | Exactly 7 inserts; per-file counts 3 / 2 / 2 against a cap of 3 |
        | Parallelism | All three initial task execution intervals overlap |
        | Worker memory, default extraction | Initial-wave Python peak RSS 99.0 / 99.0 / 99.1 MiB |
        | Repeated bounded results | 20 chunks, 4,009,372 candidate JSON bytes per chunk |
        | Repeated-result memory | Peak RSS 89.98 → 90.32 MiB; about 0.02 MiB growth after warmup |
        | Packaging | Real launcher built venv/code archives; relocated Python imported modules and classified English |
        | Config dry run | Passed without packaging, Spark, or database access |
        | Dependency consistency | `PYTHONPATH= .venv/bin/python -m pip check`: no broken requirements |
        | Python and shell syntax | Passed |
        
        The Spark test uses generated WARC files served over real localhost HTTP and real
        PostgreSQL transactions. It enables the default trafilatura-first extraction. The
        measured ingestion portion took 2.76 seconds, excluding Spark startup; this is a
        fixture result, not an estimate of Common Crawl throughput.
        
        The repeated-result probe uses selectolax fallback and real Lingua classification
        on large generated articles. It ran with the existing sibling environment. Its
        RSS measurements cover Python, not the JVM or a complete YARN container. This does
        not establish a maximum RSS for arbitrary web pages.
        
        The new `.venv` installs the declared ingestion/test dependencies. Lingua 2.2.0 was
        installed from a wheel reconstructed from the existing matching installation after
        an initial download exhausted the small `/tmp` filesystem; other dependencies came
        from the package index. Packaging uses temporary directories on the project
        filesystem and publishes local archives on that same filesystem.
        
        ## Behaviors covered
        
        - Targets below batch size, non-divisible allowances, per-file caps, duplicate-only
          chunks, duplicate IDs in a batch, and exact inserted-row counting.
        - Transaction rollback, uncertain commit acknowledgement recovery, invalid-row
          isolation, advisory-lock exclusion, stale/stalled cursor rejection, failed-file
          resume, verified partial-cursor reuse, and preservation of legacy completed files.
        - Real gzip member offsets, ignored HTTP Range, unknown response length, changed
          source validators, malformed ranges, truncated HTTP/gzip, CRC corruption, decoded
          oversized HTTP bodies, result-budget replay, and non-HTML input-budget progress.
        - French accents, declared encodings, JSON-LD metadata, nonoverlapping language
          samples, and real English/French/Arabic versus Spanish/Persian/Urdu classification.
        - Streaming RAG consumption and early-close cleanup; eager-loader limit enforcement.
        
        ## Remaining cluster validation
        
        When ResourceManager and workers are available, use a configured PostgreSQL database
        and run:
        
        ```bash
        NUM_FILES=1 MAX_ACCEPTED_ARTICLES=10 MAX_ACCEPTED_PER_FILE=10 ./run_to_db.sh
        NUM_FILES=3 MAX_ACCEPTED_ARTICLES=9 MAX_ACCEPTED_PER_FILE=3 ./run_to_db.sh
        ```
        
        Measure full executor-container memory and sustained real-CC-NEWS throughput before
        raising defaults. Atomic HDFS artifact publication has been implemented but could
        not be exercised against the unavailable cluster. There is no production before/after
        throughput comparison in this validation.
        
        Reproducible local checks are in `tests/test_ingestion.py`, `tests/test_launcher.py`,
        `tests/test_rag_loader.py`, `tests/spark_smoke.py`, `tests/memory_probe.py`, and
        `tests/package_smoke.py`. The disposable PostgreSQL server used during this session
        was stopped after testing.
        MD
        python3 - <<'PY'
        from pathlib import Path
        wheel=Path('.local-wheels/lingua_language_detector-2.2.0-cp313-cp313-manylinux_2_17_x86_64.whl')
        wheel.unlink(missing_ok=True)
        if Path('.local-wheels').exists() and not any(Path('.local-wheels').iterdir()): Path('.local-wheels').rmdir()
        PY
    ✓ • 0ms

## Activity

    $ /usr/lib/postgresql/18/bin/pg_ctl -D /tmp/warc-v2-test-pg -m fast stop
    waiting for server to shut down.... done
    server stopped
    ✓ • 0ms

## Assistant

Implemented the remaining changes and restored the [README](/home/spark-master/rag_news_project/spark_warc_v2/README.md).

- Exact committed-article quotas, worker-side language detection, bounded memory, and reliable resume.
- 28 core tests and 2 RAG tests passed.
- Real local Spark test saved exactly **7 articles**, split **3/2/2**, with three workers running concurrently.

Usage:

```bash
NUM_FILES=all MAX_ACCEPTED_ARTICLES=1000 MAX_ACCEPTED_PER_FILE=100 ./run_to_db.sh
```

**YARN validation remains pending:** ResourceManager timed out. Full results and remaining checks are in [VALIDATION.md](/home/spark-master/rag_news_project/spark_warc_v2/VALIDATION.md).

## User

i started dfs nd yarn

## Assistant

I’ll check HDFS and YARN, then run the pending one-worker and three-worker smoke tests against an isolated test database.

## Activity

    $ timeout 20 yarn node -list
         timeout 20 hdfs dfsadmin -safemode get
    2026-09-30 11:32:48,738 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at spark-master/192.168.56.10:8032
    Total Nodes:3
             Node-Id         Node-State    Node-Http-Address    Number-of-Running-Containers
       worker2:43653            RUNNING         worker2:8042                               0
       worker1:42213            RUNNING         worker1:8042                               0
       worker3:41605            RUNNING         worker3:8042                               0
    Safe mode is OFF
    ✓ • 2.71s

## Activity

    $ cat run_to_db.sh
        sed -n '1,160p' tests/spark_smoke.py
        cat VALIDATION.md
    #!/usr/bin/env bash
    set -euo pipefail
    PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
    cd "$PROJECT_ROOT"
    VENV_DIR="${VENV_DIR:-$PROJECT_ROOT/.venv}"
    if [ ! -x "$VENV_DIR/bin/python" ]; then
        echo "Missing virtual environment: $VENV_DIR. See README.md setup instructions." >&2
        exit 1
    fi
    VENV_DIR="$(cd "$VENV_DIR" && pwd)"
    export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
    # Validate before packaging, network access, database access, or Spark startup.
    "$VENV_DIR/bin/python" -c 'from stream_to_db import load_config; load_config()'
    if [ "${DRY_RUN:-0}" = 1 ]; then
        exec "$VENV_DIR/bin/python" stream_to_db.py
    fi
    TASK_TMP="$(mktemp -d "$PROJECT_ROOT/.pack-XXXXXX")"
    trap 'rm -rf "$TASK_TMP"' EXIT
    ZIP="$TASK_TMP/project_code.zip"
    zip -qr "$ZIP" extractors parsers db utils.py -x '*/__pycache__/*' '*.pyc'
    
    # Hash installed distributions as well as declared dependencies and Python.
    VENV_FINGERPRINT="$(
        {
            cat requirements.txt "$VENV_DIR/pyvenv.cfg"
            "$VENV_DIR/bin/python" -c 'import importlib.metadata as m, sysconfig; print("\n".join(sorted(d.metadata["Name"] + "==" + d.version for d in m.distributions(path=[sysconfig.get_path("purelib")]))))'
            "$VENV_DIR/bin/python" -c 'import sys; print(sys.version); print(sys.executable)'
        } | sha256sum | cut -d ' ' -f 1
    )"
    VENV_ARCHIVE="$PROJECT_ROOT/pyspark_venv-${VENV_FINGERPRINT}.tar.gz"
    if [ ! -f "$VENV_ARCHIVE" ]; then
        echo "Packing worker environment..."
        "$VENV_DIR/bin/python" -m venv_pack -p "$VENV_DIR" -o "$TASK_TMP/environment.tar.gz"
        mv "$TASK_TMP/environment.tar.gz" "$VENV_ARCHIVE"
    fi
    ARCHIVES_SPEC="$VENV_ARCHIVE#environment"
    HDFS_APPS_DIR="${HDFS_APPS_DIR:-/user/$USER/apps/spark}"
    EXTRA_CONF=()
    
    publish_hdfs() {
        local source="$1" destination="$2" temporary="$2.upload-$(basename "$TASK_TMP")"
        if hdfs dfs -test -e "$destination" 2>/dev/null; then return 0; fi
        hdfs dfs -mkdir -p "$HDFS_APPS_DIR" || return 1
        hdfs dfs -put "$source" "$temporary" || return 1
        if hdfs dfs -mv "$temporary" "$destination"; then return 0; fi
        hdfs dfs -rm -f "$temporary" >/dev/null 2>&1 || true
        hdfs dfs -test -e "$destination"
    }
    
    if [ "${USE_HDFS_CACHE:-1}" = 1 ] && hdfs dfs -test -e / >/dev/null 2>&1; then
        VENV_HASH="$(sha256sum "$VENV_ARCHIVE" | cut -d ' ' -f 1)"
        HDFS_VENV="$HDFS_APPS_DIR/pyspark_venv-$VENV_HASH.tar.gz"
        if publish_hdfs "$VENV_ARCHIVE" "$HDFS_VENV"; then
            ARCHIVES_SPEC="hdfs://$HDFS_VENV#environment"
        fi
        : "${SPARK_HOME:?Set SPARK_HOME to the cluster Spark installation}"
        JARS_HASH="$(find "$SPARK_HOME/jars" -maxdepth 1 -name '*.jar' -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum | cut -d ' ' -f 1)"
        JARS_ARCHIVE="$PROJECT_ROOT/spark-libs-$JARS_HASH.zip"
        if [ ! -f "$JARS_ARCHIVE" ]; then
            (cd "$SPARK_HOME/jars" && zip -qr "$TASK_TMP/spark-libs.zip" .)
            mv "$TASK_TMP/spark-libs.zip" "$JARS_ARCHIVE"
        fi
        HDFS_JARS="$HDFS_APPS_DIR/spark-libs-$JARS_HASH.zip"
        if publish_hdfs "$JARS_ARCHIVE" "$HDFS_JARS"; then
            EXTRA_CONF+=(--conf "spark.yarn.archive=hdfs://$HDFS_JARS")
        fi
    fi
    export PYSPARK_DRIVER_PYTHON="$VENV_DIR/bin/python"
    export PYSPARK_PYTHON="./environment/bin/python"
    spark-submit \
        --master yarn --deploy-mode client \
        --driver-memory "${SPARK_DRIVER_MEMORY:-512m}" \
        --executor-memory "${SPARK_EXECUTOR_MEMORY:-512m}" \
        --conf "spark.executor.memoryOverhead=${SPARK_EXECUTOR_MEMORY_OVERHEAD:-512m}" \
        --conf spark.executor.cores=1 \
        --conf spark.executor.instances=3 \
        --conf spark.dynamicAllocation.enabled=false \
        --conf spark.driver.maxResultSize=64m \
        --conf spark.executorEnv.RAYON_NUM_THREADS=1 \
        --conf spark.executorEnv.OMP_NUM_THREADS=1 \
        --conf spark.executorEnv.OPENBLAS_NUM_THREADS=1 \
        --conf "spark.pyspark.driver.python=$VENV_DIR/bin/python" \
        --conf "spark.pyspark.python=$PYSPARK_PYTHON" \
        "${EXTRA_CONF[@]}" --archives "$ARCHIVES_SPEC" --py-files "$ZIP" stream_to_db.py
    """Local Spark integration smoke: real HTTP, extraction, Lingua, and PostgreSQL.
    
    Run with spark-submit --master 'local[3]' --driver-memory 512m
    --conf spark.eventLog.enabled=false tests/spark_smoke.py.
    Requires WARC_TEST_DSN, and uses an isolated disposable schema.
    """
    import io
    import json
    import os
    from pathlib import Path
    import sys
    import tempfile
    import threading
    import time
    import uuid
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    from unittest.mock import patch
    
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from pyspark.sql import SparkSession
    import psycopg2
    from tests.test_ingestion import make_warc
    import stream_to_db as job
    from db import db_handler as db
    
    
    def timed_chunk(task):
        import time
        import stream_to_db
        start = time.time()
        result = stream_to_db.process_file_chunk(task)
        result['stats']['wall_start'] = start
        result['stats']['wall_end'] = time.time()
        return result
    
    
    def main():
        dsn = os.environ['WARC_TEST_DSN']
        data = {f'/file-{i}.warc.gz': make_warc(12)[0] for i in range(3)}
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                body = data.get(self.path)
                if body is None:
                    self.send_error(404); return
                value = self.headers.get('Range')
                offset = int(value.split('=')[1].split('-')[0]) if value else 0
                self.send_response(206 if offset else 200)
                self.send_header('Content-Length', str(len(body)-offset))
                self.send_header('ETag', 'test-v1')
                if offset:
                    self.send_header('Content-Range', f'bytes {offset}-{len(body)-1}/{len(body)}')
                self.end_headers()
                self.wfile.write(body[offset:])
            def log_message(self, *args): pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        schema = 'spark_smoke_' + uuid.uuid4().hex
        admin = psycopg2.connect(dsn); admin.autocommit = True
        with admin.cursor() as cur: cur.execute('CREATE SCHEMA ' + schema)
        def connect(): return psycopg2.connect(dsn, options='-c search_path='+schema)
        spark = SparkSession.builder.appName('WARC-v2-fixture-smoke').getOrCreate()
        spark.sparkContext.setLogLevel('ERROR')
        # Imported task functions must be available to the real Python workers.
        spark.sparkContext.addPyFile(str(Path(job.__file__)))
        try:
            with patch.object(db, 'get_connection', side_effect=connect), patch.object(job, 'get_spark_session', return_value=spark), \
                 patch.object(spark, 'stop'), patch.object(job, 'process_file_chunk', timed_chunk):
                urls = [f'http://127.0.0.1:{server.server_port}{path}' for path in data]
                settings = job.load_config()
                settings.update(target_articles=7, per_file_target=3, worker_max_candidates=2,
                                max_files_per_round=3, use_trafilatura=True)
                with patch.object(job, 'load_config', return_value=settings), patch.object(job, 'fetch_manifest', return_value=urls):
                    started = time.monotonic()
                    assert job.run_streaming_pipeline() == 0
                with connect() as conn, conn.cursor() as cur:
                    cur.execute('SELECT inserted_count FROM ingest_runs')
                    assert cur.fetchone()[0] == 7
                    cur.execute('SELECT inserted_count FROM ingest_run_files ORDER BY ordinal')
                    counts = [row[0] for row in cur.fetchall()]
                    assert sum(counts) == 7 and max(counts) <= 3, counts
                    cur.execute('SELECT stats FROM ingest_chunks ORDER BY committed_at')
                    stats = [row[0] for row in cur.fetchall()]
                first_wave = stats[:3]
                assert max(s['wall_start'] for s in first_wave) < min(s['wall_end'] for s in first_wave), first_wave
                print('SPARK_SMOKE_RESULT ' + json.dumps(dict(
                    articles=7, per_file=counts, parallel_workers=len({s['worker_pid'] for s in first_wave}),
                    seconds=round(time.monotonic()-started, 2),
                    worker_peak_rss_mib=[s['python_peak_rss_mib'] for s in first_wave])))
        finally:
            spark.stop()
            server.shutdown(); server.server_close()
            with admin.cursor() as cur: cur.execute('DROP SCHEMA ' + schema + ' CASCADE')
            admin.close()
    
    
    if __name__ == '__main__': main()
    # Validation — 2026-09-30
    
    Implementation and local validation are complete. Distributed YARN rollout remains
    unverified because the configured ResourceManager (`spark-master:8032`) timed out,
    including a check outside the network sandbox. No production ingestion was started.
    
    ## Checks performed
    
    | Check | Result |
    |---|---|
    | Core suite in the new `.venv` | 28 passed; 2 optional RAG tests skipped |
    | Optional RAG tests in the existing sibling environment with RAG dependencies | 2 passed |
    | PostgreSQL integration coverage | 12 tests, PostgreSQL 18, isolated schemas in a disposable local server |
    | Local Spark integration | Spark 4.2.0, `local[3]`, three real Python worker processes |
    | Quota smoke | Exactly 7 inserts; per-file counts 3 / 2 / 2 against a cap of 3 |
    | Parallelism | All three initial task execution intervals overlap |
    | Worker memory, default extraction | Initial-wave Python peak RSS 99.0 / 99.0 / 99.1 MiB |
    | Repeated bounded results | 20 chunks, 4,009,372 candidate JSON bytes per chunk |
    | Repeated-result memory | Peak RSS 89.98 → 90.32 MiB; about 0.02 MiB growth after warmup |
    | Packaging | Real launcher built venv/code archives; relocated Python imported modules and classified English |
    | Config dry run | Passed without packaging, Spark, or database access |
    | Dependency consistency | `PYTHONPATH= .venv/bin/python -m pip check`: no broken requirements |
    | Python and shell syntax | Passed |
    
    The Spark test uses generated WARC files served over real localhost HTTP and real
    PostgreSQL transactions. It enables the default trafilatura-first extraction. The
    measured ingestion portion took 2.76 seconds, excluding Spark startup; this is a
    fixture result, not an estimate of Common Crawl throughput.
    
    The repeated-result probe uses selectolax fallback and real Lingua classification
    on large generated articles. It ran with the existing sibling environment. Its
    RSS measurements cover Python, not the JVM or a complete YARN container. This does
    not establish a maximum RSS for arbitrary web pages.
    
    The new `.venv` installs the declared ingestion/test dependencies. Lingua 2.2.0 was
    installed from a wheel reconstructed from the existing matching installation after
    an initial download exhausted the small `/tmp` filesystem; other dependencies came
    from the package index. Packaging uses temporary directories on the project
    filesystem and publishes local archives on that same filesystem.
    
    ## Behaviors covered
    
    - Targets below batch size, non-divisible allowances, per-file caps, duplicate-only
      chunks, duplicate IDs in a batch, and exact inserted-row counting.
    - Transaction rollback, uncertain commit acknowledgement recovery, invalid-row
      isolation, advisory-lock exclusion, stale/stalled cursor rejection, failed-file
      resume, verified partial-cursor reuse, and preservation of legacy completed files.
    - Real gzip member offsets, ignored HTTP Range, unknown response length, changed
      source validators, malformed ranges, truncated HTTP/gzip, CRC corruption, decoded
      oversized HTTP bodies, result-budget replay, and non-HTML input-budget progress.
    - French accents, declared encodings, JSON-LD metadata, nonoverlapping language
      samples, and real English/French/Arabic versus Spanish/Persian/Urdu classification.
    - Streaming RAG consumption and early-close cleanup; eager-loader limit enforcement.
    
    ## Remaining cluster validation
    
    When ResourceManager and workers are available, use a configured PostgreSQL database
    and run:
    
    ```bash
    NUM_FILES=1 MAX_ACCEPTED_ARTICLES=10 MAX_ACCEPTED_PER_FILE=10 ./run_to_db.sh
    NUM_FILES=3 MAX_ACCEPTED_ARTICLES=9 MAX_ACCEPTED_PER_FILE=3 ./run_to_db.sh
    ```
    
    Measure full executor-container memory and sustained real-CC-NEWS throughput before
    raising defaults. Atomic HDFS artifact publication has been implemented but could
    not be exercised against the unavailable cluster. There is no production before/after
    throughput comparison in this validation.
    
    Reproducible local checks are in `tests/test_ingestion.py`, `tests/test_launcher.py`,
    `tests/test_rag_loader.py`, `tests/spark_smoke.py`, `tests/memory_probe.py`, and
    `tests/package_smoke.py`. The disposable PostgreSQL server used during this session
    was stopped after testing.
    ✓ • 0ms

## Activity

    $ tail -n 35 /tmp/warc-v2-yarn-one.log
        df -h . /tmp
        ls -lh pyspark_venv-*.tar.gz spark-libs-*.zip
    Filesystem      Size  Used Avail Use% Mounted on
    /dev/sda8       9.2G  7.1G  1.7G  82% /home/spark-master/rag_news_project/spark_warc_v2
    /dev/sda7       552M  209M  302M  41% /tmp
    ls: cannot access 'spark-libs-*.zip': No such file or directory
    -rw------- 1 hadoop hadoop 202M Sep 30 11:26 pyspark_venv-24a01a04fd03a793c2fe88eff6b704d5f7a740b4e34a26e149b4e966f96b5a52.tar.gz
    ✗ (2) • 186ms

## Assistant

All three YARN workers are running, and HDFS is out of safe mode. The first smoke run is uploading its artifacts and is capped at 10 new articles from one file.

## Activity

    $ tail -n 45 /tmp/warc-v2-yarn-one.log
    ✓ • 0ms

## Activity

    $ timeout 15 hdfs dfs -ls /user/hadoop/apps/spark
        ps -u hadoop -o pid,etime,comm
    Found 5 items
    -rw-r--r--   2 hadoop supergroup  100689950 2026-09-29 11:49 /user/hadoop/apps/spark/pyspark_venv-0172da63e7d3edcfdfae5953ed4b5e1f.tar.gz
    -rw-r--r--   2 hadoop supergroup  211582013 2026-09-30 11:33 /user/hadoop/apps/spark/pyspark_venv-9970df60f0f54948b032fcc5bd3aed4972da155ddaa46f593a1b06db1fd731fe.tar.gz
    -rw-r--r--   2 hadoop supergroup  376308439 2026-09-28 14:15 /user/hadoop/apps/spark/pyspark_venv-d1c93f46f6612013d5ba93d3ebf7e837.tar.gz
    -rw-r--r--   2 hadoop supergroup  444261627 2026-09-30 11:34 /user/hadoop/apps/spark/spark-libs-40912d7723e6c1e598007f0a0c048f1b7aa6c7363f0421577e03c48bc1845100.zip.upload-.pack-XTu4ir
    -rw-r--r--   2 hadoop supergroup  444261627 2026-09-28 15:22 /user/hadoop/apps/spark/spark-libs.zip
        PID     ELAPSED COMMAND
       1510       56:46 codex
       1761       51:20 codex
       2222       36:00 bash
       2251       35:14 codex
       2390       34:23 codex-code-mode
       4602       03:00 bash
       4689       02:49 systemd
       4692       02:49 (sd-pam)
       4741       02:49 java
       4918       02:42 java
       5168       02:08 java
       5604       00:47 bash
       5612       00:46 postgres
       5613       00:46 postgres
       5614       00:46 postgres
       5615       00:46 postgres
       5616       00:46 postgres
       5617       00:46 postgres
       5619       00:46 postgres
       5620       00:46 postgres
       5621       00:46 postgres
       5624       00:46 bash
       6051       00:05 ps
       6097       00:01 java
    ✓ • 5.10s

## Activity

    $ tail -n 40 /tmp/warc-v2-yarn-one.log
        ls -lh spark-libs-*.zip
    -rw-rw-r-- 1 hadoop hadoop 424M Sep 30 11:34 spark-libs-40912d7723e6c1e598007f0a0c048f1b7aa6c7363f0421577e03c48bc1845100.zip
    ✓ • 0ms

## Activity

    $ tail -n 45 /tmp/warc-v2-yarn-one.log
    Resume command: RESUME_RUN_ID=7dfd5c9d-deaa-41c6-b9fe-831216cf82c8 ./run_to_db.sh
    Using Spark's default log4j profile: org/apache/spark/log4j2-defaults.properties
    26/09/30 11:34:38 INFO SparkContext: Running Spark version 4.2.0
    26/09/30 11:34:38 INFO SparkContext: OS info Linux, 6.12.107+deb13-amd64, amd64
    26/09/30 11:34:38 INFO SparkContext: Java version 21.0.12.1+1-1-deb13u1-Debian
    26/09/30 11:34:38 INFO ResourceUtils: ==============================================================
    26/09/30 11:34:38 INFO ResourceUtils: No custom resources configured for spark.driver.
    26/09/30 11:34:38 INFO ResourceUtils: ==============================================================
    26/09/30 11:34:38 INFO SparkContext: Submitted application: CC-NEWS-Bounded-Ingest
    26/09/30 11:34:38 INFO SecurityManager: Changing view acls to: hadoop
    26/09/30 11:34:38 INFO SecurityManager: Changing modify acls to: hadoop
    26/09/30 11:34:38 INFO SecurityManager: Changing view acls groups to: hadoop
    26/09/30 11:34:38 INFO SecurityManager: Changing modify acls groups to: hadoop
    26/09/30 11:34:38 INFO SecurityManager: SecurityManager: authentication disabled; ui acls disabled; users with view permissions: hadoop groups with view permissions: EMPTY; users with modify permissions: hadoop; groups with modify permissions: EMPTY; RPC SSL disabled
    26/09/30 11:34:38 INFO Utils: Successfully started service 'sparkDriver' on port 40971.
    26/09/30 11:34:38 INFO SparkEnv: Registering MapOutputTracker
    26/09/30 11:34:38 INFO SparkEnv: Registering BlockManagerMaster
    26/09/30 11:34:38 INFO BlockManagerMasterEndpoint: Using org.apache.spark.storage.DefaultTopologyMapper for getting topology information
    26/09/30 11:34:38 INFO BlockManagerMasterEndpoint: BlockManagerMasterEndpoint up
    26/09/30 11:34:38 INFO SparkEnv: Registering BlockManagerMasterHeartbeat
    26/09/30 11:34:38 INFO DiskBlockManager: Created local directory at /tmp/blockmgr-f8b0935c-2d0c-4756-ab19-4f978383516b
    26/09/30 11:34:38 INFO SparkEnv: Registering OutputCommitCoordinator
    26/09/30 11:34:38 INFO JettyUtils: Start Jetty 0.0.0.0:4040 for SparkUI
    26/09/30 11:34:39 INFO Utils: Successfully started service 'SparkUI' on port 4040.
    26/09/30 11:34:39 INFO ResourceProfile: Default ResourceProfile created, executor resources: Map(memoryOverhead -> name: memoryOverhead, amount: 512, script: , vendor: , cores -> name: cores, amount: 1, script: , vendor: , memory -> name: memory, amount: 512, script: , vendor: , offHeap -> name: offHeap, amount: 0, script: , vendor: ), task resources: Map(cpus -> name: cpus, amount: 1.0)
    26/09/30 11:34:39 INFO ResourceProfile: Limiting resource is cpus at 1 tasks per executor
    26/09/30 11:34:39 INFO ResourceProfileManager: Added ResourceProfile id: 0
    26/09/30 11:34:39 INFO SecurityManager: Changing view acls to: hadoop
    26/09/30 11:34:39 INFO SecurityManager: Changing modify acls to: hadoop
    26/09/30 11:34:39 INFO SecurityManager: Changing view acls groups to: hadoop
    26/09/30 11:34:39 INFO SecurityManager: Changing modify acls groups to: hadoop
    26/09/30 11:34:39 INFO SecurityManager: SecurityManager: authentication disabled; ui acls disabled; users with view permissions: hadoop groups with view permissions: EMPTY; users with modify permissions: hadoop; groups with modify permissions: EMPTY; RPC SSL disabled
    26/09/30 11:34:39 INFO DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at spark-master/192.168.56.10:8032
    26/09/30 11:34:39 INFO Configuration: resource-types.xml not found
    26/09/30 11:34:39 INFO ResourceUtils: Unable to find 'resource-types.xml'.
    26/09/30 11:34:39 INFO Client: Verifying our application has not requested more than the maximum memory capability of the cluster (6144 MB per container)
    26/09/30 11:34:39 INFO Client: Will allocate AM container, with 896 MB memory including 384 MB overhead
    26/09/30 11:34:39 INFO Client: Setting up container launch context for our AM
    26/09/30 11:34:39 INFO Client: Setting up the launch environment for our AM container
    26/09/30 11:34:39 INFO Client: Preparing resources for our AM container
    26/09/30 11:34:39 INFO Client: Source and destination file systems are the same. Not copying hdfs:/user/hadoop/apps/spark/spark-libs-40912d7723e6c1e598007f0a0c048f1b7aa6c7363f0421577e03c48bc1845100.zip
    26/09/30 11:34:39 INFO Client: Source and destination file systems are the same. Not copying hdfs://spark-master:9000/user/hadoop/apps/spark/pyspark_venv-9970df60f0f54948b032fcc5bd3aed4972da155ddaa46f593a1b06db1fd731fe.tar.gz#environment
    26/09/30 11:34:39 INFO Client: Uploading resource file:/opt/spark-4.2.0-bin-hadoop3/python/lib/pyspark.zip -> hdfs://spark-master:9000/user/hadoop/.sparkStaging/application_1790757150855_0001/pyspark.zip
    26/09/30 11:34:39 INFO Client: Uploading resource file:/opt/spark-4.2.0-bin-hadoop3/python/lib/py4j-0.10.9.9-src.zip -> hdfs://spark-master:9000/user/hadoop/.sparkStaging/application_1790757150855_0001/py4j-0.10.9.9-src.zip
    26/09/30 11:34:39 INFO Client: Uploading resource file:/home/spark-master/rag_news_project/spark_warc_v2/.pack-XTu4ir/project_code.zip -> hdfs://spark-master:9000/user/hadoop/.sparkStaging/application_1790757150855_0001/project_code.zip
    ✓ • 0ms

## Activity

    $ tail -n 35 /tmp/warc-v2-yarn-one.log
    26/09/30 11:34:55 INFO YarnClientSchedulerBackend: Add WebUI Filter. org.apache.spark.deploy.yarn.AmIpFilter, Map(PROXY_HOSTS -> spark-master, PROXY_URI_BASES -> http://spark-master:8088/proxy/application_1790757150855_0001), /proxy/application_1790757150855_0001
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /jobs: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /jobs/json: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /jobs/job: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /jobs/job/json: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /stages: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /stages/json: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /stages/stage: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /stages/stage/json: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /stages/pool: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /stages/pool/json: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /stages/taskThreadDump: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /stages/taskThreadDump/json: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /storage: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /storage/json: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /storage/rdd: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /storage/rdd/json: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /environment: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /environment/json: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /executors: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /executors/json: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /executors/threadDump: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /executors/threadDump/json: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /executors/heapHistogram: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /executors/heapHistogram/json: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /static: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /api: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /metrics: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /jobs/job/kill: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /stages/stage/kill: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:56 INFO ServerInfo: Adding filter to /metrics/json: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:56 INFO YarnSchedulerBackend$YarnSchedulerEndpoint: ApplicationMaster registered as NettyRpcEndpointRef(spark-client://YarnAM)
    26/09/30 11:35:00 INFO YarnSchedulerBackend$YarnDriverEndpoint: Registered executor NettyRpcEndpointRef(spark-client://Executor) (192.168.56.13:59942) with ID 2, ResourceProfileId 0
    26/09/30 11:35:01 INFO BlockManagerMasterEndpoint: Registering block manager worker3:44993 with 127.2 MiB RAM, BlockManagerId(2, worker3, 44993, None)
    ✓ • 0ms

## Assistant

The artifacts uploaded successfully, and YARN has started the application. A remote executor has registered; I’m waiting for the first 10-article result before starting the three-file test.

## Activity

    $ tail -n 30 /tmp/warc-v2-yarn-one.log
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /stages/json: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /stages/stage: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /stages/stage/json: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /stages/pool: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /stages/pool/json: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /stages/taskThreadDump: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /stages/taskThreadDump/json: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /storage: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /storage/json: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /storage/rdd: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /storage/rdd/json: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /environment: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /environment/json: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /executors: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /executors/json: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /executors/threadDump: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /executors/threadDump/json: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /executors/heapHistogram: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /executors/heapHistogram/json: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /static: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /api: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /metrics: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /jobs/job/kill: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /stages/stage/kill: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:56 INFO ServerInfo: Adding filter to /metrics/json: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:56 INFO YarnSchedulerBackend$YarnSchedulerEndpoint: ApplicationMaster registered as NettyRpcEndpointRef(spark-client://YarnAM)
    26/09/30 11:35:00 INFO YarnSchedulerBackend$YarnDriverEndpoint: Registered executor NettyRpcEndpointRef(spark-client://Executor) (192.168.56.13:59942) with ID 2, ResourceProfileId 0
    26/09/30 11:35:01 INFO BlockManagerMasterEndpoint: Registering block manager worker3:44993 with 127.2 MiB RAM, BlockManagerId(2, worker3, 44993, None)
    26/09/30 11:35:09 INFO YarnClientSchedulerBackend: SchedulerBackend is ready for scheduling beginning after waiting maxRegisteredResourcesWaitingTime: 30000.0(ms)
    ✓ • 0ms

## Activity

    $ /usr/lib/postgresql/18/bin/pg_ctl -D /tmp/warc-v2-test-pg -l /tmp/warc-v2-test-pg.log -o '-k /tmp/warc-v2-test-pg -p 55439 -c listen_addresses=127.0.0.1 -c shared_buffers=16MB' start
        PGHOST=/tmp/warc-v2-test-pg PGPORT=55439 PGUSER=hadoop PGDATABASE=postgres psql -v ON_ERROR_STOP=1 -c 'CREATE SCHEMA yarn_validation;'
        PGHOST=/tmp/warc-v2-test-pg PGPORT=55439 PGUSER=hadoop PGDATABASE=postgres PGOPTIONS='-c search_path=yarn_validation' NUM_FILES=1 MAX_FILES_PER_ROUND=1 MAX_ACCEPTED_ARTICLES=10 MAX_ACCEPTED_PER_FILE=10 ./run_to_db.sh > /tmp/warc-v2-yarn-one.log 2>&1
    waiting for server to start.... done
    server started
    CREATE SCHEMA
    ✓ • 1m 49s

## Activity

    $ python3 - <<'PY'
        import urllib.request,json
        for url in ['http://spark-master:8088/ws/v1/cluster/apps/application_1790757150855_0001','http://spark-master:4040/api/v1/applications/application_1790757150855_0001/executors']:
         try:
          with urllib.request.urlopen(url,timeout=8) as r: data=json.load(r)
          if isinstance(data,dict):
           a=data.get('app',data); print({k:a.get(k) for k in ['id','state','finalStatus','runningContainers','allocatedMB','diagnostics']})
          else: print([{k:e.get(k) for k in ['id','hostPort','isActive','activeTasks','completedTasks','failedTasks','peakMemoryMetrics']} for e in data])
         except Exception as e: print(type(e).__name__,str(e))
        PY
    {'id': 'application_1790757150855_0001', 'state': 'FINISHED', 'finalStatus': 'SUCCEEDED', 'runningContainers': -1, 'allocatedMB': -1, 'diagnostics': ''}
    URLError <urlopen error [Errno 111] Connection refused>
    ✓ • 928ms

## Activity

    $ tail -n 15 /tmp/warc-v2-yarn-one.log
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /api: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /metrics: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /jobs/job/kill: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:55 INFO ServerInfo: Adding filter to /stages/stage/kill: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:56 INFO ServerInfo: Adding filter to /metrics/json: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:34:56 INFO YarnSchedulerBackend$YarnSchedulerEndpoint: ApplicationMaster registered as NettyRpcEndpointRef(spark-client://YarnAM)
    26/09/30 11:35:00 INFO YarnSchedulerBackend$YarnDriverEndpoint: Registered executor NettyRpcEndpointRef(spark-client://Executor) (192.168.56.13:59942) with ID 2, ResourceProfileId 0
    26/09/30 11:35:01 INFO BlockManagerMasterEndpoint: Registering block manager worker3:44993 with 127.2 MiB RAM, BlockManagerId(2, worker3, 44993, None)
    26/09/30 11:35:09 INFO YarnClientSchedulerBackend: SchedulerBackend is ready for scheduling beginning after waiting maxRegisteredResourcesWaitingTime: 30000.0(ms)
    Wave 1: committed 10/10; new=10; worker peak RSS MiB=[185.7]
    Run 7dfd5c9d-deaa-41c6-b9fe-831216cf82c8: complete; committed 10/10 new articles
      https://data.commoncrawl.org/crawl-data/CC-NEWS/2026/05/CC-NEWS-20260501024825-07751.warc.gz: 10 new; quota_reached
    Counters: {"accepted_candidates": 10, "already_saved": 0, "chunk_duplicates": 0, "compressed_bytes_read": 1441792, "elapsed_seconds": 9.284, "language_rejected": 9, "non_html": 24, "oversized_article": 0, "oversized_html": 0, "records": 47, "result_bytes": 38952, "too_short_or_corrupt": 4}
    Resume command: RESUME_RUN_ID=7dfd5c9d-deaa-41c6-b9fe-831216cf82c8 ./run_to_db.sh
    ✓ • 0ms

## Assistant

The first YARN run passed: it committed exactly 10 real CC-NEWS articles and exited successfully. The worker’s peak Python RSS was about 186 MiB. I’m now running three files together, with a total target of nine and a cap of three per file, while collecting executor metrics.

## Activity

    $ cat > /tmp/warc-v2-monitor-three.py <<'PY'
        import json,os,subprocess,time,urllib.request
        from pathlib import Path
        root=Path('/home/spark-master/rag_news_project/spark_warc_v2')
        env=dict(os.environ,PGHOST='/tmp/warc-v2-test-pg',PGPORT='55439',PGUSER='hadoop',PGDATABASE='postgres',PGOPTIONS='-c search_path=yarn_validation',NUM_FILES='3',MAX_FILES_PER_ROUND='3',MAX_ACCEPTED_ARTICLES='9',MAX_ACCEPTED_PER_FILE='3',SPARK_SUBMIT_OPTS='-Dspark.executor.processTreeMetrics.enabled=true -Dspark.executor.metrics.pollingInterval=1000 -Dspark.eventLog.logStageExecutorMetrics=true')
        samples=[]
        with open('/tmp/warc-v2-yarn-three.log','w') as log:
         process=subprocess.Popen(['./run_to_db.sh'],cwd=root,env=env,stdout=log,stderr=subprocess.STDOUT)
         while process.poll() is None:
          try:
           with urllib.request.urlopen('http://spark-master:4040/api/v1/applications',timeout=2) as response: apps=json.load(response)
           if apps:
            app=apps[0]['id']
            with urllib.request.urlopen(f'http://spark-master:4040/api/v1/applications/{app}/executors',timeout=2) as response: executors=json.load(response)
            samples.append(dict(time=time.time(),app=app,executors=executors))
          except (OSError,ValueError): pass
          time.sleep(1)
        Path('/tmp/warc-v2-yarn-metrics.json').write_text(json.dumps(samples))
        print('job_exit',process.returncode,'metric_samples',len(samples))
        raise SystemExit(process.returncode)
        PY
    ✓ • 7ms

## Activity

    $ tail -n 22 /tmp/warc-v2-yarn-three.log
    26/09/30 11:36:54 INFO ServerInfo: Adding filter to /stages/pool/json: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:36:54 INFO ServerInfo: Adding filter to /stages/taskThreadDump: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:36:54 INFO ServerInfo: Adding filter to /stages/taskThreadDump/json: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:36:54 INFO ServerInfo: Adding filter to /storage: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:36:54 INFO ServerInfo: Adding filter to /storage/json: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:36:54 INFO ServerInfo: Adding filter to /storage/rdd: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:36:54 INFO ServerInfo: Adding filter to /storage/rdd/json: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:36:54 INFO ServerInfo: Adding filter to /environment: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:36:54 INFO ServerInfo: Adding filter to /environment/json: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:36:54 INFO ServerInfo: Adding filter to /executors: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:36:54 INFO ServerInfo: Adding filter to /executors/json: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:36:54 INFO ServerInfo: Adding filter to /executors/threadDump: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:36:54 INFO ServerInfo: Adding filter to /executors/threadDump/json: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:36:54 INFO ServerInfo: Adding filter to /executors/heapHistogram: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:36:54 INFO ServerInfo: Adding filter to /executors/heapHistogram/json: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:36:54 INFO ServerInfo: Adding filter to /static: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:36:54 INFO ServerInfo: Adding filter to /: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:36:54 INFO ServerInfo: Adding filter to /api: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:36:54 INFO ServerInfo: Adding filter to /metrics: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:36:54 INFO ServerInfo: Adding filter to /jobs/job/kill: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:36:54 INFO ServerInfo: Adding filter to /stages/stage/kill: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:36:54 INFO ServerInfo: Adding filter to /metrics/json: org.apache.spark.deploy.yarn.AmIpFilter
    ✓ • 0ms

## Activity

    $ python3 /tmp/warc-v2-monitor-three.py
    job_exit 0 metric_samples 12
    ✓ • 37.64s

## Activity

    $ tail -n 16 /tmp/warc-v2-yarn-three.log
    26/09/30 11:36:54 INFO ServerInfo: Adding filter to /stages/stage/kill: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:36:54 INFO ServerInfo: Adding filter to /metrics/json: org.apache.spark.deploy.yarn.AmIpFilter
    26/09/30 11:36:58 INFO YarnSchedulerBackend$YarnDriverEndpoint: Registered executor NettyRpcEndpointRef(spark-client://Executor) (192.168.56.13:58196) with ID 3, ResourceProfileId 0
    26/09/30 11:36:58 INFO BlockManagerMasterEndpoint: Registering block manager worker3:42917 with 127.2 MiB RAM, BlockManagerId(3, worker3, 42917, None)
    26/09/30 11:36:59 INFO YarnSchedulerBackend$YarnDriverEndpoint: Registered executor NettyRpcEndpointRef(spark-client://Executor) (192.168.56.12:59684) with ID 1, ResourceProfileId 0
    26/09/30 11:36:59 INFO BlockManagerMasterEndpoint: Registering block manager worker2:38363 with 127.2 MiB RAM, BlockManagerId(1, worker2, 38363, None)
    26/09/30 11:36:59 INFO YarnSchedulerBackend$YarnDriverEndpoint: Registered executor NettyRpcEndpointRef(spark-client://Executor) (192.168.56.11:50750) with ID 2, ResourceProfileId 0
    26/09/30 11:36:59 INFO YarnClientSchedulerBackend: SchedulerBackend is ready for scheduling beginning after reached minRegisteredResourcesRatio: 0.8
    26/09/30 11:37:00 INFO BlockManagerMasterEndpoint: Registering block manager worker1:37453 with 127.2 MiB RAM, BlockManagerId(2, worker1, 37453, None)
    Wave 1: committed 9/9; new=9; worker peak RSS MiB=[173.1, 174.4, 176.5]
    Run aac233f9-25f9-4043-89f0-ed4707e88c34: complete; committed 9/9 new articles
      https://data.commoncrawl.org/crawl-data/CC-NEWS/2026/05/CC-NEWS-20260501024825-07751.warc.gz: 3 new; quota_reached
      https://data.commoncrawl.org/crawl-data/CC-NEWS/2026/05/CC-NEWS-20260501055621-07752.warc.gz: 3 new; quota_reached
      https://data.commoncrawl.org/crawl-data/CC-NEWS/2026/05/CC-NEWS-20260501080229-07753.warc.gz: 3 new; quota_reached
    Counters: {"accepted_candidates": 9, "already_saved": 0, "chunk_duplicates": 0, "compressed_bytes_read": 1441792, "elapsed_seconds": 10.639, "language_rejected": 17, "non_html": 29, "oversized_article": 0, "oversized_html": 0, "records": 56, "result_bytes": 30691, "too_short_or_corrupt": 1}
    Resume command: RESUME_RUN_ID=aac233f9-25f9-4043-89f0-ed4707e88c34 ./run_to_db.sh
    ✓ • 0ms

## Activity

    $ python3 - <<'PY'
        import json
        samples=json.load(open('/tmp/warc-v2-yarn-metrics.json')); peak={}
        for s in samples:
         for e in s['executors']:
          if e['id']=='driver': continue
          key=e['id']; p=peak.setdefault(key,{'host':e['hostPort'],'max_active_tasks':0,'metrics':{}})
          p['max_active_tasks']=max(p['max_active_tasks'],e.get('activeTasks',0))
          for k,v in e.get('peakMemoryMetrics',{}).items():p['metrics'][k]=max(p['metrics'].get(k,0),v)
        print(json.dumps({'samples':len(samples),'max_simultaneous_active_executors':max(sum(e.get('activeTasks',0)>0 for e in s['executors'] if e['id']!='driver') for s in samples),'executors':peak},indent=2))
        PY
    {
      "samples": 12,
      "max_simultaneous_active_executors": 3,
      "executors": {
        "3": {
          "host": "worker3:42917",
          "max_active_tasks": 1,
          "metrics": {
            "JVMHeapMemory": 59416368,
            "JVMOffHeapMemory": 61862320,
            "OnHeapExecutionMemory": 0,
            "OffHeapExecutionMemory": 0,
            "OnHeapStorageMemory": 30122,
            "OffHeapStorageMemory": 0,
            "OnHeapUnifiedMemory": 30122,
            "OffHeapUnifiedMemory": 0,
            "DirectPoolMemory": 41024,
            "MappedPoolMemory": 0,
            "ProcessTreeJVMVMemory": 2415517696,
            "ProcessTreeJVMRSSMemory": 226004992,
            "ProcessTreePythonVMemory": 576376832,
            "ProcessTreePythonRSSMemory": 221278208,
            "ProcessTreeOtherVMemory": 0,
            "ProcessTreeOtherRSSMemory": 0,
            "MinorGCCount": 14,
            "MinorGCTime": 77,
            "MajorGCCount": 0,
            "MajorGCTime": 0,
            "TotalGCTime": 89,
            "ConcurrentGCCount": 8,
            "ConcurrentGCTime": 12
          }
        },
        "2": {
          "host": "worker1",
          "max_active_tasks": 1,
          "metrics": {}
        },
        "1": {
          "host": "worker2:38363",
          "max_active_tasks": 1,
          "metrics": {}
        }
      }
    }
    ✓ • 0ms

## Assistant

The three-file YARN run passed too: exactly nine new articles, split 3/3/3. Metrics confirm simultaneous work on worker1, worker2, and worker3. I’m checking the saved counts and completed-run resume behavior, then updating the validation report.

## Activity

    $ cat /tmp/warc-v2-yarn-resume.log
    WARNING: Using incubator modules: jdk.incubator.vector
    26/09/30 11:38:08 WARN NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable
    Resuming run aac233f9-25f9-4043-89f0-ed4707e88c34: 9 committed
    Resume command: RESUME_RUN_ID=aac233f9-25f9-4043-89f0-ed4707e88c34 ./run_to_db.sh
    Run aac233f9-25f9-4043-89f0-ed4707e88c34: complete; committed 9/9 new articles
      https://data.commoncrawl.org/crawl-data/CC-NEWS/2026/05/CC-NEWS-20260501024825-07751.warc.gz: 3 new; quota_reached
      https://data.commoncrawl.org/crawl-data/CC-NEWS/2026/05/CC-NEWS-20260501055621-07752.warc.gz: 3 new; quota_reached
      https://data.commoncrawl.org/crawl-data/CC-NEWS/2026/05/CC-NEWS-20260501080229-07753.warc.gz: 3 new; quota_reached
    Counters: {"accepted_candidates": 9, "already_saved": 0, "chunk_duplicates": 0, "compressed_bytes_read": 1441792, "elapsed_seconds": 10.639, "language_rejected": 17, "non_html": 29, "oversized_article": 0, "oversized_html": 0, "records": 56, "result_bytes": 30691, "too_short_or_corrupt": 1}
    Resume command: RESUME_RUN_ID=aac233f9-25f9-4043-89f0-ed4707e88c34 ./run_to_db.sh
    ✓ • 0ms

## Activity

    $ PGHOST=/tmp/warc-v2-test-pg PGPORT=55439 PGUSER=hadoop PGDATABASE=postgres PGOPTIONS='-c search_path=yarn_validation' RESUME_RUN_ID=aac233f9-25f9-4043-89f0-ed4707e88c34 ./run_to_db.sh > /tmp/warc-v2-yarn-resume.log 2>&1
        PGHOST=/tmp/warc-v2-test-pg PGPORT=55439 PGUSER=hadoop PGDATABASE=postgres PGOPTIONS='-c search_path=yarn_validation' psql -v ON_ERROR_STOP=1 -c 'SELECT run_id,status,target_articles,per_file_target,inserted_count FROM ingest_runs ORDER BY created_at;' -c 'SELECT count(*) AS pages,count(DISTINCT warc_record_id) AS distinct_ids FROM pages;' -c 'SELECT count(*) AS complete_articles FROM pages p JOIN metadata m ON p.id=m.page_id JOIN content c ON p.id=c.page_id;' -c 'SELECT run_id,start_offset,next_offset,stats->> $$worker_host$$ AS worker FROM ingest_chunks ORDER BY committed_at;'
        hdfs dfs -ls /spark-logs/eventlog_v2_application_1790757150855_0002
        yarn node -list
                    run_id                |  status  | target_articles | per_file_target | inserted_count
    --------------------------------------+----------+-----------------+-----------------+----------------
     7dfd5c9d-deaa-41c6-b9fe-831216cf82c8 | complete |              10 |              10 |             10
     aac233f9-25f9-4043-89f0-ed4707e88c34 | complete |               9 |               3 |              9
    (2 rows)
    
     pages | distinct_ids
    -------+--------------
        19 |           19
    (1 row)
    
     complete_articles
    -------------------
                    19
    (1 row)
    
                    run_id                | start_offset | next_offset | worker
    --------------------------------------+--------------+-------------+---------
     7dfd5c9d-deaa-41c6-b9fe-831216cf82c8 |            0 |     1391560 | worker3
     aac233f9-25f9-4043-89f0-ed4707e88c34 |      1391560 |     1761274 | worker2
     aac233f9-25f9-4043-89f0-ed4707e88c34 |            0 |      424916 | worker3
     aac233f9-25f9-4043-89f0-ed4707e88c34 |            0 |      543280 | worker1
    (4 rows)
    
    Found 2 items
    -rw-rw----   2 hadoop supergroup          0 2026-09-30 11:37 /spark-logs/eventlog_v2_application_1790757150855_0002/appstatus_application_1790757150855_0002
    -rw-rw----   2 hadoop supergroup      31027 2026-09-30 11:37 /spark-logs/eventlog_v2_application_1790757150855_0002/events_1_application_1790757150855_0002.zstd
    2026-09-30 11:38:13,174 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at spark-master/192.168.56.10:8032
    Total Nodes:3
             Node-Id         Node-State    Node-Http-Address    Number-of-Running-Containers
       worker2:43653            RUNNING         worker2:8042                               0
       worker1:42213            RUNNING         worker1:8042                               0
       worker3:41605            RUNNING         worker3:8042                               0
    ✓ • 13.92s

## Activity

    $ hdfs dfs -cat /spark-logs/eventlog_v2_application_1790757150855_0002/events_1_application_1790757150855_0002.zstd > /tmp/warc-v2-yarn-events.zstd
        python3 - <<'PY'
        import json,urllib.request
        with urllib.request.urlopen('http://spark-master:8088/ws/v1/cluster/apps/application_1790757150855_0002',timeout=10) as r:a=json.load(r)['app']
        print({k:a.get(k) for k in ('id','state','finalStatus','diagnostics','memorySeconds','vcoreSeconds')})
        PY
    {'id': 'application_1790757150855_0002', 'state': 'FINISHED', 'finalStatus': 'SUCCEEDED', 'diagnostics': '', 'memorySeconds': 68985, 'vcoreSeconds': 64}
    ✓ • 1.77s

## Activity

    $ ../spark_warc_project/.venv/bin/python - <<'PY'
        import zstandard,io,json,collections
        with open('/tmp/warc-v2-yarn-events.zstd','rb') as f:
         with zstandard.ZstdDecompressor().stream_reader(f) as r:
          events=[json.loads(l) for l in io.TextIOWrapper(r)]
        print(collections.Counter(e['Event'] for e in events))
        for e in events:
         if e['Event']=='SparkListenerStageExecutorMetrics': print(json.dumps(e))
         if e['Event']=='SparkListenerTaskEnd':
          t=e['Task Info'];print('TASK', {k:t.get(k) for k in ['Task ID','Executor ID','Host','Launch Time','Finish Time','Failed','Killed']})
        PY
    Counter({'SparkListenerBlockManagerAdded': 4, 'SparkListenerStageExecutorMetrics': 4, 'SparkListenerExecutorAdded': 3, 'SparkListenerTaskStart': 3, 'SparkListenerTaskEnd': 3, 'SparkListenerExecutorMetricsUpdate': 2, 'SparkListenerLogStart': 1, 'SparkListenerResourceProfileAdded': 1, 'org.apache.spark.scheduler.SparkListenerMiscellaneousProcessAdded': 1, 'SparkListenerEnvironmentUpdate': 1, 'SparkListenerApplicationStart': 1, 'SparkListenerJobStart': 1, 'SparkListenerStageSubmitted': 1, 'SparkListenerStageCompleted': 1, 'SparkListenerJobEnd': 1, 'SparkListenerApplicationEnd': 1})
    TASK {'Task ID': 1, 'Executor ID': '3', 'Host': 'worker3', 'Launch Time': 1790757422629, 'Finish Time': 1790757426014, 'Failed': False, 'Killed': False}
    TASK {'Task ID': 2, 'Executor ID': '2', 'Host': 'worker1', 'Launch Time': 1790757422632, 'Finish Time': 1790757429735, 'Failed': False, 'Killed': False}
    TASK {'Task ID': 0, 'Executor ID': '1', 'Host': 'worker2', 'Launch Time': 1790757422598, 'Finish Time': 1790757429906, 'Failed': False, 'Killed': False}
    {"Event": "SparkListenerStageExecutorMetrics", "Executor ID": "1", "Stage ID": 0, "Stage Attempt ID": 0, "Executor Metrics": {"JVMHeapMemory": 50010432, "JVMOffHeapMemory": 62032264, "OnHeapExecutionMemory": 0, "OffHeapExecutionMemory": 0, "OnHeapStorageMemory": 30122, "OffHeapStorageMemory": 0, "OnHeapUnifiedMemory": 30122, "OffHeapUnifiedMemory": 0, "DirectPoolMemory": 41024, "MappedPoolMemory": 0, "ProcessTreeJVMVMemory": 2415525888, "ProcessTreeJVMRSSMemory": 223240192, "ProcessTreePythonVMemory": 568029184, "ProcessTreePythonRSSMemory": 208322560, "ProcessTreeOtherVMemory": 0, "ProcessTreeOtherRSSMemory": 0, "MinorGCCount": 17, "MinorGCTime": 95, "MajorGCCount": 0, "MajorGCTime": 0, "TotalGCTime": 106, "ConcurrentGCCount": 10, "ConcurrentGCTime": 11}}
    {"Event": "SparkListenerStageExecutorMetrics", "Executor ID": "2", "Stage ID": 0, "Stage Attempt ID": 0, "Executor Metrics": {"JVMHeapMemory": 64237416, "JVMOffHeapMemory": 61652952, "OnHeapExecutionMemory": 0, "OffHeapExecutionMemory": 0, "OnHeapStorageMemory": 30122, "OffHeapStorageMemory": 0, "OnHeapUnifiedMemory": 30122, "OffHeapUnifiedMemory": 0, "DirectPoolMemory": 41024, "MappedPoolMemory": 0, "ProcessTreeJVMVMemory": 2415525888, "ProcessTreeJVMRSSMemory": 232685568, "ProcessTreePythonVMemory": 556675072, "ProcessTreePythonRSSMemory": 195575808, "ProcessTreeOtherVMemory": 0, "ProcessTreeOtherRSSMemory": 0, "MinorGCCount": 15, "MinorGCTime": 97, "MajorGCCount": 0, "MajorGCTime": 0, "TotalGCTime": 110, "ConcurrentGCCount": 10, "ConcurrentGCTime": 13}}
    {"Event": "SparkListenerStageExecutorMetrics", "Executor ID": "3", "Stage ID": 0, "Stage Attempt ID": 0, "Executor Metrics": {"JVMHeapMemory": 59416368, "JVMOffHeapMemory": 61862320, "OnHeapExecutionMemory": 0, "OffHeapExecutionMemory": 0, "OnHeapStorageMemory": 30122, "OffHeapStorageMemory": 0, "OnHeapUnifiedMemory": 30122, "OffHeapUnifiedMemory": 0, "DirectPoolMemory": 41024, "MappedPoolMemory": 0, "ProcessTreeJVMVMemory": 2415517696, "ProcessTreeJVMRSSMemory": 226004992, "ProcessTreePythonVMemory": 576376832, "ProcessTreePythonRSSMemory": 221278208, "ProcessTreeOtherVMemory": 0, "ProcessTreeOtherRSSMemory": 0, "MinorGCCount": 14, "MinorGCTime": 77, "MajorGCCount": 0, "MajorGCTime": 0, "TotalGCTime": 89, "ConcurrentGCCount": 8, "ConcurrentGCTime": 12}}
    {"Event": "SparkListenerStageExecutorMetrics", "Executor ID": "driver", "Stage ID": 0, "Stage Attempt ID": 0, "Executor Metrics": {"JVMHeapMemory": 74132096, "JVMOffHeapMemory": 156603944, "OnHeapExecutionMemory": 0, "OffHeapExecutionMemory": 0, "OnHeapStorageMemory": 30122, "OffHeapStorageMemory": 0, "OnHeapUnifiedMemory": 30122, "OffHeapUnifiedMemory": 0, "DirectPoolMemory": 736125, "MappedPoolMemory": 0, "ProcessTreeJVMVMemory": 3337166848, "ProcessTreeJVMRSSMemory": 400478208, "ProcessTreePythonVMemory": 269271040, "ProcessTreePythonRSSMemory": 71487488, "ProcessTreeOtherVMemory": 0, "ProcessTreeOtherRSSMemory": 0, "MinorGCCount": 29, "MinorGCTime": 188, "MajorGCCount": 0, "MajorGCTime": 0, "TotalGCTime": 229, "ConcurrentGCCount": 18, "ConcurrentGCTime": 41}}
    ✓ • 119ms
