# Resume Tailoring Files

Scaffold templates live here (`_template.py`). **Per-job source files** are
created under `resume/outputs/{id}.py` (or `private/resume/outputs/` when the
overlay is present), next to their `.tex` / `.pdf` siblings.

## What to Edit in a Per-Job Source File

| Section      | What to change                                                  |
|--------------|-----------------------------------------------------------------|
| `JOB_ID`     | The application ID — must match the file name                   |
| `COMPANY`    | Company name shown in position header                           |
| `ROLE`       | Job title shown in position header                              |
| `CONFIG`     | `SectionConfig` — toggle which sections appear                  |
| `EXPERIENCE` | Select entries; use `replace()` to tweak bullets                |
| `PROJECTS`   | Select 2–4 most relevant projects                               |
| `SUMMARY`    | Pick from `SUMMARIES` dict or write a custom string              |
| `skills`     | Choose `SKILLS_FULL`, `SKILLS_ML_FOCUSED`, etc.                 |
| `OUTPUT_FILE`| Overlay-aware path set by scaffold/ai_tailor; `build.py` also forces it |

## What NOT to Change

- Do not redefine `HEADER`, education entries — they come from master_data.
- Do not add new `ExperienceEntry` or `ProjectEntry` objects — add to master_data first.
- Do not hardcode a public-only `OUTPUT_FILE` when the private overlay is active.

## Using replace() for Bullet Overrides

Reworded bullets follow the style guide (full rules in `docs/resume-writing-reference.md`;
condensed recap in the root `AGENTS.md`): XYZ formula ("Accomplished [X], as measured by
[Y], by doing [Z]"), action verb first, metric last, active voice, key terms in `\textbf{...}`,
under ~200 chars.

```python
from dataclasses import replace
from profile.master_data import EXAMPLE_ML_ENGINEER_ACME  # real names: uv run scripts/validate_profile.py --inventory

# Keep everything except highlights
EXP_TAILORED = replace(EXAMPLE_ML_ENGINEER_ACME, highlights=[
    "Reworded bullet 1 matching the job description keywords.",
    "Reworded bullet 2 with quantified impact.",
])
```

## Listing Convention

The order of entries in `EXPERIENCE` and `PROJECTS` lists determines the order
they appear in the PDF — most relevant first, not necessarily chronological.

## Creating a New Application Source

```bash
uv run scripts/new_application.py --id <id> --company <co> --role <role>
```

This copies `_template.py` into `resume/outputs/{id}.py` (under `private/` when present)
and pre-fills `JOB_ID`, `COMPANY`, `ROLE`, and an overlay-aware `OUTPUT_FILE`.
