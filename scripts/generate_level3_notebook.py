"""Generate notebooks/level3_functional_agent.ipynb"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
NB_PATH = ROOT / "notebooks" / "level3_functional_agent.ipynb"


def cell(source: str, cell_type: str = "code") -> dict:
    if cell_type == "markdown":
        return {"cell_type": "markdown", "metadata": {}, "source": [source]}
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [source],
    }


SETUP = """\
import sys, os
sys.path.insert(0, os.path.abspath('..'))
from notebooks.utils import (
    display_card, display_metrics, display_bar_chart,
    display_side_by_side, display_violations_list, display_status_banner,
    display_lead_scoring_results, display_customer_enrichment,
    display_nba_recommendations, display_consent_notification, display_blocked_example,
    display_kyc_gate, display_title
)
from IPython.display import display, HTML
import json, pandas as pd
from pathlib import Path

from nonagentic.tools.leads import score_leads, enrich_customer, bulk_recommend
from nonagentic.tools.functional import recommend_offer, draft_email, send_notification, create_case
from nonagentic.tools.customer import search_customer_profile, get_kyc_status

print("✅ Level 3 Functional Agent — ready")
"""

UC1 = """\
# UC1: Lead Scoring — identify top prospects for Premium Membership
offer_code = "PROMO-PREMIUM-MEMBERSHIP"
result = score_leads(offer_code, top_n=10)

display(HTML(f'<div style="font-size:18px;font-weight:600;margin:16px 0">🎯 Lead Scoring: {result["offer_name"]}</div>'))
display_metrics({
    "Total Eligible": result["total_eligible"],
    "Returned": result["returned"],
    "Offer": result["offer_name"],
})

rows = [{
    "Customer ID": p["customer_id"],
    "Name": p["full_name"][:20],
    "Segment": p["segment"],
    "Lead Score": f'{p["lead_score"]:.3f}',
    "Engagement": f'{p["engagement_score"]:.0%}',
    "Fraud Score": f'{p["fraud_score"]:.2f}',
    "Lifetime Value": f'${p["lifetime_value"]:,.0f}',
    "Rationale": p["rationale"][:50],
} for p in result["prospects"]]

df = pd.DataFrame(rows)
display(df.style.set_properties(**{"font-size": "12px"}).hide(axis="index"))

display_card("Lead Scoring Insight",
    f"Identified <strong>{result['total_eligible']}</strong> eligible prospects for {result['offer_name']}. "
    f"Top prospect: <strong>{result['prospects'][0]['customer_id']}</strong> "
    f"(score {result['prospects'][0]['lead_score']:.3f}) — {result['prospects'][0]['rationale']}.",
    emoji="🎯", color="#3b82f6")
"""

UC2 = """\
# UC2: Customer Enrichment — multi-source data enrichment
customer_id = "CUST-021"
enriched = enrich_customer(customer_id)

display_customer_enrichment(enriched, customer_id)
"""

UC3 = """\
# UC3: Next-Best-Action (NBA) Recommendation — ranked offer scoring
test_customers = ["CUST-021", "CUST-017", "CUST-041", "CUST-079", "CUST-143"]

display_nba_recommendations(test_customers, recommend_offer, search_customer_profile)
"""

UC4 = """\
# UC4: Consent-Gated Notification — send offer to eligible customer
customer_id = "CUST-021"  # vip, marketing consent=true

offer = recommend_offer(customer_id)
draft = draft_email(customer_id, "T-PROMO-01", variables={"offer_name": offer["offer_name"]})
send_result = send_notification(customer_id, "email", {"subject": draft["subject"], "body": draft["body"]})

display_consent_notification(customer_id, send_result, draft)

# Blocked example — CUST-072 has marketing consent=false
blocked_id = "CUST-072"
blocked_result = send_notification(blocked_id, "email", {"subject": "Test", "body": "Test"})
display_blocked_example(blocked_id, blocked_result)
"""

UC5 = """\
# UC5: Identity Gate — block action on unverified identity, open remediation case
customer_id = "CUST-013"  # identity_status=unverified

kyc = get_kyc_status(customer_id)

case = None
if kyc.get("kyc_status") in ("unverified", "expired"):
    case = create_case(customer_id, "identity_reverification",
                       "Identity unverified — re-verification required before action", priority="high")

display_kyc_gate(customer_id, kyc, case)
"""

UC6 = """\
# UC6: Bulk Campaign Targeting — segment-level offer execution plan
offer_code = "PROMO-WINBACK"
segment = "dormant_vip"

display(HTML(f'<div style="font-size:18px;font-weight:600;margin:16px 0">📢 Bulk Campaign: {offer_code} → {segment}</div>'))

plan = bulk_recommend(offer_code, segment=segment, top_n=50)

display_metrics({
    "Total Prospects": plan["total_prospects"],
    "To Send": plan["to_send"],
    "Blocked": plan["blocked"],
    "Approval Required": plan["approval_required"],
    "Bulk Approval Needed": "YES ⚠️" if plan["bulk_approval_needed"] else "NO ✅",
})

# Channel breakdown
channel_counts = {}
for item in plan["execution_plan"]:
    ch = item.get("channel") or "blocked"
    channel_counts[ch] = channel_counts.get(ch, 0) + 1

if channel_counts:
    display_bar_chart(channel_counts, "Execution Plan by Channel", color="#8b5cf6")

# Action breakdown
action_counts = {}
for item in plan["execution_plan"]:
    action_counts[item["action"]] = action_counts.get(item["action"], 0) + 1
if action_counts:
    display_bar_chart(action_counts, "Actions", color="#10b981")

display_card("Campaign Execution Plan",
    f"Targeting <strong>{segment}</strong> segment with <strong>{plan['offer_name']}</strong>. "
    f"{plan['to_send']} customers will receive the offer via email/SMS. "
    f"{plan['blocked']} blocked due to missing channel consent. "
    f"{'⚠️ Bulk approval required before sending.' if plan['bulk_approval_needed'] else '✅ Within auto-send threshold.'}",
    emoji="📢", color="#667eea")
"""

UC7 = """\
# UC7: Return Risk Intervention — identify high-return-risk customers and send win-back offers
customers = json.loads(Path("../data/customers.json").read_text())

# Find customers with high return risk, verified/pending identity, and marketing consent
at_risk = [
    c for c in customers
    if c.get("return_risk", 0) > 0.7
    and c.get("identity_status") in ("verified", "pending")
    and c.get("consent_flags", {}).get("marketing", False)
]
at_risk.sort(key=lambda x: x["return_risk"], reverse=True)

display(HTML('<div style="font-size:18px;font-weight:600;margin:16px 0">⚠️ Return Risk Intervention</div>'))
display_metrics({
    "High Return-Risk Customers": len(at_risk),
    "Threshold": "> 0.70",
    "Identity Filter": "Verified/Pending only",
    "Note": "Unverified identity → case opened instead",
})

rows = []
for c in at_risk[:8]:
    flags = c.get("consent_flags", {})
    channel = "email" if flags.get("email") else "sms" if flags.get("sms") else None
    if channel:
        send = send_notification(c["customer_id"], channel, {"body": "We miss you! Here is a special win-back offer."})
    else:
        send = {"status": "blocked", "reason": "no_channel_consent"}
    rows.append({
        "Customer ID": c["customer_id"],
        "Segment": c["segment"],
        "Return Risk": f'{c["return_risk"]:.2f}',
        "Lifetime Value": f'${c.get("lifetime_value", 0):,.0f}',
        "Channel": channel or "none",
        "Status": send["status"],
    })

df = pd.DataFrame(rows)
display(df.style.set_properties(**{"font-size": "12px"}).hide(axis="index"))

sent = sum(1 for r in rows if r["Status"] == "sent")
display_card("Return Risk Insight",
    f"Found <strong>{len(at_risk)}</strong> customers with return risk > 70% and verified/pending identity. "
    f"<strong>{sent}</strong> of {len(rows)} shown received win-back offers. "
    f"Customers with unverified identity are blocked — an identity re-verification case is opened instead.",
    emoji="⚠️", color="#f59e0b")
"""

UC8 = """\
# UC8: Campaign Results Dashboard — analyse past campaign performance
campaign_results = json.loads(Path("../data/campaign_results.json").read_text())

display(HTML('<div style="font-size:18px;font-weight:600;margin:16px 0">📊 Campaign Results Dashboard</div>'))

total = len(campaign_results)
converted = sum(1 for r in campaign_results if r["converted"])
conversion_rate = converted / total * 100 if total else 0

display_metrics({
    "Total Sent": total,
    "Converted": converted,
    "Conversion Rate": f"{conversion_rate:.1f}%",
    "Campaigns": len(set(r["campaign_id"] for r in campaign_results)),
})

# Outcome breakdown
outcome_counts = {}
for r in campaign_results:
    outcome_counts[r["outcome"]] = outcome_counts.get(r["outcome"], 0) + 1
display_bar_chart(outcome_counts, "Outcomes Across All Campaigns", color="#3b82f6")

# Per-campaign conversion
camp_stats = {}
for r in campaign_results:
    cid = r["campaign_id"]
    if cid not in camp_stats:
        camp_stats[cid] = {"sent": 0, "converted": 0, "offer": r["offer_code"], "segment": r["segment"]}
    camp_stats[cid]["sent"] += 1
    if r["converted"]:
        camp_stats[cid]["converted"] += 1

rows = []
for cid, s in camp_stats.items():
    rows.append({
        "Campaign": cid,
        "Offer": s["offer"].replace("OFFER-", ""),
        "Segment": s["segment"],
        "Sent": s["sent"],
        "Converted": s["converted"],
        "Conv. Rate": f'{s["converted"]/s["sent"]*100:.1f}%',
    })

df = pd.DataFrame(rows)
display(df.style.set_properties(**{"font-size": "12px"}).hide(axis="index"))

best = max(camp_stats.items(), key=lambda x: x[1]["converted"]/x[1]["sent"])
display_card("Campaign Performance Insight",
    f"Best performing campaign: <strong>{best[0]}</strong> "
    f"({best[1]['offer'].replace('OFFER-','')} → {best[1]['segment']}) "
    f"with {best[1]['converted']}/{best[1]['sent']} conversions "
    f"({best[1]['converted']/best[1]['sent']*100:.1f}%). "
    f"Overall conversion rate: <strong>{conversion_rate:.1f}%</strong> across {total} sends.",
    emoji="📊", color="#10b981")
"""

UC9 = """\
# UC9: Guardrails — PII Redaction & Policy Enforcement

import os
from nonagentic.core.guardrails import guardrail_check

# Enable guardrails
os.environ["GUARDRAIL_ENABLED"] = "true"

# Test case: output with PII and forbidden phrase
test_output = "Customer email is john.doe@example.com and phone is 555-123-4567. We recommend buying shares."

result = guardrail_check(test_output, request_id="demo-001")

display(HTML('<div style="font-size:18px;font-weight:600;margin:16px 0">🛡️ Guardrail Check</div>'))

# Use display_side_by_side helper
display_side_by_side(
    "❌ Original",
    test_output,
    "✅ Sanitized",
    result.revised_text,
    left_color="#fee2e2",
    left_text_color="#dc2626",
    right_color="#dcfce7",
    right_text_color="#16a34a"
)

# Show violations
display_violations_list(result.violations)

display_metrics({
    "Guardrail Passed": "✅ Yes" if result.passed else "❌ No",
    "Violations Found": len(result.violations),
    "Action Taken": "Redacted PII & forbidden phrases",
})

# Disable for remaining demos
os.environ["GUARDRAIL_ENABLED"] = "false"
display_status_banner("✅ Guardrails disabled for remaining demos", status="success")
"""

CELLS = [
    cell(
        "# Level 3 — Functional Agent / Lead Generation & Targeted Marketing\n\n"
        "This notebook demonstrates the Level 3 Functional Agent capabilities:\n\n"
        "- **UC1**: Lead Scoring — identify top prospects for a product offer\n"
        "- **UC2**: Customer Enrichment — multi-source data (credit bureau, business registry, location)\n"
        "- **UC3**: Next-Best-Action (NBA) Recommendation — ranked offer scoring\n"
        "- **UC4**: Consent-Gated Notification — send offer email with consent check\n"
        "- **UC5**: Identity Gate — block action on unverified identity, open remediation case\n"
        "- **UC6**: Bulk Campaign Targeting — segment-level execution plan\n"
        "- **UC7**: Return Risk Intervention — identify and contact high-return-risk customers\n"
        "- **UC8**: Campaign Results Dashboard — analyse past campaign performance\n"
        "- **UC9**: Guardrails — PII redaction and policy enforcement",
        "markdown",
    ),
    cell(SETUP),
    cell("## UC1: Lead Scoring — Identify Top Prospects", "markdown"),
    cell(UC1),
    cell("## UC2: Customer Enrichment — Multi-Source Data", "markdown"),
    cell(UC2),
    cell("## UC3: Next-Best-Action (NBA) Recommendation", "markdown"),
    cell(UC3),
    cell("## UC4: Consent-Gated Notification", "markdown"),
    cell(UC4),
    cell("## UC5: Identity Gate — Block Action on Unverified Identity", "markdown"),
    cell(UC5),
    cell("## UC6: Bulk Campaign Targeting", "markdown"),
    cell(UC6),
    cell("## UC7: Return Risk Intervention", "markdown"),
    cell(UC7),
    cell("## UC8: Campaign Results Dashboard", "markdown"),
    cell(UC8),
    cell("## UC9: Guardrails — PII Redaction & Policy Enforcement", "markdown"),
    cell(UC9),
]

nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "version": "3.10.0"},
    },
    "cells": CELLS,
}

NB_PATH.write_text(json.dumps(nb, indent=1, ensure_ascii=False))
print(f"Written: {NB_PATH}")
print(f"Cells: {len(CELLS)}")
