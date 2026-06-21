"""
coverletter/cl2latex.py
-----------------------
LaTeX generation engine for cover letters.

Usage:
    python coverletter/cl2latex.py --data coverletter/tailoring/google_swe_2026.py
"""

import sys
import argparse
import importlib.util
from pathlib import Path
from jinja2 import Environment, BaseLoader

# ==========================================
# LATEX PREAMBLE
# ==========================================

LATEX_PREAMBLE = r"""
\documentclass[10pt, letterpaper]{article}
\usepackage{ifthen}
\usepackage{graphicx}
\usepackage[
    ignoreheadfoot,
    top=1 cm,
    bottom=1 cm,
    left=1 cm,
    right=1 cm,
    footskip=1.0 cm,
]{geometry}
\usepackage{titlesec}
\usepackage{tabularx}
\usepackage{array}
\usepackage[dvipsnames]{xcolor}
\definecolor{primaryColor}{RGB}{0, 0, 0}
\usepackage{enumitem}
\usepackage{fontawesome5}
\usepackage{amsmath}
\usepackage[
    pdftitle={Cover Letter},
    pdfauthor={((= cl.header.name =))},
    pdfcreator={},
    colorlinks=true,
    linkcolor=blue,
    urlcolor=purple,
    filecolor=cyan,
    citecolor=green,
    menucolor=red,
    anchorcolor=black,
    runcolor=cyan,
    pdfview=Fit
]{hyperref}
\usepackage[pscoord]{eso-pic}
\usepackage{calc}
\usepackage{bookmark}
\usepackage{lastpage}
\usepackage{changepage}
\usepackage{paracol}
\usepackage{ifthen}
\usepackage{needspace}
\usepackage{iftex}
\usepackage{multicol}

\ifPDFTeX
    \input{glyphtounicode}
    \pdfgentounicode=1
    \usepackage[T1]{fontenc}
    \usepackage[utf8]{inputenc}
    \usepackage{lmodern}
\fi

\usepackage{charter}

\raggedright
\AtBeginEnvironment{adjustwidth}{\partopsep0 pt}
\pagestyle{empty}
\setcounter{secnumdepth}{0}
\setlength{\parindent}{0 pt}
\setlength{\topskip}{0 pt}
\setlength{\columnsep}{0.15 cm}
\pagenumbering{gobble}

\titleformat{\section}{\needspace{4\baselineskip}\bfseries\centering}{}{0pt}{}[\vspace{0.01 cm}\titlerule]
\titlespacing{\section}{-1 pt}{0.2 cm}{0.1 cm}

\renewcommand\labelitemi{$\vcenter{\hbox{\small$\bullet$}}$}

\newenvironment{onecolentry}{
    \begin{adjustwidth}{0 cm + 0.00001 cm}{0 cm + 0.00001 cm}
}{\end{adjustwidth}}

\newenvironment{twocolentry}[2][]{
    \onecolentry
    \def\secondColumn{#2}
    \setcolumnwidth{\fill, 5.5 cm}
    \begin{paracol}{2}
}{
    \switchcolumn \raggedleft \secondColumn
    \end{paracol}
    \endonecolentry
}

\let\hrefWithoutArrow\href
\usepackage{helvet}
\renewcommand{\familydefault}{\sfdefault}
\newcommand{\nline}{\hfill \break}

\title{Cover Letter}
\author{((= cl.header.name =))}
"""

# ==========================================
# LATEX BODY
# ==========================================

LATEX_BODY = r"""
\begin{document}

\textbf{((= cl.header.name =))}\\
\hrefWithoutArrow{mailto:((= cl.header.email =))}{((= cl.header.email =))} | \href{((= cl.header.linkedin_url =))}{LinkedIn}\\
((= cl.header.address_street =)),\\
((= cl.header.address_city_state_zip =))\\
\nline
((= cl.content.date_str =))\\
\nline
((= cl.recipient.company_name =))\\
((= cl.recipient.department_or_area =))\\
((= cl.recipient.city_state_zip =))\\
\nline

\textbf{Subject: Application for ((= cl.job.title =))((% if cl.job.job_id %)) (Job ID: ((= cl.job.job_id =)))((% endif %))}\\\nline

((= cl.content.salutation =))\nline

((% for paragraph in cl.content.paragraphs %))
((= paragraph =))
\nline
\nline
((% endfor %))

((= cl.content.closing =))
\nline
\nline
((% if cl.header.signature_image_path %))
\vspace{10pt}\includegraphics[width=0.1\linewidth]{((= cl.header.signature_image_path =))}\\
((% endif %))
((= cl.header.name =))

\end{document}
"""

# ==========================================
# JINJA2 ENGINE
# ==========================================

_JINJA_ENV = Environment(
    loader=BaseLoader(),
    block_start_string='((%',
    block_end_string='%))',
    variable_start_string='((=',
    variable_end_string='=))',
    comment_start_string='((#',
    comment_end_string='#))',
    trim_blocks=True,
    lstrip_blocks=True,
)

_TEMPLATE = _JINJA_ENV.from_string(LATEX_PREAMBLE + LATEX_BODY)


def load_data_module(file_path: str):
    _root = Path(__file__).resolve().parent.parent
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))
    from scripts.data_paths import apply_private_overlay
    apply_private_overlay()

    path_obj = Path(file_path)
    if not path_obj.exists():
        print(f"[x] Error: Data file '{file_path}' not found.")
        sys.exit(1)
    spec = importlib.util.spec_from_file_location("cl_data_module", str(path_obj))
    if spec is None or spec.loader is None:
        print(f"[x] Error: Could not load spec for '{file_path}'.")
        sys.exit(1)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"[x] Error executing module: {e}")
        sys.exit(1)


def generate_tex_file(data_file: str, output_file: str = "") -> Path:
    """Generate a .tex cover letter from a tailoring module.

    Args:
        data_file:   Path to a tailoring .py file containing cl_data.
        output_file: Override output path. If empty, uses cl_data.output_file.

    Returns:
        Path to the generated .tex file.
    """
    print(f">>> Loading data from: {data_file}")
    data_module = load_data_module(data_file)

    if not hasattr(data_module, 'cl_data'):
        print(f"[x] Error: '{data_file}' must expose a variable named 'cl_data'.")
        sys.exit(1)

    cl = data_module.cl_data
    output_file_path = Path(output_file) if output_file else Path(cl.output_file)
    output_file_path.parent.mkdir(parents=True, exist_ok=True)

    print(">>> Rendering cover letter template...")
    try:
        rendered_latex = _TEMPLATE.render(cl=cl)
    except Exception as e:
        print(f"[x] Rendering error: {e}")
        sys.exit(1)

    output_file_path.write_text(rendered_latex, encoding="utf-8")
    print(f"[+] Success! → {output_file_path.resolve()}")
    return output_file_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a LaTeX cover letter.")
    parser.add_argument("--data", "-p", default="coverletter/tailoring/_template.py",
                        help="Path to the tailoring .py file")
    parser.add_argument("--output", "-o", default="",
                        help="Override output .tex path")
    args = parser.parse_args()
    generate_tex_file(args.data, args.output)
