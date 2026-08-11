"""Tests for scripts/followup.py."""

from __future__ import annotations

from scripts.followup import due_rows


def test_due_includes_applied_through_onsite():
    rows = [
        {"id": "a", "status": "Applied", "last_updated": "2020-01-01"},
        {"id": "b", "status": "Recruiter Screen", "last_updated": "2020-01-01"},
        {"id": "c", "status": "Phone Screen", "last_updated": "2020-01-01"},
        {"id": "d", "status": "Technical Interview", "last_updated": "2020-01-01"},
        {"id": "e", "status": "Onsite", "last_updated": "2020-01-01"},
    ]
    due = due_rows(rows, threshold=7, only_id=None)
    assert {r["id"] for r in due} == {"a", "b", "c", "d", "e"}


def test_due_skips_saved_offer_and_terminal():
    rows = [
        {"id": "s", "status": "Saved", "last_updated": "2020-01-01"},
        {"id": "o", "status": "Offer", "last_updated": "2020-01-01"},
        {"id": "acc", "status": "Accepted", "last_updated": "2020-01-01"},
        {"id": "rej", "status": "Rejected", "last_updated": "2020-01-01"},
        {"id": "w", "status": "Withdrawn", "last_updated": "2020-01-01"},
        {"id": "ok", "status": "Applied", "last_updated": "2020-01-01"},
    ]
    due = due_rows(rows, threshold=7, only_id=None)
    assert [r["id"] for r in due] == ["ok"]


def test_due_respects_threshold_unless_only_id():
    rows = [
        {"id": "fresh", "status": "Applied", "last_updated": "2099-01-01"},
        {"id": "stale", "status": "Applied", "last_updated": "2020-01-01"},
    ]
    assert [r["id"] for r in due_rows(rows, threshold=7, only_id=None)] == ["stale"]
    # --id forces inclusion even when not past threshold
    forced = due_rows(rows, threshold=7, only_id="fresh")
    assert len(forced) == 1 and forced[0]["id"] == "fresh"


def test_draft_includes_jd_when_present(tmp_path, monkeypatch):
    from scripts.followup import draft_message

    job_id = "acme_ml_2026"
    jd_dir = tmp_path / "applications" / "jobs" / job_id
    jd_dir.mkdir(parents=True)
    (jd_dir / "jd.txt").write_text(
        "Looking for CUDA and distributed training experience.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "scripts.followup.data_path",
        lambda *parts: tmp_path.joinpath(*parts),
    )
    captured: dict = {}

    def fake_complete(system, user, model, max_tokens=400):
        captured["user"] = user
        return "Hi [Name], drafted."

    monkeypatch.setattr("scripts.followup.complete", fake_complete)
    out = draft_message(
        {"id": job_id, "company": "Acme", "role": "ML Eng", "_age": 10},
        "test-model",
    )
    assert out == "Hi [Name], drafted."
    assert "CUDA" in captured["user"]
    assert "Job description excerpt" in captured["user"]


def test_draft_without_jd_notes_missing(monkeypatch):
    from scripts.followup import draft_message

    monkeypatch.setattr(
        "scripts.followup.data_path",
        lambda *parts: __import__("pathlib").Path("/nonexistent") / "x".join(parts),
    )
    captured: dict = {}
    monkeypatch.setattr(
        "scripts.followup.complete",
        lambda system, user, model, max_tokens=400: captured.__setitem__("user", user) or "ok",
    )
    draft_message({"id": "missing_job", "company": "Acme", "role": "SWE", "_age": 8}, "m")
    assert "No job description on file" in captured["user"]
