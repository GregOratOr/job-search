---
type: CLI Tool
title: new_application.py
description: Scaffold per-job resume/cover-letter sources and job_info without AI tailoring.
tags: [script, scaffold]
timestamp: 2026-08-09T00:00:00Z
resource: scripts/new_application.py
---

```bash
uv run scripts/new_application.py --id <id> --company <co> --role "<role>"
uv run scripts/new_application.py --id <id> --company <co> --role "<role>" --force
uv run scripts/new_application.py --id <id> --company <co> --role "<role>" --private
```

Creates (overlay-aware via [data_paths.py](/okf/scripts/data-paths.md)):

- `resume/outputs/<id>.py`
- `coverletter/outputs/<id>_cl.py`
- `applications/jobs/<id>/job_info.py`

Templates: `{resume,coverletter}/tailoring/_template.py` and
`applications/jobs/_template/job_info.py`.

For AI-filled sources use [ai_tailor.py](/okf/scripts/ai-tailor.md). Agent orchestration:
[new-application skill](/skills/new-application/SKILL.md).
