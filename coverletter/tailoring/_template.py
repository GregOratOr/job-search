"""
coverletter/tailoring/_template.py
====================================
COVER LETTER TAILORING INTERFACE
"""

import datetime
from coverletter.cl_utils import CoverLetter, RecipientInfo, JobInfo, LetterContent
from profile.header import CL_HEADER

JOB_ID     = "_template"
COMPANY    = "Company Name"
ROLE       = "Role Title"
DEPT       = "Engineering / Recruiting"
CITY       = "City, State ZIP"
POSTING_ID = None

OUTPUT_FILE = f"coverletter/outputs/{JOB_ID}.tex"

PARAGRAPHS = [
    (
        "I am writing to apply for the {role} position at {company}. "
        "Having completed my M.S. in Artificial Intelligence with a focus on "
        "deep learning and GPU systems, I am drawn to {company}'s "
        "commitment to [specific company mission or product area]."
    ).format(role=ROLE, company=COMPANY),

    (
        "During my recent work, I [key achievement with metric]. Additionally, "
        "I [second key achievement]. These experiences gave me hands-on practice with "
        "PyTorch, CUDA, and production ML pipelines — directly aligned with the "
        "requirements in your posting."
    ),

    (
        "I would welcome the opportunity to discuss how my background can contribute "
        "to {company}. Thank you for your time and consideration."
    ).format(company=COMPANY),
]

cl_data = CoverLetter(
    header    = CL_HEADER,
    recipient = RecipientInfo(
        company_name       = COMPANY,
        department_or_area = DEPT,
        city_state_zip     = CITY,
    ),
    job     = JobInfo(title=ROLE, job_id=POSTING_ID),
    content = LetterContent(
        date_str   = datetime.date.today().strftime("%B %d, %Y"),
        salutation = "Dear Hiring Manager,",
        paragraphs = PARAGRAPHS,
        closing    = "Sincerely,",
    ),
    output_file = OUTPUT_FILE,
)

if __name__ == "__main__":
    import coverletter.cl2latex as engine
    engine.generate_tex_file(__file__, OUTPUT_FILE)
