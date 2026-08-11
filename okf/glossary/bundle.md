---
type: Glossary Term
title: Bundle
description: The per-application folder holding everything needed to apply.
tags: [glossary, bundle, application]
timestamp: 2026-07-05T00:00:00Z
---

Path: `applications/jobs/<id>/` (routed to `private/applications/` when overlay present).

# Typical contents

| File | Purpose |
|------|---------|
| `jd.txt` | Saved job description |
| `job_info.py` | Company, role, URL, keywords |
| `{id}_resume.pdf` / `{id}_cover_letter.pdf` | Upload deliverables |
| `{id}_resume.tex` / `{id}_cover_letter.tex` | Kept for manual recompile |
| `{id}_resume.py` / `{id}_cover_letter.py` | Sources for re-edit / rebuild |
| `{id}_resume (n).*` / `{id}_cover_letter (n).*` | Extra copies from a re-bundle (never overwrites) |
| `networking.md` | Outreach drafts + contacts (never auto-sent) |
| `research.md` | Optional company brief |
| `audit.md` | Optional pre-submit critique |

Finalized by `scripts/bundle.py` after `scripts/build.py --bundle`.
