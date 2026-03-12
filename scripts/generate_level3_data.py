"""Generate Level 3 demo data:
- data/lead_scores.json       — scored prospect list per offer
- data/campaign_results.json  — simulated past campaign execution results
- Patches customers.json to ensure every customer has >=1 offer_eligibility entry
"""
from __future__ import annotations

import json
import random
import uuid
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data"

OFFERS = ["OFFER-GOLD-UPGRADE", "OFFER-SAVINGS-BOOST", "OFFER-INSURANCE-BUNDLE", "OFFER-LOAN-REFI"]

OFFER_PRODUCT_MAP = {
    "OFFER-GOLD-UPGRADE":       {"target_segments": ["high-value", "high-value-low-engagement", "at-risk"],
                                  "excludes_product": "visa_gold",
                                  "requires_product": None},
    "OFFER-SAVINGS-BOOST":      {"target_segments": ["high-value", "new", "at-risk"],
                                  "excludes_product": None,
                                  "requires_product": None},
    "OFFER-INSURANCE-BUNDLE":   {"target_segments": ["high-value", "high-value-low-engagement", "new"],
                                  "excludes_product": None,
                                  "requires_product": None},
    "OFFER-LOAN-REFI":          {"target_segments": ["at-risk", "low-engagement", "high-value-low-engagement"],
                                  "excludes_product": None,
                                  "requires_product": "personal_loan"},
}

COMPANY_TYPES = ["sole_trader", "sme", "corporate", "non_profit", "public_sector"]
DATA_SOURCES = ["credit_bureau", "business_registry", "location_api"]


# ── helpers ──────────────────────────────────────────────────────────────────

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


def _lead_score(c: dict, offer_code: str) -> float:
    return round(
        c.get("engagement_score", 0.5) * 0.4
        + (1 - c.get("risk_score", 0.5)) * 0.3
        + _balance_factor(c.get("account_balance", 0)) * 0.2
        + _recency_factor(c.get("last_interaction_date")) * 0.1,
        4,
    )


def _eligible_for_offer(c: dict, offer_code: str) -> bool:
    cfg = OFFER_PRODUCT_MAP[offer_code]
    if c.get("kyc_status") == "expired":
        return False
    if not c.get("consent_flags", {}).get("marketing", True):
        return False
    holdings = c.get("product_holdings", [])
    if cfg["excludes_product"] and cfg["excludes_product"] in holdings:
        return False
    if cfg["requires_product"] and cfg["requires_product"] not in holdings:
        return False
    return True


def _credit_score(c: dict) -> int:
    base = 600
    base += int((1 - c.get("risk_score", 0.5)) * 150)
    base += int(c.get("engagement_score", 0.5) * 80)
    base += int(min(c.get("account_balance", 0) / 1000, 20))
    return min(850, max(300, base + random.randint(-20, 20)))


def _location_score(c: dict) -> float:
    country_base = {"HU": 0.75, "GB": 0.85, "AE": 0.80}
    return round(country_base.get(c.get("country", "GB"), 0.7) + random.uniform(-0.1, 0.1), 2)


# ── Step 1a: patch customers.json — ensure every customer has >=1 offer ──────

def patch_customers(customers: list[dict]) -> list[dict]:
    for c in customers:
        if not c.get("offer_eligibility"):
            # assign based on segment
            seg = c.get("segment", "new")
            if seg in ("high-value", "high-value-low-engagement"):
                c["offer_eligibility"] = ["OFFER-GOLD-UPGRADE"]
            elif seg == "at-risk":
                c["offer_eligibility"] = ["OFFER-SAVINGS-BOOST"]
            elif seg == "low-engagement":
                c["offer_eligibility"] = ["OFFER-LOAN-REFI"]
            else:
                c["offer_eligibility"] = ["OFFER-INSURANCE-BUNDLE"]
    return customers


# ── Step 1b: generate lead_scores.json ───────────────────────────────────────

def generate_lead_scores(customers: list[dict]) -> list[dict]:
    records = []
    for c in customers:
        enrichment = {
            "credit_bureau_score": _credit_score(c),
            "company_type": random.choice(COMPANY_TYPES),
            "employees": random.choice([1, 5, 12, 50, 200, 500]),
            "location_score": _location_score(c),
            "branch_distance_km": round(random.uniform(0.5, 25.0), 1),
            "data_sources": DATA_SOURCES,
            "enriched_at": "2026-03-01",
        }
        offer_scores = {}
        for offer in OFFERS:
            if _eligible_for_offer(c, offer):
                offer_scores[offer] = _lead_score(c, offer)

        records.append({
            "customer_id": c["customer_id"],
            "full_name": c["full_name"],
            "segment": c["segment"],
            "country": c["country"],
            "kyc_status": c["kyc_status"],
            "marketing_consent": c.get("consent_flags", {}).get("marketing", False),
            "offer_scores": offer_scores,
            "top_offer": max(offer_scores, key=offer_scores.get) if offer_scores else None,
            "top_score": max(offer_scores.values()) if offer_scores else 0.0,
            "enrichment": enrichment,
        })
    return sorted(records, key=lambda x: x["top_score"], reverse=True)


# ── Step 1c: generate campaign_results.json ───────────────────────────────────

CHANNELS = ["email", "sms", "push"]
OUTCOMES = ["clicked", "opened", "ignored", "unsubscribed", "converted"]
OUTCOME_WEIGHTS = [0.15, 0.25, 0.35, 0.10, 0.15]


def generate_campaign_results(customers: list[dict]) -> list[dict]:
    results = []
    campaigns = [
        {"campaign_id": "CAMP-L3-001", "offer": "OFFER-GOLD-UPGRADE",    "segment": "high-value-low-engagement", "date": "2026-01-15"},
        {"campaign_id": "CAMP-L3-002", "offer": "OFFER-SAVINGS-BOOST",   "segment": "at-risk",                   "date": "2026-01-22"},
        {"campaign_id": "CAMP-L3-003", "offer": "OFFER-INSURANCE-BUNDLE","segment": "new",                       "date": "2026-02-01"},
        {"campaign_id": "CAMP-L3-004", "offer": "OFFER-LOAN-REFI",       "segment": "low-engagement",            "date": "2026-02-10"},
    ]
    for camp in campaigns:
        targets = [c for c in customers
                   if c.get("segment") == camp["segment"]
                   and c.get("consent_flags", {}).get("marketing", False)
                   and c.get("kyc_status") != "expired"]
        sent = 0
        blocked = 0
        for c in targets:
            channel = random.choice(CHANNELS)
            # respect channel consent
            flags = c.get("consent_flags", {})
            if channel == "email" and not flags.get("email", True):
                blocked += 1
                continue
            if channel == "sms" and not flags.get("sms", True):
                blocked += 1
                continue
            outcome = random.choices(OUTCOMES, weights=OUTCOME_WEIGHTS)[0]
            results.append({
                "campaign_id": camp["campaign_id"],
                "offer_code": camp["offer"],
                "segment": camp["segment"],
                "customer_id": c["customer_id"],
                "channel": channel,
                "sent_date": camp["date"],
                "outcome": outcome,
                "converted": outcome == "converted",
            })
            sent += 1

        print(f"  {camp['campaign_id']}: {sent} sent, {blocked} blocked")

    return results


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    customers_path = DATA / "customers.json"
    customers = json.loads(customers_path.read_text())

    print("Patching offer_eligibility for customers with empty list...")
    customers = patch_customers(customers)
    customers_path.write_text(json.dumps(customers, ensure_ascii=False, indent=2))
    print(f"  Saved {len(customers)} customers")

    print("Generating lead_scores.json...")
    lead_scores = generate_lead_scores(customers)
    (DATA / "lead_scores.json").write_text(json.dumps(lead_scores, ensure_ascii=False, indent=2))
    print(f"  {len(lead_scores)} records written")

    print("Generating campaign_results.json...")
    campaign_results = generate_campaign_results(customers)
    (DATA / "campaign_results.json").write_text(json.dumps(campaign_results, ensure_ascii=False, indent=2))
    print(f"  {len(campaign_results)} campaign result records written")

    # summary stats
    eligible_counts = {o: sum(1 for r in lead_scores if o in r["offer_scores"]) for o in OFFERS}
    print("\nEligible prospects per offer:")
    for o, n in eligible_counts.items():
        print(f"  {o}: {n}")

    converted = sum(1 for r in campaign_results if r["converted"])
    print(f"\nCampaign results: {len(campaign_results)} sent, {converted} converted "
          f"({converted/len(campaign_results)*100:.1f}%)")


if __name__ == "__main__":
    main()
