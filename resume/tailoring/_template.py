"""
resume/tailoring/_template.py
==============================
TAILORING INTERFACE — the only file you touch per job application.

Copy this file:
    python scripts/new_application.py --id <id> --company <co> --role <role>

Then edit the 5 numbered sections below. Nothing else needs to change.
"""

from dataclasses import replace
from resume.cv_utils import SectionConfig, PositionInfo, CV
from profile.master_data import (
    HEADER,
    EXAMPLE_UNIV_MS, EXAMPLE_UNIV_BTECH,
    SKILLS_FULL, SKILLS_ML_FOCUSED, SKILLS_SWE_FOCUSED, SKILLS_RESEARCH_FOCUSED,
    EXAMPLE_ML_ENGINEER_ACME, EXAMPLE_SWE_INTERN_STARTUP,
    PROJ_EXAMPLE_ML_PIPELINE, PROJ_EXAMPLE_CUDA_KERNEL, PROJ_EXAMPLE_WEB_APP,
    RESEARCH_EXAMPLE_RL,
    COURSEWORK_EXAMPLE_MS, COURSEWORK_EXAMPLE_BTECH,
    SUMMARIES,
)

JOB_ID      = "_template"
COMPANY     = "Company Name"
ROLE        = "Role Title"
OUTPUT_FILE = f"resume/outputs/{JOB_ID}.tex"

CONFIG = SectionConfig(
    show_position_applied = True,
    show_summary          = True,
    show_skills           = True,
    show_experience       = True,
    show_projects         = True,
    show_research         = False,
    show_education        = True,
    show_coursework       = False,
)

EXPERIENCE = [
    EXAMPLE_ML_ENGINEER_ACME,
    EXAMPLE_SWE_INTERN_STARTUP,
]

PROJECTS = [
    PROJ_EXAMPLE_ML_PIPELINE,
    PROJ_EXAMPLE_CUDA_KERNEL,
]

SUMMARY = SUMMARIES["ml_engineer"]

cv_data = CV(
    config      = CONFIG,
    header      = HEADER,
    position    = PositionInfo(role=ROLE),
    summary     = SUMMARY,
    education   = [EXAMPLE_UNIV_MS, EXAMPLE_UNIV_BTECH],
    skills      = SKILLS_ML_FOCUSED,
    experience  = EXPERIENCE,
    projects    = PROJECTS,
    research    = [],
    coursework  = [],
    output_file = OUTPUT_FILE,
)

if __name__ == "__main__":
    import resume.cv2latex as engine
    engine.generate_tex_file(__file__, OUTPUT_FILE)
