---
type: Reference
title: Harness-agnostic design
description: The project is a toolbox of CLI tools and portable skills, not a single hard-wired agent loop.
tags: [architecture, harness, adr]
timestamp: 2026-07-05T00:00:00Z
resource: docs/adr/0001-harness-agnostic-toolbox.md
---

# Summary

Capabilities are exposed as plain CLI **tools** under `scripts/` and described by portable
**skills** under `skills/`. Any shell-capable harness (Hermes, Cursor, Claude Code, plain
terminal) becomes the brain. LLM access stays behind `scripts/llm_provider.py`.

# Key properties

- No binding to one provider or runtime.
- State lives on disk in per-job [bundles](/okf/glossary/bundle.md), not in a long-running process.
- Weak local models are supported via explicit skills and tolerant script parsing.

# Related

- [Harness](/okf/glossary/harness.md)
- [Skill](/okf/glossary/skill.md)
- [Tool](/okf/glossary/tool.md)
- [Autonomy ceiling](/okf/architecture/autonomy-ceiling.md)

# Citations

[1] [ADR 0001](/docs/adr/0001-harness-agnostic-toolbox.md)
