from __future__ import annotations

import json
import math
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_DATA_DIR = Path(__file__).parent.parent.parent / "data"

# Interaction weights
_WEIGHTS = {"purchase": 3.0, "click": 1.0, "view": 0.5}

# Hybrid ranking weights (configurable via env)
def _hybrid_weights() -> dict:
    raw = os.getenv("RECOMMENDATION_WEIGHTS", "")
    if raw:
        try:
            return json.loads(raw)
        except Exception:
            pass
    return {"collab": 0.4, "behaviour": 0.3, "content": 0.2, "popularity": 0.1}


def _load_interactions() -> list[dict]:
    path = _DATA_DIR / "interactions.json"
    if not path.exists():
        return []
    with open(path) as f:
        return json.load(f)


def _load_customers() -> list[dict]:
    path = _DATA_DIR / "customers.json"
    if not path.exists():
        return []
    with open(path) as f:
        return json.load(f)


def _load_products() -> list[dict]:
    path = _DATA_DIR / "products.json"
    if not path.exists():
        return []
    with open(path) as f:
        return json.load(f)


def _time_decay(ts: str | None, half_life_days: float = 90.0) -> float:
    """Exponential decay: weight = 0.5^(age_days / half_life_days). Returns 1.0 if no timestamp."""
    if not ts:
        return 1.0
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        age_days = (datetime.now(timezone.utc) - dt).total_seconds() / 86400
        return math.pow(0.5, max(age_days, 0) / half_life_days)
    except Exception:
        return 1.0


def _build_user_item_matrix(interactions: list[dict]) -> dict[str, dict[str, float]]:
    """Build sparse user→{item: weight} matrix with time-decay."""
    matrix: dict[str, dict[str, float]] = {}
    for rec in interactions:
        uid = rec["customer_id"]
        pid = rec["product_id"]
        w = _WEIGHTS.get(rec.get("interaction_type", "view"), 0.5)
        w *= _time_decay(rec.get("timestamp"))
        matrix.setdefault(uid, {})[pid] = matrix.get(uid, {}).get(pid, 0.0) + w
    return matrix


def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
    keys = set(a) & set(b)
    if not keys:
        return 0.0
    dot = sum(a[k] * b[k] for k in keys)
    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _popularity_scores(interactions: list[dict]) -> dict[str, float]:
    counts: dict[str, float] = {}
    for rec in interactions:
        pid = rec["product_id"]
        counts[pid] = counts.get(pid, 0.0) + _WEIGHTS.get(rec.get("interaction_type", "view"), 0.5)
    if not counts:
        return {}
    max_val = max(counts.values())
    return {pid: v / max_val for pid, v in counts.items()}


def _collaborative_scores(
    customer_id: str,
    user_matrix: dict[str, dict[str, float]],
    min_sim: float = 0.05,
    top_k_users: int = 50,
) -> tuple[dict[str, float], list[str]]:
    """Return {product_id: score} from similar users and list of similar user IDs."""
    target = user_matrix.get(customer_id, {})
    if not target:
        return {}, []

    sims = []
    for uid, vec in user_matrix.items():
        if uid == customer_id:
            continue
        s = _cosine(target, vec)
        if s >= min_sim:
            sims.append((uid, s))

    sims.sort(key=lambda x: x[1], reverse=True)
    top_users = sims[:top_k_users]
    similar_user_ids = [uid for uid, _ in top_users]

    scores: dict[str, float] = {}
    total_sim = sum(s for _, s in top_users) or 1.0
    for uid, sim in top_users:
        for pid, w in user_matrix[uid].items():
            if pid not in target:  # only unseen items
                scores[pid] = scores.get(pid, 0.0) + (sim * w / total_sim)

    if scores:
        max_s = max(scores.values())
        scores = {pid: v / max_s for pid, v in scores.items()}

    return scores, similar_user_ids


def _behaviour_scores(
    customer: dict,
    all_products: list[dict],
) -> dict[str, float]:
    """Score items based on customer's own interaction signals with normal distribution variation."""
    import numpy as np
    
    cats = set(customer.get("purchase_categories", []))
    clicks = set(customer.get("click_history") or [])
    views = set(customer.get("view_history") or [])
    engagement = customer.get("engagement_score", 0.5)

    scores: dict[str, float] = {}
    for p in all_products:
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
            variation = np.random.normal(s, s * 0.3)
            scores[pid] = max(0.01, min(variation, 1.0))
        else:
            noise = np.random.normal(0.05, 0.05)
            scores[pid] = max(0.0, min(noise, 0.3))
    
    return scores





def _explanation(pid: str, scores: dict, dominant: str) -> str:
    labels = {
        "collab": "Customers similar to you purchased this item",
        "behaviour": "Based on your recent browsing and purchase activity",
        "content": "Matches your purchase category preferences",
        "popularity": "Popular item among all customers",
        "cold_start": "Trending item recommended for new customers",
        "segment_fallback": "Popular in your customer segment",
    }
    return labels.get(dominant, "Recommended based on your profile")


def recommend(
    customer_id: str,
    top_k: int = 20,
    exclude_purchased: bool = True,
) -> dict:
    """
    Main recommendation API.
    Returns top_k recommendations with scores, explanations, and source model.
    """
    top_k = int(os.getenv("RECOMMENDATION_TOP_K", top_k))
    min_sim = float(os.getenv("RECOMMENDATION_MIN_SIMILARITY", "0.05"))
    cold_k = int(os.getenv("RECOMMENDATION_COLD_START_K", "5"))
    hw = _hybrid_weights()

    interactions = _load_interactions()
    customers = _load_customers()
    products = _load_products()

    customer = next((c for c in customers if c["customer_id"] == customer_id), None)
    if not customer:
        return {"error": "customer_not_found", "recommendations": []}

    user_matrix = _build_user_item_matrix(interactions)
    pop_scores = _popularity_scores(interactions)

    purchased = set(customer.get("purchase_categories", []))
    user_interactions = user_matrix.get(customer_id, {})
    is_cold_start = len(user_interactions) < 3

    # Cold start: return popular items for segment
    if is_cold_start:
        segment = customer.get("segment", "")
        seg_customers = {c["customer_id"] for c in customers if c.get("segment") == segment}
        seg_scores: dict[str, float] = {}
        for rec in interactions:
            if rec["customer_id"] in seg_customers:
                pid = rec["product_id"]
                seg_scores[pid] = seg_scores.get(pid, 0.0) + _WEIGHTS.get(rec.get("interaction_type", "view"), 0.5)

        fallback_scores = seg_scores if seg_scores else pop_scores
        if fallback_scores:
            max_v = max(fallback_scores.values())
            fallback_scores = {pid: v / max_v for pid, v in fallback_scores.items()}

        source = "segment_fallback" if seg_scores else "cold_start"
        top_items = sorted(fallback_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        recs = [
            {
                "product_id": pid,
                "score": round(score, 4),
                "explanation": _explanation(pid, {}, source),
                "source_model": source,
                "confidence": round(score * 0.7, 4),
            }
            for pid, score in top_items
        ]
        return {
            "customer_id": customer_id,
            "cold_start": True,
            "recommendations": recs,
            "similar_users": [],
        }

    # Full pipeline
    collab_scores, similar_users = _collaborative_scores(customer_id, user_matrix, min_sim)
    behav_scores = _behaviour_scores(customer, products)
    cont_scores = _content_scores(customer, products)

    # Gather all candidate products
    all_pids = (
        set(collab_scores)
        | set(behav_scores)
        | set(cont_scores)
        | set(pop_scores)
    )

    # Exclude already-interacted items if requested
    if exclude_purchased:
        all_pids -= set(user_interactions.keys())

    if not all_pids:
        all_pids = set(pop_scores.keys()) - set(user_interactions.keys())

    results = []
    for pid in all_pids:
        c_s = collab_scores.get(pid, 0.0)
        b_s = behav_scores.get(pid, 0.0)
        co_s = cont_scores.get(pid, 0.0)
        p_s = pop_scores.get(pid, 0.0)

        final = (
            hw["collab"] * c_s
            + hw["behaviour"] * b_s
            + hw["content"] * co_s
            + hw["popularity"] * p_s
        )

        # Determine dominant signal for explanation
        signal_scores = {"collab": c_s, "behaviour": b_s, "content": co_s, "popularity": p_s}
        dominant = max(signal_scores, key=signal_scores.get)

        results.append({
            "product_id": pid,
            "score": round(final, 4),
            "explanation": _explanation(pid, signal_scores, dominant),
            "source_model": "hybrid",
            "dominant_signal": dominant,
            "confidence": round(min(final * 1.1, 1.0), 4),
            "_signals": {"collab": round(c_s, 3), "behaviour": round(b_s, 3),
                         "content": round(co_s, 3), "popularity": round(p_s, 3)},
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    top_results = results[:top_k]

    # Clean internal fields from output
    for r in top_results:
        r.pop("dominant_signal", None)
        r.pop("_signals", None)

    return {
        "customer_id": customer_id,
        "cold_start": False,
        "recommendations": top_results,
        "similar_users": similar_users[:10],
    }


def evaluate_recommendations(
    test_interactions: list[dict],
    k: int = 10,
    sample_users: int = 50,
) -> dict:
    """
    Offline evaluation: precision@k, recall@k, MAP, NDCG.
    Splits interactions into train/test and evaluates recommendations.
    """
    from collections import defaultdict

    # Group by user
    by_user: dict[str, list[dict]] = defaultdict(list)
    for rec in test_interactions:
        by_user[rec["customer_id"]].append(rec)

    # Only evaluate users with enough interactions
    eligible = {uid: recs for uid, recs in by_user.items() if len(recs) >= 4}
    users = list(eligible.keys())[:sample_users]

    if not users:
        return {"error": "insufficient_data"}

    precision_list, recall_list, ap_list, ndcg_list = [], [], [], []

    for uid in users:
        recs = eligible[uid]
        # Use last 20% as ground truth
        split = max(1, len(recs) * 4 // 5)
        ground_truth = {r["product_id"] for r in recs[split:]}
        if not ground_truth:
            continue

        result = recommend(uid, top_k=k)
        predicted = [r["product_id"] for r in result.get("recommendations", [])]

        hits = [1 if p in ground_truth else 0 for p in predicted]

        # Precision@k
        precision_list.append(sum(hits) / k if k else 0)

        # Recall@k
        recall_list.append(sum(hits) / len(ground_truth) if ground_truth else 0)

        # Average Precision
        ap, running = 0.0, 0
        for i, h in enumerate(hits, 1):
            if h:
                running += 1
                ap += running / i
        ap_list.append(ap / len(ground_truth) if ground_truth else 0)

        # NDCG@k
        dcg = sum(h / math.log2(i + 1) for i, h in enumerate(hits, 1))
        ideal = sum(1 / math.log2(i + 1) for i in range(1, min(len(ground_truth), k) + 1))
        ndcg_list.append(dcg / ideal if ideal else 0)

    def _avg(lst):
        return round(sum(lst) / len(lst), 4) if lst else 0.0

    return {
        "users_evaluated": len(precision_list),
        f"precision@{k}": _avg(precision_list),
        f"recall@{k}": _avg(recall_list),
        "MAP": _avg(ap_list),
        "NDCG": _avg(ndcg_list),
    }


def _content_scores(
    customer: dict,
    all_products: list[dict],
) -> dict[str, float]:
    """Score items by category overlap with customer purchase history with normal distribution variation."""
    import numpy as np
    
    cats = set(customer.get("purchase_categories", []))
    if not cats:
        return {}
    scores: dict[str, float] = {}
    for p in all_products:
        p_cats = set(p.get("tags", []) + ([p["category"]] if p.get("category") else []))
        overlap = len(cats & p_cats)
        if overlap:
            base_score = min(overlap / max(len(cats), 1), 1.0)
            variation = np.random.normal(base_score, base_score * 0.25)
            scores[p["product_id"]] = max(0.01, min(variation, 1.0))
        else:
            noise = np.random.normal(0.03, 0.04)
            scores[p["product_id"]] = max(0.0, min(noise, 0.25))
    return scores
