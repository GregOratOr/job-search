#!/usr/bin/env -S uv run
"""
scripts/web.py
--------------
Project-owned web access tool with a pluggable search backend.

This gives any harness/model (including a bare local Ollama run that has no
browser of its own) real web search and page-text extraction.

**Harness-native web comes first.** When the harness ships built-in search/extraction,
skills instruct agents to use those tools and NOT invoke this script. This tool is the
fallback for standalone terminal runs and scripted pipelines.

Backend is selected with the WEB_BACKEND env var — it must be set explicitly
(see .env.example):
    searxng              self-hosted SearXNG at SEARXNG_URL
    tavily               Tavily API   (TAVILY_API_KEY)
    brave                Brave Search (BRAVE_API_KEY)
    serper               Serper.dev   (SERPER_API_KEY)
    harness              subprocess adapter (HARNESS_WEB_SEARCH_CMD / HARNESS_WEB_FETCH_CMD)

Harness adapters (when WEB_BACKEND=harness):
    HARNESS_WEB_SEARCH_CMD   shell command + query arg → stdout JSON array
                             [{title, url, snippet}, ...]
    HARNESS_WEB_FETCH_CMD    shell command + url arg → stdout plain text
    Point these at thin wrappers around your harness's native web tools.
    Unit tests mock the adapter; see tests/test_harness_web.py.

Import API requires use_project_web=True (ADR 0004). Running this CLI implies opt-in.

Usage (CLI):
    uv run scripts/web.py search "ML engineer remote 2026" --max 8
    uv run scripts/web.py search "..." --json
    uv run scripts/web.py fetch "https://example.com/job/123"
    uv run scripts/web.py fetch "https://..." --max-chars 8000

Usage (import):
    from scripts.web import search, fetch
    results = search("CUDA inference engineer", max_results=5, use_project_web=True)
    text    = fetch(results[0]["url"], use_project_web=True)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.llm_provider import load_env

load_env()

_DEFAULT_TIMEOUT = 30.0
_USER_AGENT = "Mozilla/5.0 (compatible; job-search-pipeline/1.0)"
_VALID_BACKENDS = frozenset({"searxng", "tavily", "brave", "serper", "harness"})
# Public alias for config validation in pipeline.py and tests.
VALID_BACKENDS = _VALID_BACKENDS


@dataclass(frozen=True)
class SearchResult:
    title: str
    url: str
    snippet: str


# ── Backend resolution ────────────────────────────────────────────────────────

def require_project_web(enabled: bool, *, caller: str = "scripts.web") -> None:
    """Raise unless the caller opted into the project web tool.

    Scripted Tools must pass ``use_project_web=True`` (CLI: ``--use-project-web``)
    before calling ``search`` / ``fetch``. Agent skills with harness-native web
    must not call this module at all (see ADR 0004).
    """
    if enabled:
        return
    raise RuntimeError(
        f"{caller}: project web tool is opt-in. Pass --use-project-web for "
        "unattended/scripted web I/O, or use harness-native search/extract "
        "(see skills + docs/adr/0004-skills-orchestrate-tools-process.md)."
    )


def resolve_backend() -> str:
    backend = os.environ.get("WEB_BACKEND", "").strip().lower()
    if not backend:
        raise RuntimeError(
            "WEB_BACKEND is not set. The project web tool needs an explicit backend:\n"
            "  set WEB_BACKEND in .env to one of: searxng | tavily | brave | serper | harness\n"
            "  plus its endpoint/key (e.g. SEARXNG_URL, TAVILY_API_KEY) - see .env.example.\n"
            "Agent harnesses with native web search/extract do not need WEB_BACKEND."
        )
    if backend not in _VALID_BACKENDS:
        raise ValueError(
            f"Unknown WEB_BACKEND={backend!r}. Use one of: {', '.join(sorted(_VALID_BACKENDS))}"
        )
    return backend


def _run_harness_cmd(env_var: str, *args: str) -> str:
    """Run a harness adapter command from env; return stdout."""
    raw = os.environ.get(env_var, "").strip()
    if not raw:
        raise RuntimeError(
            f"{env_var} is not set. Configure harness web adapters in .env — "
            "see okf/architecture/web-access-policy.md and .env.example."
        )
    cmd = shlex.split(raw, posix=os.name != "nt") + list(args)
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=120,
        cwd=ROOT,
    )
    if result.returncode != 0:
        err = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(f"{env_var} failed (exit {result.returncode}): {err[:500]}")
    return result.stdout.strip()


# ── Search backends ───────────────────────────────────────────────────────────

def _search_searxng(query: str, max_results: int) -> list[SearchResult]:
    base = os.environ.get("SEARXNG_URL", "http://127.0.0.1:8888").rstrip("/")
    url = f"{base}/search"
    params = {"q": query, "format": "json"}
    categories = os.environ.get("SEARXNG_CATEGORIES", "").strip()
    if categories:
        params["categories"] = categories
    resp = httpx.get(url, params=params, timeout=_DEFAULT_TIMEOUT,
                     headers={"User-Agent": _USER_AGENT})
    resp.raise_for_status()
    data = resp.json()
    out: list[SearchResult] = []
    for r in data.get("results", [])[:max_results]:
        out.append(SearchResult(
            title=str(r.get("title", "")).strip(),
            url=str(r.get("url", "")).strip(),
            snippet=str(r.get("content", "")).strip(),
        ))
    return out


def _search_tavily(query: str, max_results: int) -> list[SearchResult]:
    key = os.environ.get("TAVILY_API_KEY", "").strip()
    if not key:
        raise RuntimeError("TAVILY_API_KEY not set for WEB_BACKEND=tavily.")
    resp = httpx.post(
        "https://api.tavily.com/search",
        json={"api_key": key, "query": query, "max_results": max_results},
        timeout=_DEFAULT_TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()
    out: list[SearchResult] = []
    for r in data.get("results", [])[:max_results]:
        out.append(SearchResult(
            title=str(r.get("title", "")).strip(),
            url=str(r.get("url", "")).strip(),
            snippet=str(r.get("content", "")).strip(),
        ))
    return out


def _search_brave(query: str, max_results: int) -> list[SearchResult]:
    key = os.environ.get("BRAVE_API_KEY", "").strip()
    if not key:
        raise RuntimeError("BRAVE_API_KEY not set for WEB_BACKEND=brave.")
    resp = httpx.get(
        "https://api.search.brave.com/res/v1/web/search",
        params={"q": query, "count": max_results},
        headers={"X-Subscription-Token": key, "Accept": "application/json",
                 "User-Agent": _USER_AGENT},
        timeout=_DEFAULT_TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()
    out: list[SearchResult] = []
    for r in (data.get("web", {}) or {}).get("results", [])[:max_results]:
        out.append(SearchResult(
            title=str(r.get("title", "")).strip(),
            url=str(r.get("url", "")).strip(),
            snippet=str(r.get("description", "")).strip(),
        ))
    return out


def _search_serper(query: str, max_results: int) -> list[SearchResult]:
    key = os.environ.get("SERPER_API_KEY", "").strip()
    if not key:
        raise RuntimeError("SERPER_API_KEY not set for WEB_BACKEND=serper.")
    resp = httpx.post(
        "https://google.serper.dev/search",
        json={"q": query, "num": max_results},
        headers={"X-API-KEY": key, "Content-Type": "application/json"},
        timeout=_DEFAULT_TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()
    out: list[SearchResult] = []
    for r in data.get("organic", [])[:max_results]:
        out.append(SearchResult(
            title=str(r.get("title", "")).strip(),
            url=str(r.get("link", "")).strip(),
            snippet=str(r.get("snippet", "")).strip(),
        ))
    return out


def _search_harness(query: str, max_results: int) -> list[SearchResult]:
    raw = _run_harness_cmd("HARNESS_WEB_SEARCH_CMD", query)
    data = json.loads(raw)
    if not isinstance(data, list):
        raise ValueError(f"HARNESS_WEB_SEARCH_CMD must return a JSON array, got {type(data).__name__}")
    out: list[SearchResult] = []
    for item in data[:max_results]:
        if not isinstance(item, dict):
            continue
        out.append(SearchResult(
            title=str(item.get("title", "")).strip(),
            url=str(item.get("url", "")).strip(),
            snippet=str(item.get("snippet", "")).strip(),
        ))
    return out


_BACKENDS = {
    "searxng": _search_searxng,
    "tavily": _search_tavily,
    "brave": _search_brave,
    "serper": _search_serper,
    "harness": _search_harness,
}


def search(
    query: str,
    max_results: int = 8,
    backend: str | None = None,
    *,
    use_project_web: bool = False,
) -> list[dict]:
    """Run a web search. Returns a list of {title, url, snippet} dicts.

    Requires ``use_project_web=True`` (CLI invocation of this script counts as opt-in).
    """
    require_project_web(use_project_web, caller="scripts.web.search")
    backend = backend or resolve_backend()
    fn = _BACKENDS[backend]
    return [asdict(r) for r in fn(query, max_results)]


# ── Page fetch + text extraction ──────────────────────────────────────────────

def _strip_html(html: str) -> str:
    """Crude readability: drop script/style/nav noise, strip tags, collapse space."""
    # Remove script/style blocks entirely
    html = re.sub(r"<(script|style|noscript|template)[^>]*>.*?</\1>", " ",
                  html, flags=re.IGNORECASE | re.DOTALL)
    # Drop common chrome containers
    html = re.sub(r"<(nav|header|footer|aside)[^>]*>.*?</\1>", " ",
                  html, flags=re.IGNORECASE | re.DOTALL)
    # Turn block-level closers into newlines so structure survives
    html = re.sub(r"</(p|div|li|h[1-6]|tr|section|article|br)\s*>", "\n",
                  html, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", html)
    # Unescape a few common entities
    for ent, ch in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
                    ("&quot;", '"'), ("&#39;", "'"), ("&nbsp;", " ")):
        text = text.replace(ent, ch)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def fetch(
    url: str,
    max_chars: int = 12000,
    backend: str | None = None,
    *,
    use_project_web: bool = False,
) -> str:
    """Fetch a URL and return readable plain text (HTML stripped).

    Requires ``use_project_web=True`` (CLI invocation of this script counts as opt-in).
    """
    require_project_web(use_project_web, caller="scripts.web.fetch")
    resolved = backend or resolve_backend()
    if resolved == "harness":
        text = _run_harness_cmd("HARNESS_WEB_FETCH_CMD", url)
        return text[:max_chars]
    resp = httpx.get(url, follow_redirects=True, timeout=_DEFAULT_TIMEOUT,
                     headers={"User-Agent": _USER_AGENT})
    resp.raise_for_status()
    text = _strip_html(resp.text)
    return text[:max_chars]


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Project web tool: search + fetch.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_search = sub.add_parser("search", help="Search the web")
    p_search.add_argument("query")
    p_search.add_argument("--max", type=int, default=8, help="Max results (default 8)")
    p_search.add_argument("--backend", default=None, help="Override WEB_BACKEND for this run")
    p_search.add_argument("--json", action="store_true", help="Emit raw JSON")

    p_fetch = sub.add_parser("fetch", help="Fetch and extract page text")
    p_fetch.add_argument("url")
    p_fetch.add_argument("--max-chars", type=int, default=12000, help="Cap on extracted chars")
    p_fetch.add_argument("--backend", default=None, help="Override WEB_BACKEND for this run")
    p_fetch.add_argument("--json", action="store_true", help="Emit JSON {url, text}")

    args = parser.parse_args()

    if args.command == "search":
        try:
            results = search(
                args.query,
                max_results=args.max,
                backend=args.backend,
                use_project_web=True,
            )
        except Exception as e:  # noqa: BLE001 — CLI surface, show a clean error
            print(f"[x] search failed: {e}")
            sys.exit(1)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            if not results:
                print("No results.")
            for i, r in enumerate(results, 1):
                print(f"{i:2}. {r['title']}")
                print(f"    {r['url']}")
                if r["snippet"]:
                    print(f"    {r['snippet'][:200]}")
        return

    if args.command == "fetch":
        try:
            text = fetch(
                args.url,
                max_chars=args.max_chars,
                backend=getattr(args, "backend", None),
                use_project_web=True,
            )
        except Exception as e:  # noqa: BLE001
            print(f"[x] fetch failed: {e}")
            sys.exit(1)
        if args.json:
            print(json.dumps({"url": args.url, "text": text}, indent=2))
        else:
            print(text)
        return


if __name__ == "__main__":
    main()