---
type: CLI Tool
title: audit.py
description: Hiring-manager critique of tailored resume and cover letter; writes audit.md.
tags: [script, audit, quality]
timestamp: 2026-07-05T00:00:00Z
resource: scripts/audit.py
---

# Phases

1. Resume audit (ATS readiness 0–100, bullets, summary)
2. Cover letter audit (CL-only JD fit 0–100)
3. Factual accuracy vs profile ground truth
4. Prioritized action plan — overall compatibility (0–100) + ATS readiness (0–100),
   then must-fix / high-impact / nice-to-have

# Examples

```bash
uv run scripts/audit.py --id <id>
uv run scripts/audit.py --id <id> --out notes/audit.md   # also copies to --out
uv run scripts/audit.py --id <id> --provider anthropic --model claude-opus-4-7
uv run scripts/audit.py --id <id> --use-agent            # allow LLM_MODEL_AUDIT
```

Reads `resume/outputs/<id>.py` and `coverletter/outputs/<id>_cl.py` (legacy paths still
resolved via [data_paths.py](/okf/scripts/data-paths.md)).

# Output

`applications/jobs/<id>/audit.md` — advisory only; never edits profile or source files.
Re-runs append (prior reports kept, separated by `---`). Fix 🔴 items in those outputs
files, then rebuild and re-audit.

# Pipeline integration

Runs as the `audit` step in [pipeline.py](/okf/scripts/pipeline.md) at `full_bundle` level
(after `build`, before `bundle`), and independently via `scripts/audit.py --id <id>` or
`pipeline.py --id <id> --steps audit`. Model: `--model`, or `LLM_MODEL_AUDIT` only with
`--use-agent`, else `LLM_MODEL` / provider default.

# Related

- [Tailor and audit workflow](/okf/workflows/tailor-and-audit.md)
- [audit-application skill](/skills/audit-application/SKILL.md)
