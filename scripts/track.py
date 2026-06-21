#!/usr/bin/env python3
"""
scripts/track.py
----------------
Log, update, and query job applications in applications/tracker.csv.

Usage:
    # Log a new application
    python scripts/track.py log --id google_swe_2026 --platform LinkedIn --url https://...

    # Update status
    python scripts/track.py update --id google_swe_2026 --status "Phone Screen"

    # Show all applications
    python scripts/track.py list

    # Show a specific application
    python scripts/track.py show --id google_swe_2026

    # Show applications by status
    python scripts/track.py list --status Applied

Valid statuses (in order):
    Saved → Applied → Recruiter Screen → Phone Screen →
    Technical Interview → Onsite → Offer → Accepted | Rejected | Withdrawn
"""

import argparse
import csv
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from scripts.data_paths import apply_private_overlay, data_path, resolve_path

apply_private_overlay()
TRACKER_CSV = data_path("applications", "tracker.csv")

COLUMNS = [
    "id", "company", "role", "platform", "url",
    "date_applied", "status", "last_updated",
    "recruiter", "resume_version", "notes"
]

STATUS_VALUES = [
    "Saved",
    "Applied",
    "Recruiter Screen",
    "Phone Screen",
    "Technical Interview",
    "Onsite",
    "Offer",
    "Accepted",
    "Rejected",
    "Withdrawn",
]


def _read_tracker() -> list[dict]:
    if not TRACKER_CSV.exists():
        return []
    with open(TRACKER_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write_tracker(rows: list[dict]) -> None:
    TRACKER_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(TRACKER_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _job_info(job_id: str) -> dict:
    """Load job metadata from applications/jobs/{id}/job_info.py if available."""
    job_info_path = resolve_path("applications", "jobs", job_id, "job_info.py")
    if not job_info_path.exists():
        return {}
    import importlib.util
    spec   = importlib.util.spec_from_file_location("job_info", str(job_info_path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return {
        "company":  getattr(module, "COMPANY",  ""),
        "role":     getattr(module, "ROLE",     ""),
        "platform": getattr(module, "PLATFORM", ""),
        "url":      getattr(module, "URL",      ""),
        "recruiter": getattr(module, "RECRUITER", "") or "",
    }


# ──────────────────────────────────────────────────────────────────────────────
# COMMANDS
# ──────────────────────────────────────────────────────────────────────────────

def cmd_log(args) -> None:
    rows = _read_tracker()
    if any(r["id"] == args.id for r in rows):
        print(f"[!] ID '{args.id}' already exists. Use `update` to change it.")
        sys.exit(1)

    # Pre-fill from job_info.py if available
    info    = _job_info(args.id)
    today   = date.today().isoformat()
    status  = args.status or "Applied"

    if status not in STATUS_VALUES:
        print(f"[x] Invalid status '{status}'. Valid: {', '.join(STATUS_VALUES)}")
        sys.exit(1)

    row = {
        "id":             args.id,
        "company":        args.company or info.get("company", ""),
        "role":           args.role    or info.get("role",    ""),
        "platform":       args.platform or info.get("platform", ""),
        "url":            args.url      or info.get("url",      ""),
        "date_applied":   today,
        "status":         status,
        "last_updated":   today,
        "recruiter":      args.recruiter or info.get("recruiter", ""),
        "resume_version": args.resume_version or args.id,
        "notes":          args.notes or "",
    }

    rows.append(row)
    _write_tracker(rows)
    print(f"[+] Logged application: {args.id} → {status}")
    _print_row(row)


def cmd_update(args) -> None:
    rows = _read_tracker()
    found = False
    for row in rows:
        if row["id"] == args.id:
            found = True
            if args.status:
                if args.status not in STATUS_VALUES:
                    print(f"[x] Invalid status. Valid: {', '.join(STATUS_VALUES)}")
                    sys.exit(1)
                row["status"] = args.status
            if args.notes:
                row["notes"] = args.notes
            if args.recruiter:
                row["recruiter"] = args.recruiter
            row["last_updated"] = date.today().isoformat()
            _print_row(row)
            break
    if not found:
        print(f"[x] ID '{args.id}' not found. Use `log` to add it first.")
        sys.exit(1)
    _write_tracker(rows)
    print(f"[+] Updated: {args.id}")


def cmd_list(args) -> None:
    rows = _read_tracker()
    if not rows:
        print("No applications tracked yet. Use `log` to add one.")
        return
    if args.status:
        rows = [r for r in rows if r["status"].lower() == args.status.lower()]
    if not rows:
        print(f"No applications with status '{args.status}'.")
        return
    # Print table
    print(f"\n{'ID':<30} {'Company':<20} {'Role':<25} {'Status':<22} {'Date':<12}")
    print("─" * 112)
    for r in sorted(rows, key=lambda x: x["date_applied"], reverse=True):
        print(f"{r['id']:<30} {r['company']:<20} {r['role']:<25} {r['status']:<22} {r['date_applied']:<12}")
    print(f"\nTotal: {len(rows)}")


def cmd_show(args) -> None:
    rows = _read_tracker()
    for row in rows:
        if row["id"] == args.id:
            _print_row(row)
            return
    print(f"[x] ID '{args.id}' not found.")
    sys.exit(1)


def _print_row(row: dict) -> None:
    print()
    for k, v in row.items():
        if v:
            print(f"  {k:<18}: {v}")
    print()


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Track job applications.")
    sub = parser.add_subparsers(dest="command", required=True)

    # log
    p_log = sub.add_parser("log", help="Log a new application")
    p_log.add_argument("--id",             required=True)
    p_log.add_argument("--company",        default=None)
    p_log.add_argument("--role",           default=None)
    p_log.add_argument("--platform",       default=None,
                       help="LinkedIn / Indeed / Company Website / Referral")
    p_log.add_argument("--url",            default=None)
    p_log.add_argument("--status",         default="Applied")
    p_log.add_argument("--recruiter",      default=None)
    p_log.add_argument("--resume-version", dest="resume_version", default=None)
    p_log.add_argument("--notes",          default=None)

    # update
    p_upd = sub.add_parser("update", help="Update an existing application")
    p_upd.add_argument("--id",        required=True)
    p_upd.add_argument("--status",    default=None)
    p_upd.add_argument("--notes",     default=None)
    p_upd.add_argument("--recruiter", default=None)

    # list
    p_lst = sub.add_parser("list", help="List all applications")
    p_lst.add_argument("--status", default=None, help="Filter by status")

    # show
    p_show = sub.add_parser("show", help="Show details for one application")
    p_show.add_argument("--id", required=True)

    args = parser.parse_args()
    {"log": cmd_log, "update": cmd_update, "list": cmd_list, "show": cmd_show}[args.command](args)


if __name__ == "__main__":
    main()
