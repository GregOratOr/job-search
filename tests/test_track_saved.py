"""Tests for track.log_saved API."""

from __future__ import annotations

from scripts.track import _read_tracker, log_saved


def test_log_saved_writes_row(tmp_path, monkeypatch):
    tracker = tmp_path / "applications" / "tracker.csv"
    tracker.parent.mkdir(parents=True)
    job_dir = tmp_path / "applications" / "jobs" / "acme_ml_2026"
    job_dir.mkdir(parents=True)
    (job_dir / "job_info.py").write_text(
        'COMPANY = "Acme"\nROLE = "ML Engineer"\nURL = "https://example.com"\n',
        encoding="utf-8",
    )

    def _data_path(*parts):
        return tmp_path.joinpath(*parts)

    monkeypatch.setattr("scripts.track.TRACKER_CSV", tracker)
    monkeypatch.setattr("scripts.track.data_path", _data_path)
    monkeypatch.setattr("scripts.job_info_io.data_path", _data_path)

    assert log_saved("acme_ml_2026", status="Saved") is True
    assert log_saved("acme_ml_2026", status="Saved") is False

    rows = _read_tracker()
    assert len(rows) == 1
    assert rows[0]["id"] == "acme_ml_2026"
    assert rows[0]["status"] == "Saved"
    assert rows[0]["company"] == "Acme"
    assert rows[0]["date_applied"] == ""


def test_cmd_update_sets_date_applied_when_becoming_applied(tmp_path, monkeypatch):
    from argparse import Namespace

    from scripts.track import cmd_update

    tracker = tmp_path / "applications" / "tracker.csv"
    tracker.parent.mkdir(parents=True)
    monkeypatch.setattr("scripts.track.TRACKER_CSV", tracker)

    assert log_saved("acme_ml_2026", company="Acme", role="ML", status="Saved") is True
    cmd_update(Namespace(id="acme_ml_2026", status="Applied", notes=None, recruiter=None))

    rows = _read_tracker()
    assert rows[0]["status"] == "Applied"
    assert rows[0]["date_applied"]  # filled on Applied
