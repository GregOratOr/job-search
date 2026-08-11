#!/usr/bin/env -S uv run
"""
scripts/research.py
-------------------
Research Tools split for agent vs unattended use (ADR 0004):

  gather()      — web search + fetch (requires use_project_web=True)
  synthesize()  — LLM brief from already-gathered sources (no web)
  research()    — unattended batch: gather → synthesize
  write_brief() — write markdown to ``--out`` and/or the application bundle
                 (both when both are set)

Agent path: harness-native web → build sources → synthesize() or write the brief
yourself. Do not call gather()/research() without --use-project-web.

Usage:
    uv run scripts/research.py "NVIDIA inference" --use-project-web --id nvidia_ml_2026
    uv run scripts/research.py --synthesize-from sources.json --topic "NVIDIA" --out brief.md
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.data_paths import apply_private_overlay, data_path
from scripts.llm_provider import complete, get_default_model, load_env, resolve_provider
from scripts.web import fetch, require_project_web, search

apply_private_overlay()
load_env()


def gather(
    topic: str,
    max_pages: int = 5,
    *,
    use_project_web: bool = False,
) -> tuple[list[dict], list[dict]]:
    """Search + fetch source pages.

    Returns ``(sources, failures)`` where:
      sources  — ``[{title, url, text}, ...]``
      failures — ``[{title, url, error}, ...]`` for pages that could not be fetched

    Requires ``use_project_web=True`` (CLI ``--use-project-web``). Agents with
    harness-native web should gather themselves and call ``synthesize`` instead.
    """
    require_project_web(use_project_web, caller="scripts.research.gather")
    print(f"  Searching: {topic}")
    results = search(topic, max_results=max_pages, use_project_web=True)
    sources: list[dict] = []
    failures: list[dict] = []
    for r in results[:max_pages]:
        url = r.get("url", "")
        if not url:
            continue
        title = r.get("title", "")
        try:
            text = fetch(url, max_chars=4000, use_project_web=True)
        except Exception as e:  # noqa: BLE001 — skip unreachable pages
            print(f"  [skip] {url}: {e}")
            failures.append({"title": title, "url": url, "error": str(e)})
            continue
        print(f"  Fetched: {url}")
        sources.append({"title": title, "url": url, "text": text})
    return sources, failures


def synthesize(topic: str, focus: str | None, sources: list[dict], model: str) -> str:
    """LLM-only brief from sources. No web I/O."""
    if not sources:
        return f"# Research brief: {topic}\n\n_No sources could be fetched._\n"

    blocks = []
    for i, s in enumerate(sources, 1):
        blocks.append(f"[Source {i}] {s['title']} — {s['url']}\n{s['text']}")
    corpus = "\n\n---\n\n".join(blocks)

    focus_line = f"\nFocus the brief on: {focus}." if focus else ""
    system = (
        "You are a diligent research analyst. Synthesize the provided web sources into a "
        "concise, factual markdown brief. Cite sources inline as [n] matching the source "
        "numbers. Do not invent facts; if sources disagree or are thin, say so. "
        "Do not add a Sources section — the caller appends one."
    )
    user = f"""Topic: {topic}{focus_line}

Write a markdown brief with these sections:
## Summary
## Key facts
## What it means for a job applicant

Use the numbered sources below. Keep it under ~400 words.

SOURCES:
{corpus[:14000]}
"""
    print("  Synthesizing brief...")
    return complete(system, user, model, max_tokens=1500)


def _append_source_footer(
    brief: str,
    sources: list[dict],
    failures: list[dict] | None = None,
) -> str:
    """Append authoritative Sources links and any Failed fetches."""
    failures = failures or []
    parts = [brief.rstrip()]
    if sources:
        parts.append(
            "## Sources\n"
            + "\n".join(
                f"{i}. [{s['title'] or s['url']}]({s['url']})"
                for i, s in enumerate(sources, 1)
            )
        )
    if failures:
        parts.append(
            "## Failed fetches\n"
            + "\n".join(
                f"- [{f['title'] or f['url']}]({f['url']}) — {f.get('error', 'fetch failed')}"
                for f in failures
            )
        )
    if len(parts) == 1:
        return brief
    return "\n\n".join(parts) + "\n"


def research(
    topic: str,
    focus: str | None = None,
    max_pages: int = 5,
    model: str | None = None,
    *,
    use_task_model: bool = False,
    use_project_web: bool = False,
) -> str:
    """Unattended batch: gather (project web) → synthesize."""
    model = model or get_default_model(task="research", use_task_model=use_task_model)
    print(f"\n{'='*60}\n  Research: {topic}\n  Provider: {resolve_provider()}\n{'='*60}")
    sources, failures = gather(topic, max_pages, use_project_web=use_project_web)
    brief = synthesize(topic, focus, sources, model)
    return _append_source_footer(brief, sources, failures)


def write_brief(
    brief: str,
    *,
    job_id: str | None = None,
    out: str | Path | None = None,
) -> list[Path]:
    """Write brief to ``--out`` and/or ``applications/jobs/<id>/research.md``.

    When both are set, both files are written. Returns the paths written
    (empty if neither destination was given). Identical paths are written once.
    """
    destinations: list[Path] = []
    if out:
        destinations.append(Path(out))
    if job_id:
        destinations.append(data_path("applications", "jobs", job_id, "research.md"))

    written: list[Path] = []
    seen: set[str] = set()
    for out_path in destinations:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        key = str(out_path.resolve())
        if key in seen:
            continue
        seen.add(key)
        out_path.write_text(brief, encoding="utf-8")
        written.append(out_path)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Research Tools: gather / synthesize / unattended research (ADR 0004)."
    )
    parser.add_argument(
        "topic",
        nargs="?",
        default=None,
        help="What to research (or pass --topic)",
    )
    parser.add_argument(
        "--topic",
        dest="topic_flag",
        default=None,
        help="Topic (alternative to positional; required with --synthesize-from if no positional)",
    )
    parser.add_argument("--focus", default=None, help="Angle, e.g. 'interview prep' or 'culture'")
    parser.add_argument("--max", type=int, default=5, help="Max source pages (default 5)")
    parser.add_argument("--model", default=None, help="Model override")
    parser.add_argument(
        "--use-agent",
        action="store_true",
        help="Use the task-specific model from .env for this run instead of the base model.",
    )
    parser.add_argument(
        "--use-project-web",
        action="store_true",
        help="Opt in to scripts/web.py for gather/research (required for unattended web I/O).",
    )
    parser.add_argument(
        "--synthesize-from",
        default=None,
        metavar="PATH",
        help="JSON file of sources [{title,url,text}, ...] — skip gather; LLM synthesize only.",
    )
    parser.add_argument("--id", default=None, help="Application id; writes applications/jobs/<id>/research.md")
    parser.add_argument("--out", default=None, help="Explicit output path for the brief")
    args = parser.parse_args()
    topic = args.topic_flag or args.topic

    model = args.model or get_default_model(task="research", use_task_model=args.use_agent)

    if args.synthesize_from:
        if not topic:
            print("[x] --synthesize-from requires a topic (positional or --topic).")
            sys.exit(1)
        raw = Path(args.synthesize_from).read_text(encoding="utf-8")
        sources = json.loads(raw)
        if not isinstance(sources, list):
            print("[x] --synthesize-from must be a JSON array of source objects.")
            sys.exit(1)
        brief = _append_source_footer(synthesize(topic, args.focus, sources, model), sources)
    else:
        if not topic:
            print("[x] topic is required (or use --synthesize-from with --topic).")
            sys.exit(1)
        if not args.use_project_web:
            print(
                "[x] Unattended research needs web I/O. Pass --use-project-web, "
                "or gather with harness-native web and use --synthesize-from. "
                "See skills/research/SKILL.md and ADR 0004."
            )
            sys.exit(1)
        brief = research(
            topic,
            focus=args.focus,
            max_pages=args.max,
            model=model,
            use_task_model=args.use_agent,
            use_project_web=True,
        )

    written = write_brief(brief, job_id=args.id, out=args.out)
    if written:
        for path in written:
            print(f"\n[+] Brief written: {path}")
    else:
        print("\n" + brief)


if __name__ == "__main__":
    main()
