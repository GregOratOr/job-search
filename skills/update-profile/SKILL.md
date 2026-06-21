---
name: update-profile
description: Add or edit entries in the profile/ single source of truth (experience, projects, skills, summaries, education, header) ONLY when the user explicitly commands a profile change. Use when the user says to add a new job/project/skill or update their contact info.
---

# Update the Profile (explicit command only)

## ⚠️ Precondition
Editing `profile/` is allowed ONLY when the user explicitly asks to change their profile
(e.g. "add my new internship", "update my email"). Any other task treats `profile/` as
read-only. If unsure, ask before writing to `profile/`.

## Steps
1. Open the relevant file:
   - new job → `profile/experience.py` (var: `COMPANY_ROLE_YEAR`)
   - new project → `profile/projects.py` (var: `PROJ_SHORTNAME`)
   - new skill → add the enum value in `resume/cv_utils.py` first if missing, then
     reference it in `profile/skills.py`
   - new summary → `profile/summaries.py` (`SUMMARIES` dict)
   - contact info → `profile/header.py` (keep `HEADER` and `CL_HEADER` consistent)
2. For a new experience/project/research entry, also register it in
   `profile/master_data.py` (`__all__` + the matching `*_REGISTRY` dict, same order).
3. Validate: `python scripts/update_profile.py`
4. Append one line to `profile/CHANGELOG.md`:
   `| YYYY-MM-DD | <file> | <what changed> |`

## Bullet & summary style
When writing `highlights` or summaries, follow the style guide. Full rules (Harvard
guidelines, complete action-verb bank, per-section tips) are in
`docs/resume-writing-reference.md`; condensed recap in the root `AGENTS.md`:
- **XYZ formula:** "Accomplished [X], as measured by [Y], by doing [Z]." → bullet =
  **[action verb] + [what] + [tools/how] + [quantified result]**.
- Active voice, no pronouns, no narrative; action verb first, metric last; past tense
  for finished work (present only for a current role).
- Summaries: 3–4 sentences (who you are → what you build → what you want), no bullets.
- Bold key terms with `\textbf{...}`.

## Pitfalls
- Never add data to tailoring files — that's what `replace()` overrides are for.
- Forgetting the registry entry hides the new var from the AI/tailoring tools.
- Escape LaTeX specials in bullets: `%`→`\%`, `&`→`\&`, `$`→`\$`, `_`→`\_`, `#`→`\#`.
