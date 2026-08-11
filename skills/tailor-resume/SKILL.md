---
name: tailor-resume
description: Tailor a resume to a specific job description — select profile entries, rewrite bullets around the JD's keywords, and deliver a built, 1-page PDF. Use when the user provides a JD or posting URL and wants a tailored resume, or when an orchestrating skill dispatches the resume-tailoring step.
---

# Tailor Resume

You (the agent) do the tailoring reasoning yourself: read the JD, judge which profile
entries fit, rewrite the bullets. `ai_tailor.py` is the fallback for explicit script
requests or runs with no harness. Mechanical tools (`build.py`,
`validate_profile.py`) remain your normal instruments — they are deterministic; use
them rather than hand-writing LaTeX or trusting doc examples.

Deliverable: `resume/outputs/<id>.py` (overlay-aware) plus a built PDF that fits
exactly 1 page. The cover letter is `tailor-coverletter`'s job; audit verdicts, the
bundle, and tracking belong to the orchestrator (`new-application`).

## ⛔ Profile is read-only

Read `profile/` only. Every job-specific change — reworded bullets, injected
keywords — goes into the tailoring file via `dataclasses.replace()`, never into the
source entries.

## Steps

1. **Inventory.** Get the real entry variable names:
   `uv run scripts/validate_profile.py --inventory`
2. **Read the JD** (`applications/jobs/<id>/jd.txt`): extract company, role, top
   keywords, hard requirements.
3. **Read `docs/resume-writing-reference.md`** — the standard every rewrite is graded
   against (XYZ formula, action-verb bank, per-section rules).
4. **Write `resume/outputs/<id>.py`**, editing only:
   - `CONFIG` — which sections show
   - `EXPERIENCE` — select entries; `replace(ENTRY, highlights=[...])` to reword
     bullets around JD keywords
   - `PROJECTS` — the 2–4 most relevant
   - `SUMMARY` — a `SUMMARIES[...]` preset or custom 2–3 sentences naming the company
   - skills preset (`SKILLS_FULL` / `SKILLS_ML_FOCUSED` / `SKILLS_SWE_FOCUSED` /
     `SKILLS_RESEARCH_FOCUSED`)
5. **Build:** `uv run scripts/build.py --id <id> --only resume --pdf`
6. **Fit loop** — see below. Ends when the PDF is exactly 1 page with minimal wasted
   space (≤ 1 empty line) and the iteration audit raises no new 🔴 items.

## Fit loop (max 3 iterations)

The 3-iteration cap exists to stop a spiral down a wrong decision path — if the
document doesn't fit after 3 rounds, stop and report the state to the caller/user
instead of continuing to hack at it.

Each iteration:

1. **Measure.** Check the page count (`pdfinfo` or pypdf). Compare against the
   previous iteration: what did the last edit cost or buy in lines/space? Use that
   observed exchange rate to size this iteration's edit — precise cuts, not blind
   trimming.
2. **Edit** `resume/outputs/<id>.py`. Over 1 page, in order until it fits: drop the
   least-relevant project (≤ 4 total) → cut the weakest bullet per experience entry
   (≤ 5 each) → shorten wordy bullets (≤ 150 chars) → disable `show_coursework` /
   `show_research` → disable `show_summary` only if genuinely non-essential → last
   resort, drop a whole experience entry (keep the 2 strongest). Under-filled
   (> 2 empty lines), expand: restore a bullet or project that earns its space.
3. **Rebuild** (step 5) and re-check.
4. **Audit** the resume via the `audit-application` skill, scoped to the resume —
   the iteration is only done when the page fits *and* the edit didn't gut quality
   (e.g. trimmed away the JD's top keywords).

## Style rules (apply to every rewrite)

Full rules in `docs/resume-writing-reference.md`; the non-negotiables:

- **XYZ formula:** [action verb] + [what] + [tools/how] + [quantified result];
  metric last, active voice, no pronouns. Quantify only what is true — every claim
  must trace to a profile entry.
- Bold key terms with `\textbf{...}`; keep bullets under ~200 chars.
- Escape LaTeX specials: `%`→`\%`, `&`→`\&`, `$`→`\$`, `_`→`\_`, `#`→`\#`.
- Select + `replace()` only — a tailoring file that *contains* profile data is wrong.

## Script fallback

Only on explicit user request or with no harness driving:

```bash
uv run scripts/ai_tailor.py --jd jd.txt --id <id>    # or --url "<posting url>" --use-project-web
```

Calling any AI script from a cloud-model session requires `--provider`/`--model` —
see `okf/scripts/llm-provider.md` ("Calling AI scripts from a harness").
Then review its generated files against steps 4–6 above.
