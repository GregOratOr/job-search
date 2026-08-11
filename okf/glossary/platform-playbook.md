---
type: Glossary Term
title: Platform playbook
description: config/platforms.yaml — human/agent reference for navigating job boards; not loaded by Python.
tags: [glossary, discovery, config]
timestamp: 2026-08-09T00:00:00Z
resource: config/platforms.yaml
---

`config/platforms.yaml` (or `private/config/platforms.yaml` with overlay) holds per-platform
search filters, career URLs, notes, and post-shortlist application / referral checklists.

# Usage

- [discover-jobs](/skills/discover-jobs/SKILL.md) may use `url`, `search_filters`,
  `companies_and_career_urls`, and notes while searching.
- Do **not** auto-execute `application_steps` / referral `workflow` during discovery —
  those are checklists after a shortlist handoff.
- **Not imported by any Python script today.** Wiring into scripted discovery is deferred;
  see [discontinuities](/okf/audit/codebase-discontinuities.md).

# Related

- [Shortlist](/okf/glossary/shortlist.md)
- [job_search_config.yaml](/config/job_search_config.yaml) — campaign prefs the pipeline *does* load
