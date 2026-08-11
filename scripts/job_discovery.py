#!/usr/bin/env -S uv run
"""
scripts/job_discovery.py
------------------------
Job discovery library: find open positions matching your profile.

Search/fetch go through ``scripts/web.py`` when ``use_project_web=True``
(ADR 0004). Backend is ``WEB_BACKEND`` in ``.env`` (searxng / tavily / brave /
serper / harness). Agents with harness-native web should search themselves and
call ``ai_tailor`` per job — do not use this module's web path then.

There is **no CLI** here. Scripted discovery runs via ``pipeline.py``:

    uv run scripts/pipeline.py --level tailor --max 5 --use-project-web
    uv run scripts/pipeline.py --dry-run --max 5 --use-project-web

Exports used by pipeline: ``discover_jobs``, ``fetch_jd``, ``_make_id``.

Requirements:
    Configure LLM in .env for ranking.
    For web I/O: ``use_project_web=True`` plus ``WEB_BACKEND`` (+ keys / SearXNG /
    ``HARNESS_WEB_*_CMD`` when backend is harness).
"""

import datetime
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import yaml

from scripts.data_paths import apply_private_overlay, data_path, resolve_path
from scripts.json_llm import call_json
from scripts.llm_provider import (
    load_env,
    resolve_provider,
)
from scripts import web

load_env()
apply_private_overlay()


def _load_config() -> dict:
    cfg_path = resolve_path("config", "job_search_config.yaml")
    if cfg_path.exists():
        return yaml.safe_load(cfg_path.read_text())
    return {}


def _profile_summary() -> str:
    """One-paragraph profile summary for the ranking prompt."""
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


# ── Build search queries from config ──────────────────────────────────────────

_MAX_ROLE_QUERIES = 8
_MAX_COMPANY_QUERIES = 6


def _build_queries(cfg: dict, query: str | None) -> list[str]:
    """Build web search queries from config (or a single --query override).

    Mixes primary roles with ``search_terms.must_include_one_of`` so results are
    closer to the campaign prefs; ranking still decides final shortlist.
    """
    if query:
        return [query]
    year = datetime.date.today().year
    roles = cfg.get("target_roles", {}).get("primary", ["ML Engineer", "AI Engineer"])
    companies = (
        cfg.get("target_companies", {}).get("tier_1", [])
        + cfg.get("target_companies", {}).get("tier_2", [])
    )
    locations = cfg.get("profile", {}).get("preferred_locations", ["Remote"])
    loc = locations[0] if locations else "Remote"
    must = [
        t for t in cfg.get("search_terms", {}).get("must_include_one_of", [])
        if isinstance(t, str) and t.strip()
    ]
    terms = must[:4] or [""]  # at least one pass without a keyword

    queries: list[str] = []
    # Rotate role × must_include term until we hit the role-query cap.
    for i, role in enumerate(roles[:3]):
        term = terms[i % len(terms)]
        if term:
            queries.append(f"{role} {term} jobs {loc} {year}")
        else:
            queries.append(f"{role} jobs {loc} {year}")
        if len(queries) >= _MAX_ROLE_QUERIES:
            break
    # Extra role queries for remaining must terms (same first role).
    if roles and must and len(queries) < _MAX_ROLE_QUERIES:
        primary = roles[0]
        for term in must[len(roles[:3]):]:
            queries.append(f"{primary} {term} jobs {loc} {year}")
            if len(queries) >= _MAX_ROLE_QUERIES:
                break

    primary_role = roles[0] if roles else "ML Engineer"
    anchor_term = must[0] if must else ""
    for company in companies[:_MAX_COMPANY_QUERIES]:
        if not company:
            continue
        if anchor_term:
            queries.append(f"{company} {primary_role} {anchor_term}")
        else:
            queries.append(f"{company} careers {primary_role}")
    return queries


def _search_prefs_block(cfg: dict) -> str:
    """Format campaign prefs for the ranking prompt (LLM decides; no hard filter)."""
    roles_cfg = cfg.get("target_roles", {}) or {}
    terms = cfg.get("search_terms", {}) or {}
    primary = roles_cfg.get("primary") or []
    secondary = roles_cfg.get("secondary") or []
    avoid = roles_cfg.get("avoid") or []
    must = terms.get("must_include_one_of") or []
    nice = terms.get("nice_to_have") or []
    exclude = terms.get("exclude") or []

    def _join(xs: list) -> str:
        return ", ".join(str(x) for x in xs if x) or "(none)"

    return (
        "SEARCH PREFERENCES (from job_search_config.yaml):\n"
        f"- Prefer roles: {_join(primary)}\n"
        f"- Also consider: {_join(secondary)}\n"
        f"- Avoid roles: {_join(avoid)}\n"
        f"- Must include at least one of: {_join(must)}\n"
        f"- Nice to have: {_join(nice)}\n"
        f"- Exclude / downrank: {_join(exclude)}\n"
        "Prefer postings that look like real open jobs matching these prefs. "
        "Downrank articles, list pages, avoid-roles, and exclude phrases — "
        "but you still decide; do not invent URLs."
    )


# ── Phase 1a: gather candidate postings via web search ────────────────────────

def _gather_candidates(queries: list[str], per_query: int = 6) -> list[dict]:
    seen: set[str] = set()
    candidates: list[dict] = []
    for q in queries:
        try:
            results = web.search(q, max_results=per_query, use_project_web=True)
        except Exception as e:  # noqa: BLE001 — one bad query shouldn't kill discovery
            print(f"  [warn] search failed for {q!r}: {e}")
            continue
        for r in results:
            url = r.get("url", "")
            if not url or url in seen:
                continue
            seen.add(url)
            candidates.append(r)
    return candidates


# ── Phase 1b: rank/structure candidates with the LLM ──────────────────────────

def _rank_candidates(
    candidates: list[dict],
    max_jobs: int,
    model: str,
    cfg: dict | None = None,
) -> list[dict]:
    if not candidates:
        return []
    cfg = cfg or {}
    profile_str = _profile_summary()
    prefs = _search_prefs_block(cfg)
    listing = "\n".join(
        f"{i}. {c.get('title','')} | {c.get('url','')}\n   {c.get('snippet','')[:200]}"
        for i, c in enumerate(candidates, 1)
    )
    system = (
        "You are a job search assistant. From a list of real search results, select the "
        "postings that best match the candidate and campaign preferences and that look "
        "like actual open job postings (not articles or list pages). "
        "Return ONLY a JSON array, no prose."
    )
    user = f"""CANDIDATE PROFILE:
{profile_str}

{prefs}

SEARCH RESULTS (use ONLY these URLs exactly as given):
{listing}

Return up to {max_jobs} best matches as a JSON array, sorted by relevance (highest first):
[
  {{
    "company": "Company Name",
    "role": "Job title",
    "url": "one of the URLs above, copied exactly",
    "location": "City, State or Remote",
    "relevance_score": 9,
    "relevance_reason": "why it matches",
    "key_match": "top matching skills"
  }}
]
Only include items with relevance_score >= 7. Do not invent URLs."""
    try:
        ranked = call_json(system, user, model, max_tokens=3000)
    except Exception as e:  # noqa: BLE001
        print(f"  [warn] ranking failed: {e}")
        return []
    return ranked if isinstance(ranked, list) else []


# ── Phase 1: Discover jobs ────────────────────────────────────────────────────

def discover_jobs(
    query: str | None,
    max_jobs: int,
    model: str,
    cfg: dict,
    *,
    use_project_web: bool = False,
) -> list[dict]:
    """Find open job postings via scripts/web.py + LLM ranking.

    Requires ``use_project_web=True``. Backend comes from ``WEB_BACKEND``.
    Queries and the rank prompt incorporate ``search_terms`` / role prefs from cfg.
    """
    if not use_project_web:
        raise RuntimeError(
            "Discovery via scripts/web.py requires --use-project-web (ADR 0004). "
            "Use harness-native web from the discover-jobs skill, or pass the flag "
            "for unattended runs. Set WEB_BACKEND for searxng/tavily/brave/serper/harness."
        )
    backend = web.resolve_backend()  # fails fast with a clear message when unset

    print(f"\n{'='*60}")
    print(f"  Job Discovery (max {max_jobs} jobs)")
    print(f"  Provider: {resolve_provider()}  |  Web backend: {backend}")
    print(f"{'='*60}")

    queries = _build_queries(cfg, query)
    print(f"  Running {len(queries)} search queries via web backend ({backend})...")
    candidates = _gather_candidates(queries)
    print(f"  Gathered {len(candidates)} unique candidate URLs; ranking...")
    jobs = _rank_candidates(candidates, max_jobs, model, cfg)

    print(f"\n  Found {len(jobs)} relevant jobs:")
    for i, job in enumerate(jobs, 1):
        score = job.get("relevance_score", "?")
        print(f"  {i:2}. [{score}/10] {job.get('company', '?')} — {job.get('role', '?')}")
        print(f"       {job.get('url', 'no url')[:80]}")
    return jobs


# ── Phase 2: Fetch JD text for each job ──────────────────────────────────────

def fetch_jd(url: str, *, use_project_web: bool = False) -> str | None:
    """Fetch JD text via web.fetch() (WEB_BACKEND; needs use_project_web)."""
    if not use_project_web:
        print(
            f"  [warn] Could not fetch {url}: pass --use-project-web for "
            "scripts/web.py fetch (ADR 0004)."
        )
        return None
    try:
        return web.fetch(url, max_chars=10000, use_project_web=True)
    except Exception as e:  # noqa: BLE001
        print(f"  [warn] Could not fetch {url}: {e}")
        return None


# ── ID generator ─────────────────────────────────────────────────────────────

def _make_id(company: str, role: str) -> str:
    """Generate a clean application ID from company + role.

    Checks resume/outputs/, legacy resume/tailoring/, and applications/jobs/
    for existing IDs so orphaned job dirs don't get reused.
    """
    year = datetime.date.today().year
    co   = re.sub(r"[^a-z0-9]", "_", company.lower())[:12].strip("_")
    ro   = re.sub(r"[^a-z0-9]", "_", role.lower().split(",")[0])[:15].strip("_")
    ro   = re.sub(r"_+", "_", ro)
    base = f"{co}_{ro}_{year}"
    counter = 0
    candidate = base
    existing_sources = {p.stem for p in data_path("resume", "outputs").glob("*.py")}
    existing_legacy = {p.stem for p in data_path("resume", "tailoring").glob("*.py")}
    # Archived tailor versions use "id (n)" — treat base id as taken if any match.
    existing_sources |= {
        p.stem.split(" (")[0] for p in data_path("resume", "outputs").glob("*.py")
        if " (" in p.stem
    }
    jobs_dir = data_path("applications", "jobs")
    existing_jobs = {p.name for p in jobs_dir.iterdir() if p.is_dir()} if jobs_dir.exists() else set()
    existing = existing_sources | existing_legacy | existing_jobs
    while candidate in existing:
        counter += 1
        candidate = f"{base}_{counter}"
    return candidate
