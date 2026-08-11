---
type: CLI Tool
title: data_paths.py
description: Private overlay routing plus per-job document path helpers (resume `{id}` / cover letter `{id}_cl`).
tags: [script, data, private]
timestamp: 2026-08-09T00:00:00Z
resource: scripts/data_paths.py
---

# Overlay

See [private overlay](/okf/architecture/private-overlay.md).

| Helper | Role |
|--------|------|
| `uses_private_data()` | True when `private/profile/` exists (or forced) |
| `configure_overlay(private=…)` / `bootstrap_paths(args)` | Force `--private` / `--public` / auto |
| `data_path(*parts)` | Canonical **write** path (always under `private/` when overlay on) |
| `resolve_path(*parts)` | **Read** preference: private file if present, else public template |
| `resolve_env_file()` | Prefer `private/.env`, then root `.env` |
| `rel_to_root(path)` | Path string for generated `OUTPUT_FILE` values |

Shared CLI: `add_overlay_cli_flags(parser)` → `--private` / `--public`.

# Per-job document naming

| Kind | Stem | Example |
|------|------|---------|
| Resume | `{id}` | `resume/outputs/acme_ml_2026.py` |
| Cover letter | `{id}_cl` | `coverletter/outputs/acme_ml_2026_cl.py` |

Helpers:

- `document_stem(kind, job_id)` / `job_id_from_document_stem(kind, stem)`
- `document_py` / `document_tex` / `document_pdf` — overlay-aware `outputs/` paths
- `template_path(kind)` — `{kind}/tailoring/_template.py`
- `resolve_document_py` — finds source with fallbacks:
  1. Current stem (`{id}.py` / `{id}_cl.py`)
  2. Cover letter only: pre-`_cl` `outputs/{id}.py`
  3. Legacy `tailoring/{id}.py`
- `resolve_document_paths` → `(source_py, tex_out)`

After [bundle.py](/okf/scripts/bundle.md), deliverables in the job folder are renamed to
`{id}_resume.*` / `{id}_cover_letter.*` (independent of the `outputs/` stems).
