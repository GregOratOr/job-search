---
type: Playbook
title: End-to-end pipeline
description: Orchestrated discover → tailor → research → build → audit → bundle → track(Saved) flow.
tags: [workflow, pipeline]
timestamp: 2026-08-05T00:00:00Z
resource: scripts/pipeline.py
---

# Entry

```bash
uv run scripts/pipeline.py --use-project-web   # config autonomy_level + project web
uv run scripts/pipeline.py --level tailor --max 3 --use-project-web
uv run scripts/pipeline.py --url "<url>" --id <id> --use-project-web
uv run scripts/pipeline.py --jd jd.txt --id <id>   # local JD — no web flag
uv run scripts/pipeline.py --id <id> --steps build,bundle,track
uv run scripts/pipeline.py --id <id> --steps audit
uv run scripts/pipeline.py --gate --use-project-web   # pause before each per-job step
```

# Steps

`discover → tailor → research → build → audit → bundle → track`

Stopped by [autonomy_level](/okf/architecture/autonomy-ceiling.md):

| Level | Steps |
|-------|--------|
| `discover_only` / `--dry-run` | discover (shortlist only; no files) |
| `tailor` | discover, tailor, track |
| `full_bundle` | all seven steps |
| `--build` (no `--level`) | discover, tailor, build, bundle, track (skips research + audit) |

Hard ceiling: never auto-submit / auto-send; max = prepare bundle + log **Saved**.

# Web

Discovery/fetch/research/contacts need `--use-project-web`. Backend is `WEB_BACKEND` in `.env`
(or `automation.web_backend` if env unset). `--search-mode` is retired.
Agents with native web should prefer agent-driven [discovery](/okf/workflows/discovery.md).
Library: [job_discovery.py](/okf/scripts/job-discovery.md) (no CLI).

# Models

`--model` overrides all steps. Else each step: `LLM_MODEL_<TASK>` **only with** `--use-agent`
→ `LLM_MODEL` → provider var. See [llm_provider.py](/okf/scripts/llm-provider.md).

# Batch behavior

One bad job is skipped; the batch continues. `--find-contacts` is opt-in (soft-fail).

# After run

User uploads PDFs from [bundle](/okf/glossary/bundle.md), reviews `networking.md`, sends
outreach manually. Update tracker to `Applied` after submitting.

# Related

- [run-pipeline skill](/skills/run-pipeline/SKILL.md)
- [pipeline.py concept](/okf/scripts/pipeline.md)
