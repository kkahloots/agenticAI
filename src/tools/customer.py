from __future__ import annotations

import json
import os
import time
from datetime import date
from functools import lru_cache
from typing import Optional

_DATA_PATH = os.getenv(
    "CUSTOMER_DATA_PATH",
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "customers.json"),
)


@lru_cache(maxsize=1)
def _load_customers() -> list[dict]:
    with open(_DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def _find(customer_id: str | None, full_name: str | None, country: str | None) -> dict | None:
    customers = _load_customers()
    for c in customers:
        if customer_id and c["customer_id"] == customer_id:
            return c
        if full_name and full_name.lower() in c["full_name"].lower():
            if not country or c.get("country") == country:
                return c
    return None


def search_customer_profile(
    customer_id: str | None = None,
    full_name: str | None = None,
    country: str | None = None,
    retries: int = 2,
) -> dict:
    for attempt in range(retries + 1):
        try:
            record = _find(customer_id, full_name, country)
            confidence = 1.0 if (record and customer_id) else (0.8 if record else 0.0)
            return {"customer": record, "match_confidence": confidence}
        except OSError:
            if attempt == retries:
                return {"customer": None, "match_confidence": 0.0, "error": "data_unavailable"}
            time.sleep(0.5 * (2 ** attempt))
    return {"customer": None, "match_confidence": 0.0}


def get_identity_status(customer_id: str) -> dict:
    result = search_customer_profile(customer_id=customer_id)
    c = result.get("customer")
    if not c:
        return {"error": "customer_not_found", "identity_status": None}

    expiry_str: Optional[str] = c.get("identity_expiry_date")
    days_until: Optional[int] = None
    if expiry_str:
        delta = (date.fromisoformat(expiry_str) - date.today()).days
        days_until = delta

    return {
        "identity_status": c["identity_status"],
        "identity_expiry_date": expiry_str,
        "days_until_expiry": days_until,
    }


# Backwards-compatible alias used in tests
def get_kyc_status(customer_id: str) -> dict:
    result = get_identity_status(customer_id)
    # expose legacy keys so existing tests pass
    out = dict(result)
    out["kyc_status"] = result.get("identity_status")
    out["kyc_expiry_date"] = result.get("identity_expiry_date")
    return out
