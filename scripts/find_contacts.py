#!/usr/bin/env -S uv run
"""
scripts/find_contacts.py
------------------------
Find networking contacts (hiring managers, recruiters, alumni) for a company.

Approach (see docs/adr/0003 and the networking-outreach skill):
  - Emit ready-to-run LinkedIn + Google search queries (you run these manually).
  - Extract contacts from PUBLIC pages the web tool can fetch (company team/about
    pages, GitHub org, conference sites) — names/titles in snippets, emails via regex.
  - NO LinkedIn scraping.
  - Optional paid enrichment (Hunter) only when ENRICHMENT_PROVIDER=hunter,
    HUNTER_API_KEY, and --domain are set (off by default; Apollo not implemented).

When the harness has native web search/extraction, agents should use those tools
directly (see skills/find-contacts/SKILL.md) instead of invoking this script.

Results are written into the bundle's networking.md (under a "Contacts" section)
when --id is given, otherwise printed.

Usage:
    uv run scripts/find_contacts.py --company NVIDIA --role "ML Engineer"
    uv run scripts/find_contacts.py --company Cohere --id cohere_ml_2026 --use-project-web
    uv run scripts/find_contacts.py --company Acme --domain acme.com   # Hunter if configured
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import httpx

from scripts.data_paths import apply_private_overlay, data_path
from scripts.llm_provider import load_env
from scripts import web

apply_private_overlay()
load_env()

_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")


# ── Search queries (manual, copy-paste) ───────────────────────────────────────

def build_queries(company: str, role: str | None, alumni: list[str] | None) -> dict[str, list[str]]:
    role_part = f' "{role}"' if role else ""
    queries = {
        "LinkedIn (paste into LinkedIn search)": [
            f'{company} recruiter',
            f'{company}{role_part} hiring manager',
            f'{company} engineering manager',
        ],
        "Google (site-scoped)": [
            f'site:linkedin.com/in "{company}" recruiter',
            f'site:linkedin.com/in "{company}"{role_part}',
            f'"{company}" team OR "about us" engineering',
        ],
    }
    for school in (alumni or []):
        queries["LinkedIn (paste into LinkedIn search)"].append(
            f'{company} "{school}"'
        )
    return queries


# ── Public-page contact extraction ────────────────────────────────────────────

def gather_public_contacts(
    company: str,
    max_pages: int = 5,
    *,
    use_project_web: bool = False,
) -> tuple[list[dict], list[dict]]:
    """Search public pages and extract emails.

    Returns ``(contacts, failures)`` where:
      contacts — ``[{email, source, title}, ...]``
      failures — ``[{title, url, error}, ...]`` for pages that could not be fetched
    """
    if not use_project_web:
        raise RuntimeError(
            "gather_public_contacts requires use_project_web=True / --use-project-web "
            "(ADR 0004). Prefer harness-native web via skills/find-contacts."
        )
    found: list[dict] = []
    failures: list[dict] = []
    seen_emails: set[str] = set()
    queries = [
        f"{company} team page",
        f"{company} engineering team about",
        f"{company} careers contact",
    ]
    pages: list[dict] = []
    seen_urls: set[str] = set()
    for q in queries:
        try:
            for r in web.search(q, max_results=max_pages, use_project_web=True):
                url = r.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    pages.append(r)
        except Exception as e:  # noqa: BLE001
            print(f"  [warn] search failed for {q!r}: {e}")

    for p in pages[: max_pages * 2]:
        url = p.get("url", "")
        title = p.get("title", "")
        if not url:
            continue
        try:
            text = web.fetch(url, max_chars=6000, use_project_web=True)
        except Exception as e:  # noqa: BLE001 — skip unreachable pages
            print(f"  [skip] {url}: {e}")
            failures.append({"title": title, "url": url, "error": str(e)})
            continue
        for email in set(_EMAIL_RE.findall(text)):
            # Filter obvious noise (images, asset hashes)
            if email.lower().endswith((".png", ".jpg", ".svg", ".gif")):
                continue
            if email in seen_emails:
                continue
            seen_emails.add(email)
            found.append({"email": email, "source": url, "title": title})
    return found, failures


# ── Optional paid enrichment ──────────────────────────────────────────────────

def enrich(company: str, domain: str | None) -> list[dict]:
    provider = os.environ.get("ENRICHMENT_PROVIDER", "").strip().lower()
    if not provider:
        return []
    if provider == "hunter":
        return _enrich_hunter(domain)
    print(f"  [warn] ENRICHMENT_PROVIDER={provider!r} not implemented; skipping.")
    return []


def _enrich_hunter(domain: str | None) -> list[dict]:
    key = os.environ.get("HUNTER_API_KEY", "").strip()
    if not key or not domain:
        print("  [enrich] Hunter needs HUNTER_API_KEY and --domain; skipping.")
        return []
    try:
        resp = httpx.get("https://api.hunter.io/v2/domain-search",
                         params={"domain": domain, "api_key": key}, timeout=30)
        resp.raise_for_status()
        data = resp.json().get("data", {})
    except Exception as e:  # noqa: BLE001
        print(f"  [enrich] Hunter lookup failed: {e}")
        return []
    out = []
    for e in data.get("emails", []):
        out.append({
            "email": e.get("value", ""),
            "name": f"{e.get('first_name','')} {e.get('last_name','')}".strip(),
            "title": e.get("position", "") or "",
            "source": "hunter.io",
        })
    return out


# ── Render + write ────────────────────────────────────────────────────────────

_CONTACTS_MARKER = "## Contacts"


def render_markdown(
    company: str,
    role: str | None,
    queries: dict,
    public: list[dict],
    enriched: list[dict],
    failures: list[dict] | None = None,
) -> str:
    lines = [f"## Contacts — {company}" + (f" ({role})" if role else ""), ""]
    lines.append("### Search queries (run these manually)")
    for group, qs in queries.items():
        lines.append(f"**{group}**")
        for q in qs:
            lines.append(f"- `{q}`")
        lines.append("")

    lines.append("### Public contacts found")
    if public:
        for c in public:
            label = c.get("title") or c.get("source")
            lines.append(f"- `{c['email']}` — from [{label}]({c['source']})")
    else:
        lines.append("- _None extracted from public pages. Use the queries above._")
    lines.append("")

    if enriched:
        lines.append("### Enriched contacts (paid API)")
        for c in enriched:
            who = " — ".join(x for x in (c.get("name"), c.get("title")) if x)
            lines.append(f"- `{c['email']}`" + (f" — {who}" if who else "")
                         + f" _(via {c.get('source','')})_")
        lines.append("")

    if failures:
        lines.append("### Failed fetches")
        for f in failures:
            label = f.get("title") or f.get("url")
            err = f.get("error", "fetch failed")
            lines.append(f"- [{label}]({f['url']}) — {err}")
        lines.append("")

    lines.append("> Verify every contact before reaching out. Do not send a referral ask "
                 "in a first message (see networking-outreach skill).")
    return "\n".join(lines) + "\n"


def _emails_in_text(text: str) -> set[str]:
    return {m.group(0).lower() for m in _EMAIL_RE.finditer(text)}


def _split_networking(existing: str) -> tuple[str, str]:
    """Return (before_contacts, contacts_section_including_marker)."""
    if _CONTACTS_MARKER not in existing:
        return existing.rstrip(), ""
    before, _, rest = existing.partition(_CONTACTS_MARKER)
    return before.rstrip(), _CONTACTS_MARKER + rest


def _contact_emails(public: list[dict], enriched: list[dict]) -> set[str]:
    emails: set[str] = set()
    for c in public + enriched:
        email = (c.get("email") or "").strip().lower()
        if email:
            emails.add(email)
    return emails


def _format_public_line(c: dict) -> str:
    label = c.get("title") or c.get("source")
    return f"- `{c['email']}` — from [{label}]({c['source']})"


def _format_enriched_line(c: dict) -> str:
    who = " — ".join(x for x in (c.get("name"), c.get("title")) if x)
    return (
        f"- `{c['email']}`"
        + (f" — {who}" if who else "")
        + f" _(via {c.get('source', '')})_"
    )


def _bullet_lines_with_emails(section: str, under_heading: str) -> list[str]:
    """Return `- …` lines that contain an email under the given ### heading."""
    if under_heading not in section:
        return []
    after = section.split(under_heading, 1)[1]
    # Stop at next ### or verify note
    for stop in ("\n### ", "\n> Verify"):
        if stop in after:
            after = after.split(stop, 1)[0]
    lines: list[str] = []
    for line in after.splitlines():
        stripped = line.strip()
        if stripped.startswith("- ") and _EMAIL_RE.search(stripped):
            lines.append(stripped)
    return lines


def _merge_contacts_section(
    existing_section: str,
    company: str,
    role: str | None,
    queries: dict,
    public: list[dict],
    enriched: list[dict],
    failures: list[dict] | None = None,
) -> str:
    """Keep prior contact rows; refresh queries; append only new emails."""
    prior_emails = _emails_in_text(existing_section)
    prior_public = _bullet_lines_with_emails(existing_section, "### Public contacts found")
    prior_enriched = _bullet_lines_with_emails(
        existing_section, "### Enriched contacts (paid API)",
    )
    # Older heading without "(paid API)"
    if not prior_enriched:
        prior_enriched = _bullet_lines_with_emails(
            existing_section, "### Enriched contacts",
        )

    new_public_lines = [
        _format_public_line(c) for c in public
        if (c.get("email") or "").strip().lower() not in prior_emails
    ]
    new_enriched_lines = [
        _format_enriched_line(c) for c in enriched
        if (c.get("email") or "").strip().lower() not in prior_emails
    ]

    header = f"## Contacts — {company}" + (f" ({role})" if role else "")
    lines = [header, "", "### Search queries (run these manually)"]
    for group, qs in queries.items():
        lines.append(f"**{group}**")
        for q in qs:
            lines.append(f"- `{q}`")
        lines.append("")

    lines.append("### Public contacts found")
    public_lines = prior_public + new_public_lines
    if public_lines:
        lines.extend(public_lines)
    else:
        lines.append("- _None extracted from public pages. Use the queries above._")
    lines.append("")

    enriched_lines = prior_enriched + new_enriched_lines
    if enriched_lines:
        lines.append("### Enriched contacts (paid API)")
        lines.extend(enriched_lines)
        lines.append("")

    if failures:
        lines.append("### Failed fetches")
        for f in failures:
            label = f.get("title") or f.get("url")
            err = f.get("error", "fetch failed")
            lines.append(f"- [{label}]({f['url']}) — {err}")
        lines.append("")

    lines.append(
        "> Verify every contact before reaching out. Do not send a referral ask "
        "in a first message (see networking-outreach skill)."
    )
    return "\n".join(lines) + "\n"


def write_contacts_to_networking(
    job_id: str,
    company: str,
    role: str | None,
    queries: dict,
    public: list[dict],
    enriched: list[dict],
    failures: list[dict] | None = None,
) -> Path:
    """Write ## Contacts into networking.md.

    - No prior section, or this run has no *new* emails → replace the Contacts block.
    - This run found emails not already listed → keep prior rows, append only new ones,
      refresh search queries.
    Failed fetches from this run are always listed (refreshed each run).
    """
    failures = failures or []
    path = data_path("applications", "jobs", job_id, "networking.md")
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    before, prior_section = _split_networking(existing)

    this_emails = _contact_emails(public, enriched)
    prior_emails = _emails_in_text(prior_section) if prior_section else set()
    new_emails = this_emails - prior_emails

    if prior_section and new_emails:
        section = _merge_contacts_section(
            prior_section, company, role, queries, public, enriched, failures,
        )
    else:
        section = render_markdown(company, role, queries, public, enriched, failures)

    text = (before + "\n\n" + section).lstrip() if before.strip() else section
    path.write_text(text, encoding="utf-8")
    return path


def append_contacts_for_job(
    job_id: str,
    company: str,
    role: str | None = None,
    *,
    domain: str | None = None,
    max_pages: int = 5,
    alumni: list[str] | None = None,
    use_project_web: bool = False,
) -> Path:
    """Find contacts and write/merge a ## Contacts section into networking.md.

    Without ``use_project_web``, only search queries (+ optional Hunter enrich)
    are written — no ``scripts/web.py`` public-page scan.
    """
    queries = build_queries(company, role, alumni or [])
    public: list[dict] = []
    failures: list[dict] = []
    if use_project_web:
        public, failures = gather_public_contacts(
            company, max_pages=max_pages, use_project_web=True,
        )
    enriched = enrich(company, domain)
    return write_contacts_to_networking(
        job_id, company, role, queries, public, enriched, failures,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Find networking contacts for a company.")
    parser.add_argument("--company", required=True, help="Company name")
    parser.add_argument("--role", default=None, help="Target role (refines queries)")
    parser.add_argument("--id", default=None, help="Application id; appends to its networking.md")
    parser.add_argument("--domain", default=None, help="Company email domain (for Hunter enrichment)")
    parser.add_argument("--max", type=int, default=5, help="Max public pages to scan")
    parser.add_argument(
        "--use-project-web",
        action="store_true",
        help="Opt in to scripts/web.py for public-page search/fetch (ADR 0004).",
    )
    args = parser.parse_args()

    alumni: list[str] = []
    try:
        import yaml
        from scripts.data_paths import resolve_path
        cfg_path = resolve_path("config", "job_search_config.yaml")
        if cfg_path.exists():
            cfg = yaml.safe_load(cfg_path.read_text()) or {}
            alumni = cfg.get("networking", {}).get("alumni_networks", []) or []
    except Exception:  # noqa: BLE001
        pass

    if args.use_project_web:
        try:
            backend = web.resolve_backend()
        except (RuntimeError, ValueError) as e:
            print(f"[x] {e}")
            sys.exit(1)
        print(f"\n  Finding contacts for {args.company} (web backend: {backend})")
    else:
        print(
            f"\n  Finding contacts for {args.company} "
            "(queries only — pass --use-project-web to scan public pages)"
        )

    if args.id:
        path = append_contacts_for_job(
            args.id, args.company, args.role,
            domain=args.domain, max_pages=args.max, alumni=alumni,
            use_project_web=args.use_project_web,
        )
        print(f"\n[+] Contacts written to {path}")
    else:
        queries = build_queries(args.company, args.role, alumni)
        public: list[dict] = []
        failures: list[dict] = []
        if args.use_project_web:
            public, failures = gather_public_contacts(
                args.company, max_pages=args.max, use_project_web=True,
            )
        enriched = enrich(args.company, args.domain)
        print("\n" + render_markdown(
            args.company, args.role, queries, public, enriched, failures,
        ))


if __name__ == "__main__":
    main()