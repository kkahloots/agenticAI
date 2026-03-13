import os
import pytest
from unittest.mock import patch, MagicMock


def _reload_llm():
    """Force reload of src.core.llm so env var changes take effect."""
    import importlib
    import nonagentic.core.llm as mod

    mod.get_llm.cache_clear()
    importlib.reload(mod)
    return mod


# ── provider selection ────────────────────────────────────────────────────────


def test_default_provider_is_openai(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    mod = _reload_llm()
    info = mod.provider_info()
    assert info["provider"] == "openai"


def test_openai_provider_selected(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o")
    mod = _reload_llm()
    info = mod.provider_info()
    assert info["provider"] == "openai"
    assert info["model"] == "gpt-4o"


def test_ollama_provider_selected(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_MODEL", "mistral")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434")
    mod = _reload_llm()
    info = mod.provider_info()
    assert info["provider"] == "ollama"
    assert info["model"] == "mistral"
    assert "11434" in info["base_url"]


def test_gptec_provider_selected(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "gptec")
    monkeypatch.setenv("GPTEC_API_URL", "https://gptec.example.com/v1")
    monkeypatch.setenv("GPTEC_API_KEY", "test-key")
    monkeypatch.setenv("GPTEC_MODEL", "custom-model")
    mod = _reload_llm()
    info = mod.provider_info()
    assert info["provider"] == "gptec"
    assert info["model"] == "custom-model"
    assert "gptec.example.com" in info["base_url"]


# ── gptec missing env vars ────────────────────────────────────────────────────


def test_gptec_raises_without_required_vars(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "gptec")
    monkeypatch.delenv("GPTEC_API_URL", raising=False)
    monkeypatch.delenv("GPTEC_API_KEY", raising=False)
    monkeypatch.delenv("GPTEC_MODEL", raising=False)
    mod = _reload_llm()
    with pytest.raises(EnvironmentError, match="GPTEC provider requires"):
        mod.get_llm()


# ── get_llm returns BaseChatModel ─────────────────────────────────────────────


@pytest.mark.real_llm_factory
def test_get_llm_openai_returns_chat_model(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
    mod = _reload_llm()
    llm = mod.get_llm(temperature=0.0)
    from langchain_core.language_models.chat_models import BaseChatModel

    assert isinstance(llm, BaseChatModel)


@pytest.mark.real_llm_factory
def test_get_llm_ollama_falls_back_to_openai_shim(monkeypatch):
    """When langchain-ollama is not installed, falls back to ChatOpenAI shim."""
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434")
    with patch.dict("sys.modules", {"langchain_ollama": None}):
        mod = _reload_llm()
        llm = mod.get_llm(temperature=0.0)
        from langchain_core.language_models.chat_models import BaseChatModel

        assert isinstance(llm, BaseChatModel)


# ── caching ───────────────────────────────────────────────────────────────────


@pytest.mark.real_llm_factory
def test_get_llm_same_temperature_returns_cached(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    mod = _reload_llm()
    llm1 = mod.get_llm(temperature=0.0)
    llm2 = mod.get_llm(temperature=0.0)
    assert llm1 is llm2


@pytest.mark.real_llm_factory
def test_get_llm_different_temperatures_are_different(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    mod = _reload_llm()
    llm_det = mod.get_llm(temperature=0.0)
    llm_cre = mod.get_llm(temperature=0.3)
    assert llm_det is not llm_cre
