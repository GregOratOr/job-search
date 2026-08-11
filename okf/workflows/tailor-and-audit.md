---
type: Playbook
title: Tailor and audit
description: Generate tailored documents, build PDFs, audit before submit.
tags: [workflow, tailor, audit]
timestamp: 2026-08-09T00:00:00Z
---

# Generate

```bash
uv run scripts/ai_tailor.py --jd jd.txt --id <id>
uv run scripts/ai_tailor.py --url "<posting>" --id <id> --use-project-web
# or manual scaffold:
uv run scripts/new_application.py --id <id> --company <co> --role "<role>"
```

Writes `resume/outputs/<id>.py` and `coverletter/outputs/<id>_cl.py` (plus bundle
scaffold under `applications/jobs/<id>/`).

# Build

```bash
uv run scripts/build.py --id <id> --pdf
# or compile + finalize upload folder:
uv run scripts/build.py --id <id> --bundle
```

# Audit (before submit)

```bash
uv run scripts/audit.py --id <id>
```

Read `applications/jobs/<id>/audit.md`. Fix 🔴 items in the outputs sources only —
`resume/outputs/<id>.py` / `coverletter/outputs/<id>_cl.py` — never edit
[profile](/okf/glossary/profile.md). Rebuild and re-audit.

# Bundle

```bash
uv run scripts/bundle.py --id <id>
```

Moves deliverables into `applications/jobs/<id>/` as `{id}_resume.*` /
`{id}_cover_letter.*`.

# Related

- [tailor-resume skill](/skills/tailor-resume/SKILL.md)
- [tailor-coverletter skill](/skills/tailor-coverletter/SKILL.md)
- [audit-application skill](/skills/audit-application/SKILL.md)
- [ai_tailor.py](/okf/scripts/ai-tailor.md)
- [audit.py](/okf/scripts/audit.md)
- [data_paths.py](/okf/scripts/data-paths.md)
