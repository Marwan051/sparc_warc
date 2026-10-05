"""PostgreSQL schema and transactional ingestion helpers."""

import hashlib
import json
import os
import uuid
import tempfile
from functools import wraps
from contextlib import contextmanager
from urllib.parse import urlparse

import psycopg2
from psycopg2.extras import execute_values


def _db_config():
    """Use libpq-compatible environment settings, with legacy defaults."""
    # Leave absent values to libpq (including .pgpass/service/SSL settings).
    values = {"dbname": os.environ.get("PGDATABASE", "warcdb"),
              "user": os.environ.get("PGUSER", "warc_user"),
              "host": os.environ.get("PGHOST", "localhost"),
              "port": os.environ.get("PGPORT", "5432"),
              "password":os.environ.get("PGPASSWORD","password"),
              "connect_timeout": int(os.environ.get("PGCONNECT_TIMEOUT", "10"))}
    if "PGPASSWORD" in os.environ:
        values["password"] = os.environ["PGPASSWORD"]
    return values


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
def init_db(conn=None):
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
    ALTER TABLE ingest_files ADD COLUMN IF NOT EXISTS checkpoint_version INT NOT NULL DEFAULT 1;
    ALTER TABLE ingest_files ADD COLUMN IF NOT EXISTS etag TEXT;
    ALTER TABLE ingest_files ADD COLUMN IF NOT EXISTS last_modified TEXT;
    ALTER TABLE pages ADD COLUMN IF NOT EXISTS author_id INT REFERENCES authors(id) ON DELETE SET NULL;
    ALTER TABLE pages ADD COLUMN IF NOT EXISTS source_file_url TEXT;
    ALTER TABLE pages ADD COLUMN IF NOT EXISTS warc_date TEXT;
    ALTER TABLE metadata ADD COLUMN IF NOT EXISTS arabic_dialect TEXT;
    ALTER TABLE metadata ADD COLUMN IF NOT EXISTS extraction_method TEXT;
    ALTER TABLE websites ALTER COLUMN domain TYPE TEXT;
    ALTER TABLE authors ALTER COLUMN name TYPE TEXT;
    ALTER TABLE pages ALTER COLUMN warc_record_id TYPE TEXT;
    ALTER TABLE metadata ALTER COLUMN title TYPE TEXT;
    ALTER TABLE pages ALTER COLUMN url TYPE TEXT;
    ALTER TABLE metadata ALTER COLUMN published_date TYPE TEXT;
    ALTER TABLE metadata ALTER COLUMN language TYPE TEXT;
    ALTER TABLE metadata ALTER COLUMN arabic_dialect TYPE TEXT;
    """
    try:
        with _cursor(conn) as cur:
            cur.execute("SELECT pg_advisory_xact_lock(782936402)")
            cur.execute("CREATE TABLE IF NOT EXISTS ingest_schema_versions (version INT PRIMARY KEY, applied_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP)")
            cur.execute("SELECT 1 FROM ingest_schema_versions WHERE version=2")
            if not cur.fetchone():
                cur.execute(ddl)
                cur.execute("INSERT INTO ingest_schema_versions(version) VALUES (2)")
            cur.execute("SELECT 1 FROM ingest_schema_versions WHERE version=3")
            has_enrichment_schema = cur.fetchone() is not None
            if not has_enrichment_schema:
                from db.enrichment_schema import DDL
                cur.execute(DDL)
                cur.execute("INSERT INTO ingest_schema_versions(version) VALUES (3)")
            cur.execute("SELECT 1 FROM ingest_schema_versions WHERE version=4")
            if not cur.fetchone():
                from db.vector_schema import DDL
                cur.execute(DDL)
                cur.execute("INSERT INTO ingest_schema_versions(version) VALUES (4)")
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def extract_domain(url):
    try:
        host = (urlparse(url).hostname or "").lower().rstrip(".")
        if host.startswith("www."):
            host = host[4:]
        return host or "unknown_domain"
    except Exception:
        return "unknown_domain"


def acquire_coordinator_lock(manifest_id):
    """Return a live connection holding a global ingestion advisory lock."""
    conn = get_connection()
    key = int.from_bytes(hashlib.sha256(b"spark-warc-ingestion-coordinator").digest()[:8], "big", signed=True)
    with _cursor(conn) as cur:
        cur.execute("SELECT pg_try_advisory_lock(%s);", (key,))
        locked = cur.fetchone()[0]
    if not locked:
        conn.close()
        raise RuntimeError(f"another ingestion coordinator is active for {manifest_id}")
    conn.commit()
    return conn


@connection_scope
def create_run(manifest_id, urls, target_articles, per_file_target, config, conn=None):
    run_id = str(uuid.uuid4())
    try:
        with _cursor(conn) as cur:
            cur.execute(
                "INSERT INTO ingest_runs (run_id,manifest_id,target_articles,per_file_target,config) "
                "VALUES (%s,%s,%s,%s,%s::jsonb)",
                (run_id, manifest_id, target_articles, per_file_target, json.dumps(config)),
            )
            cur.execute("SELECT file_url,complete,bytes_done,checkpoint_version,etag,last_modified FROM ingest_files WHERE manifest_id=%s", (manifest_id,))
            previous = {row[0]: row[1:] for row in cur.fetchall()}
            rows = []
            for i, url in enumerate(urls):
                complete, offset, version, etag, modified = previous.get(url, (False, 0, 1, None, None))
                rows.append((run_id, i, url, complete, "eof" if complete else "pending",
                             offset if version >= 2 else 0, etag if version >= 2 else None,
                             modified if version >= 2 else None))
            if rows:
                execute_values(cur, "INSERT INTO ingest_run_files (run_id,ordinal,file_url,eof,status,next_offset,etag,last_modified) VALUES %s", rows)
        conn.commit()
        return run_id
    except Exception:
        conn.rollback()
        raise


@connection_scope
def load_run(run_id, conn=None):
    with _cursor(conn) as cur:
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


def _write_diagnostic(run_id, chunk_id, rejected):
    directory = os.environ.get("DEAD_LETTER_DIR", "dead_letter")
    os.makedirs(directory, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".pending-", dir=directory, text=True)
    destination = os.path.join(directory, f"{run_id}-{chunk_id}-{uuid.uuid4().hex}.jsonl")
    try:
        with os.fdopen(fd, "w") as stream:
            for row in rejected:
                stream.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")
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


@connection_scope
def commit_chunk(run_id, result, batch_size=25, conn=None):
    """Atomically insert new articles and advance this run's file cursor."""
    try:
        with _cursor(conn) as cur:
            cur.execute("SELECT inserted_count FROM ingest_chunks WHERE chunk_id=%s", (result["chunk_id"],))
            prior = cur.fetchone()
            if prior is not None:
                conn.rollback()
                return prior[0]
            cur.execute("SELECT target_articles,per_file_target,inserted_count FROM ingest_runs WHERE run_id=%s FOR UPDATE", (run_id,))
            target, per_file, total_done = cur.fetchone()
            cur.execute("SELECT inserted_count,next_offset FROM ingest_run_files WHERE run_id=%s AND file_url=%s FOR UPDATE",
                        (run_id, result["file_url"]))
            file_done, cursor = cur.fetchone()
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
            result.setdefault("stats", {})["already_saved"] = len(candidates) - inserted_count - len(rejected)
            result["stats"]["chunk_duplicates"] = len(result["candidates"]) - len(candidates)
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


@connection_scope
def finish_run(run_id, status, conn=None):
    with _cursor(conn) as cur:
        cur.execute("UPDATE ingest_runs SET status=%s,updated_at=CURRENT_TIMESTAMP WHERE run_id=%s", (status, run_id))
    conn.commit()


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
