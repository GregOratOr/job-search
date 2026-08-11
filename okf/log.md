# Bundle Update Log

## 2026-08-09
* **Docs sync:** OKF + AGENTS/CONTEXT/applications aligned with current code —
  cover-letter `{id}_cl` stems ([data-paths](/okf/scripts/data-paths.md));
  explicit `WEB_BACKEND`; agent [shortlist](/okf/glossary/shortlist.md) +
  [platform playbook](/okf/glossary/platform-playbook.md); `new-application.md` OKF page;
  discover-jobs vs pipeline batch clarified; refreshed
  [discontinuities](/okf/audit/codebase-discontinuities.md).

## 2026-08-05
* **Docs sync:** Brought skills/OKF/AGENTS/README/ADR notes in line with current code —
  `--use-project-web` on discovery examples; `job_discovery` library-only; SA-13 /
  `--search-mode` retirement; discovery `search_terms` in queries + rank prompt; refreshed
  [discontinuities](/okf/audit/codebase-discontinuities.md).
* **Earlier same day:** Removed `job_discovery.py` CLI; queries/rank use config `search_terms`.

## 2026-07-09 (Phase B)
* **Consolidation**: `ai_tailor` URL fetch via [web.fetch](/okf/scripts/web.md); [track.log_saved()](/okf/scripts/track.md); [json_llm.py](/okf/scripts/json-llm.md) + [text_utils.py](/okf/scripts/text-utils.md); `find_contacts.append_contacts_for_job()`; [pipeline.py](/okf/scripts/pipeline.md) primary; [job_discovery.py](/okf/scripts/job-discovery.md) as discovery library (CLI later removed); [bootstrap.py](/okf/scripts/bootstrap.md) in track/bundle.

## 2026-07-09 (Phase A)
* **Phase A audit fixes**: `import os` in `ai_tailor.py`; `scripts/job_info_io.py` for safe URL writes; dynamic education vars in AI resume codegen; `--provider` on `pipeline.py` / `job_discovery.py`; harness search via subprocess adapters (`HARNESS_WEB_*_CMD` env vars pointing at user-supplied wrappers; the in-repo stub was later removed); pytest suite under `tests/`. Updated [web access policy](/okf/architecture/web-access-policy.md), [web.py](/okf/scripts/web.md), [job-discovery](/okf/scripts/job-discovery.md), [pipeline](/okf/scripts/pipeline.md), [ai-tailor](/okf/scripts/ai-tailor.md), [job-info-io](/okf/scripts/job-info-io.md).

## 2026-07-05
* **Update**: Renamed search mode `hermes` to `harness` (generic built-in web tool; `hermes` kept as deprecated alias) across `job_discovery.py`, `pipeline.py`, skills, and OKF concepts.
* **Update**: Pipeline gained `audit` step (in `full_bundle`, also independent) and harness search mode; models now resolved exclusively from `.env` (`LLM_MODEL_<TASK>` → `LLM_MODEL` → provider var). Updated [pipeline](/okf/workflows/pipeline.md), [pipeline.py](/okf/scripts/pipeline.md), [audit.py](/okf/scripts/audit.md), [llm_provider.py](/okf/scripts/llm-provider.md), and [discontinuities](/okf/audit/codebase-discontinuities.md).
* **Creation**: Initial OKF knowledge bundle from full-project doc audit and harness-native web policy alignment.
* **Update**: Added web access policy, glossary concepts, workflow playbooks, scripts/skills indexes, and codebase discontinuities audit.
