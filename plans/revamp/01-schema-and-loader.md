# Workstream 01 — YAML Schema, Loader, and Profile Migration

> **You are implementing the foundation of a revamp.** Workstreams 02–09 all depend on this
> one. Nothing else can start until the schema and loader exist and are proven.
>
> **Before writing any code, run a `grill-with-docs` session** (the `grilling` skill driven
> through the `domain-modeling` skill): interview the user one question at a time, with your
> recommended answer attached to each, resolving the open questions at the bottom of this
> file. Look up facts yourself in the repo; only put *decisions* to the user. Do not
> implement until the user confirms shared understanding.

## Why this revamp exists

The project generates tailored resumes, cover letters, and outreach messages from a
single source of truth. It grew too many moving parts — discovery, research, contact
finding, follow-ups, tracking, a batch pipeline, and LLM calls embedded in Python — and
any one of them deviating produced wrong output. The revamp narrows the project to five
things: JD intake, profile-grounded selection, resume generation, reworked skills, and
outreach templates.

## Decisions already locked (do not re-litigate)

- **Zero LLM calls in Python.** Scripts are mechanical and deterministic. The agent is the
  only reasoning engine. `llm_provider.py`, `json_llm.py`, `ai_tailor.py`, `audit.py`,
  `research.py`, `followup.py` are all being deleted in workstream 09.
- **Profile becomes YAML.** `private/profile/*.py` converts to YAML files. Rationale:
  the user edits them by hand, and the agent reads them cheaply without executing code.
- **The tailored resume is `resume.yaml`**, fully resolved — no imports, no
  `dataclasses.replace()`, every bullet literal text. It carries `source:` ids for
  provenance and marks each bullet as either taken verbatim from the profile or rewritten.
- **No generated `.py` intermediate.** The loader builds `CV` / `CoverLetter` dataclass
  objects in memory directly from YAML and hands them to the existing renderers.
- **Skills are a whitelist.** `profile/skills.yaml` holds the full inventory; a per-job
  subset is selected in `resume.yaml`; the loader hard-fails on any skill not in the
  inventory.
- **Migration is converter-based**, verified against a current output, then the converter
  is deleted.

## Current state — read these before deciding anything

**Dataclasses (these survive unchanged — the loader targets them):**
- [resume/cv_utils.py](../../resume/cv_utils.py) — `SectionConfig`, `HeaderInfo`,
  `PositionInfo`, `EducationEntry`, `SkillCategory`, `ExperienceEntry`, `ProjectEntry`,
  `CourseworkEntry`, `ResearchEntry`, `CV`. Also holds the skill `Enum` classes
  (`Competencies`, `Languages`, `Libraries`, `Frameworks`, `Tools`) and
  `EnumStringBuilder`, which the YAML pivot replaces.
- [coverletter/cl_utils.py](../../coverletter/cl_utils.py) — `CLHeader`, `RecipientInfo`,
  `JobInfo`, `LetterContent`, `CoverLetter`.

**Renderers (survive; only their input path changes):**
- `resume/cv2latex.py` — `generate_tex_file(data_file, output_file)` currently *imports a
  `.py` module* and reads `cv_data` off it. This entry point must grow a YAML path.
- `coverletter/cl2latex.py` — same shape for `cover_letter` data.

**Profile as it exists today** (`private/profile/`, the real data; the repo-root `profile/`
is the public placeholder):
- `header.py` → `HEADER` (`HeaderInfo`), `CL_HEADER` (`CLHeader`)
- `education.py` → `OSU_MS`, `VIT_BTECH`
- `experience.py` → `UNITY_DEV_INGNIOUS`, `JAVA_INTERN_WINPOINT`, `FELLOWSHIP_TEESSIDE`,
  `AI_INTEGRATOR_DAKDAN`
- `projects.py` → `PROJ_MEDICAL_IMAGE_DENOISING`, `PROJ_PORTFOLIO_WEBSITE`,
  `PROJ_RESUME_BUILDER`, `PROJ_JOB_WORKFLOW_AUTOMATION`, `PROJ_XRAY_DENOISING_CAPSTONE`,
  `PROJ_MULTIUAV_WILDFIRE`, `PROJ_BRAIN_TUMOR_SEGMENTATION`, `PROJ_PMD_CAMERA_CUDA`,
  `PROJ_VR_FRUIT_NINJA`
- `research.py` → `RESEARCH_MARL_COORDINATION`, `RESEARCH_MARL_TRAINING`
- `skills.py` → presets `SKILLS_FULL`, `SKILLS_ML_FOCUSED`, `SKILLS_SWE_FOCUSED`,
  `SKILLS_RESEARCH_FOCUSED`, each a list of `SkillCategory` built through
  `EnumStringBuilder` chains
- `summaries.py` → `SUMMARIES` dict
- `coursework.py` → `COURSEWORK_OSU`, `COURSEWORK_VIT`
- `master_data.py` → re-export point; `CHANGELOG.md` → edit log

Confirm this list at runtime rather than trusting it: `uv run scripts/validate_profile.py
--inventory`.

**The escaping problem this pivot solves.** Look at
[private/resume/outputs/drone_geospatial_sr_ds_2026.py](../../private/resume/outputs/drone_geospatial_sr_ds_2026.py):
because bullets are Python string literals, LaTeX commands are double-escaped —
`\\textbf{...}`, `\\&`. Agents get this wrong constantly. In single-quoted YAML the text
is literal, so it reads exactly as LaTeX does: `\textbf{...}`, `\&`.

**Path routing:** [scripts/data_paths.py](../../scripts/data_paths.py) routes reads/writes
to `private/` when the overlay submodule is present, else to the repo-root template dirs.
Key functions: `data_path()`, `resolve_path()`, `document_py/tex/pdf(kind, job_id)`,
`bootstrap_paths()`, `add_overlay_cli_flags()`. The YAML world needs the equivalent, and
the `document_py` concept largely goes away.

## Scope

**In scope**
1. YAML schema for the profile — one file per current module, or a justified regrouping.
2. YAML schema for `resume.yaml` and `cover_letter.yaml` (the per-job tailored documents).
3. A loader module that reads YAML and returns populated `CV` / `CoverLetter` dataclasses.
4. Validation performed by the loader: provenance (`source` ids resolve against the
   profile), skill whitelist, required fields, and type/shape errors — all with messages
   precise enough that an agent can self-correct without a human.
5. Wiring `cv2latex.py` / `cl2latex.py` to accept the dataclasses from the loader.
6. A one-shot `py -> yaml` converter for the real profile, plus the verification that the
   converted YAML renders a byte-identical `.tex` to a current known-good output. Delete
   the converter afterwards.
7. Updating `validate_profile.py` (or its replacement) to validate the YAML profile and
   print the inventory the tailoring skill depends on.

**Out of scope** — belongs to later workstreams
- Any skill authoring (03–08), the JD schema `job.yaml` (02), page-count enforcement (05),
  deleting the retired scripts and docs (09).

## Shape to aim for (starting point, not a mandate)

```yaml
# resume.yaml  — a tailored resume, fully resolved
job_id: nvidia_ml_2026
sections:
  summary: true
  research: false
  coursework: false
summary: 'Machine learning engineer focused on \textbf{inference optimization}...'
skills:
  Core Competencies: [Deep Learning, GPU Optimization, MLOps]
  Languages: [Python3, C++]
experience:
  - source: AI_INTEGRATOR_DAKDAN
    bullets:
      - use_profile: 1          # profile bullet index 1, verbatim
      - rewrite: 'Built an \textbf{LLM outcome classifier} scoring call transcripts...'
projects:
  - source: PROJ_MULTIUAV_WILDFIRE
    title_override: 'Multi-UAV Wildfire Mitigation via Q-Learning \& Difference Rewards'
    bullets:
      - use_profile: 0
```

The `use_profile` / `rewrite` distinction is load-bearing: it tells the audit exactly which
text is new and therefore needs a fabrication check, and it lets unchanged content stay
in one place.

## Grill the user on these before implementing

1. **Bullet reference style.** `use_profile: <index>` is brittle — reordering profile
   bullets silently changes the resume. Alternatives: stable per-bullet ids in the profile
   YAML, or requiring the full text be copied even when unchanged (simple, but loses the
   unchanged/rewritten distinction unless diffed). *Recommend stable bullet ids.*
2. **Profile file layout.** Keep the one-file-per-concern split (`experience.yaml`,
   `projects.yaml`, …) or consolidate? *Recommend keeping the split — it makes hand edits
   and diffs surgical.*
3. **Entry ids.** Keep the existing SCREAMING_SNAKE names (`AI_INTEGRATOR_DAKDAN`) so old
   bundles and the changelog stay readable, or switch to kebab-case? *Recommend keeping
   them — zero-cost continuity.*
4. **Skills structure.** Categories are currently fixed by the enum classes
   (Core Competencies / Languages / Frameworks / Libraries / Tools). Should categories be
   free-form in `skills.yaml`, or a fixed set? Should the inventory record anything beyond
   the display string (proficiency, aliases for keyword matching)? *Recommend fixed
   categories, display string plus optional `aliases` used for JD keyword matching.*
5. **Validation severity.** Which failures are hard errors versus warnings — unknown skill,
   unknown `source`, bullet over the char limit, unescaped LaTeX special? *Recommend hard
   error for unknown skill/source and unescaped specials; warning for length.*
6. **LaTeX escaping ownership.** Does the agent write already-escaped LaTeX into YAML (as
   today), or does the loader escape on the way out and the agent writes plain text with a
   small markup vocabulary? *Recommend the agent writes LaTeX, loader validates — a full
   escape layer would have to understand `\textbf{}` anyway.*
7. **Cover letter YAML.** How much of `CLHeader` / `RecipientInfo` comes from the profile
   automatically versus being written per job? *Recommend header from profile, recipient
   and job from `job.yaml`, only the paragraphs authored per job.*
8. **Where the loader lives** and what the module boundary is — one `loader.py`, or split
   schema/validation/loading. *Recommend one module with a narrow public surface:
   `load_profile()`, `load_resume(job_id)`, `load_cover_letter(job_id)`.*
9. **Schema versioning.** Add a `schema_version` field now, or not? *Recommend yes, one
   line, cheap insurance while the schema is still moving.*

## Done criteria

- Profile YAML exists under the private overlay and the converter's output was verified by
  rendering a `.tex` byte-identical to a pre-migration known-good build; the converter is
  then deleted.
- `load_profile()` returns validated in-memory objects, and the inventory command lists
  every entry id the tailoring skill will need.
- A hand-written `resume.yaml` renders end-to-end to a PDF through the existing renderer.
- Every validation failure mode has a test and an error message that names the file, the
  field, and the fix.
- Invalid input cannot reach the renderer: unknown `source`, unknown skill, and missing
  required fields all fail loudly before LaTeX is generated.
- The glossary in [CONTEXT.md](../../CONTEXT.md) gains the new terms
  (`profile YAML`, `tailored document YAML`, `provenance`, `skill inventory`) as they are
  settled during the grill session.
