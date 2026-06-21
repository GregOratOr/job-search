"""
profile/education.py
--------------------
Education entries. One variable per degree, in reverse-chronological order.

Agent instructions:
  - To add a new degree: copy the template block, fill it in, give it a clear variable name.
  - To update coursework details: edit the `details` list of the relevant entry.
  - After editing, append a line to profile/CHANGELOG.md.
  - Variable naming convention: SCHOOL_DEGREE (e.g. MIT_PHD, EXAMPLE_UNIV_MS)
"""

from resume.cv_utils import EducationEntry

# ── Template (copy to add new entry) ─────────────────────────────────────────
# SCHOOL_DEGREE = EducationEntry(
#     institution = "",
#     location    = "",
#     date        = "",
#     degree      = "\\textit{Degree Name in Program}",
#     gpa         = "",   # leave "" to omit
#     details     = [
#         "\\textbf{Coursework:} ...",
#     ]
# )

# ── Entries (most recent first) ───────────────────────────────────────────────

EXAMPLE_UNIV_MS = EducationEntry(
    institution = "Example University",
    location    = "Example City, Example State, USA",
    date        = "September 2022 -- May 2024",
    degree      = "\\textit{Master of Science in Artificial Intelligence}",
    gpa         = "3.8/4.0",
    details     = [
        "\\textbf{Coursework:} Deep Learning, Computer Vision, Reinforcement Learning, "
        "Natural Language Processing, Machine Learning, Algorithms"
    ]
)

EXAMPLE_UNIV_BTECH = EducationEntry(
    institution = "Example Institute of Technology",
    location    = "Example City, Example Country",
    date        = "August 2018 -- June 2022",
    degree      = "\\textit{Bachelor of Technology in Computer Engineering}",
    gpa         = "8.5/10.0",
    details     = [
        "\\textbf{Coursework:} Data Structures, Algorithms, Data Science, "
        "Database Management Systems, Algorithms \\& Complexity"
    ]
)
