---
name: follow-up
description: Find applications that are due for a follow-up and draft follow-up messages into their networking files. Use when the user asks what needs following up, or wants follow-up messages drafted for stale applications.
---

# Follow Up on Applications

`scripts/followup.py` reads `applications/tracker.csv`, finds apps still in an active
stage (`Applied` through `Onsite`) older than `networking.follow_up_delay_days`, and
drafts a follow-up message into each `applications/jobs/<id>/networking.md`.
`Saved`, `Offer`, and terminal statuses (`Accepted` / `Rejected` / `Withdrawn`) are skipped.

## ⛔ Drafts only
This tool never sends anything. It writes a `## Follow-up (drafted ...)` section for you to
review and send manually.

## Steps
1. See what's due (no drafting):
   `uv run scripts/followup.py --list-only`
2. Draft follow-ups for everything due:
   `uv run scripts/followup.py`
3. Override the age threshold or target one app:
   `uv run scripts/followup.py --days 10`
   `uv run scripts/followup.py --id google_swe_2026`
4. Model overrides: `--model <name>` pins the drafting model; `--use-agent` lets
   `LLM_MODEL_FOLLOWUP` from `.env` apply (per-task pin).

## Pitfalls
- Only considers active stages `Applied` → `Onsite`. Advance status with `track-application`
  when you hear back (or set `Offer` / terminal) so they drop off the list.
- Uses the configured LLM to draft (grounds the fit reason in `jd.txt` when present);
  if the LLM is unavailable, a plain template is written instead.
