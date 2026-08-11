from __future__ import annotations

import pytest

from scripts.llm_provider import get_config, get_default_model, resolve_provider


@pytest.fixture(autouse=True)
def clear_llm_env(monkeypatch):
    for key in [
        "LLM_PROVIDER",
        "LLM_MODEL",
        "LLM_MODEL_TAILOR",
        "LLM_MODEL_AUDIT",
        "LLM_MODEL_RESEARCH",
        "LLM_MODEL_DISCOVERY",
        "LLM_MODEL_FOLLOWUP",
        "OLLAMA_BASE_URL",
        "OLLAMA_MODEL",
        "ANTHROPIC_API_KEY",
        "ANTHROPIC_MODEL",
        "OPENAI_API_KEY",
        "OPENAI_BASE_URL",
        "OPENAI_MODEL",
        "OLLAMA_API_KEY",
    ]:
        monkeypatch.delenv(key, raising=False)


def test_resolve_provider_defaults_to_ollama_when_nothing_is_set():
    assert resolve_provider() == "ollama"


def test_get_default_model_prefers_task_specific_model_for_agent_mode(monkeypatch):
    monkeypatch.setenv("LLM_MODEL", "base-model")
    monkeypatch.setenv("LLM_MODEL_TAILOR", "task-model")
    assert get_default_model(task="tailor", use_task_model=True) == "task-model"


def test_get_default_model_skips_task_model_without_agent_flag(monkeypatch):
    monkeypatch.setenv("LLM_MODEL", "base-model")
    monkeypatch.setenv("LLM_MODEL_TAILOR", "task-model")
    assert get_default_model(task="tailor", use_task_model=False) == "base-model"


def test_get_default_model_explicit_model_wins(monkeypatch):
    monkeypatch.setenv("LLM_MODEL", "base-model")
    monkeypatch.setenv("LLM_MODEL_TAILOR", "task-model")
    assert get_default_model(task="tailor", use_task_model=True, model="cli-model") == "cli-model"


def test_get_config_raises_for_missing_credentials(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("LLM_MODEL", "claude-3-5-haiku-latest")
    with pytest.raises(SystemExit):
        get_config()


def test_get_config_rejects_invalid_provider_model_combo(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("LLM_MODEL", "gpt-4.1")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    with pytest.raises(SystemExit):
        get_config()


def test_get_config_rejects_claude_model_for_openai(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_MODEL", "claude-opus-4-7")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    with pytest.raises(SystemExit):
        get_config()


def test_get_config_ollama_accepts_any_model_and_default_base_url(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("LLM_MODEL", "qwen3.6:27b-q4_K_M")
    cfg = get_config()
    assert cfg.provider == "ollama"
    assert cfg.model == "qwen3.6:27b-q4_K_M"
    assert cfg.base_url == "http://127.0.0.1:11434/v1"
