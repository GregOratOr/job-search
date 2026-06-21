---
name: discover-jobs
description: Find currently open job postings matching the candidate profile using the agent's own web tools, then tailor an application for each. Use when the user wants to discover/search for jobs and prepare applications without relying on a cloud API key.
---

# Discover Jobs (local-agent path)

This is the agent-driven alternative to `scripts/job_discovery.py` (which needs an
Anthropic key + its native web_search). Here the agent does the searching with its own
web tools, so it works with a local model.

## Steps
1. Read search preferences from `config/job_search_config.yaml`
   (`target_roles`, `target_companies`, `search_terms`, `profile.preferred_locations`).
2. Use your web search/fetch tools to find real, currently-open postings; capture each
   posting's company, role, URL, and JD text.
3. For each promising posting, run the `tailor-resume` skill end-to-end
   (scaffold → edit tailoring files → build).
4. Save the raw JD to `applications/jobs/<id>/jd.txt` and log with the
   `track-application` skill (status `Saved`).

## ⛔ Profile is read-only
Discovery and tailoring read `profile/` only; never edit it.

## Pitfalls
- Verify a posting is still open before tailoring; skip dead links.
- Generate collision-free ids (`{company}_{role}_{year}`, append `_2` on conflict).
