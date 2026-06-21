"""
profile/header.py
-----------------
Personal contact information — the single source of truth for your identity.

Covers both the CV header (HeaderInfo) and the cover letter sender block (CLHeader).
Update this file when your email, phone, address, or URLs change.

Agent instructions:
  - To update any contact field, edit the corresponding value below.
  - Both HEADER and CL_HEADER must be kept consistent (same name/email/LinkedIn).
  - After editing, append a line to profile/CHANGELOG.md.
"""

from resume.cv_utils import HeaderInfo
from coverletter.cl_utils import CLHeader

# ── CV Header ────────────────────────────────────────────────────────────────
# Appears in the resume PDF header.

HEADER = HeaderInfo(
    name           = "Jane Doe",
    email          = "jane.doe@example.com",
    phone_primary  = "+1 (555) 123-4567",
    phone_secondary= None,
    location       = "Example City, ST",
    linkedin_url   = "https://www.linkedin.com/in/janedoe/",
    github_url     = "https://github.com/janedoe",
    website_url    = None,
    leetcode_url   = "https://leetcode.com/u/janedoe/",
)

# ── Cover Letter Header ───────────────────────────────────────────────────────
# Appears in the cover letter sender block.

CL_HEADER = CLHeader(
    name                   = "Jane Doe",
    email                  = "jane.doe@example.com",
    linkedin_url           = "https://www.linkedin.com/in/janedoe/",
    address_street         = "123 Example Street",
    address_city_state_zip = "Example City, ST 12345",
    signature_image_path   = None,
)
