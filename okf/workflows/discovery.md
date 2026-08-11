---
type: Playbook
title: Job discovery
description: Find open postings and shortlist them; harness-native web preferred; handoff to new-application.
tags: [workflow, discovery, web]
timestamp: 2026-08-09T00:00:00Z
resource: scripts/pipeline.py
---

# Agent-driven (preferred when harness has native web)

1. Read campaign prefs from `config/job_search_config.yaml` — prefer
   `private/config/job_search_config.yaml` when the overlay is present (roles,
   companies, search_terms, locations, max_jobs).
2. Use `config/platforms.yaml` for search filters / career URLs (not application_steps).
3. Search with harness web tools (not `scripts/web.py`).
4. Rank against those prefs and present a shortlist; append a session block to
   `applications/shortlists.md` (separated by `---`).
5. For accepted jobs only: invoke [new-application](/skills/new-application/SKILL.md).

# Scripted (`pipeline.py`)

```bash
uv run scripts/pipeline.py --dry-run --max 5 --use-project-web
uv run scripts/pipeline.py --level tailor --max 5 --use-project-web
uv run scripts/pipeline.py --build --max 5 --use-project-web
```

Set `WEB_BACKEND` in `.env` (`searxng` | `tavily` | `brave` | `serper` | `harness`).
Library helpers live in [job_discovery.py](/okf/scripts/job-discovery.md) (no CLI).

# Policy

See [web access policy](/okf/architecture/web-access-policy.md).

# Related

- [discover-jobs skill](/skills/discover-jobs/SKILL.md)
- [new-application skill](/skills/new-application/SKILL.md)
- [job_discovery.py concept](/okf/scripts/job-discovery.md)
