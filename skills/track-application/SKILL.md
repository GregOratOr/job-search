---
name: track-application
description: Log and update job applications in applications/tracker.csv. Use when the user applies to a job, wants to update an application's status, or asks to list/show tracked applications.
---

# Track Applications

## Steps
- Log a new application (auto-fills company/role/platform/url from
  `applications/jobs/<id>/job_info.py` if present):
  `python scripts/track.py log --id <id> --platform <p> --url <url>`
- Update status/notes:
  `python scripts/track.py update --id <id> --status "Phone Screen" --notes "..."`
- List all / filter:
  `python scripts/track.py list` · `python scripts/track.py list --status Applied`
- Inspect one: `python scripts/track.py show --id <id>`

## Valid statuses (in order)
Saved → Applied → Recruiter Screen → Phone Screen → Technical Interview → Onsite →
Offer → Accepted | Rejected | Withdrawn

## Pitfalls
- `log` fails if the id already exists — use `update` instead.
- Don't hand-edit `tracker.csv`; go through `track.py`.
