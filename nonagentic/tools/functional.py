from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from nonagentic.tools.customer import search_customer_profile

_CASES: dict[str, dict] = {}  # in-memory support stub
_SENT: list[dict] = []  # in-memory sent log

# Promotion metadata for NBA scoring
_PROMO_RULES = {
    "PROMO-PREMIUM-MEMBERSHIP": {
        "name": "Premium Membership",
        "target_segments": {"vip", "dormant_vip", "at_risk"},
        "cross_sell_trigger": "electronics",  # bought this → good fit
        "excludes": None,
    },
    "PROMO-LOYALTY-POINTS": {
        "name": "Loyalty Points Boost",
        "target_segments": {"vip", "new", "at_risk"},
        "cross_sell_trigger": None,
        "excludes": None,
    },
    "PROMO-BUNDLE-DEAL": {
        "name": "Bundle Deal",
        "target_segments": {"vip", "dormant_vip", "new"},
        "cross_sell_trigger": "home",
        "excludes": None,
    },
    "PROMO-WINBACK": {
        "name": "Win-Back Offer",
        "target_segments": {"at_risk", "casual", "dormant_vip"},
        "cross_sell_trigger": "clothing",
        "excludes": None,
    },
}


def _score_promo(c: dict, promo_code: str) -> float:
    """NBA score for a specific promotion + customer combination (0–1)."""
    rules = _PROMO_RULES.get(promo_code, {})
    score = 0.0
    categories = c.get("purchase_categories", [])
    seg = c.get("segment", "")

    if seg in rules.get("target_segments", set()):
        score += 0.35
    trigger = rules.get("cross_sell_trigger")
    if trigger and trigger in categories:
        score += 0.25
    excl = rules.get("excludes")
    if excl and excl in categories:
        return 0.0
    score += c.get("engagement_score", 0.5) * 0.25
    score += (1 - c.get("return_risk", 0.5)) * 0.15
    return round(min(score, 1.0), 4)


def recommend_offer(customer_id: str, context: str = "") -> dict:
    result = search_customer_profile(customer_id=customer_id)
    c = result.get("customer")
    if not c:
        return {"offer_code": None, "error": "customer_not_found"}

    eligible: list[str] = c.get("promotion_eligibility", [])
    if not eligible:
        return {
            "offer_code": None,
            "offer_name": None,
            "rationale": "No eligible promotions",
            "confidence": 0.0,
        }

    scored = [(code, _score_promo(c, code)) for code in eligible]
    scored.sort(key=lambda x: x[1], reverse=True)
    best_code, best_score = scored[0]

    rules = _PROMO_RULES.get(best_code, {})
    categories = c.get("purchase_categories", [])
    rationale_parts = [
        f"segment '{c.get('segment')}'",
        f"engagement {c.get('engagement_score', 0):.0%}",
    ]
    trigger = rules.get("cross_sell_trigger")
    if trigger and trigger in categories:
        rationale_parts.append(f"cross-sell from {trigger}")

    return {
        "offer_code": best_code,
        "offer_name": rules.get("name", best_code),
        "rationale": "; ".join(rationale_parts),
        "confidence": best_score,
        "all_offers_scored": [{"offer_code": c, "score": s} for c, s in scored],
    }


def draft_email(
    customer_id: str,
    template_id: str,
    variables: Optional[dict] = None,
    language: Optional[str] = None,
) -> dict:
    result = search_customer_profile(customer_id=customer_id)
    c = result.get("customer")
    if not c:
        return {"error": "customer_not_found"}

    lang = language or c.get("preferred_language", "en")
    vars_ = variables or {}
    name = c.get("full_name", "Valued Customer")

    templates = {
        "T-PROMO-01": {
            "subject": "Exclusive promotion just for you",
            "body": f"Dear {name},\n\nWe have a special promotion: {vars_.get('offer_name', 'a great deal')}.\n\nBest regards,\nMarketing Team",
        },
        "T-WINBACK-01": {
            "subject": "We miss you — come back for a special offer",
            "body": f"Dear {name},\n\nWe haven't seen you in a while. Here's an exclusive win-back offer just for you.\n\nBest regards,\nCustomer Success Team",
        },
    }
    tpl = templates.get(template_id)
    if not tpl:
        return {"error": f"template_not_found: {template_id}"}

    return {"subject": tpl["subject"], "body": tpl["body"], "language": lang}


def send_notification(
    customer_id: str,
    channel: str,
    content: dict,
    dry_run: bool = False,
) -> dict:
    result = search_customer_profile(customer_id=customer_id)
    c = result.get("customer")
    if not c:
        return {"message_id": None, "status": "blocked", "reason": "customer_not_found"}

    flags: dict = c.get("consent_flags", {})
    if channel == "email" and not flags.get("email", True):
        return {"message_id": None, "status": "blocked", "reason": "consent_email"}
    if channel == "sms" and not flags.get("sms", True):
        return {"message_id": None, "status": "blocked", "reason": "consent_sms"}
    if not flags.get("marketing", True):
        return {"message_id": None, "status": "blocked", "reason": "consent_marketing"}

    message_id = str(uuid.uuid4())
    if not dry_run:
        _SENT.append(
            {
                "message_id": message_id,
                "customer_id": customer_id,
                "channel": channel,
                "content": content,
                "sent_at": datetime.now(timezone.utc).isoformat(),
            }
        )
    return {"message_id": message_id, "status": "queued" if dry_run else "sent"}


def create_case(
    customer_id: str,
    case_type: str,
    description: str,
    priority: str = "medium",
) -> dict:
    for case_id, case in _CASES.items():
        if (
            case["customer_id"] == customer_id
            and case["case_type"] == case_type
            and case["status"] == "open"
        ):
            return {
                "case_id": case_id,
                "status": "open",
                "assigned_to": case["assigned_to"],
                "duplicate": True,
            }

    case_id = f"CASE-{uuid.uuid4().hex[:8].upper()}"
    _CASES[case_id] = {
        "customer_id": customer_id,
        "case_type": case_type,
        "description": description,
        "priority": priority,
        "status": "open",
        "assigned_to": "support-team",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return {"case_id": case_id, "status": "open", "assigned_to": "support-team"}
