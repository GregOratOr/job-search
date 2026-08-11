---
type: CLI Tool
title: pipeline.py
description: E2E orchestrator chaining discover, tailor, research, build, audit, bundle, track.
tags: [script, pipeline, orchestrator]
timestamp: 2026-08-05T00:00:00Z
resource: scripts/pipeline.py
---

# Examples

```bash
uv run scripts/pipeline.py --use-project-web
uv run scripts/pipeline.py --level tailor --max 3 --use-project-web
uv run scripts/pipeline.py --dry-run --max 5 --use-project-web
uv run scripts/pipeline.py --build --max 5 --find-contacts --use-project-web
uv run scripts/pipeline.py --url "<url>" --id <id> --use-project-web
uv run scripts/pipeline.py --jd jd.txt --id <id>
uv run scripts/pipeline.py --id <id> --steps audit
uv run scripts/pipeline.py --gate --use-project-web
```

# Shorthand flags

- `--dry-run` — discover only (`discover_only`; no application files)
- `--build` — discover → tailor → build → bundle → track (no research/audit)
- `--find-contacts` — after each job’s steps, append contacts to `networking.md` (opt-in; soft-fail)
- `--use-project-web` — opt in to `scripts/web.py` (required for discovery/fetch/research/page-scan contacts)
- `--gate` — confirm before each **per-job** step (not before discovery)

Successful tailor+track runs log **`Saved`** via [track.log_saved()](/okf/scripts/track.md).

# Web backend

Uses [web.py](/okf/scripts/web.md) when `--use-project-web` is set.
`WEB_BACKEND` must be set explicitly in `.env` (or optional `automation.web_backend` in
config if env is unset). There is no implicit SearXNG default.
`--search-mode` is retired (ignored with a deprecation notice).

Discovery library: [job_discovery.py](/okf/scripts/job-discovery.md) — no CLI.
Agent shortlists use `applications/shortlists.md` via [discover-jobs](/skills/discover-jobs/SKILL.md);
scripted `--dry-run` only prints to the terminal.

# Provider / models

`--provider anthropic|ollama|openai` sets `LLM_PROVIDER` for the run.
`--model` overrides all step models. Per-task `LLM_MODEL_*` only with `--use-agent`.

# Audit step

Included at `full_bundle` (after `build`, before `bundle`); writes advisory `audit.md`.
Also: [audit.py](/okf/scripts/audit.md) or `--steps audit`.

# Related

- [Pipeline workflow](/okf/workflows/pipeline.md)
- [run-pipeline skill](/skills/run-pipeline/SKILL.md)
