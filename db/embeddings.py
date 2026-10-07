"""Pending chunk selection and idempotent vector storage."""

import hashlib
import math

import numpy as np
from pgvector.psycopg2 import register_vector
from psycopg2.extras import execute_values

from db.db_handler import get_connection


def iter_pending(config, limit=None):
    """Stream eligible chunks that lack this model/configuration's vector."""
    conn = get_connection()
    try:
        with conn.cursor(name="embedding_source") as cur:
            cur.itersize = 25
            cur.execute("""SELECT c.page_id,c.chunk_index,c.chunk_text,c.text_hash
                FROM article_chunks c
                WHERE c.chunking_version=%s AND c.eligible
                    AND NOT EXISTS (
                        SELECT 1 FROM chunk_embeddings e
                        WHERE e.page_id=c.page_id
                          AND e.chunking_version=c.chunking_version
                          AND e.chunk_index=c.chunk_index
                          AND e.embedding_model=%s
                          AND e.embedding_version=%s)
                ORDER BY c.page_id,c.chunk_index LIMIT %s""",
                (config["chunking_version"], config["embedding_model"],
                 config["embedding_version"], limit))
            for page_id, index, text, text_hash in cur:
                actual_hash = hashlib.sha256(text.encode()).hexdigest()
                if actual_hash != text_hash:
                    raise ValueError(f"stored chunk hash mismatch for page {page_id}, chunk {index}")
                yield {"page_id": page_id, "chunking_version": config["chunking_version"],
                       "chunk_index": index, "text": text, "text_hash": text_hash}
    finally:
        conn.close()


def commit_batch(conn, config, rows):
    """Commit one worker result batch; repeated matching rows are harmless."""
    if not rows:
        return
    keys = [(row["page_id"], config["chunking_version"], row["chunk_index"])
            for row in rows]
    if len(set(keys)) != len(keys):
        raise ValueError("embedding batch contains duplicate chunk identities")
    values = []
    for row in rows:
        vector = row["embedding"]
        if hashlib.sha256(row["text"].encode()).hexdigest() != row["text_hash"]:
            raise ValueError("embedding result text hash mismatch")
        if len(vector) != 1024 or any(not isinstance(x, (int, float)) for x in vector):
            raise ValueError("embedding vector must contain 1024 numeric values")
        if any(not math.isfinite(x) for x in vector):
            raise ValueError("embedding vector contains non-finite values")
        norm = math.sqrt(sum(x * x for x in vector))
        if not math.isclose(norm, 1.0, rel_tol=1e-3, abs_tol=1e-3):
            raise ValueError("embedding vector must be L2-normalized")
        key = keys[len(values)]
        values.append((*key, config["embedding_model"], config["embedding_version"],
                       row["text_hash"], np.asarray(vector, dtype=np.float32)))
    register_vector(conn)
    with conn:
        with conn.cursor() as cur:
            for row in rows:
                cur.execute("""SELECT text_hash,eligible FROM article_chunks
                    WHERE page_id=%s AND chunking_version=%s AND chunk_index=%s""",
                    (row["page_id"], config["chunking_version"], row["chunk_index"]))
                source = cur.fetchone()
                if source != (row["text_hash"], True):
                    raise ValueError(f"source chunk changed or is ineligible for page {row['page_id']}, chunk {row['chunk_index']}")
            execute_values(cur, """INSERT INTO chunk_embeddings
                (page_id,chunking_version,chunk_index,embedding_model,embedding_version,text_hash,embedding)
                VALUES %s ON CONFLICT DO NOTHING""", values, page_size=100)
            for row in rows:
                cur.execute("""SELECT text_hash FROM chunk_embeddings
                    WHERE page_id=%s AND chunking_version=%s AND chunk_index=%s
                      AND embedding_model=%s AND embedding_version=%s""",
                    (row["page_id"], config["chunking_version"], row["chunk_index"],
                     config["embedding_model"], config["embedding_version"]))
                stored = cur.fetchone()
                if stored is None or stored[0] != row["text_hash"]:
                    raise ValueError(f"embedding identity/hash conflict for page {row['page_id']}, chunk {row['chunk_index']}")


def counts(conn, config):
    with conn.cursor() as cur:
        cur.execute("""SELECT count(*) FROM article_chunks c WHERE c.chunking_version=%s AND c.eligible
            AND EXISTS (SELECT 1 FROM chunk_embeddings e WHERE e.page_id=c.page_id
                AND e.chunking_version=c.chunking_version AND e.chunk_index=c.chunk_index
                AND e.embedding_model=%s AND e.embedding_version=%s)""",
            (config["chunking_version"], config["embedding_model"], config["embedding_version"]))
        embedded = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM article_chunks WHERE chunking_version=%s AND eligible",
                    (config["chunking_version"],))
        eligible = cur.fetchone()[0]
    conn.commit()
    return {"eligible": eligible, "embedded": embedded, "pending": eligible - embedded}
