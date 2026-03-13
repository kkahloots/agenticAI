"""Recommendation Agent - generates personalized recommendations."""

from __future__ import annotations
from langchain_core.messages import AIMessage
from agentic.agentic_state import AgenticState
from mcp_servers.recommendation_server import RecommendationServer
from mcp_servers.customer_data_server import CustomerDataServer
from memory.memory_manager import memory_manager
from nonagentic.tools.audit import log_audit_event
import re


def recommendation_agent(state: AgenticState) -> dict:
    """Recommendation agent - generate personalized recommendations."""
    request = state["original_request"]
    customer_id = _extract_customer_id(request)

    if not customer_id:
        return {
            "error": "Customer ID required for recommendations",
            "messages": [
                AIMessage(content="❌ Please provide a customer ID for recommendations")
            ],
            "audit_trail": [
                {"agent": "recommendation", "action": "missing_customer_id"}
            ],
        }

    # Initialize MCP servers
    rec_server = RecommendationServer()
    customer_server = CustomerDataServer()

    mcp_calls = []

    # Get customer profile for context
    profile = customer_server.invoke_tool(
        "search_customer_profile", customer_id=customer_id
    )
    mcp_calls.append(
        {
            "server": "customer_data",
            "tool": "search_customer_profile",
            "params": {"customer_id": customer_id},
            "result": profile,
        }
    )

    # Generate recommendations
    top_k = _extract_top_k(request)
    result = rec_server.invoke_tool(
        "recommend_products", customer_id=customer_id, top_k=top_k
    )
    mcp_calls.append(
        {
            "server": "recommendation",
            "tool": "recommend_products",
            "params": {"customer_id": customer_id, "top_k": top_k},
            "result": result,
        }
    )

    # Format answer
    answer = _format_recommendations(result, customer_id)

    # Log audit
    log_audit_event(
        "recommendation_agent",
        "generate_recommendations",
        {"customer_id": customer_id, "top_k": top_k},
        {"count": len(result.get("recommendations", []))},
        user_id=state["user_id"],
        request_id=state["request_id"],
    )

    # Record to memory
    memory_manager.conversation.add_message(state["session_id"], "assistant", answer)
    memory_manager.interaction.record_interaction(
        state["user_id"],
        "recommendation",
        {
            "customer_id": customer_id,
            "recommendations": result.get("recommendations", []),
        },
    )

    return {
        "active_agent": "recommendation",
        "agent_history": ["recommendation"],
        "mcp_calls": mcp_calls,
        "intermediate_results": [{"agent": "recommendation", "result": result}],
        "final_result": result,
        "messages": [AIMessage(content=answer)],
        "audit_trail": [
            {
                "agent": "recommendation",
                "action": "generate_recommendations",
                "customer_id": customer_id,
                "count": len(result.get("recommendations", [])),
            }
        ],
    }


def _extract_customer_id(text: str) -> str | None:
    """Extract customer ID from text."""
    match = re.search(r"CUST-\d+", text, re.IGNORECASE)
    return match.group(0).upper() if match else None


def _extract_top_k(text: str) -> int:
    """Extract top_k from request."""
    match = re.search(r"top[_\s-]?(\d+)", text.lower())
    return int(match.group(1)) if match else 10


def _format_recommendations(result: dict, customer_id: str) -> str:
    """Format recommendations for display."""
    if "error" in result:
        return f"❌ Error generating recommendations: {result['error']}"

    recs = result.get("recommendations", [])
    if not recs:
        return f"No recommendations found for {customer_id}"

    cold_start = result.get("cold_start", False)

    lines = []
    if cold_start:
        lines.append(
            f"🌱 Cold start detected for {customer_id}. Using popularity-based recommendations."
        )
    else:
        lines.append(
            f"✅ Generated {len(recs)} personalized recommendations for {customer_id}"
        )

    lines.append("\nTop recommendations:")
    for i, rec in enumerate(recs[:5], 1):
        score = rec.get("score", 0)
        lines.append(f"  {i}. {rec['product_id']} (score: {score:.3f})")

    return "\n".join(lines)
