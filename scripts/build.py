#!/usr/bin/env python3
"""
scripts/build.py
----------------
Build the resume and/or cover letter .tex files for a given application ID.

Usage:
    python scripts/build.py --id google_swe_2026
    python scripts/build.py --id google_swe_2026 --only resume
    python scripts/build.py --id google_swe_2026 --only coverletter
    python scripts/build.py --id google_swe_2026 --pdf   # also run pdflatex

After building, compile to PDF:
    cd resume/outputs && pdflatex google_swe_2026.tex && pdflatex google_swe_2026.tex
    cd coverletter/outputs && pdflatex google_swe_2026.tex && pdflatex google_swe_2026.tex
    (run twice so bookmarks and cross-references resolve)
"""

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from scripts.data_paths import apply_private_overlay, resolve_path

apply_private_overlay()


def build_resume(job_id: str) -> Path:
    tailoring_file = resolve_path("resume", "tailoring", f"{job_id}.py")
    if not tailoring_file.exists():
        print(f"[x] Resume tailoring file not found: {tailoring_file}")
        print(f"    Run: python scripts/new_application.py --id {job_id}")
        sys.exit(1)
    import resume.cv2latex as engine
    return engine.generate_tex_file(str(tailoring_file))


def build_coverletter(job_id: str) -> Path:
    tailoring_file = resolve_path("coverletter", "tailoring", f"{job_id}.py")
    if not tailoring_file.exists():
        print(f"[!] Cover letter tailoring file not found: {tailoring_file}")
        print(f"    Skipping cover letter build.")
        return None
    import coverletter.cl2latex as engine
    return engine.generate_tex_file(str(tailoring_file))


def compile_pdf(tex_path: Path) -> None:
    """Run pdflatex twice in the directory of the .tex file."""
    if tex_path is None:
        return
    print(f">>> Compiling PDF: {tex_path.name}")
    for i in range(2):
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", tex_path.name],
            cwd=tex_path.parent,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"[x] pdflatex failed (pass {i+1}):")
            # Print only the error lines to avoid noise
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
                        help="Also compile .tex → PDF using pdflatex")
    args = parser.parse_args()

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

    print("\n✓ Build complete.")
    if resume_path:
        print(f"  Resume  → {resume_path}")
    if cl_path:
        print(f"  CL      → {cl_path}")
    print("\nNext step: compile with pdflatex (run twice for bookmarks)")
    print(f"  cd {resume_path.parent if resume_path else 'resume/outputs'}")
    print(f"  pdflatex {args.id}.tex && pdflatex {args.id}.tex")


if __name__ == "__main__":
    main()
