# Application Tracker Schema

`applications/tracker.csv` — master log of all job applications.
Updated automatically by `scripts/track.py`. Do not edit manually unless correcting data.

## Columns

| Column          | Type     | Description                                                       | Example                          |
|-----------------|----------|-------------------------------------------------------------------|----------------------------------|
| `id`            | string   | Unique application ID — matches tailoring file names              | `google_swe_2026`                |
| `company`       | string   | Company name                                                      | `Google`                         |
| `role`          | string   | Job title as listed in the posting                                | `Software Engineer, ML`          |
| `platform`      | string   | Where you applied (see valid values below)                        | `LinkedIn`                       |
| `url`           | string   | Direct link to the job posting                                    | `https://careers.google.com/...` |
| `date_applied`  | date     | ISO 8601 date (YYYY-MM-DD)                                        | `2026-06-09`                     |
| `status`        | string   | Current status (see STATUS_VALUES below)                          | `Phone Screen`                   |
| `last_updated`  | date     | ISO 8601 date of last status change                               | `2026-06-15`                     |
| `recruiter`     | string   | Recruiter name if known                                           | `Jane Doe`                       |
| `resume_version`| string   | Which tailoring file was used (usually same as `id`)              | `google_swe_2026`                |
| `notes`         | string   | Free-text notes: referral, interview date, key contact, etc.      | `Referred by John`               |

## STATUS_VALUES (ordered progression)

```
Saved            → Bookmarked; not yet applied
Applied          → Submitted application
Recruiter Screen → HR/recruiter phone screen scheduled/completed
Phone Screen     → Technical phone screen
Technical Interview → Live coding / system design round
Onsite           → Final round (in-person or virtual full day)
Offer            → Received written offer
Accepted         → Offer accepted ✓
Rejected         → Application rejected at any stage
Withdrawn        → You withdrew from the process
```

## Valid Platform Values

```
LinkedIn
Indeed
Company Website
Referral
Handshake
AngelList / Wellfound
BuiltIn
Glassdoor
Email / Direct
Other
```

## Adding New Status Values

1. Add the new value to `STATUS_VALUES` list in `scripts/track.py`
2. Add it to this doc
3. If you use a Notion mirror, add the new option to the Status property there

## Notion Mirror (optional)

If you prefer a visual Kanban board, mirror this CSV in Notion:
- Create a database with the same columns
- Status column = **Select** type with the STATUS_VALUES above
- Use a **Board view** grouped by Status for a Kanban layout
- Sync manually weekly: copy rows from tracker.csv into Notion
- Or use Zapier/Make to auto-sync (trigger: file change in Dropbox/Google Drive → Notion row)
