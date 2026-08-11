---
type: CLI Tool
title: text_utils.py
description: Shared text helpers for LaTeX-aware processing.
tags: [script, utility]
timestamp: 2026-07-09T00:00:00Z
resource: scripts/text_utils.py
---

# API

- `strip_latex(text)` — remove `\textbf{}`, `\texttimes{}`, etc. for plain-text LLM prompts

Used by [ai_tailor.py](/okf/scripts/ai-tailor.md) and [audit.py](/okf/scripts/audit.md).
