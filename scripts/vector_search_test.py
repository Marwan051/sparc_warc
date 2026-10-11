"""Test vector search: embed a query string and fetch top-k chunks from pgvector.

Run with the embedding env (has onnxruntime + pgvector):
    .venv-embedding-onnx/bin/python scripts/vector_search_test.py "your query here" --top-k 5
    .venv-embedding-onnx/bin/python scripts/vector_search_test.py "query" -k 10 --chunking-version v1
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pgvector.psycopg2 import register_vector

from db.db_handler import get_connection
from embeddings.embeddings import generate_embeddings


def resolve_config(conn, chunking_version, embedding_model, embedding_version):
    """Default to the most populated (chunking_version, model, version) combo."""
    if chunking_version and embedding_model and embedding_version:
        return chunking_version, embedding_model, embedding_version
    with conn.cursor() as cur:
        cur.execute(
            """SELECT chunking_version, embedding_model, embedding_version, count(*)
               FROM chunk_embeddings
               GROUP BY 1, 2, 3 ORDER BY count(*) DESC LIMIT 5"""
        )
        combos = cur.fetchall()
    if not combos:
        raise RuntimeError("chunk_embeddings is empty - no vectors to search")
    if chunking_version or embedding_model or embedding_version:
        match = [
            c for c in combos
            if (not chunking_version or c[0] == chunking_version)
            and (not embedding_model or c[1] == embedding_model)
            and (not embedding_version or c[2] == embedding_version)
        ]
        if not match:
            raise RuntimeError(f"no vectors match filters; available: {combos}")
        chosen = match[0]
    else:
        chosen = combos[0]
        if len(combos) > 1:
            print(f"Multiple vector configs found, using largest: {chosen[:3]}")
    return chosen[0], chosen[1], chosen[2]


def search(query: str, top_k: int, chunking_version=None, embedding_model=None,
           embedding_version=None):
    query_vec = generate_embeddings([query])[0]
    conn = get_connection()
    try:
        register_vector(conn)
        cv, em, ev = resolve_config(conn, chunking_version, embedding_model, embedding_version)
        with conn.cursor() as cur:
            cur.execute(
                """SELECT e.page_id, e.chunk_index, c.chunk_text, p.url,
                          m.title, e.embedding <=> %s::vector AS distance
                   FROM chunk_embeddings e
                   JOIN article_chunks c USING (page_id, chunking_version, chunk_index)
                   JOIN pages p ON p.id = e.page_id
                   LEFT JOIN metadata m ON m.page_id = e.page_id
                   WHERE e.chunking_version = %s
                     AND e.embedding_model = %s
                     AND e.embedding_version = %s
                   ORDER BY e.embedding <=> %s::vector
                   LIMIT %s""",
                (query_vec, cv, em, ev, query_vec, top_k),
            )
            rows = cur.fetchall()
        conn.rollback()
        return rows, (cv, em, ev)
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="Top-k vector search test")
    parser.add_argument("query", help="query string to embed and search")
    parser.add_argument("-k", "--top-k", type=int, default=5, help="number of results (default: 5)")
    parser.add_argument("--chunking-version", default=None)
    parser.add_argument("--embedding-model", default=None)
    parser.add_argument("--embedding-version", default=None)
    args = parser.parse_args()

    results, (cv, em, ev) = search(
        args.query, args.top_k, args.chunking_version,
        args.embedding_model, args.embedding_version,
    )
    print(f"Query: {args.query!r}")
    print(f"Config: chunking_version={cv} embedding_model={em} embedding_version={ev}")
    print(f"Top {len(results)} results:\n")
    for rank, (page_id, chunk_index, text, url, title, distance) in enumerate(results, 1):
        similarity = 1.0 - float(distance)
        snippet = text[:500].replace("\n", " ")
        print(f"[{rank}] page_id={page_id} chunk={chunk_index} "
              f"cosine_sim={similarity:.4f} distance={float(distance):.4f}")
        print(f"     title={title} url={url}")
        print(f"     {snippet}{'...' if len(text) > 500 else ''}\n")
    if not results:
        print("No results found.")


if __name__ == "__main__":
    main()
