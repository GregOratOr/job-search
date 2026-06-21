"""
profile/research.py
-------------------
Research entries (papers, thesis work, lab publications).
"""

from resume.cv_utils import ResearchEntry

# ── Template (copy to add new entry) ─────────────────────────────────────────
# RESEARCH_TOPIC_YEAR = ResearchEntry(
#     title           = "",
#     organization    = "",
#     date            = "Mon YYYY -- Mon YYYY",
#     highlights      = ["Bullet 1.", "Bullet 2."],
#     publication_url = None,
# )

RESEARCH_EXAMPLE_RL = ResearchEntry(
    title="Graduate Research — Multi-Agent Reinforcement Learning",
    organization="Example University AI Lab",
    date="January 2024 -- December 2024",
    highlights=[
        "Designed a custom \\textbf{multi-agent grid environment} using \\textbf{OpenAI Gym}, "
        "modeling cooperative agents under sparse global rewards.",
        "Implemented \\textbf{intrinsic reward} mechanisms including curiosity-driven exploration "
        "to drive emergent coordination without explicit communication.",
        "Benchmarked \\textbf{MAPPO} and \\textbf{IPPO} training frameworks across 100+ seeds.",
    ],
    publication_url=None,
)
