# Resume & Cover Letter Writing Reference

A complete, durable reference for drafting `highlights` (experience, project, research),
`summaries`, and cover letter paragraphs in this project. **Consult this file during every
profile/tailoring edit** — it is the long-form source behind the condensed
"Writing Bullet Points & Summaries — Style Guide" in the root `AGENTS.md`.

Contents:
1. [The XYZ bullet formula](#1-the-xyz-bullet-formula)
2. [Harvard MCS resume guidelines (full)](#2-harvard-mcs-resume-guidelines-full)
3. [Action verbs (full bank, by category)](#3-action-verbs-full-bank-by-category)
4. [Per-section guidance (experience / projects / research / summary)](#4-per-section-guidance)
5. [Cover letter tips (full)](#5-cover-letter-tips-full)
6. [Using AI responsibly](#6-using-ai-responsibly)
7. [LaTeX formatting rules for this project](#7-latex-formatting-rules-for-this-project)

Primary source: Harvard FAS Mignone Center for Career Success —
<https://careerservices.fas.harvard.edu/resources/create-a-strong-resume/>

---

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

## 2. Harvard MCS resume guidelines (full)

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

## 4. Per-section guidance

How the rules above apply to each entry type in `profile/` and `resume/tailoring/{id}.py`.

### Experience (`highlights`)

- Past tense for finished roles; present tense only for a current role.
- One accomplishment per bullet, each following the XYZ formula.
- 1–3 bullets per entry in a tailored resume — most relevant first.
- Front-load impact; bury context. Quantify scale (users, GPUs, latency, %, $, throughput).

### Projects (`highlights`)

- Same XYZ shape, but emphasize **technical approach → scale/scope → outcome**.
  - Technical approach: "Implemented X using Y achieving Z."
  - Scale/scope: "Trained on N samples / N GPUs / N agents."
  - Outcome: "Deployed as Z; reduced latency by N\%."
- Name the concrete tools/frameworks; bold them with `\textbf{}`.

### Research (`highlights`)

- Emphasize the **problem, method, and findings**; cite frameworks, datasets, baselines.
- Outcomes can be insights, benchmarks, or comparisons rather than business metrics.
- Still active voice + action verbs (Designed, Implemented, Evaluated, Investigated).

### Summary (`SUMMARIES` / tailored summary)

- 3–4 sentences, **no bullets**: **who you are → what you build → what you want**.
- Active, specific, fact-based; no pronouns where avoidable; no flowery language.
- In a tailored summary, **name the company explicitly**.
- Bold a few headline strengths with `\textbf{}`.

---

## 5. Cover letter tips (full)

A cover letter is a writing sample and part of the screening process. Articulate why you fit
*this* role at *this* organization.

### General rules about letters

- Address your letter to a specific person if you can.
- Tailor each letter to the specific situation/organization by researching before writing.
- Keep letters concise and factual — no more than a single page. Avoid flowery language.
- Give examples that support your skills and qualifications.
- Put yourself in the reader's shoes: what convinces them you are ready and able to do the job?
- Don't overuse the pronoun "I".
- Remember it's a marketing tool — use plenty of action words.
- Have an advisor (or trusted reviewer) provide feedback.
- When converting to `.pdf`, check that the formatting translates correctly.
- Reference skills/experiences from the job description and draw connections to your credentials.
- Ensure your resume and cover letter use the **same font type and size**.

### Recommended paragraph structure (project convention)

1. **Opening / hook** — why you're excited about *this company* and *this specific role*;
   mention one concrete thing about the company (product, research direction, mission).
2. **Evidence** — your strongest relevant experience with a metric, connected explicitly to
   the job description. Add context or emphasis; don't just restate the resume.
3. **Close** — a forward-looking sentence + a confident, brief call to action.

(See `coverletter/AGENTS.md` for the dataclass/build mechanics.)

---

## 6. Using AI responsibly

Your resume and cover letter should authentically represent who you are and what you offer.
Generative AI is a useful **editing** tool — to brainstorm bullet revisions, incorporate
keywords from a job description, or improve what you already have. It should **not** be the
primary author; its raw output is generic and must be grounded in true, specific facts.
In this project: AI selects/rewords entries, but every claim must trace back to real profile
data — never fabricate metrics, tools, or experience.

---

## 7. LaTeX formatting rules for this project

Bullets and summaries are rendered through the LaTeX engine, so:

- Bold key technical terms with `\textbf{...}` (skills, tools, frameworks, headline metrics).
- Keep each bullet under ~200 characters so it stays on 1–2 lines in the PDF.
- Multiplication factor: `2.3\texttimes{}`. Percentages: `40\%`.
- Escape LaTeX special characters in all bullet/summary text:
  `%` → `\%`, `&` → `\&`, `$` → `\$`, `_` → `\_`, `#` → `\#`.
