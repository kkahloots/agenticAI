"""Recommendation MCP Server - wraps recommendation and lead scoring tools."""

from typing import Optional
from nonagentic.tools.leads import score_leads as _score, bulk_recommend as _bulk
from nonagentic.tools.functional import recommend_offer as _recommend
from nonagentic.tools.recommender import (
    recommend,
    _load_customers,
    _load_interactions,
    _load_products,
    _build_user_item_matrix,
    _collaborative_scores,
)
from nonagentic.recommenders import (
    get_segment_recommendations,
    get_similar_users,
    get_behaviour_scores,
    get_content_scores,
    get_category_affinity,
    get_cold_start_recommendations,
    get_segment_recommendations_batch,
    evaluate_batch,
    check_data_leakage,
)


# ── Level 3 tools (existing) ──────────────────────────────────────────────────

def score_leads(offer_code: str, top_n: int = 20, segment: Optional[str] = None) -> dict:
    """Score and rank leads for an offer."""
    result = _score(offer_code, top_n=top_n, segment=segment)
    return {
        "result": result,
        "tool_name": "score_leads",
        "execution_status": "success",
        "audit": {"offer_code": offer_code, "top_n": top_n, "segment": segment},
    }


def recommend_offer(customer_id: str, context: str = "") -> dict:
    """Recommend best offer for customer."""
    result = _recommend(customer_id, context=context)
    return {
        "result": result,
        "tool_name": "recommend_offer",
        "execution_status": "success" if result.get("offer_code") else "no_offers",
        "audit": {"customer_id": customer_id},
    }


def bulk_recommend(offer_code: str, segment: Optional[str] = None, top_n: int = 50) -> dict:
    """Generate bulk recommendation execution plan."""
    result = _bulk(offer_code, segment=segment, top_n=top_n)
    return {
        "result": result,
        "tool_name": "bulk_recommend",
        "execution_status": "success",
        "audit": {"offer_code": offer_code, "segment": segment, "top_n": top_n},
    }


def rank_next_best_action(customer_id: str) -> dict:
    """Rank all available offers for customer (NBA)."""
    result = _recommend(customer_id)
    return {
        "result": result,
        "tool_name": "rank_next_best_action",
        "execution_status": "success" if result.get("offer_code") else "no_offers",
        "audit": {"customer_id": customer_id},
    }


# ── Level 5 tools (new) ───────────────────────────────────────────────────────

def _get_data():
    """Load shared data objects."""
    customers = _load_customers()
    interactions = _load_interactions()
    products = _load_products()
    matrix = _build_user_item_matrix(interactions)
    cust_map = {c["customer_id"]: c for c in customers}
    prod_map = {p["product_id"]: p for p in products}
    return customers, interactions, products, matrix, cust_map, prod_map


def segment_recommendations(segment: str, top_k: int = 10) -> dict:
    """UC1: Get segment-based recommendations (user-based)."""
    customers, interactions, products, _, _, _ = _get_data()
    result = get_segment_recommendations(segment, interactions, products, customers=customers, top_k=top_k)
    return {
        "result": result,
        "tool_name": "segment_recommendations",
        "execution_status": "success",
        "audit": {"segment": segment, "top_k": top_k, "count": len(result)},
    }


def collaborative_scores(customer_id: str, top_k: int = 10) -> dict:
    """UC2: Get collaborative filtering scores and similar users."""
    _, _, _, matrix, cust_map, prod_map = _get_data()
    similar_users, _ = get_similar_users(customer_id, matrix, min_sim=0.05, top_k=8)
    scores, _ = _collaborative_scores(customer_id, matrix)
    top_collab = sorted(scores.items(), key=lambda x: -x[1])[:top_k]
    return {
        "result": {
            "similar_users": similar_users,
            "recommendations": [
                {"product_id": pid, "score": s, "name": prod_map.get(pid, {}).get("name", ""),
                 "category": prod_map.get(pid, {}).get("category", "")}
                for pid, s in top_collab
            ],
        },
        "tool_name": "collaborative_scores",
        "execution_status": "success",
        "audit": {"customer_id": customer_id, "similar_users": len(similar_users)},
    }


def behaviour_scores(customer_id: str, top_k: int = 10) -> dict:
    """UC3: Get behaviour and content scores."""
    _, _, products, _, cust_map, prod_map = _get_data()
    cust = cust_map.get(customer_id)
    if not cust:
        return {"result": None, "tool_name": "behaviour_scores", "execution_status": "not_found",
                "audit": {"customer_id": customer_id}}

    behav = get_behaviour_scores(cust, products)
    content = get_content_scores(cust, products)
    affinity = get_category_affinity(behav, products)

    # Combine and rank
    all_prods = set(behav) | set(content)
    combined = []
    for pid in all_prods:
        b = behav.get(pid, 0)
        c = content.get(pid, 0)
        combined.append({
            "product_id": pid,
            "name": prod_map.get(pid, {}).get("name", ""),
            "category": prod_map.get(pid, {}).get("category", ""),
            "behaviour_score": round(b, 3),
            "content_score": round(c, 3),
            "combined": round(0.6 * b + 0.4 * c, 3),
        })
    combined.sort(key=lambda x: -x["combined"])

    return {
        "result": {
            "recommendations": combined[:top_k],
            "category_affinity": affinity,
        },
        "tool_name": "behaviour_scores",
        "execution_status": "success",
        "audit": {"customer_id": customer_id},
    }


def hybrid_recommend(customer_id: str, top_k: int = 10, exclude_purchased: bool = True) -> dict:
    """UC4: Full hybrid recommendation."""
    result = recommend(customer_id, top_k=top_k, exclude_purchased=exclude_purchased)
    return {
        "result": result,
        "tool_name": "hybrid_recommend",
        "execution_status": "success",
        "audit": {"customer_id": customer_id, "top_k": top_k},
    }


def cold_start_recommend(customer_id: str, segment: str, top_k: int = 10) -> dict:
    """UC5: Cold start recommendations."""
    customers, interactions, products, _, _, _ = _get_data()
    cold_cust = {"customer_id": customer_id, "segment": segment,
                 "purchase_categories": [], "engagement_score": 0.1}
    result = get_cold_start_recommendations(cold_cust, interactions, products, customers=customers, top_k=top_k)
    return {
        "result": result,
        "tool_name": "cold_start_recommend",
        "execution_status": "success",
        "audit": {"customer_id": customer_id, "segment": segment, "top_k": top_k},
    }


def segment_batch_recommend(segment: str, top_k: int = 10, sample_size: int = 15) -> dict:
    """UC6: Cross-user segment batch recommendations."""
    customers, _, _, _, _, _ = _get_data()
    result = get_segment_recommendations_batch(segment, customers, recommend, top_k=top_k, sample_size=sample_size)
    return {
        "result": result,
        "tool_name": "segment_batch_recommend",
        "execution_status": "success",
        "audit": {"segment": segment, "sample_size": sample_size},
    }


def evaluate_recommendations(sample_users: int = 40, k: int = 10) -> dict:
    """UC7: Offline evaluation of recommendations."""
    interactions = _load_interactions()
    metrics = evaluate_batch(
        interactions,
        lambda uid: recommend(uid, exclude_purchased=False),
        k=k,
        sample_users=sample_users,
    )
    return {
        "result": metrics,
        "tool_name": "evaluate_recommendations",
        "execution_status": "success",
        "audit": {"sample_users": sample_users, "k": k},
    }


def detect_data_leakage(sample_users: int = 10) -> dict:
    """UC7: Check for data leakage in evaluation."""
    interactions = _load_interactions()
    rows = check_data_leakage(interactions, recommend, sample_users=sample_users)
    return {
        "result": rows,
        "tool_name": "detect_data_leakage",
        "execution_status": "success",
        "audit": {"sample_users": sample_users},
    }


def popularity_scores(top_k: int = 10) -> dict:
    """Get global popularity scores across all customers."""
    interactions = _load_interactions()
    products = _load_products()
    prod_map = {p["product_id"]: p for p in products}

    from collections import Counter
    counts = Counter(i["product_id"] for i in interactions)
    total = sum(counts.values()) or 1
    top = counts.most_common(top_k)

    result = [
        {
            "product_id": pid,
            "name": prod_map.get(pid, {}).get("name", ""),
            "category": prod_map.get(pid, {}).get("category", ""),
            "count": cnt,
            "score": round(cnt / max(counts.values()), 3),
        }
        for pid, cnt in top
    ]
    return {
        "result": result,
        "tool_name": "popularity_scores",
        "execution_status": "success",
        "audit": {"top_k": top_k},
    }
