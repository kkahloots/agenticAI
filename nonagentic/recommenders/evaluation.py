"""Recommendation evaluation metrics."""
import math
from collections import defaultdict


def compute_precision_recall(predictions, ground_truth, k=10):
    """
    Compute precision@k and recall@k.
    
    Args:
        predictions: List of predicted product IDs (ordered)
        ground_truth: Set of relevant product IDs
        k: Cutoff
    
    Returns:
        (precision, recall) tuple
    """
    if not ground_truth:
        return 0.0, 0.0
    
    top_k = predictions[:k]
    hits = len(set(top_k) & ground_truth)
    
    precision = hits / k if k > 0 else 0.0
    recall = hits / len(ground_truth)
    
    return precision, recall


def compute_map(predictions, ground_truth):
    """
    Compute Mean Average Precision.
    
    Args:
        predictions: List of predicted product IDs (ordered)
        ground_truth: Set of relevant product IDs
    
    Returns:
        MAP score
    """
    if not ground_truth:
        return 0.0
    
    ap = 0.0
    running = 0
    
    for i, pid in enumerate(predictions, 1):
        if pid in ground_truth:
            running += 1
            ap += running / i
    
    return ap / len(ground_truth)


def compute_ndcg(predictions, ground_truth, k=10):
    """
    Compute Normalised Discounted Cumulative Gain.
    
    Args:
        predictions: List of predicted product IDs (ordered)
        ground_truth: Set of relevant product IDs
        k: Cutoff
    
    Returns:
        NDCG score
    """
    if not ground_truth:
        return 0.0
    
    top_k = predictions[:k]
    hits = [1 if pid in ground_truth else 0 for pid in top_k]
    
    dcg = sum(h / math.log2(i + 1) for i, h in enumerate(hits, 1))
    ideal = sum(1 / math.log2(i + 1) for i in range(1, min(len(ground_truth), k) + 1))
    
    return dcg / ideal if ideal > 0 else 0.0


def check_data_leakage(interactions, recommend_fn, sample_users=10, min_interactions=10):
    """
    Check whether ground-truth test items are reachable by the recommender.

    Returns a list of dicts, one per user, with train/test sizes, overlap count,
    and hit counts with exclude_purchased on and off.
    """
    by_user = defaultdict(list)
    for rec in interactions:
        by_user[rec["customer_id"]].append(rec)

    eligible = {uid: recs for uid, recs in by_user.items() if len(recs) >= min_interactions}
    sample_uids = list(eligible.keys())[:sample_users]

    rows = []
    for uid in sample_uids:
        recs  = eligible[uid]
        split = max(1, len(recs) * 4 // 5)
        gt    = {r["product_id"] for r in recs[split:]}
        seen  = {r["product_id"] for r in recs[:split]}

        res_excl = recommend_fn(uid, exclude_purchased=True)
        res_incl = recommend_fn(uid, exclude_purchased=False)
        pids_excl = {r["product_id"] for r in res_excl.get("recommendations", [])}
        pids_incl = {r["product_id"] for r in res_incl.get("recommendations", [])}

        rows.append({
            "User":               uid,
            "Train items":        len(seen),
            "Test items (GT)":    len(gt),
            "GT∩Train (overlap)": len(gt & seen),
            "Hits excl=True":     len(pids_excl & gt),
            "Hits excl=False":    len(pids_incl & gt),
            "Leakage risk":       "⚠️ yes" if gt & seen else "✅ none",
        })
    return rows


def evaluate_batch(interactions, recommend_fn, k=10, sample_users=40):
    """
    Offline evaluation harness.
    
    Args:
        interactions: List of interaction dicts
        recommend_fn: Function(customer_id) -> list of product_ids
        k: Cutoff for metrics
        sample_users: Number of users to evaluate
    
    Returns:
        Dict with metrics
    """
    # Group by user
    by_user = defaultdict(list)
    for rec in interactions:
        by_user[rec["customer_id"]].append(rec)
    
    # Only evaluate users with enough interactions
    eligible = {uid: recs for uid, recs in by_user.items() if len(recs) >= 6}
    eval_users = list(eligible.keys())[:sample_users]
    
    precision_list, recall_list, ap_list, ndcg_list = [], [], [], []
    
    for uid in eval_users:
        recs = eligible[uid]
        split = max(1, len(recs) * 4 // 5)
        ground_truth = {r["product_id"] for r in recs[split:]}
        
        if not ground_truth:
            continue
        
        result = recommend_fn(uid)
        predicted = result if isinstance(result, list) else result.get("recommendations", [])
        predicted_ids = [
            p if isinstance(p, str) else p.get("product_id")
            for p in predicted
        ]
        
        p, r = compute_precision_recall(predicted_ids, ground_truth, k)
        precision_list.append(p)
        recall_list.append(r)
        ap_list.append(compute_map(predicted_ids, ground_truth))
        ndcg_list.append(compute_ndcg(predicted_ids, ground_truth, k))
    
    def avg(lst):
        return round(sum(lst) / len(lst), 4) if lst else 0.0
    
    return {
        "users_evaluated": len(precision_list),
        f"precision@{k}": avg(precision_list),
        f"recall@{k}": avg(recall_list),
        "MAP": avg(ap_list),
        "NDCG": avg(ndcg_list),
    }
