---
type: CLI Tool
title: build.py
description: Render resume and cover letter .tex from outputs/ sources; optional PDF compile and bundle.
tags: [script, latex, build]
timestamp: 2026-08-09T00:00:00Z
resource: scripts/build.py
---

# Sources

Paths via [data_paths.py](/okf/scripts/data-paths.md):

- Resume: `resume/outputs/<id>.{py,tex,pdf}`
- Cover letter: `coverletter/outputs/<id>_cl.{py,tex,pdf}`

Templates stay in `{resume,coverletter}/tailoring/_template.py`.

# Examples

```bash
uv run scripts/build.py --id <id>
uv run scripts/build.py --id <id> --only resume        # or --only coverletter
uv run scripts/build.py --id <id> --pdf
uv run scripts/build.py --id <id> --bundle             # implies --pdf + finalize
uv run scripts/build.py --id <id> --private --pdf      # force private/ (--public for repo root)
```

`--pdf` / `--bundle` require `pdflatex` on PATH (TeX Live or MiKTeX). If missing,
`build.py` exits with an install hint instead of a raw `FileNotFoundError`.

See also [bundle.py](/okf/scripts/bundle.md) and [build-documents skill](/skills/build-documents/SKILL.md).
