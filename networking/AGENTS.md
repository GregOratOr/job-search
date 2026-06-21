# Networking Context

## Files

```
networking/
├── strategy.md            # Full networking workflow (read this first)
├── message_templates.md   # Copy-paste templates for LinkedIn/email
└── connections.csv        # Log of people contacted
```

## Connections CSV Schema

```
date, name, company, title, linkedin_url, application_id, status, last_contact, notes
```

Valid `status` values:
- `Pending`      — connection request sent, not yet accepted
- `Connected`    — accepted, no message sent yet
- `Messaged`     — first message sent, awaiting reply
- `Replied`      — they replied; conversation active
- `Info Chat`    — had a call/chat
- `Referral`     — submitted a referral
- `Cold`         — no response after 2+ follow-ups

## Logging a New Connection

Manually append a row to `networking/connections.csv`, or use:
```bash
# After logging the application:
python scripts/track.py update --id google_swe_2026 \
    --notes "Connected with Jane Doe (ML Eng) on LinkedIn 2026-06-09"
```

## Quick Reference — Message Templates

| Situation                         | Template location                              |
|-----------------------------------|------------------------------------------------|
| Connection request                | `message_templates.md` → Connection Requests  |
| First message after connecting    | `message_templates.md` → Follow-Up            |
| Asking for a referral             | `message_templates.md` → Referral Ask         |
| Thank you after info chat         | `message_templates.md` → Thank-You            |
| Following up on application       | `message_templates.md` → Follow-Up on App     |

## Key Rule

Never ask for a referral in the connection request. Build rapport first —
at least one genuine exchange before making any ask.
