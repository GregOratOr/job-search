## 1. The XYZ bullet formula

Google's widely-cited formula for accomplishment statements:

> **"Accomplished [X], as measured by [Y], by doing [Z]."**

- **X** = the accomplishment / impact (what got better)
- **Y** = the metric that proves it (how you know)
- **Z** = the action / method / tools you used to get there

Worked example:

> *Accomplished* a 2.3\texttimes{} faster inference path (**X**), *as measured by* p99 latency
> dropping from 180 ms to 78 ms (**Y**), *by doing* CUDA kernel fusion and FP16 quantization (**Z**).

In a tight resume bullet this compresses to:

> **[Action verb] + [what you built/did] + [tools / how] + [quantified result]**

Lead with the action verb, end with the metric. If a hard metric (**Y**) genuinely does not
exist, still close with a concrete outcome (shipped, adopted, reduced, enabled, unblocked) —
never stop at describing the task. **Never invent numbers.**

---

## 2. Harvard MCS resume guidelines

### Resume language should be

- Specific rather than general
- Active rather than passive
- Written to express, not impress
- Articulate rather than "flowery"
- Fact-based (quantify and qualify)
- Written for people who / systems that scan quickly

### Top five resume mistakes

1. Spelling and grammar errors
2. Missing email and phone information
3. Using passive language instead of "action" words
4. Not well organized, concise, or easy to skim
5. Not demonstrating results

### DON'T

- Use personal pronouns (such as *I* or *We*)
- Abbreviate
- Use a narrative style
- Use slang or colloquialisms
- Include a picture
- Include age or gender
- List references
- Start each line with a date

### DO

- Be consistent in format and content
- Make it easy to read and follow, balancing white space
- Use consistent spacing, underlining, italics, bold, and capitalization for emphasis
- List headings (such as Experience) in order of importance
- Within headings, list information in reverse chronological order (most recent first)
- Avoid information gaps such as a missing summer
- Be sure that your formatting will translate properly if converted to a `.pdf`

### Working internationally

Resume guidelines can vary from country to country. If targeting roles abroad, research the
norms for that country (length, photo, personal details) before reusing a US-style resume.

---

## 3. Action verbs (full bank, by category)

Start every bullet with a strong action verb. Pick the category that matches the work, and
**do not reuse the same verb twice within one entry**.

### Leadership

Accomplished, Achieved, Administered, Analyzed, Assigned, Attained, Chaired, Consolidated,
Contracted, Coordinated, Delegated, Developed, Directed, Earned, Evaluated, Executed,
Handled, Headed, Impacted, Improved, Increased, Led, Mastered, Orchestrated,
Organized, Oversaw, Planned, Predicted, Prioritized, Produced, Proved, Recommended,
Regulated, Reorganized, Reviewed, Scheduled, Spearheaded, Strengthened, Supervised, Surpassed

### Communication

Addressed, Arbitrated, Arranged, Authored, Collaborated, Convinced, Corresponded, Delivered,
Developed, Directed, Documented, Drafted, Edited, Energized, Enlisted, Formulated,
Influenced, Interpreted, Lectured, Liaised, Mediated, Moderated, Negotiated, Persuaded,
Presented, Promoted, Publicized, Reconciled, Recruited, Reported, Rewrote, Spoke,
Suggested, Synthesized, Translated, Verbalized, Wrote

### Research

Clarified, Collected, Concluded, Conducted, Constructed, Critiqued, Derived, Determined,
Diagnosed, Discovered, Evaluated, Examined, Extracted, Formed, Identified, Inspected,
Interpreted, Interviewed, Investigated, Modeled, Organized, Resolved, Reviewed, Summarized,
Surveyed, Systematized, Tested

### Technical

Assembled, Built, Calculated, Computed, Designed, Devised, Engineered, Fabricated,
Installed, Maintained, Operated, Optimized, Overhauled, Programmed, Remodeled, Repaired,
Solved, Standardized, Streamlined, Upgraded

### Teaching

Adapted, Advised, Clarified, Coached, Communicated, Coordinated, Demystified, Developed,
Enabled, Encouraged, Evaluated, Explained, Facilitated, Guided, Informed, Instructed,
Persuaded, Set Goals, Stimulated, Studied, Taught, Trained

### Quantitative

Administered, Allocated, Analyzed, Appraised, Audited, Balanced, Budgeted, Calculated,
Computed, Developed, Forecasted, Managed, Marketed, Maximized, Minimized, Planned,
Projected, Researched

### Creative

Acted, Composed, Conceived, Conceptualized, Created, Customized, Designed, Developed,
Directed, Established, Fashioned, Founded, Illustrated, Initiated, Instituted, Integrated,
Introduced, Invented, Originated, Performed, Planned, Published, Redesigned, Revised,
Revitalized, Shaped, Visualized

### Helping

Assessed, Assisted, Clarified, Coached, Counseled, Demonstrated, Diagnosed, Educated,
Enhanced, Expedited, Facilitated, Familiarized, Guided, Motivated, Participated, Proposed,
Provided, Referred, Rehabilitated, Represented, Served, Supported

### Organizational

Approved, Accelerated, Added, Arranged, Broadened, Cataloged, Centralized, Changed,
Classified, Collected, Compiled, Completed, Controlled, Defined, Dispatched, Executed,
Expanded, Gained, Gathered, Generated, Implemented, Inspected, Launched, Monitored,
Operated, Organized, Prepared, Processed, Purchased, Recorded, Reduced, Reinforced,
Retrieved, Screened, Selected, Simplified, Sold, Specified, Steered, Structured,
Systematized, Tabulated, Unified, Updated, Utilized, Validated, Verified

---

## 4. Per-section guidance (YAML schema)

### Experience (`experience` → `bullets`)

- Past tense for finished roles; present tense only for a current role.
- One accomplishment per bullet, each following the XYZ formula.
- 1–3 bullets per entry in a tailored resume — most relevant first.
- Front-load impact; bury context. Quantify scale (users, GPUs, latency, %, $, throughput).
- Each bullet is either:
  - `rewrite: "text"` — new wording hitting JD keywords
  - `use_profile: idx` — verbatim from profile entry's highlights[idx]
- Every entry requires `source` (profile entry id) and `rationale` (why selected).

### Projects (`projects` → `bullets`)

- Same XYZ shape, but emphasize **technical approach → scale/scope → outcome**.
  - Technical approach: "Implemented X using Y achieving Z."
  - Scale/scope: "Trained on N samples / N GPUs / N agents."
  - Outcome: "Deployed as Z; reduced latency by N\%."
- Name the concrete tools/frameworks; bold them with `\textbf{}`.
- Same `rewrite` / `use_profile` structure as experience.
- Every entry requires `source` and `rationale`.

### Research (`research` → `bullets`)

- Emphasize the **problem, method, and findings**; cite frameworks, datasets, baselines.
- Outcomes can be insights, benchmarks, or comparisons rather than business metrics.
- Still active voice + action verbs (Designed, Implemented, Evaluated, Investigated).
- Same `rewrite` / `use_profile` structure. Requires `source` and `rationale`.

### Summary (`summary`)

- 3–4 sentences, **no bullets**: **who you are → what you build → what you want**.
- Active, specific, fact-based; no pronouns where avoidable; no flowery language.
- In a tailored summary, **name the company explicitly** (at your discretion per SKILL.md).
- Bold a few headline strengths with `\textbf{}`.
- Custom per job — do not use profile preset keys directly.
- **Length target**: ~55–65 words total (~2–3 lines in PDF, ~21 words/line at 10pt). Max 3 lines.

### Skills (`skills`)

- Subset from `private/profile/skills.yaml` inventory (values or aliases).
- Loader hard-fails on unknown skills.
- Pick preset covering most JD `normalized_keywords`.

### Education (`education`)

- Select entries by `source` (usually all).
- Reverse chronological order.

### Sections (`sections`)

Visibility flags (auto-decide per `selection.md`):
- `show_position_applied`: true
- `show_summary`: true
- `show_skills`: true
- `show_experience`: true (≥1 entry)
- `show_projects`: true (≥1 entry)
- `show_research`: true if JD asks for research OR ≥1 research entry scores ≥3.0
- `show_education`: true
- `show_coursework`: true only if JD explicitly asks OR candidate <2yr post-grad with no experience

---

## 5. LaTeX formatting rules (for resume.yaml text)

Bullets and summaries are rendered through the LaTeX engine via `loader.py` → `cv2latex.py`, so:

- Bold key technical terms with `\textbf{...}` (skills, tools, frameworks, headline metrics).
- Keep each bullet under ~200 characters so it stays on 1–2 lines in the PDF.
- Multiplication factor: `\texttimes{}`. Percentiles: `40\%`.
- Escape LaTeX special characters in all bullet/summary text:
  `%` → `\%`, `&` → `\&`, `$` → `\$`, `_` → `\_`, `#` → `\#`, `{` → `\{`, `}` → `\}`.
- **In YAML: use double backslash for literal backslash.** Example: `W\\&B` in YAML → `W\&B` in LaTeX → renders `W&B`.
- Loader validates escaping; fix before build.

---

## 6. Codebase references

| Artifact | Path |
|----------|------|
| Profile source data | `private/profile/{header,education,experience,projects,research,skills,summaries,coursework}.yaml` |
| Tailored resume | `private/applications/jobs/<id>/resume.yaml` |
| Job description | `private/applications/jobs/<id>/job.yaml` + `jd.txt` |
| Validation | `uv run scripts/loader.py --resume <id>` |
| Build PDF | `uv run scripts/build.py --id <id> --pdf` |
| Selection rules | `skills/tailor-resume/selection.md` |
| Pre-build checks | `skills/tailor-resume/tailoring-checks.md` |
| Skill workflow | `skills/tailor-resume/SKILL.md` |