"""Minimal bounded LangChain RAG agent."""

from __future__ import annotations

import re

from langchain_core.prompts import ChatPromptTemplate

from retrieval.evidence import assemble_evidence
from retrieval.llm import (
    build_chat_model, resolve_model, resolve_provider, retryable_errors,
    structured_output_kwargs,
)
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
    ("system", """LANGUAGE RULE (highest priority): The evidence may be in a
different language than the question. Always write the entire answer in the
language of the Original question, translating facts as needed. Never reply in
the evidence's language unless it matches the question's language.

You are a grounded multilingual news archive assistant. Infer
the intended meaning of informal, dialectal, or grammatically imperfect
questions. Use only the supplied evidence. First check whether any passage
contains a concrete fact that responds to the intended topic. If one does,
return either an answer or a targeted search_more action—never insufficient.

Answer whenever the evidence addresses all or part of the question. If it
supports only one example for a broad or plural request, give that example and
explicitly state that the retrieved archive does not establish a complete list.
Incomplete coverage is not the same as no evidence.

For an answer, write it in the required answer language, use at most 180 words,
cite claims inline with chunk IDs such as [p12:c3], and copy the IDs into
citations. If a critical aspect is missing and another search is allowed, return
action='search_more' with one to three targeted queries. When another search is
not allowed, answer with a limitation if any relevant fact exists. Return
action='insufficient' only when every supplied passage is unrelated to the
intended question. Never invent a citation, fact, or source."""),
    ("human", """Original question:
{question}

Required answer language: {answer_language}

Another search is allowed: {retry_allowed}

Evidence:
{evidence}

Reminder: write your entire answer in the language of the Original question,
even when the evidence is in a different language."""),
])

_FINAL_ANSWER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """LANGUAGE RULE (highest priority): The evidence may be in a
different language than the question. Always write the entire answer in the
language of the Original question, translating facts as needed. Never reply in
the evidence's language unless it matches the question's language.

Your task is to produce the most useful grounded response, not
to demand exhaustive coverage. Infer the meaning of informal, dialectal, or
grammatically imperfect questions and use only the supplied news evidence.

Rules:
1. If any passage contains a concrete fact relevant to the intended question,
   you MUST return a non-empty answer based on that fact.
2. A broad or plural question can be answered with one supported example; state
   clearly that the archive does not establish a complete list.
3. Write the answer in the required answer language and translate the supported
   facts into it. Match the user's dialect when requested.
4. Use at most 180 words. Cite factual claims inline with exact chunk IDs such as
   [p12:c3] and copy those IDs into citations.
5. Return an empty answer only if every passage is unrelated to the intended
   question. Never add outside facts."""),
    ("human", """Original question:
{question}

Required answer language: {answer_language}

Evidence:
{evidence}

Reminder: write your entire answer in the language of the Original question,
even when the evidence is in a different language."""),
])


def _unique_queries(queries: list[SearchQuery],
                    previous: list[SearchQuery] | None = None) -> list[SearchQuery]:
    previous = previous or []
    seen = {item.query.casefold() for item in previous}
    used_ids = {item.id for item in previous}
    result = []
    counter = 1
    for item in queries:
        key = item.query.casefold()
        if not key or key in seen:
            continue
        seen.add(key)
        while f"q{counter}" in used_ids:
            counter += 1
        query_id = f"q{counter}"
        used_ids.add(query_id)
        counter += 1
        result.append(item.model_copy(update={"id": query_id}))
        if len(result) == 3:
            break
    return result


async def _structured_invoke(chain, payload: dict, attempts: int = 2):
    """Retry once when a provider fails to produce valid structured output."""
    retryable = retryable_errors()
    last_error: Exception | None = None
    for _ in range(attempts):
        try:
            return await chain.ainvoke(payload)
        except retryable as error:
            last_error = error
    assert last_error is not None
    raise last_error


_ANSWER_LANGUAGE = (
    "the language of the Original question. Detect it from the question text alone, "
    "never from the evidence. If the question is in a dialect, match that dialect. "
    "Translate evidence facts as needed so the entire answer is in that language"
)


def _answer_language(question: str) -> str:
    # The model reliably knows the question's language; this directive only forces
    # it to key off the question instead of the (possibly different) evidence.
    return _ANSWER_LANGUAGE


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
            f"Reranker relevance: {item.reranker_score:.6f}\n"
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
            provider = resolve_provider()
            model = resolve_model(provider)
            llm = build_chat_model(provider, model)
            structured = structured_output_kwargs(provider)
            planner = planner or (
                _PLAN_PROMPT | llm.with_structured_output(QueryPlan, **structured)
            )
            decider = decider or (
                _DECISION_PROMPT | llm.with_structured_output(AgentDecision, **structured)
            )
            finalizer = finalizer or (
                _FINAL_ANSWER_PROMPT | llm.with_structured_output(GroundedAnswer, **structured)
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

        plan = await _structured_invoke(self.planner, {"question": question})
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
        return await _structured_invoke(self.decider, {
            "question": question,
            "answer_language": _answer_language(question),
            "retry_allowed": "yes" if retry_allowed else "no",
            "evidence": _format_evidence(evidence),
        })

    async def _finalize(self, question: str, evidence: list[Evidence]) -> AgentDecision:
        final = await _structured_invoke(self.finalizer, {
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
            reason="",
            queries=[],
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

