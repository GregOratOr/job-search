#!/usr/bin/env python3
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
  resume/tailoring/{id}.py
  coverletter/tailoring/{id}.py
  applications/jobs/{id}/job_info.py
  applications/jobs/{id}/outreach.md
  applications/jobs/{id}/jd.txt         (saved copy of the JD)

Usage:
    uv run scripts/ai_tailor.py --url "https://nvidia.com/careers/..." --id nvidia_ml_2026
    uv run scripts/ai_tailor.py --jd path/to/jd.txt --id nvidia_ml_2026
    uv run scripts/ai_tailor.py --url "..." --id nvidia_ml_2026 --model claude-haiku-4-5-20251001
    uv run scripts/ai_tailor.py --url "..." --id nvidia_ml_2026 --dry-run   # print only, no files

Requirements:
    Configure LLM in .env — see .env.example (anthropic, ollama, or openai-compatible).
"""

import argparse
import datetime
import json
import re
import sys
import textwrap
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.data_paths import apply_private_overlay, data_path, resolve_path
from scripts.llm_provider import complete, get_default_model, load_env, resolve_provider

apply_private_overlay()
load_env()

DEFAULT_MODEL = get_default_model()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _call(system: str, user: str, model: str, max_tokens: int = 2048) -> str:
    """Single LLM chat completion. Returns the text response."""
    return complete(system, user, model, max_tokens)


def _parse_json(raw: str) -> dict | list:
    """Strip markdown fences then parse JSON. Raises on failure."""
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.MULTILINE)
    return json.loads(cleaned)


def _fetch_url(url: str) -> str:
    """Fetch a URL and return the text body (plain text stripped of most HTML)."""
    print(f"  Fetching URL: {url}")
    resp = httpx.get(url, follow_redirects=True, timeout=20,
                     headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    # Crude HTML→text: strip tags, collapse whitespace
    text = re.sub(r"<[^>]+>", " ", resp.text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text[:12000]   # cap at ~12k chars to stay within context budget


def _profile_text() -> str:
    """Serialize all profile entries to plain text for Claude to reason about."""
    from profile.master_data import EXPERIENCE_REGISTRY, PROJECT_REGISTRY, SUMMARIES
    from profile.header import HEADER

    lines = [
        f"CANDIDATE: {HEADER.name}",
        f"EDUCATION: M.S. Artificial Intelligence, Oregon State University (2023-2025); "
        f"B.Tech Computer Engineering, VIT Pune (2017-2021)",
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
            # Strip LaTeX commands for readability
            plain = re.sub(r"\\textbf\{([^}]+)\}", r"\1", b)
            plain = re.sub(r"\\[a-zA-Z]+\{?", "", plain).replace("}", "")
            lines.append(f"  - {plain.strip()}")

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
            plain = re.sub(r"\\textbf\{([^}]+)\}", r"\1", b)
            plain = re.sub(r"\\[a-zA-Z]+\{?", "", plain).replace("}", "")
            lines.append(f"  - {plain.strip()}")

    lines += ["", "=== SUMMARY PRESETS ==="]
    for key, val in SUMMARIES.items():
        plain = re.sub(r"\\textbf\{([^}]+)\}", r"\1", val)
        plain = re.sub(r"\\[a-zA-Z]+", "", plain)
        lines.append(f"  {key}: {plain[:120]}...")

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
    raw = _call(system, user, model)
    return _parse_json(raw)


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
        3. Every rewritten bullet must use LaTeX formatting rules:
           - Escape % as \\%   (e.g. "40\\% reduction")
           - Escape & as \\&   (e.g. "Weights \\& Biases")
           - Bold key terms:   \\textbf{keyword}
           - Multiplication:   2.3\\texttimes{} speedup
           - Keep each bullet under 200 characters
           - Use past tense, action verbs
        4. Return ONLY valid JSON, no markdown fences.""")

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
- skills_preset must be one of: SKILLS_FULL, SKILLS_ML_FOCUSED, SKILLS_SWE_FOCUSED, SKILLS_RESEARCH_FOCUSED
- The summary must mention the company by name."""
    raw = _call(system, user, model, max_tokens=3000)
    return _parse_json(raw)


# ── Phase 3 — Cover Letter ────────────────────────────────────────────────────

def write_cover_letter(jd: dict, match: dict, model: str) -> dict:
    print("  Phase 3: Writing cover letter...")
    kw_str = ", ".join(jd.get("keywords", [])[:10])
    system = textwrap.dedent("""\
        You are an expert cover letter writer. Return only valid JSON, no markdown.
        All paragraph text must be LaTeX-safe: escape % as \\%, & as \\&, $ as \\$, _ as \\_.""")
    user = f"""Write 3 cover letter paragraphs.

Company: {jd['company']}
Role: {jd['role']}
Top JD keywords: {kw_str}
Candidate summary: {match['summary']}

Paragraph guidelines:
- Para 1 (3-4 sentences): Opening hook — why THIS company and THIS role specifically.
  Reference something concrete about the company (product, mission, research area, recent news).
  Do NOT start with "I am writing to apply".
- Para 2 (4 sentences): Two strongest achievements with metrics. Connect explicitly to JD keywords.
  Use LaTeX formatting (\\textbf{{}} for emphasis).
- Para 3 (2 sentences): Forward-looking confidence + call to action.

Return JSON:
{{
  "paragraphs": ["para1 text...", "para2 text...", "para3 text..."]
}}"""
    raw = _call(system, user, model, max_tokens=1500)
    return _parse_json(raw)


# ── Phase 4 — Outreach Messages ───────────────────────────────────────────────

def write_outreach(jd: dict, model: str) -> dict:
    print("  Phase 4: Generating outreach messages...")
    from profile.header import HEADER
    system = "You are a professional networking coach. Return only valid JSON, no markdown."
    user = f"""Write personalized networking messages for this job application.

Applicant: {HEADER.name}
Background: M.S. AI, Oregon State University; B.Tech CS, VIT Pune
Applying to: {jd['role']} at {jd['company']}

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
    raw = _call(system, user, model, max_tokens=2000)
    return _parse_json(raw)


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
    show_summary    = str(cfg.get("show_summary",    True)).capitalize()[:1].lower() + str(cfg.get("show_summary",    True))[1:]
    show_research   = str(cfg.get("show_research",   False))
    show_coursework = str(cfg.get("show_coursework", False))
    show_pos        = str(cfg.get("show_position_applied", True))

    summary_escaped = match["summary"].replace("\\", "\\\\").replace('"', '\\"')

    return f'''\
"""
resume/tailoring/{job_id}.py
Auto-generated by scripts/ai_tailor.py on {datetime.date.today()}
Review, adjust, then build: python scripts/build.py --id {job_id}
"""

from dataclasses import replace
from resume.cv_utils import SectionConfig, PositionInfo, CV
# Wildcard import keeps generated files in sync with profile/master_data.py __all__
# (every experience/project/research var, skills preset, HEADER, SUMMARIES, etc.).
from profile.master_data import *

JOB_ID      = "{job_id}"
COMPANY     = "{company}"
ROLE        = "{role}"
OUTPUT_FILE = f"resume/outputs/{job_id}.tex"

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
    education   = [OSU_MS, VIT_BTECH],
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
    posting_id = jd.get("job_id_ext")
    posting_id_str = f'"{posting_id}"' if posting_id else "None"

    paragraphs = cl.get("paragraphs", [])
    para_lines = []
    for p in paragraphs:
        escaped = p.replace("\\", "\\\\").replace('"', '\\"')
        para_lines.append(f'        ("{escaped}"),')
    paras_block = "\n".join(para_lines)

    return f'''\
"""
coverletter/tailoring/{job_id}.py
Auto-generated by scripts/ai_tailor.py on {datetime.date.today()}
"""

import datetime
from coverletter.cl_utils import CoverLetter, RecipientInfo, JobInfo, LetterContent
from profile.header import CL_HEADER

JOB_ID      = "{job_id}"
COMPANY     = "{company}"
ROLE        = "{role}"
OUTPUT_FILE = f"coverletter/outputs/{job_id}.tex"

cl_data = CoverLetter(
    header    = CL_HEADER,
    recipient = RecipientInfo(
        company_name       = "{company}",
        department_or_area = "{dept}",
        city_state_zip     = "{city}",
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


def generate_outreach_file(job_id: str, jd: dict, outreach: dict) -> str:
    """Render the outreach.md file as a string."""
    company = jd["company"]
    role    = jd["role"]
    today   = datetime.date.today().strftime("%B %d, %Y")
    queries = outreach.get("linkedin_search_queries", [])
    query_block = "\n".join(f"  - `{q}`" for q in queries)

    return f"""\
# Outreach — {company}: {role}
Generated: {today}

---

## Priority Actions
- [ ] Find contacts on LinkedIn (search queries below)
- [ ] Send connection request (copy–paste ready below)
- [ ] Follow up 3–7 days after they accept (message below)
- [ ] Send referral ask if they engage (message below)
- [ ] Apply at company website, then log: `python scripts/track.py log --id {job_id}`

---

## LinkedIn Search Queries
Paste these into LinkedIn's search bar to find relevant contacts:

{query_block}

**Priority targets** (in order):
1. OSU / VIT alumni at {company}  ← highest response rate
2. ML/AI Engineer on the relevant team
3. Engineering Manager or Director
4. Technical Recruiter at {company}

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


def generate_job_info_file(job_id: str, jd: dict) -> str:
    keywords = "\n".join(f'    "{k}",' for k in jd.get("keywords", []))
    return f'''\
"""
applications/jobs/{job_id}/job_info.py
Auto-generated by scripts/ai_tailor.py on {datetime.date.today()}
"""

JOB_ID   = "{job_id}"
COMPANY  = "{jd["company"]}"
ROLE     = "{jd["role"]}"

PLATFORM    = ""
URL         = ""
JOB_ID_EXT  = {repr(jd.get("job_id_ext"))}
REFERRAL    = None
RECRUITER   = None

LOCATION       = "{jd.get("location", "")}"
VISA_SPONSORED = {repr(jd.get("visa_sponsored"))}
SALARY_RANGE   = ""
TEAM           = "{jd.get("dept", "")}"

NOTES = "Auto-tailored by ai_tailor.py"

KEYWORDS = [
{keywords}
]

NETWORKING_TARGETS = []
INTERVIEW_FORMAT   = ""
PREP_RESOURCES     = []
'''


# ── Main Orchestrator ─────────────────────────────────────────────────────────

def tailor(job_id: str, jd_text: str, model: str, dry_run: bool = False) -> dict:
    """Run the full 4-phase pipeline. Returns the combined results dict."""
    print(f"\n{'='*60}")
    print(f"  Tailoring: {job_id}")
    print(f"  Provider:  {resolve_provider()}")
    print(f"  Model:     {model}")
    print(f"{'='*60}")

    jd      = parse_jd(jd_text, model)
    match   = match_profile(jd, model)
    cl      = write_cover_letter(jd, match, model)
    outreach = write_outreach(jd, model)

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
    resume_path  = data_path("resume", "tailoring", f"{job_id}.py")
    cl_path      = data_path("coverletter", "tailoring", f"{job_id}.py")
    job_dir      = data_path("applications", "jobs", job_id)
    job_dir.mkdir(parents=True, exist_ok=True)

    resume_path.write_text(generate_resume_file(job_id, jd, match), encoding="utf-8")
    cl_path.write_text(generate_cl_file(job_id, jd, cl), encoding="utf-8")
    (job_dir / "job_info.py").write_text(generate_job_info_file(job_id, jd), encoding="utf-8")
    (job_dir / "outreach.md").write_text(generate_outreach_file(job_id, jd, outreach), encoding="utf-8")
    (job_dir / "jd.txt").write_text(jd_text, encoding="utf-8")

    print(f"\n  Files written:")
    for p in [resume_path, cl_path, job_dir / "job_info.py", job_dir / "outreach.md"]:
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
        """)
    )
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--url",  help="URL of the job posting")
    src.add_argument("--jd",   help="Path to a .txt file containing the JD")
    parser.add_argument("--id",      required=True, help="Application ID, e.g. nvidia_ml_2026")
    parser.add_argument("--model",   default=DEFAULT_MODEL,
                        help=f"Model override (default from .env: {DEFAULT_MODEL}, provider: {resolve_provider()})")
    parser.add_argument("--dry-run", action="store_true", help="Parse and print only; write no files")
    parser.add_argument("--build",   action="store_true", help="Also run build.py after tailoring")
    args = parser.parse_args()

    if not re.fullmatch(r"[A-Za-z0-9_]+", args.id):
        print("[x] --id must contain only letters, digits, and underscores")
        sys.exit(1)

    # ── Get JD text ───────────────────────────────────────────────────────────
    if args.url:
        jd_text = _fetch_url(args.url)
    else:
        path = Path(args.jd)
        if not path.exists():
            print(f"[x] JD file not found: {path}")
            sys.exit(1)
        jd_text = path.read_text(encoding="utf-8")

    results = tailor(args.id, jd_text, args.model, dry_run=args.dry_run)

    if args.build and not args.dry_run:
        print("\n  Building documents...")
        import scripts.build as build_mod
        build_mod.build_resume(args.id)
        build_mod.build_coverletter(args.id)

    print(f"""
{'='*60}
  ✓ Done! Next steps:

  1. Review generated files:
       resume/tailoring/{args.id}.py
       coverletter/tailoring/{args.id}.py
       applications/jobs/{args.id}/outreach.md

  2. Build PDFs:
       uv run scripts/build.py --id {args.id} --pdf

  3. Apply, then log:
       uv run scripts/track.py log --id {args.id} --platform <p> --url <url>

  4. Find contacts + copy outreach messages from:
       applications/jobs/{args.id}/outreach.md
{'='*60}""")


if __name__ == "__main__":
    main()
