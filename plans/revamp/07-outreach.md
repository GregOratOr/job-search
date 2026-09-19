# Workstream 07 — `outreach` Skill (Goal 5)

> **Depends on workstream 02** (`job.yaml`) and reads workstream 03's `resume.yaml` for
> the evidence to cite.
>
> **Before writing anything, run a `grill-with-docs` session** (the `grilling` skill via
> `domain-modeling`): one question at a time, each with your recommended answer, resolving
> the open questions below. Look facts up in the repo yourself; put only decisions to the
> user. Do not implement until the user confirms shared understanding.

## Goal

Produce ready-to-send LinkedIn messages and a cold email for the company, specific enough
to this role and this candidate that the user only fills in the recipient's name before
sending.

## Decisions already locked

- Output is **`outreach.md`** in the job folder.
- Messages are **drafted with real content** — company, role, team, and the user's
  matching evidence already written in. The only blanks are `[Name]` and `[Title]`.
- **Includes LinkedIn search strings** the user pastes themselves to find the right
  person.
- **No people discovery.** `find-contacts`, `find_contacts.py`, and the web tooling are
  all deleted. The skill never names a real individual it has not been told about, and
  never asserts facts about a specific person.
- Zero LLM calls in Python. This is entirely agent authoring.
- Nothing is ever sent automatically. The skill produces text; the user sends it.

## Current state

- `networking/message_templates.md`, `networking/strategy.md`, and
  `networking/connections.csv` exist (with real versions under `private/networking/`).
  `strategy.md` describes a four-step loop — Find, Connect, Engage, Convert.
- [networking/AGENTS.md](../../networking/AGENTS.md) documents the connections CSV schema
  and one hard rule worth preserving: **never ask for a referral in the connection
  request** — build rapport with at least one genuine exchange first.
- The old `networking.md` per job contained: LinkedIn search queries, a connection request
  under 300 characters, a follow-up to send three to seven days after connecting, a cold
  email with a subject line, and a referral ask. That inventory is a reasonable starting
  point.
- [skills/networking-outreach/SKILL.md](../../skills/networking-outreach/SKILL.md) is the
  predecessor skill; `skills/find-contacts/` and `skills/follow-up/` are being deleted.
- `connections.csv` and the follow-up tooling were part of the tracking layer that is
  being removed — decide deliberately whether any of it survives.

## Scope

**In scope**
- `skills/outreach/SKILL.md` and the message templates it draws on.
- The message set and what each one is for.
- How the evidence in each message is grounded in `resume.yaml` and `job.yaml`.
- The LinkedIn search strings: which ones, and how they are constructed from `job.yaml`.

**Out of scope**
- Finding or naming actual people.
- Sending anything.
- Follow-up scheduling and application tracking — both deleted.
- Cover letter content (workstream 04). A cold email to a recruiter and a cover letter are
  different artifacts with different audiences; keep them distinct.

## Grill the user on these before implementing

1. **Which messages?** Connection request, post-accept follow-up, cold email, referral
   ask — keep all four, or trim? *Recommend keeping all four; they are cheap to generate
   together and each maps to a distinct moment.*
2. **Templates versus fresh authoring.** Should the skill fill fixed templates from
   `networking/message_templates.md`, or write each message from scratch per job with the
   templates as tone guidance? *Recommend templates as structure and tone reference, with
   the substance written per job — fully templated messages read as templated.*
3. **Where templates live.** Keep `networking/` as a top-level directory, or move the
   templates inside the skill as reference files? *Recommend moving them into
   `skills/outreach/` so the skill is self-contained, and retiring `networking/`.*
4. **Does `connections.csv` survive?** It is the last remnant of the tracking layer. If
   the user still logs who they contacted, it stays; otherwise it goes with the rest.
   *Recommend deleting it unless the user actively uses it — a log nobody updates is
   worse than none.*
5. **Search strings.** How many, and targeting whom — recruiters, the hiring manager,
   alumni at the company, engineers on the named team? *Recommend three, one each for
   recruiter, team engineer, and alumni, built from `job.yaml`'s company, team, and role.*
6. **Alumni angle.** The old config carried `networking.alumni_networks`. Does the user
   want alumni framing baked into the messages, and from which institutions? *Recommend
   yes if they use it — it is the highest-response angle — sourced from the profile's
   education entries rather than a separate config file.*
7. **Evidence selection.** Should each message cite the same headline achievement the
   resume leads with, or deliberately vary? *Recommend the same headline for consistency,
   with the cold email allowed one extra specific detail.*
8. **Length limits.** LinkedIn connection requests cap at 300 characters. Should the skill
   enforce that mechanically or state it as a rule? *Recommend stating it and having the
   skill show the character count next to the message so the user can see it fits.*
9. **Tone calibration.** How formal? This varies a lot by person and industry. *Ask the
   user directly, and record the answer in the skill so it is not re-litigated every run.*
10. **When it runs.** Always as part of an application, or on demand? *Recommend on demand
    — outreach is worth it for target companies, not for every application.*

## Done criteria

- `skills/outreach/SKILL.md` exists, names no deleted script, and does not attempt to
  discover or name real people.
- A run produces `applications/jobs/<id>/outreach.md` containing the agreed messages, each
  specific to the company and role, with only `[Name]` and `[Title]` left blank.
- LinkedIn search strings are present and paste-ready.
- The no-referral-in-the-connection-request rule survives into the new skill.
- The fate of `networking/` and `connections.csv` is decided, and any deletion is queued
  for workstream 09.
