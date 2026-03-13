"""Dataset analysis and statistics."""
from collections import Counter


def get_interaction_stats(interactions):
    """
    Get interaction type breakdown.
    
    Args:
        interactions: List of interaction dicts
    
    Returns:
        Dict {interaction_type: count}
    """
    return dict(Counter(i["interaction_type"] for i in interactions))


def get_category_stats(interactions):
    """
    Get category breakdown from interactions.
    
    Args:
        interactions: List of interaction dicts
    
    Returns:
        Dict {category: count}
    """
    return dict(Counter(i.get("category") for i in interactions if i.get("category")))


def get_segment_stats(customers):
    """
    Get customer segment breakdown.
    
    Args:
        customers: List of customer dicts
    
    Returns:
        Dict {segment: count}
    """
    return dict(Counter(c.get("segment") for c in customers if c.get("segment")))
