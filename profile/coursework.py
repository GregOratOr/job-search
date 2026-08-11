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
        "Course 1",
        "Course 2",
        "Course 3"
    ]
)

COURSEWORK_EXAMPLE_BTECH = CourseworkEntry(
    title        = "Example Institute of Technology --- B.Tech Computer Engineering",
    use_multicol = True,
    courses      = [
        "Course 1",
        "Course 2",
        "Course 3"
    ]
)
