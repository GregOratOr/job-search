"""Tests for scripts/job_info_io.py."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from scripts.job_info_io import load_job_info, set_job_info_fields


SAMPLE_JOB_INFO = '''\
"""
applications/jobs/test_job/job_info.py
"""

JOB_ID   = "test_job"
COMPANY  = "Acme"
ROLE     = "ML Engineer"

PLATFORM    = ""
URL         = ""
JOB_ID_EXT  = None
REFERRAL    = None
RECRUITER   = None

LOCATION       = ""
VISA_SPONSORED = None
SALARY_RANGE   = ""
TEAM           = ""

NOTES = "Auto-tailored by ai_tailor.py"

KEYWORDS = []

NETWORKING_TARGETS = []
INTERVIEW_FORMAT   = ""
PREP_RESOURCES     = []
'''


@pytest.fixture
def job_info_file(tmp_path, monkeypatch):
    job_dir = tmp_path / "applications" / "jobs" / "test_job"
    job_dir.mkdir(parents=True)
    path = job_dir / "job_info.py"
    path.write_text(SAMPLE_JOB_INFO, encoding="utf-8")

    def _data_path(*parts: str) -> Path:
        return tmp_path.joinpath(*parts)

    monkeypatch.setattr("scripts.job_info_io.data_path", _data_path)
    return path


def test_set_url_with_quotes(job_info_file):
    tricky = 'https://example.com/jobs?id="1"&ref=foo'
    set_job_info_fields("test_job", url=tricky)
    text = job_info_file.read_text(encoding="utf-8")
    assert "URL" in text
    spec = importlib.util.spec_from_file_location("ji", str(job_info_file))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.URL == tricky


def test_set_url_whitespace_tolerant(job_info_file):
    job_info_file.write_text(
        job_info_file.read_text().replace('URL         = ""', 'URL = ""'),
        encoding="utf-8",
    )
    set_job_info_fields("test_job", url="https://jobs.example.com/123")
    info = load_job_info("test_job")
    assert info["url"] == "https://jobs.example.com/123"


def test_load_job_info_missing_file_returns_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "scripts.job_info_io.data_path",
        lambda *parts: tmp_path.joinpath(*parts),
    )
    assert load_job_info("does_not_exist") == {}


def test_set_job_info_fields_missing_file_raises(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "scripts.job_info_io.data_path",
        lambda *parts: tmp_path.joinpath(*parts),
    )
    with pytest.raises(FileNotFoundError, match="job_info.py not found"):
        set_job_info_fields("does_not_exist", url="https://example.com")


def test_set_platform_and_insert_missing_field(job_info_file):
    text = job_info_file.read_text(encoding="utf-8")
    # Drop PLATFORM so _replace_field must insert after ROLE.
    text = "\n".join(line for line in text.splitlines() if not line.startswith("PLATFORM"))
    job_info_file.write_text(text + "\n", encoding="utf-8")

    set_job_info_fields("test_job", platform="LinkedIn")
    info = load_job_info("test_job")
    assert info["platform"] == "LinkedIn"
    assert "PLATFORM" in job_info_file.read_text(encoding="utf-8")
