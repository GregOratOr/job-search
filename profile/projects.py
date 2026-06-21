"""
profile/projects.py
-------------------
Personal and academic project entries.

Agent instructions:
  - To add a new project: copy the template block, fill it in.
  - Variable naming: PROJ_{SHORT_NAME} (e.g. PROJ_EXAMPLE_ML_PIPELINE)
  - After adding/editing, append a line to profile/CHANGELOG.md.
"""

from resume.cv_utils import ProjectEntry

# ── Template (copy to add new entry) ─────────────────────────────────────────
# PROJ_NAME = ProjectEntry(
#     title        = "",
#     organization = "Personal Project | University Name | etc.",
#     date         = "Mon YYYY -- Mon YYYY",
#     aim          = None,
#     highlights   = [
#         "Bullet 1.",
#         "Bullet 2.",
#     ]
# )

# ── Entries (most impactful first) ────────────────────────────────────────────

PROJ_EXAMPLE_ML_PIPELINE = ProjectEntry(
    title="End-to-End ML Training Pipeline",
    organization="Personal Project",
    date="January 2024 -- March 2024",
    aim=None,
    highlights=[
        "Engineered a modular \\textbf{PyTorch} training pipeline with YAML-driven configuration, "
        "supporting mixed-precision training and checkpoint resume.",
        "Integrated \\textbf{Weights \\& Biases} for experiment tracking; ran 50+ ablation "
        "experiments comparing optimizers and augmentation strategies.",
        "Containerized training and inference with \\textbf{Docker}; deployed a \\textbf{FastAPI} "
        "serving endpoint with sub-20ms P95 latency.",
    ]
)

PROJ_EXAMPLE_CUDA_KERNEL = ProjectEntry(
    title="GPU-Accelerated Matrix Operations with CUDA",
    organization="Example University",
    date="September 2023 -- December 2023",
    aim=None,
    highlights=[
        "Implemented tiled \\textbf{GEMM kernels} in \\textbf{CUDA C++}, achieving 2$\\times$ "
        "throughput over naive implementations on an RTX 3080.",
        "Profiled kernels with \\textbf{Nsight Compute}; resolved bank conflicts and coalescing "
        "issues to reduce kernel runtime by 40\\%.",
    ]
)

PROJ_EXAMPLE_WEB_APP = ProjectEntry(
    title="Full-Stack Web Application",
    organization="Personal Project",
    date="June 2023 -- August 2023",
    aim=None,
    highlights=[
        "Built a responsive web app with \\textbf{Next.js} and \\textbf{TypeScript}, using "
        "server-side rendering for fast initial page loads.",
        "Configured CI/CD via GitHub Actions; automated testing and deployment to a cloud host.",
    ]
)
