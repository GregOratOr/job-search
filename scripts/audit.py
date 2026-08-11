#!/usr/bin/env -S uv run
"""
scripts/audit.py
----------------
Audit a tailored resume and cover letter from a hiring manager's perspective.

Reads the JD, resume tailoring file, cover letter tailoring file, and profile
ground truth for a given application id, then runs four LLM phases:
  1. Resume critique  — ATS score, bullet quality, keyword gaps, structure.
  2. Cover letter critique — hook, evidence, closing, tone.
  3. Factual accuracy — compare selected/rewritten bullets against profile ground truth.
  4. Action plan synthesis — prioritised must-fix / high-impact / nice-to-have items.

Outputs:
  applications/jobs/<id>/audit.md

Usage:
    uv run scripts/audit.py --id nvidia_ml_2026
    uv run scripts/audit.py --id nvidia_ml_2026 --model claude-opus-4-7 --provider anthropic
    uv run scripts/audit.py --id nvidia_ml_2026 --out path/to/audit.md

Provider / model resolution (same priority chain as ai_tailor.py):
  --provider / --model flags  →  override .env for this run only (set LLM_PROVIDER).
  LLM_PROVIDER / LLM_MODEL in .env  →  default for standalone / Ollama-harness use.
  Auto-detect from API keys / OLLAMA_BASE_URL  →  fallback.

⛔ Read-only: this script never modifies profile/ or document source files.
   Address the flagged issues manually in resume/outputs/<id>.py and
   coverletter/outputs/<id>_cl.py, then rebuild and re-audit.
"""

from __future__ import annotations

import argparse
import datetime
import importlib.util
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.data_paths import apply_private_overlay, data_path, document_py, resolve_document_py
from scripts.text_utils import strip_latex
from scripts.llm_provider import complete, get_default_model, load_env, resolve_provider

apply_private_overlay()
load_env()


_strip_latex = strip_latex  # module-local alias for readers below


def _load_module(path: Path):
    """Dynamically import a Python tailoring file and return its module."""
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ── Content readers ───────────────────────────────────────────────────────────

def _skill_lines(skills_obj) -> list[str]:
    """Best-effort extraction from whatever skills structure the profile uses."""
    lines: list[str] = []
    try:
        for cat in (skills_obj or []):
            name  = getattr(cat, "name",  None) or getattr(cat, "category", None)
            items = getattr(cat, "items", None) or getattr(cat, "skills",   None)
            if name and items:
                lines.append(f"{name}: {', '.join(str(i) for i in items)}")
            elif hasattr(cat, "__str__") and str(cat):
                lines.append(str(cat))
    except Exception:
        pass
    return lines


def _resolve_doc_py(kind: str, job_id: str) -> Path:
    """Prefer current outputs naming; fall back to legacy paths."""
    found = resolve_document_py(kind, job_id)
    return found if found is not None else document_py(kind, job_id)


def read_resume_content(job_id: str) -> dict:
    """
    Load resume source file and extract plain-text content for auditing.

    Returns a dict with keys:
        company, role, summary, experience (list), projects (list), skills (list[str])
    """
    path = _resolve_doc_py("resume", job_id)
    if not path.exists():
        raise FileNotFoundError(
            f"Resume source file not found: {path}\n"
            f"Run: uv run scripts/new_application.py --id {job_id}"
        )
    mod = _load_module(path)
    cv  = getattr(mod, "cv_data", None)
    if cv is None:
        raise ValueError(f"`cv_data` not defined in {path}")

    result: dict = {
        "company":    getattr(mod, "COMPANY", ""),
        "role":       getattr(mod, "ROLE",    ""),
        "summary":    _strip_latex(getattr(cv, "summary", "") or ""),
        "experience": [],
        "projects":   [],
        "skills":     _skill_lines(getattr(cv, "skills", None)),
    }

    for entry in (getattr(cv, "experience", None) or []):
        result["experience"].append({
            "role":     _strip_latex(getattr(entry, "role",    "") or ""),
            "company":  _strip_latex(getattr(entry, "company", "") or ""),
            "date":     getattr(entry, "date", ""),
            "bullets":  [_strip_latex(b) for b in (getattr(entry, "highlights", None) or [])],
        })

    for proj in (getattr(cv, "projects", None) or []):
        result["projects"].append({
            "title":   _strip_latex(getattr(proj, "title",   "") or ""),
            "date":    getattr(proj, "date", ""),
            "aim":     _strip_latex(getattr(proj, "aim",     "") or ""),
            "bullets": [_strip_latex(b) for b in (getattr(proj, "highlights", None) or [])],
        })

    return result


def read_cl_content(job_id: str) -> dict | None:
    """
    Load cover letter source file and extract plain-text paragraphs.

    Returns a dict with keys: company, role, paragraphs (list[str]),
    or ``None`` if no cover letter source exists (caller may soft-skip).
    """
    path = _resolve_doc_py("coverletter", job_id)
    if not path.exists():
        return None
    mod = _load_module(path)
    cl  = getattr(mod, "cl_data", None)
    if cl is None:
        raise ValueError(f"`cl_data` not defined in {path}")

    paragraphs: list[str] = []
    content = getattr(cl, "content", None)
    if content:
        for p in (getattr(content, "paragraphs", None) or []):
            paragraphs.append(_strip_latex(str(p)))

    return {
        "company":    getattr(mod, "COMPANY", ""),
        "role":       getattr(mod, "ROLE",    ""),
        "paragraphs": paragraphs,
    }


def read_jd(job_id: str) -> str:
    """Read jd.txt from the application bundle (written by ai_tailor.py)."""
    jd_path = data_path("applications", "jobs", job_id, "jd.txt")
    if not jd_path.exists():
        return ""
    return jd_path.read_text(encoding="utf-8")[:8000]


def read_ground_truth() -> dict:
    """
    Load the full EXPERIENCE_REGISTRY and PROJECT_REGISTRY from profile/master_data
    for factual accuracy comparison.
    """
    try:
        from profile.master_data import EXPERIENCE_REGISTRY, PROJECT_REGISTRY
        exp: dict = {}
        for var, e in EXPERIENCE_REGISTRY.items():
            exp[var] = {
                "role":    e.role,
                "company": e.company,
                "date":    e.date,
                "bullets": [_strip_latex(b) for b in (e.highlights or [])],
            }
        proj: dict = {}
        for var, p in PROJECT_REGISTRY.items():
            proj[var] = {
                "title":   p.title,
                "date":    p.date,
                "bullets": [_strip_latex(b) for b in (p.highlights or [])],
            }
        return {"experience": exp, "projects": proj}
    except Exception as exc:  # noqa: BLE001
        print(f"  [warn] Could not load profile ground truth: {exc}")
        return {}


# ── Formatting helpers ────────────────────────────────────────────────────────

def _fmt_resume(content: dict) -> str:
    lines = [
        f"=== RESUME: {content['company'].upper()} — {content['role']} ===",
        "",
        "SUMMARY:",
        content["summary"] or "(none)",
        "",
        "SKILLS:",
    ]
    for s in content["skills"]:
        lines.append(f"  • {s}")

    lines += ["", "EXPERIENCE:"]
    for exp in content["experience"]:
        lines.append(f"\n  {exp['role']}  @  {exp['company']}  |  {exp['date']}")
        for b in exp["bullets"]:
            lines.append(f"    - {b}")

    lines += ["", "PROJECTS:"]
    for proj in content["projects"]:
        header = proj["title"]
        if proj["aim"]:
            header += f"  ({proj['aim'][:80]})"
        lines.append(f"\n  {header}  |  {proj['date']}")
        for b in proj["bullets"]:
            lines.append(f"    - {b}")

    return "\n".join(lines)


def _fmt_cl(content: dict) -> str:
    lines = [
        f"=== COVER LETTER: {content['company'].upper()} — {content['role']} ===",
        "",
    ]
    for i, para in enumerate(content["paragraphs"], 1):
        lines.append(f"[Paragraph {i}]")
        lines.append(para)
        lines.append("")
    return "\n".join(lines)


def _fmt_ground_truth(truth: dict) -> str:
    lines = ["=== PROFILE GROUND TRUTH ===", ""]
    lines.append("EXPERIENCE:")
    for var, e in (truth.get("experience") or {}).items():
        lines.append(f"\n  [{var}] {e['role']} @ {e['company']}  |  {e['date']}")
        for b in e["bullets"]:
            lines.append(f"    TRUTH: {b}")
    lines.append("\nPROJECTS:")
    for var, p in (truth.get("projects") or {}).items():
        lines.append(f"\n  [{var}] {p['title']}  |  {p['date']}")
        for b in p["bullets"]:
            lines.append(f"    TRUTH: {b}")
    return "\n".join(lines)


# ── Audit phases ──────────────────────────────────────────────────────────────

def audit_resume(jd_text: str, resume_content: dict, model: str) -> str:
    print("  Phase 1: Resume audit...")
    system = (
        "You are a senior hiring manager doing a rigorous first-pass review of "
        "an application. Find weaknesses ruthlessly. Quote the exact bullet text "
        "when critiquing it. Never invent facts or metrics — only flag what is or "
        "is not present in the document you are given. Score each dimension 1–10."
    )
    user = f"""JOB DESCRIPTION (what we need):
{jd_text[:4000] if jd_text else "(not provided)"}

---
{_fmt_resume(resume_content)}

---
Audit the resume above. Be direct and specific.

## Resume Audit

### ATS & Human First Impression
- **ATS readiness (0–100):** estimate how well this resume would survive an ATS /
  keyword screen for *this* JD. Cite which critical JD keywords are present vs
  absent. One sentence on what would move the score most.
- Human 6-second scan score (1–10) — does the top third of the page signal fit?

### Bullet Quality — Experience
For each experience section:
- Are bullets achievement-oriented or duty-list?
- Do they follow XYZ: Action + What + How/Tool + Metric?
- Which specific bullets are weakest? Quote them. Explain the flaw. Suggest a rewrite direction (do NOT invent metrics — only restructure or flag that a metric is missing).
- Which bullets to reorder or cut?

### Bullet Quality — Projects
Same assessment for project bullets. Flag any projects that should be swapped for a more JD-relevant one.

### Summary Assessment
- Does it name the company explicitly?
- Is it differentiated or boilerplate?
- Does it reflect the seniority / scope of this specific role?

### Skills Section
- Are the JD's top hard requirements visible?
- Any mismatch between claimed skills and the evidence in the bullets?

### Keyword Gaps
List the top 6–8 JD terms / phrases that do NOT appear in the resume.

### Priority Fixes (Top 3)
The three changes with highest expected impact on pass rate, ordered."""

    return complete(system, user, model, max_tokens=2000)


def audit_cover_letter(jd_text: str, cl_content: dict, model: str) -> str:
    print("  Phase 2: Cover letter audit...")
    system = (
        "You are a hiring manager who reads dozens of cover letters weekly. "
        "Find what makes this one weak, generic, or unconvincing — then give "
        "specific rewrite suggestions. Do NOT invent facts about the candidate; "
        "only judge what is on the page."
    )
    user = f"""JOB DESCRIPTION:
{jd_text[:3000] if jd_text else "(not provided)"}

---
{_fmt_cl(cl_content)}

---
Audit this cover letter. Quote text you are critiquing.

## Cover Letter Audit

### JD fit snapshot
- Cover-letter-only fit vs this JD (0–100), one sentence why.

### Opening Hook (Paragraph 1)
- Does it open with energy or with "I am writing to apply..."?
- Is it specific to this company (product, mission, research area, recent news) or generic?
- Confidence / tone calibrated to seniority of the role?
- Suggested rewrite of the first sentence if weak (do NOT add facts — only restructure or note what is missing).

### Evidence Paragraph (Paragraph 2)
- Are the achievements chosen the strongest relevant proof points for this JD?
- Are metrics present and specific?
- Does the paragraph connect explicitly to the JD's top requirements?
- Quote the weakest sentence and explain what is missing.

### Closing (Paragraph 3)
- Is the call-to-action confident or tentative?
- Does it avoid filler ("I believe I would be a great fit")?
- Specific rewrite direction if weak.

### Overall
- Tone: confident / generic / appropriate for seniority?
- Does this differentiate the candidate or blend in with the stack?
- Page-length risk: is any paragraph unnecessarily long?

### Priority Fixes (Top 2)
Two highest-ROI changes, ordered."""

    return complete(system, user, model, max_tokens=1500)


def audit_factual_accuracy(resume_content: dict, ground_truth: dict, model: str) -> str:
    print("  Phase 3: Factual accuracy check...")
    if not ground_truth:
        return (
            "## Factual Accuracy Check\n\n"
            "_Profile ground truth not available (profile/master_data.py not importable). "
            "Ensure the private/ submodule is checked out._\n"
        )

    selected_lines = ["SELECTED (tailored) bullets:"]
    for exp in resume_content.get("experience") or []:
        selected_lines.append(f"\n{exp['role']} @ {exp['company']}:")
        for b in exp.get("bullets") or []:
            selected_lines.append(f"  SELECTED: {b}")
    for proj in resume_content.get("projects") or []:
        selected_lines.append(f"\nProject — {proj['title']}:")
        for b in proj.get("bullets") or []:
            selected_lines.append(f"  SELECTED: {b}")

    truth_text = _fmt_ground_truth(ground_truth)
    selected_text = "\n".join(selected_lines)

    system = (
        "You are an editor fact-checking a resume against its original source material. "
        "Flag any selected (tailored) bullet that: overstates impact, adds metrics not "
        "present in the original, changes the technology/tool used, or otherwise diverges "
        "materially from the ground truth. If a rewrite rephrases the same fact more "
        "strongly without changing what happened, that is acceptable — do not flag it. "
        "Be precise: quote both versions."
    )
    user = f"""Compare the selected (tailored) bullets against the profile ground truth.

{selected_text[:3500]}

---
{truth_text[:3500]}

---
## Factual Accuracy Check

For each bullet that materially diverges from its ground-truth source:
- **Selected bullet:** (quote)
- **Closest ground-truth source:** (quote)
- **Issue:** what was added, changed, or exaggerated
- **Fix direction:** how to restate accurately (do NOT invent new facts)

If a selected bullet has no clear match in the ground truth (entirely invented),
flag it as **⚠ No source found**.

If all selected bullets are faithful rewrites, say so explicitly.

End with a one-sentence overall verdict."""

    return complete(system, user, model, max_tokens=1500)


def synthesize_action_plan(
    resume_audit: str,
    cl_audit: str,
    factual_audit: str,
    job_id: str,
    model: str,
) -> str:
    print("  Phase 4: Synthesising action plan...")
    system = (
        "You are a career coach distilling three critique reports into a single "
        "prioritised action plan. Remove duplication. Keep it concrete and brief."
    )
    user = f"""Three audit reports for application `{job_id}`:

--- RESUME AUDIT ---
{resume_audit[:2500]}

--- COVER LETTER AUDIT ---
{cl_audit[:2000]}

--- FACTUAL ACCURACY ---
{factual_audit[:1500]}

Produce a prioritised action plan:

## Prioritised Action Plan

### Compatibility & ATS scores
- **Overall compatibility (0–100):** how well the *combined* resume + cover letter
  hold up against this JD's requirements (must-haves, seniority, evidence). Give
  the integer score, then 2–3 bullets justifying it (cite gaps or strengths).
- **ATS readiness (0–100):** estimate of keyword / structured-scan survival for
  this JD based on the resume audit. Give the integer score and the top missing
  keywords that drag it down (or say why it is already strong).

### 🔴 Must Fix (blocks submission)
Up to 3 items that must be corrected before submitting — factual errors, missing
critical JD keywords, or passages that would immediately disqualify.

### 🟡 High Impact (do before submitting if time allows)
Up to 5 changes with the highest expected ROI on pass rate, ordered.

### 🟢 Nice to Have (polish pass)
Up to 3 lower-priority improvements.

### ✅ What Is Working Well
2–3 genuine strengths to preserve so edits do not accidentally break them."""

    return complete(system, user, model, max_tokens=1000)


# ── Main orchestrator ─────────────────────────────────────────────────────────

def write_audit_report(report: str, out_path: Path) -> Path:
    """Write or append an audit report (like follow-up drafts — never overwrite history)."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    existing = out_path.read_text(encoding="utf-8") if out_path.exists() else ""
    if existing.strip():
        text = existing.rstrip() + "\n\n---\n\n" + report.lstrip()
    else:
        text = report
    out_path.write_text(text, encoding="utf-8")
    return out_path


def audit(job_id: str, model: str) -> str:
    """
    Run the full 4-phase audit pipeline for *job_id*.

    Returns the assembled markdown report as a string.
    """
    print(f"\n{'='*60}")
    print(f"  Audit: {job_id}")
    print(f"  Provider: {resolve_provider()}  |  Model: {model}")
    print(f"{'='*60}")

    jd_text = read_jd(job_id)
    if not jd_text:
        print("  [warn] jd.txt not found — audit will be less precise without the JD.")
        print(f"         Save the JD manually to: "
              f"{data_path('applications', 'jobs', job_id, 'jd.txt')}")

    resume_content = read_resume_content(job_id)
    cl_content     = read_cl_content(job_id)
    ground_truth   = read_ground_truth()

    print(f"  Company  : {resume_content['company']}  |  Role: {resume_content['role']}")
    print(f"  Exp entries : {len(resume_content['experience'])}"
          f"  Projects: {len(resume_content['projects'])}"
          f"  CL paras: {len(cl_content['paragraphs']) if cl_content else 0}")
    print(f"  Ground truth: "
          f"{len(ground_truth.get('experience', {}))} exp entries, "
          f"{len(ground_truth.get('projects', {}))} projects")
    print()

    resume_audit  = audit_resume(jd_text, resume_content, model)
    if cl_content is None:
        print("  Phase 2: Cover letter audit... [skip — no cover letter source]")
        cl_audit = (
            "## Cover Letter Audit\n\n"
            "_Skipped — no cover letter source found "
            f"(`coverletter/outputs/{job_id}_cl.py`). "
            "Resume/factual phases still ran._\n"
        )
    else:
        cl_audit = audit_cover_letter(jd_text, cl_content, model)
    factual_audit = audit_factual_accuracy(resume_content, ground_truth, model)
    action_plan   = synthesize_action_plan(
        resume_audit, cl_audit, factual_audit, job_id, model
    )

    report = f"""# Application Audit — {resume_content['company']}: {resume_content['role']}

**Application ID:** `{job_id}`
**Generated:** {datetime.date.today().isoformat()}
**Model:** `{resolve_provider()}/{model}`

> ⛔ This audit is advisory only. Never apply suggestions that invent metrics or facts
> not already present in your profile ground truth (`profile/`).

---

{action_plan}

---

{resume_audit}

---

{cl_audit}

---

{factual_audit}
"""
    return report


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Audit a tailored resume and cover letter from a hiring manager's "
            "perspective. Reads tailoring files + JD + profile ground truth, "
            "then writes applications/jobs/<id>/audit.md."
        )
    )
    parser.add_argument("--id", "-i", required=True,
                        help="Application id, e.g. nvidia_ml_2026")
    parser.add_argument("--model", default=None,
                        help="Model name override for this run only.")
    parser.add_argument("--use-agent", action="store_true",
                        help="Use the task-specific model from .env for this run instead of the base model.")
    parser.add_argument("--provider", default=None,
                        choices=["anthropic", "ollama", "openai"],
                        help="Override the provider for this run only (sets LLM_PROVIDER "
                             "in the current process, ignoring .env). Use when calling "
                             "from a cloud harness whose model differs from .env.")
    parser.add_argument("--out", default=None,
                        help="Also write a copy to this path "
                             "(always writes applications/jobs/<id>/audit.md)")
    args = parser.parse_args()

    # Override LLM_PROVIDER in the current process when --provider is supplied.
    # Direct assignment wins over the setdefault values load_env() already wrote.
    if args.provider:
        os.environ["LLM_PROVIDER"] = args.provider

    # Resolve model after the provider override so get_default_model() returns
    # the correct default for the chosen provider.
    model = args.model or get_default_model(task="audit", use_task_model=args.use_agent)

    try:
        report = audit(args.id, model)
    except FileNotFoundError as exc:
        print(f"\n[x] {exc}")
        sys.exit(1)

    destinations: list[Path] = [
        data_path("applications", "jobs", args.id, "audit.md"),
    ]
    if args.out:
        destinations.append(Path(args.out))

    written: list[Path] = []
    seen: set[str] = set()
    for dest in destinations:
        dest.parent.mkdir(parents=True, exist_ok=True)
        key = str(dest.resolve())
        if key in seen:
            continue
        seen.add(key)
        write_audit_report(report, dest)
        written.append(dest)
        print(f"\n[+] Audit report → {dest}")

    # Print the action plan to stdout so the agent sees it immediately.
    start = report.find("## Prioritised Action Plan")
    end   = report.find("\n---\n", start) if start >= 0 else -1
    if start >= 0:
        snippet = report[start : end if end > start else start + 2500]
        print("\n" + "─" * 60)
        print(snippet)
        print("─" * 60)
    print(f"\n  Full report: {written[0]}")
    print("  Next: fix 🔴 items in resume/outputs/<id>.py and "
          "coverletter/outputs/<id>_cl.py, then rebuild and re-audit.")


if __name__ == "__main__":
    main()
