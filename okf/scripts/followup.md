---
type: CLI Tool
title: followup.py
description: Surface stale applications and draft follow-up messages; never sends.
tags: [script, networking, followup]
timestamp: 2026-07-05T00:00:00Z
resource: scripts/followup.py
---

```bash
uv run scripts/followup.py --list-only
uv run scripts/followup.py --id <id>
uv run scripts/followup.py --days 10               # override the age threshold
uv run scripts/followup.py --model <name>          # pin the drafting model
uv run scripts/followup.py --use-agent             # allow LLM_MODEL_FOLLOWUP per-task pin
```
