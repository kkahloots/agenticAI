"""Segment-level recommendation aggregation."""
from collections import defaultdict


def get_segment_recommendations_batch(segment, customers, recommend_fn, top_k=10, sample_size=15):
    """
    Aggregate recommendations across a customer segment.
    
    Args:
        segment: Segment label (e.g. 'dormant_vip')
        customers: List of customer dicts
        recommend_fn: Function(customer_id) -> dict with 'recommendations' key
        top_k: Number of recommendations to return
        sample_size: Number of customers to sample from segment
    
    Returns:
        List of (product_id, avg_score) tuples
    """
    # Get customers in segment
    seg_custs = [c["customer_id"] for c in customers if c.get("segment") == segment]
    
    if not seg_custs:
        return []
    
    # Sample customers
    sample_custs = seg_custs[:sample_size]
    
    # Aggregate recommendations
    agg_scores = defaultdict(float)
    agg_counts = defaultdict(int)
    
    for cid in sample_custs:
        result = recommend_fn(cid)
        recs = result.get("recommendations", []) if isinstance(result, dict) else result
        
        for rec in recs:
            pid = rec.get("product_id") if isinstance(rec, dict) else rec
            score = rec.get("score", 1.0) if isinstance(rec, dict) else 1.0
            agg_scores[pid] += score
            agg_counts[pid] += 1
    
    if not agg_scores:
        return []
    
    # Normalise by appearance count
    agg_final = {
        pid: round(score / agg_counts[pid], 4)
        for pid, score in agg_scores.items()
    }
    
    # Sort and return top-k
    return sorted(agg_final.items(), key=lambda x: -x[1])[:top_k]
