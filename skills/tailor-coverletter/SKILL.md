---
name: tailor-coverletter
description: Tailor a cover letter to a specific job description — write three paragraphs (hook, evidence, close) grounded in profile facts and deliver a built, 1-page PDF. Use when the user wants a cover letter for a JD or posting, or when an orchestrating skill dispatches the cover-letter step.
---

# Tailor Cover Letter

You (the agent) write the letter yourself: read the JD, pick the strongest profile
evidence, draft the paragraphs. `ai_tailor.py` (which also generates a cover letter)
is the fallback for explicit script requests or runs with no harness. Mechanical
tools (`build.py`) remain your normal instruments.

Deliverable: `coverletter/outputs/<id>_cl.py` (overlay-aware) plus a built PDF that fits
exactly 1 page. Audit verdicts, bundling, and tracking belong to the orchestrator
(`new-application`).

## ⛔ Profile is read-only

Every claim in the letter must trace to a profile entry. Read `profile/` only —
job-specific content lives in the per-job source file.

## Inputs

- **JD** (`applications/jobs/<id>/jd.txt`) — always required: company, role, what
  they actually need.
- **Tailored resume** (`resume/outputs/<id>.py`) — read it whenever it exists (the
  normal case when working a bundle): the letter must use the same facts and metrics
  without contradiction, and *complement* the resume — add context and emphasis, never
  summarize it. When tailoring the letter independently and no resume exists, work
  from the JD, company details (name, location, etc.), and profile alone.
- **Recipient** — consume what the bundle already has (`job_info.py`,
  `networking.md`) for `RecipientInfo` and the salutation; otherwise default to
  "Dear Hiring Manager," and company-level details. Finding the actual person is
  `find-contacts`' job, not this skill's.
- **Style references** — read before drafting:
  `docs/resume-writing-reference.md` §5 (cover letter tips) and the Harvard guide:
  <https://careerservices.fas.harvard.edu/resources/create-a-strong-resume/#covertips>

## Steps

1. Gather the inputs above.
2. **Write `coverletter/outputs/<id>_cl.py`** — fill `RecipientInfo`, `JobInfo`, and
   `LetterContent` with three paragraphs:
   - **Hook** — why this company and this role; one concrete company fact (product,
     research direction, mission). Name the company explicitly.
   - **Evidence** — the strongest relevant experience with a metric, tied explicitly
     to the JD's needs.
   - **Close** — forward-looking sentence + clear call to action; confident, brief.
3. **Build:** `uv run scripts/build.py --id <id> --only coverletter --pdf`
4. **Fit loop** — max 3 iterations, then stop and report. Each iteration: check the
   page count; if over 1 page, tighten each paragraph by one sentence (hook ≤ 4,
   evidence ≤ 5, close ≤ 3), cut filler ("I am excited to…", "I believe I would be a
   great fit…"), and cut the closing sentence if the call to action is already clear.
   Size each cut by what the previous edit reclaimed. Rebuild, re-check, then audit
   via the `audit-application` skill scoped to the cover letter — done when the page
   fits and no new 🔴 items appear.

## Writing rules

- The letter is a writing sample: active voice, specific, no template smell.
- Same font/type consistency with the resume is handled by the LaTeX engine — never
  edit `cl2latex.py` for tailoring.
- Escape LaTeX specials: `%`→`\%`, `&`→`\&`, `$`→`\$`, `_`→`\_`, `#`→`\#`.
- No invented facts, metrics, or company claims you can't source from the JD,
  research notes, or profile.

## Script fallback

Only on explicit user request or with no harness driving:

```bash
uv run scripts/ai_tailor.py --jd jd.txt --id <id>    # generates resume + CL + outreach
```

Cloud-model sessions must pass `--provider`/`--model` — see
`okf/scripts/llm-provider.md` ("Calling AI scripts from a harness").
Then review the generated letter against steps 2–4 above.
