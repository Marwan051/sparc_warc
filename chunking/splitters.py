"""Split documents incrementally while retaining article metadata."""

from typing import Iterable, Iterator, List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from chunking import CHUNKING_VERSION


def iter_document_chunks(documents: Iterable[Document], chunk_size: int = 800,
                         chunk_overlap: int = 100) -> Iterator[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""],
    )
    for document in documents:
        for index, chunk in enumerate(splitter.split_documents([document])):
            chunk.metadata = dict(chunk.metadata, chunk_index=index)
            yield chunk


def split_documents_into_chunks(documents: List[Document], chunk_size: int = 800,
                                chunk_overlap: int = 100) -> List[Document]:
    return list(iter_document_chunks(documents, chunk_size, chunk_overlap))
