---
name: discover-jobs
description: Find currently open job postings matching the campaign config, rank a shortlist, and optionally hand accepted jobs to new-application. Use when the user wants to discover or search for jobs — not when they already have a specific JD (use new-application).
---

# Discover Jobs

Find and **shortlist** open roles. This skill does not tailor documents — that is
`new-application` (one accepted job) or `run-pipeline` (scripted batch).

**Saved ceiling:** discovery never submits an application and never sends a message.

## Web access

**Harness-native web first.** If the harness has search/extract (Cursor browser MCP,
Hermes `web_search` / `web_extract`, etc.), use those tools. Do not call
`scripts/web.py` in an agent session when native web is available.

Scripted / no-harness runs: `pipeline.py` with `--use-project-web` and `WEB_BACKEND`
in `.env` — see the batch fallback below and
`okf/architecture/web-access-policy.md`.

## Inputs

- **Campaign prefs (required pre-read)** — `config/job_search_config.yaml`,
  overlay-aware: prefer **`private/config/job_search_config.yaml`** when it exists;
  otherwise the public `config/job_search_config.yaml`. This file is the search
  criteria and preference context for the user's campaign — build queries and rank
  against it before searching. Use at least:
  - `profile` — location, relocate, preferred_locations, work auth, availability,
    target salary (soft filters / ranking context)
  - `target_roles` — primary / secondary / avoid
  - `target_companies` — tier_1 / tier_2 / tier_3 / startups (bias search + ranking)
  - `search_terms` — `must_include_one_of`, `nice_to_have`, `exclude`
  - `active_platforms` — which boards to prioritize
  - `automation.max_jobs` — default shortlist cap; `automation.autonomy_level` for
    scripted handoff defaults only
- **Platform playbook** — `config/platforms.yaml` as disclosed reference:
  use each platform's `url`, `search_filters`, `companies_and_career_urls`, and
  notes while searching. Do **not** execute `application_steps` / referral
  `workflow` here — those are post-shortlist apply/network checklists.
- **Custom query** — if the user supplies one, it overrides config-built queries
  for this run; still rank results against the campaign prefs above.

## Steps (agent-driven)

1. **Read `job_search_config.yaml`** (private overlay path when present) and load
   `platforms.yaml` filters for the platforms you will search. Derive search
   queries from roles × `must_include_one_of` (and company career URLs where useful).
2. Search with harness web tools for currently open postings. Cap at
   `automation.max_jobs` unless the user sets another max.
3. Rank against the campaign prefs (roles, must-include / nice / exclude terms,
   company tiers, locations, avoid-roles). Soft bar: relevance ≥ 7 / 10 — drop
   clear mismatches; keep borderline rows with a one-line why.
4. **Present the shortlist** in chat: company, role, URL, score/why, open vs stale if known.
5. **Append** the same shortlist to `applications/shortlists.md` (overlay-aware;
   create if absent). Each session is a fresh block separated by `---`. Session
   header: timestamp, query source (config vs custom text), max, platforms searched.
   Prior sessions are never edited.
6. **Handoff:** invoke `new-application` only for jobs the user accepts, or when they
   already asked to "discover and prep" a stated count. Persist `jd.txt` / scaffold
   as part of that handoff — not for every shortlisted URL.
   `autonomy_level ≥ tailor` governs *scripted* batch runs (`run-pipeline`); it is
   not a silent auto-prep of every hit in chat.

Completion criterion: shortlist shown and appended; every kept row has a URL and a
why; every rejected-with-mention has a why-not; no per-job outputs sources written by this
skill alone.

## Batch fallback

Only when the user explicitly wants the fixed pipeline, or no harness is driving:

```bash
uv run scripts/pipeline.py --dry-run --max 5 --use-project-web          # shortlist only
uv run scripts/pipeline.py --level tailor --max 5 --use-project-web     # discover + tailor
uv run scripts/pipeline.py --build --max 5 --use-project-web            # + build/bundle
```

Library helpers: `scripts/job_discovery.py` (no CLI). Flags, `WEB_BACKEND`, and
pitfalls: `okf/scripts/pipeline.md` / `okf/scripts/job-discovery.md`.
Cloud-model sessions calling AI scripts: see `okf/scripts/llm-provider.md`.
