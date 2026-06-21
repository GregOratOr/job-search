# Applications Context

## Files

```
applications/
├── tracker.csv          # Master application log — updated by scripts/track.py
├── schema.md            # Column definitions and valid values
└── jobs/
    ├── _template/       # Template job bundle (auto-copied by new_application.py)
    │   └── job_info.py
    └── {id}/
        └── job_info.py  # Per-job metadata, keywords, networking targets
```

## Common Commands

```bash
# Log a new application
python scripts/track.py log --id google_swe_2026 --platform LinkedIn --url https://...

# Update status after a phone screen
python scripts/track.py update --id google_swe_2026 --status "Phone Screen" \
    --notes "Scheduled Jan 15 10am PST with recruiter Jane Doe"

# View all applications
python scripts/track.py list

# View applications in a specific stage
python scripts/track.py list --status "Technical Interview"

# Inspect one application
python scripts/track.py show --id google_swe_2026
```

## Status Progression

```
Saved → Applied → Recruiter Screen → Phone Screen →
Technical Interview → Onsite → Offer → Accepted | Rejected | Withdrawn
```

## Job Info Files

Each `applications/jobs/{id}/job_info.py` stores:
- Posting URL, platform, external req ID
- Keywords extracted from the job description (used to align resume bullets)
- Networking targets (people to reach out to at the company)
- Interview prep notes as they accumulate

The `scripts/track.py log` command automatically reads `COMPANY`, `ROLE`,
`PLATFORM`, and `URL` from `job_info.py` if the file exists, so you don't
have to pass them as CLI flags.

## Tracker CSV Tips

- Do not edit `tracker.csv` manually unless correcting a mistake.
- To re-open a rejected application (e.g. reapplied later): create a new ID
  like `google_swe_2026_v2` rather than editing the original row.
- For a Notion Kanban view, see the "Notion Mirror" section in `schema.md`.
