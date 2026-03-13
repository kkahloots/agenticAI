"""Feature Selector - dynamic feature selection based on customer data."""

from typing import Optional
from nonagentic.tools.recommender import _load_customers


def select_features(customer_id: str, mode: str = "deterministic") -> list:
    """Select relevant features for a customer.
    
    deterministic: rule-based selection
    dynamic: uses llm_reasoning_server (with fallback)
    """
    customers = _load_customers()
    cust_map = {c["customer_id"]: c for c in customers}
    cust = cust_map.get(customer_id, {})

    if mode == "dynamic":
        from agentic.mcp import llm_reasoning_server
        context = {
            "engagement_score": cust.get("engagement_score", 0),
            "purchase_categories": cust.get("purchase_categories", []),
        }
        result = llm_reasoning_server.suggest_feature_priority(customer_id, context)
        return [f["feature"] for f in result["result"]["features"]]

    # Deterministic rule-based
    selected = []
    if cust.get("engagement_score", 0) > 0.3:
        selected.append("behaviour")
    if cust.get("purchase_categories"):
        selected.append("content")
        selected.append("category_affinity")
    return selected or ["content"]
