# Resume Tailoring Files

Each `.py` file here is a thin configuration layer over `profile/master_data.py`.

## What to Edit in a Tailoring File

| Section      | What to change                                          |
|--------------|---------------------------------------------------------|
| `JOB_ID`     | The application ID — must match the file name           |
| `COMPANY`    | Company name shown in position header                   |
| `ROLE`       | Job title shown in position header                      |
| `CONFIG`     | `SectionConfig` — toggle which sections appear          |
| `EXPERIENCE` | Select entries; use `replace()` to tweak bullets        |
| `PROJECTS`   | Select 2–4 most relevant projects                       |
| `SUMMARY`    | Pick from `SUMMARIES` dict or write a custom string     |
| `skills`     | Choose `SKILLS_FULL`, `SKILLS_ML_FOCUSED`, etc.         |

## What NOT to Change

- Do not redefine `HEADER`, `OSU_MS`, `VIT_BTECH` — they come from master_data.
- Do not add new `ExperienceEntry` or `ProjectEntry` objects — add to master_data first.
- Do not change `OUTPUT_FILE` format — it must be `resume/outputs/{JOB_ID}.tex`.

## Using replace() for Bullet Overrides

Reworded bullets follow the style guide (full rules in `docs/resume-writing-reference.md`;
condensed recap in the root `AGENTS.md`): XYZ formula ("Accomplished [X], as measured by [Y],
by doing [Z]"), action verb first, metric last, active voice, key terms in `\textbf{...}`,
under ~200 chars.

```python
from dataclasses import replace
from profile.master_data import AI_INTEGRATOR_DAKDAN  # real names: scripts/update_profile.py --inventory

# Keep everything except highlights
EXP_TAILORED = replace(AI_INTEGRATOR_DAKDAN, highlights=[
    "Reworded bullet 1 matching the job description keywords.",
    "Reworded bullet 2 with quantified impact.",
])
```

## Listing Convention

The order of entries in `EXPERIENCE` and `PROJECTS` lists determines the order
they appear in the PDF — most relevant first, not necessarily chronological.

## Creating a New Tailoring File

```bash
python scripts/new_application.py --id <id> --company <co> --role <role>
```

This copies `_template.py` and pre-fills `JOB_ID`, `COMPANY`, and `ROLE`.
