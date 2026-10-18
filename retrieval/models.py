"""Typed contracts for the bounded RAG workflow."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class SearchQuery(BaseModel):
    id: str = Field(min_length=1, max_length=80)
    query: str = Field(min_length=1, max_length=1000)
    purpose: str = Field(default="", max_length=500)

    @field_validator("id", "query", "purpose")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()


class QueryPlan(BaseModel):
    queries: list[SearchQuery] = Field(min_length=1, max_length=3)


class AgentDecision(BaseModel):
    action: Literal["answer", "search_more", "insufficient"]
    answer: str = ""
    citations: list[str] = Field(default_factory=list)
    reason: str = ""
    missing_aspects: list[str] = Field(default_factory=list, max_length=3)
    queries: list[SearchQuery] = Field(default_factory=list, max_length=3)

    @field_validator("answer", "reason")
    @classmethod
    def strip_decision_text(cls, value: str) -> str:
        return value.strip()


class GroundedAnswer(BaseModel):
    answer: str
    citations: list[str] = Field(default_factory=list)

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

