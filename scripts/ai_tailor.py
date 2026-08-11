#!/usr/bin/env -S uv run
"""
scripts/ai_tailor.py
--------------------
AI-powered tailoring from a job description (text or URL).

Given a JD this script runs four LLM calls in sequence:
  1. Parse JD   → structured JSON (company, role, keywords, requirements)
  2. Match      → select best profile entries + rewrite bullets for this JD
  3. Cover letter → 3 tailored paragraphs
  4. Outreach   → connection request, follow-up, cold email, referral ask

Outputs created:
  resume/outputs/{id}.py          (overlay → private/resume/outputs/…)
  coverletter/outputs/{id}_cl.py
  applications/jobs/{id}/job_info.py
  applications/jobs/{id}/networking.md
  applications/jobs/{id}/jd.txt         (saved copy of the JD)

Re-runs: prior resume/cover letter deliverables are archived as
``{stem} (1).*`` (then ``(2)``, …); ``job_info.py`` / ``networking.md`` / ``jd.txt``
are overwritten (one of each per application).

Usage:
    # Standalone — reads provider/model from .env:
    uv run scripts/ai_tailor.py --url "https://nvidia.com/careers/..." --id nvidia_ml_2026
    uv run scripts/ai_tailor.py --jd path/to/jd.txt --id nvidia_ml_2026
    uv run scripts/ai_tailor.py --url "..." --id nvidia_ml_2026 --dry-run

    # Inside a cloud harness (Cursor / Hermes + cloud model) — override .env:
    uv run scripts/ai_tailor.py --jd jd.txt --id <id> \\
        --provider anthropic --model claude-opus-4-7

    # Inside Hermes + Ollama — no flags needed (.env Ollama config used as-is):
    uv run scripts/ai_tailor.py --jd jd.txt --id <id>

Provider / model resolution (see scripts/llm_provider.py for full details):
  --provider / --model flags  →  highest priority; override .env for this run only.
  LLM_PROVIDER / LLM_MODEL in .env  →  default for standalone / Ollama-harness use.
  Auto-detect from API keys / OLLAMA_BASE_URL  →  fallback.

Requirements:
    Configure LLM in .env — see .env.example (anthropic, ollama, or openai-compatible).
"""

import argparse
import datetime
import os
import re
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.data_paths import (
    apply_private_overlay,
    data_path,
    document_py,
    document_stem,
    document_tex,
    rel_to_root,
)
from scripts.json_llm import call_json
from scripts.llm_provider import complete, get_default_model, load_env, resolve_provider
from scripts.text_utils import strip_latex
from scripts import web

apply_private_overlay()
load_env()


def _rel(path: Path) -> str:
    """Alias for ``rel_to_root`` (kept for call-site clarity in generators)."""
    return rel_to_root(path)


_DOC_SUFFIXES = (".py", ".tex", ".pdf")


def _outputs_stem_taken(outputs_dir: Path, stem: str) -> bool:
    return any((outputs_dir / f"{stem}{suffix}").exists() for suffix in _DOC_SUFFIXES)


def _next_archive_stem(outputs_dir: Path, job_id: str) -> str:
    """Return ``{job_id} (n)`` for the first free archive slot."""
    n = 1
    while True:
        candidate = f"{job_id} ({n})"
        if not _outputs_stem_taken(outputs_dir, candidate):
            return candidate
        n += 1


def archive_existing_outputs(kind: str, job_id: str) -> str | None:
    """If the current outputs stem already exists, rename to ``{stem} (n).*``.

    Resume uses ``{id}``; cover letter uses ``{id}_cl``. Keeps the canonical
    path free for the new tailor write so build/audit still resolve the latest.
    Returns the archive stem, or None if nothing to archive.
    """
    outputs_dir = data_path(kind, "outputs")
    stem = document_stem(kind, job_id)
    if not _outputs_stem_taken(outputs_dir, stem):
        return None
    archive = _next_archive_stem(outputs_dir, stem)
    moved: list[str] = []
    for suffix in _DOC_SUFFIXES:
        src = outputs_dir / f"{stem}{suffix}"
        if src.exists():
            dest = outputs_dir / f"{archive}{suffix}"
            src.rename(dest)
            moved.append(dest.name)
    if moved:
        print(f"  [!] Prior {kind} for '{job_id}' archived as: {', '.join(moved)}")
    return archive


# ── Helpers ───────────────────────────────────────────────────────────────────

def _call(system: str, user: str, model: str, max_tokens: int = 2048) -> str:
    """Single LLM chat completion. Returns the text response."""
    return complete(system, user, model, max_tokens)


def _fetch_url(url: str, *, use_project_web: bool = False) -> str:
    """Fetch a URL via scripts/web.py (shared HTML extraction)."""
    print(f"  Fetching URL: {url}")
    return web.fetch(url, max_chars=12000, use_project_web=use_project_web)


def _education_text() -> str:
    """Serialize education entries from profile.education to a plain-text string.

    Falls back gracefully if the education module is missing or has no parseable
    entries — the rest of the pipeline can still run, just with no education context.
    """
    try:
        import profile.education as edu_mod
        entries = [
            getattr(edu_mod, name)
            for name in dir(edu_mod)
            if name.isupper() and not name.startswith("_")
            and hasattr(getattr(edu_mod, name), "institution")
        ]
        if entries:
            parts = []
            for e in entries:
                degree = getattr(e, "degree", "")
                institution = getattr(e, "institution", "")
                date = getattr(e, "date", "")
                parts.append(f"{degree} — {institution} ({date})" if degree else f"{institution} ({date})")
            return "; ".join(parts)
    except Exception:  # noqa: BLE001
        pass
    return ""


def _education_var_names() -> list[str]:
    """Return profile.education entry variable names for resume codegen."""
    try:
        import profile.education as edu_mod
        return [
            name
            for name in dir(edu_mod)
            if name.isupper() and not name.startswith("_")
            and hasattr(getattr(edu_mod, name), "institution")
        ]
    except Exception:  # noqa: BLE001
        return []


def _profile_text() -> str:
    """Serialize all profile entries to plain text for Claude to reason about."""
    from profile.master_data import EXPERIENCE_REGISTRY, PROJECT_REGISTRY, SUMMARIES
    from profile.header import HEADER

    education_str = _education_text()
    lines = [
        f"CANDIDATE: {HEADER.name}",
    ]
    if education_str:
        lines.append(f"EDUCATION: {education_str}")
    lines += [
        "",
        "=== EXPERIENCE ENTRIES (use variable names exactly as shown) ===",
    ]
    for var, e in EXPERIENCE_REGISTRY.items():
        lines += [
            f"\nVariable: {var}",
            f"Role: {e.role} at {e.company} ({e.date})",
            "Bullets:",
        ]
        for b in e.highlights:
            lines.append(f"  - {strip_latex(b)}")

    lines += ["", "=== PROJECTS (use variable names exactly as shown) ==="]
    for var, p in PROJECT_REGISTRY.items():
        lines += [
            f"\nVariable: {var}",
            f"Title: {p.title}",
            f"Org/Date: {p.organization} | {p.date}",
        ]
        if p.aim:
            lines.append(f"Aim: {p.aim}")
        lines.append("Bullets:")
        for b in p.highlights:
            lines.append(f"  - {strip_latex(b)}")

    lines += ["", "=== SUMMARY PRESETS ==="]
    for key, val in SUMMARIES.items():
        lines.append(f"  {key}: {strip_latex(val)[:120]}...")

    return "\n".join(lines)


# ── Phase 1 — Parse JD ────────────────────────────────────────────────────────

def parse_jd(jd_text: str, model: str) -> dict:
    print("  Phase 1: Parsing JD...")
    system = "You are a job description parser. Return only valid JSON, no markdown."
    user = f"""Analyze this job description and extract structured data.

JD:
{jd_text[:8000]}

Return a JSON object with exactly these fields:
{{
  "company": "Company name",
  "role": "Job title as written",
  "job_id_ext": "req/job ID if shown, else null",
  "location": "City, State or Remote",
  "is_remote": true/false,
  "visa_sponsored": true/false/null,
  "seniority": "entry/mid/senior/staff/principal",
  "hard_requirements": ["skill or requirement 1", ...],
  "nice_to_have": ["skill 1", ...],
  "key_responsibilities": ["responsibility 1", ...],
  "keywords": ["top 15 most important technical keywords from the JD"],
  "culture_signals": ["values/culture mentions"],
  "dept": "team or department name if mentioned, else Engineering"
}}"""
    return call_json(system, user, model, required_keys=["company", "role", "keywords"])


# ── Phase 2 — Profile Matching ────────────────────────────────────────────────

def match_profile(jd: dict, model: str) -> dict:
    print("  Phase 2: Matching profile to JD...")
    profile = _profile_text()
    kw_str  = ", ".join(jd.get("keywords", []))
    resp_str = "\n".join(f"- {r}" for r in jd.get("key_responsibilities", []))

    system = textwrap.dedent("""\
        You are a senior resume writer. Your task:
        1. Select the best-matching experience and project entries from the profile.
        2. Rewrite their bullet points to directly address the JD keywords and responsibilities.
        3. FACTUAL FIDELITY (hard rules — never violate):
           - Only use facts, tools, technologies, and metrics that already appear in that
             entry's source bullets (or other profile text provided for that entry).
           - You may rephrase, reorder, bold JD keywords, tighten wording, and drop weak
             bullets. You may NOT invent percentages, speedups, scale, titles, employers,
             or technologies that are not in the source.
           - If a JD keyword is not evidenced in the profile, omit it or connect adjacent
             real experience — never fabricate coverage.
        4. Every rewritten bullet must use LaTeX formatting rules:
           - Escape % as \\%   (e.g. "40\\% reduction")
           - Escape & as \\&   (e.g. "Weights \\& Biases")
           - Bold key terms:   \\textbf{keyword}
           - Multiplication:   2.3\\texttimes{} speedup
           - Keep each bullet under 200 characters
           - Use past tense, action verbs
        5. Return ONLY valid JSON, no markdown fences.""")

    user = f"""JD KEYWORDS: {kw_str}

KEY RESPONSIBILITIES:
{resp_str}

CANDIDATE PROFILE:
{profile}

Return a JSON object:
{{
  "selected_experience": ["VAR_NAME1", "VAR_NAME2"],
  "experience_overrides": {{
    "VAR_NAME1": [
      "Rewritten LaTeX bullet 1.",
      "Rewritten LaTeX bullet 2.",
      "Rewritten LaTeX bullet 3."
    ]
  }},
  "selected_projects": ["PROJ_VAR1", "PROJ_VAR2", "PROJ_VAR3"],
  "skills_preset": "SKILLS_ML_FOCUSED",
  "summary": "2-3 sentence LaTeX-safe summary tailored to this specific role and company.",
  "section_config": {{
    "show_summary": true,
    "show_research": false,
    "show_coursework": false,
    "show_position_applied": true
  }}
}}

Rules:
- Select 2-3 experience entries and 2-4 project entries most relevant to the JD.
- Provide override bullets for ALL selected experience entries.
- For every override bullet under a VAR_NAME: the claim must be traceable to a source
  bullet (or listed fact) for that same VAR_NAME in the profile above. No new metrics.
- skills_preset must be one of: SKILLS_FULL, SKILLS_ML_FOCUSED, SKILLS_SWE_FOCUSED, SKILLS_RESEARCH_FOCUSED
- The size of the resume post-compilation should be strictly 1 page PDF.
- The summary must mention the company by name and must not invent credentials. """
    return call_json(system, user, model, max_tokens=3000,
                      required_keys=["selected_experience", "selected_projects",
                                     "skills_preset", "summary"])


# ── Phase 3 — Cover Letter ────────────────────────────────────────────────────

def write_cover_letter(jd: dict, match: dict, model: str) -> dict:
    print("  Phase 3: Writing cover letter...")
    kw_str = ", ".join(jd.get("keywords", [])[:10])
    profile = _profile_text()
    selected_exp = ", ".join(match.get("selected_experience") or []) or "(none)"
    selected_proj = ", ".join(match.get("selected_projects") or []) or "(none)"
    system = textwrap.dedent("""\
        You are an expert cover letter writer. Return only valid JSON, no markdown.
        All paragraph text must be LaTeX-safe: escape % as \\%, & as \\&, $ as \\$, _ as \\_.
        FACTUAL FIDELITY (hard rules):
        - Ground every claim in the candidate profile provided. Prefer the selected
          experience/project entries when choosing evidence, but you may cite other
          profile facts if they fit the JD better.
        - Do NOT invent metrics, tools, titles, or achievements absent from the profile.
        - Work from the full profile down to the strongest JD-aligned points — do not
          rely only on the short summary.""")
    user = f"""Write 3 cover letter paragraphs.

Company: {jd['company']}
Role: {jd['role']}
Top JD keywords: {kw_str}
Selected experience vars (resume focus): {selected_exp}
Selected project vars (resume focus): {selected_proj}
Candidate summary (from resume match — optional hint only): {match.get('summary', '')}

FULL CANDIDATE PROFILE (source of truth — tailor down from this):
{profile}

Paragraph guidelines:
- Para 1 (≤4 sentences): Opening hook — why THIS company and THIS role specifically.
  Reference something concrete about the company (product, mission, research area, recent news).
  Do NOT start with "I am writing to apply".
- Para 2 (≤4 sentences): Two strongest achievements with metrics drawn from the profile.
  Connect explicitly to JD keywords. Use LaTeX formatting (\\textbf{{}} for emphasis).
- Para 3 (≤2 sentences): Forward-looking confidence + call to action.
- The size of the coverletter post-compilation should be strictly 1 page PDF.

Return JSON:
{{
  "paragraphs": ["para1 text...", "para2 text...", "para3 text..."]
}}"""
    return call_json(system, user, model, max_tokens=1500, required_keys=["paragraphs"])


# ── Phase 4 — Outreach Messages ───────────────────────────────────────────────

def write_outreach(jd: dict, match: dict, model: str) -> dict:
    print("  Phase 4: Generating outreach messages...")
    from profile.header import HEADER
    education_str = _education_text()
    background_str = education_str if education_str else "See profile"
    kw_str = ", ".join(jd.get("keywords", [])[:12])
    hard = "; ".join(jd.get("hard_requirements", [])[:6])
    summary = (match.get("summary") or "").strip()
    system = (
        "You are a professional networking coach. Return only valid JSON, no markdown. "
        "Keep claims consistent with the relevance summary and JD — do not invent "
        "credentials or metrics beyond what is provided."
    )
    user = f"""Write personalized networking messages for this job application.

Applicant: {HEADER.name}
Background: {background_str}
Applying to: {jd['role']} at {jd['company']}

JD keywords: {kw_str or "(none)"}
JD hard requirements (short): {hard or "(none)"}
How the candidate fits this JD (use this for relevance — do not invent beyond it):
{summary or "(no summary — keep fit claims high-level and honest)"}

Write these messages:
1. LinkedIn connection request: ≤300 chars. Specific, not generic. Mention shared context if possible.
2. Follow-up message (after connecting): 150-200 words. Thank for connecting + one specific ask.
3. Cold email: Subject line (punchy, ≤60 chars) + body (200-250 words, professional).
4. Referral ask: 100-150 words. Assumes at least one prior exchange.

Also provide 3 LinkedIn search query strings to find relevant contacts at {jd['company']}.
Format queries as strings that work in LinkedIn's search bar.

Return JSON:
{{
  "linkedin_search_queries": [
    "query 1",
    "query 2",
    "query 3"
  ],
  "connection_request": "...",
  "follow_up_message": "...",
  "cold_email_subject": "...",
  "cold_email_body": "...",
  "referral_ask": "..."
}}"""
    return call_json(system, user, model, max_tokens=2000,
                      required_keys=["connection_request", "follow_up_message"])


# ── File Generators ───────────────────────────────────────────────────────────

def _py_list(items: list[str], indent: int = 8) -> str:
    """Render a Python list literal with proper indentation."""
    pad = " " * indent
    inner_pad = " " * (indent + 4)
    lines = ["["]
    for item in items:
        escaped = item.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'{inner_pad}"{escaped}",')
    lines.append(f"{pad}]")
    return "\n".join(lines)


def generate_resume_file(job_id: str, jd: dict, match: dict) -> str:
    """Render the resume tailoring .py file as a string."""
    from profile.master_data import EXPERIENCE_REGISTRY, PROJECT_REGISTRY

    company = jd["company"]
    role    = jd["role"]
    company_repr = repr(company)
    role_repr    = repr(role)

    # Resolve paths through data_path so the private overlay is respected.
    # These are computed once here and embedded as literals in the generated file —
    # the generated file itself never needs to import data_paths.
    _resume_source = _rel(document_py("resume", job_id))
    _resume_output = _rel(document_tex("resume", job_id))

    # Build EXPERIENCE block
    exp_lines = []
    for var in match["selected_experience"]:
        if var not in EXPERIENCE_REGISTRY:
            print(f"    [warn] Unknown experience var '{var}', skipping")
            continue
        override = match.get("experience_overrides", {}).get(var)
        if override:
            bullets = _py_list(override, indent=8)
            exp_lines.append(f"    replace({var}, highlights={bullets}),")
        else:
            exp_lines.append(f"    {var},")
    exp_block = "\n".join(exp_lines) if exp_lines else "    # no experience entries selected"

    # Build PROJECTS block
    proj_lines = []
    for var in match["selected_projects"]:
        if var not in PROJECT_REGISTRY:
            print(f"    [warn] Unknown project var '{var}', skipping")
            continue
        proj_lines.append(f"    {var},")
    proj_block = "\n".join(proj_lines) if proj_lines else "    # no project entries selected"

    skills_preset = match.get("skills_preset", "SKILLS_ML_FOCUSED")
    cfg = match.get("section_config", {})
    show_summary = repr(bool(cfg.get("show_summary", True)))
    show_research = repr(bool(cfg.get("show_research", False)))
    show_coursework = repr(bool(cfg.get("show_coursework", False)))
    show_pos = repr(bool(cfg.get("show_position_applied", True)))

    summary_escaped = match["summary"].replace("\\", "\\\\").replace('"', '\\"')

    edu_vars = _education_var_names()
    education_line = f"education   = [{', '.join(edu_vars)}]," if edu_vars else (
        "education   = [],  # no EducationEntry vars found in profile.education"
    )

    return f'''\
"""
{_resume_source}
Auto-generated by scripts/ai_tailor.py on {datetime.date.today()}
Review, adjust, then build: uv run scripts/build.py --id {job_id}
"""

from dataclasses import replace
from resume.cv_utils import SectionConfig, PositionInfo, CV
# Wildcard import keeps generated files in sync with profile/master_data.py __all__
# (every experience/project/research var, skills preset, HEADER, SUMMARIES, etc.).
from profile.master_data import *

JOB_ID      = "{job_id}"
COMPANY     = {company_repr}
ROLE        = {role_repr}
OUTPUT_FILE = "{_resume_output}"

CONFIG = SectionConfig(
    show_position_applied = {show_pos},
    show_summary          = {show_summary},
    show_skills           = True,
    show_experience       = True,
    show_projects         = True,
    show_research         = {show_research},
    show_education        = True,
    show_coursework       = {show_coursework},
)

EXPERIENCE = [
{exp_block}
]

PROJECTS = [
{proj_block}
]

SUMMARY = "{summary_escaped}"

cv_data = CV(
    config      = CONFIG,
    header      = HEADER,
    position    = PositionInfo(role=ROLE),
    summary     = SUMMARY,
    {education_line}
    skills      = {skills_preset},
    experience  = EXPERIENCE,
    projects    = PROJECTS,
    research    = [],
    coursework  = [],
    output_file = OUTPUT_FILE,
)

if __name__ == "__main__":
    import resume.cv2latex as engine
    engine.generate_tex_file(__file__, OUTPUT_FILE)
'''


def generate_cl_file(job_id: str, jd: dict, cl: dict) -> str:
    """Render the cover letter tailoring .py file as a string."""
    company    = jd["company"]
    role       = jd["role"]
    dept       = jd.get("dept", "Engineering")
    city       = jd.get("location", "")
    company_repr = repr(company)
    role_repr    = repr(role)
    dept_repr    = repr(dept)
    city_repr    = repr(city)
    posting_id = jd.get("job_id_ext")
    posting_id_str = f'"{posting_id}"' if posting_id else "None"

    # Resolve paths through data_path so the private overlay is respected.
    _cl_source = _rel(document_py("coverletter", job_id))
    _cl_output = _rel(document_tex("coverletter", job_id))

    paragraphs = cl.get("paragraphs", [])
    para_lines = []
    for p in paragraphs:
        escaped = p.replace("\\", "\\\\").replace('"', '\\"')
        para_lines.append(f'        ("{escaped}"),')
    paras_block = "\n".join(para_lines)

    return f'''\
"""
{_cl_source}
Auto-generated by scripts/ai_tailor.py on {datetime.date.today()}
"""

import datetime
from coverletter.cl_utils import CoverLetter, RecipientInfo, JobInfo, LetterContent
from profile.header import CL_HEADER

JOB_ID      = "{job_id}"
COMPANY     = {company_repr}
ROLE        = {role_repr}
OUTPUT_FILE = "{_cl_output}"

cl_data = CoverLetter(
    header    = CL_HEADER,
    recipient = RecipientInfo(
        company_name       = {company_repr},
        department_or_area = {dept_repr},
        city_state_zip     = {city_repr},
    ),
    job     = JobInfo(title=ROLE, job_id={posting_id_str}),
    content = LetterContent(
        date_str   = datetime.date.today().strftime("%B %d, %Y"),
        salutation = "Dear Hiring Manager,",
        paragraphs = [
{paras_block}
        ],
        closing = "Sincerely,",
    ),
    output_file = OUTPUT_FILE,
)

if __name__ == "__main__":
    import coverletter.cl2latex as engine
    engine.generate_tex_file(__file__, OUTPUT_FILE)
'''


def _alumni_networks() -> list[str]:
    """Alumni networks from config (``networking.alumni_networks``), overlay-aware."""
    try:
        import yaml
        from scripts.data_paths import resolve_path
        cfg_path = resolve_path("config", "job_search_config.yaml")
        if cfg_path.exists():
            cfg = yaml.safe_load(cfg_path.read_text()) or {}
            return cfg.get("networking", {}).get("alumni_networks", []) or []
    except Exception:  # noqa: BLE001
        pass
    return []


def generate_outreach_file(job_id: str, jd: dict, outreach: dict) -> str:
    """Render the outreach.md file as a string."""
    company = jd["company"]
    role    = jd["role"]
    today   = datetime.date.today().strftime("%B %d, %Y")
    queries = outreach.get("linkedin_search_queries", [])
    query_block = "\n".join(f"  - `{q}`" for q in queries)

    alumni = _alumni_networks()
    targets = []
    if alumni:
        targets.append(f"{' / '.join(alumni)} alumni at {company}  ← highest response rate")
    targets += [
        "ML/AI Engineer on the relevant team",
        "Engineering Manager or Director",
        f"Technical Recruiter at {company}",
    ]
    target_block = "\n".join(f"{i}. {t}" for i, t in enumerate(targets, 1))

    return f"""\
# Outreach — {company}: {role}
Generated: {today}

---

## Priority Actions
- [ ] Find contacts on LinkedIn (search queries below)
- [ ] Send connection request (copy–paste ready below)
- [ ] Follow up 3–7 days after they accept (message below)
- [ ] Send referral ask if they engage (message below)
- [ ] Apply at company website, then log: `uv run scripts/track.py log --id {job_id}`

---

## LinkedIn Search Queries
Paste these into LinkedIn's search bar to find relevant contacts:

{query_block}

**Priority targets** (in order):
{target_block}

---

## ① Connection Request
*Paste directly into LinkedIn (≤300 chars)*

> {outreach.get("connection_request", "")}

---

## ② Follow-up Message
*Send 3–7 days after they accept. Do not ask for referral yet.*

> {outreach.get("follow_up_message", "").replace(chr(10), chr(10) + "> ")}

---

## ③ Cold Email
*Use if no LinkedIn connection or for direct recruiter outreach*

**Subject:** {outreach.get("cold_email_subject", "")}

> {outreach.get("cold_email_body", "").replace(chr(10), chr(10) + "> ")}

---

## ④ Referral Ask
*Only after at least one genuine back-and-forth exchange*

> {outreach.get("referral_ask", "").replace(chr(10), chr(10) + "> ")}

---

## Notes
<!-- Add your notes here as you engage with contacts -->
"""


def _h2_sections(text: str) -> tuple[str, list[tuple[str, str]]]:
    """Split markdown into (preamble, [(heading_title, full_section), ...])."""
    lines = text.splitlines(keepends=True)
    preamble_parts: list[str] = []
    sections: list[tuple[str, str]] = []
    current_heading: str | None = None
    current_parts: list[str] = []

    def flush() -> None:
        nonlocal current_heading, current_parts
        if current_heading is not None:
            sections.append((current_heading, "".join(current_parts).rstrip() + "\n"))
        current_heading = None
        current_parts = []

    for line in lines:
        if line.startswith("## "):
            flush()
            current_heading = line[3:].strip()
            current_parts = [line]
        elif current_heading is None:
            preamble_parts.append(line)
        else:
            current_parts.append(line)
    flush()
    return "".join(preamble_parts), sections


def _notes_has_user_content(section: str) -> bool:
    """True if a Notes section has more than the empty template comment."""
    body = section.split("\n", 1)[1] if "\n" in section else ""
    stripped = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL).strip()
    return bool(stripped)


def merge_networking_markdown(existing: str, new: str) -> str:
    """Replace same outreach sections; append sections that are new (Contacts, drafts, …).

    - Headings present in *new* → use the new wording (rephrase replace), except Notes
      when the existing Notes section has user content (keep the user's notes).
    - Headings only in *existing* (e.g. Contacts, Follow-up drafts) → append.
    """
    new_pre, new_secs = _h2_sections(new)
    _, old_secs = _h2_sections(existing)
    new_titles = {title for title, _ in new_secs}
    old_by_title = {title: body for title, body in old_secs}

    chunks: list[str] = []
    if new_pre.strip():
        chunks.append(new_pre.rstrip())

    for title, body in new_secs:
        if title == "Notes" and _notes_has_user_content(old_by_title.get("Notes", "")):
            chunks.append(old_by_title["Notes"].rstrip())
        else:
            chunks.append(body.rstrip())

    for title, body in old_secs:
        if title in new_titles:
            continue
        chunks.append(body.rstrip())

    return "\n\n".join(chunks) + "\n"


def write_networking_md(path: Path, new_content: str) -> None:
    """Write outreach networking.md; merge with existing Contacts / follow-up drafts."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        if existing.strip():
            new_content = merge_networking_markdown(existing, new_content)
    path.write_text(new_content, encoding="utf-8")


def generate_job_info_file(job_id: str, jd: dict, url: str | None = None) -> str:
    keywords = "\n".join(f'    {repr(k)},' for k in jd.get("keywords", []))
    _job_info_path = _rel(data_path("applications", "jobs", job_id, "job_info.py"))
    url_val = url or ""
    return f'''\
"""
{_job_info_path}
Auto-generated by scripts/ai_tailor.py on {datetime.date.today()}
"""

JOB_ID   = {repr(job_id)}
COMPANY  = {repr(jd["company"])}
ROLE     = {repr(jd["role"])}

PLATFORM    = ""
URL         = {repr(url_val)}
JOB_ID_EXT  = {repr(jd.get("job_id_ext"))}
REFERRAL    = None
RECRUITER   = None

LOCATION       = {repr(jd.get("location", ""))}
VISA_SPONSORED = {repr(jd.get("visa_sponsored"))}
SALARY_RANGE   = ""
TEAM           = {repr(jd.get("dept", ""))}

NOTES = "Auto-tailored by ai_tailor.py"

KEYWORDS = [
{keywords}
]

NETWORKING_TARGETS = []
INTERVIEW_FORMAT   = ""
PREP_RESOURCES     = []
'''


# ── Main Orchestrator ─────────────────────────────────────────────────────────

def tailor(job_id: str, jd_text: str, model: str, dry_run: bool = False,
           url: str | None = None) -> dict:
    """Run the full 4-phase pipeline. Returns the combined results dict."""
    print(f"\n{'='*60}")
    print(f"  Tailoring: {job_id}")
    print(f"  Provider:  {resolve_provider()}")
    print(f"  Model:     {model}")
    print(f"{'='*60}")

    jd      = parse_jd(jd_text, model)
    match   = match_profile(jd, model)
    cl      = write_cover_letter(jd, match, model)
    outreach = write_outreach(jd, match, model)

    print(f"\n  Results:")
    print(f"    Company : {jd['company']}")
    print(f"    Role    : {jd['role']}")
    print(f"    Exp     : {match['selected_experience']}")
    print(f"    Projects: {match['selected_projects']}")
    print(f"    Skills  : {match['skills_preset']}")

    if dry_run:
        print("\n[dry-run] No files written.")
        return {"jd": jd, "match": match, "cl": cl, "outreach": outreach}

    # ── Write files ───────────────────────────────────────────────────────────
    # Version prior resume/CL sources; overwrite unique bundle files (job_info/jd/networking).
    archive_existing_outputs("resume", job_id)
    archive_existing_outputs("coverletter", job_id)

    resume_path = document_py("resume", job_id)
    cl_path = document_py("coverletter", job_id)
    job_dir = data_path("applications", "jobs", job_id)
    job_dir.mkdir(parents=True, exist_ok=True)
    resume_path.parent.mkdir(parents=True, exist_ok=True)
    cl_path.parent.mkdir(parents=True, exist_ok=True)

    resume_path.write_text(generate_resume_file(job_id, jd, match), encoding="utf-8")
    cl_path.write_text(generate_cl_file(job_id, jd, cl), encoding="utf-8")
    (job_dir / "job_info.py").write_text(
        generate_job_info_file(job_id, jd, url=url), encoding="utf-8")
    write_networking_md(
        job_dir / "networking.md",
        generate_outreach_file(job_id, jd, outreach),
    )
    (job_dir / "jd.txt").write_text(jd_text, encoding="utf-8")

    print(f"\n  Files written:")
    for p in [resume_path, cl_path, job_dir / "job_info.py", job_dir / "networking.md"]:
        print(f"    {p.relative_to(ROOT)}")

    return {"jd": jd, "match": match, "cl": cl, "outreach": outreach}


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="AI-powered resume + cover letter tailoring from a job description.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              uv run scripts/ai_tailor.py --url "https://nvidia.com/..." --id nvidia_ml_2026
              uv run scripts/ai_tailor.py --jd jobs/nvidia.txt --id nvidia_ml_2026
              uv run scripts/ai_tailor.py --url "..." --id test --dry-run

              # Cloud harness (Cursor / Hermes + cloud model) — override .env:
              uv run scripts/ai_tailor.py --jd jd.txt --id <id> \\
                  --provider anthropic --model claude-opus-4-7
        """)
    )
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--url",  help="URL of the job posting")
    src.add_argument("--jd",   help="Path to a .txt file containing the JD")
    parser.add_argument("--id",       required=True,
                        help="Application ID, e.g. nvidia_ml_2026")
    parser.add_argument("--provider", default=None,
                        choices=["anthropic", "ollama", "openai"],
                        help="Override the provider for this run only (sets LLM_PROVIDER "
                             "in the current process, ignoring .env). Use when calling "
                             "from a cloud harness whose model differs from .env.")
    parser.add_argument("--model",    default=None,
                        help="Model name override for this run only. If omitted, the "
                             "default for the resolved provider is used.")
    parser.add_argument("--use-agent", action="store_true",
                        help="Use the task-specific model from .env for this run instead of the base model.")
    parser.add_argument(
        "--use-project-web",
        action="store_true",
        help="Opt in to scripts/web.py when fetching --url (ADR 0004). Not needed for --jd.",
    )
    parser.add_argument("--dry-run",  action="store_true",
                        help="Parse and print only; write no files")
    parser.add_argument("--build",    action="store_true",
                        help="Also run build.py after tailoring")
    args = parser.parse_args()

    if not re.fullmatch(r"[A-Za-z0-9_]+", args.id):
        print("[x] --id must contain only letters, digits, and underscores")
        sys.exit(1)

    # If --provider was supplied, override LLM_PROVIDER in the current process.
    # load_env() uses os.environ.setdefault() so it won't clobber a value we
    # set here — but load_env() was already called at import time, so we use
    # direct assignment to win over whatever .env wrote into the environment.
    if args.provider:
        os.environ["LLM_PROVIDER"] = args.provider

    # Resolve model *after* the provider override is in place so that
    # get_default_model() returns the correct default for the chosen provider.
    model = args.model or get_default_model(task="tailor", use_task_model=args.use_agent)

    # ── Get JD text ───────────────────────────────────────────────────────────
    if args.url:
        if not args.use_project_web:
            print(
                "[x] --url fetch uses scripts/web.py. Pass --use-project-web, "
                "or save the JD and use --jd (ADR 0004)."
            )
            sys.exit(1)
        jd_text = _fetch_url(args.url, use_project_web=True)
    else:
        path = Path(args.jd)
        if not path.exists():
            print(f"[x] JD file not found: {path}")
            sys.exit(1)
        jd_text = path.read_text(encoding="utf-8")

    results = tailor(args.id, jd_text, model, dry_run=args.dry_run, url=args.url)

    if args.build and not args.dry_run:
        print("\n  Building documents...")
        import scripts.build as build_mod
        rp = build_mod.build_resume(args.id)
        cp = build_mod.build_coverletter(args.id)
        if rp:
            build_mod.compile_pdf(rp)
        if cp:
            build_mod.compile_pdf(cp)

    # Compute display paths via data_path so they reflect the private overlay when active.
    _resume_disp = _rel(document_py("resume", args.id))
    _cl_disp = _rel(document_py("coverletter", args.id))
    _net_disp = _rel(data_path("applications", "jobs", args.id, "networking.md"))

    print(f"""
{'='*60}
  ✓ Done! Next steps:

  1. Review generated files:
       {_resume_disp}
       {_cl_disp}
       {_net_disp}

  2. Build PDFs:
       uv run scripts/build.py --id {args.id} --pdf

  3. Apply, then log:
       uv run scripts/track.py log --id {args.id} --platform <p> --url <url>

  4. Find contacts + copy outreach messages from:
       {_net_disp}
{'='*60}""")


if __name__ == "__main__":
    main()