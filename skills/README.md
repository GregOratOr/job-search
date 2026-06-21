# skills/

Project-authored agent skill files (`SKILL.md`) that teach Hermes and Cursor how to run
this project's workflows. They are thin wrappers over `scripts/` — see the table below and
[SETUP.md](SETUP.md). You may optionally also pull external skills from
**https://github.com/GregOratOr/skills** using one of the options below.

## Optional: add external skills

### Option A — Git Submodule

```bash
# From the repo root (first time)
git submodule add https://github.com/GregOratOr/skills skills
git submodule update --init --recursive

# Keep in sync later
git submodule update --remote --merge
```

### Option B — Sparse Clone (if you only need specific skills)

```bash
git clone --no-checkout https://github.com/GregOratOr/skills skills-src
cd skills-src
git sparse-checkout init --cone
git sparse-checkout set latex_cv networking          # whichever folders you need
git checkout main
cd ..
cp -r skills-src/* skills/
```

### Option C — Manual Copy

Download the skills you need from GitHub and drop them into `skills/`.

---

## Setup

See [SETUP.md](SETUP.md) for wiring these skills into **Hermes (local Ollama)** and
**Cursor**.

> Hard rule: `profile/` is READ-ONLY for agents unless the user explicitly commands a
> profile change. Tailoring writes only to `resume/tailoring/`, `coverletter/tailoring/`,
> and `applications/`. See root `AGENTS.md`.

## Skills in this folder

Each skill is a thin wrapper over a `scripts/` command. The agent reasons; the script
generates files.

| Skill file                              | What it does                                          |
|-----------------------------------------|-------------------------------------------------------|
| `skills/tailor-resume/SKILL.md`         | Tailor resume + cover letter from a JD/URL            |
| `skills/build-documents/SKILL.md`       | Render `.tex` and compile PDFs                        |
| `skills/track-application/SKILL.md`     | Log/update applications in tracker.csv                |
| `skills/new-application/SKILL.md`       | Scaffold a new application bundle                     |
| `skills/update-profile/SKILL.md`        | Edit `profile/` — ONLY on explicit user command      |
| `skills/discover-jobs/SKILL.md`         | Find open roles (agent web tools) + tailor each       |
| `skills/networking-outreach/SKILL.md`   | Draft LinkedIn/email outreach from templates          |

---

## How Skills Are Discovered by Hermes

Hermes progressively discovers `AGENTS.md` files in subdirectories as it reads
files in those directories (see root `AGENTS.md` for details). Skill files
should either:
1. Be referenced from a subdirectory `AGENTS.md`, or
2. Be placed in a location Hermes navigates to during a task.

---

## Authoring a New Skill

Create `skills/{skill-name}/SKILL.md`:

```markdown
# Skill: <Name>

## When to use
Describe the trigger condition.

## Steps
1. Step one (concrete, actionable)
2. Step two
3. ...

## Examples
### Example 1
Input: ...
Output: ...

## Pitfalls
- Common mistake 1
- Common mistake 2
```

Then reference it in the relevant subdirectory `AGENTS.md`:

```markdown
## Available Skills
- `skills/my_skill/SKILL.md` — short description of when to use
```
