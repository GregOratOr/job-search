from profile.header     import HEADER, CL_HEADER
from profile.education  import *
from profile.experience import *
from profile.projects   import *
from profile.skills     import *
from profile.summaries  import SUMMARIES
from profile.research   import *
from profile.coursework import *

# Re-exports everything for tailoring files.
# This is the single import point for tailoring files.

__all__ = [
    "HEADER", "CL_HEADER",

    "EXAMPLE_UNIV_MS", "EXAMPLE_UNIV_BTECH",

    # "EXAMPLE_ML_ENGINEER_ACME", "EXAMPLE_SWE_INTERN_STARTUP",

    # "PROJ_EXAMPLE_ML_PIPELINE", "PROJ_EXAMPLE_CUDA_KERNEL", "PROJ_EXAMPLE_WEB_APP",

    # "RESEARCH_EXAMPLE_RL",

    "SKILLS_FULL", "SKILLS_ML_FOCUSED", "SKILLS_SWE_FOCUSED", "SKILLS_RESEARCH_FOCUSED",

    "SUMMARIES",

    "COURSEWORK_EXAMPLE_MS", "COURSEWORK_EXAMPLE_BTECH",
]

EXPERIENCE_REGISTRY = {
    "EXAMPLE_ML_ENGINEER_ACME": EXAMPLE_ML_ENGINEER_ACME,
    "EXAMPLE_SWE_INTERN_STARTUP": EXAMPLE_SWE_INTERN_STARTUP,
}

PROJECT_REGISTRY = {
    "PROJ_EXAMPLE_ML_PIPELINE": PROJ_EXAMPLE_ML_PIPELINE,
    "PROJ_EXAMPLE_CUDA_KERNEL": PROJ_EXAMPLE_CUDA_KERNEL,
    "PROJ_EXAMPLE_WEB_APP": PROJ_EXAMPLE_WEB_APP,
}

RESEARCH_REGISTRY = {
    "RESEARCH_EXAMPLE_RL": RESEARCH_EXAMPLE_RL,
}

__all__.extend(EXPERIENCE_REGISTRY.keys())     #type:ignore
__all__.extend(PROJECT_REGISTRY.keys())        #type:ignore
__all__.extend(RESEARCH_REGISTRY.keys())       #type:ignore

