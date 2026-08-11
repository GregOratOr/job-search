---
type: CLI Tool
title: web.py
description: Project-owned pluggable web search and page fetch; opt-in fallback (ADR 0004).
tags: [script, web, fallback]
timestamp: 2026-07-05T00:00:00Z
resource: scripts/web.py
---

# When to use

**Only** when scripted code explicitly opts in (`use_project_web=True` / running this CLI).
Agents with harness-native web must not call this module. See
[web access policy](/okf/architecture/web-access-policy.md) and
[ADR 0004](/docs/adr/0004-skills-orchestrate-tools-process.md).

# API

- `require_project_web(enabled)` — shared gate helper
- `search(..., *, use_project_web=False)` — requires opt-in
- `fetch(..., *, use_project_web=False)` — requires opt-in
- CLI `uv run scripts/web.py search|fetch …` — implies opt-in

# Backends

`WEB_BACKEND` must be set explicitly (no default; scripts exit with a message when unset):
`searxng` | `tavily` | `brave` | `serper` | `harness`.

## Harness adapter (`harness`)

Set `HARNESS_WEB_SEARCH_CMD` and `HARNESS_WEB_FETCH_CMD` in `.env`. Wire to thin wrappers
around your harness's native web tools. Covered by `tests/test_harness_web.py`.

# Examples

```bash
uv run scripts/web.py search "ML engineer remote 2026" --max 8
uv run scripts/web.py search "ML engineer remote 2026" --backend tavily --json
uv run scripts/web.py fetch "https://example.com/job/123"
uv run scripts/web.py fetch "https://example.com/job/123" --max-chars 8000 --backend brave --json
```

Flags: search takes `--max`, `--backend` (per-run `WEB_BACKEND` override), `--json`;
fetch takes `--max-chars`, `--backend`, `--json`.

# Consumers (must pass --use-project-web / use_project_web=True)

- `research.py` gather
- `find_contacts.py` public-page scan
- `job_discovery` / `pipeline` discovery + JD fetch
- `ai_tailor.py --url`
