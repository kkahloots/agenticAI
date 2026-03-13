"""Analytics MCP Server - wraps analytics, SQL, and evaluation tools."""

from typing import Optional
from collections import Counter, defaultdict
from nonagentic.tools.recommender import (
    _load_customers, _load_interactions, _load_products,
    _build_user_item_matrix, _cosine, recommend,
)
from nonagentic.recommenders import evaluate_batch, check_data_leakage


# ── SQL execution (safe read-only simulation) ─────────────────────────────────

def run_sql_query(query: str, safe_mode: bool = True) -> dict:
    """Execute a safe read-only SQL query (simulated against in-memory data).

    In this implementation SQL is pattern-matched to in-memory data since
    there is no live database.  Only SELECT statements are accepted.
    """
    query_upper = query.strip().upper()
    if not query_upper.startswith("SELECT"):
        return {
            "result": None,
            "tool_name": "run_sql_query",
            "execution_status": "rejected",
            "audit": {"reason": "only SELECT allowed", "query": query[:120]},
        }

    customers = _load_customers()
    interactions = _load_interactions()
    products = _load_products()

    # Pattern: dormant_vip segment
    if "DORMANT_VIP" in query_upper:
        rows = [
            {"customer_id": c["customer_id"], "segment": c["segment"],
             "engagement_score": c.get("engagement_score", 0)}
            for c in customers if c.get("segment") == "dormant_vip"
        ]
        return {
            "result": rows,
            "tool_name": "run_sql_query",
            "execution_status": "success",
            "audit": {"rows": len(rows), "query": query[:120]},
        }

    # Pattern: segment filter
    if "SEGMENT" in query_upper and "WHERE" in query_upper:
        rows = [
            {"customer_id": c["customer_id"], "segment": c["segment"]}
            for c in customers
        ]
        return {
            "result": rows,
            "tool_name": "run_sql_query",
            "execution_status": "success",
            "audit": {"rows": len(rows), "query": query[:120]},
        }

    # Default: return customer list
    rows = [{"customer_id": c["customer_id"], "segment": c.get("segment", "")} for c in customers]
    return {
        "result": rows,
        "tool_name": "run_sql_query",
        "execution_status": "success",
        "audit": {"rows": len(rows), "query": query[:120]},
    }


# ── Similarity matrix stats ───────────────────────────────────────────────────

def build_similarity_matrix_stats(customer_id: str, top_k: int = 8) -> dict:
    """Compute similarity statistics for a customer."""
    interactions = _load_interactions()
    customers = _load_customers()
    matrix = _build_user_item_matrix(interactions)
    cust_map = {c["customer_id"]: c for c in customers}

    target_vec = matrix.get(customer_id, {})
    sims = []
    for other_id, other_vec in matrix.items():
        if other_id == customer_id:
            continue
        sim = _cosine(target_vec, other_vec)
        if sim > 0:
            sims.append({"customer_id": other_id, "similarity": round(sim, 4),
                         "segment": cust_map.get(other_id, {}).get("segment", "")})

    sims.sort(key=lambda x: -x["similarity"])
    top = sims[:top_k]

    return {
        "result": {
            "customer_id": customer_id,
            "top_similar": top,
            "total_comparable": len(sims),
            "avg_similarity": round(sum(s["similarity"] for s in top) / max(len(top), 1), 4),
        },
        "tool_name": "build_similarity_matrix_stats",
        "execution_status": "success",
        "audit": {"customer_id": customer_id, "top_k": top_k},
    }


# ── Segment recommendation stats ─────────────────────────────────────────────

def build_segment_recommendation_stats(segment: str, sample_size: int = 15) -> dict:
    """Aggregate recommendation stats for a segment."""
    customers = _load_customers()
    seg_custs = [c["customer_id"] for c in customers if c.get("segment") == segment][:sample_size]

    score_totals: dict = defaultdict(float)
    score_counts: dict = defaultdict(int)

    for cid in seg_custs:
        try:
            result = recommend(cid, top_k=10)
            for rec in result.get("recommendations", []):
                pid = rec["product_id"]
                score_totals[pid] += rec.get("score", 0)
                score_counts[pid] += 1
        except Exception:
            continue

    avg_scores = {
        pid: round(score_totals[pid] / score_counts[pid], 4)
        for pid in score_totals
    }
    top = sorted(avg_scores.items(), key=lambda x: -x[1])[:10]

    return {
        "result": {
            "segment": segment,
            "customers_sampled": len(seg_custs),
            "top_products": [{"product_id": pid, "avg_score": s} for pid, s in top],
        },
        "tool_name": "build_segment_recommendation_stats",
        "execution_status": "success",
        "audit": {"segment": segment, "sample_size": sample_size},
    }


# ── Evaluation tools ──────────────────────────────────────────────────────────

def evaluate_recommendations_tool(sample_users: int = 40, k: int = 10) -> dict:
    """Offline evaluation of recommendations."""
    interactions = _load_interactions()
    metrics = evaluate_batch(
        interactions,
        lambda uid: recommend(uid, exclude_purchased=False),
        k=k,
        sample_users=sample_users,
    )
    return {
        "result": metrics,
        "tool_name": "evaluate_recommendations_tool",
        "execution_status": "success",
        "audit": {"sample_users": sample_users, "k": k},
    }


def detect_leakage_tool(sample_users: int = 10) -> dict:
    """Check for data leakage in evaluation."""
    interactions = _load_interactions()
    rows = check_data_leakage(interactions, recommend, sample_users=sample_users)
    return {
        "result": rows,
        "tool_name": "detect_leakage_tool",
        "execution_status": "success",
        "audit": {"sample_users": sample_users},
    }


# ── Segment / campaign tools (Level 3) ───────────────────────────────────────

def generate_segment(criteria: dict) -> dict:
    """Generate customer segment based on criteria."""
    customers = _load_customers()
    segment_name = criteria.get("segment")
    min_engagement = criteria.get("min_engagement", 0)

    filtered = [
        c for c in customers
        if (not segment_name or c.get("segment") == segment_name)
        and c.get("engagement_score", 0) >= min_engagement
    ]

    return {
        "result": {
            "customers": [c["customer_id"] for c in filtered],
            "count": len(filtered),
            "criteria": criteria,
        },
        "tool_name": "generate_segment",
        "execution_status": "success",
        "audit": {"criteria": criteria, "count": len(filtered)},
    }


def campaign_performance_summary() -> dict:
    """Summarize campaign performance (simulated)."""
    return {
        "result": {
            "campaigns": [
                {"offer_code": "OFFER-001", "sends": 150, "conversions": 23, "conversion_rate": 0.153},
                {"offer_code": "OFFER-002", "sends": 200, "conversions": 18, "conversion_rate": 0.090},
                {"offer_code": "OFFER-003", "sends": 80,  "conversions": 12, "conversion_rate": 0.150},
            ]
        },
        "tool_name": "campaign_performance_summary",
        "execution_status": "success",
        "audit": {},
    }


def identify_high_return_risk(threshold: float = 0.7) -> dict:
    """Identify customers with high return risk (simulated)."""
    customers = _load_customers()
    at_risk = [
        {"customer_id": c["customer_id"], "return_risk": c.get("return_risk", 0),
         "segment": c.get("segment", "")}
        for c in customers
        if c.get("return_risk", 0) >= threshold
    ]
    return {
        "result": at_risk,
        "tool_name": "identify_high_return_risk",
        "execution_status": "success",
        "audit": {"threshold": threshold, "count": len(at_risk)},
    }
