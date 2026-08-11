"""Harness web adapter tests (mocked — no stub CLI)."""

from __future__ import annotations

import json
import os
from unittest.mock import patch

import pytest

from scripts import web


def test_search_requires_use_project_web():
    with pytest.raises(RuntimeError, match="opt-in"):
        web.search("q", use_project_web=False)


def test_fetch_requires_use_project_web():
    with pytest.raises(RuntimeError, match="opt-in"):
        web.fetch("https://example.com", use_project_web=False)


def test_harness_search_returns_results(monkeypatch):
    monkeypatch.setenv("HARNESS_WEB_SEARCH_CMD", "true")

    payload = json.dumps(
        [
            {
                "title": "ML Engineer",
                "url": "https://example.com/careers/ml",
                "snippet": "Remote ML role",
            }
        ]
    )
    with patch.object(web, "_run_harness_cmd", return_value=payload) as run:
        results = web.search(
            "ML engineer remote", max_results=3, backend="harness", use_project_web=True,
        )

    run.assert_called_once_with("HARNESS_WEB_SEARCH_CMD", "ML engineer remote")
    assert len(results) == 1
    assert results[0]["url"] == "https://example.com/careers/ml"
    assert results[0]["title"] == "ML Engineer"


def test_harness_fetch_returns_text(monkeypatch):
    monkeypatch.setenv("HARNESS_WEB_FETCH_CMD", "true")
    body = "Company: Example Corp\nRole: Machine Learning Engineer\n"

    with patch.object(web, "_run_harness_cmd", return_value=body) as run:
        text = web.fetch(
            "https://example.com/job/1", backend="harness", use_project_web=True,
        )

    run.assert_called_once_with("HARNESS_WEB_FETCH_CMD", "https://example.com/job/1")
    assert "Machine Learning Engineer" in text


def test_harness_search_missing_env_raises():
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(RuntimeError, match="HARNESS_WEB_SEARCH_CMD"):
            web.search("test", backend="harness", use_project_web=True)


def test_strip_html_basic():
    html = "<html><script>x</script><p>Hello &amp; world</p></html>"
    text = web._strip_html(html)
    assert "Hello & world" in text
    assert "script" not in text.lower() or "x" not in text
