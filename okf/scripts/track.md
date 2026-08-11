---
type: CLI Tool
title: track.py
description: Log and update applications in tracker.csv; programmatic log_saved() for orchestrators.
tags: [script, tracker]
timestamp: 2026-07-09T00:00:00Z
resource: scripts/track.py
---

# CLI

```bash
uv run scripts/track.py log --id <id> --platform LinkedIn --url <url>
uv run scripts/track.py update --id <id> --status "Phone Screen"
uv run scripts/track.py list
```

# Programmatic API

`log_saved(job_id, *, url=..., company=..., role=..., platform=..., status="Saved")` — used by
[pipeline.py](/okf/scripts/pipeline.md) after tailoring. Returns `False` if the id already exists.
Reads defaults from `applications/jobs/<id>/job_info.py` via [job_info_io.py](/okf/scripts/job-info-io.md).

Status flow: `Saved → Applied → ... → Accepted | Rejected | Withdrawn`
