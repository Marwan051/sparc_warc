"""Additive version-three DDL; no optional model dependencies."""

DDL = """
CREATE TABLE IF NOT EXISTS chunk_materializations (
    page_id INT NOT NULL REFERENCES pages(id) ON DELETE CASCADE,
    chunking_version TEXT NOT NULL,
    source_hash TEXT NOT NULL,
    chunk_count INT NOT NULL CHECK (chunk_count >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (page_id, chunking_version)
);
CREATE TABLE IF NOT EXISTS article_chunks (
    page_id INT NOT NULL REFERENCES pages(id) ON DELETE CASCADE,
    chunking_version TEXT NOT NULL,
    chunk_index INT NOT NULL CHECK (chunk_index >= 0),
    chunk_text TEXT NOT NULL,
    text_hash TEXT NOT NULL,
    eligible BOOLEAN NOT NULL,
    filter_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (page_id, chunking_version, chunk_index),
    CHECK (eligible = (filter_reason IS NULL))
);
CREATE INDEX IF NOT EXISTS idx_article_chunks_pending ON article_chunks
    (chunking_version, page_id, chunk_index) WHERE eligible;
CREATE TABLE IF NOT EXISTS chunk_analyses (
    page_id INT NOT NULL,
    chunking_version TEXT NOT NULL,
    chunk_index INT NOT NULL,
    backend TEXT NOT NULL,
    model TEXT NOT NULL,
    analysis_version TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('SUCCESS','NOISE','ERROR')),
    summary TEXT,
    category TEXT,
    tags JSONB NOT NULL DEFAULT '[]'::jsonb CHECK (jsonb_typeof(tags) = 'array'),
    error TEXT,
    attempt_count INT NOT NULL CHECK (attempt_count >= 0),
    batch_id TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (page_id, chunking_version, chunk_index, backend, model, analysis_version),
    FOREIGN KEY (page_id, chunking_version, chunk_index)
        REFERENCES article_chunks(page_id, chunking_version, chunk_index) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_chunk_analyses_status ON chunk_analyses
    (chunking_version, backend, model, analysis_version, status);
"""
