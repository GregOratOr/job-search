---
name: run-pipeline
description: Run the scripted batch pipeline (pipeline.py; discover -> tailor -> research -> build -> audit -> bundle -> track) for unattended or multi-job runs, honoring the configured autonomy_level. Use when the user explicitly wants to "run the pipeline" or do a batch discovery+application-prep run.
---

# Run the Batch Pipeline

`scripts/pipeline.py` is the scripted orchestrator for **unattended / batch** runs. It
chains discover -> tailor -> research -> build -> audit -> bundle -> track(`Saved`),
stopping at the configured `autonomy_level`. Discovery helpers live in
`scripts/job_discovery.py` (library only — no CLI).

For a single specific job with an agent driving, use the `new-application` skill
instead — it orchestrates the same steps agent-natively via the specialist skills.

## ⛔ Hard ceiling (always)
This pipeline NEVER submits an application and NEVER sends a message. The most it does is
prepare the per-application bundle and log it as `Saved`. The user submits and sends manually.

## Autonomy levels (config/job_search_config.yaml -> automation.autonomy_level)
- `discover_only` — find + shortlist jobs only (no files written).
- `tailor` — also tailor resume / cover letter / outreach drafts, then log `Saved`.
- `full_bundle` — also run company research, build PDFs, run the audit, finalize the
  bundle, log `Saved`.

CLI shorthands:
- `--dry-run` → discover only
- `--build` (without `--level`) → discover, tailor, build, bundle, track (skips research + audit)
- `--steps a,b,…` → overrides level / shorthands

The `audit` step writes an advisory `applications/jobs/<id>/audit.md` (see the
`audit-application` skill). Run it independently with
`uv run scripts/pipeline.py --id <id> --steps audit` or `uv run scripts/audit.py --id <id>`.

## Steps
1. Confirm the LLM provider is set. For web: if the harness has native search/extract,
   prefer agent-driven discovery (`discover-jobs`). For unattended scripted runs, confirm
   `WEB_BACKEND` and pass `--use-project-web`.
2. Discovery-driven run (config defaults + project web):
   `uv run scripts/pipeline.py --use-project-web`
3. Override scope:
   - `uv run scripts/pipeline.py --level tailor --max 3 --use-project-web`
   - `uv run scripts/pipeline.py --query "LLM inference engineer remote" --max 5 --use-project-web`
4. Single known job, end to end:
   `uv run scripts/pipeline.py --url "<posting>" --id <company_role_year> --use-project-web`
   or `uv run scripts/pipeline.py --jd jd.txt --id <id>` (no web flag — local file)
5. Piecewise on an existing application (skips discovery; no web unless a step needs it):
   `uv run scripts/pipeline.py --id <id> --steps build,bundle,track`
   `uv run scripts/pipeline.py --id <id> --steps audit`
6. Interactive gating (pause before each **per-job** step — not before discovery): add `--gate`.

## Web (discovery-driven / `--url` / research / contacts)
Pass `--use-project-web` so those steps may call `scripts/web.py`. Set `WEB_BACKEND` in
`.env` (`searxng` | `tavily` | `brave` | `serper` | `harness`). Optional:
`automation.web_backend` in config applies only when `WEB_BACKEND` is unset.
`--search-mode` is retired (ignored if passed).

When an agent harness has native web tools, prefer agent-driven discovery (see
`discover-jobs`) instead of forcing `scripts/web.py` through the pipeline.

## Models
Each step resolves its model from `.env`: `LLM_MODEL_<TASK>` (TAILOR, AUDIT, RESEARCH,
DISCOVERY, FOLLOWUP) **only with** `--use-agent` → `LLM_MODEL` → provider variable.
`--model` overrides all steps for one run. `--provider anthropic|ollama|openai` overrides
`LLM_PROVIDER` for cloud-harness sessions (same as `ai_tailor.py`).

## After a run
Each `applications/jobs/<id>/` holds the upload-ready bundle (`{id}_resume.pdf`,
`{id}_cover_letter.pdf`, `jd.txt`, `job_info.py`, `networking.md`, `research.md` if generated).
Open the posting, upload the PDFs, review `networking.md`, and send outreach yourself.

## Pitfalls
- Discovery / `--url` / research / page-scan contacts need `--use-project-web` + working `WEB_BACKEND`.
- `build`/`bundle` need `pdflatex`; set `automation.build_pdf: false` to skip PDF compilation.
- `track` logs `Saved`, never `Applied`. Mark `Applied` manually after you upload.
- A single bad job/JD is skipped; the batch continues.
- `--find-contacts` is opt-in; failures warn only and do not fail the job.
