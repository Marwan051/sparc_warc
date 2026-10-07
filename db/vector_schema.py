"""Versioned pgvector storage for embeddings of persisted article chunks."""

DDL = """
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS chunk_embeddings (
    page_id INT NOT NULL,
    chunking_version TEXT NOT NULL,
    chunk_index INT NOT NULL,
    embedding_model TEXT NOT NULL,
    embedding_version TEXT NOT NULL,
    text_hash TEXT NOT NULL,
    embedding VECTOR(1024) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (page_id, chunking_version, chunk_index, embedding_model, embedding_version),
    FOREIGN KEY (page_id, chunking_version, chunk_index)
        REFERENCES article_chunks(page_id, chunking_version, chunk_index)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_chunk_embeddings_hnsw
    ON chunk_embeddings USING hnsw (embedding vector_ip_ops);
"""

# Upgrade databases that already applied schema v4. Existing vectors have no
# reproducible model configuration, so preserve them under an explicit legacy ID.
UPGRADE_V5 = """
ALTER TABLE chunk_embeddings ADD COLUMN IF NOT EXISTS embedding_version TEXT NOT NULL DEFAULT 'legacy-v0';
ALTER TABLE chunk_embeddings DROP CONSTRAINT IF EXISTS chunk_embeddings_pkey;
ALTER TABLE chunk_embeddings ADD CONSTRAINT chunk_embeddings_pkey
    PRIMARY KEY (page_id, chunking_version, chunk_index, embedding_model, embedding_version);
"""
