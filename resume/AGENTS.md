# Resume Subsystem Context

## File Map

```
resume/
├── cv_utils.py          # Dataclass and Enum definitions ONLY — no personal data
├── cv2latex.py          # Jinja2 → LaTeX engine; do not edit for tailoring
├── tailoring/
│   └── _template.py     # Scaffold template — copied into outputs/{id}.py
└── outputs/
    ├── {id}.py          # Per-job source (select + replace)
    ├── {id}.tex         # Generated LaTeX (gitignored)
    └── {id}.pdf         # Compiled PDF (gitignored)
```

## Key Conventions

- Per-job files expose a `cv_data` variable of type `CV`.
- Paths are overlay-aware: with `private/` present they live under `private/resume/outputs/`.
- `build.py` always writes `.tex` via `data_path` (never the public tree when overlay is on).
- Use `dataclasses.replace(ENTRY, highlights=[...])` for per-job bullet overrides.
- After `--bundle`, `.py` / `.tex` / `.pdf` move into `applications/jobs/{id}/` as `{id}_resume.*`.

## Writing Override Bullets

Reworded `highlights` must follow the style guide. Full rules (Harvard guidelines, complete
action-verb bank, per-section tips) are in `docs/resume-writing-reference.md`; the root
`AGENTS.md` has a condensed recap. In short: XYZ formula ("Accomplished [X], as measured by
[Y], by doing [Z]"), strong action verb first, quantified result last, active voice, no
pronouns, under ~200 chars, key terms in `\\textbf{...}`. Rewrite to hit the JD's keywords
without inventing facts.

## Build Command

```bash
uv run scripts/build.py --id <id>                   # generate .tex beside the .py
uv run scripts/build.py --id <id> --pdf             # also compile to PDF
uv run scripts/build.py --id <id> --bundle          # pdf + move .py/.tex/.pdf into the job bundle
uv run scripts/build.py --id <id> --private --pdf   # force private/ paths
uv run resume/cv2latex.py --id <id> --private       # engine-only, same path routing
```

## Common LaTeX Pitfalls

Escape these characters in bullet point strings:
- `&` → `\\&` (e.g. "Weights \\& Biases")
- `%` → `\\%` (e.g. "reduced cost by 40\\%")
- `_` → `\\_` (e.g. "model\\_name")
- `#` → `\\#`
- `$` → `\\$`

## Adding a New Section

1. Add a `show_*: bool` to `SectionConfig` in `cv_utils.py`
2. Add the `\newboolean{show*}` and `\setboolean{}` block in `LATEX_PREAMBLE` in `cv2latex.py`
3. Add the `\ifthenelse{\boolean{show*}}{...}{}` block in `LATEX_BODY`
4. Add the corresponding field to the `CV` dataclass in `cv_utils.py`
5. Export the new field from `profile/master_data.py`

## Modifying the LaTeX Layout

- Margins: edit the `geometry` package options in `LATEX_PREAMBLE`
- Font size: change `[10pt, letterpaper]` in `\\documentclass`
- Column widths: edit `\setcolumnwidth{\fill, 5.6 cm}` in the `twocolentry` environment
- Section spacing: edit `\titlespacing{\section}` values
