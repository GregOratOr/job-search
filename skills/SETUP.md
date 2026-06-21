# Agent Setup — Hermes (local Ollama) + Cursor

The skills in this folder are thin wrappers over the deterministic scripts in `scripts/`.
The agent does the reasoning (reading the JD, picking entries, rewriting bullets) and the
scripts do the file generation. No cloud API key is required for this path.

> Hard rule for every agent: `profile/` is READ-ONLY unless the user explicitly asks to
> change a profile file. See root `AGENTS.md` and `.cursor/rules/job-search.mdc`.

---

## Hermes Agent + local Ollama

Hermes (NousResearch/hermes-agent) drives a local model served by Ollama.

```bash
# 1. Pull a capable tool-calling model (larger = more reliable for agentic edits)
ollama pull qwen2.5-coder:32b        # or another strong instruct/coder model

# 2. REQUIRED: give it a >= 64k context window (Hermes rejects smaller)
#    PowerShell (Windows):
setx OLLAMA_CONTEXT_LENGTH 65536
#    then restart the Ollama service so it takes effect

# 3. Configure Hermes to use the local endpoint
hermes setup
#   → choose "Custom endpoint" → http://127.0.0.1:11434/v1
#   → leave the API key blank → select your pulled model
#   (one-shot alternative on recent Ollama builds: `ollama launch hermes`)

# 4. Make these skills available to Hermes
#    Copy (or symlink) this folder into Hermes' skills directory:
#    Windows: xcopy /E /I skills %USERPROFILE%\.hermes\skills
```

Run Hermes **from the repo root** (`L:\Job Search`) so it auto-loads `AGENTS.md` and the
subdirectory `AGENTS.md` files, then prompt naturally, e.g.
"Tailor my resume for this JD: <paste>" or "Find 5 ML Engineer roles and prepare each".

Notes:
- Pick a model with strong tool-calling; small models mangle multi-step file edits.
- `config.yaml` lives at `~/.hermes/config.yaml` if you prefer editing it directly.

---

## Cursor Agent

Cursor reads `AGENTS.md` and `.cursor/rules/job-search.mdc` natively, so the workflow and
the profile read-only guardrail apply automatically. Open the repo and use Agent mode; it
will run the `scripts/` commands and read `skills/{name}/SKILL.md` as needed.

- Recommended: use Cursor's own (frontier) models to drive the scripts — most reliable.
- Optional local model in Cursor: Settings → Models → Override OpenAI Base URL. Note
  Cursor routes BYOK through its servers, so `localhost` needs an HTTPS tunnel
  (ngrok/Cloudflare) and model names with `:`/`-` can hit a validation bug. Tab stays cloud.

---

## What stays untouched
`scripts/ai_tailor.py` and `scripts/job_discovery.py` use `scripts/llm_provider.py` and read
`LLM_PROVIDER` from `.env` (`anthropic`, `ollama`, or `openai`-compatible). For agent-driven
search/tailoring without those scripts, use the `discover-jobs` and `tailor-resume` skills with Hermes.
