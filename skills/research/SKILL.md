---
name: research
description: Research a company, team, or topic from the web and produce a concise sourced markdown brief. Use when the user wants background on a company/role, interview prep notes, or any "look this up and summarize" task.
---

# Research a Topic / Company

Produce a short sourced markdown brief for a company, team, or topic.

Architecture (ADR 0004): **Skills orchestrate; Tools process.**

| Piece | What it does | When |
|-------|----------------|------|
| Harness-native web | Search + fetch pages | Agent has built-in web — **prefer this** |
| `gather()` / `--use-project-web` | Same via `scripts/web.py` | Unattended / no harness web only |
| `synthesize()` / `--synthesize-from` | LLM brief from sources | Agent gathered sources **or** scripted after gather |
| `research()` | Batch: gather → synthesize | Unattended only (`--use-project-web`) |

## Tools — when to use / when not

| Tool / command | Use when | Do **not** use when |
|----------------|----------|---------------------|
| Harness web search/extract | Agent session with native web | — |
| `scripts/research.py --synthesize-from …` | You already have sources JSON; want LLM brief | You still need to search the web via this script |
| `scripts/research.py "topic" --use-project-web` | No harness web; unattended brief | Agent already has native web (use agent path) |
| Full `pipeline.py` research step | Unattended batch with `--use-project-web` | Agent can write `research.md` itself |

**Never** call `scripts/web.py` or `gather`/`research` without `--use-project-web` from an agent that has native web.

## Steps

### Agent-driven (harness has native web)

1. Search the topic with harness web tools (2–4 angled queries).
2. Fetch and read the top result pages.
3. Either:
   - Write the markdown brief yourself (Summary / Key facts / What it means for a job applicant), then add a Sources link list, **or**
   - Save sources as JSON `[{title, url, text}, …]` and run:
     `uv run scripts/research.py --synthesize-from sources.json --topic "<topic>" --id <id>`
     (the Tool always appends `## Sources` from the JSON)
4. Save to `applications/jobs/<id>/research.md` (or user path).

### Scripted / unattended (no harness web)

```bash
uv run scripts/research.py "Anthropic interview process" --focus "interview prep" --use-project-web
uv run scripts/research.py "Cohere ML platform team" --id cohere_ml_2026 --use-project-web
uv run scripts/research.py "<topic>" --out notes/topic.md --max 6 --use-project-web
```

Pipeline research step also requires `--use-project-web` or it skips with a message.

Model overrides: `--model <name>` pins the synthesis model; `--use-agent` lets
`LLM_MODEL_RESEARCH` from `.env` apply (per-task pin).

## Pitfalls

- Scripted gather needs an explicit `WEB_BACKEND` in `.env` (`searxng` | `tavily` |
  `brave` | `serper` | `harness`) plus that backend's endpoint/key or harness adapters.
- Briefs cite only fetched sources; failed URLs are listed under `## Failed fetches`.
- Flag thin or conflicting material in the prose.
- Don't treat dates/numbers as ground truth without verifying.
