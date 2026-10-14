"""Exact cosine retrieval over the project's versioned pgvector rows."""

from __future__ import annotations

import asyncio
import os
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

import numpy as np
from pgvector.psycopg2 import register_vector

from chunking import CHUNKING_VERSION
from db.db_handler import get_connection
from embeddings.embeddings import generate_embeddings, model_version
from retrieval.models import SearchQuery, Source
from retrieval.ranking import rerank_query_groups
from retrieval.reranker import OnnxReranker
from jobs.validation import env_int


@dataclass(frozen=True)
class RetrievalConfig:
    chunking_version: str
    embedding_model: str
    embedding_version: str
    top_k: int = 5
    candidate_k:int = 20
    max_concurrent_searches: int = 3

    @classmethod
    def from_environment(cls) -> RetrievalConfig:
        max_length = env_int("EMBEDDING_MAX_LENGTH", 256, minimum=1)
        candidate_k=env_int("RERANKER_CANDIDATE_K", 20, minimum=1)
        if candidate_k < cls.top_k:
            raise ValueError("Number of candidates can not be less than the top candidates to get")
        return cls(
            chunking_version=os.environ.get("CHUNKING_VERSION", CHUNKING_VERSION),
            embedding_model=os.environ.get("EMBEDDING_MODEL", "BAAI/bge-m3-int8"),
            embedding_version=os.environ.get("EMBEDDING_VERSION") or model_version(max_length),
            top_k=env_int("TOP_K", 5, minimum=1),
            max_concurrent_searches=env_int("RAG_DB_CONCURRENCY", 3, minimum=1),
        )


@dataclass
class SearchHit:
    page_id: int 
    chunk_index: int
    text_hash: str
    text: str
    similarity: float
    query_id: str
    source: Source
    reranker_score: float | None = None

    @property
    def chunk_id(self) -> str:
        return f"p{self.page_id}:c{self.chunk_index}"


_SEARCH_SQL = """
SELECT e.page_id, e.chunk_index, e.text_hash, c.chunk_text,
       1 - (e.embedding <=> %s::vector) AS similarity,
       p.url, m.title, w.domain, a.name, m.language, m.published_date
FROM chunk_embeddings AS e
JOIN article_chunks AS c
  USING (page_id, chunking_version, chunk_index)
JOIN pages AS p ON p.id = e.page_id
LEFT JOIN websites AS w ON w.id = p.website_id
LEFT JOIN authors AS a ON a.id = p.author_id
LEFT JOIN metadata AS m ON m.page_id = e.page_id
WHERE e.chunking_version = %s
  AND e.embedding_model = %s
  AND e.embedding_version = %s
  AND c.eligible
ORDER BY e.embedding <=> %s::vector, e.page_id, e.chunk_index
LIMIT %s
"""


class VectorRetriever:
    """Batch query embedding followed by bounded parallel exact searches."""

    def __init__(self, config: RetrievalConfig | None = None,
                 embedder: Callable[[list[str]], np.ndarray] = generate_embeddings,reranker: OnnxReranker | None = None,):
        self.config = config or RetrievalConfig.from_environment()
        self.embedder = embedder
        self.reranker = reranker or OnnxReranker()

    async def retrieve(self, queries: list[SearchQuery]) -> list[SearchHit]:
        if not queries or len(queries) > 3:
            raise ValueError("retrieval requires one to three queries")
        # Own the coordinator thread instead of using asyncio's process-global
        # executor, which gives the CLI deterministic shutdown on Python 3.13.
        with ThreadPoolExecutor(max_workers=1, thread_name_prefix="rag-coordinator") as executor:
            future = executor.submit(self._retrieve_sync, queries)
            while not future.done():
                await asyncio.sleep(0.01)
            groups = future.result()
        return [hit for group in groups for hit in group]
    
    def _retrieve_sync(self, queries: list[SearchQuery]) -> list[list[SearchHit]]:
        vectors = self._embed_queries(queries)
        groups = self._search_queries(queries, vectors)
        return rerank_query_groups(queries, groups, self.reranker, self.config.top_k)

    def _embed_queries(self, queries: list[SearchQuery]) -> np.ndarray:
        vectors = self.embedder([item.query for item in queries])
        if np.asarray(vectors).shape != (len(queries), 1024):
            raise ValueError("query embedder must return one 1024-dimensional vector per query")
        return vectors

    def _search_queries(self, queries: list[SearchQuery], vectors: np.ndarray) -> list[list[SearchHit]]:
        with ThreadPoolExecutor(max_workers=self.config.max_concurrent_searches,
                                 thread_name_prefix="rag-search") as executor:
            futures = [
                 executor.submit(self._search_one, query, np.asarray(vector, dtype=np.float32))
                 for query, vector in zip(queries, vectors)
             ]
        return [future.result() for future in futures]


    def _search_one(self, query: SearchQuery, vector: np.ndarray) -> list[SearchHit]:
        conn = get_connection()
        try:
            register_vector(conn)
            with conn.cursor() as cur:
                cur.execute(_SEARCH_SQL, (
                    vector,
                    self.config.chunking_version,
                    self.config.embedding_model,
                    self.config.embedding_version,
                    vector,
                    self.config.candidate_k,
                ))
                rows = cur.fetchall()
            conn.rollback()
        finally:
            conn.close()

        hits = []
        for row in rows:
            (page_id, chunk_index, text_hash, text, similarity, url, title,
             publisher, author, language, published_date) = row
            hits.append(SearchHit(
                page_id=page_id,
                chunk_index=chunk_index,
                text_hash=text_hash,
                text=text,
                similarity=float(similarity),
                query_id=query.id,
                source=Source(
                    page_id=page_id,
                    url=url or "",
                    title=title or "N/A",
                    publisher=publisher or "Unknown",
                    author=author or publisher or "Unknown",
                    language=language or "",
                    published_date=published_date or "N/A",
                ),
            ))
        return hits

