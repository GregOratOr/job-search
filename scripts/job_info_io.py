"""
scripts/job_info_io.py
----------------------
Read/write helpers for applications/jobs/<id>/job_info.py.

Uses whitespace-tolerant regex replacement (same approach as new_application.py)
so field updates survive minor formatting drift in generated files.
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path
from typing import Any

from scripts.data_paths import data_path


def job_info_path(job_id: str) -> Path:
    return data_path("applications", "jobs", job_id, "job_info.py")


def _replace_field(content: str, field: str, value_repr: str) -> str:
    """Replace one assignment line; append if the field is missing."""
    pattern = rf"^{re.escape(field)}\s*=\s*.+$"
    replacement = f"{field:<12}= {value_repr}"
    if re.search(pattern, content, flags=re.MULTILINE):
        return re.sub(pattern, replacement, content, count=1, flags=re.MULTILINE)
    # Insert after ROLE block when possible.
    anchor = re.search(r"^ROLE\s*=.*$", content, flags=re.MULTILINE)
    if anchor:
        pos = anchor.end()
        return content[:pos] + f"\n{replacement}" + content[pos:]
    return content.rstrip() + f"\n{replacement}\n"


def set_job_info_fields(
    job_id: str,
    *,
    url: str | None = None,
    platform: str | None = None,
    location: str | None = None,
    team: str | None = None,
    notes: str | None = None,
) -> Path:
    """Patch string fields in job_info.py. Values are written with repr() for safety."""
    path = job_info_path(job_id)
    if not path.exists():
        raise FileNotFoundError(f"job_info.py not found for {job_id}: {path}")

    content = path.read_text(encoding="utf-8")
    updates: dict[str, str] = {}
    if url is not None:
        updates["URL"] = repr(url)
    if platform is not None:
        updates["PLATFORM"] = repr(platform)
    if location is not None:
        updates["LOCATION"] = repr(location)
    if team is not None:
        updates["TEAM"] = repr(team)
    if notes is not None:
        updates["NOTES"] = repr(notes)

    for field, value_repr in updates.items():
        content = _replace_field(content, field, value_repr)

    path.write_text(content, encoding="utf-8")
    return path


def load_job_info(job_id: str) -> dict[str, Any]:
    """Load metadata from job_info.py if present."""
    path = job_info_path(job_id)
    if not path.exists():
        return {}
    spec = importlib.util.spec_from_file_location(f"job_info_{job_id}", str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return {
        "company":  getattr(module, "COMPANY",  ""),
        "role":     getattr(module, "ROLE",     ""),
        "platform": getattr(module, "PLATFORM", ""),
        "url":      getattr(module, "URL",      ""),
        "recruiter": getattr(module, "RECRUITER", "") or "",
    }
