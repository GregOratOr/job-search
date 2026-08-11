---
type: CLI Tool
title: llm_provider.py
description: Provider-agnostic chat completions for anthropic, ollama, openai-compatible endpoints.
tags: [script, llm]
timestamp: 2026-07-05T00:00:00Z
resource: scripts/llm_provider.py
---

Configured via `.env`: `LLM_PROVIDER`, models, provider-specific keys/URLs.

# Model resolution (no hardcoded model names)

All models come from `.env` or an explicit `model=` / `--model`. Per call,
`get_default_model(...)` resolves:

0. Explicit `model=` argument (wins immediately)
1. `LLM_MODEL_<TASK>` — only when `use_task_model=True` (`--use-agent`):
   `LLM_MODEL_TAILOR`, `LLM_MODEL_AUDIT`, `LLM_MODEL_RESEARCH`,
   `LLM_MODEL_DISCOVERY`, `LLM_MODEL_FOLLOWUP`
2. `LLM_MODEL` — global default for the active provider
3. Provider variable — `OLLAMA_MODEL` | `ANTHROPIC_MODEL` | `OPENAI_MODEL`
4. Error — exits asking you to set a model in `.env`

Provider fallback when nothing is configured: `ollama`.

# Calling AI scripts from a harness

The AI scripts (`ai_tailor.py`, `audit.py`, `research.py`, `followup.py`, `pipeline.py`)
make their own LLM calls. Which flags the agent must pass depends on the session model:

| Harness | Session model | What to pass to scripts |
|---------|--------------|------------------------|
| None (standalone) | ← from `.env` | nothing |
| Hermes / Cursor | Ollama (local) | nothing (or `--model <alt-ollama-model>` to switch) |
| Hermes / Cursor | Anthropic cloud | `--provider anthropic --model <model-name>` |
| Hermes / Cursor | OpenAI cloud | `--provider openai --model <model-name>` |

`--provider` overrides `LLM_PROVIDER` for that one run without touching `.env`.
From a cloud-model session, always pass both flags — otherwise the script falls back
to the `.env` Ollama config, which may point at a model that is weaker or not running.

Also exposes `anthropic_web_search_complete` (legacy helper; discovery no longer uses it).
