"""Behaviour-based and content-based recommendation scoring."""
from collections import Counter


def get_behaviour_scores(customer, products):
    """
    Score items based on customer's own interaction signals.
    
    Args:
        customer: Customer dict with purchase_categories, engagement_score
        products: List of product dicts
    
    Returns:
        Dict {product_id: score}
    """
    cats = set(customer.get("purchase_categories", []))
    clicks = set(customer.get("click_history") or [])
    views = set(customer.get("view_history") or [])
    engagement = customer.get("engagement_score", 0.5)
    
    scores = {}
    for p in products:
        pid = p["product_id"]
        s = 0.0
        if pid in clicks:
            s += 0.5
        if pid in views:
            s += 0.2
        if p.get("category") in cats:
            s += 0.3
        s *= (0.5 + engagement * 0.5)
        if s > 0:
            scores[pid] = min(s, 1.0)
    
    return scores


def get_content_scores(customer, products):
    """
    Score items by category overlap with customer purchase history.
    
    Args:
        customer: Customer dict with purchase_categories
        products: List of product dicts
    
    Returns:
        Dict {product_id: score}
    """
    cats = set(customer.get("purchase_categories", []))
    if not cats:
        return {}
    
    scores = {}
    for p in products:
        p_cats = set(p.get("tags", []) + ([p["category"]] if p.get("category") else []))
        overlap = len(cats & p_cats)
        if overlap:
            scores[p["product_id"]] = min(overlap / max(len(cats), 1), 1.0)
    
    return scores


def get_category_affinity(behaviour_scores, products):
    """
    Aggregate behaviour scores by category.
    
    Args:
        behaviour_scores: Dict {product_id: score}
        products: List of product dicts
    
    Returns:
        Dict {category: total_score}
    """
    prod_map = {p["product_id"]: p for p in products}
    affinity = Counter()
    
    for pid, score in behaviour_scores.items():
        cat = prod_map.get(pid, {}).get("category", "unknown")
        affinity[cat] += score
    
    return dict(affinity)
