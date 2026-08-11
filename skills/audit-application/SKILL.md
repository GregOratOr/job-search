---
name: audit-application
description: Audit a tailored application from the hiring panel's perspective — score it against the JD, trace every claim to profile ground truth, and write the verdict to the bundle's audit.md. Use when the user wants to audit, critique, or stress-test an application before submitting, or when a tailoring skill finishes a draft and needs a verdict.
---

# Audit Application

You (the agent) perform the audit yourself: read the documents, apply the rubric below,
write the verdict. The audit is **report + verdict only** — fixes to the per-job outputs
sources (`resume/outputs/<id>.py`, `coverletter/outputs/<id>_cl.py`) belong to the
tailoring skill (or the user), which reads your verdict, edits, rebuilds, and re-invokes
this skill until the 🔴 list is empty.

Adopt the **hiring panel** persona throughout: a recruiter (ATS + keyword reality),
a hiring manager (fit + evidence), and a team lead (technical credibility) reading
together. Every section of the rubric is judged from that panel's chair.

## Scope

Default scope is the whole application: resume + cover letter, plus cross-document
checks. When a document is absent, mark its sections "skipped — not in scope" in the
report. When a caller (e.g. a tailoring skill) asks for a single document, audit only
that document and the always-applicable sections.

## Locating the inputs

All paths are overlay-aware — prefer `private/` when it exists:

1. **Sources**: `resume/outputs/<id>.py`, `coverletter/outputs/<id>_cl.py`.
   If already bundled, they live in `applications/jobs/<id>/` as `<id>_resume.py`,
   `<id>_cover_letter.py` (with `.tex`/`.pdf` siblings).
2. **JD**: `applications/jobs/<id>/jd.txt` — required. If missing, stop and ask the
   user for the JD text; an audit without the JD is guesswork.
3. **Ground truth**: the `profile/` package (`master_data.py` and the modules it
   re-exports). Read the actual entries the tailoring file selected or rewrote.
4. **Style reference**: read `docs/resume-writing-reference.md` before judging bullet
   quality and the summary — it is the standard the tailoring skills write against,
   so it is the standard you grade against.

## Rubric

Score every applicable section. A score (0–100) expresses **confidence that this
application clears the hiring panel for this specific JD** — high resolution so
deficiencies show up in the number, not precision theater. Each section gets its
score/verdict plus concrete findings; a section without findings is an unfinished
section.

| # | Section | Applies to | Output |
|---|---------|-----------|--------|
| 1 | ATS compatibility | Resume | 0–100 + specific blockers (parsing, formatting, missing fields) |
| 2 | Visual scan | Resume | 0–100 — must cover both lenses: what a 6-second skim catches, and whether the left edge / first lines carry the weight (F-pattern) |
| 3 | Bullet quality | Resume (experience, projects) | Per-bullet critique vs the XYZ formula and verb bank in `docs/resume-writing-reference.md` |
| 4 | Skills & competencies | Resume | Gaps vs JD; dead weight to cut |
| 5 | Keyword strengths & gaps | Both | Matched / missing JD keywords, where each missing one could live |
| 6 | Professional summary | Resume, if present | 0–100 — company named? seniority right? differentiated? |
| 7 | Cover letter | CL, if in scope | 0–100 CL-only JD fit + verdict per paragraph: hook, evidence, closing, tone |
| 8 | Cross-document consistency | Both, when both audited | Contradictory metrics; duplicated vs complementary content |
| 9 | Factual accuracy | Both | Trace **every** selected/rewritten claim to a profile entry, side by side. Untraceable ⇒ automatic 🔴 |
| 10 | Action plan | Always | Overall JD confidence 0–100; 🔴 must-fix / 🟡 high-impact / 🟢 polish / ✅ working well — each item with an accept-or-reject recommendation and reasoning |

Completion criterion: every applicable section scored and populated with findings;
every inapplicable section explicitly marked skipped; every 🔴 item cites either a
JD requirement or a profile ground-truth entry. Any suggestion you endorse must
trace to facts already in the profile — the audit proposes rewording and emphasis,
never new facts.

## Writing the report

Append to `applications/jobs/<id>/audit.md` (create if absent; overlay-aware path):

- Each run is a **fresh, complete report**, separated from the previous run by `---`.
  Prior runs are never edited.
- Each report ends with an **Audit Trail** section (before any future `---`): why this
  audit was triggered (fresh tailor, re-audit after fixes, user request), and the delta
  since the previous audit — which prior 🔴/🟡 items were resolved, which remain, how
  scores moved.

## Reporting back

End by handing the caller the verdict directly — overall confidence score, the 🔴 list
with accept/reject recommendations, and the score deltas if this was a re-audit — so
the tailoring process can act without re-reading `audit.md`.

## Batch fallback

Only for unattended runs (`pipeline.py` at `full_bundle`) or when the user explicitly
wants the fixed pipeline instead of an agent-run audit:

```bash
uv run scripts/audit.py --id <id>
```

Flags, model resolution, and script pitfalls: see `okf/scripts/audit.md`.
