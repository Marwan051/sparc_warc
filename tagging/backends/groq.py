"""Groq adapter with one client per worker and bounded per-item retries."""

import os
import time
import httpx
from langchain_groq import ChatGroq
from tagging.contracts import AnalysisOutcome, BatchResult
from tagging.backends import groq_rules as rules


class GroqBackend:
    def __init__(self, model):
        self.model = model
        self.client = httpx.Client(timeout=60)
        self.chains = {}
        self.interval = float(os.environ.get("TAG_REQUEST_INTERVAL_SECONDS", "1.5"))
        self.next_request = 0.0
        self.parallelism = int(os.environ.get("TAG_PARALLELISM", "3"))
        self.rpm = int(os.environ.get("TAG_REQUESTS_PER_MINUTE", "0"))
        self.tpm = int(os.environ.get("TAG_TOKENS_PER_MINUTE", "0"))

    def close(self):
        self.client.close()

    def _chain(self, temperature):
        if temperature not in self.chains:
            llm = ChatGroq(model=self.model, temperature=temperature,
                           max_tokens=600, max_retries=0,
                           api_key=os.environ["GROQ_API_KEY"], http_client=self.client,
                           **({"reasoning_effort": "none"} if self.model == rules.DEFAULT_GROQ_MODEL else {}))
            self.chains[temperature] = rules.CHUNK_ANALYSIS_PROMPT | llm.with_structured_output(rules.ChunkAnalysis)
        return self.chains[temperature]

    def analyze_batch(self, requests):
        batch = BatchResult()
        for request in requests:
            outcome = AnalysisOutcome(request.page_id, request.chunk_index, "ERROR")
            for attempt in range(5):
                time.sleep(max(0, self.next_request - time.monotonic()))
                interval = self.interval
                if self.rpm:
                    interval = max(interval, 60 * self.parallelism / self.rpm)
                if self.tpm:
                    # UTF-8 bytes are a conservative input-token estimate, plus
                    # output allowance. This shapes throughput, not a shared
                    # provider quota ledger; 429 handling remains authoritative.
                    prompt = rules.CHUNK_ANALYSIS_PROMPT.format(text=request.text,
                        title=request.title, language=rules.LANGUAGE_NAMES.get(request.language, request.language))
                    token_budget = len(prompt.encode()) + 600
                    interval = max(interval, 60 * self.parallelism * token_budget / self.tpm)
                self.next_request = time.monotonic() + interval
                outcome.attempt_count += 1
                try:
                    result = self._chain(0.0 if attempt == 0 else 0.3).invoke({
                        "text": request.text, "title": request.title or "(none)",
                        "language": rules.LANGUAGE_NAMES.get(request.language.lower(), request.language),
                    })
                    problem = rules._summary_problem(result.summary, request.language)
                    if problem:
                        raise ValueError(f"bad summary: {problem}")
                    if rules.is_noise_summary(result.summary, result.category):
                        outcome.status = "NOISE"
                        outcome.summary = rules._NOT_ARTICLE_TAG_RE.sub("", result.summary).strip()
                    else:
                        outcome.status = "SUCCESS"
                        outcome.summary = result.summary
                        outcome.category = result.category
                        outcome.tags = rules._cap_tags(rules._filter_tags(result.tags, request.text))
                    outcome.error = None
                    break
                except Exception as error:
                    message = str(error).replace(os.environ.get("GROQ_API_KEY", "\0"), "[REDACTED]")
                    if rules._is_daily_quota_error(message):
                        batch.quota_exhausted = True
                        return batch
                    outcome.error = message[:2000]
                    status = getattr(error, "status_code", None)
                    if status in (401, 403, 404):
                        raise RuntimeError(f"Groq configuration failure (HTTP {status})") from None
                    if not (status in (429, 500, 502, 503, 504) or rules._is_retryable(message)):
                        break
                    if attempt < 4:
                        wait = rules._quota_wait_seconds(message) or 5 * 2 ** attempt
                        headers = getattr(getattr(error, "response", None), "headers", {})
                        try:
                            wait = max(wait, float(headers.get("retry-after", 0)))
                        except (TypeError, ValueError):
                            pass
                        if wait > rules.MAX_AUTO_WAIT:
                            batch.quota_exhausted = True
                            return batch
                        time.sleep(wait)
            batch.outcomes.append(outcome)
        return batch
