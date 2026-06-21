"""
profile/coursework.py
---------------------
Coursework section entries.
"""

from resume.cv_utils import CourseworkEntry

COURSEWORK_EXAMPLE_MS = CourseworkEntry(
    title        = "Example University --- M.S. Artificial Intelligence",
    use_multicol = True,
    courses      = [
        "Deep Learning",
        "Computer Vision",
        "Natural Language Processing",
        "Machine Learning",
        "Multiagent Systems",
        "Algorithms",
    ]
)

COURSEWORK_EXAMPLE_BTECH = CourseworkEntry(
    title        = "Example Institute of Technology --- B.Tech Computer Engineering",
    use_multicol = True,
    courses      = [
        "Data Structures",
        "Algorithms",
        "Data Science",
        "Database Management",
        "Operating Systems",
        "Linear Algebra",
    ]
)
