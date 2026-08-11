---
name: build-documents
description: Render resume and cover letter LaTeX from per-job outputs sources (`{id}.py` / `{id}_cl.py`) and optionally compile to PDF. Use when the user wants to build, render, or compile application documents for an application id.
---

# Build Resume / Cover Letter

## Steps
1. Render `.tex` (and PDF) for an application id (paths via `scripts.data_paths`):
   - Both: `uv run scripts/build.py --id <id>`
   - Resume only: `uv run scripts/build.py --id <id> --only resume`
   - Cover letter only: `uv run scripts/build.py --id <id> --only coverletter`
   - Also compile PDF: `uv run scripts/build.py --id <id> --pdf`
   - Compile AND finalize the upload bundle: `uv run scripts/build.py --id <id> --bundle`
2. Path mode flags (same on `build.py`, `bundle.py`, `cv2latex.py`, `cl2latex.py`, `new_application.py`):
   - *(default)* auto-detect `private/profile/`
   - `--private` force writes under `private/`
   - `--public` force the public repo-root tree
3. Outputs live under `resume/outputs/<id>.{py,tex,pdf}` and
   `coverletter/outputs/<id>_cl.{py,tex,pdf}` (or `private/…` when overlay is on).
   `.tex`/`.pdf` are gitignored; rebuild from the `.py` source.
4. Finalize the bundle (move `.py`+`.tex`+`.pdf` into `applications/jobs/<id>/` as
   `{id}_resume.*` / `{id}_cover_letter.*` and delete LaTeX temp files):
   `uv run scripts/bundle.py --id <id>` (or just use `build.py --bundle`).
   Use `--keep-temp` to keep the `.aux/.log/...` artifacts.
5. Engines also accept `--id` directly:
   `uv run resume/cv2latex.py --id <id> --private`
   `uv run coverletter/cl2latex.py --id <id> --private`
6. Manual PDF compile (run pdflatex twice so bookmarks resolve):
   `cd` into the overlay-aware outputs dir (e.g. `private/resume/outputs`) then
   `pdflatex <id>.tex && pdflatex <id>.tex`

## Pitfalls
- `--pdf` needs a LaTeX install (`pdflatex` / MiKTeX on Windows, TeX Live elsewhere).
- `ImportError` on build usually means a tailoring file references a name not in
  `profile/master_data` — fix the tailoring file (see `--inventory`), not `profile/`.
- Unescaped LaTeX specials in a bullet cause `! Undefined control sequence`.
- `--private` errors if `private/profile/` is missing; use default auto or `--public`.
