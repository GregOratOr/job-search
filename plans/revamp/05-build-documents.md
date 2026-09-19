# Workstream 05 — `build-documents` Skill and `build.py`

> **Depends on workstream 01** (loader), and consumes the output of 03 and 04.
>
> **Before writing anything, run a `grill-with-docs` session** (the `grilling` skill via
> `domain-modeling`): one question at a time, each with your recommended answer, resolving
> the open questions below — the one-page enforcement question in particular was
> explicitly deferred to this workstream and the user said they would explain the details
> here. Look facts up in the repo yourself; put only decisions to the user. Do not
> implement until the user confirms shared understanding.

## Goal

Turn `resume.yaml` and `cover_letter.yaml` into compiled PDFs, deterministically, with
failures that name the cause precisely enough to fix without guessing.

This is the only stage that is pure machinery. It should be boring, and it should be the
component that *enforces* the constraints the agent might otherwise fudge.

## Decisions already locked

- **YAML → loader → `CV` / `CoverLetter` dataclasses in memory → LaTeX → PDF.** No
  generated `.py` intermediate at any point.
- Scripts contain zero LLM calls. This one is entirely mechanical.
- Artifacts land in the job folder: `resume.tex`, `resume.pdf`, `cover_letter.tex`,
  `cover_letter.pdf`, alongside the YAML sources.
- Every stage is independently re-runnable, so building must work from files on disk
  without any chat context.

## Current state

- [scripts/build.py](../../scripts/build.py) is the existing entry point. It resolves the
  per-job `.py` source through [scripts/data_paths.py](../../scripts/data_paths.py), calls
  `resume.cv2latex.generate_tex_file()` / `coverletter.cl2latex.generate_tex_file()`, then
  optionally runs `pdflatex` twice (needed for bookmarks and cross-references) and
  optionally bundles. Flags today: `--id`, `--only`, `--pdf`, `--bundle`,
  `--private/--public`.
- `generate_tex_file(data_file, output_file)` currently imports a `.py` module and reads
  `cv_data` off it — that import path is what changes.
- `scripts/bundle.py` moves `resume/outputs/<id>.*` and `coverletter/outputs/<id>_cl.*`
  into the job folder and renames them. With YAML sources authored **directly in the job
  folder**, this whole move-and-rename step may become unnecessary — check before keeping
  it.
- `pdflatex` must be on PATH; the script already exits with an install hint when missing.
- The LaTeX layout lives in `LATEX_PREAMBLE` / `LATEX_BODY` inside
  `resume/cv2latex.py` and `coverletter/cl2latex.py`. Not in scope to redesign, but page
  fit is a property of it.
- [skills/build-documents/SKILL.md](../../skills/build-documents/SKILL.md) is the skill
  being reworked.

## Scope

**In scope**
- Rewiring `build.py` and both `*2latex.py` entry points to the YAML loader.
- Deciding whether the separate `outputs/` directories and `bundle.py` survive at all now
  that sources live in the job folder.
- Page-count measurement and what happens when a document exceeds one page.
- Error reporting: LaTeX failures today print only lines starting with `!` or containing
  "Error", which frequently hides the actual cause.
- `skills/build-documents/SKILL.md` — a thin wrapper describing when to build, how to read
  a failure, and how to hand an overflow back to the tailoring skill.

**Out of scope**
- Changing the visual design of the documents.
- Deciding *what* to cut when a resume overflows — that judgment belongs to
  `tailor-resume` (workstream 03). This workstream owns detecting and reporting overflow.

## The deferred question — one-page enforcement

The one-page rule cannot be checked before compiling: it is a property of the PDF, not the
YAML. So the checks split into pre-build (facts, keywords, relevance, character limits,
handled in workstream 03) and post-build (actual page count, here).

The options previously sketched, for the grill session:

- **Hard fail.** `build.py` exits non-zero on more than one page and reports the overflow;
  the agent trims and rebuilds, capped at three attempts before stopping to ask the user.
  Makes the rule machine-enforced rather than dependent on agent judgment, and the cap
  stops a spiral down a wrong path.
- **Warn only.** `build.py` reports the page count; the agent decides.
- **Estimate up front.** Predict length from character counts pre-build, skip the
  post-build check. Cheap but unreliable — LaTeX line breaking is not predictable from
  character counts.

The old `tailor-resume` skill already encoded a workable loop worth reusing: measure, note
what the previous edit cost or bought in lines, size the next edit to that observed
exchange rate, then apply an ordered trim ladder. It also treated *under*-filling (more
than two empty lines) as a defect to fix by restoring content.

**The user has said they will explain the details of how this should work in this
session — ask them first, before proposing.**

## Grill the user on these before implementing

1. **Overflow behaviour** — the deferred question above. Ask the user to describe the
   behaviour they want before you recommend one.
2. **Under-fill.** Is a resume with a lot of empty space a build failure, a warning, or
   not the build's business? *Recommend a warning with the measured empty space reported,
   since the fix is a tailoring decision.*
3. **Page-count mechanism.** `pypdf` as a dependency, `pdfinfo` from the LaTeX
   distribution, or parsing the `pdflatex` log? *Recommend `pypdf` — already a Python
   dependency question, works cross-platform, no external binary beyond `pdflatex`.*
4. **Measuring empty space**, if that is wanted, is harder than counting pages. Is
   approximate last-line position enough, or is this not worth the complexity?
   *Recommend approximate, or dropping it if the user does not value it.*
5. **Do `outputs/` directories and `bundle.py` survive?** If YAML is authored in the job
   folder and the PDFs are written there, both may be dead. *Recommend deleting both — one
   canonical location per application, and the move-rename step disappears along with its
   failure modes.*
6. **CLI surface.** What flags remain? `--id` plus what else — `--only`, `--tex-only`,
   `--keep-temp`? *Recommend `--id`, `--only resume|coverletter`, and `--keep-temp`;
   PDF compilation becomes the default rather than an opt-in, since a `.tex` alone is
   never the goal.*
7. **LaTeX temp files** (`.aux`, `.log`, `.out`) — delete after a successful build, keep
   on failure? *Recommend exactly that: the log is the only diagnostic when it fails.*
8. **Error reporting.** How much of the `pdflatex` log should surface on failure, and
   should the script try to map common LaTeX errors back to the offending YAML field (for
   example an unescaped `&` in a specific bullet)? *Recommend attempting the mapping for
   the handful of common escaping errors — that is the single most frequent failure and
   the mapping turns a cryptic log into a one-line fix.*
9. **Overlay flags.** Keep `--private` / `--public`, or auto-detect only? *Recommend
   auto-detect only, unless the user still uses the public tree for testing.*

## Done criteria

- `uv run scripts/build.py --id <id>` reads the YAML from the job folder and produces
  compiled PDFs there, with no `.py` tailoring file involved anywhere.
- Page count is measured and the agreed overflow behaviour is implemented and tested.
- A deliberate escaping error in a YAML bullet produces an error message naming the field,
  not a raw LaTeX log dump.
- `skills/build-documents/SKILL.md` describes building and failure triage in one short
  read and names no deleted script.
- If `bundle.py` and the `outputs/` directories are retired, every reference to them
  elsewhere is queued for workstream 09.
