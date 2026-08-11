---
type: Audit Report
title: Codebase discontinuities
description: Known weaknesses and resolved gaps; refreshed 2026-08-09 after docs/code sync.
tags: [audit, technical-debt, documentation]
timestamp: 2026-08-09T00:00:00Z
---

# Summary

Structurally sound: harness-agnostic toolbox, Saved ceiling (ADR 0002), private overlay,
skills-orchestrate / tools-process (ADR 0004), project web opt-in via `--use-project-web`,
explicit `WEB_BACKEND`, cover-letter `{id}_cl` naming via `document_stem`.

# Resolved (historical + 2026-08)

| Issue | Resolution |
|-------|------------|
| Docs forced `scripts/web.py` in harness sessions | Web access policy + skills: harness-native first |
| Dual web gates (`--search-mode` + backends) | **SA-13:** `--search-mode` retired; `WEB_BACKEND` + `--use-project-web` only; Anthropic-native discovery removed |
| Dual orchestrators / deprecated `job_discovery` CLI | **CLI removed** — `job_discovery.py` is library-only; scripted entry is `pipeline.py` |
| Discovery ignored `search_terms` in config | Queries + rank prompt use `must_include` / nice / exclude / avoid roles |
| `audit-application` missing from indexes | Added to AGENTS / README / skills |
| Hardcoded model defaults | `.env`-only resolution; `--use-agent` for per-task models |
| Harness mode was prompt-only | `WEB_BACKEND=harness` + `HARNESS_WEB_*_CMD` adapters |
| Brittle `job_info` URL patching | `scripts/job_info_io.py` |
| Phase B consolidations | `web.fetch`, `track.log_saved`, `json_llm`, `text_utils`, `append_contacts_for_job`, `bootstrap` |
| Silent SearXNG default | `resolve_backend()` requires explicit `WEB_BACKEND` |
| Cover letter / resume same basename | `document_stem`: resume `{id}`, cover letter `{id}_cl`; bundle still `{id}_resume` / `{id}_cover_letter` |
| Broken `update_profile.py` alias | `sys.path` bootstrap; prefer `validate_profile.py` |
| Agent discovery vs scripted pipeline confusion | `discover-jobs` → shortlist + `shortlists.md`; pipeline is batch fallback |

# Open gaps

## 1. Script layer cannot auto-detect harness-native web

Scripted Tools still need explicit `--use-project-web` (or agent-written artifacts). There is
no runtime “does Cursor have browser MCP?” probe. Mitigation: skills prefer harness-native
paths; batch pipeline is for unattended runs only (ADR 0004).

**Severity:** Low — by design.

## 2. Public vs private template drift

Public `profile/` holds examples; real data in `private/`. Contributors without the submodule
see placeholders. Mitigation: `validate_profile.py --inventory`.

**Severity:** Medium for new contributors.

## 3. Optional future knobs

- `automation.run_audit: false` if audit tokens are costly at `full_bundle`
- Secondary roles / tier_3 companies in discovery query builder (currently primary + tier_1/2)
- **`config/platforms.yaml`** — [platform playbook](/okf/glossary/platform-playbook.md).
  Agent discovery consumes search filters / career URLs / notes via `discover-jobs`;
  `application_steps` remain human/post-shortlist checklists. Still not imported by Python
  scripts (deferred until a discover-jobs rework wires them).

# Citations

[1] [Web access policy](/okf/architecture/web-access-policy.md)
[2] [ADR 0004](/docs/adr/0004-skills-orchestrate-tools-process.md)
[3] [plans/README.md](/plans/README.md) (SA-13)
[4] [data_paths.py](/okf/scripts/data-paths.md)
