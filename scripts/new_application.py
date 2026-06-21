#!/usr/bin/env python3
"""
scripts/new_application.py
--------------------------
Scaffold a new job application bundle.

Creates:
  - resume/tailoring/{id}.py
  - coverletter/tailoring/{id}.py
  - applications/jobs/{id}/job_info.py

Usage:
    python scripts/new_application.py --id nvidia_ml_2026 --company NVIDIA --role "ML Engineer"
    python scripts/new_application.py --id google_swe_2026 --company Google --role "SWE" --force
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from scripts.data_paths import apply_private_overlay, data_path, resolve_path

apply_private_overlay()


def _sub(pattern: str, replacement: str, text: str) -> str:
    """Regex replace — whitespace-tolerant, so spacing in the template doesn't matter."""
    return re.sub(pattern, replacement, text, count=1)


def scaffold(job_id: str, company: str, role: str, force: bool = False) -> None:
    if not re.fullmatch(r'[A-Za-z0-9_]+', job_id):
        print(f"[x] ID must contain only letters, digits, and underscores. Got: '{job_id}'")
        sys.exit(1)

    resume_dst   = data_path("resume", "tailoring", f"{job_id}.py")
    cl_dst       = data_path("coverletter", "tailoring", f"{job_id}.py")
    job_dir      = data_path("applications", "jobs", job_id)
    job_info_dst = job_dir / "job_info.py"

    for path in [resume_dst, cl_dst, job_info_dst]:
        if path.exists() and not force:
            print(f"[!] Already exists: {path.relative_to(ROOT)}")
            print(f"    Use --force to overwrite.")
            sys.exit(1)

    # ── Resume tailoring file ─────────────────────────────────────────────────
    src = resolve_path("resume", "tailoring", "_template.py").read_text(encoding="utf-8")
    src = _sub(r'JOB_ID\s*=\s*"_template"',     f'JOB_ID      = "{job_id}"', src)
    src = _sub(r'COMPANY\s*=\s*"Company Name"', f'COMPANY     = "{company}"', src)
    src = _sub(r'ROLE\s*=\s*"Role Title"',       f'ROLE        = "{role}"',   src)
    resume_dst.write_text(src, encoding="utf-8")
    print(f"[+] Resume tailoring  → {resume_dst.relative_to(ROOT)}")

    # ── Cover letter tailoring file ───────────────────────────────────────────
    src = resolve_path("coverletter", "tailoring", "_template.py").read_text(encoding="utf-8")
    src = _sub(r'JOB_ID\s*=\s*"_template"',     f'JOB_ID     = "{job_id}"', src)
    src = _sub(r'COMPANY\s*=\s*"Company Name"', f'COMPANY    = "{company}"', src)
    src = _sub(r'ROLE\s*=\s*"Role Title"',       f'ROLE       = "{role}"',   src)
    cl_dst.write_text(src, encoding="utf-8")
    print(f"[+] CL tailoring      → {cl_dst.relative_to(ROOT)}")

    # ── Job info file ─────────────────────────────────────────────────────────
    job_dir.mkdir(parents=True, exist_ok=True)
    job_info_dst.write_text(f'''\
"""
applications/jobs/{job_id}/job_info.py
Auto-generated {date.today()} by scripts/new_application.py.
Fill in the fields after reviewing the job posting.
"""

JOB_ID   = "{job_id}"
COMPANY  = "{company}"
ROLE     = "{role}"

PLATFORM    = ""    # LinkedIn / Indeed / Company Website / Referral / Handshake
URL         = ""    # Full URL to the job posting
JOB_ID_EXT  = None  # External req ID, e.g. "REQ-12345"
REFERRAL    = None  # Referrer name if applicable
RECRUITER   = None  # Recruiter name if known

LOCATION       = ""
VISA_SPONSORED = None  # True / False / None
SALARY_RANGE   = ""
TEAM           = ""

NOTES = ""

# Keywords from the job description — use to align resume bullets
KEYWORDS = [
    # "CUDA kernel optimization",
    # "distributed training",
]

# People to connect with at this company (see networking/strategy.md)
NETWORKING_TARGETS = [
    # {{"name": "Jane Doe", "title": "ML Engineer", "linkedin": "https://..."}},
]

INTERVIEW_FORMAT = ""
PREP_RESOURCES   = []
''', encoding="utf-8")
    print(f"[+] Job info          → {job_info_dst.relative_to(ROOT)}")

    print(f"""
✓ Application bundle: {job_id}

  1. Edit resume:       resume/tailoring/{job_id}.py
  2. Edit cover letter: coverletter/tailoring/{job_id}.py
  3. Fill job details:  applications/jobs/{job_id}/job_info.py
  4. Build:             python scripts/build.py --id {job_id}
  5. Log after apply:   python scripts/track.py log --id {job_id} --platform <p> --url <url>
""")


def main():
    parser = argparse.ArgumentParser(description="Scaffold a new job application bundle.")
    parser.add_argument("--id",      "-i", required=True, help="e.g. google_swe_2026")
    parser.add_argument("--company", "-c", default="Company Name")
    parser.add_argument("--role",    "-r", default="Role Title")
    parser.add_argument("--force",   action="store_true", help="Overwrite existing files")
    args = parser.parse_args()
    scaffold(args.id, args.company, args.role, args.force)


if __name__ == "__main__":
    main()
