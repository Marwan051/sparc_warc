"""Minimal bounded LangChain RAG agent."""

from __future__ import annotations

import os
import re

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from retrieval.evidence import assemble_evidence
from retrieval.models import (
    AgentDecision, Evidence, GroundedAnswer, QueryPlan, RagResult, SearchQuery,
)
from retrieval.store import VectorRetriever


_PLAN_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You plan semantic searches over a multilingual news archive.
Return one search query for a simple question, or two to three self-contained
queries only when separate evidence is needed. Preserve names, dates, places,
and the user's language. Do not answer the question."""),
    ("human", "Original question:\n{question}"),
])

_DECISION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a grounded multilingual news archive assistant. Infer
the intended meaning of informal, dialectal, or grammatically imperfect
questions. Use only the supplied evidence. First check whether any passage
contains a concrete fact that responds to the intended topic. If one does,
return either an answer or a targeted search_more action—never insufficient.

Answer whenever the evidence addresses all or part of the question. If it
supports only one example for a broad or plural request, give that example and
explicitly state that the retrieved archive does not establish a complete list.
Incomplete coverage is not the same as no evidence.

For an answer, obey Required answer language exactly, use at most 180 words, cite
claims inline with chunk IDs such as [p12:c3], and copy the IDs into citations.
If a critical aspect is missing and another search is allowed, return
action='search_more' with one to three targeted queries. When another search is
not allowed, answer with a limitation if any relevant fact exists. Return
action='insufficient' only when every supplied passage is unrelated to the
intended question. Never invent a citation, fact, or source."""),
    ("human", """Original question:
{question}

Required answer language: {answer_language}

Another search is allowed: {retry_allowed}

Evidence:
{evidence}"""),
])

_FINAL_ANSWER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """Your task is to produce the most useful grounded response, not
to demand exhaustive coverage. Infer the meaning of informal, dialectal, or
grammatically imperfect questions and use only the supplied news evidence.

Rules:
1. If any passage contains a concrete fact relevant to the intended question,
   you MUST return a non-empty answer based on that fact.
2. A broad or plural question can be answered with one supported example; state
   clearly that the archive does not establish a complete list.
3. Obey Required answer language exactly and translate the supported facts into
   it. Match the user's dialect when requested.
4. Use at most 180 words. Cite factual claims inline with exact chunk IDs such as
   [p12:c3] and copy those IDs into citations.
5. Return an empty answer only if every passage is unrelated to the intended
   question. Never add outside facts."""),
    ("human", """Original question:
{question}

Required answer language: {answer_language}

Evidence:
{evidence}"""),
])


def _unique_queries(queries: list[SearchQuery],
                    previous: list[SearchQuery] | None = None) -> list[SearchQuery]:
    seen = {item.query.casefold() for item in (previous or [])}
    result = []
    for item in queries:
        key = item.query.casefold()
        if key not in seen:
            seen.add(key)
            result.append(item)
        if len(result) == 3:
            break
    return result


def _answer_language(question: str) -> str:
    if re.search(r"[\u0600-\u06ff]", question):
        return "Arabic; match the user's dialect when possible"
    return "the same language as the original question"


def _format_evidence(evidence: list[Evidence]) -> str:
    if not evidence:
        return "(no matching evidence)"
    blocks = []
    for item in evidence:
        source_text = "; ".join(
            f"{source.title} | {source.publisher} | {source.published_date} | {source.url}"
            for source in item.sources
        )
        blocks.append(
            f"Chunk IDs: {', '.join(item.chunk_ids)}\n"
            f"Matched queries: {', '.join(item.query_ids)}\n"
            f"Cosine similarity: {item.similarity:.6f}\n"
            f"Sources: {source_text}\n"
            f"Text: {item.text}"
        )
    return "\n\n---\n\n".join(blocks)


class RagAgent:
    """Two-round agent: plan, retrieve, answer or make one corrective search."""

    def __init__(self, retriever=None, planner=None, decider=None, finalizer=None):
        self.retriever = retriever or VectorRetriever()
        injected_decider = decider is not None
        if planner is None or decider is None:
            api_key = os.environ.get("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY is required")
            llm = ChatGroq(
                model=os.environ.get("RAG_MODEL", "qwen/qwen3.8-27b"),
                temperature=0,
                max_tokens=2400,
                max_retries=2,
                api_key=api_key,
                reasoning_effort="none",
            )
            planner = planner or (
                _PLAN_PROMPT | llm.with_structured_output(QueryPlan, method="json_schema")
            )
            decider = decider or (
                _DECISION_PROMPT | llm.with_structured_output(AgentDecision, method="json_schema")
            )
            finalizer = finalizer or (
                _FINAL_ANSWER_PROMPT
                | llm.with_structured_output(GroundedAnswer, method="json_schema")
            )
        elif finalizer is None and injected_decider:
            # Test/custom chains can handle both decision shapes themselves.
            finalizer = decider
        self.planner = planner
        self.decider = decider
        self.finalizer = finalizer

    async def answer(self, question: str) -> RagResult:
        question = question.strip()
        if not question:
            raise ValueError("question must not be empty")

        plan = await self.planner.ainvoke({"question": question})
        queries = _unique_queries(plan.queries)
        if not queries:
            raise ValueError("query planner returned no usable queries")

        all_hits = await self.retriever.retrieve(queries)
        evidence = assemble_evidence(all_hits)
        rounds = 1
        decision = await self._decide(question, evidence, retry_allowed=True)

        if decision.action == "search_more":
            follow_up = _unique_queries(decision.queries, queries)
            if follow_up:
                queries.extend(follow_up)
                all_hits.extend(await self.retriever.retrieve(follow_up))
                evidence = assemble_evidence(all_hits)
                rounds = 2
                decision = await self._finalize(question, evidence)
        elif decision.action == "insufficient" and evidence:
            decision = await self._finalize(question, evidence)

        return self._result(question, queries, evidence, rounds, decision)

    async def _decide(self, question: str, evidence: list[Evidence], retry_allowed: bool):
        return await self.decider.ainvoke({
            "question": question,
            "answer_language": _answer_language(question),
            "retry_allowed": "yes" if retry_allowed else "no",
            "evidence": _format_evidence(evidence),
        })

    async def _finalize(self, question: str, evidence: list[Evidence]) -> AgentDecision:
        final = await self.finalizer.ainvoke({
            "question": question,
            "answer_language": _answer_language(question),
            "evidence": _format_evidence(evidence),
        })
        if isinstance(final, AgentDecision):
            return final
        return AgentDecision(
            action="answer" if final.answer else "insufficient",
            answer=final.answer,
            citations=final.citations,
        )

    @staticmethod
    def _result(question, queries, evidence, rounds, decision) -> RagResult:
        available = {chunk_id for item in evidence for chunk_id in item.chunk_ids}
        inline_citations = re.findall(r"p[0-9]+:c[0-9]+", decision.answer)
        valid_citations = list(dict.fromkeys(
            citation for citation in [*decision.citations, *inline_citations]
            if citation in available
        ))
        sufficient = decision.action == "answer" and bool(decision.answer) and bool(valid_citations)
        if sufficient:
            answer = decision.answer
        else:
            reason = decision.reason or "The retrieved archive evidence does not support a reliable answer."
            answer = f"Insufficient evidence: {reason}"

        cited_pages = {int(item.split(":", 1)[0][1:]) for item in valid_citations}
        sources = []
        seen_sources = set()
        for item in evidence:
            if not cited_pages.intersection(source.page_id for source in item.sources):
                continue
            for source in item.sources:
                key = (source.page_id, source.url)
                if source.page_id in cited_pages and key not in seen_sources:
                    seen_sources.add(key)
                    sources.append(source)
        return RagResult(
            question=question,
            answer=answer,
            sufficient=sufficient,
            citations=valid_citations,
            sources=sources,
            queries=queries,
            evidence=evidence,
            retrieval_rounds=rounds,
        )


async def answer(question: str) -> RagResult:
    """Answer one question with the default environment-configured agent."""
    return await RagAgent().answer(question)

