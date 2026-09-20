---
name: tailor-resume
description: Tailor a resume to a specific job description — select profile entries, rewrite bullets around the JD's keywords, and deliver a validated resume.yaml. Use when the user provides a JD or posting URL and wants a tailored resume, or when an orchestrating skill dispatches the resume-tailoring step.
---

# Tailor Resume

You (the agent) do the tailoring reasoning yourself: read the JD, judge which profile entries fit, rewrite the bullets. Zero LLM calls in Python. The only scripts involved are the loader's validation and the renderer.

**Deliverable:** `applications/jobs/<id>/resume.yaml` — fully resolved, validated by `loader.py`, ready for `build.py`.

## ⛔ Profile is read-only

Read `profile/` only. Every job-specific change — reworded bullets, injected keywords — goes into `resume.yaml`, never into the source entries.

## Date format rule (CRITICAL)

All dates in `profile/` YAML files MUST use compact 3-letter months: `Jan`, `Feb`, `Mar`, `Apr`, `May`, `Jun`, `Jul`, `Aug`, `Sep`, `Oct`, `Nov`, `Dec`. Example: `Feb 2026 -- Mar 2026`, `Sep 2024 -- Dec 2025`. This ensures visual consistency across experience, projects, and education sections in the rendered PDF. Update `profile/experience.yaml`, `profile/projects.yaml`, `profile/education.yaml` to this format before tailoring.

## LaTeX escaping in YAML

In `resume.yaml` and `profile/` YAML files: use double backslash for literal backslash in LaTeX output.
- `W\\&B` in YAML → `W\&B` in LaTeX → renders `W&B`
- `b\\_min` → `b\_min`
- `40\\%` → `40\%`
The `loader.py` auto-escapes skill items; write them readable (`C#`, `Weights & Biases`).

## Reference files (read these first)

- `skills/tailor-resume/selection.md` — scoring rubric, budgets, section visibility, ordering
- `skills/tailor-resume/tailoring-checks.md` — pre-build self-review (facts, keyword coverage, bullet length, one-page fit)
- `skills/tailor-resume/RESUME_GUIDELINES.md` — style authority (XYZ, Harvard MCS, verb bank, per-section rules)

## Steps

1. **Inventory.** Get real entry variable names:
   `uv run scripts/validate_profile.py --inventory`
2. **Read the JD** (`applications/jobs/<id>/jd.txt` + `job.yaml`): extract company, role, hard requirements, nice-to-haves, normalized keywords, company hooks.
3. **Read reference files** above.
4. **Selection** (Goal 2). Score every profile entry against the JD using the rubric in `selection.md`. Pick entries within budgets. Record a short `rationale` per entry in `resume.yaml`.
5. **Authoring** (Goal 3). Write `resume.yaml` with:
   - `position` (role)
   - `sections` (visibility flags per `selection.md` rules)
   - `summary` — custom per job, 3–4 sentences, grounded in profile facts; include company name at your discretion (may affect application quality in some cases)
   - `skills` — subset from `profile/skills.yaml` inventory
   - `experience` — selected entries with `source` id; bullets as `use_profile: idx` or `rewrite: "text"`; each bullet marked verbatim/rewritten
   - `projects` — same structure
   - `research` — same structure (if visible)
   - `education` — selected entries (usually all)
6. **Validate.** `uv run scripts/loader.py --resume <id>` — must pass on first attempt.
7. **Tailoring checks.** Run through `tailoring-checks.md` before handing off to build. Key: keyword coverage is hybrid — cover as many hard requirements as possible, flag missing in audit, ask user per-case (see `tailoring-checks.md` Check 2).
8. **Approval gate.** Present `resume.yaml` to user for review before build. Fix text there — cheap.
9. **Build.** User runs `uv run scripts/build.py --id <id> --pdf` (or orchestrator does it).

## Fit loop (max 3 iterations) — carried from old skill

If PDF > 1 page or checks fail, iterate (max 3):
1. **Measure.** Check page count. Compare against previous iteration: what did the last edit cost/buy in lines/space? Use observed exchange rate to size this edit — precise cuts, not blind trimming.
2. **Edit** `resume.yaml`. Over 1 page, in order until it fits:
   - Drop least-relevant project (≤ 4 total)
   - Cut weakest bullet per experience entry (≤ 5 each)
   - Shorten wordy bullets (≤ 150 chars)
   - Disable `show_coursework` / `show_research`
   - Disable `show_summary` only if genuinely non-essential
   - Last resort: drop a whole experience entry (keep 2 strongest)
   Under-filled (> 2 empty lines): restore a bullet or project that earns its space.
3. **Rebuild** + re-check.
4. **Audit** via `audit-application` skill (scoped to resume) — iteration done only when page fits AND edit didn't gut quality (e.g., trimmed away JD's top keywords).

## Re-tailoring

When user says "redo this, emphasise X": edit the existing `resume.yaml` — prior manual fixes survive. Re-run selection only for the changed emphasis; preserve bullet rewrites where source unchanged.

## Script fallback

Only on explicit user request or with no harness driving:
```bash
uv run scripts/ai_tailor.py --jd jd.txt --id <id>    # or --url "<posting url>" --use-project-web
```
Then review generated files against steps 4–8 above.