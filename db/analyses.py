"""Pending analysis selection, batch commits, and streaming JSON export."""

import json
import os
import tempfile
from psycopg2.extras import execute_values
from db.db_handler import get_connection


def identity(config):
    return tuple(config[k] for k in ("chunking_version", "backend", "model", "analysis_version"))


def iter_pending(config, limit=None, retry_errors=False):
    conn = get_connection()
    try:
        with conn.cursor(name="analysis_source") as cur:
            cur.itersize = 30
            cur.execute("""SELECT c.page_id,c.chunk_index,c.chunk_text,m.language,m.title
                FROM article_chunks c LEFT JOIN metadata m ON m.page_id=c.page_id
                LEFT JOIN chunk_analyses a ON a.page_id=c.page_id
                    AND a.chunking_version=c.chunking_version AND a.chunk_index=c.chunk_index
                    AND a.backend=%s AND a.model=%s AND a.analysis_version=%s
                WHERE c.chunking_version=%s AND c.eligible
                    AND (a.status IS NULL OR (%s AND a.status='ERROR'))
                ORDER BY c.page_id,c.chunk_index LIMIT %s""",
                (config["backend"],config["model"],config["analysis_version"],config["chunking_version"],retry_errors,limit))
            for page_id, index, text, language, title in cur:
                yield {"page_id": page_id, "chunk_index": index, "text": text,
                       "language": language or "", "title": title or ""}
    finally:
        conn.close()


def commit_batch(conn, config, batch_id, outcomes):
    if not outcomes:
        return
    rows = [(o["page_id"], config["chunking_version"], o["chunk_index"], config["backend"],
             config["model"], config["analysis_version"], o["status"], o["summary"], o["category"],
             json.dumps(o["tags"], ensure_ascii=False), o["error"], o["attempt_count"], batch_id) for o in outcomes]
    with conn:
        with conn.cursor() as cur:
            execute_values(cur, """INSERT INTO chunk_analyses
                (page_id,chunking_version,chunk_index,backend,model,analysis_version,status,summary,category,tags,error,attempt_count,batch_id)
                VALUES %s ON CONFLICT (page_id,chunking_version,chunk_index,backend,model,analysis_version)
                DO UPDATE SET status=EXCLUDED.status,summary=EXCLUDED.summary,category=EXCLUDED.category,
                    tags=EXCLUDED.tags,error=EXCLUDED.error,
                    attempt_count=chunk_analyses.attempt_count+EXCLUDED.attempt_count,
                    batch_id=EXCLUDED.batch_id,updated_at=CURRENT_TIMESTAMP
                WHERE chunk_analyses.batch_id<>EXCLUDED.batch_id AND chunk_analyses.status='ERROR'""", rows)


def counts(conn, config):
    with conn.cursor() as cur:
        cur.execute("SELECT status,count(*) FROM chunk_analyses WHERE chunking_version=%s AND backend=%s AND model=%s AND analysis_version=%s GROUP BY status", identity(config))
        result = {status.lower(): count for status, count in cur.fetchall()}
        cur.execute("SELECT count(*) FROM article_chunks WHERE chunking_version=%s AND eligible", (config["chunking_version"],))
        eligible = cur.fetchone()[0]
    conn.commit()
    result["pending"] = eligible - sum(result.values())
    return result


def export_json(config, destination):
    destination = os.path.abspath(destination)
    fd, temporary = tempfile.mkstemp(prefix=".analyses-", dir=os.path.dirname(destination), text=True)
    conn = None
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            conn = get_connection()
            with conn.cursor(name="analysis_export") as cur:
                cur.itersize = 100
                cur.execute("""SELECT a.page_id,a.chunk_index,p.url,m.title,m.language,a.model,
                    left(c.chunk_text,120),c.chunk_text,a.status,a.summary,a.category,a.tags,a.error,
                    a.chunking_version,a.analysis_version,a.backend
                    FROM chunk_analyses a JOIN article_chunks c USING(page_id,chunking_version,chunk_index)
                    JOIN pages p ON p.id=a.page_id LEFT JOIN metadata m ON m.page_id=a.page_id
                    WHERE a.chunking_version=%s AND a.backend=%s AND a.model=%s AND a.analysis_version=%s
                    ORDER BY a.page_id,a.chunk_index""", identity(config))
                fields = ('doc_id','chunk_index','source','title','language','model_used',
                          'chunk_text_preview','chunk_text_full','status','summary','category','tags','error',
                          'chunking_version','prompt_version','backend')
                stream.write('[')
                first = True
                for row in cur:
                    if not first:
                        stream.write(',\n')
                    json.dump(dict(zip(fields,row)), stream, ensure_ascii=False)
                    first = False
                stream.write(']\n')
        os.replace(temporary, destination)
    finally:
        if conn is not None:
            conn.close()
        if os.path.exists(temporary):
            os.unlink(temporary)
