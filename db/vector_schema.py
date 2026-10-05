"""Version-four pgvector storage for embeddings of persisted article chunks."""

DDL = """
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS chunk_embeddings (
    page_id INT NOT NULL,
    chunking_version TEXT NOT NULL,
    chunk_index INT NOT NULL,
    embedding_model TEXT NOT NULL,
    text_hash TEXT NOT NULL,
    embedding VECTOR(1024) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (page_id, chunking_version, chunk_index, embedding_model),
    FOREIGN KEY (page_id, chunking_version, chunk_index)
        REFERENCES article_chunks(page_id, chunking_version, chunk_index)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_chunk_embeddings_hnsw
    ON chunk_embeddings USING hnsw (embedding vector_ip_ops);
"""
