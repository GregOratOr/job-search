# Job Search

Automated resume/cover letter generation, AI-powered tailoring, job discovery,
application tracking, and networking pipeline.

This public repository ships with **template/example profile data** so you can
explore the tooling without exposing personal information. Your real data lives
in a **private git submodule** at `private/` (see [Private data setup](#private-data-setup)).

---

## Setup (one time)

```bash
# 1. Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh   # macOS / Linux
# or: pip install uv

# 2. Clone the repo and sync dependencies
git clone https://github.com/yourusername/job-search
cd job-search
uv sync

# 3. Configure LLM provider
cp .env.example .env
# Cloud:  ANTHROPIC_API_KEY=sk-ant-...
# Local:  LLM_PROVIDER=ollama  OLLAMA_MODEL=gemma4:12b

# 4. Clone your Hermes skills (optional)
git submodule add https://github.com/yourusername/skills skills

# 5. Fill in your personal data (see Private data setup below)
```

---

## Private data setup

When `private/` is present and contains `private/profile/`, all scripts automatically
prefer your real data over the public templates.

```bash
# Create a private repo on GitHub (keep it private), then:
git submodule add git@github.com:YOUR_USER/job-search-private.git private
git submodule update --init private
```

Your private repo should mirror this structure:

```
private/
├── profile/              # real contact info, experience, projects
├── applications/         # tracker.csv and job bundles
├── networking/           # connections.csv, message templates
├── resume/tailoring/     # per-job resume files
├── coverletter/tailoring/
├── config/job_search_config.yaml
└── .env                  # API keys (never push to a public remote)
```

---

## Core Workflows

### Tailor a resume from a job posting (URL or paste)

```bash
uv run scripts/ai_tailor.py --url "https://careers.example.com/..." --id acme_ml_2026
uv run scripts/build.py --id acme_ml_2026 --pdf
```

### Manual tailoring (without AI)

```bash
uv run scripts/new_application.py --id acme_ml_2026 --company Acme --role "ML Engineer"
# Edit resume/tailoring/acme_ml_2026.py (5 sections)
uv run scripts/build.py --id acme_ml_2026 --pdf
```

### Update your profile

```bash
# Edit profile/experience.py or profile/projects.py (in private/ if using submodule)
uv run scripts/update_profile.py
```

### Track applications

```bash
uv run scripts/track.py log    --id acme_ml_2026 --platform "Company Website" --url https://...
uv run scripts/track.py update --id acme_ml_2026 --status "Phone Screen"
uv run scripts/track.py list
```

---

## Project Structure

```
job-search/
├── private/                 ← private git submodule (your real data)
├── profile/                 ← template/example data (public)
├── resume/tailoring/        ← template + worked examples
├── applications/            ← schema + templates
├── scripts/data_paths.py    ← routes reads/writes to private/ when present
└── ...
```

---

## Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/)
- LLM configured in `.env` for AI scripts
- LaTeX (TeX Live or MiKTeX) for PDF compilation
