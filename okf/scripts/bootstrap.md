---
type: CLI Tool
title: bootstrap.py
description: One-call script initialization (ROOT, private overlay, .env).
tags: [script, utility]
timestamp: 2026-07-09T00:00:00Z
resource: scripts/bootstrap.py
---

# Usage

```python
from scripts.bootstrap import init_script

ROOT = init_script()
```

Replaces repeated `sys.path.insert`, `apply_private_overlay()`, and `load_env()` boilerplate.

# Consumers

Today: [track.py](/okf/scripts/track.md) only (auto-detect overlay; no `--private` / `--public`).

Scripts that need forced path mode still use `bootstrap_paths` / `configure_overlay` from
[data_paths.py](/okf/scripts/data-paths.md) after argparse (e.g. [bundle.py](/okf/scripts/bundle.md)).

# Future

Unify script startup control flow: extend `init_script(overlay=None | True | False)` and call it
**after** argparse so nearly every Tool shares one path+env bootstrap. See `plans/README.md` (SA-12).
