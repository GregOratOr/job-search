---
type: CLI Tool
title: json_llm.py
description: Shared JSON extraction and retry logic for LLM completions.
tags: [script, llm, utility]
timestamp: 2026-07-09T00:00:00Z
resource: scripts/json_llm.py
---

# API

- `parse_json(text)` — strip fences, parse JSON (raises on failure)
- `repair_json(text)` — fix common LLM JSON mistakes (trailing commas)
- `call_json(system, user, model, *, required_keys=...)` — `complete()` + parse with one retry

Used by [ai_tailor.py](/okf/scripts/ai-tailor.md) and [job_discovery.py](/okf/scripts/job-discovery.md).
