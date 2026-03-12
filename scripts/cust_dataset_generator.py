#!/usr/bin/env python3
"""
Generate synthetic customer records for an online store.

Usage:
    python scripts/cust_dataset_generator.py --output data/customers.json --count 208
"""

import argparse
import json
import random
from datetime import datetime, timedelta, date

try:
    from faker import Faker
except ImportError:
    raise SystemExit("Install faker: pip install faker")

fake_en = Faker("en_US")
fake_hu = Faker("hu_HU")
fake_ar = Faker("ar_AA")

SEGMENTS = ["vip", "dormant_vip", "casual", "at_risk", "new"]
SEG_WEIGHTS = [0.30, 0.15, 0.20, 0.20, 0.15]

PURCHASE_CATEGORIES = ["electronics", "clothing", "books", "home", "sports", "beauty", "toys", "garden"]
PROMOTIONS = ["PROMO-PREMIUM-MEMBERSHIP", "PROMO-LOYALTY-POINTS", "PROMO-BUNDLE-DEAL", "PROMO-WINBACK"]
COUNTRIES = {"en": "GB", "hu": "HU", "ar": "AE", "zh": "CN", "el": "GR"}

ZH_NAMES = [
    "陈伟强", "王丽华", "张建国", "刘秀英", "李明", "赵雪梅", "孙志远", "周婷婷",
    "吴国华", "郑晓燕", "黄建军", "林美玲", "何志强", "谢丽娟", "徐国庆",
]
EL_NAMES = [
    "Νικόλαος Παπαδόπουλος", "Σοφία Αναγνωστοπούλου", "Δημήτριος Κωνσταντινίδης",
    "Ελένη Παπαγεωργίου", "Γεώργιος Αλεξανδρόπουλος", "Μαρία Χριστοδούλου",
    "Αντώνιος Παπαθανασίου", "Αικατερίνη Βασιλείου", "Ιωάννης Σταματόπουλος",
]


def _fake_name(lang: str) -> str:
    if lang == "hu":
        return fake_hu.name()
    if lang == "ar":
        return fake_ar.name()
    if lang == "zh":
        return random.choice(ZH_NAMES)
    if lang == "el":
        return random.choice(EL_NAMES)
    return fake_en.name()


def _identity_dates(status: str):
    today = date.today()
    if status == "verified":
        expiry = today + timedelta(days=random.randint(30, 730))
        return expiry.isoformat()
    if status == "unverified":
        expiry = today - timedelta(days=random.randint(1, 730))
        return expiry.isoformat()
    return None  # pending


def generate_record(index: int, used_phones: list, lang: str = None) -> dict:
    if lang is None:
        lang = random.choices(["en", "hu", "ar"], weights=[0.34, 0.33, 0.33])[0]
    identity_status = random.choices(["verified", "unverified", "pending"], weights=[0.60, 0.30, 0.10])[0]
    segment = random.choices(SEGMENTS, weights=SEG_WEIGHTS)[0]

    if segment == "dormant_vip":
        engagement = round(random.uniform(0.05, 0.30), 2)
    elif segment == "vip":
        engagement = round(random.uniform(0.60, 1.00), 2)
    else:
        engagement = round(random.uniform(0.20, 0.80), 2)

    if identity_status == "unverified":
        return_risk = round(random.uniform(0.50, 1.00), 2)
    else:
        # Mix of low and some high return risk for verified/pending
        # 80% low risk, 20% high risk
        if random.random() < 0.20:
            return_risk = round(random.uniform(0.70, 0.95), 2)  # High risk
        else:
            return_risk = round(random.uniform(0.00, 0.40), 2)  # Low risk

    email = fake_en.email() if random.random() > 0.10 else None

    if random.random() < 0.05 and used_phones:
        phone = random.choice(used_phones)
    else:
        phone = fake_en.phone_number()
    used_phones.append(phone)

    fraud_score = round(random.uniform(0.0, 1.0), 2) if random.random() > 0.05 else None

    categories = random.sample(PURCHASE_CATEGORIES, k=random.randint(1, 3))
    eligible_promos = random.sample(PROMOTIONS, k=random.randint(0, 2))

    campaign_history = []
    if random.random() > 0.4:
        campaign_history.append({
            "campaign_id": f"C-{random.randint(2023,2025)}-Q{random.randint(1,4)}",
            "sent_date": (date.today() - timedelta(days=random.randint(30, 365))).isoformat(),
            "channel": random.choice(["email", "sms", "push"]),
            "outcome": random.choice(["opened", "clicked", "ignored", "unsubscribed"])
        })

    return {
        "customer_id": f"CUST-{index:03d}",
        "full_name": _fake_name(lang),
        "email": email,
        "phone": phone,
        "preferred_language": lang,
        "segment": segment,
        "identity_status": identity_status,
        "identity_expiry_date": _identity_dates(identity_status),
        "country": COUNTRIES.get(lang, "GB"),
        "fraud_score": fraud_score,
        "engagement_score": engagement,
        "purchase_categories": categories,
        "lifetime_value": round(random.uniform(100, 80000), 2),
        "consent_flags": {
            "marketing": random.random() > 0.15,
            "data_sharing": random.random() > 0.10,
            "sms": random.random() > 0.20,
            "email": random.random() > 0.05
        },
        "last_interaction_date": (date.today() - timedelta(days=random.randint(0, 365))).isoformat(),
        "return_risk": return_risk,
        "promotion_eligibility": eligible_promos,
        "campaign_history": campaign_history
    }


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic customer dataset for online store.")
    parser.add_argument("--output", required=True, help="Output JSON file path")
    parser.add_argument("--count", type=int, default=208, help="Number of records")
    args = parser.parse_args()

    used_phones: list = []
    records = [generate_record(i + 1, used_phones) for i in range(args.count)]

    # Patch null fraud_scores with dataset mean
    valid_scores = [r["fraud_score"] for r in records if r["fraud_score"] is not None]
    mean_score = round(sum(valid_scores) / len(valid_scores), 2) if valid_scores else 0.5
    for r in records:
        if r["fraud_score"] is None:
            r["fraud_score"] = mean_score

    import os
    os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else ".", exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    print(f"Generated {args.count} records → {args.output}")


if __name__ == "__main__":
    main()
