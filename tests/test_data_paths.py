"""data_paths routing tests."""

from __future__ import annotations

import argparse

import pytest

from scripts.data_paths import (
    ROOT,
    PRIVATE,
    add_overlay_cli_flags,
    bootstrap_paths,
    configure_overlay,
    data_path,
    document_pdf,
    document_py,
    document_tex,
    rel_to_root,
    resolve_document_paths,
    resolve_document_py,
    resolve_env_file,
    resolve_path,
    template_path,
    uses_private_data,
)


def test_data_path_under_root():
    p = data_path("applications", "tracker.csv")
    assert ROOT in p.parents or p.parent == ROOT


def test_resolve_path_prefers_existing_private_candidate():
    private_cfg = ROOT / "private" / "config" / "job_search_config.yaml"
    public_cfg = ROOT / "config" / "job_search_config.yaml"
    resolved = resolve_path("config", "job_search_config.yaml")
    if private_cfg.is_file():
        assert resolved == private_cfg
    else:
        assert resolved == public_cfg


def test_document_paths_use_outputs_and_respect_overlay():
    py = document_py("resume", "acme_ml_2026")
    tex = document_tex("resume", "acme_ml_2026")
    pdf = document_pdf("coverletter", "acme_ml_2026")
    cl_py = document_py("coverletter", "acme_ml_2026")
    assert py.name == "acme_ml_2026.py"
    assert tex.name == "acme_ml_2026.tex"
    assert pdf.name == "acme_ml_2026_cl.pdf"
    assert cl_py.name == "acme_ml_2026_cl.py"
    assert py.parent.name == "outputs"
    assert tex.parent.name == "outputs"
    if uses_private_data():
        assert PRIVATE in py.parents
        assert "private/resume/outputs/acme_ml_2026.tex" == rel_to_root(tex)
        assert "private/coverletter/outputs/acme_ml_2026_cl.py" == rel_to_root(cl_py)
    else:
        assert PRIVATE not in py.parents
        assert "resume/outputs/acme_ml_2026.tex" == rel_to_root(tex)
        assert "coverletter/outputs/acme_ml_2026_cl.py" == rel_to_root(cl_py)


def test_generate_resume_embeds_overlay_aware_output_path():
    from scripts.ai_tailor import generate_resume_file

    jd = {"company": "Test Co", "role": "ML Engineer", "keywords": []}
    match = {
        "selected_experience": [],
        "selected_projects": [],
        "skills_preset": "SKILLS_ML_FOCUSED",
        "section_config": {},
        "summary": "Test summary.",
        "experience_overrides": {},
    }
    text = generate_resume_file("path_check_job", jd, match)
    expected = rel_to_root(document_tex("resume", "path_check_job"))
    assert f'OUTPUT_FILE = "{expected}"' in text
    assert "resume/outputs/path_check_job.py" in text or "private/resume/outputs/path_check_job.py" in text


def test_configure_overlay_force_public_and_private():
    had_private = (PRIVATE / "profile").is_dir()
    try:
        configure_overlay(private=False)
        assert uses_private_data() is False
        assert data_path("resume", "outputs", "x.tex") == ROOT / "resume" / "outputs" / "x.tex"

        if had_private:
            configure_overlay(private=True)
            assert uses_private_data() is True
            assert data_path("resume", "outputs", "x.tex") == PRIVATE / "resume" / "outputs" / "x.tex"
    finally:
        configure_overlay(private=None)


def test_overlay_cli_flags_wire_to_bootstrap():
    parser = argparse.ArgumentParser()
    add_overlay_cli_flags(parser)
    args = parser.parse_args(["--public"])
    assert args.overlay is False
    try:
        active = bootstrap_paths(args)
        assert active is False
        assert uses_private_data() is False
    finally:
        configure_overlay(private=None)

    args = parser.parse_args([])
    assert args.overlay is None


def test_resolve_env_file_respects_force_flags():
    try:
        configure_overlay(private=False)
        env = resolve_env_file()
        if env is not None:
            assert env == ROOT / ".env"
            assert env.is_file()

        if (PRIVATE / "profile").is_dir():
            configure_overlay(private=True)
            env = resolve_env_file()
            if env is not None:
                assert env == PRIVATE / ".env"
                assert env.is_file()

        configure_overlay(private=None)
        env = resolve_env_file()
        if (PRIVATE / ".env").is_file():
            assert env == PRIVATE / ".env"
        elif (ROOT / ".env").is_file():
            assert env == ROOT / ".env"
        else:
            assert env is None
    finally:
        configure_overlay(private=None)


def test_template_path_points_at_scaffold():
    try:
        configure_overlay(private=False)
        p = template_path("resume")
        assert p == ROOT / "resume" / "tailoring" / "_template.py"
        assert p.is_file()
    finally:
        configure_overlay(private=None)


def test_resolve_document_py_outputs_then_legacy_then_missing():
    job_id = "_pytest_path_probe_2026"
    primary = ROOT / "resume" / "outputs" / f"{job_id}.py"
    legacy = ROOT / "resume" / "tailoring" / f"{job_id}.py"
    created: list = []
    try:
        configure_overlay(private=False)
        assert resolve_document_py("resume", job_id) is None
        with pytest.raises(FileNotFoundError, match="resume source not found"):
            resolve_document_paths("resume", job_id)

        legacy.parent.mkdir(parents=True, exist_ok=True)
        legacy.write_text("# pytest probe legacy\n", encoding="utf-8")
        created.append(legacy)
        assert resolve_document_py("resume", job_id) == legacy
        src, tex = resolve_document_paths("resume", job_id)
        assert src == legacy
        assert tex == ROOT / "resume" / "outputs" / f"{job_id}.tex"

        primary.parent.mkdir(parents=True, exist_ok=True)
        primary.write_text("# pytest probe primary\n", encoding="utf-8")
        created.append(primary)
        assert resolve_document_py("resume", job_id) == primary
        src, tex = resolve_document_paths("resume", job_id)
        assert src == primary
        assert tex.name == f"{job_id}.tex"
    finally:
        for path in created:
            if path.exists():
                path.unlink()
        configure_overlay(private=None)


def test_coverletter_uses_cl_suffix_with_pre_cl_fallback():
    job_id = "_pytest_cl_probe_2026"
    primary = ROOT / "coverletter" / "outputs" / f"{job_id}_cl.py"
    pre_cl = ROOT / "coverletter" / "outputs" / f"{job_id}.py"
    created: list = []
    try:
        configure_overlay(private=False)
        assert resolve_document_py("coverletter", job_id) is None

        pre_cl.parent.mkdir(parents=True, exist_ok=True)
        pre_cl.write_text("# pytest pre-_cl\n", encoding="utf-8")
        created.append(pre_cl)
        assert resolve_document_py("coverletter", job_id) == pre_cl
        src, tex = resolve_document_paths("coverletter", job_id)
        assert src == pre_cl
        assert tex.name == f"{job_id}_cl.tex"

        primary.write_text("# pytest primary _cl\n", encoding="utf-8")
        created.append(primary)
        assert resolve_document_py("coverletter", job_id) == primary
        src, tex = resolve_document_paths("coverletter", job_id)
        assert src == primary
        assert tex == ROOT / "coverletter" / "outputs" / f"{job_id}_cl.tex"
    finally:
        for path in created:
            if path.exists():
                path.unlink()
        configure_overlay(private=None)
