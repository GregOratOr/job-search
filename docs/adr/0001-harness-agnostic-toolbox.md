# 1. Harness-agnostic toolbox instead of an Ollama-only agent

Date: 2026-06-24

## Status

Accepted

## Context

The goal is to run the job-search pipeline autonomously, ideally driven by a locally-run
Ollama model to avoid burning limited cloud API quota. The naive approach is to write a
single bespoke agent loop hard-wired to Ollama.

Two realities push against that:

1. Local quota is limited only for *cloud* harnesses (e.g. Hermes on OpenRouter). When quota
   is available, the user wants to be able to use stronger cloud models/harnesses (Cursor,
   Claude Code, OpenRouter) on the *same* project without rewrites.
2. A bespoke Ollama-only loop duplicates what mature harnesses already do (tool dispatch,
   retries, conversation state) and locks the project to one runtime.

## Decision

Build the project as a **harness-agnostic toolbox + portable skills**, not as a single agent:

- Capabilities are exposed as plain CLI **tools** under `scripts/` that any shell-capable
  harness can invoke.
- Each capability has a portable **skill** (`skills/<name>/SKILL.md`) describing when/how to
  use it.
- The **harness** (local Ollama+Hermes by default; Cursor/Claude Code/OpenRouter when quota
  allows) is the brain. The repo binds to no single provider; LLM access stays behind the
  existing provider-agnostic `scripts/llm_provider.py`.

## Consequences

- The same repo works under any harness; switching is a config/runtime choice, not a code
  change.
- Weak local models need help: tools must be robust (e.g. tolerant JSON parsing) and skills
  must be explicit, since a small model is a poor planner.
- There is no central long-running process to own state; the bundle folder on disk is the
  source of truth between steps.
