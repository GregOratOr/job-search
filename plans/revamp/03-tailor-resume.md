# Workstream 03 — `tailor-resume` Skill (Goals 2 and 3)

> **Depends on workstream 01** (profile YAML, `resume.yaml` schema, loader) and
> **workstream 02** (`job.yaml`). Do not start until 01 has landed.
>
> **Before writing anything, run a `grill-with-docs` session** (the `grilling` skill via
> `domain-modeling`): one question at a time, each with your recommended answer, resolving
> the open questions below. Look facts up in the repo yourself; put only decisions to the
> user. Do not implement until the user confirms shared understanding.

## Goal

This is the heart of the project, and the stage where bad output hurts most. Two halves:

- **Goal 2 — selection.** Read the profile (the ground truth and the only starting point)
  and the extracted JD, then decide which skills, experience entries, projects, and
  research best match what the posting asks for.
- **Goal 3 — authoring.** Write the selected material into `resume.yaml` in the exact
  shape the loader expects, with bullets rewritten to hit the JD's language without
  inventing anything that is not in the profile.

## Decisions already locked

- Output is **`resume.yaml`**, fully resolved: no imports, no `dataclasses.replace()`,
  every bullet is literal text, LaTeX written with single backslashes (`\textbf{}`, `\&`).
- Each entry carries a **`source:` id** that must resolve against the profile, and each
  bullet is marked as **taken verbatim** from the profile or **rewritten**. That
  distinction is what makes fabrication mechanically checkable.
- Skills come from the **whitelist** in `profile/skills.yaml`; a per-job subset is chosen
  here. The loader hard-fails on anything not in the inventory, so the agent cannot invent
  a skill the user does not have.
- Profile is **read-only**. Job-specific rewrites never go upstream into the profile.
- **Two audits, and only the first belongs here.** The tailoring checks — facts, keyword
  coverage, relevance, bullet length, one-page fit — live as a **reference file inside
  this skill**, cited from `SKILL.md` the way a skill cites supporting docs. The second
  audit, the hiring-manager fit report, is a separate standalone skill (workstream 06).
- Zero LLM calls in Python. The selection and rewriting happen in the agent's context; the
  only scripts involved are the loader's validation and the renderer.

## Current state

- [skills/tailor-resume/SKILL.md](../../skills/tailor-resume/SKILL.md) is the version being
  replaced. Read it first — it already encodes hard-won knowledge worth carrying over:
  the fit loop with a 3-iteration cap, the ordered trim ladder (drop least-relevant
  project, then weakest bullet, then shorten, then disable sections, then drop an
  experience entry last), and the measure-then-edit discipline of comparing against the
  previous iteration instead of trimming blind. What must change: it writes a `.py` file
  via `replace()`, it names `ai_tailor.py` as a fallback, and it references skill presets.
- [docs/resume-writing-reference.md](../../docs/resume-writing-reference.md) is the durable
  style authority — Harvard MCS rules, the XYZ formula, the full action-verb bank,
  per-section guidance. **Keep it and keep citing it.** Do not copy its contents into the
  skill; cite it.
- Profile entry ids (verify at runtime, do not trust this list): experience
  `UNITY_DEV_INGNIOUS`, `JAVA_INTERN_WINPOINT`, `FELLOWSHIP_TEESSIDE`,
  `AI_INTEGRATOR_DAKDAN`; projects `PROJ_MEDICAL_IMAGE_DENOISING`,
  `PROJ_PORTFOLIO_WEBSITE`, `PROJ_RESUME_BUILDER`, `PROJ_JOB_WORKFLOW_AUTOMATION`,
  `PROJ_XRAY_DENOISING_CAPSTONE`, `PROJ_MULTIUAV_WILDFIRE`,
  `PROJ_BRAIN_TUMOR_SEGMENTATION`, `PROJ_PMD_CAMERA_CUDA`, `PROJ_VR_FRUIT_NINJA`;
  research `RESEARCH_MARL_COORDINATION`, `RESEARCH_MARL_TRAINING`.
- A good example of the *old* output shape, useful for seeing what a well-tailored
  selection looks like:
  [private/resume/outputs/drone_geospatial_sr_ds_2026.py](../../private/resume/outputs/drone_geospatial_sr_ds_2026.py).
- Section visibility is `SectionConfig` in [resume/cv_utils.py](../../resume/cv_utils.py):
  position applied, summary, skills, experience, projects, research, education, coursework.

## Scope

**In scope**
- `skills/tailor-resume/SKILL.md` — the logical steps, when to use and when not to.
- A **selection** reference file: how to score profile entries against a JD, how many of
  each kind to include, how to order them, and when to show or hide optional sections.
- A **tailoring-checks** reference file: the pre-build self-review the agent must pass
  before handing off to build.
- Rewriting rules specific to this pipeline, on top of the style reference — what may be
  rephrased, what may never change, how to inject JD keywords honestly.
- The `resume.yaml` the skill produces, validated by the loader from workstream 01.

**Out of scope**
- Rendering, compiling, and the page-count loop mechanics (workstream 05 — this skill will
  call into it, but does not own it).
- The hiring-manager fit report (workstream 06).
- Cover letter content (workstream 04).

## The fabrication problem, stated plainly

The single worst failure mode is a resume bullet that reads well and is not true. The
`source` + verbatim/rewritten marking exists so that a reviewer — human or agent — can
mechanically list every piece of new text and compare it to the profile original. The
tailoring-checks file must make that comparison a required step, not an optional one.

A rewrite may: reorder, compress, change the action verb, surface a tool or metric that is
already present in the profile entry, and adopt the JD's vocabulary for a thing the user
actually did. A rewrite may not: add a metric that does not appear in the profile, claim a
tool the entry never mentions, upgrade scope or seniority, or turn a contribution into
sole ownership.

## Grill the user on these before implementing

1. **Selection budget.** Fixed caps (for example 2–3 experience entries, 2–4 projects,
   5 bullets max per entry) or a judgment-based budget driven by the one-page constraint?
   *Recommend soft targets plus hard caps, so the agent has room but the page fit is not
   left to chance.*
2. **Scoring method.** Should the skill prescribe an explicit scoring rubric (keyword
   overlap, recency, seniority signal, domain match) with the agent showing its scores, or
   just describe the judgment and let the agent exercise it? *Recommend a lightweight
   explicit rubric with the scores shown — it makes a wrong selection debuggable instead
   of mysterious.*
3. **Selection transparency.** Should `resume.yaml` record *why* each entry was chosen, or
   should the rationale stay in chat? *Recommend a short `rationale` per entry in the YAML
   — it is exactly what the fit-audit and the user want when reviewing.*
4. **Summary.** The profile has a `SUMMARIES` dict of preset variants. Keep presets, always
   write a custom per-job summary naming the company, or presets as a starting point?
   *Recommend custom per job, grounded in the profile's factual claims.*
5. **Research and coursework sections.** Auto-decide visibility from the JD, or always ask?
   *Recommend auto-decide with the rule stated in the selection reference (research on
   when the JD asks for research or the domain matches; coursework normally off).*
6. **Keyword coverage target.** Is there a numeric bar (for example every hard requirement
   addressed by at least one bullet), or is it qualitative? *Recommend the requirement-
   coverage rule, since `job.yaml` already lists requirements and it makes the check
   mechanical.*
7. **Approval gate.** Does the user review `resume.yaml` before the build, after the PDF,
   or not at all in the default flow? *Recommend reviewing the YAML before build — fixing
   text is cheap there and expensive after.*
8. **Reference file count.** Two files (selection, tailoring-checks) or more, and what
   exactly goes in the main `SKILL.md` versus a reference? *Recommend keeping `SKILL.md`
   short enough to read in one pass, with detail pushed into the two references.*
9. **Re-tailoring.** When the user says "redo this, emphasise X", does the skill start
   from the existing `resume.yaml` or from scratch? *Recommend editing the existing file so
   prior manual fixes survive.*

## Done criteria

- `skills/tailor-resume/SKILL.md` plus its reference files exist, cite
  `docs/resume-writing-reference.md` rather than duplicating it, and never mention any
  deleted script.
- Running the skill against a real JD produces a `resume.yaml` that the loader validates
  without errors on the first attempt.
- Every rewritten bullet is traceable to a profile entry, and the checks file forces that
  comparison before build.
- The fit-loop knowledge from the old skill (iteration cap, trim ladder, measure before
  editing) is carried into the new flow rather than lost.
- Selection caps, section-visibility rules, and the keyword-coverage bar are written down,
  not left to the agent's discretion.
