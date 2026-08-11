# CONTEXT — Glossary

This is the project's glossary: the precise, canonical meaning of the terms used across
skills, scripts, and docs. It is **not** a spec or a design doc — it only defines language.

> Structured reference for agents: see the [OKF knowledge bundle](okf/index.md).

## Core terms

**Harness**
The runtime that pairs a model with a set of callable tools and drives a conversation/loop.
Examples: Hermes (local Ollama), Cursor, Claude Code, VS Code chat, or a plain terminal
session. The harness — not any single hard-coded model — is the "brain" that decides which
skills and tools to invoke. The project is built to be *harness-agnostic*: nothing in the
repo binds to one provider.

**Model**
The LLM doing the reasoning/generation inside a harness. Defaults vary by provider and are
overridable via `LLM_MODEL` in `.env`. See `scripts/llm_provider.py` for resolution order.

**Skill**
A portable `skills/<name>/SKILL.md` that tells an agent the **logical steps** for a capability,
lists available Tools, and states **when to use / when not to use** each one. Skills never
execute on their own. They orchestrate agent behavior; they must not default to “just run the
hardwired pipeline” when the harness can carry out the steps (including harness-native web).
_Avoid_: treating a Skill as a thin wrapper that only shells out to `pipeline.py`.

**Tool**
A callable CLI (or importable library) under `scripts/` that performs a **unit of work**.
Tools are not responsible for deciding the overall multi-step job-search flow; that belongs
to Skills (agent) or to an unattended batch runner. Two kinds with different policies:
_Avoid_: “pipeline” as a synonym for every script.

**AI tool**
A Tool that makes its own LLM calls (`ai_tailor.py`, `audit.py`, `research.py`,
`followup.py`). In a harness, the agent performs this reasoning itself; AI tools run only
on explicit user request or when no harness is driving (the script-fallback policy).

**Mechanical tool**
A deterministic Tool with no LLM calls (`build.py`, `new_application.py`, `track.py`,
`bundle.py`, `validate_profile.py`). These stay first-class in agent flows — the agent
invokes them as its normal instruments rather than hand-writing LaTeX, scaffolds, or
tracker rows, because the script guarantees identical output every run.

**Batch pipeline** (a.k.a. hardwired / unattended pipeline)
A scripted orchestrator such as `scripts/pipeline.py` that chains Tools for **unattended or
batch** runs when no agent is driving the loop. Optional; not the primary path for agent
harnesses that can follow a Skill step-by-step.
_Avoid_: using the batch pipeline as the agent’s default when native tools exist.

**Harness-native web**
The built-in search and page-extraction tools a harness already provides (e.g. Hermes
`web_search` / `web_extract`, Cursor browser MCP, Anthropic `web_search`). When present,
Skills instruct the agent to use these directly — **not** `scripts/web.py`.

**Project web tool**
`scripts/web.py` — pluggable search + fetch used only when scripted code is **explicitly**
allowed to do web I/O (no harness-native web, or an opt-in flag such as `--use-project-web`).
`WEB_BACKEND` must be set explicitly (`searxng` | `tavily` | `brave` | `serper` | `harness`) —
there is no implicit default. Not the agent’s default web path.
_Avoid_: importing `scripts.web` from other Tools without an opt-in gate.

**Bundle** (a.k.a. the application folder)
The single per-application folder `applications/jobs/<id>/` that holds everything needed to
apply: `jd.txt`, `job_info.py`, `{id}_resume.py`, `{id}_resume.tex`, `{id}_resume.pdf`,
`{id}_cover_letter.py`, `{id}_cover_letter.tex`, `{id}_cover_letter.pdf`, `networking.md`,
and optionally `research.md` and `audit.md`. It is the one-stop upload location.

**Deliverables**
The finished, uploadable artifacts inside a bundle: the `.pdf` files (for upload) and the
`.py` / `.tex` sources (kept for future edits and recompiles). Before bundling, these live
together under `resume/outputs/<id>.*` and `coverletter/outputs/<id>_cl.*` (routed to `private/`
when the overlay is present).

**autonomy_level**
The config knob (`config/job_search_config.yaml`, or `private/config/` when the overlay is
present) that sets how far the pipeline runs without asking. Values: `discover_only` (find +
shortlist jobs), `tailor` (also tailor resume/cover letter/outreach), `full_bundle` (also
research, build PDFs, run the audit, finalize the bundle, and log `Saved`).

**Saved ceiling**
The hard, level-independent safety limit: the automation never submits an application to a
job site and never sends a message (LinkedIn/email). The maximum action it may take is to
prepare the bundle and log the application as `Saved`. Actual submission and sending are
always manual.

**Shortlist**
The ranked set of open postings from a discovery run (company, role, URL, why). Shown in
chat and appended as a session block to `applications/shortlists.md` (separated by `---`).
JD persistence and tailoring happen only after handoff to `new-application`, or via
scripted `pipeline.py` when the user asked for batch prep.

**Platform playbook**
`config/platforms.yaml` — per-platform search filters, career URLs, notes, and
post-shortlist application/referral checklists. `discover-jobs` uses filters/URLs/notes
during search; it does not auto-execute apply steps. Not loaded by Python scripts today.

**Profile** (read-only by default)
`profile/` (or `private/profile/` when the private overlay is present) — the single source of
truth for personal data. Tools and skills read it. Writes only via the gated
`update-profile` skill: the user must explicitly name what to change. Job-specific
rewrites never enter the profile — they go in `resume/outputs/<id>.py` /
`coverletter/outputs/<id>_cl.py` via `replace()`.
_Avoid_: treating "improve my resume" as a profile gate.

**Tailoring source**
The per-job `.py` files (`resume/outputs/<id>.py`, `coverletter/outputs/<id>_cl.py`) that
*select and configure* profile entries via `dataclasses.replace()`. They contain no profile
data of their own. Scaffold templates remain in `{resume,coverletter}/tailoring/_template.py`.

**Private overlay**
The optional `private/` submodule. When `private/profile/` exists, scripts read/write user
data under `private/` instead of the public template dirs (see `scripts/data_paths.py`).
Mirrored paths: `profile/`, `resume/`, `coverletter/`, `applications/`, `config/`,
`networking/`, and `.env`.

**use-project-web** (scripted opt-in)
Flag / gate for unattended scripts that would otherwise call `scripts/web.py`. When unset,
scripted Tools must not perform project-web I/O; the agent/harness is expected to supply web
results or the step is out of scope for that run. Backend selection is `WEB_BACKEND` in `.env`
(not `--search-mode`, which is retired — see [ADR 0004](docs/adr/0004-skills-orchestrate-tools-process.md)).

**Audit**
A critique of a tailored application from the hiring panel's perspective, producing a
verdict in `applications/jobs/<id>/audit.md` (each run appends a fresh report separated
by `---`, ending with an audit trail). Report + verdict only — fixes belong to the
tailoring flow; the audit never edits profile or tailoring files. In a harness the agent
performs the audit itself (`skills/audit-application/SKILL.md`); `scripts/audit.py` is
the batch fallback (pipeline step at `full_bundle`, after `build`, before `bundle`).
_Avoid_: treating the audit as "run audit.py".

**Hiring panel**
The composite persona every audit is judged from: a recruiter (ATS + keyword reality),
a hiring manager (fit + evidence), and a team lead (technical credibility) reading the
application together.

**Audit trail**
The closing section of each audit report: why the audit was triggered, and the delta
since the previous audit (resolved/remaining 🔴🟡 items, score movement).

**Per-task model**
Model selection is configured entirely in `.env` — no hardcoded model names in code.
Resolution order: explicit `--model` / `model=` → `LLM_MODEL_<TASK>` **only when**
`use_task_model=True` (`--use-agent`; tasks: `TAILOR`, `AUDIT`, `RESEARCH`, `DISCOVERY`,
`FOLLOWUP`) → `LLM_MODEL` → the provider variable (`OLLAMA_MODEL` / `ANTHROPIC_MODEL` /
`OPENAI_MODEL`). Scripts exit with a clear message when no model is configured.
