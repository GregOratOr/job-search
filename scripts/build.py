#!/usr/bin/env -S uv run
"""
scripts/build.py
----------------
Build the resume and/or cover letter .tex files for a given application ID.

New flow: loads YAML via loader.py -> CV/CoverLetter dataclasses -> renderer.
Per-job sources live under applications/jobs/<id>/ (resume.yaml, cover_letter.yaml).

Usage:
    uv run scripts/build.py --id google_swe_2026
    uv run scripts/build.py --id google_swe_2026 --pdf
    uv run scripts/build.py --id google_swe_2026 --only resume
    uv run scripts/build.py --id google_swe_2026 --only coverletter
    uv run scripts/build.py --id google_swe_2026 --keep-temp
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
    data_path,
    rel_to_root,
)


def build_resume(job_id: str) -> Path:
    from scripts.loader import load_resume
    import resume.cv2latex as engine

    cv = load_resume(job_id)
    tex_out = data_path("applications", "jobs", job_id, "resume.tex")
    tex_out.parent.mkdir(parents=True, exist_ok=True)
    return engine.generate_tex_from_cv(cv, str(tex_out))


def build_coverletter(job_id: str) -> Path | None:
    from scripts.loader import load_cover_letter
    import coverletter.cl2latex as engine

    cl = load_cover_letter(job_id)
    tex_out = data_path("applications", "jobs", job_id, "cover_letter.tex")
    tex_out.parent.mkdir(parents=True, exist_ok=True)
    return engine.generate_tex_from_cl(cl, str(tex_out))


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
            print("    then re-run. Alternatively, drop --pdf to generate only the .tex file.")
            sys.exit(1)
        if result.returncode != 0:
            print(f"[x] pdflatex failed (pass {i+1}):")
            # Show more context around errors
            for line in result.stdout.split("\n"):
                if line.startswith("!") or "Error" in line or "Undefined control sequence" in line:
                    print(f"    {line}")
            # Also show the last 20 lines for context
            print("    --- Last 20 lines of output ---")
            for line in result.stdout.split("\n")[-20:]:
                print(f"    {line}")
            sys.exit(1)
    pdf_path = tex_path.with_suffix(".pdf")
    print(f"[+] PDF generated: {pdf_path.resolve()}")


def clean_temp_files(tex_path: Path, keep: bool = False) -> None:
    """Delete LaTeX auxiliary files unless keep=True."""
    if keep:
        print(f"[!] Keeping LaTeX temp files in {tex_path.parent}")
        return
    for ext in (".aux", ".log", ".out", ".toc", ".fls", ".fdb_latexmk", ".synctex.gz"):
        for f in tex_path.parent.glob(f"*{ext}"):
            try:
                f.unlink()
            except OSError:
                pass


def main():
    parser = argparse.ArgumentParser(description="Build resume/cover letter for a job application.")
    parser.add_argument("--id", "-i", required=True, help="Application ID, e.g. google_swe_2026")
    parser.add_argument("--only", choices=["resume", "coverletter"],
                        help="Build only resume or only coverletter (default: both)")
    parser.add_argument("--pdf", action="store_true",
                        help="Also compile .tex -> PDF using pdflatex")
    parser.add_argument("--keep-temp", action="store_true",
                        help="Keep LaTeX auxiliary files (.aux, .log, etc.) after PDF compile")
    add_overlay_cli_flags(parser)
    args = parser.parse_args()

    active = bootstrap_paths(args)
    print(f">>> Path mode: {'private' if active else 'public'}"
          f"{' (forced)' if args.overlay is not None else ' (auto)'}")

    resume_path = None
    cl_path = None

    if args.only != "coverletter":
        try:
            resume_path = build_resume(args.id)
        except Exception as e:
            print(f"[x] Resume build failed: {e}")
            sys.exit(1)

    if args.only != "resume":
        try:
            cl_path = build_coverletter(args.id)
        except FileNotFoundError:
            print(f"[!] cover_letter.yaml not found for {args.id}; skipping cover letter.")
        except Exception as e:
            print(f"[x] Cover letter build failed: {e}")
            sys.exit(1)

    if args.pdf:
        if resume_path:
            compile_pdf(resume_path)
            clean_temp_files(resume_path, keep=args.keep_temp)
        if cl_path:
            compile_pdf(cl_path)
            clean_temp_files(cl_path, keep=args.keep_temp)

    print("\n* Build complete.")
    if resume_path:
        print(f"  Resume  -> {resume_path}")
    if cl_path:
        print(f"  CL      -> {cl_path}")

    if not args.pdf:
        out_dir = resume_path.parent if resume_path else data_path("applications", "jobs", args.id)
        print("\nNext step: compile with pdflatex (run twice for bookmarks)")
        print(f"  cd {out_dir}")
        if resume_path:
            print(f"  pdflatex {args.id}.tex && pdflatex {args.id}.tex")


if __name__ == "__main__":
    main()