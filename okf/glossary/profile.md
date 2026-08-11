---
type: Glossary Term
title: Profile
description: Single source of truth for personal data; read-only to agents unless explicitly updated.
tags: [glossary, profile]
timestamp: 2026-08-09T00:00:00Z
---

Path: `profile/` (or `private/profile/` with overlay). Split modules: `header.py`, `education.py`,
`experience.py`, `projects.py`, `skills.py`, `summaries.py`, `research.py`, `coursework.py`,
`master_data.py`.

# Rules

- Agents treat profile as **read-only** unless the user explicitly commands an update.
- Job-specific selection/rewrites use `dataclasses.replace()` in
  `resume/outputs/<id>.py` and `coverletter/outputs/<id>_cl.py` — never duplicate profile data.
- Updates append to `profile/CHANGELOG.md`.

Discover live entry names (public templates use `EXAMPLE_*`; private overlay may differ):

```bash
uv run scripts/validate_profile.py --inventory
```
