<!-- scripts/AGENTS.md -->
# Scripts Context

## Project layout — public repo + private submodule

The repo is **public**. Sensitive data (profile, resumes, applications, config, keys)
lives in a **private git submodule** at `private/`. When it is checked out,
`scripts/data_paths.py` automatically routes all reads and writes there.

```
private/
  profile/          ← Python package (imported as `profile`)
  resume/           ← templates in tailoring/; per-job .py/.tex/.pdf in outputs/
  coverletter/      ← templates in tailoring/; per-job .py/.tex/.pdf in outputs/
  applications/     ← per-job bundles, tracker.csv
  config/           ← job_search_config.yaml
  networking/       ← global networking notes
  .env              ← API keys and provider config
```

If `private/` is absent the scripts fall back to the public template directories
in the repo root — useful for contributors who don't have the private submodule.

## Web access policy

**Harness-native web first; `scripts/web.py` as fallback.**

- Agent harnesses with built-in search/extract (Hermes, Cursor browser MCP, Anthropic
  `web_search`): use harness tools directly; do **not** run `scripts/web.py`.
- Standalone / scripted runs: `scripts/web.py` with `WEB_BACKEND` set explicitly
  (`searxng` | `tavily` | `brave` | `serper` | `harness` — no implicit default).
- `job_discovery.py` / `pipeline.py` discovery: pass `--use-project-web`; backend via
  `WEB_BACKEND` (`--search-mode` retired).

See [`okf/architecture/web-access-policy.md`](../okf/architecture/web-access-policy.md).

## Package manager — uv

All scripts are run with **`uv run`**. Never use bare `python scripts/…`.

```bash
uv run scripts/ai_tailor.py --url "..." --id nvidia_ml_2026 --use-project-web
uv run scripts/build.py --id nvidia_ml_2026 --pdf
uv run scripts/track.py log --id nvidia_ml_2026 --platform LinkedIn --url "..."
```

`uv` reads `pyproject.toml` for dependencies and handles the virtual environment
automatically. No manual `pip install` or venv activation needed.

---

## Available Scripts

### `new_application.py` — scaffold a new application bundle

```bash
uv run scripts/new_application.py --id <id> --company <company> --role <role>
uv run scripts/new_application.py --id nvidia_ml_2026 --company NVIDIA --role "ML Engineer"
```

Creates:
- `resume/outputs/<id>.py` (copy of _template.py with JOB_ID/COMPANY/ROLE/OUTPUT_FILE set)
- `coverletter/outputs/<id>_cl.py` (copy of _template.py)
- `applications/jobs/<id>/job_info.py`

All files land in `private/` when the submodule is present.
Use `--force` to overwrite existing files.

---

### `build.py` — render .tex files for a given application ID

```bash
uv run scripts/build.py --id <id>                      # both resume + cover letter
uv run scripts/build.py --id <id> --only resume        # resume only
uv run scripts/build.py --id <id> --only coverletter   # cover letter only
uv run scripts/build.py --id <id> --pdf                # also run pdflatex
uv run scripts/build.py --id <id> --bundle             # pdf + move .py/.tex/.pdf into bundle
uv run scripts/build.py --id <id> --private --pdf      # force private/ paths
uv run scripts/build.py --id <id> --public             # force public repo-root paths
```

Sources and builds land in `resume/outputs/<id>.{py,tex,pdf}` and
`coverletter/outputs/<id>_cl.{py,tex,pdf}` (under `private/` when the overlay is active).
`build.py` / `cv2latex.py` / `cl2latex.py` all resolve paths via `scripts.data_paths`
(`--id` + optional `--private`/`--public`).

Engines directly:
```bash
uv run resume/cv2latex.py --id <id> --private
uv run coverletter/cl2latex.py --id <id> --private
```

To compile to PDF manually:
```bash
cd private/resume/outputs   # or resume/outputs without overlay
pdflatex <id>.tex && pdflatex <id>.tex
```
Run pdflatex **twice** so bookmarks and cross-references resolve correctly.
PDF compilation requires a LaTeX distribution (TeX Live or MiKTeX) on PATH —
`build.py` exits with an install hint when `pdflatex` is missing.

---

### `bundle.py` — finalize the per-job upload folder

```bash
uv run scripts/bundle.py --id <id>              # move .py/.tex/.pdf into the bundle + clean temp
uv run scripts/bundle.py --id <id> --keep-temp  # keep LaTeX temp files
uv run scripts/bundle.py --id <id> --private    # force private/ paths (--public for repo root)
```

Moves `resume/outputs/<id>.*` and `coverletter/outputs/<id>_cl.*` into
`applications/jobs/<id>/` as `<id>_resume.*` / `<id>_cover_letter.*` and deletes
LaTeX temp files. `build.py --bundle` runs this automatically.

---

### `track.py` — log and update job applications

```bash
# Add a new application (log defaults to status "Applied"; override with --status)
uv run scripts/track.py log --id <id> --platform LinkedIn --url <url>
uv run scripts/track.py log --id <id> --platform LinkedIn --status Saved

# Update status
uv run scripts/track.py update --id <id> --status "Phone Screen"

# List all or filter
uv run scripts/track.py list
uv run scripts/track.py list --status Applied

# Inspect one
uv run scripts/track.py show --id <id>
```

Other `log` flags: `--company`, `--role`, `--recruiter`, `--resume-version`, `--notes`
(company/role/platform/url are auto-read from `job_info.py` when present).

Valid statuses: `Saved → Applied → Recruiter Screen → Phone Screen →
Technical Interview → Onsite → Offer → Accepted | Rejected | Withdrawn`

**Programmatic:** `log_saved(job_id, ...)` — called by `pipeline.py` after tailoring (status `Saved`).

---

## Typical End-to-End Workflow

```bash
# 1. Scaffold
uv run scripts/new_application.py --id nvidia_ml_2026 --company NVIDIA --role "ML Engineer"

# 2. Edit the per-job sources (fill keywords from JD, select entries, write summary)
#    resume/outputs/nvidia_ml_2026.py
#    coverletter/outputs/nvidia_ml_2026_cl.py
#    applications/jobs/nvidia_ml_2026/job_info.py

# 3. Build
uv run scripts/build.py --id nvidia_ml_2026 --pdf

# 4. Apply (upload PDFs from resume/outputs/ and coverletter/outputs/)

# 5. Log
uv run scripts/track.py log --id nvidia_ml_2026 --platform "Company Website" \
    --url "https://nvidia.wd5.myworkdayjobs.com/..." --notes "Applied via direct site"

# 6. Follow up (run after 7+ days)
uv run scripts/followup.py
```

## Common Errors

| Error                                  | Fix                                                        |
|----------------------------------------|------------------------------------------------------------|
| `ModuleNotFoundError: profile`         | Run from project root; check `private/` submodule is init'd |
| `cv_data not found in module`          | The per-job file must define `cv_data = CV(...)`          |
| `LaTeX: ! Undefined control sequence`  | Unescaped special char in a bullet — see resume/AGENTS.md |
| `pdflatex not found on PATH`           | Install TeX Live or MiKTeX, or drop `--pdf`/`--bundle`    |
| `WEB_BACKEND is not set`               | Set `WEB_BACKEND` in `.env` (see `.env.example`)          |
| `ID already exists` (track.py log)     | Use `update` instead, or pick a new `--id`                |

---

### `ai_tailor.py` — AI tailoring from a JD

```bash
uv run scripts/ai_tailor.py --url "https://..." --id <id> --use-project-web
uv run scripts/ai_tailor.py --jd /path/to/jd.txt --id <id>
uv run scripts/ai_tailor.py --url "..." --id <id> --use-project-web --dry-run  # parse only
uv run scripts/ai_tailor.py --url "..." --id <id> --use-project-web --build    # tailor + build PDF
```

`--url` requires `--use-project-web` (ADR 0004); `--jd` reads a local file and needs no web.
Other flags: `--provider`, `--model`, `--use-agent`.

**4-phase pipeline:**
1. `parse_jd()`      → extract company, role, keywords, requirements → JSON
2. `match_profile()` → score EXPERIENCE_REGISTRY + PROJECT_REGISTRY → select + rewrite bullets
3. `write_cover_letter()` → 3 tailored paragraphs
4. `write_outreach()` → connection request, follow-up, cold email, referral ask

Education and background in phases 2 & 4 are read **dynamically from
`profile.education`** — not hardcoded — so they stay in sync with your profile.

**Outputs:**
- `resume/outputs/{id}.py`
- `coverletter/outputs/{id}_cl.py`
- `applications/jobs/{id}/job_info.py`
- `applications/jobs/{id}/networking.md`   ← copy-paste ready messages
- `applications/jobs/{id}/jd.txt`

All outputs land in `private/` when the submodule is present.

**Model / provider:** configured entirely in `.env` — no hardcoded model names in code.
Provider via `LLM_PROVIDER` (`anthropic`, `ollama`, `openai`). Model resolution:
explicit `--model` → `LLM_MODEL_<TASK>` **only with** `--use-agent` (`TAILOR`, `AUDIT`,
`RESEARCH`, `DISCOVERY`, `FOLLOWUP`) → `LLM_MODEL` → provider variable
(`OLLAMA_MODEL` / `ANTHROPIC_MODEL` / `OPENAI_MODEL`).

Local Ollama example (`.env`):
```
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen3.6:27b-q4_K_M
OLLAMA_BASE_URL=http://127.0.0.1:11434/v1
# optional per-task pin:
LLM_MODEL_AUDIT=claude-opus-4-7
```

---

### `job_discovery.py` — Discovery library (no CLI)

Exports `discover_jobs()`, `fetch_jd()`, `_make_id()` for `pipeline.py`. Scripted
discovery is always via `pipeline.py` (this module has no `__main__`).

```bash
uv run scripts/pipeline.py --level tailor --max 5 --use-project-web
uv run scripts/pipeline.py --dry-run --max 5 --use-project-web
```

**Common errors:** (see `pipeline.py` — same discovery/tailor stack)

---

### `pipeline.py` — End-to-end orchestrator (primary)

```bash
uv run scripts/pipeline.py --use-project-web                  # config autonomy_level + web
uv run scripts/pipeline.py --level tailor --max 3 --use-project-web
uv run scripts/pipeline.py --dry-run --max 5 --use-project-web
uv run scripts/pipeline.py --build --max 5 --find-contacts --use-project-web
uv run scripts/pipeline.py --url "https://..." --id <id> --use-project-web
uv run scripts/pipeline.py --jd jd.txt --id <id>              # local JD
uv run scripts/pipeline.py --id <id> --steps build,track      # piecewise (no web)
uv run scripts/pipeline.py --id <id> --steps audit
uv run scripts/pipeline.py --gate --use-project-web           # confirm each per-job step
```

Other flags: `--query`, `--model`, `--provider`, `--use-agent`.

**Steps:** `discover → tailor → research → build → audit → bundle → track`

**Web:** Discovery/fetch/research/contacts need `--use-project-web`. Backend is `WEB_BACKEND`
in `.env` (`searxng` | `tavily` | `brave` | `serper` | `harness`) — it must be set
explicitly (or via `automation.web_backend` in config). `--search-mode` is retired
(accepted but ignored).

**Autonomy levels:**

| Level          | Steps run                                      |
|----------------|------------------------------------------------|
| `discover_only`| discover                                       |
| `tailor`       | discover, tailor, **track** (logs as Saved via `log_saved()`) |
| `full_bundle`  | discover, tailor, research, build, audit, bundle, track |

The `audit` step writes `applications/jobs/<id>/audit.md` (advisory only) and can also run
independently via `scripts/audit.py --id <id>`.

**Models:** resolved per step from `.env` → `--model` → `LLM_MODEL_<TASK>` only with
`--use-agent` → `LLM_MODEL` → provider variable. No hardcoded model names in code.

HARD CEILING: never auto-submits applications, never auto-sends messages.

---

### `research.py` — Company/topic research brief

```bash
# Unattended (requires project web opt-in)
uv run scripts/research.py "NVIDIA inference org structure" --use-project-web
uv run scripts/research.py "Anthropic interview process" --focus "interview prep" --use-project-web
uv run scripts/research.py "Cohere ML platform team" --id cohere_ml_2026 --use-project-web

# Agent already gathered sources → LLM synthesize only
uv run scripts/research.py --synthesize-from sources.json --topic "Cohere" --id cohere_ml_2026
```

Other flags: `--max`, `--model`, `--use-agent`, `--out`.

When `--id` is given, writes to `applications/jobs/<id>/research.md` (in `private/`).
The pipeline `research` step also requires `--use-project-web` or it skips.
See ADR 0004 and `skills/research/SKILL.md`.

---

### `find_contacts.py` — Find networking contacts

```bash
# Queries only (no web I/O)
uv run scripts/find_contacts.py --company NVIDIA --role "ML Engineer"
# Also scan public pages (needs WEB_BACKEND)
uv run scripts/find_contacts.py --company Cohere --id cohere_ml_2026 --use-project-web
```

Other flags: `--domain` (Hunter enrichment), `--max` (pages to scan).

When `--id` is given, appends a "Contacts" section to the job's `networking.md`.
Pass `--find-contacts` to `pipeline.py` to run per job.
Uses `append_contacts_for_job()` — shared with pipeline's contact step.

---

### `followup.py` — Draft follow-up messages

```bash
uv run scripts/followup.py                   # list due apps + draft messages
uv run scripts/followup.py --list-only       # just show what's due
uv run scripts/followup.py --days 10         # override threshold
uv run scripts/followup.py --id <id>         # draft for one application
uv run scripts/followup.py --use-agent       # use LLM_MODEL_FOLLOWUP (or --model <m>)
```

Reads `tracker.csv` for applications in `Applied` → `Onsite` that are
older than `follow_up_delay_days` (default 7, from `config/job_search_config.yaml`).
`Saved`, `Offer`, and terminal statuses are skipped.
Drafts are written to `applications/jobs/<id>/networking.md` — **never sent automatically**.

---

### `audit.py` — critique tailored application documents

```bash
uv run scripts/audit.py --id nvidia_ml_2026
uv run scripts/audit.py --id nvidia_ml_2026 --provider anthropic --model claude-opus-4-7
uv run scripts/audit.py --id nvidia_ml_2026 --out custom_audit.md --use-agent
```

Four LLM phases: resume audit, cover letter audit, factual accuracy vs profile ground truth,
action plan. Writes `applications/jobs/<id>/audit.md` (override with `--out`). Read-only —
never edits profile or tailoring files. See `skills/audit-application/SKILL.md`.

---

### `web.py` — project web tool (fallback)

```bash
uv run scripts/web.py search "ML engineer remote 2026" --max 8
uv run scripts/web.py search "..." --backend tavily --json
uv run scripts/web.py fetch "https://example.com/job/123"
uv run scripts/web.py fetch "https://..." --max-chars 8000
```

Requires `WEB_BACKEND` in `.env` (or `--backend` per run) — there is no implicit default.
Use only when the harness lacks native web tools. Agent sessions with built-in search/extract
should use those instead.

---

### `validate_profile.py` — Validate profile imports (read-only)

```bash
uv run scripts/validate_profile.py              # full report
uv run scripts/validate_profile.py --validate   # import check only (for CI)
uv run scripts/validate_profile.py --changelog  # recent changelog
uv run scripts/validate_profile.py --inventory  # all profile entries
```

Deprecated alias: `scripts/update_profile.py` (same flags; prints a rename notice).
Does **not** edit `profile/` — use the `update-profile` skill for that, then re-validate.
