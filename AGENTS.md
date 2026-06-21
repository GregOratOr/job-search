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
  All job-specific changes go downstream into `resume/tailoring/{id}.py` and
  `coverletter/tailoring/{id}.py` via `dataclasses.replace()`.
- The ONLY time you may write to `profile/` is when the user explicitly asks to update
  their profile (e.g. "add my new NVIDIA internship"). Then follow the "Update Your
  Profile" workflow below and append to `profile/CHANGELOG.md`.
- The real, current entry variable names are NOT the illustrative examples in these docs.
  Always discover them at runtime with: `python scripts/update_profile.py --inventory`.

## Available Skills

Agent skill wrappers live in `skills/{name}/SKILL.md` (shared by Hermes and Cursor):

| Skill | Use when |
|-------|----------|
| `skills/tailor-resume/SKILL.md`      | Tailor resume + cover letter from a JD/URL |
| `skills/build-documents/SKILL.md`    | Render/compile `.tex` and PDFs |
| `skills/track-application/SKILL.md`  | Log/update applications in tracker.csv |
| `skills/new-application/SKILL.md`    | Scaffold a new application bundle |
| `skills/update-profile/SKILL.md`     | Edit `profile/` — ONLY on explicit user command |
| `skills/discover-jobs/SKILL.md`      | Find open roles (agent web tools) + tailor each |
| `skills/networking-outreach/SKILL.md`| Draft LinkedIn/email outreach from templates |

## Architecture Overview

```
job-search/
├── profile/                         # ← SINGLE SOURCE OF TRUTH (split into focused modules)
│   ├── header.py                    #   contact info (HEADER, CL_HEADER)
│   ├── education.py                 #   OSU_MS, VIT_BTECH
│   ├── experience.py                #   AI_INTEGRATOR_DAKDAN, ... (run --inventory for live list)
│   ├── projects.py                  #   PROJ_XRAY_DENOISING_CAPSTONE, ... (run --inventory)
│   ├── skills.py                    #   SKILLS_FULL, SKILLS_ML_FOCUSED, ...
│   ├── summaries.py                 #   SUMMARIES dict
│   ├── research.py                  #   research entries
│   ├── coursework.py                #   coursework entries
│   ├── master_data.py               #   thin re-export of all the above
│   └── CHANGELOG.md                 #   append here after every profile edit
├── resume/
│   ├── cv_utils.py                  # dataclass + enum definitions — no personal data
│   ├── cv2latex.py                  # Jinja2 → LaTeX engine
│   └── tailoring/
│       ├── _template.py             # copy this per job (5 sections to edit)
│       └── {id}.py                  # per-job tailoring files
├── coverletter/
│   ├── cl_utils.py                  # cover letter dataclasses
│   ├── cl2latex.py                  # Jinja2 → LaTeX engine
│   └── tailoring/
│       ├── _template.py
│       └── {id}.py
├── applications/
│   ├── tracker.csv                  # master application log
│   └── jobs/{id}/job_info.py        # per-job metadata, keywords, networking targets
├── networking/
│   ├── strategy.md                  # 4-step loop: Find→Connect→Engage→Convert
│   ├── message_templates.md         # LinkedIn/email copy
│   └── connections.csv
├── config/
│   ├── job_search_config.yaml       # search terms, target companies, platforms
│   └── platforms.yaml               # per-platform application steps
├── skills/                          # Hermes agent skills (GregOratOr/skills submodule)
├── pyproject.toml                   # pip install -e . for clean imports everywhere
└── scripts/
    ├── new_application.py           # scaffold new application bundle
    ├── build.py                     # render .tex (optionally compile to PDF)
    ├── track.py                     # log/update/list applications
    └── update_profile.py            # validate profile imports + show inventory
```

## Setup (run once after cloning)

```bash
pip install -e .
```

This registers the project as a package so every file can import cleanly:
```python
from profile.experience import AI_INTEGRATOR_DAKDAN   # works from anywhere
from resume.cv_utils import CV
```
No `sys.path` hacks needed.

---

## Core Design Principle — Single Source of Truth

`profile/` is split into focused files so **agent updates are surgical**.
When adding a new project, only `profile/projects.py` is touched.
When updating contact info, only `profile/header.py` is touched.

**Tailoring files only SELECT and CONFIGURE — they never contain data.**

```python
# CORRECT — resume/tailoring/nvidia_ml_2026.py
from dataclasses import replace
from profile.master_data import *

cv_data = CV(
    experience=[
        replace(AI_INTEGRATOR_DAKDAN, highlights=["Job-specific rewrite..."]),
        UNITY_DEV_INGNIOUS,
    ],
    projects=[PROJ_PMD_CAMERA_CUDA, PROJ_MEDICAL_IMAGE_DENOISING],
    ...
)
# Variable names above are illustrative — get the live list with:
#   python scripts/update_profile.py --inventory

# WRONG — never duplicate data from profile/
cv_data = CV(
    experience=[ExperienceEntry(role="Research Assistant", ...)],  # ← violation
)
```

---

## Workflow: Update Your Profile (add experience/projects)

### "I just finished a new internship at NVIDIA"

```
1. Open profile/experience.py
2. Copy the template block at the top
3. Fill in role, company, date, highlights
4. Name it: NVIDIA_INTERN_2026 = ExperienceEntry(...)
5. Add to profile/master_data.py: import + __all__
6. Run: python scripts/update_profile.py   ← validates everything
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
6. python scripts/update_profile.py
7. Append to profile/CHANGELOG.md
```

### "I want to update a bullet point"

```
1. Open the relevant profile file (experience.py or projects.py)
2. Edit the string in the highlights list
3. python scripts/update_profile.py --validate
4. Append to profile/CHANGELOG.md
```

### "I want to add a new skill"

```
1. If not in any Enum: add to resume/cv_utils.py (relevant Enum class)
2. Open profile/skills.py
3. Add .add(EnumClass.value) to the builder chains in relevant presets
4. python scripts/update_profile.py
5. Append to profile/CHANGELOG.md
```

**After any profile change, always run:**
```bash
python scripts/update_profile.py
```

---

## Workflow: Create a Tailored Resume

```bash
# 1. Scaffold
python scripts/new_application.py --id nvidia_ml_2026 --company NVIDIA --role "ML Engineer"

# 2. Edit (only 5 sections in resume/tailoring/nvidia_ml_2026.py):
#    ① JOB_ID, COMPANY, ROLE
#    ② SectionConfig flags
#    ③ EXPERIENCE list (select entries, use replace() for bullet overrides)
#    ④ PROJECTS list
#    ⑤ SUMMARY string

# 3. Build
python scripts/build.py --id nvidia_ml_2026 --pdf

# 4. Log after applying
python scripts/track.py log --id nvidia_ml_2026 --platform "Company Website" --url https://...
```

---

## Workflow: Track Applications

```bash
python scripts/track.py log    --id <id> --platform LinkedIn --url <url>
python scripts/track.py update --id <id> --status "Phone Screen"
python scripts/track.py list
python scripts/track.py list   --status Applied
python scripts/track.py show   --id <id>
```

Status flow: `Saved → Applied → Recruiter Screen → Phone Screen → Technical Interview → Onsite → Offer → Accepted | Rejected | Withdrawn`

---

## File Naming Conventions

- Application IDs: `{company}_{role}_{year}` lowercase with underscores — e.g. `nvidia_ml_eng_2026`
- Tailoring files: `resume/tailoring/{id}.py`, `coverletter/tailoring/{id}.py`
- Output .tex: `resume/outputs/{id}.tex`, `coverletter/outputs/{id}.tex`
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
| Add a new application status            | `STATUS_VALUES` in `scripts/track.py` + `applications/schema.md` |

---

## Suggestions When You Want to Modify Something

**"I want to A/B test two resume versions for the same job"**
→ Create `resume/tailoring/{id}_v1.py` and `{id}_v2.py`. Log which was submitted with `--notes "Submitted v2"` in track.py.

**"I want a different summary for each role type"**
→ Add a new key to `profile/summaries.py` → `SUMMARIES` dict, then reference it in the tailoring file.

**"I want to add a Publications section"**
→ Add `show_publications: bool` to `SectionConfig` in `cv_utils.py`. Add the `\newboolean` + `\ifthenelse` block to `LATEX_BODY` in `cv2latex.py`. Add a `publications` field to `CV`. Add entries in `profile/research.py` or a new `profile/publications.py`.

**"I want to keep a master resume that shows everything"**
→ Create `resume/tailoring/master_all.py` that includes all experience and projects with `SKILLS_FULL`. Use it to review your full profile.

**"I want to see which applications need follow-up"**
→ `python scripts/track.py list --status Applied` shows everything still in Applied state. Cross-reference `date_applied` for ones older than 2 weeks.

**"I want to add a referral to an existing application"**
→ `python scripts/track.py update --id <id> --notes "Referred by Jane Doe (jane@co.com)"`.

---

## Important Rules

- Never commit API keys. Use `.env` for secrets.
- `resume/outputs/` and `coverletter/outputs/` are gitignored — rebuild from tailoring files.
- `profile/CHANGELOG.md` must be updated after every profile edit.
- Run `python scripts/update_profile.py` after any profile change to catch broken imports early.
- LaTeX special characters in bullet text must be escaped: `%→\\%`, `&→\\&`, `$→\\$`, `_→\\_`.
- `skills/` should stay in sync with https://github.com/GregOratOr/skills — use git submodule.

---

## Workflow: AI Tailoring from a Job Description

The fastest path from JD → ready-to-send application.

### Given a URL
```bash
uv run scripts/ai_tailor.py --url "https://careers.nvidia.com/..." --id nvidia_ml_2026
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
6. Writes all files: `resume/tailoring/{id}.py`, `coverletter/tailoring/{id}.py`, `applications/jobs/{id}/outreach.md`

### After the script runs
1. **Review** the generated tailoring file — confirm entry selection and bullet rewrites look right
2. **Tweak** any bullet points in the tailoring file using `replace()` if needed
3. **Build**: `uv run scripts/build.py --id {id} --pdf`
4. **Apply** using the PDF, then log: `uv run scripts/track.py log --id {id} --platform X --url Y`
5. **Outreach**: open `applications/jobs/{id}/outreach.md` — all messages are copy-paste ready

### Agent instructions for JD tailoring
When the user provides a JD (as text or URL), the agent should:
1. Save the JD text to `/tmp/jd_<company>.txt` if it's a paste
2. Run `uv run scripts/ai_tailor.py --jd /tmp/jd_<company>.txt --id <id>`
   OR `uv run scripts/ai_tailor.py --url <url> --id <id>`
3. Read the generated `resume/tailoring/{id}.py` and verify:
   - The selected entries make sense for the role
   - Bullet points read naturally and hit the JD keywords
   - The summary names the company explicitly
4. If anything looks off, edit the tailoring file directly (the agent knows how to use `replace()`)
5. Run `uv run scripts/build.py --id {id}` to confirm the .tex compiles
6. Show the user the path to `applications/jobs/{id}/outreach.md` for copy-paste messages

---

## Workflow: Automated Job Discovery

Find jobs, tailor everything, generate all outreach — in one command.

```bash
# Discover up to 5 jobs matching your profile (uses config/job_search_config.yaml)
uv run scripts/job_discovery.py

# Limit count
uv run scripts/job_discovery.py --max 10

# Custom search query
uv run scripts/job_discovery.py --query "LLM inference optimization remote 2026"

# Preview only — see what would be found without writing files
uv run scripts/job_discovery.py --max 10 --dry-run

# Discover + tailor + build PDFs in one shot
uv run scripts/job_discovery.py --max 5 --build
```

### What the script does automatically for each discovered job
1. Searches the web (Claude + web_search tool) for open positions
2. Fetches the actual job posting from each URL
3. Runs the full `ai_tailor.py` pipeline (parse → match → cover letter → outreach)
4. Updates `applications/jobs/{id}/outreach.md` with ready-to-send messages
5. Saves a copy of the raw JD as `applications/jobs/{id}/jd.txt`

### After discovery
- Review `uv run scripts/track.py list` to see all new applications in "Saved" state
- For each job: open `applications/jobs/{id}/outreach.md` for the copy-paste outreach messages
- Find the contact on LinkedIn using the search queries in `outreach.md`
- Send the connection request (already written, just paste it)
- After they accept (3–7 days): send the follow-up message

### Tuning discovery
Edit `config/job_search_config.yaml` to control:
- `target_roles.primary` — roles to search for
- `target_companies.tier_1/tier_2` — preferred companies
- `search_terms.must_include_one_of` — required technical keywords
- `profile.preferred_locations` — location filter

---

## Outreach Files

Every application gets `applications/jobs/{id}/outreach.md` containing:

| Section | Content |
|---------|---------|
| LinkedIn Search Queries | 3 ready-to-paste search strings to find contacts |
| ① Connection Request | ≤300 chars, paste directly into LinkedIn |
| ② Follow-up Message | Send 3–7 days after connecting |
| ③ Cold Email | Full email with subject line for recruiter outreach |
| ④ Referral Ask | Use only after genuine exchange |

All messages are **fully written** — no placeholders except `[Name]` and `[topic discussed]`.
