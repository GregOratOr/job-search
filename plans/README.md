# Phase A + B implementation plans (audit remediation)

Executed 2026-07-09.

| ID | Status | Summary |
|----|--------|---------|
| SA-01 | done | pytest, `import os`, `searxng` config, web_backend validation |
| SA-02 | done | `job_info_io.py`, URL in `tailor()`, removed brittle replace |
| SA-03 | done | Dynamic education vars in `generate_resume_file` |
| SA-04 | done | `--provider` on pipeline + job_discovery |
| SA-05 | done | Harness subprocess adapters + mocked tests (stub CLI removed) |
| SA-06 | done | `ai_tailor` URL fetch via `web.fetch()` |
| SA-07 | done | `track.log_saved()` API; pipeline calls it directly |
| SA-08 | done | `json_llm.py` + `text_utils.py` shared modules |
| SA-09 | done | `find_contacts.append_contacts_for_job()` dedup |
| SA-10 | done | `pipeline.py` primary; `job_discovery` library-only (CLI removed 2026-08) |
| SA-11 | done | `bootstrap.init_script()`; adopted in `track.py` (bundle still uses `bootstrap_paths`) |
| SA-12 | later | Unify startup: `init_script(overlay=…)` after argparse across Tools (see okf bootstrap.md) |
| SA-13 | done | `--use-project-web` gate; `--search-mode` retired (WEB_BACKEND only; Anthropic-native discovery removed) |
| SA-14 | done | Docs/OKF/skills sync to code (2026-08-05); discovery `search_terms` in queries + rank |

Verify: `uv run pytest`
