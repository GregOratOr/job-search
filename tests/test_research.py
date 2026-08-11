"""Tests for scripts/research.py (ADR 0004 gather/synthesize split)."""

from __future__ import annotations

import json

import pytest

from scripts.research import gather, research, synthesize, write_brief
from scripts.web import require_project_web


def test_require_project_web_raises_when_disabled():
    with pytest.raises(RuntimeError, match="opt-in"):
        require_project_web(False, caller="test")
    require_project_web(True, caller="test")


def test_gather_requires_use_project_web():
    with pytest.raises(RuntimeError, match="opt-in"):
        gather("NVIDIA", max_pages=1, use_project_web=False)


def test_gather_calls_web_when_opted_in(monkeypatch):
    monkeypatch.setattr(
        "scripts.research.search",
        lambda q, max_results=5, **kwargs: [
            {"title": "T", "url": "https://example.com", "snippet": ""}
        ],
    )
    monkeypatch.setattr(
        "scripts.research.fetch",
        lambda url, max_chars=4000, **kwargs: "body text",
    )
    sources, failures = gather("topic", max_pages=1, use_project_web=True)
    assert sources == [{"title": "T", "url": "https://example.com", "text": "body text"}]
    assert failures == []


def test_gather_records_fetch_failures(monkeypatch):
    monkeypatch.setattr(
        "scripts.research.search",
        lambda q, max_results=5, **kwargs: [
            {"title": "Bad", "url": "https://bad.example", "snippet": ""},
            {"title": "Good", "url": "https://good.example", "snippet": ""},
        ],
    )

    def fake_fetch(url, max_chars=4000, **kwargs):
        if "bad" in url:
            raise ConnectionError("timeout")
        return "ok body"

    monkeypatch.setattr("scripts.research.fetch", fake_fetch)
    sources, failures = gather("topic", max_pages=2, use_project_web=True)
    assert sources == [{"title": "Good", "url": "https://good.example", "text": "ok body"}]
    assert failures == [
        {"title": "Bad", "url": "https://bad.example", "error": "timeout"}
    ]


def test_synthesize_no_sources():
    assert "No sources" in synthesize("topic", None, [], "model")


def test_synthesize_calls_complete(monkeypatch):
    monkeypatch.setattr("scripts.research.complete", lambda *a, **k: "# Brief\n\nDone.")
    out = synthesize("topic", "focus", [{"title": "A", "url": "https://a", "text": "x"}], "m")
    assert "Done" in out


def test_research_batch_requires_flag():
    with pytest.raises(RuntimeError, match="opt-in"):
        research("topic", model="m", use_project_web=False)


def test_write_brief_to_out(tmp_path):
    path = tmp_path / "brief.md"
    written = write_brief("# hi", out=path)
    assert written == [path]
    assert path.read_text(encoding="utf-8") == "# hi"


def test_write_brief_to_both(tmp_path, monkeypatch):
    out = tmp_path / "notes" / "brief.md"
    monkeypatch.setattr(
        "scripts.research.data_path",
        lambda *parts: tmp_path.joinpath(*parts),
    )
    written = write_brief("# both", job_id="acme_ml_2026", out=out)
    bundle = tmp_path / "applications" / "jobs" / "acme_ml_2026" / "research.md"
    assert out in written
    assert bundle in written
    assert out.read_text(encoding="utf-8") == "# both"
    assert bundle.read_text(encoding="utf-8") == "# both"


def test_append_source_footer_always(monkeypatch):
    from scripts.research import _append_source_footer

    sources = [{"title": "A", "url": "https://a.example", "text": "x"}]
    brief = "# Brief\n\nSee https://already.example for context.\n"
    out = _append_source_footer(brief, sources)
    assert "## Sources" in out
    assert "https://a.example" in out
    assert out.count("## Sources") == 1


def test_append_source_footer_empty_sources():
    from scripts.research import _append_source_footer

    brief = "# Brief\n\nok\n"
    assert _append_source_footer(brief, []) == brief


def test_append_failed_fetches_section():
    from scripts.research import _append_source_footer

    brief = "# Brief\n\nok\n"
    sources = [{"title": "A", "url": "https://a.example", "text": "x"}]
    failures = [{"title": "B", "url": "https://b.example", "error": "timeout"}]
    out = _append_source_footer(brief, sources, failures)
    assert "## Failed fetches" in out
    assert "https://b.example" in out
    assert "timeout" in out


def test_synthesize_from_cli(tmp_path, monkeypatch):
    sources = [{"title": "A", "url": "https://a.example", "text": "hello"}]
    src = tmp_path / "sources.json"
    src.write_text(json.dumps(sources), encoding="utf-8")
    out = tmp_path / "out.md"

    monkeypatch.setattr("scripts.research.complete", lambda *a, **k: "## Summary\n\nok")
    monkeypatch.setattr("scripts.research.get_default_model", lambda **k: "test-model")
    monkeypatch.setattr(
        "sys.argv",
        [
            "research.py",
            "--synthesize-from",
            str(src),
            "--topic",
            "Acme",
            "--out",
            str(out),
        ],
    )
    from scripts.research import main

    main()
    assert out.exists()
    assert "ok" in out.read_text(encoding="utf-8")
