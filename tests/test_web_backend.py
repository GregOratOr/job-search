"""Web backend config validation tests."""

from __future__ import annotations

import os
from unittest.mock import patch

from scripts.pipeline import _apply_web_backend


def test_apply_web_backend_rejects_invalid_backend():
    """Invalid automation.web_backend must not poison WEB_BACKEND (W-06)."""
    with patch.dict(os.environ, {}, clear=True):
        _apply_web_backend({"web_backend": "duckduckgo"})
        assert "WEB_BACKEND" not in os.environ


def test_apply_web_backend_accepts_valid_backend():
    with patch.dict(os.environ, {}, clear=True):
        _apply_web_backend({"web_backend": "searxng"})
        assert os.environ.get("WEB_BACKEND") == "searxng"


def test_apply_web_backend_does_not_override_existing_env():
    with patch.dict(os.environ, {"WEB_BACKEND": "tavily"}, clear=True):
        _apply_web_backend({"web_backend": "searxng"})
        assert os.environ.get("WEB_BACKEND") == "tavily"
