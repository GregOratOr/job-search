"""
scripts/loader.py
-----------------
YAML loader for profile and tailored documents.
Returns validated CV / CoverLetter dataclasses ready for the renderer.

Public API:
    load_profile() -> dict with header, cl_header, education, experience, projects,
                      research, skills, summaries, coursework
    load_resume(job_id: str) -> CV
    load_cover_letter(job_id: str) -> CoverLetter

Validation rules (hard errors):
    - Unknown skill not in profile/skills.yaml inventory
    - Unknown source id in resume.yaml / cover_letter.yaml
    - Unescaped LaTeX specials in bullet/summary text (& % $ _ # { })
    - Missing required fields

Warnings:
    - Bullet length > 200 chars
"""

from __future__ import annotations

import sys
import re
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, field

import yaml

ROOT = Path(__file__).resolve().parent.parent
PRIVATE = ROOT / "private"
PROFILE_DIR = PRIVATE / "profile"
JOBS_DIR = PRIVATE / "applications" / "jobs"

# Add resume/coverletter to path for dataclass imports
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from resume.cv_utils import (
    SectionConfig, HeaderInfo, PositionInfo, EducationEntry,
    SkillCategory, ExperienceEntry, ProjectEntry, CourseworkEntry,
    ResearchEntry, CV
)
from coverletter.cl_utils import CLHeader, RecipientInfo, JobInfo, LetterContent, CoverLetter


# ==============================================================================
# VALIDATION HELPERS
# ==============================================================================

LATEX_SPECIALS_PATTERN = re.compile(r'[&%$#_{}]')
# Allow common LaTeX commands - they contain backslashes followed by letters
LATEX_COMMAND_PATTERN = re.compile(r'\\[a-zA-Z]+')

# Known LaTeX commands we allow without flagging (not exhaustive, just common ones)
ALLOWED_LATEX_COMMANDS = {
    'textbf', 'textit', 'texttt', 'emph', 'underline',
    'texttimes', 'times', 'textbullet', 'bullet',
    'href', 'url', 'faEnvelope', 'faPhone', 'faMapMarker',
    'faLinkedin', 'faGithub', 'faCode', 'AND', 'nline',
    'small', 'fontsize', 'selectfont', 'textbf', 'textit',
    'vspace', 'hfill', 'break', 'unskip', 'cleaders',
    'copy', 'hskip', 'wd', 'ignorespaces', 'sbox',
    'needspace', 'baselineskip', 'bfseries', 'raggedright',
    'centering', 'linespread', 'kern', 'topsep', 'par',
    'section', 'item', 'begin', 'end', 'ifthenelse', 'boolean',
    'setboolean', 'true', 'false', 'vspace', 'hspace',
    'textbackslash', 'textasciitilde', 'textasciicircum',
    'textless', 'textgreater', 'textbar', 'textunderscore',
    'textdollar', 'textpercent', 'textampersand', 'texthash',
    'textbraceleft', 'textbraceright', 'textleft', 'textright',
    'multicolumn', 'multicolumn', 'parbox', 'makebox', 'framebox',
    'rule', 'hrule', 'vrule', 'hline', 'cline', 'vline',
    'tabular', 'tabularx', 'array', 'newcolumntype',
    'thead', 'tbody', 'tfoot', 'tr', 'td', 'th',
    'multicolumn', 'multirow', 'cline', 'hline', 'vspace',
    'raggedleft', 'raggedright', 'centering', 'justify',
    'textbf', 'textit', 'textsc', 'textsf', 'texttt',
    'uppercase', 'lowercase', 'MakeUppercase', 'MakeLowercase',
    'label', 'ref', 'pageref', 'cite', 'bibitem', 'bibliography',
    'bibliographystyle', 'chapter', 'section', 'subsection',
    'subsubsection', 'paragraph', 'subparagraph', 'tableofcontents',
    'listoffigures', 'listoftables', 'appendix', 'index',
    'glossary', 'acronym', 'printglossary', 'printacronyms',
    'newglossaryentry', 'newacronym', 'gls', 'glspl', 'Gls', 'Glspl',
    'includegraphics', 'graphicspath', 'DeclareGraphicsExtensions',
    'caption', 'label', 'ref', 'subfloat', 'subfigure', 'subtable',
    'float', 'figure', 'table', 'centering', 'captionof',
    'footnote', 'footnotetext', 'footnotemark', 'marginpar',
    'todo', 'TODO', 'FIXME', 'XXX', 'NOTE', 'HACK', 'OPTIMIZE',
    'begin', 'end', 'item', 'itemize', 'enumerate', 'description',
    'label', 'ref', 'pageref', 'nameref', 'autoref', 'cref',
    'Cref', 'vpageref', 'Vref', 'eqref', 'Eqref', 'tags',
    'hyperref', 'href', 'url', 'nolinkurl', 'hyperbaseurl',
    'pdfbookmark', 'pdfstringdef', 'texorpdfstring', 'pdfauthor',
    'pdftitle', 'pdfsubject', 'pdfkeywords', 'pdfproducer',
    'pdfcreator', 'hypersetup', 'urlstyle', 'def', 'newcommand',
    'renewcommand', 'providecommand', 'DeclareMathOperator',
    'operatorname', 'DeclarePairedDelimiter', 'DeclarePairedDelimiterX',
    'left', 'right', 'big', 'Big', 'bigg', 'Bigg', 'bigl', 'Bigr',
    'biggl', 'Biggr', 'middle', 'langle', 'rangle', 'lfloor', 'rfloor',
    'lceil', 'rceil', 'lbrace', 'rbrace', 'vert', 'Vert', 'lvert',
    'rvert', 'lVert', 'rVert', 'parallel', 'parallel', 'perp',
    'mid', 'nmid', 'models', 'nmodels', 'vdash', 'nvdash', 'Vdash',
    'NVdash', 'vDash', 'nvDash', 'VvDash', 'NVvDash', 'approx',
    'simeq', 'cong', 'equiv', 'sim', 'backsim', 'thicksim',
    'thickapprox', 'propto', 'varpropto', 'propto', 'varkappa',
    'infty', 'infty', 'emptyset', 'varnothing', 'nabla', 'partial',
    'infty', 'infty', 'infty', 'infty', 'infty', 'infty', 'infty',
}

def check_latex_escaping(text: str, context: str) -> list[str]:
    """Check for unescaped LaTeX special characters. Returns list of error messages.

    LaTeX special chars that must be escaped: & % $ # _ { }
    Allowed (protected from flagging):
    - LaTeX commands: \cmd{...}, \cmd[...]{...} (single or double backslash)
    - Math mode: $...$, $$...$$
    - Already-escaped specials: \% \& \$ \# \_ \{ \} (one or two backslashes)
    """
    errors = []
    if not isinstance(text, str):
        return errors
    
    protected = text
    
    # Protect LaTeX commands with braced args: \cmd{...} or \cmd[...]{...}
    # Match 1 or 2 backslashes followed by command name + optional bracket args + brace args
    protected = re.sub(r'\\{1,2}[a-zA-Z]+(\s*\[[^\]]*\])?\s*\{[^}]*\}', 
                       lambda m: chr(0) + m.group() + chr(1), protected)
    
    # Protect math mode $$...$$ and $...$
    protected = re.sub(r'\$\$[^$]*\$\$', lambda m: chr(0) + m.group() + chr(1), protected)
    protected = re.sub(r'\$[^$]*\$', lambda m: chr(0) + m.group() + chr(1), protected)
    
    # Protect already-escaped specials: \% \& \$ \# \_ \{ \}
    # Match 1 or 2 backslashes + special char
    protected = re.sub(r'\\{1,2}[&%$#_{}]', lambda m: chr(0) + m.group() + chr(1), protected)
    
    # Check for unescaped specials, skipping protected regions
    in_protected = False
    for i, ch in enumerate(protected):
        if ch == chr(0):
            in_protected = True
            continue
        if ch == chr(1):
            in_protected = False
            continue
        if in_protected:
            continue
        if ch in '&%$#_{}':
            start = max(0, i - 40)
            end = min(len(protected), i + 40)
            snippet = protected[start:end].replace(chr(0), '').replace(chr(1), '')
            errors.append(
                f"Unescaped LaTeX special '{ch}' in {context}: ...{snippet}..."
            )
    return errors


def check_bullet_length(text: str, context: str, limit: int = 200) -> list[str]:
    """Check bullet length. Returns list of warnings."""
    warnings = []
    if isinstance(text, str) and len(text) > limit:
        warnings.append(
            f"Bullet in {context} exceeds {limit} chars ({len(text)}): {text[:80]}..."
        )
    return warnings


# ==============================================================================
# PROFILE LOADING
# ==============================================================================

def _load_yaml(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")
    with path.open('r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    if data is None:
        return {}
    return data


def _validate_profile_skills(skills_data: dict) -> list[str]:
    """Validate that skill categories and items match the inventory."""
    errors = []
    # The skills.yaml defines the canonical inventory
    # We trust it as the source of truth; tailoring just selects from it
    return errors


def load_profile() -> dict:
    """
    Load the entire profile from YAML files.
    Returns a dict with all profile components as dataclass instances.
    """
    profile = {}
    
    # Header
    header_data = _load_yaml(PROFILE_DIR / "header.yaml")
    profile['header'] = HeaderInfo(**header_data['header'])
    profile['cl_header'] = CLHeader(**header_data['cl_header'])
    
    # Education
    edu_data = _load_yaml(PROFILE_DIR / "education.yaml")
    profile['education'] = []
    for e in edu_data.get('education', []):
        e_copy = dict(e)
        e_copy.pop('id', None)  # Remove id field not in dataclass
        profile['education'].append(EducationEntry(**e_copy))
    
    # Experience
    exp_data = _load_yaml(PROFILE_DIR / "experience.yaml")
    profile['experience'] = []
    for e in exp_data.get('experience', []):
        e_copy = dict(e)
        e_copy.pop('id', None)
        # YAML uses 'highlights' with id/text; dataclass uses 'highlights' as list of strings
        highlights = []
        for b in e_copy.get('highlights', []):
            if isinstance(b, dict):
                highlights.append(b.get('text', ''))
            else:
                highlights.append(b)
        e_copy['highlights'] = highlights
        profile['experience'].append(ExperienceEntry(**e_copy))
    
    # Projects
    proj_data = _load_yaml(PROFILE_DIR / "projects.yaml")
    profile['projects'] = []
    for p in proj_data.get('projects', []):
        p_copy = dict(p)
        p_copy.pop('id', None)
        highlights = []
        for b in p_copy.get('highlights', []):
            if isinstance(b, dict):
                highlights.append(b.get('text', ''))
            else:
                highlights.append(b)
        p_copy['highlights'] = highlights
        profile['projects'].append(ProjectEntry(**p_copy))

    # Research
    res_data = _load_yaml(PROFILE_DIR / "research.yaml")
    profile['research'] = []
    for r in res_data.get('research', []):
        r_copy = dict(r)
        r_copy.pop('id', None)
        highlights = []
        for b in r_copy.get('highlights', []):
            if isinstance(b, dict):
                highlights.append(b.get('text', ''))
            else:
                highlights.append(b)
        r_copy['highlights'] = highlights
        profile['research'].append(ResearchEntry(**r_copy))

    # Coursework
    cw_data = _load_yaml(PROFILE_DIR / "coursework.yaml")
    profile['coursework'] = []
    for c in cw_data.get('coursework', []):
        c_copy = dict(c)
        c_copy.pop('id', None)
        profile['coursework'].append(CourseworkEntry(**c_copy))
    
    # Skills - load inventory
    skills_data = _load_yaml(PROFILE_DIR / "skills.yaml")
    # skills.yaml has top-level 'skills' key
    skills_root = skills_data.get('skills', skills_data)
    profile['skills_inventory'] = skills_root  # raw for validation
    profile['skills_presets'] = skills_root.get('presets', {})
    
    # Summaries
    summ_data = _load_yaml(PROFILE_DIR / "summaries.yaml")
    profile['summaries'] = summ_data.get('summaries', {})
    
    return profile


# ==============================================================================
# SKILL INVENTORY VALIDATION
# ==============================================================================

def _build_skill_inventory(skills_data: dict) -> set[str]:
    """Build a flat set of all allowed skill display strings from skills.yaml."""
    allowed = set()
    for cat in skills_data.get('categories', []):
        for item in cat.get('items', []):
            allowed.add(item['value'])
            # Also add aliases as valid
            for alias in item.get('aliases', []):
                allowed.add(alias)
    return allowed


def _validate_resume_skills(resume_skills: list[dict], allowed_skills: set[str], job_id: str) -> list[str]:
    """Validate that all skills in resume.yaml exist in the inventory."""
    errors = []
    for cat in resume_skills:
        cat_name = cat.get('name', '')
        items_str = cat.get('items', '')
        if not items_str:
            continue
        # Split by comma and check each
        for item in items_str.split(','):
            item = item.strip()
            if item and item not in allowed_skills:
                errors.append(
                    f"resume.yaml ({job_id}): Unknown skill '{item}' in category '{cat_name}'. "
                    f"Not in profile/skills.yaml inventory."
                )
    return errors


# ==============================================================================
# RESUME LOADING
# ==============================================================================

def _resolve_experience_entry(source_id: str, profile: dict, overrides: dict) -> ExperienceEntry:
    """Resolve an experience entry by source_id, applying bullet overrides."""
    # Find in profile
    base_entry = None
    for e in profile['experience']:
        # Match by id field - but ExperienceEntry doesn't have id, we need to track it
        # We'll match by role+company+date as a composite key, or we need to add id to dataclass
        pass
    
    # Since the YAML has id but dataclass doesn't, we need a mapping
    # Build a map from the profile data
    exp_map = {}
    exp_data = _load_yaml(PROFILE_DIR / "experience.yaml")
    for e in exp_data.get('experience', []):
        exp_map[e['id']] = e
    
    if source_id not in exp_map:
        raise ValueError(f"Unknown experience source id: {source_id}")
    
    base = exp_map[source_id]
    
    # Build highlights with overrides
    highlights = []
    base_bullets = base.get('highlights', [])
    
    # overrides can contain bullets as a list of {"use_profile": idx} or {"rewrite": "text"}
    for bullet_spec in overrides.get('bullets', []):
        if 'use_profile' in bullet_spec:
            idx = bullet_spec['use_profile']
            if 0 <= idx < len(base_bullets):
                highlights.append(base_bullets[idx]['text'])
            else:
                raise ValueError(f"Bullet index {idx} out of range for {source_id} (has {len(base_bullets)} bullets)")
        elif 'rewrite' in bullet_spec:
            highlights.append(bullet_spec['rewrite'])
        else:
            raise ValueError(f"Bullet spec must have 'use_profile' or 'rewrite': {bullet_spec}")
    
    # If no bullets specified, use all from profile
    if not highlights and 'bullets' not in overrides:
        highlights = [b['text'] for b in base_bullets]
    
    return ExperienceEntry(
        role=overrides.get('role_override', base['role']),
        company=overrides.get('company_override', base['company']),
        date=overrides.get('date_override', base['date']),
        highlights=highlights,
        active=overrides.get('active', base.get('active', True))
    )


def _resolve_project_entry(source_id: str, profile: dict, overrides: dict) -> ProjectEntry:
    proj_map = {}
    proj_data = _load_yaml(PROFILE_DIR / "projects.yaml")
    for p in proj_data.get('projects', []):
        proj_map[p['id']] = p
    
    if source_id not in proj_map:
        raise ValueError(f"Unknown project source id: {source_id}")
    
    base = proj_map[source_id]
    
    highlights = []
    base_bullets = base.get('highlights', [])
    for bullet_spec in overrides.get('bullets', []):
        if 'use_profile' in bullet_spec:
            idx = bullet_spec['use_profile']
            if 0 <= idx < len(base_bullets):
                highlights.append(base_bullets[idx]['text'])
            else:
                raise ValueError(f"Bullet index {idx} out of range for {source_id}")
        elif 'rewrite' in bullet_spec:
            highlights.append(bullet_spec['rewrite'])
        else:
            raise ValueError(f"Bullet spec must have 'use_profile' or 'rewrite': {bullet_spec}")
    
    if not highlights and 'bullets' not in overrides:
        highlights = [b['text'] for b in base_bullets]
    
    return ProjectEntry(
        title=overrides.get('title_override', base['title']),
        organization=overrides.get('organization_override', base['organization']),
        date=overrides.get('date_override', base['date']),
        aim=overrides.get('aim', base.get('aim')),
        highlights=highlights,
        active=overrides.get('active', base.get('active', True))
    )


def _resolve_research_entry(source_id: str, profile: dict, overrides: dict) -> ResearchEntry:
    res_map = {}
    res_data = _load_yaml(PROFILE_DIR / "research.yaml")
    for r in res_data.get('research', []):
        res_map[r['id']] = r
    
    if source_id not in res_map:
        raise ValueError(f"Unknown research source id: {source_id}")
    
    base = res_map[source_id]
    
    highlights = []
    base_bullets = base.get('highlights', [])
    for bullet_spec in overrides.get('bullets', []):
        if 'use_profile' in bullet_spec:
            idx = bullet_spec['use_profile']
            if 0 <= idx < len(base_bullets):
                highlights.append(base_bullets[idx]['text'])
            else:
                raise ValueError(f"Bullet index {idx} out of range for {source_id}")
        elif 'rewrite' in bullet_spec:
            highlights.append(bullet_spec['rewrite'])
        else:
            raise ValueError(f"Bullet spec must have 'use_profile' or 'rewrite': {bullet_spec}")
    
    if not highlights and 'bullets' not in overrides:
        highlights = [b['text'] for b in base_bullets]
    
    return ResearchEntry(
        title=overrides.get('title_override', base['title']),
        organization=overrides.get('organization_override', base['organization']),
        date=overrides.get('date_override', base['date']),
        highlights=highlights,
        publication_url=overrides.get('publication_url', base.get('publication_url')),
        active=overrides.get('active', base.get('active', True))
    )


def _resolve_education_entry(source_id: str, profile: dict, overrides: dict) -> EducationEntry:
    edu_map = {}
    edu_data = _load_yaml(PROFILE_DIR / "education.yaml")
    for e in edu_data.get('education', []):
        edu_map[e['id']] = e
    
    if source_id not in edu_map:
        raise ValueError(f"Unknown education source id: {source_id}")
    
    base = edu_map[source_id]
    return EducationEntry(
        institution=overrides.get('institution_override', base['institution']),
        location=overrides.get('location_override', base['location']),
        date=overrides.get('date_override', base['date']),
        degree=overrides.get('degree_override', base['degree']),
        gpa=overrides.get('gpa', base.get('gpa', '')),
        details=overrides.get('details', base.get('details', [])),
        achievements=overrides.get('achievements', base.get('achievements', []))
    )


def load_resume(job_id: str) -> CV:
    """
    Load a tailored resume from applications/jobs/<job_id>/resume.yaml
    Resolves all source references against the profile.
    """
    resume_path = JOBS_DIR / job_id / "resume.yaml"
    if not resume_path.exists():
        raise FileNotFoundError(f"resume.yaml not found for job {job_id}: {resume_path}")
    
    with resume_path.open('r', encoding='utf-8') as f:
        resume_data = yaml.safe_load(f)
    
    if not resume_data:
        raise ValueError(f"Empty resume.yaml for {job_id}")
    
    # Load profile for resolution and validation
    profile = load_profile()
    allowed_skills = _build_skill_inventory(profile['skills_inventory'])
    
    errors = []
    warnings = []
    
    # Validate skills against inventory
    if 'skills' in resume_data:
        errors.extend(_validate_resume_skills(resume_data['skills'], allowed_skills, job_id))
    
    # Validate LaTeX escaping in all text fields
    if 'summary' in resume_data and resume_data['summary']:
        errors.extend(check_latex_escaping(resume_data['summary'], f"resume.yaml summary ({job_id})"))
    
    # SectionConfig
    sections_data = resume_data.get('sections', {})
    section_config = SectionConfig(
        show_position_applied=sections_data.get('show_position_applied', False),
        show_summary=sections_data.get('show_summary', False),
        show_skills=sections_data.get('show_skills', True),
        show_experience=sections_data.get('show_experience', True),
        show_projects=sections_data.get('show_projects', True),
        show_research=sections_data.get('show_research', False),
        show_education=sections_data.get('show_education', True),
        show_coursework=sections_data.get('show_coursework', False),
    )
    
    # Resolve experience entries
    experience = []
    for exp_spec in resume_data.get('experience', []):
        source_id = exp_spec.get('source')
        if not source_id:
            errors.append(f"resume.yaml ({job_id}): experience entry missing 'source'")
            continue
        try:
            entry = _resolve_experience_entry(source_id, profile, exp_spec)
            experience.append(entry)
            # Validate bullets
            for i, bullet in enumerate(entry.highlights):
                errors.extend(check_latex_escaping(bullet, f"resume.yaml experience[{source_id}] bullet {i}"))
                warnings.extend(check_bullet_length(bullet, f"resume.yaml experience[{source_id}] bullet {i}"))
        except ValueError as e:
            errors.append(f"resume.yaml ({job_id}): {e}")
    
    # Resolve projects
    projects = []
    for proj_spec in resume_data.get('projects', []):
        source_id = proj_spec.get('source')
        if not source_id:
            errors.append(f"resume.yaml ({job_id}): project entry missing 'source'")
            continue
        try:
            entry = _resolve_project_entry(source_id, profile, proj_spec)
            projects.append(entry)
            for i, bullet in enumerate(entry.highlights):
                errors.extend(check_latex_escaping(bullet, f"resume.yaml project[{source_id}] bullet {i}"))
                warnings.extend(check_bullet_length(bullet, f"resume.yaml project[{source_id}] bullet {i}"))
        except ValueError as e:
            errors.append(f"resume.yaml ({job_id}): {e}")
    
    # Resolve research
    research = []
    for res_spec in resume_data.get('research', []):
        source_id = res_spec.get('source')
        if not source_id:
            errors.append(f"resume.yaml ({job_id}): research entry missing 'source'")
            continue
        try:
            entry = _resolve_research_entry(source_id, profile, res_spec)
            research.append(entry)
            for i, bullet in enumerate(entry.highlights):
                errors.extend(check_latex_escaping(bullet, f"resume.yaml research[{source_id}] bullet {i}"))
                warnings.extend(check_bullet_length(bullet, f"resume.yaml research[{source_id}] bullet {i}"))
        except ValueError as e:
            errors.append(f"resume.yaml ({job_id}): {e}")
    
    # Resolve education
    education = []
    for edu_spec in resume_data.get('education', []):
        source_id = edu_spec.get('source')
        if not source_id:
            errors.append(f"resume.yaml ({job_id}): education entry missing 'source'")
            continue
        try:
            entry = _resolve_education_entry(source_id, profile, edu_spec)
            education.append(entry)
            for detail in entry.details:
                errors.extend(check_latex_escaping(detail, f"resume.yaml education[{source_id}] detail"))
        except ValueError as e:
            errors.append(f"resume.yaml ({job_id}): {e}")
    
    # Skills - convert to SkillCategory list
    skills = []
    for cat in resume_data.get('skills', []):
        skills.append(SkillCategory(name=cat['name'], items=cat['items']))
    
    # Summary
    summary = resume_data.get('summary')
    if summary:
        errors.extend(check_latex_escaping(summary, f"resume.yaml summary ({job_id})"))
    
    # Position
    position = PositionInfo(role=resume_data.get('position', ''))
    
    # Report warnings
    for w in warnings:
        print(f"[!] {w}", file=sys.stderr)
    
    if errors:
        for e in errors:
            print(f"[x] {e}", file=sys.stderr)
        raise ValueError(f"Validation failed for resume.yaml ({job_id}) - {len(errors)} errors")
    
    return CV(
        config=section_config,
        header=profile['header'],
        position=position,
        education=education,
        skills=skills,
        experience=experience,
        projects=projects,
        research=research,
        coursework=[],  # coursework entries not typically selected individually
        summary=summary,
        output_file=str(JOBS_DIR / job_id / "resume.tex")
    )


# ==============================================================================
# COVER LETTER LOADING
# ==============================================================================

def load_cover_letter(job_id: str) -> CoverLetter:
    """
    Load a tailored cover letter from applications/jobs/<job_id>/cover_letter.yaml
    """
    cl_path = JOBS_DIR / job_id / "cover_letter.yaml"
    if not cl_path.exists():
        raise FileNotFoundError(f"cover_letter.yaml not found for job {job_id}: {cl_path}")
    
    with cl_path.open('r', encoding='utf-8') as f:
        cl_data = yaml.safe_load(f)
    
    if not cl_data:
        raise ValueError(f"Empty cover_letter.yaml for {job_id}")
    
    profile = load_profile()
    errors = []
    warnings = []
    
    # Header from profile
    header = profile['cl_header']
    
    # Recipient from job.yaml (or cl_data override)
    job_info_data = _load_yaml(JOBS_DIR / job_id / "job.yaml")
    recipient = RecipientInfo(
        company_name=cl_data.get('company', job_info_data.get('company', '')),
        department_or_area=cl_data.get('team', job_info_data.get('team', '')),
        city_state_zip=cl_data.get('location', job_info_data.get('location', '')),
    )
    
    # Job info
    job_info = JobInfo(
        title=cl_data.get('role', job_info_data.get('role', '')),
        job_id=job_id
    )
    
    # Paragraphs - authored per job
    paragraphs = cl_data.get('paragraphs', [])
    for i, p in enumerate(paragraphs):
        errors.extend(check_latex_escaping(p, f"cover_letter.yaml paragraph {i} ({job_id})"))
        warnings.extend(check_bullet_length(p, f"cover_letter.yaml paragraph {i} ({job_id})", limit=500))
    
    # Date string - written at authoring time
    date_str = cl_data.get('date_str', '')
    if not date_str:
        errors.append(f"cover_letter.yaml ({job_id}): missing required 'date_str'")
    
    salutation = cl_data.get('salutation', 'Dear Hiring Manager,')
    closing = cl_data.get('closing', 'Sincerely,')
    
    for w in warnings:
        print(f"[!] {w}", file=sys.stderr)
    
    if errors:
        for e in errors:
            print(f"[x] {e}", file=sys.stderr)
        raise ValueError(f"Validation failed for cover_letter.yaml ({job_id}) - {len(errors)} errors")
    
    content = LetterContent(
        date_str=date_str,
        salutation=salutation,
        paragraphs=paragraphs,
        closing=closing
    )
    
    return CoverLetter(
        header=header,
        recipient=recipient,
        job=job_info,
        content=content,
        output_file=str(JOBS_DIR / job_id / "cover_letter.tex")
    )


# ==============================================================================
# INVENTORY COMMAND (for validate_profile.py replacement)
# ==============================================================================

def print_inventory() -> None:
    """Print inventory of all profile entries with their IDs."""
    profile = load_profile()
    
    print("\n=== Education ===")
    for e in profile['education']:
        print(f"  {e.institution:<45} {getattr(e, 'date', 'N/A')}")
    
    print("\n=== Experience ===")
    exp_data = _load_yaml(PROFILE_DIR / "experience.yaml")
    for e in exp_data.get('experience', []):
        print(f"  {e['id']:<28} {e['role']:<40} {e['date']}")
    
    print("\n=== Projects ===")
    proj_data = _load_yaml(PROFILE_DIR / "projects.yaml")
    for p in proj_data.get('projects', []):
        print(f"  {p['id']:<32} {p['title'][:45]:<45} {p['date']}")
    
    print("\n=== Research ===")
    res_data = _load_yaml(PROFILE_DIR / "research.yaml")
    for r in res_data.get('research', []):
        print(f"  {r['id']:<32} {r['title'][:50]:<50} {r['date']}")
    
    print("\n=== Skill Presets ===")
    for name in profile['skills_presets']:
        print(f"  {name}")
    
    print("\n=== Summary Variants ===")
    for key in profile['summaries']:
        preview = profile['summaries'][key][:60].replace('\n', ' ')
        print(f'  "{key}"   {preview}...')


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Load and validate profile/resume/cover_letter YAML")
    parser.add_argument("--inventory", action="store_true", help="Print profile inventory")
    parser.add_argument("--resume", help="Load and validate resume.yaml for job_id")
    parser.add_argument("--cover-letter", help="Load and validate cover_letter.yaml for job_id")
    args = parser.parse_args()
    
    if args.inventory:
        print_inventory()
    elif args.resume:
        try:
            cv = load_resume(args.resume)
            print(f"[+] Resume for {args.resume} loaded successfully")
            print(f"    Experience: {len(cv.experience)} entries")
            print(f"    Projects: {len(cv.projects)} entries")
            print(f"    Research: {len(cv.research)} entries")
            print(f"    Skills: {len(cv.skills)} categories")
        except Exception as e:
            print(f"[x] Failed: {e}")
            sys.exit(1)
    elif args.cover_letter:
        try:
            cl = load_cover_letter(args.cover_letter)
            print(f"[+] Cover letter for {args.cover_letter} loaded successfully")
            print(f"    Paragraphs: {len(cl.content.paragraphs)}")
        except Exception as e:
            print(f"[x] Failed: {e}")
            sys.exit(1)
    else:
        # Default: validate profile
        try:
            profile = load_profile()
            print("[+] Profile loaded successfully")
            print(f"    Experience: {len(profile['experience'])} entries")
            print(f"    Projects: {len(profile['projects'])} entries")
            print(f"    Research: {len(profile['research'])} entries")
            print(f"    Education: {len(profile['education'])} entries")
            print(f"    Coursework: {len(profile['coursework'])} entries")
            print(f"    Skill presets: {len(profile['skills_presets'])}")
            print(f"    Summary variants: {len(profile['summaries'])}")
        except Exception as e:
            print(f"[x] Failed: {e}")
            sys.exit(1)