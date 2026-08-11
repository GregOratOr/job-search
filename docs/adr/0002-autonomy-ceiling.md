# 2. Autonomy ceiling stops at bundle preparation

Date: 2026-06-24

## Status

Accepted

## Context

"Fully autonomous" is ambiguous. The pipeline could, in principle, submit applications to job
sites and send LinkedIn connection requests / cold emails on the user's behalf. But:

- Application sites require manual file upload and vary wildly; auto-submission is brittle and
  risks sending wrong/half-baked materials under the user's name.
- Auto-sending outreach risks reputational damage (spammy or off-tone messages) and violates
  several platforms' terms.
- The user explicitly applies by visiting the link and uploading the prepared files, and wants
  to review messaging before it goes out.

The user also wants to choose *how far* a run goes (fully autonomous vs. piecewise/manual).

## Decision

Make the stopping point **config-driven** via `autonomy_level`
(`discover_only | tailor | full_bundle`) plus per-step CLI flags for manual piecewise runs.

Impose a **hard ceiling that applies at every level**: the automation never submits an
application and never sends a message. The maximum action is preparing the bundle (tailored
resume + cover letter PDFs, drafted outreach in `networking.md`) and logging the application
as `Saved`. Submission and sending remain manual.

## Consequences

- The user can run end-to-end safely and review/upload/send everything themselves.
- `full_bundle` logs `Saved`, never `Applied`; `Applied` is set manually after the user
  uploads (keeps the tracker honest).
- New capabilities must respect the ceiling: a tool may *draft* an outreach message but must
  never transmit it.
