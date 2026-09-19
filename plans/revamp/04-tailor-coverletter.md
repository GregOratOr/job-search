# Workstream 04 — `tailor-coverletter` Skill

> **Depends on workstream 01** (`cover_letter.yaml` schema and loader) and
> **workstream 02** (`job.yaml`). Reads workstream 03's `resume.yaml` as input.
>
> **Before writing anything, run a `grill-with-docs` session** (the `grilling` skill via
> `domain-modeling`): one question at a time, each with your recommended answer, resolving
> the open questions below. Look facts up in the repo yourself; put only decisions to the
> user. Do not implement until the user confirms shared understanding.

## Goal

Produce a one-page cover letter for the job, grounded in the same profile facts as the
resume and consistent with it, written into `cover_letter.yaml`.

## Decisions already locked

- Output is **`cover_letter.yaml`** in the job folder, loaded into the existing
  `CoverLetter` dataclasses and rendered by `coverletter/cl2latex.py`. No `.py` tailoring
  file, no imports, single-backslash LaTeX.
- **Reads `resume.yaml`**, not just the profile. The letter must not contradict the resume
  or repeat it verbatim, and it should lean on whichever evidence the resume foregrounded.
- Profile is read-only. Every claim traces to a profile entry.
- Zero LLM calls in Python.
- One page, like the resume.

## Current state

- [coverletter/cl_utils.py](../../coverletter/cl_utils.py) defines the target objects:
  `CLHeader` (name, email, linkedin, street, city/state/zip, optional signature image
  path), `RecipientInfo` (company name, department or area, city/state/zip), `JobInfo`
  (title, optional job id), `LetterContent` (date string, salutation, list of paragraph
  strings, closing), and `CoverLetter` tying them together.
- `CL_HEADER` lives in the profile (`profile/header.py` today, `header.yaml` after
  workstream 01) and should be pulled automatically — it is not per-job content.
- `coverletter/cl2latex.py` renders it. The signature image path is relative to the output
  `.tex` location; `None` skips the `\includegraphics` line.
- [skills/tailor-coverletter/SKILL.md](../../skills/tailor-coverletter/SKILL.md) is the
  version being replaced — read it for anything worth carrying forward.
- [coverletter/AGENTS.md](../../coverletter/AGENTS.md) documents the recommended paragraph
  structure: opening (why this company and role, naming one concrete thing about them),
  evidence (strongest relevant experience with a metric, connected explicitly to the JD,
  adding context rather than summarising the resume), close (forward-looking, brief,
  confident). Section 5 of
  [docs/resume-writing-reference.md](../../docs/resume-writing-reference.md) holds the
  durable cover-letter guidance.

## Scope

**In scope**
- `skills/tailor-coverletter/SKILL.md`, plus a reference file if the paragraph guidance
  and checks get long.
- What the agent authors versus what is filled automatically from profile and `job.yaml`.
- Consistency rules between the letter and the resume.
- The letter's own pre-build checks (length, no fabrication, no resume regurgitation,
  company hook is real).

**Out of scope**
- Rendering and compiling (workstream 05).
- Fit analysis (workstream 06) and outreach messages (workstream 07) — a cover letter and
  a cold email are different artifacts with different audiences; do not merge them.

## Grill the user on these before implementing

1. **Always or on demand?** Is a cover letter produced for every application by default,
   or only when the user asks or the posting requires one? *Recommend on demand — most
   applications do not read it, and generating one by default costs a review cycle every
   time.*
2. **Salutation.** Default to "Dear Hiring Manager," always, or attempt a named
   recipient? Nothing in the new project discovers people. *Recommend the generic
   salutation by default, with the user able to supply a name.*
3. **Recipient city/state/zip.** The dataclass requires it, but the JD often gives only a
   metro area or nothing. Where does it come from, and what is the fallback? *Recommend
   taking `location` from `job.yaml` and allowing the field to be omitted cleanly in the
   template rather than inventing an address.*
4. **Paragraph count.** Fixed at three, or allowed to vary? *Recommend fixed at three —
   it fits one page reliably and the structure is already documented.*
5. **Company hook sourcing.** The opening needs one concrete, true thing about the
   company. `job.yaml` carries `company_hooks` derived from the JD. May the agent use
   outside knowledge, and if so must it be flagged as unverified for the user to confirm?
   *Recommend JD-derived by default; anything external is surfaced for explicit approval,
   because a wrong claim about the company is worse than a generic sentence.*
6. **Overlap with the resume.** How much repetition is acceptable? Should the skill
   require that the evidence paragraph add context the resume could not fit, rather than
   restating a bullet? *Recommend requiring added context, and listing which resume bullet
   it extends.*
7. **Date string.** Auto-filled from today's date at authoring time or at build time? Note
   a rebuild weeks later would silently change it. *Recommend written at authoring time
   into the YAML, so the artifact is stable and reproducible.*
8. **Signature image.** Keep the optional signature, and where does the path live —
   profile or per job? *Recommend profile, since it never varies by job.*
9. **Checks ownership.** Does the cover letter get its own checks reference file, or does
   it share the tailoring-checks file from workstream 03? *Recommend its own short file —
   the failure modes differ (tone, repetition, hook accuracy versus keyword coverage).*

## Done criteria

- `skills/tailor-coverletter/SKILL.md` exists and names no deleted script.
- The skill produces a `cover_letter.yaml` that the loader validates and the renderer
  compiles to a one-page PDF.
- Header comes from the profile automatically; recipient and job details come from
  `job.yaml`; only the paragraphs are authored per job.
- Every factual claim in the letter traces to a profile entry or to the JD.
- The consistency rule against `resume.yaml` is written down and checkable.
