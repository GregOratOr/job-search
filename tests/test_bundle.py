"""Tests for scripts/bundle.py."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts import bundle


@pytest.fixture
def bundle_paths(tmp_path, monkeypatch):
    def data_path(*parts: str) -> Path:
        return tmp_path.joinpath(*parts)

    monkeypatch.setattr(bundle, "data_path", data_path)
    monkeypatch.setattr(
        bundle,
        "document_py",
        lambda kind, jid: tmp_path / kind / "outputs" / (
            f"{jid}_cl.py" if kind == "coverletter" else f"{jid}.py"
        ),
    )
    monkeypatch.setattr(
        bundle,
        "document_tex",
        lambda kind, jid: tmp_path / kind / "outputs" / (
            f"{jid}_cl.tex" if kind == "coverletter" else f"{jid}.tex"
        ),
    )
    monkeypatch.setattr(
        bundle,
        "document_pdf",
        lambda kind, jid: tmp_path / kind / "outputs" / (
            f"{jid}_cl.pdf" if kind == "coverletter" else f"{jid}.pdf"
        ),
    )
    monkeypatch.setattr(
        bundle,
        "document_stem",
        lambda kind, jid: f"{jid}_cl" if kind == "coverletter" else jid,
    )
    monkeypatch.setattr(bundle, "rel_to_root", lambda p: Path(p).as_posix())
    return tmp_path


def test_finalize_renames_to_id_prefix(bundle_paths):
    jid = "acme_ml_2026"
    for kind, label in (("resume", "resume"), ("coverletter", "cover_letter")):
        out = bundle_paths / kind / "outputs"
        out.mkdir(parents=True)
        stem = f"{jid}_cl" if kind == "coverletter" else jid
        for suffix in (".py", ".tex", ".pdf"):
            (out / f"{stem}{suffix}").write_text("x", encoding="utf-8")
        (out / f"{stem}.aux").write_text("temp", encoding="utf-8")

    dest = bundle.finalize_bundle(jid)
    assert dest == bundle_paths / "applications" / "jobs" / jid

    for label in ("resume", "cover_letter"):
        for suffix in (".py", ".tex", ".pdf"):
            assert (dest / f"{jid}_{label}{suffix}").exists()
            stem = f"{jid}_cl" if label == "cover_letter" else jid
            kind = "coverletter" if label == "cover_letter" else "resume"
            assert not (bundle_paths / kind / "outputs" / f"{stem}{suffix}").exists()

    assert not (bundle_paths / "resume" / "outputs" / f"{jid}.aux").exists()
    assert not (bundle_paths / "coverletter" / "outputs" / f"{jid}_cl.aux").exists()


def test_finalize_skips_missing_kind(bundle_paths):
    jid = "solo_resume_2026"
    out = bundle_paths / "resume" / "outputs"
    out.mkdir(parents=True)
    (out / f"{jid}.pdf").write_text("pdf", encoding="utf-8")

    dest = bundle.finalize_bundle(jid)
    assert (dest / f"{jid}_resume.pdf").exists()
    assert not (dest / f"{jid}_cover_letter.pdf").exists()


def test_keep_temp_leaves_aux(bundle_paths):
    jid = "keep_temp_2026"
    out = bundle_paths / "resume" / "outputs"
    out.mkdir(parents=True)
    (out / f"{jid}.pdf").write_text("pdf", encoding="utf-8")
    (out / f"{jid}.aux").write_text("temp", encoding="utf-8")

    bundle.finalize_bundle(jid, keep_temp=True)
    assert (out / f"{jid}.aux").exists()


def test_rerun_uses_shared_postfix(bundle_paths):
    jid = "acme_ml_2026"
    dest = bundle_paths / "applications" / "jobs" / jid
    dest.mkdir(parents=True)
    (dest / f"{jid}_resume.pdf").write_text("old", encoding="utf-8")
    (dest / f"{jid}_resume.py").write_text("old", encoding="utf-8")

    out = bundle_paths / "resume" / "outputs"
    out.mkdir(parents=True)
    for suffix in (".py", ".tex", ".pdf"):
        (out / f"{jid}{suffix}").write_text("new", encoding="utf-8")

    bundle.finalize_bundle(jid)

    assert (dest / f"{jid}_resume.pdf").read_text(encoding="utf-8") == "old"
    for suffix in (".py", ".tex", ".pdf"):
        assert (dest / f"{jid}_resume (1){suffix}").read_text(encoding="utf-8") == "new"


def test_rerun_bumps_past_existing_postfix(bundle_paths):
    jid = "acme_ml_2026"
    dest = bundle_paths / "applications" / "jobs" / jid
    dest.mkdir(parents=True)
    (dest / f"{jid}_resume.pdf").write_text("v0", encoding="utf-8")
    (dest / f"{jid}_resume (1).pdf").write_text("v1", encoding="utf-8")

    out = bundle_paths / "resume" / "outputs"
    out.mkdir(parents=True)
    (out / f"{jid}.pdf").write_text("v2", encoding="utf-8")

    bundle.finalize_bundle(jid)
    assert (dest / f"{jid}_resume (2).pdf").read_text(encoding="utf-8") == "v2"
