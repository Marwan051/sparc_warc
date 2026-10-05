"""Provider-independent, serializable batch contracts."""

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class AnalysisRequest:
    page_id: int
    chunk_index: int
    text: str
    language: str
    title: str


@dataclass
class AnalysisOutcome:
    page_id: int
    chunk_index: int
    status: str
    summary: str | None = None
    category: str | None = None
    tags: list[str] = field(default_factory=list)
    error: str | None = None
    attempt_count: int = 0


@dataclass
class BatchResult:
    outcomes: list[AnalysisOutcome] = field(default_factory=list)
    quota_exhausted: bool = False


class AnalyzerBackend(Protocol):
    def analyze_batch(self, requests: list[AnalysisRequest]) -> BatchResult: ...
    def close(self) -> None: ...
