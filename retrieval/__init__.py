"""Public interface for the news RAG agent."""

from retrieval.agent import RagAgent, answer
from retrieval.models import RagResult

__all__ = ["RagAgent", "RagResult", "answer"]

