---
type: CLI Tool
title: ai_tailor.py
description: Four-phase LLM pipeline from JD to tailored resume, cover letter, outreach, and bundle scaffold.
tags: [script, tailor, llm]
timestamp: 2026-07-05T00:00:00Z
resource: scripts/ai_tailor.py
---

# Phases

1. Parse JD
2. Match profile entries + rewrite bullets
3. Write cover letter
4. Write outreach messages

# Examples

```bash
uv run scripts/ai_tailor.py --jd jd.txt --id <id>
uv run scripts/ai_tailor.py --url "<posting>" --id <id> --use-project-web
uv run scripts/ai_tailor.py --jd jd.txt --id <id> --provider anthropic --model claude-opus-4-7
```

When `--url` is passed, the posting URL is written into `job_info.py` (`URL` field)
and `--use-project-web` is required (ADR 0004). Education entries in generated resume
files are discovered dynamically from `profile.education`.

# Outputs

- `resume/outputs/<id>.py` / `coverletter/outputs/<id>_cl.py` — latest; prior runs archived
  with the same stem (`<id> (1).*` for resume, `<id>_cl (1).*` for cover letter, then `(2)`, …)
- `applications/jobs/<id>/` — `jd.txt`, `job_info.py` overwritten; `networking.md` replaces
  same outreach sections and **appends** new blocks (Contacts, follow-up drafts, user Notes)

Outreach priority targets include alumni from `networking.alumni_networks` in
`config/job_search_config.yaml` (overlay-aware) when that list is non-empty.
