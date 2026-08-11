---
type: Library
title: job_discovery.py
description: Discovery library (discover_jobs, fetch_jd, _make_id); used by pipeline.py. No CLI.
tags: [script, discovery, web, library]
timestamp: 2026-07-09T00:00:00Z
resource: scripts/job_discovery.py
---

# Role

Library only — **no CLI**. Scripted discovery runs via [pipeline.py](/okf/scripts/pipeline.md):

```bash
uv run scripts/pipeline.py --level tailor --max 5 --use-project-web
uv run scripts/pipeline.py --dry-run --max 5 --use-project-web
uv run scripts/pipeline.py --build --max 5 --find-contacts --use-project-web
```

Exports: `discover_jobs`, `fetch_jd`, `_make_id`.

Queries and the rank prompt incorporate `search_terms` / role prefs from
`config/job_search_config.yaml`. Ranking soft-threshold is relevance ≥ 7 (prompt only).

# Web access (ADR 0004)

Unattended discovery uses [scripts/web.py](/okf/scripts/web.md) only when
`use_project_web=True` (pipeline `--use-project-web`). Backend is `WEB_BACKEND` in `.env`
(`searxng` | `tavily` | `brave` | `serper` | `harness`).

Agents with harness-native web: follow [discover-jobs skill](/skills/discover-jobs/SKILL.md)
([shortlist](/okf/glossary/shortlist.md) → optional `new-application` handoff); do not call
this library's web path. Scripted `--dry-run` prints a shortlist; it does not write
`applications/shortlists.md`.

# Related

- [pipeline.py](/okf/scripts/pipeline.md)
- [discover-jobs skill](/skills/discover-jobs/SKILL.md)
- [Platform playbook](/okf/glossary/platform-playbook.md)
- [web access policy](/okf/architecture/web-access-policy.md)
