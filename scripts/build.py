#!/usr/bin/env -S uv run
"""
scripts/build.py
----------------
Build the resume and/or cover letter .tex files for a given application ID.

Per-job sources live under ``{resume,coverletter}/outputs/``
(``{id}.py`` for resume, ``{id}_cl.py`` for cover letter). Paths are
routed through ``scripts.data_paths`` (``private/`` when the overlay is active).

Path mode (shared with cv2latex / cl2latex / bundle):
    (default)   auto-detect private/profile/
    --private   force private/ paths
    --public    force public repo-root paths

Usage:
    uv run scripts/build.py --id google_swe_2026
    uv run scripts/build.py --id google_swe_2026 --private --pdf
    uv run scripts/build.py --id google_swe_2026 --only resume
    uv run scripts/build.py --id google_swe_2026 --only coverletter
    uv run scripts/build.py --id google_swe_2026 --bundle
"""

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from scripts.data_paths import (
    add_overlay_cli_flags,
    bootstrap_paths,
    document_py,
    document_tex,
    rel_to_root,
    resolve_document_paths,
)


def build_resume(job_id: str) -> Path:
    try:
        src, tex_out = resolve_document_paths("resume", job_id)
    except FileNotFoundError:
        expected = document_py("resume", job_id)
        print(f"[x] Resume source file not found: {expected}")
        print(f"    Run: uv run scripts/new_application.py --id {job_id}")
        sys.exit(1)
    if src.parent.name == "tailoring":
        print(f"[!] Using legacy path {rel_to_root(src)}; "
              f"move to {rel_to_root(document_py('resume', job_id))} when convenient.")
    import resume.cv2latex as engine
    tex_out.parent.mkdir(parents=True, exist_ok=True)
    return engine.generate_tex_file(str(src), str(tex_out))


def build_coverletter(job_id: str) -> Path | None:
    try:
        src, tex_out = resolve_document_paths("coverletter", job_id)
    except FileNotFoundError:
        expected = document_py("coverletter", job_id)
        print(f"[!] Cover letter source file not found: {expected}")
        print(f"    Skipping cover letter build.")
        return None
    if src.parent.name == "tailoring":
        print(f"[!] Using legacy path {rel_to_root(src)}")
    import coverletter.cl2latex as engine
    tex_out.parent.mkdir(parents=True, exist_ok=True)
    return engine.generate_tex_file(str(src), str(tex_out))


def compile_pdf(tex_path: Path) -> None:
    """Run pdflatex twice in the directory of the .tex file."""
    if tex_path is None:
        return
    print(f">>> Compiling PDF: {tex_path.name}")
    for i in range(2):
        try:
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", tex_path.name],
                cwd=tex_path.parent,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError:
            print("[x] pdflatex not found on PATH — a LaTeX distribution is required for PDF output.")
            print("    Install TeX Live (https://tug.org/texlive/) or MiKTeX (https://miktex.org/),")
            print("    then re-run. Alternatively, drop --pdf/--bundle to generate only the .tex file.")
            sys.exit(1)
        if result.returncode != 0:
            print(f"[x] pdflatex failed (pass {i+1}):")
            for line in result.stdout.split("\n"):
                if line.startswith("!") or "Error" in line:
                    print(f"    {line}")
            sys.exit(1)
    pdf_path = tex_path.with_suffix(".pdf")
    print(f"[+] PDF generated: {pdf_path.resolve()}")


def main():
    parser = argparse.ArgumentParser(description="Build resume/cover letter for a job application.")
    parser.add_argument("--id", "-i", required=True, help="Application ID, e.g. google_swe_2026")
    parser.add_argument("--only", choices=["resume", "coverletter"],
                        help="Build only resume or only coverletter (default: both)")
    parser.add_argument("--pdf", action="store_true",
                        help="Also compile .tex -> PDF using pdflatex")
    parser.add_argument("--bundle", action="store_true",
                        help="After compiling, move .py/.tex/.pdf into applications/jobs/<id>/ "
                             "and clean LaTeX temp files (implies --pdf)")
    add_overlay_cli_flags(parser)
    args = parser.parse_args()

    active = bootstrap_paths(args)
    print(f">>> Path mode: {'private' if active else 'public'}"
          f"{' (forced)' if args.overlay is not None else ' (auto)'}")

    if args.bundle:
        args.pdf = True

    resume_path = None
    cl_path = None

    if args.only != "coverletter":
        resume_path = build_resume(args.id)

    if args.only != "resume":
        cl_path = build_coverletter(args.id)

    if args.pdf:
        if resume_path:
            compile_pdf(resume_path)
        if cl_path:
            compile_pdf(cl_path)

    if args.bundle:
        from scripts.bundle import finalize_bundle
        finalize_bundle(args.id)
        print("\n* Build + bundle complete.")
        return

    print("\n* Build complete.")
    if resume_path:
        print(f"  Resume  -> {resume_path}")
    if cl_path:
        print(f"  CL      -> {cl_path}")
    out_dir = resume_path.parent if resume_path else document_tex("resume", args.id).parent
    print("\nNext step: compile with pdflatex (run twice for bookmarks)")
    print(f"  cd {out_dir}")
    print(f"  pdflatex {args.id}.tex && pdflatex {args.id}.tex")


if __name__ == "__main__":
    main()
