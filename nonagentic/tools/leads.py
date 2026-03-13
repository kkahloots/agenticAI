"""Lead scoring, enrichment, and bulk recommendation tools for Level 3."""

from __future__ import annotations

import json
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Optional

_ROOT = Path(__file__).parent.parent.parent
_LEAD_SCORES_PATH = _ROOT / "data" / "lead_scores.json"
_CUSTOMERS_PATH = _ROOT / "data" / "customers.json"

_OFFER_LABELS = {
    "PROMO-PREMIUM-MEMBERSHIP": "Premium Membership",
    "PROMO-LOYALTY-POINTS": "Loyalty Points Boost",
    "PROMO-BUNDLE-DEAL": "Bundle Deal",
    "PROMO-WINBACK": "Win-Back Offer",
}


@lru_cache(maxsize=1)
def _load_lead_scores() -> list[dict]:
    if not _LEAD_SCORES_PATH.exists():
        return []
    return json.loads(_LEAD_SCORES_PATH.read_text())


@lru_cache(maxsize=1)
def _load_customers() -> list[dict]:
    if not _CUSTOMERS_PATH.exists():
        return []
    return json.loads(_CUSTOMERS_PATH.read_text())


def _recency_factor(last_interaction: str | None) -> float:
    if not last_interaction:
        return 0.3
    days = (date.today() - date.fromisoformat(last_interaction)).days
    if days <= 30:
        return 1.0
    if days <= 90:
        return 0.7
    if days <= 180:
        return 0.5
    return 0.2


def _balance_factor(balance: float) -> float:
    if balance >= 50_000:
        return 1.0
    if balance >= 20_000:
        return 0.7
    if balance >= 5_000:
        return 0.4
    return 0.1


def _compute_lead_score(c: dict) -> float:
    return round(
        c.get("engagement_score", 0.5) * 0.4
        + (1 - c.get("fraud_score", 0.5)) * 0.3
        + _balance_factor(c.get("lifetime_value", 0)) * 0.2
        + _recency_factor(c.get("last_interaction_date")) * 0.1,
        4,
    )


def _offer_rationale(c: dict, offer_code: str) -> str:
    parts = []
    seg = c.get("segment", "")
    categories = c.get("purchase_categories", [])
    eng = c.get("engagement_score", 0)
    ltv = c.get("lifetime_value", 0)

    if offer_code == "PROMO-PREMIUM-MEMBERSHIP" and "electronics" in categories:
        parts.append("electronics buyer — premium membership fits")
    if offer_code == "PROMO-LOYALTY-POINTS" and ltv > 30_000:
        parts.append(f"high lifetime value (€{ltv:,.0f}) — loyalty boost fits")
    if offer_code == "PROMO-BUNDLE-DEAL" and "home" in categories:
        parts.append("home category buyer — bundle deal opportunity")
    if offer_code == "PROMO-WINBACK" and "clothing" in categories:
        parts.append("clothing buyer — win-back offer relevant")
    if eng > 0.7:
        parts.append(f"high engagement ({eng:.0%})")
    if seg in ("vip", "dormant_vip"):
        parts.append(f"premium segment ({seg})")
    return (
        "; ".join(parts)
        if parts
        else f"eligible for {_OFFER_LABELS.get(offer_code, offer_code)}"
    )


def score_leads(
    offer_code: str, top_n: int = 20, segment: Optional[str] = None
) -> dict:
    """
    Score and rank customers as prospects for a given promotion.

    Returns top_n customers ranked by lead score, filtered by:
    - verified/pending identity
    - marketing consent = true
    - optional segment filter
    """
    customers = _load_customers()
    results = []

    for c in customers:
        if c.get("identity_status") == "unverified":
            continue
        if not c.get("consent_flags", {}).get("marketing", False):
            continue
        if segment and c.get("segment") != segment:
            continue

        score = _compute_lead_score(c)
        results.append(
            {
                "customer_id": c["customer_id"],
                "full_name": c["full_name"],
                "segment": c["segment"],
                "country": c["country"],
                "lead_score": score,
                "engagement_score": c.get("engagement_score"),
                "fraud_score": c.get("fraud_score"),
                "lifetime_value": c.get("lifetime_value"),
                "purchase_categories": c.get("purchase_categories", []),
                "rationale": _offer_rationale(c, offer_code),
            }
        )

    results.sort(key=lambda x: x["lead_score"], reverse=True)
    top = results[:top_n]

    return {
        "offer_code": offer_code,
        "offer_name": _OFFER_LABELS.get(offer_code, offer_code),
        "segment_filter": segment,
        "total_eligible": len(results),
        "returned": len(top),
        "prospects": top,
    }


def enrich_customer(customer_id: str) -> dict:
    """
    Return enrichment data for a customer from the lead_scores dataset.
    Simulates multi-source enrichment (credit bureau, business registry, location API).
    """
    records = _load_lead_scores()
    record = next((r for r in records if r["customer_id"] == customer_id), None)
    if not record:
        return {"error": "customer_not_found", "customer_id": customer_id}

    return {
        "customer_id": customer_id,
        "full_name": record.get("full_name"),
        "segment": record.get("segment"),
        "enrichment": record.get("enrichment", {}),
        "offer_scores": record.get("offer_scores", {}),
        "top_offer": record.get("top_offer"),
        "top_score": record.get("top_score"),
    }


# ---------------------------------------------------------------------------
# Upsell & Recommendation helpers
# ---------------------------------------------------------------------------

_UPSELL_MAP: dict[str, list[str]] = {
    # category → higher-tier / complementary categories to upsell into
    "electronics": ["premium_electronics", "accessories"],
    "clothing": ["premium_fashion", "accessories"],
    "home": ["premium_home", "garden"],
    "sports": ["premium_sports", "outdoor"],
    "beauty": ["premium_beauty", "wellness"],
    "books": ["premium_books", "courses"],
    "food": ["premium_food", "gourmet"],
    "travel": ["premium_travel", "experiences"],
    "automotive": ["premium_automotive", "accessories"],
    "toys": ["premium_toys", "educational"],
}

_UPSELL_PROMO_MAP: dict[str, str] = {
    # segment → best upsell promo
    "vip": "PROMO-PREMIUM-MEMBERSHIP",
    "dormant_vip": "PROMO-WINBACK",
    "at_risk": "PROMO-LOYALTY-POINTS",
    "casual": "PROMO-BUNDLE-DEAL",
    "new": "PROMO-LOYALTY-POINTS",
}


def upsell_recommend(customer_id: str) -> dict:
    """
    Recommend upsell opportunities for a customer based on their current
    purchase categories and segment. Returns target categories and best promo.
    """
    customers = _load_customers()
    c = next((x for x in customers if x["customer_id"] == customer_id), None)
    if not c:
        return {"error": "customer_not_found", "customer_id": customer_id}

    categories = c.get("purchase_categories", [])
    upsell_targets: list[str] = []
    for cat in categories:
        upsell_targets.extend(_UPSELL_MAP.get(cat, []))
    # deduplicate, preserve order
    seen: set[str] = set()
    unique_targets = [t for t in upsell_targets if not (t in seen or seen.add(t))]  # type: ignore[func-returns-value]

    seg = c.get("segment", "")
    best_promo = _UPSELL_PROMO_MAP.get(seg, "PROMO-BUNDLE-DEAL")
    promo_name = _OFFER_LABELS.get(best_promo, best_promo)

    ltv = c.get("lifetime_value", 0)
    eng = c.get("engagement_score", 0)
    upsell_score = round(
        eng * 0.5 + _balance_factor(ltv) * 0.3 + (1 - c.get("fraud_score", 0.5)) * 0.2,
        4,
    )

    return {
        "customer_id": customer_id,
        "full_name": c["full_name"],
        "segment": seg,
        "current_categories": categories,
        "upsell_targets": unique_targets[:4],
        "recommended_promo": best_promo,
        "promo_name": promo_name,
        "upsell_score": upsell_score,
        "rationale": (
            f"Segment '{seg}', engagement {eng:.0%}, "
            f"lifetime value €{ltv:,.0f}. "
            f"Upsell from {', '.join(categories[:2])} into {', '.join(unique_targets[:2]) or 'premium tiers'}."
        ),
    }


def user_based_recommend(customer_id: str, top_n: int = 5) -> dict:
    """
    Recommend products/categories for a customer based on their own profile:
    purchase history, segment peers, and engagement level.
    Returns ranked category recommendations with confidence scores.
    """
    customers = _load_customers()
    c = next((x for x in customers if x["customer_id"] == customer_id), None)
    if not c:
        return {"error": "customer_not_found", "customer_id": customer_id}

    owned = set(c.get("purchase_categories", []))
    seg = c.get("segment", "")
    eng = c.get("engagement_score", 0.5)
    ltv = c.get("lifetime_value", 0)

    # Score candidate categories from segment peers
    category_scores: dict[str, float] = {}
    peer_count = 0
    for peer in customers:
        if peer["customer_id"] == customer_id:
            continue
        if peer.get("segment") != seg:
            continue
        peer_count += 1
        peer_cats = set(peer.get("purchase_categories", []))
        new_cats = peer_cats - owned
        for cat in new_cats:
            # weight by peer engagement similarity
            peer_eng = peer.get("engagement_score", 0.5)
            similarity = 1 - abs(eng - peer_eng)
            category_scores[cat] = category_scores.get(cat, 0.0) + similarity

    if not category_scores:
        return {
            "customer_id": customer_id,
            "recommendations": [],
            "rationale": "No peer data available for recommendations",
        }

    # Normalise scores
    max_score = max(category_scores.values())
    ranked = sorted(
        [
            {"category": cat, "confidence": round(score / max_score, 3)}
            for cat, score in category_scores.items()
        ],
        key=lambda x: x["confidence"],
        reverse=True,
    )[:top_n]

    return {
        "customer_id": customer_id,
        "full_name": c["full_name"],
        "segment": seg,
        "current_categories": list(owned),
        "peer_count": peer_count,
        "recommendations": ranked,
        "rationale": (
            f"Based on {peer_count} peers in '{seg}' segment. "
            f"Customer engagement {eng:.0%}, lifetime value €{ltv:,.0f}."
        ),
    }


def collaborative_recommend(customer_id: str, top_n: int = 5) -> dict:
    """
    Cross-customer collaborative filtering recommendation.
    Finds the most similar customers (by purchase category overlap + engagement)
    and recommends categories they buy that this customer doesn't.
    """
    customers = _load_customers()
    c = next((x for x in customers if x["customer_id"] == customer_id), None)
    if not c:
        return {"error": "customer_not_found", "customer_id": customer_id}

    owned = set(c.get("purchase_categories", []))
    eng = c.get("engagement_score", 0.5)
    ltv = c.get("lifetime_value", 0)

    # Compute Jaccard similarity + engagement proximity for each other customer
    similarities: list[tuple[float, dict]] = []
    for other in customers:
        if other["customer_id"] == customer_id:
            continue
        other_cats = set(other.get("purchase_categories", []))
        if not other_cats:
            continue
        intersection = len(owned & other_cats)
        union = len(owned | other_cats)
        jaccard = intersection / union if union else 0.0
        eng_sim = 1 - abs(eng - other.get("engagement_score", 0.5))
        combined = round(jaccard * 0.7 + eng_sim * 0.3, 4)
        if combined > 0:
            similarities.append((combined, other))

    similarities.sort(key=lambda x: x[0], reverse=True)
    top_similar = similarities[:10]  # top-10 neighbours

    # Aggregate candidate categories from neighbours
    category_votes: dict[str, float] = {}
    for sim_score, neighbour in top_similar:
        for cat in neighbour.get("purchase_categories", []):
            if cat not in owned:
                category_votes[cat] = category_votes.get(cat, 0.0) + sim_score

    if not category_votes:
        return {
            "customer_id": customer_id,
            "recommendations": [],
            "similar_customers": [],
            "rationale": "No new categories found from similar customers",
        }

    max_votes = max(category_votes.values())
    ranked = sorted(
        [
            {"category": cat, "confidence": round(votes / max_votes, 3)}
            for cat, votes in category_votes.items()
        ],
        key=lambda x: x["confidence"],
        reverse=True,
    )[:top_n]

    similar_ids = [n["customer_id"] for _, n in top_similar[:3]]

    return {
        "customer_id": customer_id,
        "full_name": c["full_name"],
        "segment": c.get("segment", ""),
        "current_categories": list(owned),
        "top_similar_customers": similar_ids,
        "recommendations": ranked,
        "rationale": (
            f"Collaborative filtering across {len(similarities)} customers. "
            f"Top neighbours: {', '.join(similar_ids)}. "
            f"Recommendations based on Jaccard similarity (70%) + engagement proximity (30%)."
        ),
    }


def bulk_recommend(
    offer_code: str,
    segment: Optional[str] = None,
    top_n: int = 50,
) -> dict:
    """
    Generate a bulk recommendation execution plan for an offer.

    Returns:
    - prospects to target (scored + ranked)
    - execution summary: how many to send, blocked by consent, need approval
    """
    from nonagentic.core.config import load_config

    cfg = load_config()

    scored = score_leads(offer_code, top_n=top_n, segment=segment)
    prospects = scored["prospects"]

    plan = []
    sent_count = 0
    blocked_count = 0
    approval_needed = 0

    customers = {c["customer_id"]: c for c in _load_customers()}

    for p in prospects:
        c = customers.get(p["customer_id"], {})
        flags = c.get("consent_flags", {})

        # determine best channel
        if flags.get("email", False):
            channel = "email"
        elif flags.get("sms", False):
            channel = "sms"
        else:
            blocked_count += 1
            plan.append(
                {
                    **p,
                    "action": "blocked",
                    "reason": "no_channel_consent",
                    "channel": None,
                }
            )
            continue

        if c.get("fraud_score", 0) > cfg.risk_score_threshold:
            approval_needed += 1
            plan.append(
                {
                    **p,
                    "action": "approval_required",
                    "channel": channel,
                    "reason": f"fraud_score {c['fraud_score']:.2f} > threshold",
                }
            )
            continue

        sent_count += 1
        plan.append({**p, "action": "send", "channel": channel, "reason": None})

    needs_bulk_approval = (
        sent_count + approval_needed
    ) > cfg.bulk_notification_threshold

    return {
        "offer_code": offer_code,
        "offer_name": _OFFER_LABELS.get(offer_code, offer_code),
        "segment_filter": segment,
        "total_prospects": len(prospects),
        "to_send": sent_count,
        "blocked": blocked_count,
        "approval_required": approval_needed,
        "bulk_approval_needed": needs_bulk_approval,
        "bulk_threshold": cfg.bulk_notification_threshold,
        "execution_plan": plan,
    }
