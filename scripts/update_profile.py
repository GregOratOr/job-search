#!/usr/bin/env -S uv run
"""
Deprecated alias for scripts/validate_profile.py.

    uv run scripts/validate_profile.py --inventory
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make `scripts.*` importable when invoked as `uv run scripts/update_profile.py`.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

print(
    "[deprecated] update_profile.py was renamed to validate_profile.py "
    "(it never wrote profile files). Prefer: uv run scripts/validate_profile.py …",
    file=sys.stderr,
)

from scripts.validate_profile import main

if __name__ == "__main__":
    main()
