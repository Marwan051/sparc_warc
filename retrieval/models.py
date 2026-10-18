"""Typed contracts for the bounded RAG workflow."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator


# Groq strict-mode structured output requires every field to be present and
# objects to forbid additional properties. Keep the LLM-facing schemas free of
# defaults and length constraints (enforced in code instead) so constrained
# decoding can guarantee the shape.
_STRICT = ConfigDict(extra="forbid")


class SearchQuery(BaseModel):
    model_config = _STRICT
    id: str
    query: str

    @field_validator("id", "query")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()


class QueryPlan(BaseModel):
    model_config = _STRICT
    queries: list[SearchQuery]


class AgentDecision(BaseModel):
    model_config = _STRICT
    action: Literal["answer", "search_more", "insufficient"]
    answer: str
    citations: list[str]
    reason: str
    queries: list[SearchQuery]

    @field_validator("answer", "reason")
    @classmethod
    def strip_decision_text(cls, value: str) -> str:
        return value.strip()


class GroundedAnswer(BaseModel):
    model_config = _STRICT
    answer: str
    citations: list[str]

    @field_validator("answer")
    @classmethod
    def strip_answer(cls, value: str) -> str:
        return value.strip()


class Source(BaseModel):
    page_id: int
    url: str
    title: str
    publisher: str
    author: str
    language: str
    published_date: str


class Evidence(BaseModel):
    text: str
    chunk_ids: list[str]
    query_ids: list[str]
    reranker_score: float
    similarity: float
    sources: list[Source]


class RagResult(BaseModel):
    question: str
    answer: str
    sufficient: bool
    citations: list[str]
    sources: list[Source]
    queries: list[SearchQuery]
    evidence: list[Evidence]
    retrieval_rounds: int

