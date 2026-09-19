#!/usr/bin/env -S uv run
"""
scripts/convert_profile.py
--------------------------
One-shot converter: private/profile/*.py  ->  private/profile/*.yaml

Run once after verifying the YAML renders byte-identical .tex to the current
known-good output. Then delete this script.
"""

import sys
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PRIVATE = ROOT / "private"
PROFILE_PY = PRIVATE / "profile"
PROFILE_YAML = PRIVATE / "profile"

# Import the actual profile modules to get the live objects
import private.profile.header as header_mod
import private.profile.education as education_mod
import private.profile.experience as experience_mod
import private.profile.projects as projects_mod
import private.profile.research as research_mod
import private.profile.skills as skills_mod
import private.profile.summaries as summaries_mod
import private.profile.coursework as coursework_mod
import private.profile.master_data as master_data


def extract_dataclass_fields(obj, include_none=False):
    """Extract fields from a dataclass instance as a dict."""
    result = {}
    for field_name in obj.__dataclass_fields__:
        value = getattr(obj, field_name)
        if value is not None or include_none:
            result[field_name] = value
    return result


def escape_for_yaml(text: str) -> str:
    """Escape string for YAML double-quoted scalar."""
    # YAML double-quoted strings: escape backslashes and quotes
    text = text.replace('\\', '\\\\')
    text = text.replace('"', '\\"')
    return text


def write_yaml_file(path: Path, data: dict, top_key: str = None):
    """Write a dict as YAML with schema_version."""
    import yaml
    output = {'schema_version': 1}
    if top_key:
        output[top_key] = data
    else:
        output.update(data)
    
    # Use yaml.dump with custom string representation
    yaml_str = yaml.dump(output, default_flow_style=False, sort_keys=False, allow_unicode=True, width=200)
    path.write_text(yaml_str, encoding='utf-8')
    print(f"[+] Wrote {path}")


def convert_header():
    header_yaml = {
        'header': extract_dataclass_fields(header_mod.HEADER),
        'cl_header': extract_dataclass_fields(header_mod.CL_HEADER),
    }
    write_yaml_file(PROFILE_YAML / "header.yaml", header_yaml)


def convert_education():
    edu_list = []
    for name in dir(education_mod):
        if name.isupper() and not name.startswith('_'):
            obj = getattr(education_mod, name)
            if hasattr(obj, 'institution'):
                d = extract_dataclass_fields(obj)
                d['id'] = name
                edu_list.append(d)
    write_yaml_file(PROFILE_YAML / "education.yaml", {'education': edu_list})


def convert_experience():
    exp_list = []
    for name in master_data.EXPERIENCE_REGISTRY:
        obj = master_data.EXPERIENCE_REGISTRY[name]
        d = extract_dataclass_fields(obj)
        d['id'] = name
        # Convert highlights to bullets with id/text structure
        bullets = []
        for i, bullet_text in enumerate(obj.highlights):
            bullets.append({'id': f'b{i+1}', 'text': bullet_text})
        d['bullets'] = bullets
        del d['highlights']
        exp_list.append(d)
    write_yaml_file(PROFILE_YAML / "experience.yaml", {'experience': exp_list})


def convert_projects():
    proj_list = []
    for name in master_data.PROJECT_REGISTRY:
        obj = master_data.PROJECT_REGISTRY[name]
        d = extract_dataclass_fields(obj)
        d['id'] = name
        bullets = []
        for i, bullet_text in enumerate(obj.highlights):
            bullets.append({'id': f'b{i+1}', 'text': bullet_text})
        d['bullets'] = bullets
        del d['highlights']
        proj_list.append(d)
    write_yaml_file(PROFILE_YAML / "projects.yaml", {'projects': proj_list})


def convert_research():
    res_list = []
    for name in master_data.RESEARCH_REGISTRY:
        obj = master_data.RESEARCH_REGISTRY[name]
        d = extract_dataclass_fields(obj)
        d['id'] = name
        bullets = []
        for i, bullet_text in enumerate(obj.highlights):
            bullets.append({'id': f'b{i+1}', 'text': bullet_text})
        d['bullets'] = bullets
        del d['highlights']
        res_list.append(d)
    write_yaml_file(PROFILE_YAML / "research.yaml", {'research': res_list})


def convert_skills():
    # Skills are more complex - we'll keep the manually written skills.yaml
    # since it has the enum/aliases structure that the Python version doesn't
    print("[!] Skipping skills.yaml - manually maintained with enum/aliases structure")
    pass


def convert_summaries():
    write_yaml_file(PROFILE_YAML / "summaries.yaml", {'summaries': summaries_mod.SUMMARIES})


def convert_coursework():
    cw_list = []
    for name in dir(coursework_mod):
        if name.isupper() and not name.startswith('_'):
            obj = getattr(coursework_mod, name)
            if hasattr(obj, 'title'):
                d = extract_dataclass_fields(obj)
                d['id'] = name
                cw_list.append(d)
    write_yaml_file(PROFILE_YAML / "coursework.yaml", {'coursework': cw_list})


def main():
    print("Converting profile Python -> YAML...")
    convert_header()
    convert_education()
    convert_experience()
    convert_projects()
    convert_research()
    convert_skills()
    convert_summaries()
    convert_coursework()
    print("\n[+] Conversion complete. Verify with: uv run scripts/loader.py --inventory")


if __name__ == "__main__":
    main()