from __future__ import annotations

from langchain_core.messages import AIMessage

from nonagentic.core.state import AgentState
from nonagentic.tools.recommender import recommend
from nonagentic.tools.audit import log_audit_event
from nonagentic.core.observability import node_trace


@node_trace("level5_recommendation")
def level5_node(state: AgentState) -> dict:
    request = state["original_request"]
    customer_id = state.get("customer_id")

    # Extract top_k from request if mentioned
    import re
    top_k = 10
    m = re.search(r"top[_\s-]?(\d+)", request.lower())
    if m:
        top_k = int(m.group(1))

    if not customer_id:
        # Try to extract from request
        m2 = re.search(r"cust-\d+", request.lower())
        if m2:
            customer_id = m2.group(0).upper()

    if not customer_id:
        return {
            "routed_to": "level5_recommendation",
            "result": {"error": "No customer_id provided", "recommendations": []},
            "messages": [AIMessage(content="❌ Please provide a customer ID to generate recommendations.")],
            "audit_trail": [{"node": "level5_recommendation", "action": "missing_customer_id"}],
        }

    result = recommend(customer_id=customer_id, top_k=top_k)

    log_audit_event(
        "level5_recommendation", "recommend",
        {"customer_id": customer_id, "top_k": top_k, "request": request},
        {"count": len(result.get("recommendations", [])), "cold_start": result.get("cold_start")},
        user_id=state["user_id"],
        request_id=state["request_id"],
    )

    recs = result.get("recommendations", [])
    cold = result.get("cold_start", False)

    if not recs:
        summary = f"No recommendations found for {customer_id}."
    elif cold:
        summary = (
            f"🌱 Cold start detected for {customer_id}. "
            f"Returning {len(recs)} popular/segment-based recommendations."
        )
    else:
        top3 = ", ".join(r["product_id"] for r in recs[:3])
        similar_count = len(result.get("similar_users", []))
        summary = (
            f"✅ Generated {len(recs)} hybrid recommendations for {customer_id}. "
            f"Top items: {top3}. "
            f"Based on {similar_count} similar users."
        )

    return {
        "routed_to": "level5_recommendation",
        "result": result,
        "messages": [AIMessage(content=summary)],
        "tool_calls": [{"tool": "recommend", "inputs": {"customer_id": customer_id, "top_k": top_k}, "outputs": result}],
        "audit_trail": [{"node": "level5_recommendation", "action": "completed",
                         "customer_id": customer_id, "count": len(recs)}],
    }
