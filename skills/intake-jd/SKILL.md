---
name: intake-jd
description: >
  Use when starting new application. Converts raw JD (text, URL, or screenshot) 
  into standardized `jd.md` and `job.yaml` artifacts.
---

# Intake JD

Convert input JD into structured artifacts for downstream tailoring and audit.

## Inputs
- **URL**: Fetch verbatim via harness-native web.
- **Text**: Paste verbatim.
- **Screenshot**: Transcribe verbatim. If multiple, user orders them -> one continuous file. Mark unreadable regions as `[UNREADABLE]`.

## Artifacts
All files land in `applications/jobs/<id>/` (routed via `scripts/data_paths.py`).

### 1. `jd.md`
Two sections:
1. **JD Summary** — Cleaned, structured extraction (role, company, team, location, requirements, keywords, hooks).
2. **Verbatim Transcription** — Full raw posting including boilerplate.

### 2. `job.yaml`
```yaml
job_id: <company>_<role>_<YYYY>_<MM>_<DD>
company: <Official Company Name>
role: <Official Job Title>
team: <Specific Team/Dept or null>
location: <City, State (Remote/Hybrid/Onsite) or null>
source: url | screenshot | text
source_url: <URL if applicable or null>
seniority: <new-grad | mid-level | senior | null>
keywords:
  - <Literal term from JD>
normalized_keywords:
  - <Expanded/Standardized term>
hard_requirements:
  - <Must-have requirement>
nice_to_have:
  - <Preferred requirement>
company_hooks:
  - <Specific fact about company/team from JD for CL hook>
```

## Workflow

1. **Identify Job ID**
   - Format: `{company}_{role}_{YYYY}_{MM}_{DD}` (lowercase, underscores). Date = intake date.
   - Check if `applications/jobs/<id>/` exists.
   - **Collision**: Stop and ask user for confirmation/new ID.

2. **Produce `jd.md`**
   - Fetch/Transcribe verbatim.
   - Write **Summary** (cleaned) then **Verbatim** sections.
   - Write to `applications/jobs/<id>/jd.md`.

3. **Extract `job.yaml`**
   - Populate schema from JD.
   - **Keywords**: `keywords` = literal strings only. `normalized_keywords` for expansion.
   - **Hooks**: JD-derived only.
   - Write to `applications/jobs/<id>/job.yaml`.

4. **Confirmation Gate**
   - Display short summary of `job.yaml` (Company, Role, Team, Key Req).
   - Continue unless run in gated orchestrator mode.

## Re-run Semantics
- If `applications/jobs/<id>/` exists: **Refuse by default**.
- Require explicit `force` to overwrite. Hand-corrections to `job.yaml` take priority.