"""Tests for scripts/audit.py prompt contracts (no live LLM)."""

from __future__ import annotations

from scripts import audit as audit_mod


def test_resume_audit_asks_ats_0_100(monkeypatch):
    captured: dict = {}

    def fake_complete(system, user, model, max_tokens=2000):
        captured["user"] = user
        return "## Resume Audit\nok"

    monkeypatch.setattr(audit_mod, "complete", fake_complete)
    audit_mod.audit_resume(
        "Need CUDA and PyTorch",
        {
            "company": "Acme",
            "role": "ML Eng",
            "summary": "x",
            "skills": [],
            "experience": [],
            "projects": [],
        },
        "m",
    )
    assert "ATS readiness (0–100)" in captured["user"]


def test_action_plan_asks_compatibility_and_ats(monkeypatch):
    captured: dict = {}

    def fake_complete(system, user, model, max_tokens=1000):
        captured["user"] = user
        return "## Prioritised Action Plan\nok"

    monkeypatch.setattr(audit_mod, "complete", fake_complete)
    audit_mod.synthesize_action_plan("r", "c", "f", "acme_ml_2026", "m")
    assert "Overall compatibility (0–100)" in captured["user"]
    assert "ATS readiness (0–100)" in captured["user"]


def test_write_audit_report_appends(tmp_path):
    path = tmp_path / "audit.md"
    audit_mod.write_audit_report("# Run one\n", path)
    audit_mod.write_audit_report("# Run two\n", path)
    text = path.read_text(encoding="utf-8")
    assert text.count("# Run one") == 1
    assert text.count("# Run two") == 1
    assert "---" in text


def test_cli_writes_bundle_and_out(tmp_path, monkeypatch):
    bundle = tmp_path / "applications" / "jobs" / "acme_ml_2026" / "audit.md"
    extra = tmp_path / "notes" / "audit.md"

    monkeypatch.setattr(
        audit_mod,
        "data_path",
        lambda *parts: tmp_path.joinpath(*parts),
    )
    monkeypatch.setattr(audit_mod, "audit", lambda job_id, model: "# Audit\nok\n")
    monkeypatch.setattr(audit_mod, "get_default_model", lambda **k: "m")
    monkeypatch.setattr(
        "sys.argv",
        ["audit.py", "--id", "acme_ml_2026", "--out", str(extra)],
    )
    audit_mod.main()
    assert bundle.exists() and "ok" in bundle.read_text(encoding="utf-8")
    assert extra.exists() and "ok" in extra.read_text(encoding="utf-8")


def test_read_cl_content_missing_returns_none(tmp_path, monkeypatch):
    monkeypatch.setattr(
        audit_mod,
        "_resolve_doc_py",
        lambda kind, jid: tmp_path / kind / f"{jid}.py",
    )
    assert audit_mod.read_cl_content("missing_job") is None
