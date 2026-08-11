#!/usr/bin/env -S uv run
"""
scripts/new_application.py
--------------------------
Scaffold a new job application bundle.

Creates:
  - resume/outputs/{id}.py
  - coverletter/outputs/{id}_cl.py
  - applications/jobs/{id}/job_info.py

Templates:
  - {resume,coverletter}/tailoring/_template.py
  - applications/jobs/_template/job_info.py

Per-job sources live under ``outputs/`` (routed to ``private/`` when the overlay
is present).

Usage:
    uv run scripts/new_application.py --id nvidia_ml_2026 --company NVIDIA --role "ML Engineer"
    uv run scripts/new_application.py --id google_swe_2026 --company Google --role "SWE" --force
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))
from scripts.data_paths import (
    add_overlay_cli_flags,
    bootstrap_paths,
    data_path,
    document_py,
    document_tex,
    rel_to_root,
    resolve_path,
    template_path,
)


def _job_info_template() -> Path:
    return resolve_path("applications", "jobs", "_template", "job_info.py")


def _patch_document_template(kind: str, src: str, job_id: str, company: str, role: str) -> str:
    """Fill JOB_ID/COMPANY/ROLE and set overlay-aware OUTPUT_FILE."""
    src = re.sub(r'JOB_ID\s*=\s*"_template"', f'JOB_ID = "{job_id}"', src, count=1)
    src = re.sub(r'COMPANY\s*=\s*"Company Name"', f'COMPANY = "{company}"', src, count=1)
    src = re.sub(r'ROLE\s*=\s*"Role Title"', f'ROLE = "{role}"', src, count=1)
    out_rel = rel_to_root(document_tex(kind, job_id))
    src = re.sub(
        r'^OUTPUT_FILE\s*=\s*.*$',
        f'OUTPUT_FILE = "{out_rel}"',
        src,
        count=1,
        flags=re.MULTILINE,
    )
    return src


def _patch_job_info(src: str, job_id: str, company: str, role: str, dest_rel: str) -> str:
    """Fill identity fields and refresh the module docstring path/date."""
    src = re.sub(
        r'^"""[\s\S]*?"""',
        f'"""\n{dest_rel}\nAuto-generated {date.today()} by scripts/new_application.py.\n'
        f"Fill in the fields after reviewing the job posting.\n\"\"\"",
        src,
        count=1,
    )
    src = re.sub(r'JOB_ID\s*=\s*"_template"', f'JOB_ID   = "{job_id}"', src, count=1)
    src = re.sub(r'COMPANY\s*=\s*"Company Name"', f'COMPANY  = "{company}"', src, count=1)
    src = re.sub(r'ROLE\s*=\s*"Role Title"', f'ROLE     = "{role}"', src, count=1)
    return src


def scaffold(job_id: str, company: str, role: str, force: bool = False) -> None:
    if not re.fullmatch(r"[A-Za-z0-9_]+", job_id):
        print(f"[x] ID must contain only letters, digits, and underscores. Got: '{job_id}'")
        sys.exit(1)

    resume_dst = document_py("resume", job_id)
    cl_dst = document_py("coverletter", job_id)
    job_dir = data_path("applications", "jobs", job_id)
    job_info_dst = job_dir / "job_info.py"
    job_info_tpl = _job_info_template()

    if not job_info_tpl.is_file():
        print(f"[x] Missing job_info template: {rel_to_root(job_info_tpl)}")
        sys.exit(1)

    for path in [resume_dst, cl_dst, job_info_dst]:
        if path.exists() and not force:
            print(f"[!] Already exists: {rel_to_root(path)}")
            print("    Use --force to overwrite.")
            sys.exit(1)

    resume_dst.parent.mkdir(parents=True, exist_ok=True)
    cl_dst.parent.mkdir(parents=True, exist_ok=True)
    job_dir.mkdir(parents=True, exist_ok=True)

    resume_src = template_path("resume").read_text(encoding="utf-8")
    resume_dst.write_text(
        _patch_document_template("resume", resume_src, job_id, company, role),
        encoding="utf-8",
    )
    print(f"[+] Resume source     -> {rel_to_root(resume_dst)}")

    cl_src = template_path("coverletter").read_text(encoding="utf-8")
    cl_dst.write_text(
        _patch_document_template("coverletter", cl_src, job_id, company, role),
        encoding="utf-8",
    )
    print(f"[+] CL source         -> {rel_to_root(cl_dst)}")

    job_info_rel = rel_to_root(job_info_dst)
    job_info_src = job_info_tpl.read_text(encoding="utf-8")
    job_info_dst.write_text(
        _patch_job_info(job_info_src, job_id, company, role, job_info_rel),
        encoding="utf-8",
    )
    print(f"[+] Job info          -> {job_info_rel}")

    print(f"""
* Application bundle: {job_id}

  1. Edit resume:       {rel_to_root(resume_dst)}
  2. Edit cover letter: {rel_to_root(cl_dst)}
  3. Fill job details:  {job_info_rel}
  4. Build:             uv run scripts/build.py --id {job_id}
  5. Log after apply:   uv run scripts/track.py log --id {job_id} --platform <p> --url <url>
  6. Follow up later:   uv run scripts/followup.py
""")


def main():
    parser = argparse.ArgumentParser(description="Scaffold a new job application bundle.")
    parser.add_argument("--id", "-i", required=True, help="e.g. google_swe_2026")
    parser.add_argument("--company", "-c", default="Company Name")
    parser.add_argument("--role", "-r", default="Role Title")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    add_overlay_cli_flags(parser)
    args = parser.parse_args()
    active = bootstrap_paths(args)
    print(
        f">>> Path mode: {'private' if active else 'public'}"
        f"{' (forced)' if args.overlay is not None else ' (auto)'}"
    )
    scaffold(args.id, args.company, args.role, args.force)


if __name__ == "__main__":
    main()
