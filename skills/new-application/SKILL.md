---
name: new-application
description: Orchestrate a single job application end to end — intake a specific JD (pasted text, URL, or company+role), then drive tailoring, research, outreach, build, audit, bundle, and tracking by invoking the other skills. Use when the user brings one specific job to apply to, or asks to run any individual application step for an id.
---

# New Application (single-application orchestrator)

You (the agent) drive one application's lifecycle by invoking the other skills in
sequence. This skill owns intake and assembly; the specialist skills own their steps.
There is no discovery here — the job is already chosen (for finding jobs, see
`discover-jobs`).

**Saved ceiling (absolute):** the furthest this flow ever goes is a finished bundle
logged as `Saved` in the tracker. Submitting the application and sending messages are
always manual user actions.

## Scope: how far to run

`autonomy_level` in `config/job_search_config.yaml` (overlay-aware) sets the default
stopping point; anything the user says in the conversation overrides it for this run.

| Scope | Steps run |
|-------|-----------|
| `tailor` | intake → id → tailoring → track(`Saved`) |
| `full_bundle` | intake → id → tailoring → research → contacts/outreach → build → audit → bundle → track(`Saved`) |

**Piecewise:** when the user asks for one step exclusively ("just research X",
"rebuild the PDFs for <id>", "re-audit <id>"), run only that step via its skill —
no ceremony around it.

## Steps

1. **Intake the JD.** Pasted text → save to `applications/jobs/<id>/jd.txt`.
   URL → fetch with harness web tools, extract the posting text, save `jd.txt` and
   record the URL for `job_info.py` / tracking. Company + role with no JD yet → note
   that tailoring is deferred (see step 3).
2. **Derive the id and check for collisions.** Format: `{company}_{role}_{year}`,
   lowercase, underscores only. Check `tracker.csv` and `applications/jobs/` for the
   id. On collision, stop and ask — surface the existing row's status first. Many
   situations are possible: a re-run that should replace the previous attempt, a later
   reapplication to the same position (postfix, e.g. `_v2`), or a genuine duplicate.
   The user decides.
3. **Scaffold only if tailoring is deferred.** When the user wants the bundle to exist
   now and hand-fill later:
   `uv run scripts/new_application.py --id <id> --company "<co>" --role "<role>"`
   The script is the sole scaffolder — it patches the templates deterministically.
   When tailoring runs immediately (the normal path), skip this; tailoring creates
   the source files itself.
4. **Tailor** — invoke `tailor-resume` and/or `tailor-coverletter` per the user's
   ask (both, for a full bundle).
5. **Research** the company/role via the `research` skill → `applications/jobs/<id>/research.md`.
6. **Contacts & outreach** via `find-contacts` and `networking-outreach` →
   contacts and draft messages in `applications/jobs/<id>/networking.md`. Drafts only.
7. **Build** PDFs via the `build-documents` skill.
8. **Audit** via the `audit-application` skill. On 🔴 items, loop: hand the verdict
   back to tailoring (step 4), rebuild, re-audit — until the 🔴 list is empty.
9. **Bundle** — finalize `applications/jobs/<id>/` as the one-stop upload folder.
10. **Track** — log the application as `Saved` via the `track-application` skill.

Completion criterion: every step in scope either done or explicitly reported as
skipped-with-reason; the bundle contains everything the scope promised; the tracker
row exists.

## Script fallback

Only when the user explicitly asks for the fixed pipeline, or no harness is driving:
`uv run scripts/pipeline.py --url "<url>" --id <id> --use-project-web` (or `--jd <file>`,
no web flag needed) runs the
scripted equivalent honoring `autonomy_level`. See `okf/scripts/pipeline.md`.
