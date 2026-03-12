"""Collaborative filtering recommendations."""
import math


def _cosine(a, b):
    """Compute cosine similarity between two vectors (dicts)."""
    keys = set(a) & set(b)
    if not keys:
        return 0.0
    dot = sum(a[k] * b[k] for k in keys)
    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def get_similar_users(customer_id, matrix, min_sim=0.05, top_k=20):
    """
    Find similar users via cosine similarity.
    
    Args:
        customer_id: Target customer ID
        matrix: User-item interaction matrix {user_id: {product_id: weight}}
        min_sim: Minimum similarity threshold
        top_k: Number of similar users to return
    
    Returns:
        (similar_user_ids, similarity_scores) tuple
    """
    target = matrix.get(customer_id, {})
    if not target:
        return [], []
    
    sims = []
    for uid, vec in matrix.items():
        if uid == customer_id:
            continue
        s = _cosine(target, vec)
        if s >= min_sim:
            sims.append((uid, s))
    
    sims.sort(key=lambda x: -x[1])
    top_users = sims[:top_k]
    
    return [uid for uid, _ in top_users], [s for _, s in top_users]


def get_collaborative_recommendations(customer_id, matrix, products, exclude_ids=None, top_k=10):
    """
    Get recommendations from similar users.
    
    Args:
        customer_id: Target customer ID
        matrix: User-item interaction matrix
        products: List of product dicts
        exclude_ids: Set of product IDs to exclude
        top_k: Number of recommendations to return
    
    Returns:
        List of (product_id, score) tuples
    """
    exclude_ids = exclude_ids or set()
    
    similar_users, sims = get_similar_users(customer_id, matrix, min_sim=0.05, top_k=20)
    if not similar_users:
        return []
    
    target = matrix.get(customer_id, {})
    scores = {}
    total_sim = sum(sims) or 1.0
    
    for uid, sim in zip(similar_users, sims):
        for pid, w in matrix[uid].items():
            if pid not in target and pid not in exclude_ids:
                scores[pid] = scores.get(pid, 0.0) + (sim * w / total_sim)
    
    if not scores:
        return []
    
    max_s = max(scores.values())
    normalised = {pid: v / max_s for pid, v in scores.items()}
    
    return sorted(normalised.items(), key=lambda x: -x[1])[:top_k]
