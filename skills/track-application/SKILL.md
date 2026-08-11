---
name: track-application
description: Log and update job applications in applications/tracker.csv. Use when the user applies to a job, wants to update an application's status, or asks to list/show tracked applications.
---

# Track Applications

## Steps
- Log a new application (auto-fills company/role/platform/url from
  `applications/jobs/<id>/job_info.py` if present):
  `uv run scripts/track.py log --id <id> --platform <p> --url <url>`
- Update status/notes:
  `uv run scripts/track.py update --id <id> --status "Phone Screen" --notes "..."`
- List all / filter:
  `uv run scripts/track.py list` · `uv run scripts/track.py list --status Applied`
- Inspect one: `uv run scripts/track.py show --id <id>`

## Valid statuses (in order)
Saved → Applied → Recruiter Screen → Phone Screen → Technical Interview → Onsite →
Offer → Accepted | Rejected | Withdrawn

## Pipeline interaction
The orchestrator (`run-pipeline` skill) logs new applications as `Saved` automatically — it
never advances past `Saved`. After you actually upload the application yourself, set it to
`Applied`: `uv run scripts/track.py update --id <id> --status Applied`.

## Pitfalls
- `log` fails if the id already exists — use `update` instead.
- Don't hand-edit `tracker.csv`; go through `track.py`.