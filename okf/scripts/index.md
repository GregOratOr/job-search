# Scripts

Callable CLI tools under `scripts/`. All invoked with `uv run scripts/<name>.py`.

* [pipeline.py](/okf/scripts/pipeline.md) - E2E orchestrator (primary for discovery)
* [job_discovery.py](/okf/scripts/job-discovery.md) - discovery library (`discover_jobs`, `fetch_jd`, `_make_id`); no CLI — use pipeline
* [ai_tailor.py](/okf/scripts/ai-tailor.md) - JD → tailored resume/CL/outreach
* [audit.py](/okf/scripts/audit.md) - pre-submit critique
* [web.py](/okf/scripts/web.md) - project web tool (fallback; requires explicit `WEB_BACKEND`)
* [new_application.py](/okf/scripts/new-application.md) - scaffold resume/coverletter/job_info from templates
* [build.py](/okf/scripts/build.md) - render/compile LaTeX
* [bundle.py](/okf/scripts/bundle.md) - finalize upload folder
* [research.py](/okf/scripts/research.md) - company/topic brief (scripted web)
* [find_contacts.py](/okf/scripts/find-contacts.md) - contact queries + public pages
* [track.py](/okf/scripts/track.md) - application tracker + `log_saved()`
* [followup.py](/okf/scripts/followup.md) - stale-app follow-up drafts
* [validate_profile.py](/okf/scripts/validate-profile.md) - profile validation/inventory (read-only; alias `update_profile.py`)
* [llm_provider.py](/okf/scripts/llm-provider.md) - provider-agnostic LLM access
* [json_llm.py](/okf/scripts/json-llm.md) - shared JSON LLM helpers
* [text_utils.py](/okf/scripts/text-utils.md) - LaTeX strip helpers
* [bootstrap.py](/okf/scripts/bootstrap.md) - script init boilerplate
* [data_paths.py](/okf/scripts/data-paths.md) - private overlay + `{id}` / `{id}_cl` document paths
* [job_info_io.py](/okf/scripts/job-info-io.md) - safe job_info.py field updates

Full reference: [scripts/AGENTS.md](/scripts/AGENTS.md)
