---
name: find-contacts
description: Find networking contacts (recruiters, hiring managers, alumni) for a company by emitting ready-to-run search queries and extracting contacts from public pages. Use when the user wants to find who to reach out to at a company or collect contact details for an application.
---

# Find Networking Contacts

Produce, for a company:
- Ready-to-run LinkedIn + Google search queries (run manually).
- Contacts extracted from PUBLIC pages (team/about pages, GitHub, conference sites) —
  names/titles from snippets, emails via regex.
- Optional paid enrichment (**Hunter only**) when `ENRICHMENT_PROVIDER=hunter`,
  `HUNTER_API_KEY`, and `--domain` are set in `.env` / CLI. Off by default.
  Apollo is not implemented.

Alumni labels for query generation come from `networking.alumni_networks` in
`config/job_search_config.yaml` (overlay-aware) — same list used by `ai_tailor` outreach
priority targets.

## Web access — harness-native first

**If your harness has built-in web search and page extraction**, use those tools to search
public team/about/careers pages and extract contact hints. Append a `## Contacts` section to
`applications/jobs/<id>/networking.md`. **Do not run `scripts/web.py` or
`scripts/find_contacts.py`** when native web is available.

## Scripted fallback (`scripts/find_contacts.py`)

When no harness web tools exist, the script uses `scripts/web.py` to search public pages.

## ⛔ No scraping, no sending
Never scrape LinkedIn. This tool only drafts queries and reads public pages; it never sends
messages (see the `networking-outreach` skill for the messages themselves).

## Steps

### Agent-driven (harness has native web)

1. Build LinkedIn/Google search queries (see `networking/message_templates.md`).
2. Use harness web tools to search `{company} team page`, `{company} careers contact`, etc.
3. Extract emails and names from fetched public pages.
4. Append results to `applications/jobs/<id>/networking.md` under `## Contacts`.

### Scripted

1. Queries only (no web scan — safe default):
   `uv run scripts/find_contacts.py --company NVIDIA --role "ML Engineer"`
2. Public-page email extraction (needs `WEB_BACKEND` + `--use-project-web`):
   `uv run scripts/find_contacts.py --company Cohere --id cohere_ml_2026 --use-project-web`
3. Optional Hunter email lookup (needs `ENRICHMENT_PROVIDER=hunter`, `HUNTER_API_KEY`, and `--domain`):
   `uv run scripts/find_contacts.py --company Acme --domain acme.com --id acme_ml_2026`
   (add `--use-project-web` if you also want the public-page scan; Hunter alone doesn't need it)

## Pitfalls

- Public-page scan needs `WEB_BACKEND` and `--use-project-web` — see ADR 0004 / `discover-jobs`.
  Without the flag, the script still emits search queries (and optional Hunter if configured).
- Always verify extracted emails/names before contacting; public pages go stale.
- Failed page fetches are skipped and listed under `### Failed fetches` (refreshed each run).
- Re-running: **same emails** → replace the `## Contacts` block (queries refreshed);
  **new emails** → keep prior contact rows and append only the new ones (no versioned files).
