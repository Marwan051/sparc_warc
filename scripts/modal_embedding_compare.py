"""Compare Modal-hosted BGE-M3 vectors with vectors already stored in PostgreSQL.

Read-only: this script never writes to the database.

Example:

    python scripts/modal_embedding_compare.py \
        --endpoint-url https://<workspace>--warc-embedding-parity-web.modal.run \
        --languages en,fr,ar --per-language 2
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - only for a lean environment
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv(PROJECT_ROOT / ".env")

# The project's normal configuration uses libpq PG* variables, while this
# checkout's .env uses POSTGRES_* aliases. Bridge them when needed.
for source, target in (
    ("POSTGRES_HOST", "PGHOST"),
    ("POSTGRES_PORT", "PGPORT"),
    ("POSTGRES_DB", "PGDATABASE"),
    ("POSTGRES_USER", "PGUSER"),
    ("POSTGRES_PASSWORD", "PGPASSWORD"),
):
    if not os.environ.get(target) and os.environ.get(source):
        os.environ[target] = os.environ[source]

DEFAULT_MODEL = "BAAI/bge-m3-int8"
CHUNK_QUERY = """
WITH ranked AS (
    SELECT
        e.page_id,
        e.chunk_index,
        e.text_hash,
        c.chunk_text,
        e.embedding,
        COALESCE(m.language, 'unknown') AS language,
        row_number() OVER (
            PARTITION BY COALESCE(m.language, 'unknown')
            ORDER BY e.page_id, e.chunk_index
        ) AS rn
    FROM chunk_embeddings AS e
    JOIN article_chunks AS c
      ON c.page_id = e.page_id
     AND c.chunking_version = e.chunking_version
     AND c.chunk_index = e.chunk_index
    LEFT JOIN metadata AS m ON m.page_id = e.page_id
    WHERE e.embedding_model = %s
      AND e.embedding_version = %s
      AND c.eligible
      AND COALESCE(m.language, 'unknown') = ANY(%s)
)
SELECT page_id, chunk_index, text_hash, chunk_text, embedding, language
FROM ranked
WHERE rn <= %s
ORDER BY language, page_id, chunk_index
"""


def _as_vector(value) -> np.ndarray:
    # pgvector.psycopg2 returns either a numpy array or a Vector wrapper,
    # depending on the installed pgvector version.
    if hasattr(value, "to_numpy"):
        value = value.to_numpy()
    return np.asarray(value, dtype=np.float32)


def _rows_to_vectors(rows) -> np.ndarray:
    return np.asarray([_as_vector(row[4]) for row in rows], dtype=np.float32)


def _cosine(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    left_norm = np.linalg.norm(left, axis=1)
    right_norm = np.linalg.norm(right, axis=1)
    return np.sum(left * right, axis=1) / np.maximum(left_norm * right_norm, 1e-12)


def _resolve_version(conn, model: str, explicit: str | None) -> str:
    if explicit:
        return explicit
    with conn.cursor() as cur:
        cur.execute(
            "SELECT embedding_version, count(*) FROM chunk_embeddings "
            "WHERE embedding_model=%s GROUP BY embedding_version ORDER BY count(*) DESC LIMIT 2",
            (model,),
        )
        rows = cur.fetchall()
    if not rows:
        raise SystemExit(f"no stored embeddings for model {model!r}")
    if len(rows) > 1:
        print(
            f"multiple embedding versions found for {model!r}; using the largest "
            f"({rows[0][0]!r}, {rows[0][1]} rows). Pass --embedding-version to override."
        )
    return rows[0][0]


def _fetch_chunks(conn, model: str, version: str, languages: list[str], per_language: int, limit: int):
    from pgvector.psycopg2 import register_vector

    register_vector(conn)
    with conn.cursor() as cur:
        cur.execute(CHUNK_QUERY, (model, version, languages, per_language))
        rows = cur.fetchall()
    if not rows:
        raise SystemExit(
            "no eligible embedded chunks matched the requested languages; "
            "check --embedding-model / --embedding-version / --languages"
        )
    return rows[:limit]


def _endpoint_url(base: str) -> str:
    url = base.rstrip("/")
    if url.endswith("/v1/embeddings"):
        return url
    if url.endswith("/v1"):
        return url + "/embeddings"
    return url + "/v1/embeddings"


def _call_modal(endpoint: str, token: str | None, model: str, texts: list[str], timeout: float):
    import httpx

    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    payload = {"model": model, "input": texts, "encoding_format": "float"}
    url = _endpoint_url(endpoint)
    last_error = None
    with httpx.Client(timeout=timeout) as client:
        for attempt in range(6):
            try:
                response = client.post(url, headers=headers, json=payload)
            except httpx.HTTPError as error:
                last_error = f"{type(error).__name__}: {error}"
            else:
                if response.status_code in (429, 500, 502, 503, 504):
                    last_error = f"HTTP {response.status_code}: {response.text[:300]}"
                elif response.status_code >= 400:
                    raise RuntimeError(
                        f"Modal endpoint returned HTTP {response.status_code}: {response.text[:2000]}"
                    )
                else:
                    data = response.json()
                    items = sorted(data["data"], key=lambda item: item["index"])
                    if len(items) != len(texts):
                        raise RuntimeError(
                            f"endpoint returned {len(items)} vectors for {len(texts)} texts"
                        )
                    vectors = np.asarray(
                        [item["embedding"] for item in items], dtype=np.float32
                    )
                    return vectors, data
            delay = min(2 ** attempt, 20)
            print(f"  request failed ({last_error}); retrying in {delay}s ...", flush=True)
            time.sleep(delay)
    raise RuntimeError(f"Modal endpoint failed after retries: {last_error}")


def _local_vectors(texts: list[str]) -> np.ndarray:
    configured = os.environ.get("EMBEDDING_MODEL_DIR")
    if not configured or not Path(configured).is_absolute():
        os.environ["EMBEDDING_MODEL_DIR"] = str(PROJECT_ROOT / ".models" / "bge-m3-int8")
    os.environ["EMBEDDING_MAX_LENGTH"] = "256"
    os.environ["EMBEDDING_BATCH_SIZE"] = "1"
    os.environ["EMBEDDING_INTRA_OP_THREADS"] = "1"

    from embeddings.embeddings import generate_embeddings

    return np.asarray(generate_embeddings(texts), dtype=np.float32)


def _pipeline_check(rows, modal_vectors: np.ndarray) -> None:
    from unittest.mock import patch

    from embeddings.pipeline import process_batch

    cache = {row[3]: vector for row, vector in zip(rows, modal_vectors)}

    def fake_embedder(texts):
        return np.asarray([cache[text] for text in texts], dtype=np.float32)

    items = [
        {
            "page_id": row[0],
            "chunk_index": row[1],
            "text": row[3],
            "text_hash": row[2],
        }
        for row in rows
    ]
    task = {"items": items, "max_length": 256, "result_bytes": 1024 * 1024}
    with patch("embeddings.generate_embeddings", fake_embedder):
        result = process_batch(task)
    if len(result["rows"]) != len(items):
        raise RuntimeError("normal embedding pipeline did not preserve the input row count")


def _validate_vectors(vectors: np.ndarray, count: int) -> list[str]:
    problems = []
    if vectors.shape != (count, 1024):
        problems.append(f"shape is {vectors.shape}, expected {(count, 1024)}")
    if not np.all(np.isfinite(vectors)):
        problems.append("contains non-finite values")
    norms = np.linalg.norm(vectors, axis=1)
    if not np.allclose(norms, 1.0, atol=1e-3):
        problems.append(f"not L2-normalized (norms {norms.min():.6f}..{norms.max():.6f})")
    return problems


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--endpoint-url", required=True)
    parser.add_argument("--token", default=os.environ.get("MODAL_PROXY_TOKEN"))
    parser.add_argument("--model", default=os.environ.get("MODAL_EMBEDDING_MODEL", "bge-m3-int8"))
    parser.add_argument("--embedding-model", default=DEFAULT_MODEL)
    parser.add_argument("--embedding-version", default=os.environ.get("EMBEDDING_VERSION"))
    parser.add_argument("--languages", default="en,fr,ar")
    parser.add_argument("--per-language", type=int, default=2)
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--threshold", type=float, default=0.999)
    parser.add_argument("--timeout", type=float, default=300.0)
    parser.add_argument("--no-local-baseline", action="store_true")
    parser.add_argument("--no-pipeline-check", action="store_true")
    args = parser.parse_args(argv)

    languages = [item.strip() for item in args.languages.split(",") if item.strip()]
    if not languages:
        parser.error("--languages must contain at least one language code")

    from db.db_handler import get_connection

    conn = get_connection()
    try:
        version = _resolve_version(conn, args.embedding_model, args.embedding_version)
        rows = _fetch_chunks(
            conn, args.embedding_model, version, languages, args.per_language, args.limit
        )
    finally:
        conn.rollback()
        conn.close()

    texts = [row[3] for row in rows]
    stored = _rows_to_vectors(rows)

    print(f"stored model:   {args.embedding_model}")
    print(f"stored version: {version}")
    print(f"chunks:         {len(rows)} ({', '.join(sorted({row[5] for row in rows}))})")
    print(f"endpoint:       {_endpoint_url(args.endpoint_url)}")
    print(f"auth:           {'proxy token' if args.token else 'none'}")
    print()

    modal_vectors, response = _call_modal(
        args.endpoint_url, args.token, args.model, texts, args.timeout
    )
    print(f"endpoint model: {response.get('model')!r}")
    print(f"usage:          {response.get('usage')}")
    print()

    problems = _validate_vectors(modal_vectors, len(texts))
    modal_cos = _cosine(modal_vectors, stored)
    modal_max_abs = np.max(np.abs(modal_vectors - stored), axis=1)

    local_cos = None
    if not args.no_local_baseline:
        print("running local ONNX baseline ...", flush=True)
        local_vectors = _local_vectors(texts)
        local_problems = _validate_vectors(local_vectors, len(texts))
        problems.extend(f"local: {problem}" for problem in local_problems)
        local_cos = _cosine(local_vectors, stored)

    print()
    header = (
        f"{'page':>7} {'chunk':>5} {'lang':>4} "
        f"{'cos(modal,stored)':>18} {'max_abs':>10} {'cos(local,stored)':>18}"
    )
    print(header)
    print("-" * len(header))
    for index, row in enumerate(rows):
        local_text = f"{local_cos[index]:.8f}" if local_cos is not None else "n/a"
        print(
            f"{row[0]:>7} {row[1]:>5} {row[5]:>4} "
            f"{modal_cos[index]:>18.8f} {modal_max_abs[index]:>10.2e} {local_text:>18}"
        )

    print()
    print(
        f"cos(modal, stored): mean={modal_cos.mean():.8f} "
        f"min={modal_cos.min():.8f} max={modal_cos.max():.8f}"
    )
    if local_cos is not None:
        print(
            f"cos(local, stored): mean={local_cos.mean():.8f} "
            f"min={local_cos.min():.8f} max={local_cos.max():.8f}"
        )
    print(f"modal norms:        {np.linalg.norm(modal_vectors, axis=1).min():.8f} "
          f".. {np.linalg.norm(modal_vectors, axis=1).max():.8f}")
    print(f"max abs difference: {modal_max_abs.max():.3e}")

    if not args.no_pipeline_check:
        try:
            _pipeline_check(rows, modal_vectors)
        except Exception as error:
            problems.append(f"pipeline check failed: {type(error).__name__}: {error}")
        else:
            print("pipeline contract:  OK (process_batch accepted the Modal vectors)")

    if not args.no_local_baseline:
        try:
            from embeddings.embeddings import model_version

            local_version = model_version(256)
        except Exception as error:
            print(f"local version check: skipped ({type(error).__name__}: {error})")
        else:
            if local_version == version:
                print(f"local version match: OK ({local_version})")
            else:
                problems.append(
                    f"local model_version(256)={local_version!r} does not match stored version {version!r}"
                )

    failures = [index for index, value in enumerate(modal_cos) if value < args.threshold]
    if failures:
        problems.append(
            f"{len(failures)} chunk(s) below cosine threshold {args.threshold}: "
            f"{', '.join(f'p{rows[i][0]}:c{rows[i][1]}={modal_cos[i]:.6f}' for i in failures)}"
        )

    print()
    if problems:
        print("FAIL")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print(f"PASS (all cosine values >= {args.threshold})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
