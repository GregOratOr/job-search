"""
scripts/data_paths.py
---------------------
Resolve paths for user-specific data. When the ``private/`` submodule is present
(contains ``private/profile/``), scripts read and write there instead of the
public template directories shipped with the repo.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRIVATE = ROOT / "private"
_overlay_applied = False


def uses_private_data() -> bool:
    return (PRIVATE / "profile").is_dir()


def apply_private_overlay() -> bool:
    """Prefer ``private/profile`` for ``import profile`` when submodule is present."""
    global _overlay_applied
    if _overlay_applied:
        return uses_private_data()
    _overlay_applied = True
    if uses_private_data():
        sys.path.insert(0, str(PRIVATE))
        return True
    return False


def data_path(*parts: str) -> Path:
    """Read/write path for user data — ``private/`` when submodule is checked out."""
    if uses_private_data():
        return PRIVATE.joinpath(*parts)
    return ROOT.joinpath(*parts)


def resolve_path(*parts: str) -> Path:
    """Read path — use ``private/`` file when it exists, else the public template."""
    private_candidate = PRIVATE.joinpath(*parts)
    if private_candidate.exists():
        return private_candidate
    return ROOT.joinpath(*parts)


def resolve_env_file() -> Path | None:
    for candidate in (PRIVATE / ".env", ROOT / ".env"):
        if candidate.is_file():
            return candidate
    return None
