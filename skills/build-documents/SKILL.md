---
name: build-documents
description: Render resume and cover letter LaTeX from per-job tailoring files and optionally compile to PDF. Use when the user wants to build, render, or compile application documents for an application id.
---

# Build Resume / Cover Letter

## Steps
1. Render `.tex` (and PDF) for an application id:
   - Both: `python scripts/build.py --id <id>`
   - Resume only: `python scripts/build.py --id <id> --only resume`
   - Cover letter only: `python scripts/build.py --id <id> --only coverletter`
   - Also compile PDF: `python scripts/build.py --id <id> --pdf`
2. Outputs land in `resume/outputs/<id>.tex` and `coverletter/outputs/<id>.tex`
   (gitignored; always rebuildable).
3. Manual PDF compile (run pdflatex twice so bookmarks resolve):
   `cd resume/outputs && pdflatex <id>.tex && pdflatex <id>.tex`

## Pitfalls
- `--pdf` needs a LaTeX install (`pdflatex` / MiKTeX on Windows, TeX Live elsewhere).
- `ImportError` on build usually means a tailoring file references a name not in
  `profile/master_data` — fix the tailoring file (see `--inventory`), not `profile/`.
- Unescaped LaTeX specials in a bullet cause `! Undefined control sequence`.
