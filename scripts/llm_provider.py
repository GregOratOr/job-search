"""
scripts/llm_provider.py
-------------------------
Provider-agnostic chat completions for ai_tailor.py, audit.py, and job_discovery.py.

── Standalone use (no agent harness) ────────────────────────────────────────────
Configure via .env (see .env.example). Scripts read it automatically:

    LLM_PROVIDER=ollama          # anthropic | ollama | openai
    LLM_MODEL=qwen3.6:27b        # global default model for the provider
    OLLAMA_BASE_URL=http://127.0.0.1:11434/v1
    OLLAMA_API_KEY=ollama        # optional; Ollama ignores it

    ANTHROPIC_API_KEY=sk-ant-... # when LLM_PROVIDER=anthropic

    OPENAI_BASE_URL=...          # when LLM_PROVIDER=openai
    OPENAI_API_KEY=...

── Model resolution (per use) ───────────────────────────────────────────────────
Models are configured in .env — there are NO hardcoded model defaults in code.
Resolution order:

    0. Explicit model= / --model argument (wins immediately)
    1. LLM_MODEL_<TASK>   only when use_task_model=True (--use-agent)
                      (LLM_MODEL_TAILOR, LLM_MODEL_AUDIT, LLM_MODEL_RESEARCH,
                       LLM_MODEL_DISCOVERY, LLM_MODEL_FOLLOWUP)
    2. LLM_MODEL          (global default for the active provider)
    3. Provider-specific: OLLAMA_MODEL | ANTHROPIC_MODEL | OPENAI_MODEL
    4. Error — the script exits and asks you to set a model in .env.

── Harness use (Hermes / Cursor agent) ──────────────────────────────────────────
The scripts can't detect the harness automatically, so the SKILL.md instructs the
agent to pass the correct flags when the harness model differs from .env:

  Harness uses Ollama   → no flags needed; .env Ollama config is used as-is.
  Harness uses cloud    → agent passes --provider and --model so the script uses
                          the same cloud model instead of the .env Ollama config.

The --provider flag sets LLM_PROVIDER in the current process (overrides .env).
The --model   flag is used directly, bypassing LLM_MODEL from .env.
These are CLI-flag overrides for one run only — they do not touch .env.

── Provider resolution order (no CLI flags in effect) ───────────────────────────
  1. LLM_PROVIDER in env (from .env or shell export)
  2. Auto-detect: OLLAMA_BASE_URL / OLLAMA_MODEL / OLLAMA_API_KEY → ollama
  3. Auto-detect: ANTHROPIC_API_KEY present               → anthropic
  4. Auto-detect: OPENAI_API_KEY / OPENAI_BASE_URL        → openai
  5. Fallback: ollama
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

# Per-provider model variable in .env. There are NO hardcoded model defaults:
# every model must be configured in .env (see .env.example).
_PROVIDER_MODEL_VARS = {
    "anthropic": "ANTHROPIC_MODEL",
    "ollama": "OLLAMA_MODEL",
    "openai": "OPENAI_MODEL",
}

_REQUIRED_CREDENTIAL_VARS = {
    "anthropic": ("ANTHROPIC_API_KEY",),
    "openai": ("OPENAI_API_KEY",),
    "ollama": (),
}

_PROVIDER_MODEL_PREFIXES = {
    "anthropic": ("claude-", "anthropic/"),
    "openai": ("gpt-", "o1", "o3", "chatgpt-"),
    "ollama": (),
}


def load_env() -> None:
    """Load KEY=VALUE pairs from .env (private/ preferred) into os.environ (no overwrite)."""
    if str(ROOT) not in sys.path:
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

    if os.environ.get("OLLAMA_BASE_URL") or os.environ.get("OLLAMA_MODEL") or os.environ.get("OLLAMA_API_KEY"):
        return "ollama"
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    if os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI_BASE_URL"):
        return "openai"
    return "ollama"


def _validate_provider_credentials(provider: str) -> None:
    missing = [var for var in _REQUIRED_CREDENTIAL_VARS[provider] if not os.environ.get(var, "").strip()]
    if missing:
        joined = ", ".join(missing)
        print(f"[x] Missing credentials for provider '{provider}': {joined}")
        sys.exit(1)


def _validate_provider_model(provider: str, model: str) -> None:
    prefixes = _PROVIDER_MODEL_PREFIXES[provider]
    if not prefixes:
        return
    model_lower = model.lower()
    if not any(model_lower.startswith(prefix) for prefix in prefixes):
        expected = "Claude" if provider == "anthropic" else "OpenAI"
        print(f"[x] Model '{model}' is not valid for provider '{provider}'. Expected a {expected} model.")
        sys.exit(1)


def get_default_model(
    provider: str | None = None,
    task: str | None = None,
    *,
    use_task_model: bool = False,
    model: str | None = None,
) -> str:
    """Resolve the model from .env: explicit → task-specific → base → provider var.

    Exits with a clear message when no model is configured — there are no
    hardcoded model defaults in code.
    """
    if model:
        return model

    provider = provider or resolve_provider()

    if use_task_model and task:
        task_key = f"LLM_MODEL_{task.strip().upper()}"
        task_model = os.environ.get(task_key, "").strip()
        if task_model:
            return task_model

    global_model = os.environ.get("LLM_MODEL", "").strip()
    if global_model:
        return global_model

    provider_var = _PROVIDER_MODEL_VARS[provider]
    provider_model = os.environ.get(provider_var, "").strip()
    if provider_model:
        return provider_model

    task_hint = f" Per-task override: LLM_MODEL_{task.strip().upper()}." if task else ""
    print(f"[x] No model configured for provider '{provider}'. Set LLM_MODEL or {provider_var} in .env (see .env.example).{task_hint}")
    sys.exit(1)


@dataclass(frozen=True)
class LLMConfig:
    provider: str
    model: str
    base_url: str | None = None
    api_key: str | None = None


def get_config(
    model: str | None = None,
    *,
    task: str | None = None,
    use_task_model: bool = False,
) -> LLMConfig:
    provider = resolve_provider()
    resolved_model = model or get_default_model(provider=provider, task=task, use_task_model=use_task_model)
    _validate_provider_model(provider, resolved_model)

    if provider == "anthropic":
        _validate_provider_credentials(provider)
        api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        return LLMConfig(provider=provider, model=resolved_model, api_key=api_key)

    if provider == "ollama":
        _validate_provider_credentials(provider)
        base_url = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1").strip()
        api_key = os.environ.get("OLLAMA_API_KEY", "ollama").strip() or "ollama"
        return LLMConfig(provider=provider, model=resolved_model, base_url=base_url, api_key=api_key)

    # openai-compatible (OpenAI, Azure OpenAI, LM Studio, vLLM, etc.)
    _validate_provider_credentials(provider)
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").strip()
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
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
    task: str | None = None,
    use_task_model: bool = False,
) -> str:
    """Run one chat completion. Returns assistant text."""
    cfg = get_config(model, task=task, use_task_model=use_task_model)
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
    *,
    task: str | None = None,
    use_task_model: bool = False,
) -> str:
    """
    Anthropic-only: messages.create with web_search tool.
    Raises RuntimeError if provider is not anthropic.
    """
    cfg = get_config(model, task=task, use_task_model=use_task_model)
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