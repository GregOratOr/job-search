#!/usr/bin/env python3
"""
scripts/job_discovery.py
------------------------
AI-powered job discovery: finds open positions matching your profile,
then runs the full ai_tailor.py pipeline for each one.

For every discovered job you get:
  - Tailored resume (.py tailoring file + built .tex)
  - Tailored cover letter
  - Ready-to-send outreach messages (connection request, follow-up, cold email)
  - Application logged in tracker.csv

Usage:
    uv run scripts/job_discovery.py                      # uses config defaults
    uv run scripts/job_discovery.py --max 5              # limit to 5 jobs
    uv run scripts/job_discovery.py --query "CUDA inference engineer remote"
    uv run scripts/job_discovery.py --max 10 --dry-run   # search only, no files

Requirements:
    Configure LLM in .env — see .env.example (anthropic, ollama, or openai-compatible).
    Live web search in discovery requires LLM_PROVIDER=anthropic.
"""

import argparse
import datetime
import json
import re
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import yaml

from scripts.data_paths import apply_private_overlay, data_path, resolve_path
from scripts.ai_tailor import DEFAULT_MODEL, tailor, _parse_json
from scripts.llm_provider import (
    anthropic_web_search_complete,
    complete,
    load_env,
    resolve_provider,
    supports_web_search,
)

load_env()
apply_private_overlay()


def _load_config() -> dict:
    cfg_path = resolve_path("config", "job_search_config.yaml")
    if cfg_path.exists():
        return yaml.safe_load(cfg_path.read_text())
    return {}


def _profile_summary() -> str:
    """One-paragraph profile summary for the search prompt."""
    from profile.header import HEADER
    from profile.master_data import EXPERIENCE_REGISTRY, PROJECT_REGISTRY, SUMMARIES
    exp_list  = ", ".join(
        f"{e.role} at {e.company}" for e in list(EXPERIENCE_REGISTRY.values())[:3]
    )
    proj_list = ", ".join(list(PROJECT_REGISTRY.keys())[:4])
    return (
        f"Candidate: {HEADER.name}. "
        f"Experience: {exp_list}. "
        f"Projects: {proj_list}. "
        f"Summary: {list(SUMMARIES.values())[0][:200]}"
    )


# ── Phase 1: Discover jobs ────────────────────────────────────────────────────

def discover_jobs(query: str | None, max_jobs: int, model: str, cfg: dict) -> list[dict]:
    """Find open job postings via LLM (web search when provider=anthropic)."""
    print(f"\n{'='*60}")
    print(f"  Job Discovery (max {max_jobs} jobs)")
    print(f"  Provider: {resolve_provider()}")
    print(f"{'='*60}")

    target_roles     = cfg.get("target_roles", {}).get("primary", ["ML Engineer", "AI Engineer"])
    target_companies = (
        cfg.get("target_companies", {}).get("tier_1", []) +
        cfg.get("target_companies", {}).get("tier_2", [])
    )[:12]
    search_must      = cfg.get("search_terms", {}).get("must_include_one_of", ["machine learning"])
    location_prefs   = cfg.get("profile", {}).get("preferred_locations", ["Remote"])

    if query:
        search_directive = f"Search for: {query}"
    else:
        roles_str     = ", ".join(target_roles)
        companies_str = ", ".join(target_companies[:8])
        keywords_str  = ", ".join(search_must[:5])
        locations_str = ", ".join(location_prefs[:3])
        search_directive = (
            f"Search for currently open positions with these roles: {roles_str}. "
            f"Prioritize these companies: {companies_str}. "
            f"Must involve: {keywords_str}. "
            f"Preferred locations: {locations_str}."
        )

    profile_str = _profile_summary()

    system_prompt = textwrap.dedent("""\
        You are a job search assistant. Use web_search to find real, currently open
        job postings. For each job, verify it is open (not expired/filled).
        Return ONLY a JSON array, no markdown fences.""")

    user_prompt = f"""Find {max_jobs} currently open job postings for this candidate.

CANDIDATE PROFILE:
{profile_str}

SEARCH DIRECTIVE:
{search_directive}

For each job found:
1. Search for the actual posting URL
2. Verify it's currently open
3. Score relevance 1-10 against the candidate's profile

Return a JSON array, sorted by relevance (highest first):
[
  {{
    "company": "Company Name",
    "role": "Exact job title",
    "url": "https://direct-link-to-posting",
    "location": "City, State or Remote",
    "relevance_score": 9,
    "relevance_reason": "Strong match because...",
    "key_match": "Top 3 matching skills/requirements"
  }},
  ...
]

Only include jobs where relevance_score >= 7."""

    if supports_web_search():
        print("  Searching for jobs with web search...")
        raw = anthropic_web_search_complete(system_prompt, user_prompt, model, max_tokens=4096)
    else:
        print("  [note] Web search unavailable without LLM_PROVIDER=anthropic.")
        print("         Using local model only — verify URLs manually before applying.")
        fallback_user = user_prompt + textwrap.dedent("""

        IMPORTANT: You cannot browse the web. Return a JSON array of plausible
        currently-open postings you believe match the search directive. Use well-known
        career-page URL patterns where possible. Mark uncertain entries with
        relevance_score 7 only if reasonably confident.""")
        raw = complete(system_prompt, fallback_user, model, max_tokens=4096)

    try:
        jobs = _parse_json(raw)
        if not isinstance(jobs, list):
            jobs = []
    except Exception as e:
        print(f"  [warn] Could not parse job list: {e}")
        print(f"  Raw response: {raw[:500]}")
        jobs = []

    print(f"\n  Found {len(jobs)} relevant jobs:")
    for i, job in enumerate(jobs, 1):
        score = job.get("relevance_score", "?")
        print(f"  {i:2}. [{score}/10] {job.get('company', '?')} — {job.get('role', '?')}")
        print(f"       {job.get('url', 'no url')[:80]}")

    return jobs


# ── Phase 2: Fetch JD text for each job ──────────────────────────────────────

def fetch_jd(url: str) -> str | None:
    """Fetch JD text from URL. Returns None on failure."""
    import httpx
    try:
        resp = httpx.get(url, follow_redirects=True, timeout=20,
                         headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        # Strip HTML tags
        text = re.sub(r"<[^>]+>", " ", resp.text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text[:10000]
    except Exception as e:
        print(f"  [warn] Could not fetch {url}: {e}")
        return None


# ── ID generator ─────────────────────────────────────────────────────────────

def _make_id(company: str, role: str) -> str:
    """Generate a clean application ID from company + role."""
    year = datetime.date.today().year
    co   = re.sub(r"[^a-z0-9]", "_", company.lower())[:12].strip("_")
    ro   = re.sub(r"[^a-z0-9]", "_", role.lower().split(",")[0])[:15].strip("_")
    ro   = re.sub(r"_+", "_", ro)
    base = f"{co}_{ro}_{year}"
    # Avoid collisions
    counter = 0
    candidate = base
    existing = {p.stem for p in data_path("resume", "tailoring").glob("*.py")}
    while candidate in existing:
        counter += 1
        candidate = f"{base}_{counter}"
    return candidate


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="AI-powered job discovery + auto-tailoring pipeline.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              uv run scripts/job_discovery.py
              uv run scripts/job_discovery.py --max 5 --dry-run
              uv run scripts/job_discovery.py --query "LLM inference engineer remote 2026"
        """)
    )
    parser.add_argument("--query",   default=None, help="Custom search query (overrides config defaults)")
    parser.add_argument("--max",     type=int, default=5, help="Max jobs to discover and tailor (default: 5)")
    parser.add_argument("--model",   default=DEFAULT_MODEL,
                        help=f"Model override (default from .env: {DEFAULT_MODEL}, provider: {resolve_provider()})")
    parser.add_argument("--dry-run", action="store_true",
                        help="Discover and print jobs only; skip tailoring and file creation")
    parser.add_argument("--build",   action="store_true",
                        help="Also compile .tex → PDF after tailoring each job")
    args = parser.parse_args()

    cfg  = _load_config()
    jobs = discover_jobs(args.query, args.max, args.model, cfg)

    if not jobs:
        print("\n  No jobs found. Try --query with different keywords, or check your config.")
        sys.exit(0)

    if args.dry_run:
        print("\n[dry-run] Stopping after discovery. No tailoring files written.")
        sys.exit(0)

    # ── Tailor each job ───────────────────────────────────────────────────────
    summary_rows = []
    for job in jobs:
        url     = job.get("url", "")
        company = job.get("company", "Unknown")
        role    = job.get("role", "Unknown Role")
        job_id  = _make_id(company, role)

        print(f"\n{'─'*60}")
        print(f"  Processing: {company} — {role}")
        print(f"  ID: {job_id}")

        jd_text = fetch_jd(url) if url else None
        if not jd_text:
            print(f"  [skip] Could not fetch JD text for {url}")
            continue

        try:
            results = tailor(job_id, jd_text, args.model, dry_run=False)
            real_company = results["jd"].get("company", company)
            real_role    = results["jd"].get("role", role)

            # Update URL from job discovery result
            job_info_path = data_path("applications", "jobs", job_id, "job_info.py")
            if job_info_path.exists():
                content = job_info_path.read_text()
                content = content.replace('URL         = ""', f'URL         = "{url}"', 1)
                job_info_path.write_text(content)

            if args.build:
                import scripts.build as build_mod
                build_mod.build_resume(job_id)
                build_mod.build_coverletter(job_id)

            summary_rows.append({"id": job_id, "company": real_company, "role": real_role,
                                  "url": url, "status": "✓ tailored"})
        except Exception as e:
            print(f"  [error] Tailoring failed for {job_id}: {e}")
            summary_rows.append({"id": job_id, "company": company, "role": role,
                                  "url": url, "status": f"✗ {e}"})

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("  DISCOVERY COMPLETE")
    print(f"{'='*60}")
    print(f"\n  {'ID':<35} {'Status':<12} {'Company'}")
    print(f"  {'─'*35} {'─'*12} {'─'*20}")
    for row in summary_rows:
        print(f"  {row['id']:<35} {row['status']:<12} {row['company']}")

    print(f"\n  Next steps for each job:")
    print(f"  1. Review:  resume/tailoring/<id>.py")
    print(f"  2. Review:  applications/jobs/<id>/outreach.md")
    print(f"  3. Build:   uv run scripts/build.py --id <id> --pdf")
    print(f"  4. Apply + log: uv run scripts/track.py log --id <id> --platform <p> --url <url>")


if __name__ == "__main__":
    main()
