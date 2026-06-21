---
name: new-application
description: Scaffold a new job application bundle (resume + cover letter tailoring files and job_info). Use when the user wants to start a new application or create the files for a specific company/role.
---

# Scaffold a New Application

## Steps
1. Create the bundle:
   `python scripts/new_application.py --id <id> --company "<co>" --role "<role>"`
   (use `--force` to overwrite). The id must be letters/digits/underscores only.
2. This copies the templates and creates:
   - `resume/tailoring/<id>.py`
   - `coverletter/tailoring/<id>.py`
   - `applications/jobs/<id>/job_info.py`
3. Continue with the `tailor-resume` skill to fill them in.

## Pitfalls
- Existing files block scaffolding unless `--force` is passed.
- Generated tailoring files import from `profile/master_data` — select entries by name
  (`python scripts/update_profile.py --inventory`); do not add data to `profile/`.
