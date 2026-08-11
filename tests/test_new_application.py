"""Tests for scripts/new_application.py."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts import new_application as na


@pytest.fixture
def scaffold_env(tmp_path, monkeypatch):
    # Minimal public-style tree under tmp_path
    for kind in ("resume", "coverletter"):
        tpl_dir = tmp_path / kind / "tailoring"
        tpl_dir.mkdir(parents=True)
        (tpl_dir / "_template.py").write_text(
            'JOB_ID = "_template"\nCOMPANY = "Company Name"\nROLE = "Role Title"\n'
            'OUTPUT_FILE = "x.tex"\n',
            encoding="utf-8",
        )
    job_tpl = tmp_path / "applications" / "jobs" / "_template"
    job_tpl.mkdir(parents=True)
    (job_tpl / "job_info.py").write_text(
        '"""template"""\nJOB_ID   = "_template"\nCOMPANY  = "Company Name"\n'
        'ROLE     = "Role Title"\nSTATUS = "Applied"\n',
        encoding="utf-8",
    )

    monkeypatch.setattr(na, "data_path", lambda *p: tmp_path.joinpath(*p))
    monkeypatch.setattr(na, "document_py", lambda kind, jid: tmp_path / kind / "outputs" / (
        f"{jid}_cl.py" if kind == "coverletter" else f"{jid}.py"
    ))
    monkeypatch.setattr(na, "document_tex", lambda kind, jid: tmp_path / kind / "outputs" / (
        f"{jid}_cl.tex" if kind == "coverletter" else f"{jid}.tex"
    ))
    monkeypatch.setattr(
        na,
        "template_path",
        lambda kind: tmp_path / kind / "tailoring" / "_template.py",
    )
    monkeypatch.setattr(
        na,
        "resolve_path",
        lambda *p: tmp_path.joinpath(*p),
    )
    monkeypatch.setattr(na, "rel_to_root", lambda p: Path(p).as_posix())
    return tmp_path


def test_scaffold_writes_outputs_and_job_info(scaffold_env):
    na.scaffold("acme_ml_2026", "Acme", "ML Engineer", force=False)
    resume = scaffold_env / "resume" / "outputs" / "acme_ml_2026.py"
    cl = scaffold_env / "coverletter" / "outputs" / "acme_ml_2026_cl.py"
    info = scaffold_env / "applications" / "jobs" / "acme_ml_2026" / "job_info.py"
    assert resume.is_file()
    assert cl.is_file()
    assert info.is_file()
    assert 'JOB_ID = "acme_ml_2026"' in resume.read_text(encoding="utf-8")
    assert 'COMPANY  = "Acme"' in info.read_text(encoding="utf-8")
    assert 'ROLE     = "ML Engineer"' in info.read_text(encoding="utf-8")


def test_scaffold_refuses_overwrite_without_force(scaffold_env):
    na.scaffold("acme_ml_2026", "Acme", "ML Engineer", force=False)
    with pytest.raises(SystemExit):
        na.scaffold("acme_ml_2026", "Acme", "ML Engineer", force=False)


def test_scaffold_force_overwrites(scaffold_env):
    na.scaffold("acme_ml_2026", "Acme", "ML Engineer", force=False)
    na.scaffold("acme_ml_2026", "Acme", "Senior ML", force=True)
    info = (scaffold_env / "applications" / "jobs" / "acme_ml_2026" / "job_info.py").read_text(
        encoding="utf-8"
    )
    assert "Senior ML" in info


def test_scaffold_rejects_bad_id(scaffold_env):
    with pytest.raises(SystemExit):
        na.scaffold("bad-id!", "Acme", "ML", force=False)
