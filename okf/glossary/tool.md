---
type: Glossary Term
title: Tool
description: A callable CLI script under scripts/ that performs real work.
tags: [glossary, tool]
timestamp: 2026-07-05T00:00:00Z
---

Tools live under `scripts/*.py` and are invoked with `uv run scripts/<name>.py`. The harness
or user runs them from a shell; they are not embedded in the harness runtime.

Index: [scripts index](/okf/scripts/index.md).

Web fallback tool: [scripts/web.py](/okf/scripts/web.md).
