# 3. Project-owned web tool with a pluggable backend

Date: 2026-06-24

## Status

Accepted

## Context

Job discovery, company research, and contact-finding all need web access. Today, browsing is
hard-wired to Anthropic's `web_search` tool (`anthropic_web_search_complete` in
`scripts/llm_provider.py`), so a bare local Ollama run has *no* web access at all. Harnesses
differ: Hermes ships `web_search`/`web_extract`, but other harnesses (or a plain Ollama loop)
may ship nothing, and Hermes' DuckDuckGo backend may not support extraction everywhere.

## Decision

Give the project its **own** web tool, `scripts/web.py`, with a pluggable backend selected by
env var (`WEB_BACKEND`). The backend must be set explicitly (no implicit default):

- `searxng` — a free, self-hosted SearXNG instance at `SEARXNG_URL`.
- `tavily` / `brave` / `serper` — optional hosted APIs behind their own keys.
- `harness` — subprocess adapters via `HARNESS_WEB_SEARCH_CMD` / `HARNESS_WEB_FETCH_CMD`.

It exposes `search(query)` and `fetch(url)` (with readability-style text extraction). Callers
must pass `--use-project-web` / `use_project_web=True` (ADR 0004).

**Harness-native web comes first.** When the harness ships built-in search/extraction (Hermes
`web_search`/`web_extract`, Cursor browser MCP, Anthropic `web_search`), skills instruct
the agent to use those tools directly and **not** invoke `scripts/web.py`. The project web
tool is the fallback for bare local runs and scripted pipelines where no harness web
capability exists.

## Consequences

- Local Ollama runs gain real web access without any cloud key.
- Discovery is decoupled from Anthropic; Anthropic `web_search` is not used by discovery
  (scripted discovery always goes through `web.py` when opted in).
- The user must set `WEB_BACKEND` explicitly and configure the matching endpoint/key (or
  harness adapters); this is documented in `.env.example`.

## Updates

- **2026-07 / ADR 0004:** Callers must pass `--use-project-web` / `use_project_web=True`.
- **2026-08 (SA-13):** `--search-mode` retired; backend is only `WEB_BACKEND`
  (`searxng` | `tavily` | `brave` | `serper` | `harness`). `job_discovery.py` is library-only.
- **2026-08:** `WEB_BACKEND` must be set explicitly — the implicit `searxng` default was
  removed; scripts exit with a clear message when it is unset.
