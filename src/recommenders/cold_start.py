"""Cold start recommendation handling."""
from collections import defaultdict


def get_cold_start_recommendations(customer, interactions, products, customers=None, top_k=10):
    """
    Get recommendations for a cold-start customer using segment fallback.

    Args:
        customer:     Customer dict with 'segment' key
        interactions: List of interaction dicts
        products:     List of product dicts (unused, kept for API consistency)
        customers:    List of all customer dicts (used for segment lookup)
        top_k:        Number of recommendations to return

    Returns:
        List of (product_id, score) tuples
    """
    segment = customer.get("segment")
    if not segment:
        return []

    if customers:
        seg_customers = {c["customer_id"] for c in customers if c.get("segment") == segment}
    else:
        seg_customers = {i["customer_id"] for i in interactions if i.get("segment") == segment}

    if not seg_customers:
        return []

    weights = {"purchase": 3.0, "click": 1.0, "view": 0.5}
    scores = defaultdict(float)
    for rec in interactions:
        if rec["customer_id"] in seg_customers:
            scores[rec["product_id"]] += weights.get(rec.get("interaction_type", "view"), 0.5)

    if not scores:
        return []

    max_score = max(scores.values())
    return sorted(
        [(pid, round(v / max_score, 3)) for pid, v in scores.items()],
        key=lambda x: -x[1]
    )[:top_k]
