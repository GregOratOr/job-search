# Skills orchestrate; tools process; pipelines are unattended only

Date: 2026-07 (accepted); updated 2026-08-05

## Status

Accepted

## Decision

Agent-driven work follows **skills**: logical steps plus an explicit tool list with when-to-use /
when-not-to-use. **Tools** (`scripts/*.py`) perform units of work—especially AI data processing
and document generation—not end-to-end orchestration. Hardwired runners such as `pipeline.py`
exist for **unattended/batch** runs when no agent is driving the loop; skills must not steer
agents to jump straight into those runners when the harness can execute the skill’s steps
(including harness-native web). The project web tool (`scripts/web.py`) is an opt-in fallback
for scripted/no-harness-web cases, not the agent’s default search path.

**Opt-in:** scripted Tools that would call `scripts/web.py` require `--use-project-web` /
`use_project_web=True`. Backend selection is `WEB_BACKEND` only (`--search-mode` retired).

## Consequences

- Skills (`discover-jobs`, `research`, `find-contacts`, …) document harness-native paths first.
- `pipeline.py` is for batch/unattended runs with explicit web opt-in.
- `job_discovery.py` is a library used by the pipeline — no CLI.
