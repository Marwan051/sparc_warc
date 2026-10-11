import importlib.util
import threading
import time
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import Mock, patch


AVAILABLE = all(importlib.util.find_spec(name) is not None for name in (
    "langchain_core", "langchain_groq", "pgvector", "pydantic", "numpy",
))


@unittest.skipUnless(AVAILABLE, "install requirements/rag-agent.txt for retrieval tests")
class EvidenceTests(unittest.TestCase):
    @staticmethod
    def hit(page, chunk, text, query="q1", score=0.8, url=None):
        from retrieval.models import Source
        from retrieval.store import SearchHit
        return SearchHit(
            page_id=page, chunk_index=chunk, text_hash=f"hash-{page}-{chunk}",
            text=text, similarity=score, query_id=query,
            source=Source(page_id=page, url=url or f"https://example.com/{page}",
                          title=f"Title {page}", publisher="Publisher", author="Author",
                          language="en", published_date="2026-01-01"),
        )

    def test_deduplicates_hits_and_merges_only_retrieved_adjacent_chunks(self):
        from retrieval.evidence import assemble_evidence
        evidence = assemble_evidence([
            self.hit(1, 0, "alpha shared", "q1", 0.7),
            self.hit(1, 0, "alpha shared", "q2", 0.9),
            self.hit(1, 1, "shared beta", "q2", 0.8),
            self.hit(1, 3, "not adjacent", "q1", 0.6),
        ])
        self.assertEqual(len(evidence), 2)
        merged = next(item for item in evidence if item.chunk_ids == ["p1:c0", "p1:c1"])
        self.assertEqual(merged.text, "alpha shared beta")
        self.assertEqual(merged.query_ids, ["q1", "q2"])
        self.assertEqual(merged.similarity, 0.9)

    def test_deduplicates_identical_text_across_articles_and_keeps_sources(self):
        from retrieval.evidence import assemble_evidence
        evidence = assemble_evidence([
            self.hit(1, 2, "same text", url="https://one.example"),
            self.hit(2, 7, "same text", url="https://two.example"),
        ])
        self.assertEqual(len(evidence), 1)
        self.assertEqual(evidence[0].chunk_ids, ["p1:c2", "p2:c7"])
        self.assertEqual(len(evidence[0].sources), 2)

    def test_cli_prints_full_retrieved_evidence(self):
        from retrieval.evidence import assemble_evidence
        from scripts.ask import _print_evidence
        evidence = assemble_evidence([
            self.hit(1, 2, "the complete retrieved chunk", query="comparison", score=0.8123456),
        ])
        output = StringIO()
        with redirect_stdout(output):
            _print_evidence(evidence)
        rendered = output.getvalue()
        self.assertIn("Retrieved evidence:", rendered)
        self.assertIn("chunks=p1:c2", rendered)
        self.assertIn("cosine=0.812346", rendered)
        self.assertIn("queries=comparison", rendered)
        self.assertIn("the complete retrieved chunk", rendered)


@unittest.skipUnless(AVAILABLE, "install requirements/rag-agent.txt for retrieval tests")
class StoreTests(unittest.IsolatedAsyncioTestCase):
    def config(self, concurrency=3):
        from retrieval.store import RetrievalConfig
        return RetrievalConfig("chunks-v1", "model", "model-v1", 5, concurrency)

    def test_search_uses_exact_cosine_and_version_filters(self):
        import numpy as np
        from retrieval.models import SearchQuery
        from retrieval.store import VectorRetriever
        cursor = Mock()
        cursor.__enter__ = Mock(return_value=cursor)
        cursor.__exit__ = Mock(return_value=False)
        cursor.fetchall.return_value = []
        conn = Mock()
        conn.cursor.return_value = cursor
        retriever = VectorRetriever(self.config(), embedder=Mock())
        vector = np.zeros(1024, dtype=np.float32)
        with patch("retrieval.store.get_connection", return_value=conn), \
             patch("retrieval.store.register_vector"):
            self.assertEqual(retriever._search_one(SearchQuery(id="q", query="query"), vector), [])
        sql, params = cursor.execute.call_args.args
        self.assertIn("<=>", sql)
        self.assertIn("c.eligible", sql)
        self.assertEqual(params[1:4], ("chunks-v1", "model", "model-v1"))
        conn.rollback.assert_called_once()
        conn.close.assert_called_once()

    async def test_query_searches_run_concurrently_after_one_embedding_batch(self):
        import numpy as np
        from retrieval.models import SearchQuery
        from retrieval.store import VectorRetriever
        calls = []
        active = 0
        max_active = 0
        lock = threading.Lock()

        def embed(texts):
            calls.append(list(texts))
            return np.zeros((len(texts), 1024), dtype=np.float32)

        retriever = VectorRetriever(self.config(), embedder=embed)

        def search(query, vector):
            nonlocal active, max_active
            with lock:
                active += 1
                max_active = max(max_active, active)
            time.sleep(0.03)
            with lock:
                active -= 1
            return []

        retriever._search_one = search
        queries = [SearchQuery(id=f"q{i}", query=f"query {i}") for i in range(3)]
        await retriever.retrieve(queries)
        self.assertEqual(calls, [["query 0", "query 1", "query 2"]])
        self.assertGreater(max_active, 1)


@unittest.skipUnless(AVAILABLE, "install requirements/rag-agent.txt for retrieval tests")
class AgentTests(unittest.IsolatedAsyncioTestCase):
    class Chain:
        def __init__(self, *responses):
            self.responses = list(responses)
            self.inputs = []

        async def ainvoke(self, values):
            self.inputs.append(values)
            return self.responses.pop(0)

    class Retriever:
        def __init__(self, groups):
            self.groups = list(groups)
            self.queries = []

        async def retrieve(self, queries):
            self.queries.append(queries)
            return self.groups.pop(0)

    @staticmethod
    def hit(query_id="main"):
        return EvidenceTests.hit(3, 4, "supported fact", query_id, 0.91)

    def test_configures_groq_native_json_schema_output(self):
        from langchain_core.runnables import RunnableLambda
        from retrieval.agent import RagAgent
        methods = []

        class Llm:
            def with_structured_output(self, schema, **kwargs):
                methods.append((schema.__name__, kwargs))
                return RunnableLambda(lambda value: value)

        with patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}), \
             patch("retrieval.agent.ChatGroq", return_value=Llm()):
            RagAgent(retriever=Mock())
        self.assertEqual(methods, [
            ("QueryPlan", {"method": "json_schema"}),
            ("AgentDecision", {"method": "json_schema"}),
            ("GroundedAnswer", {"method": "json_schema"}),
        ])

    def test_arabic_questions_require_arabic_answers(self):
        from retrieval.agent import _answer_language
        self.assertEqual(
            _answer_language("إزاي الفلوس بتتنقل بين الدول؟"),
            "Arabic; match the user's dialect when possible",
        )
        self.assertEqual(
            _answer_language("How does money move?"),
            "the same language as the original question",
        )

    async def test_answers_with_valid_citation_in_one_round(self):
        from retrieval.agent import RagAgent
        from retrieval.models import AgentDecision, QueryPlan, SearchQuery
        query = SearchQuery(id="main", query="supported fact")
        planner = self.Chain(QueryPlan(queries=[query]))
        decider = self.Chain(AgentDecision(
            action="answer", answer="The fact is supported [p3:c4].", citations=["p3:c4"]
        ))
        result = await RagAgent(self.Retriever([[self.hit()]]), planner, decider).answer("Question?")
        self.assertTrue(result.sufficient)
        self.assertEqual(result.retrieval_rounds, 1)
        self.assertEqual(result.citations, ["p3:c4"])
        self.assertEqual(len(result.sources), 1)

    async def test_accepts_valid_inline_citation_when_structured_list_is_empty(self):
        from retrieval.agent import RagAgent
        from retrieval.models import AgentDecision, QueryPlan, SearchQuery
        query = SearchQuery(id="main", query="supported fact")
        planner = self.Chain(QueryPlan(queries=[query]))
        decider = self.Chain(AgentDecision(
            action="answer", answer="The fact is supported [p3:c4].", citations=[]
        ))
        result = await RagAgent(self.Retriever([[self.hit()]]), planner, decider).answer("Question?")
        self.assertTrue(result.sufficient)
        self.assertEqual(result.citations, ["p3:c4"])

    async def test_returns_supported_partial_answer_after_follow_up(self):
        from retrieval.agent import RagAgent
        from retrieval.models import AgentDecision, QueryPlan, SearchQuery
        first = SearchQuery(id="first", query="new cross-border payment methods")
        retry = SearchQuery(id="retry", query="other cross-border payment methods")
        planner = self.Chain(QueryPlan(queries=[first]))
        decider = self.Chain(
            AgentDecision(action="search_more", reason="look for other methods", queries=[retry]),
            AgentDecision(
                action="answer",
                answer=("The archive supports stablecoins as one method [p3:c4], "
                        "but does not establish a complete list."),
                citations=["p3:c4"],
            ),
        )
        retriever = self.Retriever([[self.hit("first")], [self.hit("retry")]])
        result = await RagAgent(retriever, planner, decider).answer("What are the new methods?")
        self.assertTrue(result.sufficient)
        self.assertEqual(result.retrieval_rounds, 2)
        self.assertIn("does not establish a complete list", result.answer)

    async def test_initial_insufficient_decision_gets_grounded_final_pass(self):
        from retrieval.agent import RagAgent
        from retrieval.models import AgentDecision, GroundedAnswer, QueryPlan, SearchQuery
        query = SearchQuery(id="main", query="new cross-border payment methods")
        planner = self.Chain(QueryPlan(queries=[query]))
        decider = self.Chain(AgentDecision(action="insufficient"))
        finalizer = self.Chain(GroundedAnswer(
            answer="Stablecoins are one supported method [p3:c4].",
            citations=["p3:c4"],
        ))
        result = await RagAgent(
            self.Retriever([[self.hit()]]), planner, decider, finalizer
        ).answer("What are the new methods?")
        self.assertTrue(result.sufficient)
        self.assertEqual(result.retrieval_rounds, 1)
        self.assertIn("Stablecoins", result.answer)

    async def test_allows_only_one_targeted_follow_up_round(self):
        from retrieval.agent import RagAgent
        from retrieval.models import AgentDecision, QueryPlan, SearchQuery
        first = SearchQuery(id="first", query="first query")
        retry = SearchQuery(id="retry", query="missing evidence")
        planner = self.Chain(QueryPlan(queries=[first]))
        decider = self.Chain(
            AgentDecision(action="search_more", reason="missing", queries=[retry]),
            AgentDecision(action="search_more", reason="still missing", queries=[
                SearchQuery(id="third", query="forbidden third round")
            ]),
        )
        retriever = self.Retriever([[self.hit("first")], [self.hit("retry")]])
        result = await RagAgent(retriever, planner, decider).answer("Question?")
        self.assertFalse(result.sufficient)
        self.assertEqual(result.retrieval_rounds, 2)
        self.assertEqual(len(retriever.queries), 2)
        self.assertIn("still missing", result.answer)

    async def test_rejects_unknown_citations_as_insufficient(self):
        from retrieval.agent import RagAgent
        from retrieval.models import AgentDecision, QueryPlan, SearchQuery
        query = SearchQuery(id="main", query="fact")
        planner = self.Chain(QueryPlan(queries=[query]))
        decider = self.Chain(AgentDecision(
            action="answer", answer="Invented [p99:c99].", citations=["p99:c99"]
        ))
        result = await RagAgent(self.Retriever([[self.hit()]]), planner, decider).answer("Question?")
        self.assertFalse(result.sufficient)
        self.assertEqual(result.sources, [])

