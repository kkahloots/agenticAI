from __future__ import annotations

from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from src.core.state import AgentState
from src.orchestration.orchestrator import orchestrator_node, route
from src.agents.level1 import level1_node
from src.agents.level2 import level2_node
from src.agents.level3 import level3_node
from src.agents.level4 import level4_node
from src.agents.level5 import level5_node
from src.tools.audit import log_audit_event


def human_approval_node(state: AgentState) -> dict:
    """
    In production this node is interrupted and awaits an external callback.
    In dev/test the approval tool handles it inline.
    """
    from src.tools.approval import request_human_approval

    approval = request_human_approval(
        workflow_id=state["request_id"],
        action_description=f"Clarify or approve: {state['original_request'][:120]}",
        risk_level="medium",
    )
    log_audit_event(
        "human_approval", "request_human_approval",
        {"request": state["original_request"]},
        approval,
        user_id=state["user_id"],
        request_id=state["request_id"],
    )
    if approval["approved"]:
        # Re-route with boosted confidence so we don't loop
        return {
            "approval_status": "approved",
            "confidence": 0.9,
            "audit_trail": [{"node": "human_approval", "action": "approved"}],
        }
    return {
        "approval_status": "rejected",
        "error": "Request rejected or could not be clarified.",
        "audit_trail": [{"node": "human_approval", "action": "rejected"}],
    }


def after_approval_route(state: AgentState) -> str:
    if state.get("approval_status") == "rejected" or state.get("error"):
        return "error_handler"
    # Re-classify intent if still unknown so we don't loop back to human_approval
    intent = state.get("intent", "unknown")
    if intent == "unknown":
        from src.orchestration.orchestrator import _rule_classify
        intent, _, _ = _rule_classify(state["original_request"])
    mapping = {
        "informational":  "level1_knowledge",
        "analytical":     "level2_analytics",
        "action":         "level3_functional",
        "strategic":      "level4_strategic",
        "recommendation": "level5_recommendation",
    }
    return mapping.get(intent, "error_handler")


def error_handler_node(state: AgentState) -> dict:
    msg = state.get("error", "An unexpected error occurred.")
    log_audit_event(
        "error_handler", "handle_error",
        {"request": state["original_request"]},
        {"error": msg},
        user_id=state["user_id"],
        request_id=state["request_id"],
    )
    return {
        "routed_to": "error_handler",
        "result": {"error": msg},
        "messages": [AIMessage(content=f"❌ {msg}")],
        "audit_trail": [{"node": "error_handler", "error": msg}],
    }


def build_graph(checkpointer=None) -> object:
    builder = StateGraph(AgentState)

    builder.add_node("orchestrator",      orchestrator_node)
    builder.add_node("level1_knowledge",  level1_node)
    builder.add_node("level2_analytics",  level2_node)
    builder.add_node("level3_functional", level3_node)
    builder.add_node("level4_strategic",  level4_node)
    builder.add_node("level5_recommendation", level5_node)
    builder.add_node("human_approval",    human_approval_node)
    builder.add_node("error_handler",     error_handler_node)

    builder.set_entry_point("orchestrator")

    builder.add_conditional_edges("orchestrator", route, {
        "level1_knowledge":     "level1_knowledge",
        "level2_analytics":     "level2_analytics",
        "level3_functional":    "level3_functional",
        "level4_strategic":     "level4_strategic",
        "level5_recommendation": "level5_recommendation",
        "human_approval":       "human_approval",
        "error_handler":        "error_handler",
    })

    builder.add_conditional_edges("human_approval", after_approval_route, {
        "level1_knowledge":     "level1_knowledge",
        "level2_analytics":     "level2_analytics",
        "level3_functional":    "level3_functional",
        "level4_strategic":     "level4_strategic",
        "level5_recommendation": "level5_recommendation",
        "error_handler":        "error_handler",
    })

    for node in ("level1_knowledge", "level2_analytics", "level3_functional",
                 "level4_strategic", "level5_recommendation", "error_handler"):
        builder.add_edge(node, END)

    cp = checkpointer or MemorySaver()
    return builder.compile(checkpointer=cp)


# Module-level default graph instance
graph = build_graph()
