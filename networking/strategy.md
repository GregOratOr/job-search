# Networking Strategy

End-to-end workflow for finding relevant people, making connections, and
turning them into referrals or informational conversations.

---

## The 4-Step Networking Loop

```
FIND      →  CONNECT    →  ENGAGE    →  CONVERT
Job post     Send req.     Message       Referral /
LinkedIn     with note      after 3d     Info chat
search
```

---

## Step 1 — Find People at Target Companies

### Via LinkedIn

1. **Search from the job posting**: click the company name → "People" tab → filter by:
   - Title keywords: `ML Engineer`, `Research Engineer`, `Software Engineer`
   - School: `Oregon State University` or `Vishwakarma Institute of Technology` (shared alumni first)
   - Connections: check 2nd degree first (mutual intro is more effective)

2. **Use advanced search** (LinkedIn Premium or Boolean):
   - `site:linkedin.com/in/ "ML Engineer" "NVIDIA" "Oregon State"`
   - `"Machine Learning" AND "PyTorch" AND "NVIDIA" site:linkedin.com/in/`

3. **Target personas** (in order of warmth):
   - OSU / VIT alumni at the company ← highest response rate
   - Hiring manager for the team (usually Director/Manager of ML Eng)
   - A peer ML engineer on the relevant team
   - Recruiter at the company (helpful for interview prep info, less for technical referrals)

4. **Log targets** in `applications/jobs/{id}/job_info.py` under `NETWORKING_TARGETS`.

---

## Step 2 — Send Connection Request

**Always personalize** the connection note. The default "I'd like to connect" is ignored.
Use the templates in `networking/message_templates.md` → "Connection Request" section.

**Character limit**: 300 characters. Be direct, mention the shared context.

Examples:
- Alumni angle: "Hi [Name], fellow OSU alum here. I'm exploring ML Engineer roles at NVIDIA — would love to connect!"
- Shared tech angle: "Hi [Name], I came across your work on [project/paper]. Impressed by [specific thing] — would love to be in your network."
- Direct ask (for warm connections only): "Hi [Name], [mutual connection] suggested I reach out. Applying to [role] at [company] — would you be open to a quick chat?"

**Do not** ask for a referral in the connection request. Build the relationship first.

---

## Step 3 — Follow Up After Connecting (3–7 days later)

Only message after they accept. Use the "Follow-up after connecting" template.

Keep it short:
1. Thank them for connecting.
2. One sentence of genuine context (why you're reaching out *now*).
3. One specific ask: a 15-min call, or just a question you can answer via message.

Examples of asks:
- "Would you be open to a 15-minute call to share what it's like working on ML infra at NVIDIA?"
- "No need for a call — if you have a moment, I'd love your take on whether my background (M.S. AI, CUDA optimization) is a good fit for the [role] posting."

**Log the interaction** in `networking/connections.csv`.

---

## Step 4 — Convert to Referral or Interview Prep

### Getting a referral
Only ask after 1+ exchange. Be explicit but not pushy:
> "If you feel comfortable and my background seems like a fit, I'd really appreciate a referral for the [role] posting. No pressure at all — I understand if it's not a match."

Provide a referral package:
- 1-paragraph bio you wrote specifically for them to forward
- Link to your LinkedIn
- The job ID / req number

### Informational interview
Ask for 15 minutes on Zoom. Prepare 3–5 sharp questions:
- "What does day-to-day work look like for an ML engineer on your team?"
- "What skills differentiate strong candidates from average ones for this role?"
- "Is there anything in my background I should highlight or address in the interview?"
- "How does the interview process work — is there a system design or coding component?"

Always send a thank-you message within 24h.

---

## Tracking

Log every contact in `networking/connections.csv`:

```
python scripts/track.py log --id google_swe_2026 \
    --notes "Referred by Jane Doe (jane@gmail.com)"
```

And manually update `networking/connections.csv`:

```csv
date,name,company,title,linkedin_url,status,notes
2026-06-09,Jane Doe,Google,ML Engineer,https://linkedin.com/in/jane,Connected,Reached out re: SWE role
```

---

## Weekly Rhythm

| Day       | Task                                                              |
|-----------|-------------------------------------------------------------------|
| Monday    | Review job alerts (LinkedIn + Indeed + company websites)         |
| Monday    | Scaffold new applications (new_application.py)                   |
| Tue–Wed   | Tailor resumes + cover letters for that week's applications      |
| Wed–Thu   | Send connection requests to targets at companies you're applying |
| Friday    | Follow up on pending connections (3+ days old, no message yet)  |
| Friday    | Follow up on applications > 2 weeks old with no response         |
| Sunday    | Review tracker.csv — update statuses, prune dead applications    |

---

## LinkedIn Profile Optimization

Keep your profile in sync with your best resume version:
- **Headline**: "M.S. AI @ OSU | ML Engineer | PyTorch · CUDA · LLMs"
- **About**: 3–4 sentences: who you are → what you build → what you're looking for
- **Open to Work**: turn on (visible to recruiters, not your network, to avoid awkwardness)
- **Featured**: pin your best project (GitHub or a live demo)
- **Skills**: match exactly the keywords in `search_terms.must_include_one_of`
- **Recommendations**: request 1–2 from advisors/supervisors; offer to write one for them first
