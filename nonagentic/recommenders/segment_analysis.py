"""Segment-level recommendation analysis."""
from collections import defaultdict, Counter


def get_segment_recommendations(segment, interactions, products, customers=None, exclude_ids=None, top_k=10):
    """
    Get top recommendations for a segment by aggregating peer interactions.
    
    Args:
        segment: Segment label (e.g. 'dormant_vip')
        interactions: List of interaction dicts
        products: List of product dicts
        customers: List of customer dicts (optional, for segment lookup)
        exclude_ids: Set of product IDs to exclude
        top_k: Number of recommendations to return
    
    Returns:
        List of (product_id, score) tuples, sorted by score descending
    """
    exclude_ids = exclude_ids or set()
    weights = {"purchase": 3.0, "click": 1.0, "view": 0.5}
    
    # Get all customers in segment
    if customers:
        seg_customers = {c["customer_id"] for c in customers if c.get("segment") == segment}
    else:
        seg_customers = {c["customer_id"] for c in interactions if c.get("segment") == segment}
    
    if not seg_customers:
        return []
    
    # Aggregate scores
    scores = defaultdict(float)
    for rec in interactions:
        if rec["customer_id"] in seg_customers and rec["product_id"] not in exclude_ids:
            w = weights.get(rec.get("interaction_type", "view"), 0.5)
            scores[rec["product_id"]] += w
    
    if not scores:
        return []
    
    # Normalise
    max_score = max(scores.values())
    normalised = {pid: v / max_score for pid, v in scores.items()}
    
    # Sort and return top-k
    return sorted(normalised.items(), key=lambda x: -x[1])[:top_k]


def get_segment_stats(segment, customers, interactions):
    """
    Get statistics for a segment.
    
    Args:
        segment: Segment label
        customers: List of customer dicts
        interactions: List of interaction dicts
    
    Returns:
        Dict with segment stats
    """
    seg_custs = [c for c in customers if c.get("segment") == segment]
    seg_ints = [i for i in interactions if i["customer_id"] in {c["customer_id"] for c in seg_custs}]
    
    itype_counts = Counter(i["interaction_type"] for i in seg_ints)
    cat_counts = Counter(i.get("category") for i in seg_ints)
    
    return {
        "segment": segment,
        "customer_count": len(seg_custs),
        "interaction_count": len(seg_ints),
        "interaction_types": dict(itype_counts),
        "categories": dict(cat_counts),
    }
