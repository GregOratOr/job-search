"""
resume/tailoring/example_acme_ml_2026.py
=========================================
Worked example — Acme AI Labs Machine Learning Engineer.

Build:  python scripts/build.py --id example_acme_ml_2026
"""

from dataclasses import replace
from resume.cv_utils import SectionConfig, PositionInfo, CV
from profile.master_data import (
    HEADER, EXAMPLE_UNIV_MS, EXAMPLE_UNIV_BTECH,
    SKILLS_ML_FOCUSED,
    EXAMPLE_ML_ENGINEER_ACME, EXAMPLE_SWE_INTERN_STARTUP,
    PROJ_EXAMPLE_CUDA_KERNEL, PROJ_EXAMPLE_ML_PIPELINE,
    SUMMARIES,
)

JOB_ID      = "example_acme_ml_2026"
COMPANY     = "Acme AI Labs"
ROLE        = "Machine Learning Engineer"
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
    replace(EXAMPLE_ML_ENGINEER_ACME, highlights=[
        "Developed \\textbf{CUDA C++ kernels} for transformer attention; profiled with "
        "\\textbf{Nsight Compute}, achieving 2.1$\\times$ throughput improvement on A100 GPUs.",
        "Designed \\textbf{PyTorch DDP} training pipeline across 8 GPUs; reduced per-iteration "
        "wall-clock time by 35\\% via gradient bucketing and async all-reduce.",
    ]),
    EXAMPLE_SWE_INTERN_STARTUP,
]

PROJECTS = [
    PROJ_EXAMPLE_CUDA_KERNEL,
    PROJ_EXAMPLE_ML_PIPELINE,
]

SUMMARY = (
    "ML Engineer with an M.S. in AI and hands-on experience building "
    "\\textbf{CUDA kernels}, optimizing transformer inference, and deploying PyTorch models "
    "to production. Proficient in GPU profiling, ONNX export, and distributed training."
)

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
