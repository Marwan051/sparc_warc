"""Driver-owned chunk storage and bounded source selection."""

import hashlib
import json
from psycopg2.extras import execute_values
from db.db_handler import get_connection


def source_hash(document):
    return hashlib.sha256(json.dumps(document, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def acquire_lock(stage):
    conn = get_connection()
    key = int.from_bytes(hashlib.sha256(f"spark-warc-{stage}".encode()).digest()[:8], "big", signed=True)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT pg_try_advisory_lock(%s)", (key,))
            if not cur.fetchone()[0]:
                raise RuntimeError(f"another {stage} coordinator is active")
        conn.commit()
        return conn
    except BaseException:
        conn.close()
        raise


def iter_pending_documents(conn, version, limit=None):
    # Separate read connection: driver commits must not invalidate this cursor.
    read = get_connection()
    try:
        with read.cursor(name="chunk_source") as cur:
            cur.itersize = 25
            cur.execute("""SELECT p.id, c.cleaned_text, p.url, m.title, m.language
                FROM pages p JOIN content c ON c.page_id=p.id
                LEFT JOIN metadata m ON m.page_id=p.id
                WHERE c.cleaned_text IS NOT NULL AND NOT EXISTS (
                    SELECT 1 FROM chunk_materializations r
                    WHERE r.page_id=p.id AND r.chunking_version=%s)
                ORDER BY p.id LIMIT %s""", (version, limit))
            for page_id, text, url, title, language in cur:
                yield {"page_id": page_id, "text": text, "source": url,
                       "title": title or "", "language": language or ""}
    finally:
        read.close()


def commit_document(conn, version, result):
    chunks = result["chunks"]
    if [c["chunk_index"] for c in chunks] != list(range(len(chunks))):
        raise ValueError("chunk indexes must be contiguous")
    expected = [(c["chunk_index"], c["text_hash"], c["eligible"], c["filter_reason"]) for c in chunks]
    for chunk in chunks:
        if hashlib.sha256(chunk["chunk_text"].encode()).hexdigest() != chunk["text_hash"]:
            raise ValueError("invalid chunk text hash")
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT source_hash,chunk_count FROM chunk_materializations WHERE page_id=%s AND chunking_version=%s",
                        (result["page_id"], version))
            receipt = cur.fetchone()
            cur.execute("SELECT chunk_index,text_hash,eligible,filter_reason FROM article_chunks WHERE page_id=%s AND chunking_version=%s ORDER BY chunk_index",
                        (result["page_id"], version))
            stored = cur.fetchall()
            if receipt or stored:
                if receipt != (result["source_hash"], len(chunks)) or stored != expected:
                    raise ValueError(f"chunking drift for page {result['page_id']}; use a new version")
                return
            if chunks:
                execute_values(cur, """INSERT INTO article_chunks
                    (page_id,chunking_version,chunk_index,chunk_text,text_hash,eligible,filter_reason)
                    VALUES %s""", [(result["page_id"], version, c["chunk_index"], c["chunk_text"],
                                   c["text_hash"], c["eligible"], c["filter_reason"]) for c in chunks], page_size=100)
            cur.execute("INSERT INTO chunk_materializations(page_id,chunking_version,source_hash,chunk_count) VALUES (%s,%s,%s,%s)",
                        (result["page_id"], version, result["source_hash"], len(chunks)))


def counts(conn, version):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*),count(*) FILTER (WHERE NOT eligible) FROM article_chunks WHERE chunking_version=%s", (version,))
        stored, filtered = cur.fetchone()
        cur.execute("SELECT count(*) FROM chunk_materializations WHERE chunking_version=%s", (version,))
        documents = cur.fetchone()[0]
    conn.commit()
    return {"documents": documents, "stored": stored, "filtered": filtered}
