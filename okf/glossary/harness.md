---
type: Glossary Term
title: Harness
description: The runtime pairing a model with callable tools that drives the conversation loop.
tags: [glossary, harness]
timestamp: 2026-07-05T00:00:00Z
---

The harness — not any single model — is the "brain" that reads [skills](/okf/glossary/skill.md)
and invokes [tools](/okf/glossary/tool.md). Examples: Hermes, Cursor, Claude Code, VS Code chat,
plain terminal.

The project is harness-agnostic: switching harnesses is a runtime choice, not a code change.

See [CONTEXT.md](/CONTEXT.md) and [harness-agnostic design](/okf/architecture/harness-agnostic-design.md).
