"""
resume/cv2latex.py
------------------
LaTeX generation engine.  Feed it a tailoring file path; it renders the CV.

Usage:
    python resume/cv2latex.py --data resume/tailoring/google_swe_2026.py
    python resume/cv2latex.py --data resume/tailoring/google_swe_2026.py --output out.tex

Or import generate_tex_file() from scripts/build.py.
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
\usepackage[fontsize=10pt]{scrextend}
\usepackage{ifthen}
\usepackage{graphicx}
\usepackage[
    ignoreheadfoot,
    top=0.6 cm,
    bottom=0.6 cm,
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
    pdftitle={CV},
    pdfauthor={((= cv.header.name =))},
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
\usepackage{charter}

\ifPDFTeX
    \input{glyphtounicode}
    \pdfgentounicode=1
    \usepackage[T1]{fontenc}
    \usepackage[utf8]{inputenc}
    \usepackage{lmodern}
\fi

\raggedright
\AtBeginEnvironment{adjustwidth}{\partopsep0 pt}
\pagestyle{empty}
\setcounter{secnumdepth}{0}
\setlength{\parindent}{0 pt}
\setlength{\topskip}{0 pt}
\setlength{\columnsep}{0.15 cm}
\pagenumbering{gobble}

\titleformat{\section}{\needspace{4\baselineskip}\bfseries\raggedright}{}{0pt}{}[\vspace{0.01 cm}\titlerule]
\titlespacing{\section}{-1 pt}{0.1 cm}{0.05 cm}

\renewcommand\labelitemi{$\vcenter{\hbox{\small$\bullet$}}$}

\newenvironment{highlights}{
    \begin{itemize}[topsep=0.05 cm,parsep=0.01 cm,partopsep=0 pt,itemsep=0 pt,leftmargin=0 cm + 10 pt]
}{\end{itemize}}

\newenvironment{highlightsforbulletentries}{
    \begin{itemize}[topsep=0.05 cm,parsep=0.01 cm,partopsep=0pt,itemsep=0pt,leftmargin=10pt]
}{\end{itemize}}

\newenvironment{onecolentry}{
    \begin{adjustwidth}{0 cm + 0.00001 cm}{0 cm + 0.00001 cm}
}{\end{adjustwidth}}

\newenvironment{twocolentry}[2][]{
    \onecolentry
    \def\secondColumn{#2}
    \setcolumnwidth{\fill, 5.6 cm}
    \begin{paracol}{2}
}{
    \switchcolumn \raggedleft \secondColumn
    \end{paracol}
    \endonecolentry
}

\newenvironment{threecolentry}[3][]{
    \onecolentry
    \def\thirdColumn{#3}
    \setcolumnwidth{, \fill, 5.5 cm}
    \begin{paracol}{3}
    {\raggedright #2} \switchcolumn
}{
    \switchcolumn \raggedleft \thirdColumn
    \end{paracol}
    \endonecolentry
}

\newenvironment{projectentry}[2]{
    \begin{twocolentry}{\textbf{#2}}
        {\fontsize{11}{11}\selectfont\textbf{#1}}
    \end{twocolentry}
    \begin{highlightsforbulletentries}
}{\end{highlightsforbulletentries}}

\newenvironment{header}{
    \setlength{\topsep}{0pt}\par\kern\topsep\centering\linespread{1.5}
}{\par\kern\topsep}

\let\hrefWithoutArrow\href
\usepackage{helvet}
\renewcommand{\familydefault}{\sfdefault}
\newcommand{\nline}{\hfill \break}

\newboolean{showSummary}
\newboolean{showEducation}
\newboolean{showSkills}
\newboolean{showWorkExp}
\newboolean{showProjects}
\newboolean{showCourseWork}
\newboolean{showResearch}

\setboolean{showSummary}{((= 'true' if cv.config.show_summary else 'false' =))}
\setboolean{showEducation}{((= 'true' if cv.config.show_education else 'false' =))}
\setboolean{showSkills}{((= 'true' if cv.config.show_skills else 'false' =))}
\setboolean{showWorkExp}{((= 'true' if cv.config.show_experience else 'false' =))}
\setboolean{showProjects}{((= 'true' if cv.config.show_projects else 'false' =))}
\setboolean{showCourseWork}{((= 'true' if cv.config.show_coursework else 'false' =))}
\setboolean{showResearch}{((= 'true' if cv.config.show_research else 'false' =))}
\title{Resume}
\author{((= cv.header.name =))}
"""

# ==========================================
# LATEX BODY
# ==========================================

LATEX_BODY = r"""
\begin{document}

    \newcommand{\AND}{\unskip\cleaders\copy\ANDbox\hskip\wd\ANDbox\ignorespaces}
    \newsavebox\ANDbox
    \sbox\ANDbox{$|$}

% ─── HEADER ───────────────────────────────────────────────────────────────────
\begin{header}
    \begin{twocolentry}
        {
            \small
            \faEnvelope\ \href{mailto:((= cv.header.email =))}{((= cv.header.email =))} \\
            \faPhone\ ((= cv.header.phone_primary =))
            ((% if cv.header.phone_secondary %)) \\ \faPhone\ ((= cv.header.phone_secondary =))((% endif %))
        }
        {\fontsize{20 pt}{20 pt}\selectfont \textbf{((= cv.header.name =))}}
    \end{twocolentry}

    \vspace{-7pt}
    \raggedright
    \small
    \faMapMarker\ ((= cv.header.location =)) \ | \ 
    \faLinkedin\ \href{((= cv.header.linkedin_url =))}{LinkedIn} \ | \ 
    \faGithub\ \href{((= cv.header.github_url =))}{GitHub}
    ((% if cv.header.leetcode_url %)) \ | \ \faCode\ \href{((= cv.header.leetcode_url =))}{LeetCode} ((% endif %))
    ((% if cv.header.website_url %))\ | \ \href{((= cv.header.website_url =))}{Portfolio} ((% endif %))

    ((% if cv.config.show_position_applied %))
    \vspace{2pt}
    \textbf{Position Applied: }{((= cv.position.role =))}
    ((% endif %))
\end{header}

% ─── SUMMARY ──────────────────────────────────────────────────────────────────
\ifthenelse{\boolean{showSummary}}{
    \section{SUMMARY}
        \vspace{1px}
        \begin{onecolentry}
            ((= cv.summary =))
        \end{onecolentry}
}{}

% ─── SKILLS ───────────────────────────────────────────────────────────────────
\ifthenelse{\boolean{showSkills}}{
    \section{SKILLS}
        \vspace{0.10 cm}
        \begin{onecolentry}
            \begin{highlights}
                ((% for cat in cv.skills %))
                \item \textbf{((= cat.name =)):} ((= cat.items =))
                ((% endfor %))
            \end{highlights}
        \end{onecolentry}
}{}

% ─── WORK EXPERIENCE ──────────────────────────────────────────────────────────
\ifthenelse{\boolean{showWorkExp}}{
    \section{WORK EXPERIENCE}
        \vspace{0.10 cm}
        ((% for job in cv.experience %))
        ((% if job.active %))
            \begin{projectentry}{((= job.role =)) | ((= job.company =))}{((= job.date =))}
                ((% for item in job.highlights %))
                \item ((= item =))
                ((% endfor %))
            \end{projectentry}
        ((% endif %))
        ((% endfor %))
}{}

% ─── RESEARCH ─────────────────────────────────────────────────────────────────
\ifthenelse{\boolean{showResearch}}{
    \section{RESEARCH}
        \vspace{0.10 cm}
        ((% for res in cv.research %))
        ((% if res.active %))
            \begin{projectentry}{((= res.title =)) | ((= res.organization =))}{((= res.date =))}
                ((% for item in res.highlights %))
                \item ((= item =))
                ((% endfor %))
                ((% if res.publication_url %))
                \item \url{((= res.publication_url =))}
                ((% endif %))
            \end{projectentry}
        ((% endif %))
        ((% endfor %))
}{}

% ─── PROJECTS ─────────────────────────────────────────────────────────────────
\ifthenelse{\boolean{showProjects}}{
    \section{PROJECTS}
        \vspace{0.1 cm}
        ((% for proj in cv.projects %))
        ((% if proj.active %))
            \begin{projectentry}{((= proj.title =)) | ((= proj.organization =))}{((= proj.date =))}
                ((% if proj.aim %))
                \item \textbf{Aim:} ((= proj.aim =))
                ((% endif %))
                ((% for item in proj.highlights %))
                \item ((= item =))
                ((% endfor %))
            \end{projectentry}
        ((% endif %))
        ((% endfor %))
}{}

% ─── EDUCATION ────────────────────────────────────────────────────────────────
\ifthenelse{\boolean{showEducation}}{
    \section{EDUCATION}
        \vspace{1px}
        ((% for edu in cv.education %))
        \begin{twocolentry}
            {{((= edu.location =))}\\{\textbf{((= edu.date =))}}}
            {{\fontsize{11}{11}\selectfont{\textbf{((= edu.institution =))}}}\\{\textit{((= edu.degree =))}((% if edu.gpa %))--- GPA: ((= edu.gpa =))((% endif %))}
                \begin{itemize}[leftmargin=*, label={$\bullet$}, itemsep=0pt, parsep=0pt, topsep=0pt, after=\vspace{1px}]
                    ((% for detail in edu.details %))
                    \item ((= detail =))
                    ((% endfor %))
                \end{itemize}
            }
        \end{twocolentry}
        ((% endfor %))
}{}

% ─── COURSEWORK ───────────────────────────────────────────────────────────────
\ifthenelse{\boolean{showCourseWork}}{
    \section{COURSEWORK}
        \vspace{0.10 cm}
        ((% for course in cv.coursework %))
        ((% if course.active %))
            \noindent \textbf{((= course.title =))}
            ((% if course.use_multicol %))
            \setlength{\multicolsep}{0pt}
            \begin{multicols}{2}
            \raggedright
            ((% endif %))
            \begin{highlights}
                ((% for item in course.courses %))
                \item ((= item =))
                ((% endfor %))
            \end{highlights}
            ((% if course.use_multicol %))
            \end{multicols}
            ((% endif %))
            \vspace{0.2cm}
        ((% endif %))
        ((% endfor %))
}{}

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
    spec = importlib.util.spec_from_file_location("cv_data_module", str(path_obj))
    if spec is None or spec.loader is None:
        print(f"[x] Error: Could not load spec for '{file_path}'.")
        sys.exit(1)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"[x] Error executing data module: {e}")
        sys.exit(1)


def generate_tex_file(data_file: str, output_file: str = "") -> Path:
    """Generate a .tex file from a tailoring module.

    Args:
        data_file:   Path to a tailoring .py file containing cv_data.
        output_file: Override output path. If empty, uses cv_data.output_file.

    Returns:
        Path to the generated .tex file.
    """
    print(f">>> Loading data from: {data_file}")
    data_module = load_data_module(data_file)

    if not hasattr(data_module, 'cv_data'):
        print(f"[x] Error: '{data_file}' must expose a variable named 'cv_data'.")
        sys.exit(1)

    cv = data_module.cv_data
    output_file_path = Path(output_file) if output_file else Path(cv.output_file)
    output_file_path.parent.mkdir(parents=True, exist_ok=True)

    print(">>> Rendering LaTeX template...")
    try:
        rendered_latex = _TEMPLATE.render(cv=cv)
    except Exception as e:
        print(f"[x] Rendering error: {e}")
        sys.exit(1)

    output_file_path.write_text(rendered_latex, encoding="utf-8")
    print(f"[+] Success! → {output_file_path.resolve()}")
    return output_file_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a LaTeX CV from a tailoring file.")
    parser.add_argument("--data", "-p", default="resume/tailoring/_template.py",
                        help="Path to the tailoring .py file")
    parser.add_argument("--output", "-o", default="",
                        help="Override output .tex path")
    args = parser.parse_args()
    generate_tex_file(args.data, args.output)
