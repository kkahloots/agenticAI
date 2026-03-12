"""
Universal LLM factory with token-usage tracking.

Provider is selected by the LLM_PROVIDER environment variable:

  LLM_PROVIDER=openai   (default)
    OPENAI_API_KEY=<key>
    OPENAI_MODEL=gpt-4o-mini

  LLM_PROVIDER=ollama
    OLLAMA_BASE_URL=http://localhost:11434
    OLLAMA_MODEL=llama3

  LLM_PROVIDER=gptec
    GPTEC_API_URL=https://<your-gptec-endpoint>/v1
    GPTEC_API_KEY=<key>
    GPTEC_MODEL=<model-name>

All providers return a LangChain BaseChatModel wrapped with token tracking.
"""
from __future__ import annotations

import os
from functools import lru_cache
from langchain_core.language_models.chat_models import BaseChatModel


@lru_cache(maxsize=4)
def get_llm(temperature: float = 0.0) -> BaseChatModel:
    """Return a cached, token-tracking LangChain chat model for the configured provider."""
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    if provider == "ollama":
        base = _ollama(temperature)
    elif provider == "gptec":
        base = _gptec(temperature)
    else:
        base = _openai(temperature)
    return _with_token_tracking(base)


def _openai(temperature: float) -> BaseChatModel:
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=temperature,
        api_key=os.getenv("OPENAI_API_KEY"),
    )


def _ollama(temperature: float) -> BaseChatModel:
    try:
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "llama3"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=temperature,
        )
    except ImportError:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=os.getenv("OLLAMA_MODEL", "llama3"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434") + "/v1",
            api_key="ollama",
            temperature=temperature,
        )


def _gptec(temperature: float) -> BaseChatModel:
    from langchain_openai import ChatOpenAI
    url = os.getenv("GPTEC_API_URL")
    key = os.getenv("GPTEC_API_KEY")
    model = os.getenv("GPTEC_MODEL")
    if not url or not key or not model:
        raise EnvironmentError(
            "GPTEC provider requires GPTEC_API_URL, GPTEC_API_KEY, and GPTEC_MODEL to be set."
        )
    return ChatOpenAI(model=model, base_url=url, api_key=key, temperature=temperature)


class _TokenTrackingLLM(BaseChatModel):
    """
    Thin wrapper that delegates all calls to the underlying model and
    reports token usage to src.observability.record_tokens after each invoke.
    """
    _inner: BaseChatModel

    def __init__(self, inner: BaseChatModel):
        # bypass Pydantic init — store inner directly
        object.__setattr__(self, "_inner", inner)

    # ── delegate required abstract methods ──────────────────────────────────

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        return self._inner._generate(messages, stop=stop, run_manager=run_manager, **kwargs)

    @property
    def _llm_type(self) -> str:
        return getattr(self._inner, "_llm_type", "tracked")

    # ── override invoke to capture token metadata ────────────────────────────

    def invoke(self, input, config=None, **kwargs):
        response = self._inner.invoke(input, config=config, **kwargs)
        self._report(response)
        return response

    def _report(self, response) -> None:
        try:
            from src.core.observability import record_tokens
            # LangChain stores usage in response.usage_metadata or response.response_metadata
            usage = getattr(response, "usage_metadata", None) or {}
            tokens = (
                usage.get("total_tokens")
                or usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
            )
            if not tokens:
                meta = getattr(response, "response_metadata", {}) or {}
                token_usage = meta.get("token_usage") or meta.get("usage") or {}
                tokens = token_usage.get("total_tokens", 0)
            if tokens:
                # request_id is not available here; use a sentinel key
                # node_trace will pop it by request_id — we use "_last" as fallback
                import threading
                key = getattr(threading.current_thread(), "_lg_request_id", "_last")
                record_tokens(key, int(tokens))
        except Exception:
            pass


def _with_token_tracking(model: BaseChatModel) -> BaseChatModel:
    return _TokenTrackingLLM(model)


def provider_info() -> dict:
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    if provider == "ollama":
        return {
            "provider": "ollama",
            "model": os.getenv("OLLAMA_MODEL", "llama3"),
            "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        }
    if provider == "gptec":
        return {
            "provider": "gptec",
            "model": os.getenv("GPTEC_MODEL", "<not set>"),
            "base_url": os.getenv("GPTEC_API_URL", "<not set>"),
        }
    return {
        "provider": "openai",
        "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        "base_url": "https://api.openai.com/v1",
    }
