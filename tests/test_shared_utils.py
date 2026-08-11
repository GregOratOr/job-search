"""Tests for scripts/json_llm.py and scripts/text_utils.py."""

from __future__ import annotations

import pytest

from scripts.json_llm import call_json, parse_json, repair_json, validate_keys
from scripts.text_utils import strip_latex


def test_parse_json_strips_fences():
    raw = 'Here you go:\n```json\n{"a": 1}\n```'
    assert parse_json(raw) == {"a": 1}


def test_parse_json_extracts_array_from_prose():
    raw = 'Results:\n[{"id": "a"}, {"id": "b"}]\nThanks!'
    assert parse_json(raw) == [{"id": "a"}, {"id": "b"}]


def test_repair_json_trailing_comma():
    assert parse_json(repair_json('{"a": 1,}')) == {"a": 1}


def test_parse_json_repairs_smart_quotes():
    assert parse_json('{\u201cok\u201d: true}') == {"ok": True}


def test_validate_keys_requires_dict_and_keys():
    validate_keys({"a": 1, "b": 2}, ["a", "b"])
    with pytest.raises(ValueError, match="missing required keys"):
        validate_keys({"a": 1}, ["a", "b"])
    with pytest.raises(ValueError, match="Expected a JSON object"):
        validate_keys([1, 2], ["a"])


def test_strip_latex_texttimes():
    assert "×" in strip_latex(r"2.3\texttimes{} faster")


def test_strip_latex_textbf_and_escapes():
    assert strip_latex(r"Built \textbf{CUDA} kernels") == "Built CUDA kernels"
    assert strip_latex(r"cut cost by 40\% via A \& B") == "cut cost by 40% via A & B"


def test_strip_latex_braces_and_whitespace():
    assert strip_latex(r"foo   {bar}  baz") == "foo bar baz"
    assert strip_latex(r"  \textit{hello}  ") == "hello"


def test_call_json_retries(monkeypatch):
    calls = ["not json", '{"ok": true}']

    def fake_complete(system, user, model, max_tokens=2048, *, quiet=False, **kwargs):
        return calls.pop(0)

    monkeypatch.setattr("scripts.json_llm.complete", fake_complete)
    assert call_json("s", "u", "m", required_keys=["ok"]) == {"ok": True}


def test_call_json_typeerror_fallback(monkeypatch):
    calls = ['{"ok": true}']

    def fake_complete_legacy(system, user, model, max_tokens=2048):
        return calls.pop(0)

    monkeypatch.setattr("scripts.json_llm.complete", fake_complete_legacy)
    assert call_json("s", "u", "m", required_keys=["ok"], task="tailor") == {"ok": True}
