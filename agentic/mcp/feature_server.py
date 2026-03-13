"""Feature MCP Server - wraps feature building and selection tools."""

from typing import Optional
from nonagentic.recommenders import get_behaviour_scores, get_content_scores, get_category_affinity
from nonagentic.tools.recommender import _load_customers, _load_products


def build_features(customer_id: str, feature_set: Optional[list] = None) -> dict:
    """Build features for a customer.
    
    feature_set: list of feature names to include, e.g. ['behaviour', 'content', 'category_affinity']
    If None, builds all features.
    """
    customers = _load_customers()
    products = _load_products()
    cust_map = {c["customer_id"]: c for c in customers}
    cust = cust_map.get(customer_id)

    if not cust:
        return {
            "result": None,
            "tool_name": "build_features",
            "execution_status": "not_found",
            "audit": {"customer_id": customer_id},
        }

    feature_set = feature_set or ["behaviour", "content", "category_affinity"]
    features = {}

    if "behaviour" in feature_set:
        features["behaviour_scores"] = get_behaviour_scores(cust, products)

    if "content" in feature_set:
        features["content_scores"] = get_content_scores(cust, products)

    if "category_affinity" in feature_set and "behaviour_scores" in features:
        features["category_affinity"] = get_category_affinity(
            features["behaviour_scores"], products
        )

    return {
        "result": features,
        "tool_name": "build_features",
        "execution_status": "success",
        "audit": {"customer_id": customer_id, "feature_set": feature_set},
    }


def select_features(customer_id: str, available_features: list) -> dict:
    """Select relevant features for a customer based on data availability."""
    customers = _load_customers()
    cust_map = {c["customer_id"]: c for c in customers}
    cust = cust_map.get(customer_id)

    if not cust:
        return {
            "result": available_features,
            "tool_name": "select_features",
            "execution_status": "not_found",
            "audit": {"customer_id": customer_id},
        }

    # Rule-based feature selection based on customer data
    selected = []
    purchase_cats = cust.get("purchase_categories", [])
    engagement = cust.get("engagement_score", 0)

    if engagement > 0.3:
        selected.append("behaviour")
    if purchase_cats:
        selected.append("content")
        selected.append("category_affinity")
    if not selected:
        selected = ["content"]  # fallback

    return {
        "result": selected,
        "tool_name": "select_features",
        "execution_status": "success",
        "audit": {
            "customer_id": customer_id,
            "engagement": engagement,
            "selected": selected,
        },
    }


def compute_category_affinity(customer_id: str) -> dict:
    """Compute category affinity scores for a customer."""
    customers = _load_customers()
    products = _load_products()
    cust_map = {c["customer_id"]: c for c in customers}
    cust = cust_map.get(customer_id)

    if not cust:
        return {
            "result": {},
            "tool_name": "compute_category_affinity",
            "execution_status": "not_found",
            "audit": {"customer_id": customer_id},
        }

    behav_scores = get_behaviour_scores(cust, products)
    affinity = get_category_affinity(behav_scores, products)

    return {
        "result": affinity,
        "tool_name": "compute_category_affinity",
        "execution_status": "success",
        "audit": {"customer_id": customer_id},
    }
