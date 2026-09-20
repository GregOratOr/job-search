# Tailoring Checks Reference — tailor-resume

**Run these checks before every build.** They are the pre-build self-review. The agent must pass all checks (or document why not) before handing off to `build.py`.

---

## Check 1: Fact traceability (fabrication guard)

**Rule:** Every bullet in `resume.yaml` must trace to a profile entry. No invented metrics, tools, scope, or ownership.

**Procedure:**
1. For each entry in `resume.yaml` (experience, projects, research):
   - Load the profile source entry by `source` id.
   - For each bullet:
     - If `use_profile: idx`: verify the text matches the profile bullet exactly (LaTeX escapes allowed).
     - If `rewrite: "text"`: verify every **metric** (numbers, %, ×, $, latency, throughput, params, GPU count, dataset size, user count, team size, duration), **tool/framework** (PyTorch, CUDA, Unity, etc.), and **claim of ownership/leadership** ("led", "owned", "sole", "architected") appears in the profile entry's highlights.
2. List any bullet where a metric/tool/claim has **no source** in the profile. These are 🔴 fabrication risks — must fix or drop.

**Output:** Chat must show a table:
| Entry | Bullet | Claim | Profile source | Status |
|-------|--------|-------|----------------|--------|

---

## Check 2: Keyword coverage (hybrid — cover hard reqs, flag gaps, ask user)

**Rule:** Cover as many `hard_requirements` from `job.yaml` as possible. Flag any missing in audit; ask user per-case what to do.

**Procedure:**
1. Load `job.yaml` → `hard_requirements` list.
2. For each requirement, search all bullets in `resume.yaml` (case-insensitive, substring match on key terms).
3. Report coverage:
   - ✅ Covered — which bullet(s)
   - ❌ Missing — requirement not addressed
4. For each ❌: check if profile has evidence to cover it.
   - If yes → suggest rewrite/add bullet, ask user to approve.
   - If no → flag as **genuine gap** (cannot honestly cover), ask user: drop requirement, note in cover letter, or accept gap.
5. Nice-to-haves: qualitative — report coverage, no hard bar.

---

## Check 3: Bullet length

**Rule:** Every bullet ≤ 200 chars (warning at > 150). Loader warns at > 200; we enforce ≤ 150 as soft target for density.

**Procedure:**
- Count chars of each bullet text (after LaTeX escapes).
- Flag any > 150 as ⚠️, > 200 as 🔴.

---

## Check 4: LaTeX escaping

**Rule:** All bullet/summary text must escape LaTeX specials: `%` `&` `$` `#` `_` `{` `}`. Loader validates this; we pre-check.

**Procedure:**
- Scan all text fields for unescaped specials (excluding inside `\cmd{...}`, `$...$`, `$$...$$`, and already-escaped `\%` etc.).
- Any hit = 🔴 — fix before build.

---

## Check 5: One-page fit (pre-flight)

**Rule:** The rendered PDF must be exactly 1 page with ≤ 1 empty line at bottom.

**Procedure:**
1. Run `uv run scripts/build.py --id <id> --pdf` (or use `build.py --keep-temp` + `pdfinfo`).
2. If > 1 page: enter fit loop (see `SKILL.md`).
3. If ≤ 1 empty line: ✅
4. If > 2 empty lines: ⚠️ under-filled — restore a bullet/project that earns space.

**Note:** This check requires a build. Run it after Checks 1–4 pass.

---

## Check 6: Skill inventory compliance

**Rule:** Every skill in `resume.yaml` must exist in `profile/skills.yaml` inventory (value or alias). Loader hard-fails on unknown skills.

**Procedure:**
- Load `profile/skills.yaml` → build allowed set.
- Check each skill item in `resume.yaml` against allowed set.
- Any unknown = 🔴 — remove or replace with allowed alias.

---

## Check 7: Summary quality

**Rule:** Custom per job, 3–4 sentences, names the company, grounded in profile facts, no pronouns where avoidable, bolds 2–3 headline strengths.

**Procedure:**
- Verify company name appears.
- Verify ≥ 2 `\textbf{...}` terms.
- Verify no "I am", "I have", "My experience".
- Verify every claim traces to profile (same as Check 1).

---

## Check 8: Section visibility matches rules

**Rule:** `sections` flags in `resume.yaml` must follow `selection.md` auto-decide rules.

**Procedure:**
- Verify `show_research` follows rule (JD asks for research OR ≥ 1 research entry scores ≥ 3.0).
- Verify `show_coursework` follows rule (JD asks for coursework OR candidate < 2yr post-grad with no experience).
- Any mismatch = ⚠️ — correct or justify.

---

## Check 9: Rationale present

**Rule:** Every selected entry (experience, project, research) has a `rationale` field in `resume.yaml`.

**Procedure:**
- Scan `resume.yaml` for missing `rationale`.
- Any missing = ⚠️ — add it.

---

## Checklist summary (agent must report)

```
=== TAILORING CHECKS ===
✅ Fact traceability: N bullets checked, 0 fabrications
✅ Keyword coverage: M/N hard requirements covered (list missing + genuine gaps)
✅ Bullet length: max X chars (Y bullets > 150)
✅ LaTeX escaping: 0 unescaped specials
✅ One-page fit: 1 page, Z empty lines
✅ Skill inventory: all K skills allowed
✅ Summary quality: company named, N bold terms, 0 pronouns
✅ Section visibility: matches rules
✅ Rationale present: all entries have rationale
```

If any 🔴 (fabrication, LaTeX, skill inventory, >1 page): **STOP**. Fix before build.
If ❌ hard requirements with profile evidence: **ASK USER** — suggest rewrite.
If ❌ hard requirements without profile evidence: **ASK USER** — genuine gap.
If only ⚠️: **PROCEED** but note in chat.