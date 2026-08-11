"""job_discovery.py — discovery library (no CLI)."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from scripts import job_discovery


def test_discover_jobs_requires_use_project_web():
    with pytest.raises(RuntimeError, match="use-project-web"):
        job_discovery.discover_jobs(None, 3, "m", {}, use_project_web=False)


def test_fetch_jd_without_flag_returns_none():
    assert job_discovery.fetch_jd("https://example.com", use_project_web=False) is None


_FIXTURE_CFG = {
    "profile": {"preferred_locations": ["Remote"]},
    "target_roles": {
        "primary": ["ML Engineer", "AI Engineer"],
        "secondary": ["Research Engineer"],
        "avoid": ["Data Analyst"],
    },
    "target_companies": {
        "tier_1": ["NVIDIA", "OpenAI"],
        "tier_2": ["Databricks"],
    },
    "search_terms": {
        "must_include_one_of": ["PyTorch", "CUDA", "LLM"],
        "nice_to_have": ["GPU"],
        "exclude": ["10+ years"],
    },
}


def test_build_queries_override():
    assert job_discovery._build_queries(_FIXTURE_CFG, "custom query") == ["custom query"]


def test_build_queries_includes_must_terms_and_companies():
    qs = job_discovery._build_queries(_FIXTURE_CFG, None)
    blob = " | ".join(qs)
    assert "PyTorch" in blob or "CUDA" in blob or "LLM" in blob
    assert "ML Engineer" in blob
    assert "NVIDIA" in blob
    assert "Remote" in blob
    assert len(qs) <= (
        job_discovery._MAX_ROLE_QUERIES + job_discovery._MAX_COMPANY_QUERIES
    )


def test_search_prefs_block_includes_config_terms():
    block = job_discovery._search_prefs_block(_FIXTURE_CFG)
    assert "PyTorch" in block
    assert "Data Analyst" in block
    assert "10+ years" in block
    assert "GPU" in block


def test_rank_candidates_prompt_includes_prefs():
    captured: dict[str, str] = {}

    def fake_call_json(system, user, model, **kwargs):
        captured["system"] = system
        captured["user"] = user
        return [{"company": "X", "role": "Y", "url": "https://ex.com/j", "relevance_score": 8}]

    cands = [{"title": "ML Eng", "url": "https://ex.com/j", "snippet": "PyTorch"}]
    with patch("scripts.job_discovery.call_json", fake_call_json):
        with patch.object(job_discovery, "_profile_summary", return_value="Candidate: Test"):
            out = job_discovery._rank_candidates(cands, 2, "m", _FIXTURE_CFG)

    assert len(out) == 1
    assert "SEARCH PREFERENCES" in captured["user"]
    assert "must include" in captured["user"].lower() or "PyTorch" in captured["user"]
