---
type: CLI Tool
title: find_contacts.py
description: Networking contact queries and public-page extraction via web.py. Agents with native web should skip this script.
tags: [script, networking, web]
timestamp: 2026-07-05T00:00:00Z
resource: scripts/find_contacts.py
---

# Note

Public-page scan uses [scripts/web.py](/okf/scripts/web.md) only with `--use-project-web`
(ADR 0004). When the harness has native web, follow the agent-driven path in
[find-contacts skill](/skills/find-contacts/SKILL.md) instead.

Re-run merge: same emails → replace `## Contacts`; new emails → keep prior rows and
append only the new ones. Failed fetches are listed under `### Failed fetches`.

Enrichment: opt-in only via `ENRICHMENT_PROVIDER=hunter` + `HUNTER_API_KEY` + `--domain`
(Apollo not implemented; `contact_enrichment` in yaml is unused).

Alumni search strings come from `networking.alumni_networks` in
`config/job_search_config.yaml` (overlay-aware), same source used by
[ai_tailor.py](/okf/scripts/ai-tailor.md) outreach priority targets.

# Examples

```bash
# Queries only (no scripts/web.py)
uv run scripts/find_contacts.py --company NVIDIA --role "ML Engineer" --id nvidia_ml_2026

# Also scan public pages (requires WEB_BACKEND)
uv run scripts/find_contacts.py --company NVIDIA --role "ML Engineer" --id nvidia_ml_2026 --use-project-web

# Optional Hunter enrichment
uv run scripts/find_contacts.py --company Acme --domain acme.com --id acme_ml_2026 --use-project-web
```

Other flags: `--max` (pages to scan).