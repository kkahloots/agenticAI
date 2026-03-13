"""Feature Builder - wraps nonagentic feature extraction."""

from typing import Optional
from nonagentic.recommenders import get_behaviour_scores, get_content_scores, get_category_affinity
from nonagentic.tools.recommender import _load_customers, _load_products


def build_features(customer_id: str, feature_set: Optional[list] = None) -> dict:
    """Build features for a customer."""
    customers = _load_customers()
    products = _load_products()
    cust_map = {c["customer_id"]: c for c in customers}
    cust = cust_map.get(customer_id)
    if not cust:
        return {}

    feature_set = feature_set or ["behaviour", "content", "category_affinity"]
    features = {}

    if "behaviour" in feature_set:
        features["behaviour_scores"] = get_behaviour_scores(cust, products)
    if "content" in feature_set:
        features["content_scores"] = get_content_scores(cust, products)
    if "category_affinity" in feature_set and "behaviour_scores" in features:
        features["category_affinity"] = get_category_affinity(features["behaviour_scores"], products)

    return features
