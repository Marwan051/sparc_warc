"""LLM provider selection for the RAG agent.

Switching providers is a single knob: set ``RAG_MODEL`` to a Gemini/Gemma model
and the provider is inferred, or force one explicitly with ``RAG_PROVIDER``.
"""

from __future__ import annotations

import os

from langchain_core.exceptions import OutputParserException
from langchain_groq import ChatGroq


PROVIDER_DEFAULT_MODELS = {
    "groq": "openai/gpt-oss-120b",
    # Gemini's schema dialect drops "additionalProperties"/"strict" for us, and
    # this lite model follows the answer-language rule across ar/en/fr.
    "gemini": "gemini-3.5-flash-lite",
}

_GEMINI_PREFIXES = ("gemini", "gemma", "models/gemini", "models/gemma")


def resolve_provider(model: str | None = None) -> str:
    """Return the provider name from RAG_PROVIDER, else inferred from the model."""
    explicit = os.environ.get("RAG_PROVIDER", "").strip().lower()
    if explicit:
        if explicit not in PROVIDER_DEFAULT_MODELS:
            raise ValueError(
                "RAG_PROVIDER must be one of "
                f"{sorted(PROVIDER_DEFAULT_MODELS)}, got {explicit!r}"
            )
        return explicit
    name = (model or os.environ.get("RAG_MODEL", "")).strip().lower()
    if name.startswith(_GEMINI_PREFIXES):
        return "gemini"
    return "groq"


def resolve_model(provider: str, model: str | None = None) -> str:
    """Return the configured model or the provider's default."""
    return (model or os.environ.get("RAG_MODEL", "")).strip() or PROVIDER_DEFAULT_MODELS[provider]


def structured_output_kwargs(provider: str) -> dict:
    """Keyword arguments for ``with_structured_output`` per provider."""
    if provider == "gemini":
        return {"method": "json_schema"}
    # Groq speaks OpenAI strict json_schema; keep the constrained-decoding flag.
    return {"method": "json_schema", "strict": True}


def build_chat_model(provider: str, model: str):
    """Construct the chat model for a resolved provider and model name."""
    if provider == "gemini":
        return _build_gemini(model)
    return _build_groq(model)


def _build_groq(model: str):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is required for the groq provider")
    kwargs = dict(model=model, temperature=0, max_tokens=2400, max_retries=2, api_key=api_key)
    # gpt-oss-120b only honours the answer-language rule at "medium" or higher;
    # at "low" it mirrors the (possibly different-language) evidence. Only the
    # groq reasoning models accept this knob.
    effort = os.environ.get("RAG_REASONING_EFFORT", "medium")
    if effort:
        kwargs["reasoning_effort"] = effort
    return ChatGroq(**kwargs)


def _build_gemini(model: str):
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is required for the gemini provider")
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
    except ImportError as error:  # pragma: no cover - depends on local install
        raise ImportError(
            "langchain-google-genai is required for the gemini provider; "
            "install it with: pip install -r requirements/rag-agent.txt"
        ) from error
    # Gemini reasoning models spend output budget on thoughts, so leave headroom.
    return ChatGoogleGenerativeAI(
        model=model,
        api_key=api_key,
        max_output_tokens=8192,
        max_retries=2,
    )


def retryable_errors() -> tuple[type[Exception], ...]:
    """Provider errors that a single structured-output retry can recover from."""
    errors: list[type[Exception]] = [OutputParserException]
    try:
        from groq import BadRequestError
    except ImportError:  # pragma: no cover - groq is a hard dependency
        pass
    else:
        errors.append(BadRequestError)
    try:
        from google.api_core import exceptions as google_exceptions
    except ImportError:  # pragma: no cover - only when gemini is selected
        pass
    else:
        errors.extend([google_exceptions.BadRequest, google_exceptions.InvalidArgument])
    return tuple(errors)
