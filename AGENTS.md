# Job Search Project — AGENTS.md

This project automates tailored resume/cover letter generation, tracks job applications,
and manages the networking pipeline.

## ⛔ Profile is Read-Only (Hard Rule)

`profile/` is the single source of truth. **Agents must treat every file under `profile/`
as READ-ONLY.** Do NOT create, edit, or delete any file in `profile/` (header.py,
education.py, experience.py, projects.py, skills.py, summaries.py, research.py,
coursework.py, master_data.py, CHANGELOG.md) unless the user gives an **explicit command
in this conversation to change a specific profile file**.

- Tailoring (rewriting bullets, adding keywords, picking entries) NEVER edits `profile/`.
  All job-specific changes go downstream into `resume/outputs/{id}.py` and
  `coverletter/outputs/{id}_cl.py` via `dataclasses.replace()`.
- The ONLY time you may write to `profile/` is when the user explicitly asks to update
  their profile (e.g. "add my new NVIDIA internship"). Then follow the "Update Your
  Profile" workflow below and append to `profile/CHANGELOG.md`.
- The real, current entry variable names are NOT the illustrative examples in these docs.
  Always discover them at runtime with: `uv run scripts/validate_profile.py --inventory`

## Available Skills

Agent skill wrappers live in `skills/{name}/SKILL.md` (shared by Hermes and Cursor):

| Skill | Use when |
|-------|----------|
| `skills/run-pipeline/SKILL.md`       | Run the scripted batch pipeline honoring `autonomy_level` |
| `skills/tailor-resume/SKILL.md`      | Tailor a resume from a JD/URL to a built 1-page PDF |
| `skills/tailor-coverletter/SKILL.md` | Tailor a cover letter (hook/evidence/close) to a built 1-page PDF |
| `skills/build-documents/SKILL.md`    | Render/compile `.tex` and PDFs |
| `skills/track-application/SKILL.md`  | Log/update applications in tracker.csv |
| `skills/new-application/SKILL.md`    | Orchestrate a single application end to end (intake → bundle) |
| `skills/update-profile/SKILL.md`     | Edit `profile/` — ONLY on explicit user command |
| `skills/discover-jobs/SKILL.md`      | Find open roles → shortlist (+ optional handoff to new-application) |
| `skills/research/SKILL.md`           | Research a company/topic into a sourced brief |
| `skills/find-contacts/SKILL.md`      | Find recruiters/hiring managers via public pages |
| `skills/networking-outreach/SKILL.md`| Draft LinkedIn/email outreach from templates |
| `skills/follow-up/SKILL.md`          | Surface + draft follow-ups for stale applications |
| `skills/audit-application/SKILL.md`| Critique tailored resume/CL before submitting |

## Web access policy

**Harness-native web first; project web tool as fallback.**

| Context | Web access |
|---------|------------|
| Agent harness with built-in search/extract (Hermes, Cursor browser MCP, etc.) | Use the harness tools directly. Do **not** run `scripts/web.py`. |
| Scripted discovery / research / contacts / `ai_tailor --url` | Pass `--use-project-web`; backend from `WEB_BACKEND` in `.env` |
| Standalone terminal / bare Ollama / no harness web | `scripts/web.py` with `WEB_BACKEND` configured (`searxng` / `tavily` / … / `harness`) |
| Agent-driven research or contact-finding | Search and fetch with harness tools; write results to bundle files. Run `scripts/research.py` or `scripts/find_contacts.py` only when no harness web is available. |

See [`docs/adr/0003-project-owned-web-tool.md`](docs/adr/0003-project-owned-web-tool.md) and
[`okf/architecture/web-access-policy.md`](okf/architecture/web-access-policy.md).

## Architecture Overview

```
job-search/
├── .cursor/                         # Cursor IDE config (plans/ and rules/)
├── .vscode/                         # VS Code workspace settings
├── profile/                         # ← SINGLE SOURCE OF TRUTH (split into focused modules)
│   ├── header.py                    #   contact info (HEADER, CL_HEADER)
│   ├── education.py                 #   EXAMPLE_UNIV_MS, EXAMPLE_UNIV_BTECH
│   ├── experience.py                #   EXAMPLE_ML_ENGINEER_ACME, ... (run --inventory for live list)
│   ├── projects.py                  #   PROJ_EXAMPLE_CUDA_KERNEL, ... (run --inventory)
│   ├── skills.py                    #   SKILLS_FULL, SKILLS_ML_FOCUSED, ...
│   ├── summaries.py                 #   SUMMARIES dict
│   ├── research.py                  #   research entries
│   ├── coursework.py                #   coursework entries
│   ├── master_data.py               #   thin re-export of all the above
│   └── CHANGELOG.md                 #   append here after every profile edit
├── resume/
│   ├── cv_utils.py                  # dataclass + enum definitions — no personal data
│   ├── cv2latex.py                  # Jinja2 → LaTeX engine
│   ├── tailoring/_template.py       # scaffold only
│   └── outputs/{id}.py|.tex|.pdf    # per-job source + builds (overlay → private/)
├── coverletter/
│   ├── cl_utils.py                  # cover letter dataclasses
│   ├── cl2latex.py                  # Jinja2 → LaTeX engine
│   ├── tailoring/_template.py       # scaffold only
│   └── outputs/{id}_cl.py|.tex|.pdf # per-job source + builds (overlay → private/)
│   └── jobs/
│       ├── _template/               # example bundle structure (reference only)
│       └── {id}/                    # jd, job_info, networking, {id}_resume.*, {id}_cover_letter.*
├── networking/
│   ├── strategy.md                  # 4-step loop: Find→Connect→Engage→Convert
│   ├── message_templates.md         # LinkedIn/email copy
│   └── connections.csv
├── config/
│   ├── job_search_config.yaml       # search terms, target companies, platforms
│   └── platforms.yaml               # platform playbook (agent reference; not loaded by scripts)
├── private/                         # ← git submodule; overlays all of the above with real data
│   ├── .env                         #   API keys / endpoints (never on a public remote)
│   ├── profile/                     #   real contact info, experience, projects, skills, summaries
│   ├── resume/outputs/              #   per-job resume .py/.tex/.pdf
│   ├── coverletter/outputs/         #   per-job cover letter {id}_cl.py/.tex/.pdf
│   ├── applications/jobs/           #   real per-job bundles + tracker.csv
│   ├── config/                      #   real job_search_config.yaml
│   └── networking/                  #   connections.csv, message templates, strategy
├── skills/                          # Hermes/Cursor agent skills (one subdir per skill)
│   ├── audit-application/
│   ├── build-documents/
│   ├── discover-jobs/
│   ├── find-contacts/
│   ├── follow-up/
│   ├── networking-outreach/
│   ├── new-application/
│   ├── research/
│   ├── run-pipeline/
│   ├── tailor-coverletter/
│   ├── tailor-resume/
│   ├── track-application/
│   └── update-profile/
├── docs/adr/                        # architecture decision records
├── pyproject.toml                   # uv sync handles deps + virtual env
└── scripts/
    ├── pipeline.py                  # E2E orchestrator (discover→tailor→research→build→audit→bundle→track)
    ├── job_discovery.py             # discovery library (discover_jobs / fetch_jd / _make_id)
    ├── ai_tailor.py                 # JD → tailored resume/CL/outreach (4-phase LLM pipeline)
    ├── audit.py                     # hiring-manager critique → applications/jobs/<id>/audit.md
    ├── build.py                     # render .tex (optionally compile to PDF + bundle)
    ├── bundle.py                    # finalize the per-job upload folder
    ├── web.py                       # pluggable web search + page fetch (SearXNG/Tavily/Brave/Serper)
    ├── research.py                  # company/topic research brief via web + LLM
    ├── find_contacts.py             # contacts via queries + public pages (no LinkedIn scraping)
    ├── followup.py                  # surface stale apps + draft follow-up messages
    ├── track.py                     # log/update/list applications in tracker.csv
    ├── new_application.py           # scaffold new application bundle from templates
    ├── validate_profile.py          # validate profile imports + show inventory
    ├── llm_provider.py              # provider-agnostic LLM completions (Anthropic/Ollama/OpenAI)
    ├── json_llm.py                  # JSON-mode LLM helper shared by the AI tools
    ├── text_utils.py                # shared text helpers
    ├── job_info_io.py               # safe reads/writes of per-job job_info.py
    ├── bootstrap.py                 # shared CLI bootstrap (paths + env)
    └── data_paths.py                # routes reads/writes to private/ when present
```

## Setup (run once after cloning)

```bash
uv sync
```

This installs all dependencies and creates the virtual environment. All scripts are then
run with `uv run`, e.g.:
```bash
uv run scripts/validate_profile.py --inventory
```
`uv` handles the virtual environment automatically — no manual activation needed.

---

## Core Design Principle — Single Source of Truth

`profile/` is split into focused files so **agent updates are surgical**.
When adding a new project, only `profile/projects.py` is touched.
When updating contact info, only `profile/header.py` is touched.

**Tailoring files only SELECT and CONFIGURE — they never contain data.**

```python
# CORRECT — resume/outputs/nvidia_ml_2026.py
from dataclasses import replace
from profile.master_data import *

cv_data = CV(
    experience=[
        replace(EXAMPLE_ML_ENGINEER_ACME, highlights=["Job-specific rewrite..."]),
        EXAMPLE_SWE_INTERN_STARTUP,
    ],
    projects=[PROJ_EXAMPLE_ML_PIPELINE, PROJ_EXAMPLE_CUDA_KERNEL],
    ...
)
# Variable names above are illustrative — get the live list with:
#   uv run scripts/validate_profile.py --inventory

# WRONG — never duplicate data from profile/
cv_data = CV(
    experience=[ExperienceEntry(role="Research Assistant", ...)],  # ← violation
)
```

---

## Writing Bullet Points & Summaries — Style Guide

This is the condensed style guide for drafting `highlights` (experience, project, research)
and `summaries`. It applies in two places:
1. **Master profile** entries in `profile/*.py` (only on an explicit "update profile" command).
2. **Per-job rewrites** in `resume/outputs/{id}.py` via `dataclasses.replace()`.

> 📖 **Full reference:** `docs/resume-writing-reference.md` holds the complete, durable
> rule set — the entire Harvard MCS guide (resume language, top mistakes, full DO/DON'T
> lists), the **complete action-verb bank by category**, per-section guidance, cover letter
> tips, and AI-usage rules. **Read it before any profile or tailoring edit** so nothing is
> missed during a long session. The section below is only a quick recap.

Other docs (`profile/AGENTS.md`, `resume/AGENTS.md`, the SKILL.md files) point to the same
reference.

### The XYZ formula (use for every bullet)

Google's formula — **"Accomplished [X], as measured by [Y], by doing [Z]."**

> *Accomplished* a 2.3\\texttimes{} faster inference path (**X**), *as measured by* p99 latency
> dropping from 180ms to 78ms (**Y**), *by doing* CUDA kernel fusion and FP16 quantization (**Z**).

In a resume bullet this compresses to: **[Action verb] + [what you built/did] + [tools/how] +
[quantified result]**. Lead with the verb, end with the metric. If you cannot measure Y,
still name a concrete outcome (shipped, adopted, reduced, enabled) — never stop at the task.

### Harvard MCS guidelines (resume language)

Source: <https://careerservices.fas.harvard.edu/resources/create-a-strong-resume/>

**DO**
- Be **specific, not general**; **active, not passive**; write to **express, not impress**.
- Be **fact-based** — quantify and qualify every claim you can.
- Start each bullet with a strong **action verb**; vary verbs across bullets.
- Use reverse-chronological order within a section (most recent first).
- Write for systems/people that **scan quickly** — front-load the impact.

**DON'T**
- Use personal pronouns ("I", "we") or narrative/full-sentence prose.
- Start a line with a date, abbreviate, or use slang/flowery language.
- Describe duties without results — every bullet should *demonstrate an outcome*.
- Use passive voice ("was responsible for…") — convert to an action verb.

### Action verb bank (Harvard categories)

Pick a verb that matches the work; never reuse the same verb twice in one entry.
**Full list of all verbs per category lives in `docs/resume-writing-reference.md` §3.**

| Category | Sample verbs |
|----------|--------------|
| Leadership   | Led, Directed, Spearheaded, Orchestrated, Oversaw, Coordinated, Improved, Increased |
| Technical    | Built, Designed, Engineered, Optimized, Programmed, Streamlined, Standardized, Overhauled |
| Research     | Investigated, Analyzed, Modeled, Derived, Evaluated, Diagnosed, Tested, Identified |
| Quantitative | Calculated, Computed, Forecasted, Maximized, Minimized, Analyzed, Projected |
| Communication| Authored, Presented, Documented, Collaborated, Negotiated, Synthesized |
| Creative     | Created, Designed, Conceived, Initiated, Introduced, Redesigned, Founded |

### Per-section nuances

- **Experience** — past tense (present tense only for a current role). Each bullet = one
  accomplishment with a metric. 1–3 bullets per entry in a tailored resume.
- **Projects** — same XYZ shape but emphasize **technical approach → scale/scope → outcome**
  (e.g. "Implemented X using Y, trained on N samples, achieving Z").
- **Research** — emphasize the problem, method, and findings; cite frameworks/datasets.
  Outcomes can be insights or benchmarks rather than business metrics.
- **Summary** — 3–4 sentences, no bullets: **who you are → what you build → what you want**.
  In a tailored summary, name the company explicitly. Keep it active and specific.

### Formatting rules (apply everywhere)

- Bold key technical terms with `\textbf{...}` (skills, tools, frameworks, headline metrics).
- Keep each bullet under ~200 characters so it stays on 1–2 lines in the PDF.
- Multiplication factor: `2.3\texttimes{}`. Percentages: `40\%`.
- Escape LaTeX specials in all bullet/summary text: `%→\%`, `&→\&`, `$→\$`, `_→\_`, `#→\#`.

---

## Workflow: Update Your Profile (add experience/projects)

### "I just finished a new internship at NVIDIA"

```
1. Open profile/experience.py
2. Copy the template block at the top
3. Fill in role, company, date, highlights
4. Name it: NVIDIA_INTERN_2026 = ExperienceEntry(...)
5. Add to profile/master_data.py: import + __all__
6. Run: uv run scripts/validate_profile.py   ← validates everything
7. Append to profile/CHANGELOG.md:
   | 2026-06-15 | experience.py | Added NVIDIA_INTERN_2026 |
```

### "I finished a new project"

```
1. Open profile/projects.py
2. Copy the template block
3. Fill in title, organization, date, highlights
4. Name it: PROJ_NAME = ProjectEntry(...)
5. Add to profile/master_data.py: import + __all__
6. uv run scripts/validate_profile.py
7. Append to profile/CHANGELOG.md
```

### "I want to update a bullet point"

```
1. Open the relevant profile file (experience.py or projects.py)
2. Edit the string in the highlights list
3. uv run scripts/validate_profile.py --validate
4. Append to profile/CHANGELOG.md
```

### "I want to add a new skill"

```
1. If not in any Enum: add to resume/cv_utils.py (relevant Enum class)
2. Open profile/skills.py
3. Add .add(EnumClass.value) to the builder chains in relevant presets
4. uv run scripts/validate_profile.py
5. Append to profile/CHANGELOG.md
```

**After any profile change, always run:**
```bash
uv run scripts/validate_profile.py
```

---

## Workflow: Create a Tailored Resume

```bash
# 1. Scaffold
uv run scripts/new_application.py --id nvidia_ml_2026 --company NVIDIA --role "ML Engineer"

# 2. Edit (only 5 sections in resume/outputs/nvidia_ml_2026.py):
#    ① JOB_ID, COMPANY, ROLE
#    ② SectionConfig flags
#    ③ EXPERIENCE list (select entries, use replace() for bullet overrides)
#    ④ PROJECTS list
#    ⑤ SUMMARY string

# 3. Build + finalize the upload bundle
uv run scripts/build.py --id nvidia_ml_2026 --bundle

# 4. Log after applying
uv run scripts/track.py log --id nvidia_ml_2026 --platform "Company Website" --url https://...
```

---

## Workflow: Track Applications

```bash
uv run scripts/track.py log    --id <id> --platform LinkedIn --url <url>
uv run scripts/track.py update --id <id> --status "Phone Screen"
uv run scripts/track.py list
uv run scripts/track.py list   --status Applied
uv run scripts/track.py show   --id <id>
```

Status flow: `Saved → Applied → Recruiter Screen → Phone Screen → Technical Interview → Onsite → Offer → Accepted | Rejected | Withdrawn`

---

## File Naming Conventions

- Application IDs: `{company}_{role}_{year}` lowercase with underscores — e.g. `nvidia_ml_eng_2026`
- Tailoring files: `resume/outputs/{id}.py`, `coverletter/outputs/{id}_cl.py`
- Per-job docs: `resume/outputs/{id}.{py,tex,pdf}`, `coverletter/outputs/{id}_cl.{py,tex,pdf}` (under `private/` when overlay is present)
- Profile variables: `COMPANY_ROLE_YEAR` for experience, `PROJ_{NAME}` for projects

---

## Modifying the Pipeline

| What you want to do                     | Where to change                                      |
|-----------------------------------------|------------------------------------------------------|
| Add a new LaTeX section to the CV       | `resume/cv_utils.py` (SectionConfig + CV) + `cv2latex.py` (LATEX_BODY) |
| Change CV layout / fonts / margins      | `LATEX_PREAMBLE` in `resume/cv2latex.py`             |
| Add a new Enum skill value              | Relevant Enum class in `resume/cv_utils.py`          |
| Add a new cover letter field            | `coverletter/cl_utils.py` + `LATEX_BODY` in `cl2latex.py` |
| Add / remove a job platform             | `active_platforms` in `config/job_search_config.yaml` |
| Add platform-specific steps             | `config/platforms.yaml`                              |
| Update networking message templates     | `networking/message_templates.md`                    |
| Add a new application status            | `STATUS_VALUES` in `scripts/track.py`                |

---

## Suggestions When You Want to Modify Something

**"I want to A/B test two resume versions for the same job"**
→ Create `resume/outputs/{id}_v1.py` and `{id}_v2.py`. Log which was submitted with `--notes "Submitted v2"` in track.py.

**"I want a different summary for each role type"**
→ Add a new key to `profile/summaries.py` → `SUMMARIES` dict, then reference it in the tailoring file.

**"I want to add a Publications section"**
→ Add `show_publications: bool` to `SectionConfig` in `cv_utils.py`. Add the `\newboolean` + `\ifthenelse` block to `LATEX_BODY` in `cv2latex.py`. Add a `publications` field to `CV`. Add entries in `profile/research.py` or a new `profile/publications.py`.

**"I want to keep a master resume that shows everything"**
→ Create `resume/outputs/master_all.py` that includes all experience and projects with `SKILLS_FULL`. Use it to review your full profile.

**"I want to see which applications need follow-up"**
→ `uv run scripts/track.py list --status Applied` shows everything still in Applied state. Cross-reference `date_applied` for ones older than 2 weeks. Or run `uv run scripts/followup.py --list-only` to surface apps past the configured threshold automatically.

**"I want to add a referral to an existing application"**
→ `uv run scripts/track.py update --id <id> --notes "Referred by Jane Doe (jane@co.com)"`.

---

## Important Rules

- Never commit API keys. Use `.env` for secrets.
- `.tex` / `.pdf` under `resume/outputs/` and `coverletter/outputs/` are gitignored —
  rebuild from the `.py` sources (`{id}.py` / `{id}_cl.py`).
- `profile/CHANGELOG.md` must be updated after every profile edit.
- Run `uv run scripts/validate_profile.py` after any profile change to catch broken imports early.
- LaTeX special characters in bullet text must be escaped: `%→\%`, `&→\&`, `$→\$`, `_→\_`.
- `skills/` is project-owned and versioned with this repo. Mirroring it to a personal skills
  repo (e.g. https://github.com/GregOratOr/skills) is optional — see `skills/README.md`.

---

## Workflow: AI Tailoring from a Job Description

The fastest path from JD → ready-to-send application.

### Given a URL
```bash
# --url requires the project-web opt-in (and WEB_BACKEND in .env)
uv run scripts/ai_tailor.py --url "https://careers.nvidia.com/..." --id nvidia_ml_2026 --use-project-web
```

### Given pasted JD text
```bash
# Save the JD to a file first, then:
uv run scripts/ai_tailor.py --jd /tmp/jd.txt --id nvidia_ml_2026
```

### What the script does automatically
1. Fetches + parses the JD (company, role, keywords, requirements)
2. Scores every entry in `EXPERIENCE_REGISTRY` and `PROJECT_REGISTRY` against the JD
3. Rewrites bullet points to hit the JD's keywords (LaTeX-safe output)
4. Generates 3 cover letter paragraphs specific to this company and role
5. Generates 4 ready-to-send outreach messages (connection request, follow-up, cold email, referral ask)
6. Writes all files: `resume/outputs/{id}.py`, `coverletter/outputs/{id}_cl.py`,
   `applications/jobs/{id}/job_info.py`, `applications/jobs/{id}/networking.md`,
   `applications/jobs/{id}/jd.txt`

> **Note:** `ai_tailor.py` reads the education entries dynamically from `profile.education`,
> so the generated tailoring file always matches your profile's actual variable names.

### After the script runs
1. **Review** the generated tailoring file — confirm entry selection and bullet rewrites look right
2. **Tweak** any bullet points in the tailoring file using `replace()` if needed
3. **Build**: `uv run scripts/build.py --id {id} --bundle`
4. **Apply** using the PDF, then log: `uv run scripts/track.py log --id {id} --platform X --url Y`
5. **Outreach**: open `applications/jobs/{id}/networking.md` — all messages are copy-paste ready

### Agent instructions for JD tailoring
When the user provides a JD (as text or URL), the agent should:
1. Save the JD text to `/tmp/jd_<company>.txt` if it's a paste
2. Run `uv run scripts/ai_tailor.py --jd /tmp/jd_<company>.txt --id <id>`
   OR `uv run scripts/ai_tailor.py --url <url> --id <id> --use-project-web`
3. Read the generated `resume/outputs/{id}.py` and verify:
   - The selected entries make sense for the role
   - Bullet points read naturally and hit the JD keywords
   - The summary names the company explicitly
   - The `education` list matches the profile's actual education variable names
4. If anything looks off, edit the tailoring file directly (the agent knows how to use `replace()`)
5. Run `uv run scripts/build.py --id {id}` to confirm the .tex compiles
6. Show the user the path to `applications/jobs/{id}/networking.md` for copy-paste messages

---

## Workflow: Automated Job Discovery

**Agent path (preferred):** follow `skills/discover-jobs/SKILL.md` — shortlist in chat,
append to `applications/shortlists.md`, hand accepted jobs to `new-application`.
Use harness-native web; do not call `scripts/web.py` when the harness already has search.

**Scripted batch** (no harness / explicit pipeline request):

```bash
# Discover + tailor (uses config/job_search_config.yaml)
uv run scripts/pipeline.py --level tailor --use-project-web

# Limit count
uv run scripts/pipeline.py --level tailor --max 10 --use-project-web

# Custom search query
uv run scripts/pipeline.py --level tailor --query "LLM inference optimization remote 2026" --use-project-web

# Preview only — shortlist to terminal, no application files
uv run scripts/pipeline.py --max 10 --dry-run --use-project-web

# Discover + tailor + build PDFs in one shot
uv run scripts/pipeline.py --max 5 --build --use-project-web

# Discover + tailor + build + append networking contacts for each job
uv run scripts/pipeline.py --max 5 --build --find-contacts --use-project-web

# WEB_BACKEND must be set explicitly in .env (searxng|tavily|brave|serper|harness)
```

> **Harness-native web:** When you are an agent inside a harness that already has web
> search/extraction (Cursor, Hermes, etc.), use those tools directly for discovery,
> research, and contact-finding. Do **not** invoke `scripts/web.py` unless the harness lacks
> web access. For scripted runs, pass `--use-project-web` and set `WEB_BACKEND`.

> **Note:** Discovery helpers live in `scripts/job_discovery.py` (library only). Use
> `pipeline.py` for scripted runs. `--search-mode` is retired.
> Platform navigation notes live in `config/platforms.yaml` (agent playbook — not loaded by Python).

### What the scripted pipeline does for each discovered job
1. Searches via `scripts/web.py` (`WEB_BACKEND`) when `--use-project-web` is set — queries
   incorporate `search_terms.must_include_one_of` from config; LLM ranks with campaign prefs
2. Fetches the actual job posting from each URL
3. Runs the full `ai_tailor.py` pipeline (parse → match → cover letter → outreach)
4. Writes ready-to-send messages to `applications/jobs/{id}/networking.md`
5. Saves a copy of the raw JD as `applications/jobs/{id}/jd.txt`
6. Logs each successfully tailored job as `Saved` in `tracker.csv`

### After scripted discovery
- Review `uv run scripts/track.py list` to see all new applications in "Saved" state
- For each job: open `applications/jobs/{id}/networking.md` for the copy-paste outreach messages
- Find the contact on LinkedIn using the search queries in `networking.md`
- Send the connection request (already written, just paste it)
- After they accept (3–7 days): send the follow-up message

### Tuning discovery
Edit `config/job_search_config.yaml` to control:
- `target_roles.primary` — roles to search for
- `target_companies.tier_1/tier_2` — preferred companies
- `search_terms.must_include_one_of` — required technical keywords
- `profile.preferred_locations` — location filter
- `networking.alumni_networks` — alumni labels for outreach / contact queries

Also see `config/platforms.yaml` for board-specific search filters (agent-driven discovery).
---

## Networking Files

Every application gets `applications/jobs/{id}/networking.md` containing:

| Section | Content |
|---------|---------| 
| LinkedIn Search Queries | 3 ready-to-paste search strings to find contacts |
| ① Connection Request | ≤300 chars, paste directly into LinkedIn |
| ② Follow-up Message | Send 3–7 days after connecting |
| ③ Cold Email | Full email with subject line for recruiter outreach |
| ④ Referral Ask | Use only after genuine exchange |

All messages are **fully written** — no placeholders except `[Name]` and `[topic discussed]`.