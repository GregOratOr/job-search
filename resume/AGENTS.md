# Resume Subsystem Context

## File Map

```
resume/
├── cv_utils.py          # Dataclass and Enum definitions ONLY — no personal data
├── cv2latex.py          # Jinja2 → LaTeX engine; do not edit for tailoring
├── tailoring/
│   ├── _template.py     # Master template — copy to create a new version
│   └── {id}.py          # One file per job application
└── outputs/
    └── {id}.tex         # Generated LaTeX files (gitignored)
```

## Key Conventions

- Tailoring files expose a `cv_data` variable of type `CV`.
- The `active` flag on `ExperienceEntry`/`ProjectEntry` is set to `True` by default in master_data. Control visibility by **selecting** entries in the tailoring file list, not by setting `active=False`.
- Use `dataclasses.replace(ENTRY, highlights=[...])` for per-job bullet overrides.
- `OUTPUT_FILE` in every tailoring file must be `f"resume/outputs/{JOB_ID}.tex"`.

## Writing Override Bullets

Reworded `highlights` must follow the style guide. Full rules (Harvard guidelines, complete
action-verb bank, per-section tips) are in `docs/resume-writing-reference.md`; the root
`AGENTS.md` has a condensed recap. In short: XYZ formula ("Accomplished [X], as measured by
[Y], by doing [Z]"), strong action verb first, quantified result last, active voice, no
pronouns, under ~200 chars, key terms in `\\textbf{...}`. Rewrite to hit the JD's keywords
without inventing facts.

## Build Command

```bash
python scripts/build.py --id <id>            # generate .tex
python scripts/build.py --id <id> --pdf      # also compile to PDF
```

## Common LaTeX Pitfalls

Escape these characters in bullet point strings:
- `&`  →  `\\&`     (e.g. "Weights \\& Biases")
- `%`  →  `\\%`     (e.g. "reduced cost by 40\\%")
- `_`  →  `\\_`     (e.g. "model\\_name")
- `#`  →  `\\#`
- `$`  →  `\\$`

## Adding a New Section

1. Add a `show_*: bool` to `SectionConfig` in `cv_utils.py`
2. Add a `\newboolean{show*}` and `\setboolean{}` block in `LATEX_PREAMBLE` in `cv2latex.py`
3. Add the `\ifthenelse{\boolean{show*}}{...}{}` block in `LATEX_BODY`
4. Add the corresponding field to the `CV` dataclass in `cv_utils.py`
5. Export the new field from `profile/master_data.py`

## Modifying the LaTeX Layout

- Margins: edit the `geometry` package options in `LATEX_PREAMBLE`
- Font size: change `[10pt, letterpaper]` in `\\documentclass`
- Column widths: edit `\setcolumnwidth{\fill, 5.6 cm}` in the `twocolentry` environment
- Section spacing: edit `\titlespacing{\section}` values
