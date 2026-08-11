"""Dynamic education variable discovery for ai_tailor codegen."""

from __future__ import annotations

from scripts.ai_tailor import _education_var_names, generate_resume_file


def test_education_vars_in_generated_resume():
    names = _education_var_names()
    assert isinstance(names, list)
    jd = {"company": "Test Co", "role": "ML Engineer", "keywords": []}
    match = {
        "selected_experience": [],
        "selected_projects": [],
        "skills_preset": "SKILLS_ML_FOCUSED",
        "section_config": {},
        "summary": "Test summary.",
        "experience_overrides": {},
    }
    text = generate_resume_file("test_edu_job", jd, match)
    if names:
        for var in names:
            assert var in text
        # The education list must be exactly the live profile names — no stale
        # hardcoded variables from an older profile may appear.
        assert f"education   = [{', '.join(names)}]" in text
    else:
        assert "education   = []" in text
