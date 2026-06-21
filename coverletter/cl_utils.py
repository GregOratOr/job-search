"""
coverletter/cl_utils.py
-----------------------
Dataclass definitions for the cover letter system.

RULE: No personal data here. All content lives in profile/master_data.py
      or in a tailoring file.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CLHeader:
    """Sender's personal details for the cover letter."""
    name:                  str
    email:                 str
    linkedin_url:          str
    address_street:        str    # e.g. "426 NW 11th ST"
    address_city_state_zip: str   # e.g. "Corvallis, OR-97330"
    signature_image_path:  Optional[str] = None  # e.g. "../signature.png"


@dataclass
class RecipientInfo:
    company_name:       str
    department_or_area: str
    city_state_zip:     str


@dataclass
class JobInfo:
    title:  str
    job_id: Optional[str] = None


@dataclass
class LetterContent:
    date_str:   str          # e.g. "June 09, 2026"
    salutation: str          # e.g. "Dear Hiring Manager,"
    paragraphs: List[str]    # Each paragraph is a string (no newlines inside)
    closing:    str          # e.g. "Sincerely,"


@dataclass
class CoverLetter:
    header:    CLHeader
    recipient: RecipientInfo
    job:       JobInfo
    content:   LetterContent
    output_file: str = ""


# CL_HEADER has moved to profile/header.py — import it from there:
#   from profile.header import CL_HEADER
