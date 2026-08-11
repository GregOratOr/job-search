---
type: Reference
title: Autonomy ceiling
description: Automation never submits applications or sends messages; maximum action is Saved + prepared bundle.
tags: [architecture, safety, adr]
timestamp: 2026-07-05T00:00:00Z
resource: docs/adr/0002-autonomy-ceiling.md
---

# Saved ceiling

Regardless of `autonomy_level` (`discover_only`, `tailor`, `full_bundle`), the pipeline:

- **Never** submits an application to a job site.
- **Never** sends LinkedIn or email messages.
- **May** prepare the [bundle](/okf/glossary/bundle.md) and log status `Saved` in `tracker.csv`.

The user uploads PDFs and sends outreach manually.

# autonomy_level steps

| Level | Automated steps |
|-------|-----------------|
| `discover_only` | discover (shortlist only; no application files) |
| `tailor` | discover, tailor, track(Saved) |
| `full_bundle` | discover, tailor, research, build, audit, bundle, track(Saved) |

CLI shorthand `--build` (without `--level`): discover, tailor, build, bundle, track
(skips research + audit).

# Citations

[1] [ADR 0002](/docs/adr/0002-autonomy-ceiling.md)
