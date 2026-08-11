---
type: CLI Tool
title: bundle.py
description: Move compiled PDFs and .tex into applications/jobs/id/ upload folder.
tags: [script, bundle]
timestamp: 2026-07-05T00:00:00Z
resource: scripts/bundle.py
---

```bash
uv run scripts/bundle.py --id <id>
uv run scripts/bundle.py --id <id> --keep-temp    # keep LaTeX temp artifacts
uv run scripts/bundle.py --id <id> --private      # force private/ paths (--public forces repo root)
```

Moves `resume/outputs/<id>.{py,tex,pdf}` and `coverletter/outputs/<id>_cl.{py,tex,pdf}`
into `applications/jobs/<id>/` as `{id}_resume.*` / `{id}_cover_letter.*`, then cleans
LaTeX temp artifacts. Re-runs that would collide write `{id}_resume (1).*` (then `(2)`, …)
instead of overwriting. Paths are overlay-aware (`private/` when present).
