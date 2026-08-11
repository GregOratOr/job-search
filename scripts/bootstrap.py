"""
scripts/bootstrap.py
--------------------
One-call script initialization: ROOT on sys.path, private overlay, .env load.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_bootstrapped = False


def init_script() -> Path:
    """Insert project root, apply private overlay, load .env. Returns ROOT."""
    global _bootstrapped
    root_str = str(ROOT)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    if not _bootstrapped:
        from scripts.data_paths import apply_private_overlay
        from scripts.llm_provider import load_env

        apply_private_overlay()
        load_env()
        _bootstrapped = True
    return ROOT
