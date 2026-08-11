"""CLI smoke tests for ai_tailor.py."""

from __future__ import annotations

import os
import sys
from unittest.mock import patch

import pytest


def test_provider_flag_does_not_raise_name_error():
    """--provider must set LLM_PROVIDER without NameError (W-01)."""
    argv = [
        "ai_tailor",
        "--jd", "nonexistent_jd_file.txt",
        "--id", "test_cli_smoke",
        "--provider", "anthropic",
    ]
    with patch.object(sys, "argv", argv):
        from scripts.ai_tailor import main
        with pytest.raises(SystemExit):
            main()
    assert os.environ.get("LLM_PROVIDER") == "anthropic"


def test_use_agent_flag_requests_task_specific_model(monkeypatch, tmp_path):
    jd_path = tmp_path / "jd.txt"
    jd_path.write_text("fake jd", encoding="utf-8")
    argv = [
        "ai_tailor",
        "--jd", str(jd_path),
        "--id", "test_cli_smoke",
        "--use-agent",
    ]
    with patch.object(sys, "argv", argv):
        import scripts.ai_tailor as ai_tailor

        seen: dict[str, object] = {}

        def fake_get_default_model(*, task=None, use_task_model=False, model=None, provider=None):
            seen["task"] = task
            seen["use_task_model"] = use_task_model
            return "resolved-model"

        monkeypatch.setattr(ai_tailor, "get_default_model", fake_get_default_model)
        monkeypatch.setattr(ai_tailor, "tailor", lambda *args, **kwargs: {})

        ai_tailor.main()

    assert seen["task"] == "tailor"
    assert seen["use_task_model"] is True


def test_archive_existing_outputs_versions_py_tex_pdf(tmp_path, monkeypatch):
    import scripts.ai_tailor as ai_tailor

    monkeypatch.setattr(
        ai_tailor,
        "data_path",
        lambda *parts: tmp_path.joinpath(*parts),
    )
    out = tmp_path / "resume" / "outputs"
    out.mkdir(parents=True)
    jid = "acme_ml_2026"
    (out / f"{jid}.py").write_text("old", encoding="utf-8")
    (out / f"{jid}.tex").write_text("oldtex", encoding="utf-8")
    (out / f"{jid}.pdf").write_bytes(b"%PDF")

    stem = ai_tailor.archive_existing_outputs("resume", jid)
    assert stem == f"{jid} (1)"
    assert not (out / f"{jid}.py").exists()
    assert (out / f"{jid} (1).py").read_text(encoding="utf-8") == "old"
    assert (out / f"{jid} (1).tex").exists()
    assert (out / f"{jid} (1).pdf").exists()

    # Second archive bumps to (2)
    (out / f"{jid}.py").write_text("newer", encoding="utf-8")
    stem2 = ai_tailor.archive_existing_outputs("resume", jid)
    assert stem2 == f"{jid} (2)"
    assert (out / f"{jid} (2).py").read_text(encoding="utf-8") == "newer"


def test_merge_networking_replaces_outreach_appends_contacts():
    import scripts.ai_tailor as ai_tailor

    existing = """\
# Outreach — Acme: Old

## ① Connection Request

> old connection

## Contacts — Acme

- `a@acme.com` — from [Team](https://acme.com)

## Follow-up (drafted 2026-01-01)
*Review and send manually — this was not sent.*

> Hi there
"""
    new = """\
# Outreach — Acme: SWE
Generated: today

## ① Connection Request

> new connection

## Notes
<!-- Add your notes here as you engage with contacts -->
"""
    merged = ai_tailor.merge_networking_markdown(existing, new)
    assert "new connection" in merged
    assert "old connection" not in merged
    assert "a@acme.com" in merged
    assert "Follow-up (drafted 2026-01-01)" in merged


def test_outreach_prompt_uses_jd_and_fit_not_full_profile(monkeypatch):
    import types

    import scripts.ai_tailor as ai_tailor

    captured: dict = {}

    def fake_call_json(system, user, model, max_tokens=2000, required_keys=None):
        captured["user"] = user
        return {
            "connection_request": "hi",
            "follow_up_message": "thanks",
            "linkedin_search_queries": [],
        }

    class _H:
        name = "Test User"

    fake_header_mod = types.ModuleType("profile.header")
    fake_header_mod.HEADER = _H()
    monkeypatch.setitem(sys.modules, "profile.header", fake_header_mod)
    monkeypatch.setattr(ai_tailor, "call_json", fake_call_json)
    monkeypatch.setattr(ai_tailor, "_education_text", lambda: "MS — Example University")
    monkeypatch.setattr(
        ai_tailor,
        "_profile_text",
        lambda: "SHOULD_NOT_APPEAR_FULL_PROFILE_DUMP",
    )

    ai_tailor.write_outreach(
        {
            "company": "Acme",
            "role": "ML Eng",
            "keywords": ["CUDA", "PyTorch"],
            "hard_requirements": ["C++"],
        },
        {"summary": "Built CUDA kernels for inference at scale."},
        "m",
    )
    assert "Built CUDA kernels" in captured["user"]
    assert "CUDA" in captured["user"]
    assert "SHOULD_NOT_APPEAR_FULL_PROFILE_DUMP" not in captured["user"]
    assert "How the candidate fits this JD" in captured["user"]


def test_cover_letter_prompt_includes_full_profile(monkeypatch):
    import scripts.ai_tailor as ai_tailor

    captured: dict = {}

    def fake_call_json(system, user, model, max_tokens=1500, required_keys=None):
        captured["system"] = system
        captured["user"] = user
        return {"paragraphs": ["a", "b", "c"]}

    monkeypatch.setattr(ai_tailor, "call_json", fake_call_json)
    monkeypatch.setattr(
        ai_tailor,
        "_profile_text",
        lambda: "=== EXPERIENCE ===\nVariable: FOO\nBullets:\n  - Built CUDA kernels",
    )
    ai_tailor.write_cover_letter(
        {"company": "Acme", "role": "ML Eng", "keywords": ["CUDA"]},
        {
            "summary": "short summary only",
            "selected_experience": ["FOO"],
            "selected_projects": [],
        },
        "m",
    )
    assert "FULL CANDIDATE PROFILE" in captured["user"]
    assert "Built CUDA kernels" in captured["user"]
    assert "FACTUAL FIDELITY" in captured["system"]
    assert "short summary only" in captured["user"]


def test_match_profile_prompt_forbids_invented_metrics(monkeypatch):
    import scripts.ai_tailor as ai_tailor

    captured: dict = {}

    def fake_call_json(system, user, model, max_tokens=3000, required_keys=None):
        captured["system"] = system
        captured["user"] = user
        return {
            "selected_experience": [],
            "selected_projects": [],
            "skills_preset": "SKILLS_ML_FOCUSED",
            "summary": "x",
        }

    monkeypatch.setattr(ai_tailor, "call_json", fake_call_json)
    monkeypatch.setattr(ai_tailor, "_profile_text", lambda: "Variable: FOO\nBullets:\n  - Built X")
    ai_tailor.match_profile(
        {"keywords": ["CUDA"], "key_responsibilities": ["train models"], "company": "Acme"},
        "m",
    )
    assert "FACTUAL FIDELITY" in captured["system"]
    assert "traceable to a source" in captured["user"]
    assert "invent" in captured["system"].lower() or "NOT invent" in captured["system"]


def test_merge_networking_keeps_user_notes():
    import scripts.ai_tailor as ai_tailor

    existing = """\
# Outreach — Acme: SWE

## Notes
Talked to Jane on Tuesday.
"""
    new = """\
# Outreach — Acme: SWE

## Notes
<!-- Add your notes here as you engage with contacts -->
"""
    merged = ai_tailor.merge_networking_markdown(existing, new)
    assert "Talked to Jane" in merged
    assert "<!-- Add your notes" not in merged
