---
name: tailor-resume
description: Tailor a resume and cover letter to a specific job description by selecting profile entries and rewriting bullets in the per-job tailoring files. Use when the user provides a job description or posting URL and wants tailored application documents.
---

# Tailor Resume + Cover Letter from a JD

## ⛔ Profile is read-only
Read `profile/` only. NEVER edit any file under `profile/`. Every job-specific change
(reworded bullets, injected keywords) goes into the tailoring files via
`dataclasses.replace()` — not the source entries.

## Steps
1. Get the real entry variable names (do not trust doc examples):
   `python scripts/update_profile.py --inventory`
2. Pick an id `{company}_{role}_{year}` (lowercase, underscores) and scaffold:
   `python scripts/new_application.py --id <id> --company "<co>" --role "<role>"`
3. Read the JD; extract company, role, top keywords, hard requirements.
4. Edit ONLY `resume/tailoring/<id>.py`:
   - `CONFIG` (which sections show)
   - `EXPERIENCE` — select entries; use `replace(ENTRY, highlights=[...])` to reword bullets around JD keywords
   - `PROJECTS` — select 2–4 most relevant
   - `SUMMARY` — a `SUMMARIES[...]` preset or a custom string that names the company
   - skills preset (`SKILLS_FULL` / `SKILLS_ML_FOCUSED` / `SKILLS_SWE_FOCUSED` / `SKILLS_RESEARCH_FOCUSED`)
5. Edit `coverletter/tailoring/<id>.py` — 3 paragraphs (hook → evidence+metric → call to action).
6. Fill `applications/jobs/<id>/job_info.py` (KEYWORDS, URL, PLATFORM).
7. Build: `python scripts/build.py --id <id> --pdf`

## Bullet & summary style
Full rules in `docs/resume-writing-reference.md` (Harvard guidelines, complete action-verb
bank, cover letter tips); condensed recap in the root `AGENTS.md`. Reworded bullets must follow it:
- **XYZ formula:** "Accomplished [X], as measured by [Y], by doing [Z]." → bullet =
  **[action verb] + [what] + [tools/how] + [quantified result]**.
- Active voice, no pronouns, no narrative; strong action verb first, metric last.
- Bold key terms with `\textbf{...}`; keep each bullet under ~200 chars.
- Tailored summary: 3–4 sentences naming the company explicitly.

## Pitfalls
- Only use entry names returned by `--inventory`; never invent variable names.
- Escape LaTeX specials in bullets: `%`→`\%`, `&`→`\&`, `$`→`\$`, `_`→`\_`, `#`→`\#`.
- Do not duplicate profile data into tailoring files — only select + `replace()`.
- Never invent metrics or facts — quantify only what is true.
