"""
scripts/llm_provider.py
-------------------------
Provider-agnostic chat completions for ai_tailor.py and job_discovery.py.

Configure via .env (see .env.example):

    LLM_PROVIDER=ollama          # anthropic | ollama | openai
    LLM_MODEL=gemma4:12b         # default model for all providers
    OLLAMA_BASE_URL=http://127.0.0.1:11434/v1
    OLLAMA_API_KEY=ollama        # optional; Ollama ignores it

    ANTHROPIC_API_KEY=sk-ant-... # when LLM_PROVIDER=anthropic

    OPENAI_BASE_URL=...          # when LLM_PROVIDER=openai
    OPENAI_API_KEY=...

If LLM_PROVIDER is unset, resolution order is:
  explicit OLLAMA_* vars → ollama
  ANTHROPIC_API_KEY      → anthropic
  OPENAI_* vars          → openai
  else                   → anthropic (requires key)
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parent.parent

_VALID_PROVIDERS = frozenset({"anthropic", "ollama", "openai"})

_DEFAULT_MODELS = {
    "anthropic": "claude-opus-4-7",
    "ollama": "gemma4:12b",
    "openai": "gpt-4o",
}


def load_env() -> None:
    """Load KEY=VALUE pairs from .env (private/ preferred) into os.environ (no overwrite)."""
    sys.path.insert(0, str(ROOT))
    from scripts.data_paths import resolve_env_file
    env_file = resolve_env_file()
    if env_file is None:
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def resolve_provider() -> str:
    explicit = os.environ.get("LLM_PROVIDER", "").strip().lower()
    if explicit:
        if explicit not in _VALID_PROVIDERS:
            print(f"[x] Unknown LLM_PROVIDER={explicit!r}. Use: anthropic, ollama, openai")
            sys.exit(1)
        return explicit

    if os.environ.get("OLLAMA_BASE_URL") or os.environ.get("OLLAMA_MODEL"):
        return "ollama"
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    if os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI_BASE_URL"):
        return "openai"
    return "anthropic"


def get_default_model(provider: str | None = None) -> str:
    provider = provider or resolve_provider()
    for key in ("LLM_MODEL", "AI_TAILOR_MODEL"):
        override = os.environ.get(key, "").strip()
        if override:
            return override
    if provider == "ollama":
        return os.environ.get("OLLAMA_MODEL", _DEFAULT_MODELS["ollama"]).strip()
    if provider == "openai":
        return os.environ.get("OPENAI_MODEL", _DEFAULT_MODELS["openai"]).strip()
    return _DEFAULT_MODELS["anthropic"]


@dataclass(frozen=True)
class LLMConfig:
    provider: str
    model: str
    base_url: str | None = None
    api_key: str | None = None


def get_config(model: str | None = None) -> LLMConfig:
    provider = resolve_provider()
    resolved_model = model or get_default_model(provider)

    if provider == "anthropic":
        api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        if not api_key:
            print("[x] ANTHROPIC_API_KEY not set. Add it to .env or set LLM_PROVIDER=ollama.")
            sys.exit(1)
        return LLMConfig(provider=provider, model=resolved_model, api_key=api_key)

    if provider == "ollama":
        base_url = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1").strip()
        api_key = os.environ.get("OLLAMA_API_KEY", "ollama").strip() or "ollama"
        return LLMConfig(provider=provider, model=resolved_model, base_url=base_url, api_key=api_key)

    # openai-compatible (OpenAI, Azure OpenAI, LM Studio, vLLM, etc.)
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").strip()
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        print("[x] OPENAI_API_KEY not set for LLM_PROVIDER=openai.")
        sys.exit(1)
    return LLMConfig(provider=provider, model=resolved_model, base_url=base_url, api_key=api_key)


def provider_label(cfg: LLMConfig) -> str:
    return f"{cfg.provider}/{cfg.model}"


def _extract_openai_text(data: dict[str, Any]) -> str:
    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError(f"No choices in response: {data!r}")
    message = choices[0].get("message") or {}
    content = message.get("content", "")
    if isinstance(content, list):
        # Some providers return multimodal blocks
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        content = "".join(parts)
    return str(content).strip()


def _openai_compatible_complete(cfg: LLMConfig, system: str, user: str, max_tokens: int) -> tuple[str, int | None]:
    assert cfg.base_url is not None
    url = cfg.base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": cfg.model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.2,
    }
    headers = {"Content-Type": "application/json"}
    if cfg.api_key:
        headers["Authorization"] = f"Bearer {cfg.api_key}"

    resp = httpx.post(url, json=payload, headers=headers, timeout=600.0)
    if resp.status_code >= 400:
        raise RuntimeError(f"HTTP {resp.status_code} from {url}: {resp.text[:500]}")
    data = resp.json()
    text = _extract_openai_text(data)
    usage = data.get("usage") or {}
    out_tokens = usage.get("completion_tokens")
    return text, out_tokens


def _anthropic_complete(cfg: LLMConfig, system: str, user: str, max_tokens: int) -> tuple[str, int | None]:
    import anthropic

    client = anthropic.Anthropic(api_key=cfg.api_key)
    resp = client.messages.create(
        model=cfg.model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    text = resp.content[0].text.strip()
    return text, resp.usage.output_tokens


def complete(
    system: str,
    user: str,
    model: str | None = None,
    max_tokens: int = 2048,
    *,
    quiet: bool = False,
) -> str:
    """Run one chat completion. Returns assistant text."""
    cfg = get_config(model)
    if not quiet:
        print(f"    [api] {provider_label(cfg)} ...", end="", flush=True)

    if cfg.provider == "anthropic":
        text, out_tokens = _anthropic_complete(cfg, system, user, max_tokens)
    else:
        text, out_tokens = _openai_compatible_complete(cfg, system, user, max_tokens)

    if not quiet:
        suffix = f" {out_tokens} tokens" if out_tokens is not None else ""
        print(f"{suffix}")
    return text


def anthropic_web_search_complete(
    system: str,
    user: str,
    model: str | None = None,
    max_tokens: int = 4096,
) -> str:
    """
    Anthropic-only: messages.create with web_search tool.
    Raises RuntimeError if provider is not anthropic.
    """
    cfg = get_config(model)
    if cfg.provider != "anthropic":
        raise RuntimeError(
            f"Web search requires LLM_PROVIDER=anthropic (current: {cfg.provider}). "
            "Use Hermes/discover-jobs skill for local agent web search, or switch provider."
        )

    import anthropic

    print(f"    [api] {provider_label(cfg)} + web_search ...", end="", flush=True)
    client = anthropic.Anthropic(api_key=cfg.api_key)
    resp = client.messages.create(
        model=cfg.model,
        max_tokens=max_tokens,
        system=system,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": user}],
    )
    text_blocks = [b.text for b in resp.content if hasattr(b, "text")]
    raw = text_blocks[-1] if text_blocks else "[]"
    print(" done")
    return raw.strip()


def supports_web_search() -> bool:
    return resolve_provider() == "anthropic"
