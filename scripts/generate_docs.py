#!/usr/bin/env python3
"""
Generate fake documents (emails, notes, policy docs) consistent with
the existing customers.json dataset for an online store.

Usage:
    python scripts/generate_docs.py
"""
import json
import random
import pathlib
from datetime import date, timedelta
from email.mime.text import MIMEText

random.seed(42)

DATA_DIR   = pathlib.Path("data")
DOCS_DIR   = DATA_DIR / "docs"
EMAILS_DIR = DOCS_DIR / "emails"
NOTES_DIR  = DOCS_DIR / "notes"
POLICY_DIR = DOCS_DIR / "policies"

for d in (EMAILS_DIR, NOTES_DIR, POLICY_DIR):
    d.mkdir(parents=True, exist_ok=True)

customers = json.loads((DATA_DIR / "customers.json").read_text(encoding="utf-8"))


def rand_date(days_back: int = 365) -> str:
    return (date.today() - timedelta(days=random.randint(0, days_back))).isoformat()


# ── Emails ────────────────────────────────────────────────────────────────────

EMAIL_TEMPLATES = [
    (
        "Identity Verification Reminder",
        lambda c: (
            f"Dear {c['full_name']},\n\n"
            f"Your identity verification is due for renewal. Current status: {c['identity_status']}.\n"
            f"Expiry date: {c.get('identity_expiry_date', 'N/A')}.\n"
            f"Please visit your account settings or upload documents via the app.\n\n"
            f"Regards,\nTrust & Safety Team"
        ),
    ),
    (
        "Exclusive Promotion for You",
        lambda c: (
            f"Dear {c['full_name']},\n\n"
            f"As a valued {c['segment']} customer, we have a special promotion for you: "
            f"{', '.join(c['promotion_eligibility']) if c['promotion_eligibility'] else 'personalised discount'}.\n"
            f"Your recent purchases: {', '.join(c['purchase_categories'])}.\n"
            f"Shop now to claim your offer.\n\n"
            f"Best,\nMarketing Team"
        ),
    ),
    (
        "Order Activity Alert",
        lambda c: (
            f"Dear {c['full_name']},\n\n"
            f"We noticed activity on your account (lifetime value: €{c['lifetime_value']:.2f}).\n"
            f"If this was not you, please contact us immediately.\n\n"
            f"Security Team"
        ),
    ),
    (
        "We Miss You",
        lambda c: (
            f"Dear {c['full_name']},\n\n"
            f"We haven't seen you in a while! Your return risk score is {c['return_risk']}.\n"
            f"Come back and enjoy exclusive deals on {', '.join(c['purchase_categories'])}.\n\n"
            f"Customer Success Team"
        ),
    ),
]

for c in random.sample(customers, k=min(40, len(customers))):
    subject, body_fn = random.choice(EMAIL_TEMPLATES)
    msg = MIMEText(body_fn(c))
    msg["Subject"] = subject
    msg["From"]    = "shop@example.com"
    msg["To"]      = c.get("email") or "customer@example.com"
    msg["Date"]    = rand_date()
    fname = EMAILS_DIR / f"{c['customer_id']}-{subject.lower().replace(' ', '_')}.eml"
    fname.write_bytes(msg.as_bytes())

print(f"Generated {len(list(EMAILS_DIR.glob('*.eml')))} emails")


# ── CRM Notes ─────────────────────────────────────────────────────────────────

NOTE_TEMPLATES = [
    lambda c: (
        f"Customer ID: {c['customer_id']}\n"
        f"Support note ({rand_date(90)}): Customer contacted regarding "
        f"{random.choice(['order delivery', 'product return', 'account access', 'promotion query'])}. "
        f"Resolved in {random.randint(3, 20)} minutes. Satisfaction: {random.choice(['high', 'medium', 'low'])}."
    ),
    lambda c: (
        f"Customer ID: {c['customer_id']}\n"
        f"Escalation note ({rand_date(180)}): Customer {c['full_name']} escalated complaint about "
        f"{random.choice(['delayed shipment', 'incorrect charge', 'identity rejection', 'promotion not applied'])}. "
        f"Assigned to senior advisor. Fraud score: {c['fraud_score']}."
    ),
    lambda c: (
        f"Customer ID: {c['customer_id']}\n"
        f"Onboarding note ({rand_date(365)}): New customer in segment '{c['segment']}'. "
        f"First purchases: {', '.join(c['purchase_categories'])}. "
        f"Identity status at registration: {c['identity_status']}. Country: {c['country']}."
    ),
    lambda c: (
        f"Customer ID: {c['customer_id']}\n"
        f"Retention note ({rand_date(60)}): Customer showed churn signals. "
        f"Engagement score: {c['engagement_score']}. "
        f"Offered: {', '.join(c['promotion_eligibility']) if c['promotion_eligibility'] else 'loyalty bonus'}. "
        f"Outcome: {random.choice(['accepted', 'declined', 'pending'])}."
    ),
]

for c in customers:
    note_fn = random.choice(NOTE_TEMPLATES)
    fname = NOTES_DIR / f"{c['customer_id']}-note.txt"
    fname.write_text(note_fn(c), encoding="utf-8")

print(f"Generated {len(list(NOTES_DIR.glob('*.txt')))} notes")
print(f"\nAll documents written to {DOCS_DIR}/")
print("  emails/   — .eml files")
print("  notes/    — .txt files")
print("  policies/ — .md files")
