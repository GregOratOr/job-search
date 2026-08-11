---
type: Reference
title: Private overlay
description: The optional private/ git submodule overlays all sensitive data paths when present.
tags: [architecture, data, private]
timestamp: 2026-07-05T00:00:00Z
resource: scripts/data_paths.py
---

# Behavior

When `private/profile/` exists, `scripts/data_paths.py` routes reads and writes to:

- `private/profile/`
- `private/resume/`, `private/coverletter/`
- `private/applications/`
- `private/config/`
- `private/networking/`
- `private/.env` (loaded first)

Public repo directories remain templates for contributors without the submodule.

Per-job document stems (under `{resume,coverletter}/outputs/`): resume `{id}.*`,
cover letter `{id}_cl.*`. See [data_paths.py](/okf/scripts/data-paths.md).

# Validation

After cloning the submodule:

```bash
uv run scripts/validate_profile.py --inventory
```

# Related

- [Profile](/okf/glossary/profile.md)

# Citations

[1] [README private overlay section](/README.md)
