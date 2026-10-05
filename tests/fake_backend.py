"""Deterministic batch adapter for tests; never calls a provider."""

from tagging.contracts import AnalysisOutcome, BatchResult


class FakeBackend:
    def __init__(self, model):
        self.model = model

    def close(self):
        pass

    def analyze_batch(self, requests):
        result = BatchResult()
        for item in requests:
            if item.text == "quota":
                result.quota_exhausted = True
                break
            status = "ERROR" if item.text == "error" else "SUCCESS"
            result.outcomes.append(AnalysisOutcome(item.page_id, item.chunk_index, status,
                summary="A test summary." if status == "SUCCESS" else None,
                category="Other" if status == "SUCCESS" else None,
                error="test error" if status == "ERROR" else None, attempt_count=1))
        return result
