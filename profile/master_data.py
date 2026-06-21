"""
profile/master_data.py
======================
Re-exports everything from the focused sub-modules.

This is the single import point for tailoring files:
    from profile.master_data import *
"""

from profile.header     import HEADER, CL_HEADER
from profile.education  import EXAMPLE_UNIV_MS, EXAMPLE_UNIV_BTECH
from profile.experience import *
from profile.projects   import *
from profile.skills     import *
from profile.summaries  import SUMMARIES
from profile.research   import *
from profile.coursework import COURSEWORK_EXAMPLE_MS, COURSEWORK_EXAMPLE_BTECH

__all__ = [
    "HEADER", "CL_HEADER",
    "EXAMPLE_UNIV_MS", "EXAMPLE_UNIV_BTECH",
    "EXAMPLE_ML_ENGINEER_ACME", "EXAMPLE_SWE_INTERN_STARTUP",
    "PROJ_EXAMPLE_ML_PIPELINE", "PROJ_EXAMPLE_CUDA_KERNEL", "PROJ_EXAMPLE_WEB_APP",
    "RESEARCH_EXAMPLE_RL",
    "SKILLS_FULL", "SKILLS_ML_FOCUSED", "SKILLS_SWE_FOCUSED", "SKILLS_RESEARCH_FOCUSED",
    "SUMMARIES",
    "COURSEWORK_EXAMPLE_MS", "COURSEWORK_EXAMPLE_BTECH",
    "EXPERIENCE_REGISTRY", "PROJECT_REGISTRY", "RESEARCH_REGISTRY",
]

EXPERIENCE_REGISTRY: dict = {
    "EXAMPLE_ML_ENGINEER_ACME": EXAMPLE_ML_ENGINEER_ACME,
    "EXAMPLE_SWE_INTERN_STARTUP": EXAMPLE_SWE_INTERN_STARTUP,
}

PROJECT_REGISTRY: dict = {
    "PROJ_EXAMPLE_ML_PIPELINE": PROJ_EXAMPLE_ML_PIPELINE,
    "PROJ_EXAMPLE_CUDA_KERNEL": PROJ_EXAMPLE_CUDA_KERNEL,
    "PROJ_EXAMPLE_WEB_APP":    PROJ_EXAMPLE_WEB_APP,
}

RESEARCH_REGISTRY: dict = {
    "RESEARCH_EXAMPLE_RL": RESEARCH_EXAMPLE_RL,
}
