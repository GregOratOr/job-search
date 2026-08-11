---
type: Playbook
title: Web access policy
description: Use harness-native web search/extraction when available; scripts/web.py is the fallback for standalone runs.
tags: [architecture, web, harness, adr]
timestamp: 2026-07-05T00:00:00Z
resource: scripts/web.py
---

# Decision tree

```
Does the harness provide built-in web search + page extraction?
├── YES → Use harness tools directly. Do NOT run scripts/web.py.
│         Agent-driven: search/fetch yourself, then call ai_tailor.py etc.
│         Scripted (optional): WEB_BACKEND=harness + --use-project-web
│         (shells out via HARNESS_WEB_*_CMD adapters)
└── NO  → Configure WEB_BACKEND in .env and pass --use-project-web
          on pipeline / research / contacts / ai_tailor --url
```

# Harness-native examples

| Harness | Native capability |
|---------|-------------------|
| Hermes | `web_search`, `web_extract` |
| Cursor | Browser MCP (`browser_navigate`, fetch, snapshot) |
| Anthropic (provider) | `web_search` via `llm_provider` exists but is **not** used by discovery (retired) |

# Project web tool (fallback + harness adapter)

`scripts/web.py` — pluggable backends: `searxng` | `tavily` | `brave` | `serper` | `harness`.
`WEB_BACKEND` must be set explicitly — there is no default; scripts exit with a clear
message when it is unset.

## Harness subprocess adapters (`WEB_BACKEND=harness`)

Scripted harness backend does **not** rely on prompt-only LLM search. Instead `web.py` shells out to
env-configured adapters **only when** callers opt in with `--use-project-web` (ADR 0004).
Agents with native web must not call `scripts/web.py`.

| Env var | Invocation | stdout contract |
|---------|------------|-----------------|
| `HARNESS_WEB_SEARCH_CMD` | `{cmd} <query>` | JSON array `[{title, url, snippet}, ...]` |
| `HARNESS_WEB_FETCH_CMD` | `{cmd} <url>` | Plain text (JD body) |

Example `.env` (point at your harness's thin wrapper scripts):

```
HARNESS_WEB_SEARCH_CMD=your-harness-search-adapter
HARNESS_WEB_FETCH_CMD=your-harness-fetch-adapter
```

Unit tests mock these adapters (`tests/test_harness_web.py`); there is no in-repo stub CLI.
Each harness ships thin wrapper scripts that call its native `web_search` / `web_extract` (or
browser MCP) and emit the JSON/text contract above.

Used by scripted paths when no direct harness API exists in-process:
- `pipeline.py` discovery (via `job_discovery.discover_jobs` / `fetch_jd`)
- `research.py`
- `find_contacts.py`
- `pipeline.py` research step (calls `research.py`)

# Agent instructions

When executing skills `discover-jobs`, `research`, or `find-contacts` inside a harness with
native web, follow the **agent-driven** steps in each skill — not the scripted CLI path.

# Related

- [Discovery workflow](/okf/workflows/discovery.md)
- [scripts/web.py concept](/okf/scripts/web.md)

# Citations

[1] [ADR 0003](/docs/adr/0003-project-owned-web-tool.md)
[2] [discover-jobs skill](/skills/discover-jobs/SKILL.md)
