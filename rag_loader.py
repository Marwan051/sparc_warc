import sys
import os
from typing import Iterable, Iterator, List, Optional
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from db.db_handler import get_connection

FETCH_BATCH_SIZE = int(os.environ.get("RAG_FETCH_BATCH_SIZE", "1000"))

_JOIN_QUERY = """
SELECT p.id AS doc_id, c.cleaned_text AS text, p.url AS url,
       m.title AS title, w.domain AS source_domain, a.name AS author,
       m.language AS lang, m.arabic_dialect AS arabic_dialect,
       m.published_date AS pub_date, p.warc_record_id AS warc_record_id
FROM pages AS p
LEFT JOIN websites AS w ON w.id = p.website_id
LEFT JOIN authors AS a ON a.id = p.author_id
LEFT JOIN metadata AS m ON m.page_id = p.id
LEFT JOIN content AS c ON c.page_id = p.id
WHERE c.cleaned_text IS NOT NULL AND length(c.cleaned_text) > 0
ORDER BY p.id;
"""


def _to_document(row) -> Document:
    (doc_id, text, url, title, source_domain, author, lang,
     arabic_dialect, pub_date, warc_record_id) = row
    return Document(
        page_content=text,
        metadata={
            "doc_id": doc_id,
            "source": url,
            "title": title or "N/A",
            "publisher": source_domain or "Unknown",
            "author": author or source_domain or "Unknown",
            "domain": source_domain or "",
            "language": lang or "",
            "arabic_dialect": arabic_dialect or "N/A",
            "published_date": pub_date or "N/A",
            "warc_record_id": warc_record_id or "",
        },
    )


def iter_documents(limit: Optional[int] = None) -> Iterator[Document]:
    """Stream Documents from a server-side cursor without corpus accumulation."""
    if limit is not None and limit < 1:
        raise ValueError("limit must be positive")
    if FETCH_BATCH_SIZE < 1:
        raise ValueError("RAG_FETCH_BATCH_SIZE must be positive")
    conn = get_connection()
    try:
        cur = conn.cursor(name="rag_loader")
        try:
            cur.itersize = FETCH_BATCH_SIZE
            query = _JOIN_QUERY
            params = ()
            if limit is not None:
                query = _JOIN_QUERY.rstrip().rstrip(";") + " LIMIT %s;"
                params = (limit,)
            cur.execute(query, params)
            for row in cur:
                yield _to_document(row)
        finally:
            cur.close()
    finally:
        conn.close()


def load_documents_distributed(limit: Optional[int] = None) -> List[Document]:
    """Compatibility eager loader with a required safety limit."""
    if limit is None:
        raw = os.environ.get("RAG_DOCUMENT_LIMIT", "").strip()
        limit = int(raw) if raw else None
    if limit is None or limit < 1:
        raise ValueError("set RAG_DOCUMENT_LIMIT or pass limit= to use the eager loader")
    return list(iter_documents(limit=limit))


def iter_document_chunks(
    documents: Iterable[Document], chunk_size: int = 800, chunk_overlap: int = 100
) -> Iterator[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""],
    )
    for document in documents:
        yield from splitter.split_documents([document])


def split_documents_into_chunks(documents: List[Document], chunk_size: int = 800, chunk_overlap: int = 100) -> List[Document]:
    return list(iter_document_chunks(documents, chunk_size, chunk_overlap))
