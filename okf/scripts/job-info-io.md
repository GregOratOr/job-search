---
type: CLI Tool
title: job_info_io.py
description: Safe read/write helpers for applications/jobs/<id>/job_info.py field updates.
tags: [script, applications, io]
timestamp: 2026-07-09T00:00:00Z
resource: scripts/job_info_io.py
---

# Purpose

Whitespace-tolerant regex patching for `job_info.py` string fields (`URL`, `PLATFORM`, etc.).
Uses `repr()` for values so URLs with quotes do not corrupt the file.

# API

```python
from scripts.job_info_io import set_job_info_fields, load_job_info

set_job_info_fields("nvidia_ml_2026", url="https://careers.example.com/job/1")
info = load_job_info("nvidia_ml_2026")
```

# Consumers

- `ai_tailor.py` — sets `URL` at generation time when `--url` is passed
- `track.py` / `pipeline.py` — read metadata via `load_job_info`
