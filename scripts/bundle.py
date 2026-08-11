#!/usr/bin/env -S uv run
"""
scripts/bundle.py
-----------------
Finalize an application "bundle": the single per-application folder
applications/jobs/<id>/ that holds everything you upload.

After the resume/cover letter are built and compiled, this tool:
  1. Moves per-job .py/.tex/.pdf out of resume/outputs/ and coverletter/outputs/
     (resume: {id}.*; cover letter: {id}_cl.*) into applications/jobs/<id>/ as
     {id}_resume.{py,tex,pdf} and {id}_cover_letter.{py,tex,pdf}.
     Re-runs that would overwrite existing deliverables use a shared
     Windows-style postfix instead: {id}_resume (1).pdf, (2), …
  2. Deletes the LaTeX temp artifacts left in the outputs folders
     (.aux, .log, .out, .toc, .fls, .fdb_latexmk, .synctex.gz, .nav, .snm).
  3. Keeps the .py/.tex/.pdf in the bundle so documents can be edited and
     recompiled later.

Path mode (same flags as build.py / cv2latex / cl2latex):
    (default)   auto-detect private/profile/
    --private   force private/ paths
    --public    force public repo-root paths

Usage:
    uv run scripts/bundle.py --id google_swe_2026
    uv run scripts/bundle.py --id google_swe_2026 --private
    uv run scripts/bundle.py --id google_swe_2026 --keep-temp
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.data_paths import (
    add_overlay_cli_flags,
    bootstrap_paths,
    data_path,
    document_pdf,
    document_py,
    document_stem,
    document_tex,
    rel_to_root,
)

# LaTeX intermediate files that should never live in the bundle.
_TEMP_SUFFIXES = (
    ".aux", ".log", ".out", ".toc", ".lof", ".lot", ".fls",
    ".fdb_latexmk", ".synctex.gz", ".nav", ".snm", ".vrb", ".bbl", ".blg",
)

# (kind, destination basename stem in the bundle — "{job_id}_resume" etc.)
_DOC_KINDS = (
    ("resume", "resume"),
    ("coverletter", "cover_letter"),
)

_KEEP_SUFFIXES = (".py", ".tex", ".pdf")


def _clean_temp(stem: str, outputs_dir: Path) -> list[str]:
    removed: list[str] = []
    for suffix in _TEMP_SUFFIXES:
        artifact = outputs_dir / f"{stem}{suffix}"
        if artifact.exists():
            artifact.unlink()
            removed.append(artifact.name)
    return removed


def _stem_taken(bundle_dir: Path, stem: str) -> bool:
    return any((bundle_dir / f"{stem}{suffix}").exists() for suffix in _KEEP_SUFFIXES)


def _versioned_dest_stem(bundle_dir: Path, dest_base: str) -> str:
    """Return dest_base, or ``dest_base (n)`` if those deliverables already exist."""
    if not _stem_taken(bundle_dir, dest_base):
        return dest_base
    n = 1
    while True:
        candidate = f"{dest_base} ({n})"
        if not _stem_taken(bundle_dir, candidate):
            return candidate
        n += 1


def finalize_bundle(job_id: str, keep_temp: bool = False) -> Path:
    """Move built .py/.tex/.pdf into the bundle folder and clean temp artifacts.

    Returns the bundle directory. Missing docs are skipped with a warning
    (e.g. an application with no cover letter). If a prior bundle already has
    ``{id}_resume.*`` / ``{id}_cover_letter.*``, this run writes
    ``{id}_resume (1).*`` (then ``(2)``, …) so nothing is overwritten.
    """
    bundle_dir = data_path("applications", "jobs", job_id)
    bundle_dir.mkdir(parents=True, exist_ok=True)

    moved: list[str] = []
    for kind, label in _DOC_KINDS:
        dest_base = f"{job_id}_{label}"
        outputs_dir = data_path(kind, "outputs")
        sources = {
            ".py": document_py(kind, job_id),
            ".tex": document_tex(kind, job_id),
            ".pdf": document_pdf(kind, job_id),
        }
        if not sources[".py"].exists():
            legacy_py = data_path(kind, "tailoring", f"{job_id}.py")
            if legacy_py.exists():
                sources[".py"] = legacy_py
            elif kind == "coverletter":
                pre_cl = data_path(kind, "outputs", f"{job_id}.py")
                if pre_cl.exists():
                    sources[".py"] = pre_cl

        if not any(p.exists() for p in sources.values()):
            print(f"  [skip] No built {kind} found in {outputs_dir} for '{job_id}'")
            continue

        dest_stem = _versioned_dest_stem(bundle_dir, dest_base)
        if dest_stem != dest_base:
            print(f"  [!] {dest_base}.* already in bundle — writing {dest_stem}.*")

        for suffix in _KEEP_SUFFIXES:
            src = sources[suffix]
            dest = bundle_dir / f"{dest_stem}{suffix}"
            if src.exists():
                shutil.move(str(src), str(dest))
                moved.append(dest.name)
                print(f"  [+] {rel_to_root(src)} -> applications/jobs/{job_id}/{dest.name}")

        if not keep_temp:
            removed = _clean_temp(document_stem(kind, job_id), outputs_dir)
            if kind == "coverletter":
                removed += _clean_temp(job_id, outputs_dir)  # pre-_cl naming
            if removed:
                print(f"  [clean] removed temp: {', '.join(removed)}")

    if not moved:
        print(f"  [!] Nothing moved. Build first: uv run scripts/build.py --id {job_id} --pdf")
    else:
        print(f"  Bundle ready: {rel_to_root(bundle_dir)}")

    return bundle_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Finalize application upload bundle.")
    parser.add_argument("--id", "-i", required=True, help="Application ID")
    parser.add_argument("--keep-temp", action="store_true",
                        help="Do not delete LaTeX temp artifacts from outputs/")
    add_overlay_cli_flags(parser)
    args = parser.parse_args()

    active = bootstrap_paths(args)
    print(f">>> Path mode: {'private' if active else 'public'}"
          f"{' (forced)' if args.overlay is not None else ' (auto)'}")

    finalize_bundle(args.id, keep_temp=args.keep_temp)


if __name__ == "__main__":
    main()
