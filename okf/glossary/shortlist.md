---
type: Glossary Term
title: Shortlist
description: Ranked discovery results shown in chat and appended to applications/shortlists.md.
tags: [glossary, discovery, shortlist]
timestamp: 2026-08-09T00:00:00Z
---

The ranked set of open postings from a discovery run (company, role, URL, why / score).

# Agent path

[discover-jobs](/skills/discover-jobs/SKILL.md) presents the shortlist in chat and **appends**
a session block to `applications/shortlists.md` (overlay-aware; create if absent). Sessions
are separated by `---`; prior blocks are never edited. Handoff to
[new-application](/skills/new-application/SKILL.md) only for accepted jobs — discovery itself
does not write per-job bundles.

# Scripted path

`pipeline.py --dry-run` (or `autonomy_level: discover_only`) prints a shortlist and does
**not** write application files. Higher levels tailor and log `Saved` instead of using
`shortlists.md`.

# Related

- [Discovery workflow](/okf/workflows/discovery.md)
- [Platform playbook](/okf/glossary/platform-playbook.md)
