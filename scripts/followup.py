#!/usr/bin/env -S uv run
"""
scripts/followup.py
-------------------
Surface applications that are due for a follow-up and draft follow-up messages.

"Due" = status still in {Applied, Recruiter Screen, Phone Screen, Technical Interview,
Onsite} and the last update is older than networking.follow_up_delay_days
(config/job_search_config.yaml; default 7). Saved / Offer / terminal statuses are skipped.

Drafted messages are appended to each application's networking.md under a
"Follow-up (drafted ...)" section. This tool NEVER sends anything — it only
drafts (see docs/adr/0002-autonomy-ceiling.md).

Usage:
    uv run scripts/followup.py                 # list due + draft messages
    uv run scripts/followup.py --list-only     # just show what's due
    uv run scripts/followup.py --days 10       # override the threshold
    uv run scripts/followup.py --id google_swe_2026   # draft for one app
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import yaml

from scripts.data_paths import apply_private_overlay, data_path, resolve_path
from scripts.llm_provider import complete, get_default_model, load_env
from scripts.track import _read_tracker

apply_private_overlay()
load_env()

_FOLLOWUP_STATUSES = {
    "applied",
    "recruiter screen",
    "phone screen",
    "technical interview",
    "onsite",
}


def _delay_days() -> int:
    cfg_path = resolve_path("config", "job_search_config.yaml")
    if cfg_path.exists():
        cfg = yaml.safe_load(cfg_path.read_text()) or {}
        return int(cfg.get("networking", {}).get("follow_up_delay_days", 7))
    return 7


def _age_days(row: dict) -> int | None:
    stamp = row.get("last_updated") or row.get("date_applied") or ""
    if not stamp:
        return None
    # Try ISO date/datetime first (the format track.py writes).
    # Fall back to a broader set of common formats so that manually edited
    # timestamps (e.g. "Jun 26 2026") don't silently swallow the row.
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%B %d, %Y", "%b %d, %Y",
                "%d/%m/%Y", "%m/%d/%Y"):
        try:
            d = datetime.strptime(stamp.strip(), fmt).date()
            return (date.today() - d).days
        except ValueError:
            continue
    # Last resort: try fromisoformat which handles datetime strings with offsets
    try:
        d = datetime.fromisoformat(stamp).date()
        return (date.today() - d).days
    except ValueError:
        return None


def due_rows(rows: list[dict], threshold: int, only_id: str | None) -> list[dict]:
    due = []
    for r in rows:
        if only_id and r.get("id") != only_id:
            continue
        if r.get("status", "").strip().lower() not in _FOLLOWUP_STATUSES:
            continue
        age = _age_days(r)
        if age is None:
            continue
        if only_id or age >= threshold:
            r = {**r, "_age": age}
            due.append(r)
    return due


def _jd_snippet(job_id: str, max_chars: int = 1500) -> str:
    """Return a short JD excerpt for drafting context, or empty if missing."""
    if not job_id:
        return ""
    path = data_path("applications", "jobs", job_id, "jd.txt")
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return ""
    if len(text) > max_chars:
        return text[:max_chars].rstrip() + "\n…"
    return text


def draft_message(row: dict, model: str) -> str:
    company = row.get("company", "the company")
    role    = row.get("role", "the role")
    age     = row.get("_age", "?")
    job_id  = row.get("id", "")
    jd      = _jd_snippet(job_id)
    system = ("You write brief, warm, professional follow-up notes for job applications. "
              "No fluff, no pressure, 90-130 words. Plain text. "
              "If a job-description excerpt is provided, ground the fit reason in it — "
              "do not invent requirements that are not there.")
    jd_block = (
        f"\n\nJob description excerpt (use for a concrete fit reason):\n{jd}"
        if jd else
        "\n\n(No job description on file — keep the fit reason high-level and honest.)"
    )
    user = (f"Draft a follow-up message for an application submitted ~{age} days ago for the "
            f"{role} role at {company}. Reiterate genuine interest, add one concrete reason "
            f"the candidate is a fit, and politely ask about next steps. Sign off as the "
            f"candidate (leave the name as [Your Name]).{jd_block}")
    try:
        return complete(system, user, model, max_tokens=400).strip()
    except Exception as e:  # noqa: BLE001 — fall back to a template if the model is down
        return (f"Hi [Name],\n\nI wanted to follow up on my application for the {role} role at "
                f"{company}, submitted about {age} days ago. I remain very interested and would "
                f"love to learn about next steps. Happy to share anything that would help.\n\n"
                f"Thank you for your time,\n[Your Name]\n\n_(template fallback: {e})_")


def _append_followup(job_id: str, message: str) -> Path:
    path = data_path("applications", "jobs", job_id, "networking.md")
    path.parent.mkdir(parents=True, exist_ok=True)
    section = (f"## Follow-up (drafted {date.today().isoformat()})\n"
               f"*Review and send manually — this was not sent.*\n\n> "
               + message.replace("\n", "\n> ") + "\n")
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    path.write_text((existing.rstrip() + "\n\n" + section) if existing.strip() else section,
                    encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Surface + draft application follow-ups.")
    parser.add_argument("--days", type=int, default=None, help="Override follow-up threshold (days)")
    parser.add_argument("--id", default=None, help="Only this application id")
    parser.add_argument("--list-only", action="store_true", help="List due apps; draft nothing")
    parser.add_argument("--model", default=None, help="Model override")
    parser.add_argument("--use-agent", action="store_true",
                        help="Use the task-specific model from .env for this run instead of the base model.")
    args = parser.parse_args()

    threshold = args.days if args.days is not None else _delay_days()
    rows = _read_tracker()
    if not rows:
        print("No applications tracked yet.")
        return

    due = due_rows(rows, threshold, args.id)
    if not due:
        print(f"No applications due for follow-up (threshold: {threshold} days).")
        return

    print(f"\n  {len(due)} application(s) due for follow-up (>= {threshold} days, "
          f"status Applied→Onsite):\n")
    for r in due:
        print(f"  - {r['id']:<32} {r.get('company',''):<18} {r.get('status',''):<10} {r['_age']}d")

    if args.list_only:
        return

    model = args.model or get_default_model(task="followup", use_task_model=args.use_agent)
    print()
    for r in due:
        msg = draft_message(r, model)
        path = _append_followup(r["id"], msg)
        print(f"  [+] drafted follow-up for {r['id']} -> {path}")

    print("\n  Drafts written. Review each networking.md and send manually.")


if __name__ == "__main__":
    main()