---
name: networking-outreach
description: Draft LinkedIn connection requests, follow-ups, cold emails, and referral asks from the project's templates for a target contact at a company. Use when the user wants outreach messages or to log a networking connection.
---

# Networking Outreach

## Steps
1. Read the workflow and copy in:
   - `networking/strategy.md` (the 4-step Find→Connect→Engage→Convert loop)
   - `networking/message_templates.md` (connection request, follow-up, referral ask, thank-you)
2. To find WHO to contact, use the `find-contacts` skill
   (`uv run scripts/find_contacts.py --company <co> --id <id>`), which writes a `## Contacts`
   section into the bundle's `networking.md`.
3. Personalize a message for the specific person/company. Keep connection requests
   ≤300 chars and specific (shared school/team/project).
4. If an application bundle exists, copy ready-made messages from
   `applications/jobs/<id>/networking.md` (drafted by tailoring; never auto-sent).
5. Log the contact by appending a row to `networking/connections.csv`:
   `date, name, company, title, linkedin_url, application_id, status, last_contact, notes`

## Key rule
Never ask for a referral in the first connection request — build at least one genuine
exchange first.

## Pitfalls
- `status` must be one of: Pending, Connected, Messaged, Replied, Info Chat, Referral, Cold.