#!/usr/bin/env -S uv run
"""
scripts/pipeline.py
-------------------
End-to-end orchestrator for the job-search pipeline. Chains:

    discover -> tailor -> research -> build -> audit -> bundle -> track(Saved)

How far it runs is controlled by `autonomy_level` in
config/job_search_config.yaml (overridable with --level), or by an explicit
--steps list for piecewise/manual runs.

  autonomy_level:
    discover_only : find + shortlist jobs (no tailoring)
    tailor        : also tailor resume / cover letter / outreach drafts
    full_bundle   : also build PDFs, run the audit, finalize the bundle,
                    log as "Saved"

The audit step writes applications/jobs/<id>/audit.md (advisory only — it never
edits profile or tailoring files). It can also be run independently:

    uv run scripts/audit.py --id <id>
    uv run scripts/pipeline.py --id <id> --steps audit

HARD CEILING (always enforced, every level): this tool NEVER submits an
application to a job site and NEVER sends a message. The most it does is
prepare the bundle and log the application as "Saved". Submitting and sending
stay manual. (See docs/adr/0002-autonomy-ceiling.md.)

Usage:
    # Discovery-driven (config autonomy_level) — needs project web for search/fetch
    uv run scripts/pipeline.py --use-project-web

    # Override how far it goes
    uv run scripts/pipeline.py --level tailor --max 3 --use-project-web
    uv run scripts/pipeline.py --query "LLM inference engineer remote" --max 5 --use-project-web

    # Single known job, end-to-end
    uv run scripts/pipeline.py --url "https://company/careers/123" --id company_role_2026 --use-project-web
    uv run scripts/pipeline.py --jd jd.txt --id company_role_2026

    # Piecewise on an existing application (skip discovery)
    uv run scripts/pipeline.py --id company_role_2026 --steps build,track
    uv run scripts/pipeline.py --id company_role_2026 --steps audit

    # Pause for confirmation before each per-job step
    uv run scripts/pipeline.py --gate --use-project-web
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import yaml

from scripts.data_paths import apply_private_overlay, data_path, resolve_path
from scripts.llm_provider import get_default_model, load_env, resolve_provider
from scripts.job_info_io import load_job_info
from scripts.track import log_saved

load_env()
apply_private_overlay()

ALL_STEPS = ["discover", "tailor", "research", "build", "audit", "bundle", "track"]

_LEVEL_STEPS = {
    "discover_only": ["discover"],
    "tailor":        ["discover", "tailor", "track"],
    "full_bundle":   ["discover", "tailor", "research", "build", "audit", "bundle", "track"],
}

# Search/fetch for discovery go through scripts/web.py when --use-project-web
# is set (ADR 0004). Backend is WEB_BACKEND in .env (searxng|tavily|brave|serper|harness).
# Retired: --search-mode web|anthropic|harness (use WEB_BACKEND instead).


def _load_config() -> dict:
    cfg_path = resolve_path("config", "job_search_config.yaml")
    if cfg_path.exists():
        return yaml.safe_load(cfg_path.read_text()) or {}
    return {}


def _automation(cfg: dict) -> dict:
    return cfg.get("automation", {}) or {}


def _apply_web_backend(auto: dict) -> None:
    """Let config pick the web backend unless the env already sets one."""
    from scripts.web import VALID_BACKENDS

    backend = str(auto.get("web_backend", "") or "").strip().lower()
    if not backend or os.environ.get("WEB_BACKEND"):
        return
    if backend not in VALID_BACKENDS:
        print(f"  [warn] automation.web_backend={backend!r} is not valid "
              f"({', '.join(sorted(VALID_BACKENDS))}); ignoring. "
              f"Set WEB_BACKEND in .env or fix config/job_search_config.yaml.")
        return
    os.environ["WEB_BACKEND"] = backend


def _gate(step: str, enabled: bool) -> bool:
    """Return True to proceed. When gating, ask the user; otherwise always proceed."""
    if not enabled:
        return True
    try:
        ans = input(f"  >> Proceed with step '{step}'? [Y/n] ").strip().lower()
    except EOFError:
        return True
    return ans in ("", "y", "yes")


# ── Per-job processing ────────────────────────────────────────────────────────

def _tailor_job(job_id: str, jd_text: str, model: str, url: str | None) -> bool:
    from scripts.ai_tailor import tailor
    tailor(job_id, jd_text, model, dry_run=False, url=url)
    return True


def _resolve_task_model(task: str, model_override: str | None, use_task_model: bool) -> str:
    return model_override or get_default_model(task=task, use_task_model=use_task_model)


def _research_job(job_id: str, model: str, *, use_project_web: bool = False) -> None:
    """Run research.py for this job and write research.md into the bundle dir."""
    from scripts.research import research, write_brief
    if not use_project_web:
        print(
            f"  [research] skipped for {job_id}: pass --use-project-web for "
            "unattended web gather, or have the agent write research.md "
            "(see skills/research/SKILL.md, ADR 0004)."
        )
        return
    job_info_path = data_path("applications", "jobs", job_id, "job_info.py")
    if not job_info_path.exists():
        print(f"  [research] no job_info.py for {job_id}; skipping research step.")
        return
    import importlib.util
    spec   = importlib.util.spec_from_file_location("job_info", str(job_info_path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    company = getattr(module, "COMPANY", "")
    role    = getattr(module, "ROLE", "")
    if not company:
        print(f"  [research] COMPANY not set in job_info.py for {job_id}; skipping.")
        return
    topic = f"{company} {role} team culture interview"
    brief = research(topic, model=model, use_project_web=True)
    written = write_brief(brief, job_id=job_id)
    if written:
        print(f"  [+] research.md written for {job_id} ({written[0]})")
    else:
        print(f"  [+] research.md written for {job_id}")


def _build_job(job_id: str, build_pdf: bool) -> None:
    import scripts.build as build_mod
    rp = build_mod.build_resume(job_id)
    cp = build_mod.build_coverletter(job_id)
    if build_pdf:
        if rp:
            build_mod.compile_pdf(rp)
        if cp:
            build_mod.compile_pdf(cp)


def _audit_job(job_id: str, model: str) -> None:
    """Run the 4-phase application audit and append to audit.md in the bundle dir."""
    from scripts.audit import audit, write_audit_report
    try:
        report = audit(job_id, model)
    except FileNotFoundError as e:
        print(f"  [audit] skipped for {job_id}: {e}")
        return
    out_path = data_path("applications", "jobs", job_id, "audit.md")
    write_audit_report(report, out_path)
    print(f"  [+] audit.md updated for {job_id} (advisory only — review 🔴 items "
          "in resume/outputs/ and coverletter/outputs/ before submitting)")


def _bundle_job(job_id: str) -> None:
    from scripts.bundle import finalize_bundle
    finalize_bundle(job_id)


def _contacts_job(job_id: str, company: str, role: str, *, use_project_web: bool = False) -> None:
    """Append a Contacts section to the job bundle's networking.md."""
    try:
        from scripts.find_contacts import append_contacts_for_job
        path = append_contacts_for_job(
            job_id, company, role, use_project_web=use_project_web,
        )
        print(f"  [+] Contacts appended to {path}")
    except Exception as e:  # noqa: BLE001
        print(f"  [warn] find_contacts failed for {job_id}: {e}")


def _track_saved(job_id: str, url: str | None, company: str | None = None,
                 role: str | None = None) -> None:
    """Log the application as 'Saved' (the autonomy ceiling)."""
    log_saved(job_id, url=url, company=company, role=role, status="Saved")


def _process_job(job_id: str, jd_text: str, url: str | None, steps: list[str],
                 model_override: str | None, build_pdf: bool, gate: bool,
                 use_task_model: bool = False,
                 find_contacts: bool = False,
                 use_project_web: bool = False,
                 company: str | None = None, role: str | None = None) -> str:
    """Run the selected steps for one job.

    *model_override* is the CLI --model value; when None, each step resolves
    its own model from .env (LLM_MODEL_<TASK> → LLM_MODEL → provider var).
    """
    print(f"\n{'─'*60}\n  Job: {job_id}\n{'─'*60}")
    try:
        if "tailor" in steps and _gate("tailor", gate):
            _tailor_job(job_id, jd_text,
                        _resolve_task_model("tailor", model_override, use_task_model), url)
        if "research" in steps and _gate("research", gate):
            _research_job(
                job_id,
                _resolve_task_model("research", model_override, use_task_model),
                use_project_web=use_project_web,
            )
        if "build" in steps and _gate("build", gate):
            _build_job(job_id, build_pdf)
        if "audit" in steps and _gate("audit", gate):
            _audit_job(job_id, _resolve_task_model("audit", model_override, use_task_model))
        if "bundle" in steps and _gate("bundle", gate):
            _bundle_job(job_id)
        if "track" in steps and _gate("track", gate):
            _track_saved(job_id, url, company=company, role=role)
        if find_contacts:
            info = load_job_info(job_id)
            co = company or info.get("company", "")
            ro = role or info.get("role", "")
            if co:
                _contacts_job(job_id, co, ro, use_project_web=use_project_web)
        return "ok"
    except Exception as e:  # noqa: BLE001 — keep the batch alive
        print(f"  [error] {job_id}: {e}")
        return f"error: {e}"


# ── Main run ──────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="End-to-end job pipeline orchestrator (honors autonomy_level).",
    )
    parser.add_argument("--level", choices=list(_LEVEL_STEPS),
                        help="Override autonomy_level from config")
    parser.add_argument("--steps", default=None,
                        help="Explicit comma-separated steps "
                             "(discover,tailor,research,build,audit,bundle,track) — overrides --level")
    parser.add_argument("--query", default=None, help="Custom discovery query")
    parser.add_argument("--max", type=int, default=None, help="Max jobs to discover")
    parser.add_argument(
        "--search-mode",
        choices=["web", "anthropic", "harness", "hermes"],
        default=None,
        help=argparse.SUPPRESS,  # retired — WEB_BACKEND + --use-project-web
    )
    parser.add_argument("--url", default=None, help="Single job posting URL (skips discovery)")
    parser.add_argument("--jd", default=None, help="Path to a JD text file (skips discovery)")
    parser.add_argument("--id", default=None, help="Application id (required for single-job / piecewise)")
    parser.add_argument("--model", default=None, help="Model override")
    parser.add_argument("--provider", default=None,
                        choices=["anthropic", "ollama", "openai"],
                        help="Override LLM_PROVIDER for this run (cloud harness sessions)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Discover and shortlist only (no tailoring or files)")
    parser.add_argument("--build", action="store_true",
                        help="Shorthand: discover,tailor,build,bundle,track (no research/audit)")
    parser.add_argument("--find-contacts", action="store_true",
                        help="After each tailored job, append contacts to networking.md")
    parser.add_argument("--use-agent", action="store_true",
                        help="Use task-specific models from .env for the pipeline steps.")
    parser.add_argument(
        "--use-project-web",
        action="store_true",
        help="Opt in to scripts/web.py for discovery/fetch/research/contacts (ADR 0004). "
             "Backend from WEB_BACKEND in .env (searxng|tavily|brave|serper|harness). "
             "Agents with harness-native web should skip this and use harness tools.",
    )
    parser.add_argument("--gate", action="store_true",
                        help="Pause for confirmation before each step")
    args = parser.parse_args()

    if args.provider:
        os.environ["LLM_PROVIDER"] = args.provider

    if args.search_mode:
        print(
            f"[deprecated] --search-mode={args.search_mode!r} is ignored. "
            "Use --use-project-web and set WEB_BACKEND in .env "
            "(searxng|tavily|brave|serper|harness)."
        )

    cfg   = _load_config()
    auto  = _automation(cfg)
    _apply_web_backend(auto)
    # CLI --model overrides everything; otherwise each step resolves its own
    # model from .env (LLM_MODEL_<TASK> → LLM_MODEL → provider variable).
    model_override = args.model
    build_pdf = bool(auto.get("build_pdf", True))

    level = args.level or auto.get("autonomy_level", "full_bundle")
    if args.dry_run:
        level = "discover_only"
        steps = ["discover"]
    elif args.steps:
        steps = [s.strip() for s in args.steps.split(",") if s.strip()]
        bad = [s for s in steps if s not in ALL_STEPS]
        if bad:
            print(f"[x] Unknown steps {bad}. Valid: {', '.join(ALL_STEPS)}")
            sys.exit(1)
        level = args.level or "custom"
    elif args.build and not args.level:
        level = "tailor_build"
        steps = ["discover", "tailor", "build", "bundle", "track"]
    else:
        if level not in _LEVEL_STEPS:
            print(f"[x] Unknown autonomy_level '{level}'. Use: {', '.join(_LEVEL_STEPS)}")
            sys.exit(1)
        steps = _LEVEL_STEPS[level]

    single_job = bool(args.url or args.jd)

    model_label = model_override or "per-task from .env"
    print(f"\n{'='*60}")
    print(f"  Pipeline  |  provider: {resolve_provider()}  model: {model_label}")
    print(f"  Steps: {', '.join(steps)}   (level: {level})")
    print(f"  Ceiling: never auto-submits, never auto-sends; max action = log 'Saved'.")
    print(f"{'='*60}")

    # ── Single known job (skips discovery) ────────────────────────────────────
    if single_job or (args.id and "discover" not in steps):
        if not args.id:
            print("[x] --id is required for a single-job or piecewise run.")
            sys.exit(1)
        jd_text = ""
        if args.url:
            from scripts.web import fetch, require_project_web
            try:
                require_project_web(args.use_project_web, caller="pipeline --url")
            except RuntimeError as e:
                print(f"[x] {e}")
                sys.exit(1)
            jd_text = fetch(args.url, max_chars=10000, use_project_web=True)
        elif args.jd:
            p = Path(args.jd)
            if not p.exists():
                print(f"[x] JD file not found: {p}")
                sys.exit(1)
            jd_text = p.read_text(encoding="utf-8")
        elif "tailor" in steps:
            print("[x] tailor step needs --url or --jd to supply the job description.")
            sys.exit(1)
        status = _process_job(args.id, jd_text, args.url, steps,
                              model_override, build_pdf, args.gate,
                              use_task_model=args.use_agent,
                              find_contacts=args.find_contacts,
                              use_project_web=args.use_project_web)
        print(f"\n  Result: {args.id} -> {status}")
        return

    # ── Discovery-driven batch ────────────────────────────────────────────────
    from scripts.job_discovery import discover_jobs, fetch_jd, _make_id
    max_jobs = args.max or int(auto.get("max_jobs", 5))
    discovery_model = _resolve_task_model("discovery", model_override, args.use_agent)
    jobs = discover_jobs(args.query, max_jobs, discovery_model, cfg,
                         use_project_web=args.use_project_web)

    if not jobs:
        print("\n  No jobs found.")
        return

    if steps == ["discover"]:
        print("\n  discover_only: shortlist above. No files written.")
        return

    summary = []
    for job in jobs:
        url     = job.get("url", "")
        company = job.get("company", "Unknown")
        role    = job.get("role", "Unknown Role")
        job_id  = _make_id(company, role)
        jd_text = (
            fetch_jd(url, use_project_web=args.use_project_web)
            if url else None
        )
        if "tailor" in steps and not jd_text:
            print(f"  [skip] {job_id}: could not fetch JD from {url}")
            summary.append((job_id, "skipped (no JD)"))
            continue
        status = _process_job(job_id, jd_text or "", url, steps,
                              model_override, build_pdf, args.gate,
                              use_task_model=args.use_agent,
                              find_contacts=args.find_contacts,
                              use_project_web=args.use_project_web,
                              company=company, role=role)
        summary.append((job_id, status))

    print(f"\n{'='*60}\n  PIPELINE COMPLETE\n{'='*60}")
    for jid, st in summary:
        print(f"  {jid:<38} {st}")
    print("\n  Manual next steps (the ceiling): open each applications/jobs/<id>/, "
          "upload the PDFs to the posting, review networking.md, then send outreach yourself.")
    print("\n  Follow-up reminder: run the following after 7+ days to draft follow-up messages:")
    print("    uv run scripts/followup.py")


if __name__ == "__main__":
    main()