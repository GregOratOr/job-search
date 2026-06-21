# Scripts Context

## Available Scripts

### `new_application.py` — scaffold a new application bundle

```bash
python scripts/new_application.py --id <id> --company <company> --role <role>
python scripts/new_application.py --id nvidia_ml_2026 --company NVIDIA --role "ML Engineer"
```

Creates:
- `resume/tailoring/<id>.py`        (copy of _template.py with JOB_ID/COMPANY/ROLE set)
- `coverletter/tailoring/<id>.py`   (copy of _template.py)
- `applications/jobs/<id>/job_info.py`

Use `--force` to overwrite existing files.

---

### `build.py` — render .tex files for a given application ID

```bash
python scripts/build.py --id <id>                      # both resume + cover letter
python scripts/build.py --id <id> --only resume        # resume only
python scripts/build.py --id <id> --only coverletter   # cover letter only
python scripts/build.py --id <id> --pdf                # also run pdflatex
```

Outputs land in `resume/outputs/<id>.tex` and `coverletter/outputs/<id>.tex`.

To compile to PDF manually:
```bash
cd resume/outputs && pdflatex <id>.tex && pdflatex <id>.tex
```
Run pdflatex **twice** so bookmarks and cross-references resolve correctly.

---

### `track.py` — log and update job applications

```bash
# Add a new application
python scripts/track.py log --id <id> --platform LinkedIn --url <url>

# Update status
python scripts/track.py update --id <id> --status "Phone Screen"

# List all or filter
python scripts/track.py list
python scripts/track.py list --status Applied

# Inspect one
python scripts/track.py show --id <id>
```

---

## Typical End-to-End Workflow

```bash
# 1. Scaffold
python scripts/new_application.py --id nvidia_ml_2026 --company NVIDIA --role "ML Engineer"

# 2. Edit tailoring files (fill keywords from JD, select entries, write summary)
#    resume/tailoring/nvidia_ml_2026.py
#    coverletter/tailoring/nvidia_ml_2026.py
#    applications/jobs/nvidia_ml_2026/job_info.py

# 3. Build
python scripts/build.py --id nvidia_ml_2026 --pdf

# 4. Apply (upload PDFs from resume/outputs/ and coverletter/outputs/)

# 5. Log
python scripts/track.py log --id nvidia_ml_2026 --platform "Company Website" \
    --url "https://nvidia.wd5.myworkdayjobs.com/..." --notes "Applied via direct site"
```

## Common Errors

| Error                                  | Fix                                                    |
|----------------------------------------|--------------------------------------------------------|
| `ModuleNotFoundError: profile`         | Run from project root; check `sys.path.insert` in file |
| `cv_data not found in module`          | The tailoring file must define `cv_data = CV(...)`    |
| `LaTeX: ! Undefined control sequence`  | Unescaped special char in a bullet — see resume/AGENTS.md |
| `ID already exists` (track.py log)     | Use `update` instead, or pick a new `--id`             |

---

### `ai_tailor.py` — AI tailoring from a JD

```bash
uv run scripts/ai_tailor.py --url "https://..." --id <id>
uv run scripts/ai_tailor.py --jd /path/to/jd.txt --id <id>
uv run scripts/ai_tailor.py --url "..." --id <id> --dry-run    # parse only
uv run scripts/ai_tailor.py --url "..." --id <id> --build      # tailor + build PDF
```

**4-phase pipeline:**
1. `parse_jd()`     — extract company, role, keywords, requirements → JSON
2. `match_profile()` — score EXPERIENCE_REGISTRY + PROJECT_REGISTRY → select + rewrite bullets
3. `write_cover_letter()` — 3 tailored paragraphs
4. `write_outreach()` — connection request, follow-up, cold email, referral ask

**Outputs:**
- `resume/tailoring/{id}.py`
- `coverletter/tailoring/{id}.py`
- `applications/jobs/{id}/job_info.py`
- `applications/jobs/{id}/outreach.md`   ← **copy-paste ready messages**
- `applications/jobs/{id}/jd.txt`

**Model / provider:** configured in `.env` via `LLM_PROVIDER` (`anthropic`, `ollama`, `openai`).
Default model from `LLM_MODEL` or provider-specific defaults. Override per run with `--model`.

Local Ollama example (`.env`):
```
LLM_PROVIDER=ollama
OLLAMA_MODEL=gemma4:12b
OLLAMA_BASE_URL=http://127.0.0.1:11434/v1
```

---

### `job_discovery.py` — Automated job search + full pipeline

```bash
uv run scripts/job_discovery.py                      # uses config defaults
uv run scripts/job_discovery.py --max 10
uv run scripts/job_discovery.py --query "CUDA engineer remote"
uv run scripts/job_discovery.py --max 5 --dry-run    # preview only
uv run scripts/job_discovery.py --max 5 --build      # include PDF compilation
```

Internally calls `discover_jobs()` then loops `ai_tailor.tailor()` for each found job.
Live web search requires `LLM_PROVIDER=anthropic`; with Ollama, discovery uses the local model only (verify URLs manually).

**Common errors:**

| Error | Fix |
|-------|-----|
| `ANTHROPIC_API_KEY not set` | Set `LLM_PROVIDER=ollama` for local Ollama, or add `ANTHROPIC_API_KEY` to `.env` |
| `HTTP 404 from .../chat/completions` | Check `OLLAMA_BASE_URL` and that the model is pulled (`ollama pull <model>`) |
| `Could not fetch JD text` | The URL may block scrapers; save the JD to a file and use `--jd` flag |
| `Unknown experience var 'X'` | Claude hallucinated a var name; edit the tailoring file and replace with a real variable from `EXPERIENCE_REGISTRY` |
| `JSONDecodeError` | Increase `--max_tokens` or retry; Claude occasionally returns malformed JSON |
