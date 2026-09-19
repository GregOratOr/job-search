# Workstream 02 — `intake-jd` Skill (Goal 1)

> **Depends on workstream 01** (YAML schema and loader) for conventions, though this
> skill's output `job.yaml` is its own schema.
>
> **Before writing anything, run a `grill-with-docs` session** (the `grilling` skill via
> `domain-modeling`): one question at a time, each with your recommended answer, resolving
> the open questions below. Look facts up in the repo yourself; put only decisions to the
> user. Do not implement until the user confirms shared understanding.

## Goal

Given a job description as **raw text, a screenshot, or a URL**, produce the two files
every downstream stage reads: the JD as text, and the extracted structured facts.

This is the first stage of the pipeline. Everything after it — resume tailoring, cover
letter, fit audit, outreach — consumes its output and never re-reads the original input.
A bad extraction here silently poisons every later stage, so the extraction must be
inspectable and correctable by hand.

## Decisions already locked

- The three input paths **converge on one artifact**: `jd.md`. A screenshot is transcribed
  by the agent's own vision into `jd.md`. A URL is fetched with **harness-native web
  only** — `scripts/web.py` is deleted, no fetch script is coming back. If the harness has
  no web access, the user pastes text.
- Structured extraction lands in `job.yaml`, a file, not chat context — so it can be
  inspected, hand-corrected, and the later stages re-run without redoing intake.
- Zero LLM calls in Python. This skill is pure agent work plus, at most, a tiny mechanical
  helper for folder scaffolding.
- Stages pass state through files in the job folder; each is independently re-runnable.

## Current state

- `applications/jobs/<id>/` is the per-job folder (routed to `private/applications/jobs/`
  by [scripts/data_paths.py](../../scripts/data_paths.py)). Existing folders such as
  `private/applications/jobs/microsoft_swe_qrt_2026/` show the old layout.
- Today JD text lands in `jd.txt` and extraction in a Python file `job_info.py`, written
  by the deleted `ai_tailor.py`. The new equivalents are `jd.md` and `job.yaml`.
- Folder scaffolding was `scripts/new_application.py` (being deleted) — it copied
  `applications/jobs/_template/`.
- Id convention in use: `{company}_{role}_{year}`, lowercase with underscores, e.g.
  `nvidia_dl_swe_tensorrt_ncg_2026`.
- Old job folders are archived untouched in workstream 09; do not migrate them.

## Scope

**In scope**
- The `intake-jd` skill: `skills/intake-jd/SKILL.md`, plus reference files if the
  extraction rules get long enough to hurt the main file's readability.
- The `job.yaml` schema and what belongs in it.
- Transcription rules for screenshots (what to preserve, what to drop, how to handle
  multi-screenshot postings and unreadable regions).
- Job folder creation and the id convention.
- Behaviour when intake is re-run over an existing folder.

**Out of scope**
- Selecting profile entries or writing any resume content (workstream 03).
- Discovering jobs. Discovery is deleted; the user always supplies the posting.
- Tracking application status. `track.py` and the tracker are deleted.

## What `job.yaml` is for

Each downstream consumer needs something different, and the schema should be driven by
those needs rather than by what a JD happens to contain:

- **tailor-resume** needs the keywords and hard requirements to select and rewrite against.
- **tailor-coverletter** needs company, role, and something concrete and specific about
  the company or team to hook the opening paragraph on.
- **fit-audit** needs the requirements list to judge fit and name the gaps.
- **outreach** needs company, role, team, and location to make messages specific.
- **build-documents** needs company and role for the header and the position line.

Starting shape:

```yaml
job_id: nvidia_ml_2026
company: NVIDIA
role: Deep Learning Software Engineer
team: TensorRT Inference
location: Santa Clara, CA (Hybrid)
source: url | screenshot | text
source_url: https://...
seniority: new-grad
keywords: [TensorRT, CUDA, quantization, inference optimization]
hard_requirements:
  - 'MS in CS or related field'
nice_to_have:
  - 'Published research in model compression'
company_hooks:
  - 'Team ships the inference path behind ...'
```

## Grill the user on these before implementing

1. **Agent-only or is there a script?** Intake is pure reasoning, so the skill could be
   entirely agent-driven with no Python at all, apart from creating the folder. *Recommend
   no script — the agent creates the folder and writes both files. One less thing to drift.*
2. **Job id derivation.** Auto-derive from company+role+year, or always confirm with the
   user? What about collisions with an existing folder? *Recommend auto-derive, show the
   id, and stop for confirmation if the folder already exists.*
3. **`jd.md` fidelity.** Verbatim transcription including boilerplate (benefits, EEO
   statements, legal), or a cleaned version keeping only the substantive sections? Note
   that discarded text cannot be recovered later without the original. *Recommend verbatim
   for text and URL inputs; for screenshots, transcribe everything legible and mark
   unreadable regions explicitly rather than guessing.*
4. **Keyword extraction discipline.** Should `keywords` be strictly terms literally present
   in the JD, or may the agent normalise and expand (e.g. "LLMs" → "large language models",
   "PyTorch")? The resume audit later checks keyword coverage, so invented keywords inflate
   a false score. *Recommend literal terms only, with an optional separate
   `normalized_keywords` list so the distinction stays visible.*
5. **Requirement classification.** Splitting hard requirements from nice-to-haves is a
   judgment call the JD often does not make cleanly. Keep the split, or keep one list with
   a flag per item? *Recommend one `requirements` list with `must: true|false` per item —
   less lossy, and the fit-audit reads it directly.*
6. **Company hooks.** Should the agent pull these only from the JD, or may it use its own
   knowledge of the company? Hooks end up in the cover letter, so an inaccurate one is a
   credibility risk. *Recommend JD-derived only by default, with anything else explicitly
   marked as unverified.*
7. **Re-run semantics.** When intake runs again over an existing folder: overwrite,
   refuse, or diff and ask? Remember the user may have hand-corrected `job.yaml`.
   *Recommend refuse by default and require an explicit force, because hand corrections
   are exactly what re-running would destroy.*
8. **Extraction confirmation gate.** Does intake stop and show the extracted `job.yaml`
   for approval before tailoring starts, or flow straight through? *Recommend showing a
   short summary and continuing unless run inside the orchestrator's gated mode — the
   downstream audit catches extraction errors too.*
9. **Multiple screenshots** of one long posting, and screenshots that include unrelated
   browser chrome — what should the skill say about assembling them? *Recommend explicit
   ordering by the user, transcribed into one continuous `jd.md`.*

## Done criteria

- `skills/intake-jd/SKILL.md` exists, states when to use and when not to use, and covers
  all three input paths with the same terminating artifacts.
- Running it on pasted text, on a screenshot, and on a URL each produces
  `applications/jobs/<id>/jd.md` and `applications/jobs/<id>/job.yaml`.
- The `job.yaml` schema is documented in one place and every field has a named downstream
  consumer — fields nothing reads should not exist.
- Re-run behaviour is defined and does not silently destroy hand edits.
- The new terms are reflected in [CONTEXT.md](../../CONTEXT.md).
