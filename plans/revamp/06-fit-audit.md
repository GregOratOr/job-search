# Workstream 06 — `fit-audit` Skill (standalone)

> **Depends on workstream 02** (`job.yaml`) and consumes a finished resume. Can be built
> once 01–05 exist, but is deliberately usable on its own.
>
> **Before writing anything, run a `grill-with-docs` session** (the `grilling` skill via
> `domain-modeling`): one question at a time, each with your recommended answer, resolving
> the open questions below. Look facts up in the repo yourself; put only decisions to the
> user. Do not implement until the user confirms shared understanding.

## Goal

Judge a **finished resume against a job description** from a recruiter's and hiring
manager's point of view: how strong is this candidate for this role, where is the
application weak, and which missing keywords are the symptom of a real skill gap rather
than a tailoring miss.

## Why this is a separate skill

The user identified two distinct audits, and conflating them is what made the old one
useless:

- **Tailoring checks** — facts are true, keywords present, bullets the right length,
  relevance holds, resume fits one page. These run *during* tailoring, they are cheap and
  mechanical, and they belong inside `tailor-resume` as a reference file (workstream 03).
  **Not this workstream.**
- **Fit audit** — the resume is done; now weigh it against the JD as a hiring panel
  would. This is analysis and advice, not a checklist, and it is valuable on its own: it
  should work on any resume and JD pair, including a resume this project did not produce.

## Decisions already locked

- **Standalone and reusable.** Must work on an arbitrary resume and JD, not only on a
  generated bundle.
- **Writes `fit_audit.md` next to the resume it audited** — in the job folder for pipeline
  runs, beside the file for ad-hoc runs. The report is long and worth rereading when
  deciding whether to apply.
- **Report only.** The audit never edits the profile, the tailored YAML, or anything else.
  Fixes are the tailoring skill's job.
- Zero LLM calls in Python. This is entirely agent reasoning; `scripts/audit.py` is being
  deleted.

## Current state

- [skills/audit-application/SKILL.md](../../skills/audit-application/SKILL.md) is the
  predecessor. Read it for what is worth keeping. The old design already had useful ideas:
  the **hiring panel** persona (recruiter for ATS and keyword reality, hiring manager for
  fit and evidence, team lead for technical credibility, reading together), an explicit
  verdict, and an **audit trail** section recording why the audit ran and what changed
  since the previous one — resolved versus remaining issues and score movement, with
  reports appended under a `---` separator rather than overwritten.
- `scripts/audit.py` ran four LLM phases (resume audit, cover letter audit, factual
  accuracy against profile ground truth, action plan). It is being deleted, but the phase
  decomposition is a reasonable outline for what the agent should cover.
- Both of those concepts are defined in [CONTEXT.md](../../CONTEXT.md) under **Audit**,
  **Hiring panel**, and **Audit trail** — update those definitions to match whatever this
  workstream settles on.

## Scope

**In scope**
- `skills/fit-audit/SKILL.md`, plus a rubric reference file if the scoring detail is long.
- The report structure and what a verdict means.
- The skill-gap and missing-keyword analysis, including the distinction between a keyword
  missing because the resume failed to surface it and a keyword missing because the user
  genuinely lacks the skill — these lead to completely different actions.
- Ad-hoc invocation: how the user points it at a resume PDF and a JD that never went
  through intake.

**Out of scope**
- Fixing anything. Report and recommend only.
- The pre-build tailoring checks (workstream 03).
- Deciding whether to apply — that is the user's call, informed by this.

## Grill the user on these before implementing

1. **Input format.** Does the audit read `resume.yaml`, the compiled PDF, or either? A PDF
   is what the recruiter actually sees, which argues for auditing it; the YAML is easier
   to reason about and carries provenance. *Recommend supporting both, preferring the PDF
   when present, since ATS-reality questions depend on the rendered document.*
2. **Verdict form.** A numeric score, a band (strong / borderline / weak), a
   should-I-apply recommendation, or several of these? *Recommend a band plus an explicit
   apply recommendation, and no fake-precision number unless the user wants score movement
   tracked across runs.*
3. **Append or overwrite.** The old design appended each run under a `---` with an audit
   trail. Keep that, or overwrite with the latest? *Recommend appending — seeing what
   changed after a revision is most of the value.*
4. **Cover letter.** Is the letter in scope for the fit audit, or resume only? *Recommend
   resume only by default, with the letter auditable on request — the user framed this as
   a resume-versus-JD analysis.*
5. **Skill-gap output.** How actionable should it be? A bare list of gaps, or gaps ranked
   by how often they appear across the JDs the user has audited, with suggested ways to
   close them? Note that cross-JD aggregation requires persistent state that nothing else
   in the slimmed project keeps. *Recommend per-JD gaps now, ranked by importance to this
   role, and no cross-JD aggregation until the user asks for it.*
6. **Fabrication check.** Should the fit audit re-verify claims against the profile, or
   trust that the tailoring checks already did? For an externally supplied resume there is
   no profile to check against. *Recommend verifying when a profile is available and
   saying explicitly that it was skipped when not.*
7. **ATS realism.** How far should the recruiter persona go into ATS mechanics (parsing,
   keyword density, formatting)? Much of the folklore here is unreliable. *Recommend
   sticking to defensible points: requirement coverage, terminology match, plain
   structure — and avoiding keyword-density superstition.*
8. **Ad-hoc output location** when auditing a loose PDF with no job folder. *Recommend
   `<resume-name>.fit_audit.md` beside the input file.*
9. **Length.** Is this a one-page report or a long analysis? *Recommend a short verdict
   and gap list up front, with the detailed per-requirement walkthrough below it, so the
   top of the file answers the question.*

## Done criteria

- `skills/fit-audit/SKILL.md` exists, is invocable standalone on any resume and JD pair,
  and never edits anything.
- A run produces `fit_audit.md` whose first section answers "should I apply, and why".
- Missing keywords are separated into tailoring misses and genuine skill gaps.
- The audit-trail behaviour across repeat runs is defined and implemented.
- The **Audit**, **Hiring panel**, and **Audit trail** entries in
  [CONTEXT.md](../../CONTEXT.md) are updated to the two-audit model, with the tailoring
  checks named as the other half and pointed at workstream 03's reference file.
