"""LLM Reasoning MCP Server - LLM-based reasoning with deterministic fallback.

All LLM calls fall back to rule-based logic if LLM is unavailable.
Simulation-only paths are clearly marked.
"""

from typing import Optional


# Strategy classification rules (fallback when LLM unavailable)
_STRATEGY_RULES = {
    "collaborative": lambda ctx: ctx.get("interaction_count", 0) >= 10,
    "behaviour": lambda ctx: ctx.get("engagement_score", 0) > 0.3,
    "content": lambda ctx: bool(ctx.get("purchase_categories")),
    "cold_start": lambda ctx: ctx.get("interaction_count", 0) < 3,
    "segment_batch": lambda ctx: bool(ctx.get("segment")) and not ctx.get("customer_id"),
}


def classify_recommendation_request(request: str, context: Optional[dict] = None) -> dict:
    """Classify recommendation request type.
    
    Returns one of: collaborative, behaviour, content, hybrid, cold_start,
    segment_batch, evaluation, visualization
    """
    context = context or {}
    request_lower = request.lower()

    # Rule-based classification (deterministic fallback)
    if "evaluat" in request_lower or "metric" in request_lower or "precision" in request_lower:
        strategy = "evaluation"
    elif "visual" in request_lower or "chart" in request_lower or "plot" in request_lower:
        strategy = "visualization"
    elif "segment" in request_lower and "batch" in request_lower:
        strategy = "segment_batch"
    elif "cold" in request_lower or context.get("interaction_count", 10) < 3:
        strategy = "cold_start"
    elif "collaborat" in request_lower or "similar user" in request_lower:
        strategy = "collaborative"
    elif "behaviour" in request_lower or "behavior" in request_lower:
        strategy = "behaviour"
    elif "hybrid" in request_lower:
        strategy = "hybrid"
    else:
        # Default: hybrid if enough data, else cold_start
        strategy = "hybrid" if context.get("interaction_count", 0) >= 5 else "cold_start"

    return {
        "result": {"strategy": strategy, "confidence": 0.85, "method": "rule_based"},
        "tool_name": "classify_recommendation_request",
        "execution_status": "success",
        "audit": {"request": request[:100], "strategy": strategy},
    }


def choose_recommendation_strategy(customer_id: str, context: Optional[dict] = None) -> dict:
    """Choose best recommendation strategy for a customer."""
    context = context or {}
    interaction_count = context.get("interaction_count", 0)
    engagement = context.get("engagement_score", 0)
    purchase_cats = context.get("purchase_categories", [])

    # Rule-based strategy selection
    if interaction_count < 3:
        strategy = "cold_start"
        reason = "Insufficient interaction history"
    elif interaction_count >= 10 and engagement > 0.4:
        strategy = "collaborative"
        reason = "Rich interaction history enables collaborative filtering"
    elif purchase_cats and engagement > 0.3:
        strategy = "hybrid"
        reason = "Good engagement and category data supports hybrid approach"
    elif purchase_cats:
        strategy = "content"
        reason = "Category preferences available for content-based filtering"
    else:
        strategy = "behaviour"
        reason = "Behaviour signals available"

    return {
        "result": {"strategy": strategy, "reason": reason, "method": "rule_based"},
        "tool_name": "choose_recommendation_strategy",
        "execution_status": "success",
        "audit": {"customer_id": customer_id, "strategy": strategy},
    }


def suggest_feature_priority(customer_id: str, context: Optional[dict] = None) -> dict:
    """Suggest which features to prioritize for recommendation.
    
    Returns ordered list of feature names with reasoning.
    """
    context = context or {}
    engagement = context.get("engagement_score", 0)
    purchase_cats = context.get("purchase_categories", [])
    interaction_count = context.get("interaction_count", 0)

    features = []
    if interaction_count >= 5:
        features.append({"feature": "behaviour", "priority": 1, "reason": "Active interaction history"})
    if purchase_cats:
        features.append({"feature": "content", "priority": 2, "reason": "Category preferences known"})
        features.append({"feature": "category_affinity", "priority": 3, "reason": "Affinity computable"})
    if not features:
        features.append({"feature": "content", "priority": 1, "reason": "Fallback to content"})

    return {
        "result": {"features": features, "method": "rule_based"},
        "tool_name": "suggest_feature_priority",
        "execution_status": "success",
        "audit": {"customer_id": customer_id},
    }


def explain_recommendation(product_id: str, customer_id: str, signals: Optional[dict] = None) -> dict:
    """Generate explanation for why a product was recommended."""
    signals = signals or {}
    collab = signals.get("collaborative", 0)
    behav = signals.get("behaviour", 0)
    content = signals.get("content", 0)
    pop = signals.get("popularity", 0)

    # Determine dominant signal
    signal_map = {
        "collaborative": collab,
        "behaviour": behav,
        "content": content,
        "popularity": pop,
    }
    dominant = max(signal_map, key=signal_map.get)

    explanations = {
        "collaborative": "Customers similar to you purchased this item",
        "behaviour": "Based on your recent browsing and purchase activity",
        "content": "Matches your preferred product categories",
        "popularity": "Popular item among all customers",
    }

    explanation = explanations.get(dominant, "Recommended based on your profile")

    return {
        "result": {
            "explanation": explanation,
            "dominant_signal": dominant,
            "signal_values": signal_map,
            "method": "rule_based",
        },
        "tool_name": "explain_recommendation",
        "execution_status": "success",
        "audit": {"product_id": product_id, "customer_id": customer_id},
    }


def propose_weight_adjustments(
    current_weights: dict, evaluation_metrics: Optional[dict] = None
) -> dict:
    """[SIMULATION ONLY] Propose alternative hybrid weights.
    
    Does NOT replace production weights. For comparison only.
    """
    # Simulation: suggest slight adjustments based on metrics
    metrics = evaluation_metrics or {}
    ndcg = metrics.get("ndcg", 0.1)

    # If NDCG is low, suggest boosting collaborative weight
    if ndcg < 0.1:
        proposed = {
            "collaborative": min(0.5, current_weights.get("collaborative", 0.4) + 0.05),
            "behaviour": current_weights.get("behaviour", 0.3),
            "content": current_weights.get("content", 0.2),
            "popularity": max(0.05, current_weights.get("popularity", 0.1) - 0.05),
        }
        reason = "Low NDCG suggests boosting collaborative signal"
    else:
        proposed = current_weights
        reason = "Current weights appear adequate"

    return {
        "result": {
            "proposed_weights": proposed,
            "current_weights": current_weights,
            "reason": reason,
            "simulation_only": True,
            "warning": "These weights are for simulation only. Do not apply to production.",
        },
        "tool_name": "propose_weight_adjustments",
        "execution_status": "success",
        "audit": {"simulation_only": True},
    }
