"""Tests for scripts/build.py (engines mocked — no pdflatex)."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import build


@pytest.fixture
def build_paths(tmp_path, monkeypatch):
    monkeypatch.setattr(
        build,
        "document_py",
        lambda kind, jid: tmp_path / kind / "outputs" / (
            f"{jid}_cl.py" if kind == "coverletter" else f"{jid}.py"
        ),
    )
    monkeypatch.setattr(
        build,
        "document_tex",
        lambda kind, jid: tmp_path / kind / "outputs" / (
            f"{jid}_cl.tex" if kind == "coverletter" else f"{jid}.tex"
        ),
    )
    monkeypatch.setattr(build, "rel_to_root", lambda p: Path(p).as_posix())

    def resolve(kind, jid):
        stem = f"{jid}_cl" if kind == "coverletter" else jid
        src = tmp_path / kind / "outputs" / f"{stem}.py"
        tex = tmp_path / kind / "outputs" / f"{stem}.tex"
        if not src.exists():
            raise FileNotFoundError(src)
        return src, tex

    monkeypatch.setattr(build, "resolve_document_paths", resolve)
    return tmp_path


def _install_fake_engines(monkeypatch):
    class Eng:
        @staticmethod
        def generate_tex_file(s, t):
            p = Path(t)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("% tex\n", encoding="utf-8")
            return p

    import sys

    monkeypatch.setitem(sys.modules, "resume.cv2latex", Eng)
    monkeypatch.setitem(sys.modules, "coverletter.cl2latex", Eng)


def test_build_resume_missing_exits(build_paths):
    with pytest.raises(SystemExit):
        build.build_resume("missing_job")


def test_build_resume_calls_engine(build_paths, monkeypatch):
    src = build_paths / "resume" / "outputs" / "acme_ml_2026.py"
    src.parent.mkdir(parents=True)
    src.write_text("# resume\n", encoding="utf-8")
    tex = build_paths / "resume" / "outputs" / "acme_ml_2026.tex"
    _install_fake_engines(monkeypatch)

    out = build.build_resume("acme_ml_2026")
    assert out == tex
    assert tex.exists()


def test_build_coverletter_missing_returns_none(build_paths):
    assert build.build_coverletter("missing_job") is None


def test_main_bundle_implies_pdf_and_finalize(build_paths, monkeypatch):
    src = build_paths / "resume" / "outputs" / "acme_ml_2026.py"
    src.parent.mkdir(parents=True)
    src.write_text("# resume\n", encoding="utf-8")
    _install_fake_engines(monkeypatch)

    calls = {"pdf": [], "bundle": 0}
    monkeypatch.setattr(build, "compile_pdf", lambda p: calls["pdf"].append(p))
    monkeypatch.setattr(build, "bootstrap_paths", lambda args: False)
    monkeypatch.setattr(
        "scripts.bundle.finalize_bundle",
        lambda job_id: calls.__setitem__("bundle", calls["bundle"] + 1),
    )

    import sys

    monkeypatch.setattr(
        sys,
        "argv",
        ["build.py", "--id", "acme_ml_2026", "--only", "resume", "--bundle", "--public"],
    )

    build.main()
    assert len(calls["pdf"]) == 1
    assert calls["bundle"] == 1
