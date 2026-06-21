#!/usr/bin/env python3
"""
scripts/update_profile.py
--------------------------
Profile management tool: validate imports, show current inventory, and
display the changelog. Run this after updating any profile/ file to confirm
everything loads correctly.

Usage:
    python scripts/update_profile.py              # full report
    python scripts/update_profile.py --validate   # import check only (for CI)
    python scripts/update_profile.py --changelog  # show recent changelog
    python scripts/update_profile.py --inventory  # show all entries
"""

import argparse
import sys
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from scripts.data_paths import apply_private_overlay, data_path, resolve_path

apply_private_overlay()


# ── ANSI colours (degrade gracefully if terminal doesn't support them) ────────
GREEN  = "\033[32m"
YELLOW = "\033[33m"
RED    = "\033[31m"
BOLD   = "\033[1m"
RESET  = "\033[0m"
ok     = lambda s: f"{GREEN}✓{RESET} {s}"
warn   = lambda s: f"{YELLOW}!{RESET} {s}"
fail   = lambda s: f"{RED}✗{RESET} {s}"
head   = lambda s: f"\n{BOLD}{s}{RESET}"


def validate_imports() -> bool:
    """Try importing every profile sub-module and master_data. Return True if all OK.

    Experience/project/research entries are validated dynamically via the registries
    in master_data, so this never drifts when entries are renamed/added.
    """
    modules = [
        ("profile.header",     ["HEADER", "CL_HEADER"]),
        ("profile.education",  ["EXAMPLE_UNIV_MS", "EXAMPLE_UNIV_BTECH"]),
        ("profile.experience", []),
        ("profile.projects",   []),
        ("profile.skills",     ["SKILLS_FULL", "SKILLS_ML_FOCUSED"]),
        ("profile.summaries",  ["SUMMARIES"]),
        ("profile.research",   []),
        ("profile.coursework", ["COURSEWORK_EXAMPLE_MS", "COURSEWORK_EXAMPLE_BTECH"]),
        ("profile.master_data", ["HEADER", "EXPERIENCE_REGISTRY",
                                  "PROJECT_REGISTRY", "RESEARCH_REGISTRY"]),
    ]

    all_ok = True
    print(head("Import Validation"))
    for mod_name, attrs in modules:
        try:
            mod = __import__(mod_name, fromlist=attrs)
            missing = [a for a in attrs if not hasattr(mod, a)]
            if missing:
                print(warn(f"{mod_name} — missing exports: {missing}"))
                all_ok = False
            else:
                print(ok(f"{mod_name}"))
        except Exception as e:
            print(fail(f"{mod_name} — {e}"))
            all_ok = False

    # ── Registry consistency: every name in master_data.__all__ must resolve, and
    #    every registry entry must be importable from master_data by its key. ──────
    try:
        import profile.master_data as md
        registries = {
            "EXPERIENCE_REGISTRY": getattr(md, "EXPERIENCE_REGISTRY", {}),
            "PROJECT_REGISTRY":    getattr(md, "PROJECT_REGISTRY", {}),
            "RESEARCH_REGISTRY":   getattr(md, "RESEARCH_REGISTRY", {}),
        }
        for reg_name, reg in registries.items():
            if not reg:
                print(warn(f"{reg_name} is empty"))
                continue
            bad_keys = [k for k in reg if not hasattr(md, k)]
            if bad_keys:
                print(fail(f"{reg_name} — keys not exported by master_data: {bad_keys}"))
                all_ok = False
            else:
                print(ok(f"{reg_name} ({len(reg)} entries)"))
    except Exception as e:
        print(fail(f"registry validation — {e}"))
        all_ok = False

    return all_ok


def show_inventory() -> None:
    """Print a formatted table of all profile entries (driven by master_data registries)."""
    try:
        from profile.master_data import (
            EXAMPLE_UNIV_MS, EXAMPLE_UNIV_BTECH,
            EXPERIENCE_REGISTRY, PROJECT_REGISTRY, RESEARCH_REGISTRY,
            SUMMARIES,
            SKILLS_FULL, SKILLS_ML_FOCUSED, SKILLS_SWE_FOCUSED, SKILLS_RESEARCH_FOCUSED,
        )
    except ImportError as e:
        print(fail(f"Cannot load profile for inventory: {e}"))
        return

    print(head("Education"))
    for e in [EXAMPLE_UNIV_MS, EXAMPLE_UNIV_BTECH]:
        print(f"  {e.institution:<45} {e.date}")

    print(head("Experience"))
    for var, e in EXPERIENCE_REGISTRY.items():
        print(f"  {var:<28} {e.role:<40} {e.date}")

    print(head("Projects"))
    for var, p in PROJECT_REGISTRY.items():
        print(f"  {var:<32} {p.title[:45]:<45} {p.date}")

    print(head("Research"))
    if RESEARCH_REGISTRY:
        for var, r in RESEARCH_REGISTRY.items():
            print(f"  {var:<32} {r.title[:50]:<50} {r.date}")
    else:
        print("  (none yet)")

    print(head("Skill Presets"))
    for name, preset in [
        ("SKILLS_FULL",             SKILLS_FULL),
        ("SKILLS_ML_FOCUSED",       SKILLS_ML_FOCUSED),
        ("SKILLS_SWE_FOCUSED",      SKILLS_SWE_FOCUSED),
        ("SKILLS_RESEARCH_FOCUSED", SKILLS_RESEARCH_FOCUSED),
    ]:
        print(f"  {name:<30} ({len(preset)} categories)")

    print(head("Summary Variants"))
    for key in SUMMARIES:
        preview = SUMMARIES[key][:60].replace("\n", " ")
        print(f"  \"{key}\"   {preview}...")

    print()


def show_changelog(n: int = 15) -> None:
    """Print the last N lines of the changelog table."""
    cl_path = ROOT / "profile" / "CHANGELOG.md"
    if not cl_path.exists():
        print(warn("profile/CHANGELOG.md not found"))
        return
    print(head("Recent Changelog"))
    lines = cl_path.read_text(encoding="utf-8").splitlines()
    table_lines = [l for l in lines if l.startswith("|") and "---" not in l and "Date" not in l]
    for line in table_lines[-n:]:
        print(f"  {line}")
    print()


def show_tailoring_files() -> None:
    """List all existing tailoring files and their build status."""
    print(head("Resume Tailoring Files"))
    tailoring_dir = ROOT / "resume" / "tailoring"
    for f in sorted(tailoring_dir.glob("*.py")):
        if f.name.startswith("_"):
            continue
        output_tex = ROOT / "resume" / "outputs" / f.stem / f"{f.stem}.tex"
        # Check if matching .tex exists in outputs/
        tex_files = list((ROOT / "resume" / "outputs").glob(f"{f.stem}.tex"))
        built = ok("built") if tex_files else warn("not built")
        print(f"  {f.name:<40} {built}")

    print(head("Cover Letter Tailoring Files"))
    cl_tailoring_dir = ROOT / "coverletter" / "tailoring"
    for f in sorted(cl_tailoring_dir.glob("*.py")):
        if f.name.startswith("_"):
            continue
        tex_files = list((ROOT / "coverletter" / "outputs").glob(f"{f.stem}.tex"))
        built = ok("built") if tex_files else warn("not built")
        print(f"  {f.name:<40} {built}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Profile management and validation tool.")
    parser.add_argument("--validate",  action="store_true", help="Import check only (exit 1 on failure)")
    parser.add_argument("--changelog", action="store_true", help="Show changelog only")
    parser.add_argument("--inventory", action="store_true", help="Show entry inventory only")
    args = parser.parse_args()

    if args.validate:
        ok_ = validate_imports()
        sys.exit(0 if ok_ else 1)

    if args.changelog:
        show_changelog()
        return

    if args.inventory:
        show_inventory()
        return

    # Full report
    all_ok = validate_imports()
    show_inventory()
    show_tailoring_files()
    show_changelog()

    if not all_ok:
        print(fail("One or more imports failed. Fix errors above before building."))
        sys.exit(1)
    else:
        print(ok("All profile imports healthy.\n"))


if __name__ == "__main__":
    main()
