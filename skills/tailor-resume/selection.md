# Selection Reference — tailor-resume

**Read this before every tailoring run.** Defines how to score, pick, and order profile entries against a JD.

---

## Scoring rubric (explicit, lightweight, scores shown)

Score each profile entry (experience, project, research) 0–5 on four dimensions. Show scores in chat; write `rationale` in `resume.yaml`.

| Dimension | Weight | What to measure |
|-----------|--------|-----------------|
| **Keyword overlap** | 35% | Count of JD `normalized_keywords` / `hard_requirements` addressed by the entry's highlights (verbatim or rewritten). |
| **Domain match** | 30% | Does the entry's core domain (RL, CV, LLM, systems, data eng, etc.) match the JD's primary asks? |
| **Recency + seniority signal** | 20% | More recent = higher. Lead/ownership language = higher. Intern > fellowship > coursework. |
| **Scale / metric density** | 15% | Bullets with quantified outcomes (latency, throughput, %, $, users, GPUs, params) score higher. |

**Total** = weighted sum. Round to 1 decimal. Tie-break: recency > seniority > metrics.

**Thresholds:**
- ≥ 3.5 → strong include
- 2.5–3.4 → include if budget allows
- < 2.5 → exclude unless unique coverage of a hard requirement

---

## Selection budgets (soft targets + hard caps)

| Category | Soft target | Hard cap | Ordering |
|----------|-------------|----------|----------|
| Experience entries | 2–3 | 3 | By score desc, then recency desc |
| Bullets per experience entry | 2–3 | 5 | By relevance to JD (top keywords first) |
| Projects | 2–4 | 4 | By score desc |
| Bullets per project | 1–2 | 3 | By relevance |
| Research entries | 0–2 | 2 | By score desc (only if section visible) |
| Skills categories | 3–5 | 5 | Prioritize categories covering JD keywords |
| Summary | 1 custom | 1 | — |
| Education | All | All | Reverse chronological |

**Hard cap = 1 page.** If the rendered PDF exceeds 1 page, the fit loop trims per the ladder in `SKILL.md`.

---

## Section visibility rules (auto-decide)

| Section | Show when |
|---------|-----------|
| `show_position_applied` | Always true (role in header) |
| `show_summary` | Always true (custom per job) |
| `show_skills` | Always true |
| `show_experience` | Always true (≥ 1 entry) |
| `show_projects` | Always true (≥ 1 entry) |
| `show_research` | **True** if: JD `hard_requirements` or `nice_to_have` mentions research, publications, PhD, novel algorithms, OR ≥ 1 research entry scores ≥ 3.0. **False** otherwise. |
| `show_coursework` | **True** only if: JD explicitly asks for coursework / recent grad / specific courses, OR candidate < 2 years post-grad and no experience entries. **False** otherwise. |
| `show_education` | Always true |

---

## Skill selection

From `profile/skills.yaml` presets, pick the preset that covers the most JD `normalized_keywords`. If two tie, prefer more specific (ML_FOCUSED > FULL). List the chosen preset in `resume.yaml` and which categories are included.

---

## Rationale format (in resume.yaml)

```yaml
experience:
  - source: AI_INTEGRATOR_DAKDAN
    rationale: "Technical lead on 15-engineer LLM platform; LLM routing, outcome classification, objection handling — directly hits post-training, serving systems, agentic platform"
    bullets:
      - use_profile: 0
      - rewrite: "Built LLM outcome classifier scoring call transcripts into structured JSON with confidence — predictive modeling over unstructured text — plus multi-provider routing hub with latency/cost/quality failover"
```

Every entry gets a one-line `rationale` citing the specific JD keywords/requirements it covers.