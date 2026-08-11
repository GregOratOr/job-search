---
name: update-profile
description: Edit the profile single source of truth (experience, projects, skills, summaries, education, header, research, coursework) only when the user explicitly commands a profile change. Use when the user asks to add or update a job, project, skill, summary, or contact info in their profile — never for job-specific resume tailoring.
---

# Update Profile (gated)

Surgical edits to `profile/` under an explicit **gate**. Job-specific rewrites belong
in `resume/outputs/<id>.py` via `dataclasses.replace()` — refuse those and route to
`tailor-resume`.

## Gate

Proceed only when the user names **what** to change (a role/company/project/skill/
contact field, or "update my profile with …"). Ambiguous asks ("make my resume
stronger", "add CUDA keywords for this JD") → refuse; that is tailoring.

If facts are incomplete (missing dates, metrics, company spelling), ask once before
writing. Do not invent metrics or employers.

**Scope:** add and edit only. Renames and deletes need an extra explicit confirm —
they can break existing `resume/outputs/<id>.py` imports. Never silently remove a var.

## Paths

Overlay-aware: when `private/profile/` exists, edit there (the live source of truth).
Public `profile/` is the template tree for contributors without the submodule.

## Steps

1. **Confirm the gate** (above). If it fails, stop.
2. **Inventory** — discover live variable names (do not trust doc examples):
   `uv run scripts/validate_profile.py --inventory`
3. **Style pre-read** — before writing any `highlights` or summary, read
   `docs/resume-writing-reference.md`.
4. **Edit the right module** — file map and copy-template recipes:
   `profile/AGENTS.md` (or `private/profile/AGENTS.md` when the overlay is live).
   Typical targets: `experience.py`, `projects.py`, `skills.py`, `summaries.py`,
   `header.py`, `education.py`, `research.py`, `coursework.py`. New skills may need
   an Enum value in `resume/cv_utils.py` first.
5. **Register new entries** in `master_data.py`: matching `*_REGISTRY` dict
   (`EXPERIENCE_REGISTRY` / `PROJECT_REGISTRY` / `RESEARCH_REGISTRY`) **and** `__all__`,
   same order as sibling entries. Edits to existing entries skip this step.
6. **Validate:** `uv run scripts/validate_profile.py`
7. **Changelog** — append one line to `profile/CHANGELOG.md`:
   `| YYYY-MM-DD | <file> | <what changed> |`

Completion criterion: validate passes; every new entry appears in both the registry
and inventory; CHANGELOG has today's line; no new facts that the user did not supply.

## Out of scope

- Tailoring / keyword injection for a JD → `tailor-resume` / `tailor-coverletter`
- Editing `resume/outputs/` or `coverletter/outputs/` under this skill's name
