# Profile Context

This directory is the **single source of truth** for all personal data.
It is split into focused modules so agent updates are surgical — touching
only the relevant file.

## File Map

```
profile/
├── header.py       ← HEADER (CV) + CL_HEADER (cover letter) — contact info
├── education.py    ← OSU_MS, VIT_BTECH — degree entries
├── experience.py   ← AI_INTEGRATOR_DAKDAN, ... — work history (run --inventory for live list)
├── projects.py     ← PROJ_XRAY_DENOISING_CAPSTONE, ... — project portfolio (run --inventory)
├── skills.py       ← SKILLS_FULL, SKILLS_ML_FOCUSED, etc. — skill presets
├── summaries.py    ← SUMMARIES dict — professional summary variants
├── research.py     ← research entries (empty until first paper)
├── coursework.py   ← COURSEWORK_OSU, COURSEWORK_VIT
├── master_data.py  ← thin re-export of all the above (import point for tailoring files)
└── CHANGELOG.md    ← append one line here after EVERY edit to any profile file
```

## Golden Rule

**This directory is READ-ONLY for agents unless the user gives an explicit command in the
current conversation to change a specific profile file.** Tailoring, keyword rewrites, and
job-specific edits must NEVER modify anything here — they go into `resume/tailoring/{id}.py`
via `dataclasses.replace()`. Only edit `profile/` when the user explicitly asks to update
their profile (then follow the workflows below and append to `CHANGELOG.md`).

Only add data here. **Never** add data to tailoring files directly.
When a tailoring file needs a new bullet variation, use `dataclasses.replace()`.

---

## How to Write Bullets & Summaries

Follow the style guide for every `highlights` list and summary. The **full rule set** —
complete Harvard guidelines, the entire action-verb bank, per-section and cover letter tips —
lives in `docs/resume-writing-reference.md`. The root `AGENTS.md` has a condensed recap.
**Open the reference before editing entries.**

Quick reference:
- **XYZ formula:** "Accomplished [X], as measured by [Y], by doing [Z]." → in a bullet:
  **[Action verb] + [what] + [tools/how] + [quantified result]**.
- Active voice, no pronouns, no narrative; start with an action verb, end with a metric.
- Past tense for finished work (present tense only for a current role).
- Summaries: 3–4 sentences (who you are → what you build → what you want), no bullets.
- Bold key terms with `\textbf{...}`; escape LaTeX specials (`%→\%`, `&→\&`, `$→\$`, `_→\_`).

---

## Agent Workflows — How to Update the Profile

### Add a new work experience entry

1. Open `profile/experience.py`
2. Copy the template block at the top of the file
3. Fill in `role`, `company`, `date`, and `highlights`
4. Choose a variable name: `COMPANY_ROLE_YEAR` (e.g. `NVIDIA_INTERN_2026`)
5. Add the variable name to the `__all__` export list in `profile/master_data.py`
6. Append to `profile/CHANGELOG.md`:
   `| YYYY-MM-DD | experience.py | Added NVIDIA_INTERN_2026 (NVIDIA Intern, Jun 2026) |`

### Add a new project

1. Open `profile/projects.py`
2. Copy the template block
3. Fill in `title`, `organization`, `date`, and `highlights`
4. Variable name: `PROJ_{SHORTNAME}` (e.g. `PROJ_DIFFUSION_2026`)
5. Add to `profile/master_data.py` imports and `__all__`
6. Append to `profile/CHANGELOG.md`

### Update an existing bullet point

1. Open the relevant file (e.g. `profile/experience.py`)
2. Edit the specific string in the `highlights` list
3. Append to `profile/CHANGELOG.md`:
   `| YYYY-MM-DD | experience.py | Updated AI_INTEGRATOR_DAKDAN bullet 2 (added metric) |`

### Update contact info

1. Open `profile/header.py`
2. Edit both `HEADER` and `CL_HEADER` to keep them consistent
3. Append to `profile/CHANGELOG.md`

### Add a new skill

1. If the skill isn't in any Enum yet: add it to the relevant Enum class in `resume/cv_utils.py`
2. Open `profile/skills.py`
3. Add `.add(EnumClass.new_value)` to the relevant builder chain in each preset where it belongs
4. Append to `profile/CHANGELOG.md`

### Add a new summary variant

1. Open `profile/summaries.py`
2. Add a new key-value pair to the `SUMMARIES` dict
3. Append to `profile/CHANGELOG.md`

---

## Validation

After any edit, run:
```bash
python scripts/update_profile.py
```
This validates all imports, shows the full inventory, and lists recent changelog entries.
For a quick import-only check:
```bash
python scripts/update_profile.py --validate
```
