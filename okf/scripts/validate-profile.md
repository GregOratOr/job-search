---
type: CLI Tool
title: validate_profile.py
description: Read-only profile health check — imports, inventory, changelog (does not edit profile/).
tags: [script, profile, validation]
timestamp: 2026-08-05T00:00:00Z
resource: scripts/validate_profile.py
---

```bash
uv run scripts/validate_profile.py --inventory
uv run scripts/validate_profile.py --validate
uv run scripts/validate_profile.py --changelog
```

Deprecated alias: `scripts/update_profile.py` (same CLI; prints a rename notice; requires
the same `sys.path` bootstrap as other scripts — prefer `validate_profile.py`).

Also lists per-job document sources under `resume/outputs/` and `coverletter/outputs/`
(cover letters as `<id>_cl.py`) and whether matching `.tex` files exist.

Editing profile files is a separate workflow — see [update-profile skill](/skills/update-profile/SKILL.md).
