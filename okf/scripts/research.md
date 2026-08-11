---
type: CLI Tool
title: research.py
description: Split research Tools — gather (opt-in web), synthesize (LLM), research (batch).
tags: [script, research, web]
timestamp: 2026-07-05T00:00:00Z
resource: scripts/research.py
---

# API (ADR 0004)

- `gather(topic, *, use_project_web=True)` — search/fetch via [web.py](/okf/scripts/web.md); **opt-in**; returns `(sources, failures)`
- `synthesize(topic, focus, sources, model)` — LLM brief; **no web**
- `research(...)` — unattended batch gather → synthesize (`use_project_web` required)
- `write_brief(brief, *, job_id=, out=)` — write to `--out` and/or bundle `research.md` (both when both set)

# CLI

```bash
# Unattended (project web)
uv run scripts/research.py "NVIDIA inference org" --id nvidia_ml_2026 --use-project-web

# Agent gathered sources already
uv run scripts/research.py --synthesize-from sources.json --topic "NVIDIA" --id nvidia_ml_2026
```

Other flags: `--topic`, `--max`, `--model`, `--use-agent`, `--out`.

Agents with harness-native web: follow [research skill](/skills/research/SKILL.md); do not call
`gather`/`research` without `--use-project-web`.
