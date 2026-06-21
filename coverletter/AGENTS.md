# Cover Letter Subsystem Context

## File Map

```
coverletter/
├── cl_utils.py          # Dataclasses (CLHeader, RecipientInfo, JobInfo, etc.)
├── cl2latex.py          # Jinja2 → LaTeX engine
├── tailoring/
│   ├── _template.py     # Master template — copy to create a new version
│   └── {id}.py          # One file per job application
└── outputs/
    └── {id}.tex         # Generated LaTeX files (gitignored)
```

## Key Object: CoverLetter

```python
CoverLetter(
    header    = CL_HEADER,          # from cl_utils.py (personal address etc.)
    recipient = RecipientInfo(...),  # company name, dept, city
    job       = JobInfo(...),        # role title, posting ID
    content   = LetterContent(
        date_str   = "June 09, 2026",
        salutation = "Dear Hiring Manager,",
        paragraphs = ["Para 1...", "Para 2...", "Para 3..."],
        closing    = "Sincerely,",
    ),
    output_file = f"coverletter/outputs/{JOB_ID}.tex",
)
```

## Paragraph Structure (recommended)

1. **Opening**: Why you're excited about *this company* and *this specific role*.
   Mention 1 concrete thing about the company (product, research direction, mission).
2. **Evidence**: Your strongest relevant experience with a metric. Connect explicitly
   to the job description. Do not summarize the resume — add context or emphasis.
3. **Close**: Forward-looking sentence + call to action. Keep it confident but brief.

## Build Command

```bash
python scripts/build.py --id <id> --only coverletter
```

## Signature Image

Set `signature_image_path` in `cl_utils.py → CL_HEADER`.
Path is relative to the output `.tex` file location (`coverletter/outputs/`).
If no signature: set to `None` and the `\\includegraphics` line is skipped.

## Adding a New Field

1. Add field to the appropriate dataclass in `cl_utils.py`
2. Add the Jinja2 template tag in `LATEX_BODY` in `cl2latex.py`
3. Populate the field in tailoring files
