"""
profile/experience.py
---------------------
Work experience and internship entries. This is the file you'll update most often.

Agent instructions:
  - To add a new role: copy the template block below, fill it in, pick a variable name.
  - Variable naming: COMPANY_ROLE_YEAR (e.g. ACME_ML_2026, STARTUP_INTERN_2024)
  - Write bullet points in past tense with action verb + context + metric.
  - Escape LaTeX special chars: % → \\%   & → \\&   $ → \\$   _ → \\_
  - After adding/editing, append a line to profile/CHANGELOG.md.
  - Keep ALL entries here even after leaving a job — tailoring files select what appears.
"""

from resume.cv_utils import ExperienceEntry

# ── Template (copy to add new entry) ─────────────────────────────────────────
# COMPANY_ROLE_YEAR = ExperienceEntry(
#     role    = "",
#     company = "",
#     date    = "Mon YYYY -- Mon YYYY",   # or "Mon YYYY -- Present"
#     highlights = [
#         "Action verb + what + tools + metric/impact.",
#         "Action verb + what + tools + metric/impact.",
#     ]
# )

# ── Entries (most recent first) ───────────────────────────────────────────────

EXAMPLE_ML_ENGINEER_ACME = ExperienceEntry(
    role    = "Machine Learning Engineer",
    company = "Acme AI Labs",
    date    = "Jan 2024 -- Present",
    highlights = [
        "Built \\textbf{PyTorch} training pipelines for vision models; improved validation "
        "accuracy by 12\\% through data augmentation and learning-rate scheduling.",
        "Deployed models via \\textbf{FastAPI} and \\textbf{Docker}; reduced P95 inference "
        "latency from 45ms to 18ms using ONNX Runtime and batching.",
        "Profiled GPU kernels with \\textbf{Nsight Compute}; optimized memory access patterns "
        "to cut peak VRAM usage by 30\\%.",
    ]
)

EXAMPLE_SWE_INTERN_STARTUP = ExperienceEntry(
    role    = "Software Engineering Intern",
    company = "Example Startup Inc.",
    date    = "Jun 2023 -- Aug 2023",
    highlights = [
        "Implemented REST APIs in \\textbf{Python/FastAPI} serving 200+ req/s with automated "
        "pytest coverage above 85\\%.",
        "Added CI/CD pipeline with GitHub Actions; cut deployment time from 20 minutes to 5.",
    ]
)
