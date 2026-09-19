# Workstream 09 — Deletions, Archive, and Documentation

> **Runs last.** Nothing here may be executed until workstreams 01–08 have landed and the
> replacement path works end to end. Deleting first would leave the project unusable.
>
> **Before doing anything destructive, run a `grill-with-docs` session** (the `grilling`
> skill via `domain-modeling`): one question at a time, each with your recommended answer,
> resolving the open questions below. Look facts up in the repo yourself; put only
> decisions to the user. Do not delete anything until the user confirms.

## Goal

Remove everything the revamp retired — code, skills, config, and documentation — so that
nothing stale remains to mislead a future agent, and rewrite the docs that survive.

Stale documentation misleads an agent exactly as badly as stale code. Most of the current
documentation describes scripts that will no longer exist.

## Decisions already locked

- **Delete, do not quarantine.** Git history is the recovery path. No `legacy/` directory.
- **Old job folders are archived untouched**, not migrated. They are finished
  applications.
- **Docs collapse** to: root `AGENTS.md`, `CONTEXT.md`, `docs/resume-writing-reference.md`,
  `docs/adr/`, and `okf/`. Nested `AGENTS.md` files are deleted and `README.md` is
  rewritten.
- **`okf/` is kept** at the user's request and must be updated, not abandoned. An `okf/`
  full of pages about deleted scripts is worse than no `okf/` at all.

## Deletion list

**Skills** (`skills/`): `discover-jobs`, `research`, `find-contacts`, `follow-up`,
`track-application`, `run-pipeline`, `new-application`, `update-profile`,
`audit-application` (replaced by `fit-audit`), `networking-outreach` (replaced by
`outreach`).

**Scripts** (`scripts/`): `pipeline.py`, `job_discovery.py`, `web.py`, `research.py`,
`find_contacts.py`, `followup.py`, `audit.py`, `ai_tailor.py`, `llm_provider.py`,
`json_llm.py`, `track.py`, `new_application.py`, `update_profile.py`, `job_info_io.py`.
Also `bundle.py` and the `resume/outputs/` + `coverletter/outputs/` directories **if**
workstream 05 retired them.

**Profile Python** — every `*.py` under `profile/` and `private/profile/`, once the YAML
conversion in workstream 01 is verified. The skill `Enum` classes and `EnumStringBuilder`
in `resume/cv_utils.py` also go, replaced by the skills inventory; the dataclasses in that
file stay.

**Config**: `config/job_search_config.yaml` and `config/platforms.yaml` (discovery,
autonomy levels, follow-up delays, platform playbooks — all belong to deleted features).
Check whether anything surviving still reads them before removing.

**Env**: every LLM and web variable in `.env` / `.env.example` — `LLM_PROVIDER`,
`LLM_MODEL`, `LLM_MODEL_<TASK>`, `OLLAMA_*`, `ANTHROPIC_*`, `OPENAI_*`, `WEB_BACKEND`,
and the search-provider keys. With no LLM calls and no web calls in Python, `.env` may end
up empty — check before keeping the plumbing in `scripts/bootstrap.py` /
`scripts/data_paths.py::resolve_env_file`.

**Other**: `applications/shortlists.md`, `applications/tracker.csv` and
`applications/schema.md` (tracking is gone), `networking/` if workstream 07 moved the
templates into the skill, and the Hermes setup material in `skills/SETUP.md` and
`docs/hermes/` if local-model support is no longer meaningful without `llm_provider.py`.

**Tests**: anything under `tests/` covering the above.

## Documentation to rewrite

- **Root [AGENTS.md](../../AGENTS.md)** — currently 29 KB, most of it describing deleted
  scripts, the batch pipeline, discovery tuning, and the `.py` tailoring workflow. It
  should become short: the profile read-only rule, the five-stage pipeline, the skills
  table, and pointers. Everything procedural belongs in a skill.
- **Nested `AGENTS.md`** — `scripts/`, `resume/`, `resume/tailoring/`, `coverletter/`,
  `applications/`, `networking/`, `profile/`, and their `private/` counterparts. All
  delete; fold anything still true into the relevant skill or the root file.
- **[README.md](../../README.md)** — 20 KB, rewrite around the new five goals.
- **[CONTEXT.md](../../CONTEXT.md)** — the glossary survives and is the place the earlier
  workstreams have been appending terms. Remove the dead entries: **Batch pipeline**,
  **Shortlist**, **Platform playbook**, **Harness-native web**, **Project web tool**,
  **use-project-web**, **AI tool**, **Per-task model**, **autonomy_level**. Rewrite
  **Audit** for the two-audit model, **Tailoring source** for YAML, **Bundle** and
  **Deliverables** for the new folder contents, and **Saved ceiling** without the tracker.
- **`okf/`** — 38 files. `okf/scripts/` has a page per script, most of which are being
  deleted (`ai-tailor`, `audit`, `web`, `research`, `find-contacts`, `followup`,
  `job-discovery`, `pipeline`, `track`, `new-application`, `json-llm`, `llm-provider`,
  `job-info-io`, `bundle`). `okf/workflows/` describes the old flows; `okf/glossary/`
  duplicates `CONTEXT.md`; `okf/architecture/web-access-policy.md` documents a deleted
  policy. Needs a deliberate rebuild, not a patch.
- **`docs/adr/`** — `0001-harness-agnostic-toolbox.md` and
  `0002-autonomy-ceiling.md` largely survive; `0003-project-owned-web-tool.md` is
  superseded by the deletion of `web.py`; `0004-skills-orchestrate-tools-process.md` needs
  revisiting. Add new ADRs for this revamp's two hard-to-reverse decisions: **YAML as the
  data format for profile and tailored documents**, and **no LLM calls inside Python**.
  Do not write an ADR for anything easily reversed.
- **`docs/resume-writing-reference.md`** — keep as is. It is the durable style authority
  and the skills cite it.
- **`.cursor/rules/job-search.mdc`** — lists the old skill names; update to the new set.

## Grill the user on these before implementing

1. **Archive location and form** for the old job folders — a sibling `archive/`
   directory, a zip, or left alone in place? *Recommend moving them to
   `private/applications/archive/` untouched, so the live folder shows only new-format
   applications.*
2. **Does `private/profile/CHANGELOG.md` survive** the move to YAML, and does the
   convention of logging every profile edit continue now that the `update-profile` skill
   is deleted? *Recommend keeping the changelog and the habit — it is cheap and it is the
   only audit trail on ground truth.*
3. **Local-model support.** Deleting `llm_provider.py` ends the Ollama and Hermes path.
   Does `skills/SETUP.md` shrink to Cursor only, or does the user still want Hermes
   documented as a harness? *Recommend keeping Hermes as a documented harness — it still
   works, since the agent is now the only brain — while deleting all provider and model
   configuration.*
4. **`okf/` rebuild scope.** Regenerate it wholesale from the new code and skills, or
   prune page by page? *Recommend regenerating: nearly two thirds of the pages describe
   deleted code, and pruning tends to leave stale cross-references.*
5. **Duplication between `okf/glossary/` and `CONTEXT.md`.** Both define the same terms
   today. *Recommend `CONTEXT.md` as the single glossary, with `okf/glossary/` linking to
   it rather than restating it.*
6. **Config directory.** Does anything survive in `config/`, or does the whole directory
   go? *Recommend deleting it and letting any residual preference live in the profile
   YAML.*
7. **Tests.** What level of test coverage does the new codebase need, given it is now a
   loader plus two renderers? *Recommend focusing tests on loader validation failures and
   one golden-render case — those are the failure modes that actually bite.*
8. **Commit strategy.** One large deletion commit, or grouped by concern? *Recommend
   grouping — deletions, profile migration, docs — so a bisect can isolate a regression.*

## Done criteria

- Every item on the deletion list is gone, and `rg` finds no reference to any deleted
  script, skill, or config key anywhere in the repo — including inside `okf/` and
  `.cursor/rules/`.
- Root `AGENTS.md` is short and describes only what exists.
- `CONTEXT.md` defines exactly the current vocabulary, with no dead entries.
- `okf/` reflects the new codebase.
- New ADRs record the YAML pivot and the no-LLM-in-Python boundary; superseded ADRs are
  marked as superseded rather than deleted.
- Old job folders are archived and untouched.
- A clean clone plus `uv sync` can run the full pipeline on a new JD using only the
  documentation that remains.
