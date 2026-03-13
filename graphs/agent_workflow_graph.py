"""Agentic Workflow Graph - LangGraph execution for agentic AI."""

from __future__ import annotations
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage

from agentic.agentic_state import AgenticState
from agentic.orchestrator_agent import orchestrator_agent, route_to_agent
from agentic.knowledge_agent import knowledge_agent
from agentic.analytics_agent import analytics_agent
from agentic.recommendation_agent import recommendation_agent
from agentic.other_agents import (
    workflow_agent,
    action_agent,
    evaluation_agent,
    memory_agent,
)


def human_approval_node(state: AgenticState) -> dict:
    """Human approval node for low confidence requests."""
    from nonagentic.tools.approval import request_human_approval

    approval = request_human_approval(
        workflow_id=state["request_id"],
        action_description=f"Approve request: {state['original_request'][:100]}",
        risk_level="medium",
    )

    if approval["approved"]:
        return {
            "confidence": 0.9,
            "audit_trail": [{"agent": "human_approval", "action": "approved"}],
        }

    return {
        "error": "Request rejected by human approver",
        "audit_trail": [{"agent": "human_approval", "action": "rejected"}],
    }


def error_handler_node(state: AgenticState) -> dict:
    """Error handler node."""
    error_msg = state.get("error", "Unknown error occurred")

    return {
        "active_agent": "error_handler",
        "final_result": {"error": error_msg},
        "messages": [AIMessage(content=f"❌ Error: {error_msg}")],
        "audit_trail": [{"agent": "error_handler", "error": error_msg}],
    }


def after_approval_route(state: AgenticState) -> str:
    """Route after human approval."""
    if state.get("error"):
        return "error_handler"
    return route_to_agent(state)


def should_evaluate(state: AgenticState) -> str:
    """Determine if evaluation is needed."""
    # Evaluate for workflow and action agents
    if state.get("active_agent") in ["workflow", "action"]:
        return "evaluation_agent"
    return END


def build_agentic_graph(checkpointer=None) -> object:
    """Build the agentic workflow graph."""
    builder = StateGraph(AgenticState)

    # Add nodes
    builder.add_node("orchestrator", orchestrator_agent)
    builder.add_node("knowledge_agent", knowledge_agent)
    builder.add_node("analytics_agent", analytics_agent)
    builder.add_node("recommendation_agent", recommendation_agent)
    builder.add_node("workflow_agent", workflow_agent)
    builder.add_node("action_agent", action_agent)
    builder.add_node("evaluation_agent", evaluation_agent)
    builder.add_node("memory_agent", memory_agent)
    builder.add_node("human_approval", human_approval_node)
    builder.add_node("error_handler", error_handler_node)

    # Set entry point
    builder.set_entry_point("orchestrator")

    # Orchestrator routing
    builder.add_conditional_edges(
        "orchestrator",
        route_to_agent,
        {
            "knowledge_agent": "knowledge_agent",
            "analytics_agent": "analytics_agent",
            "recommendation_agent": "recommendation_agent",
            "workflow_agent": "workflow_agent",
            "action_agent": "action_agent",
            "human_approval": "human_approval",
            "error_handler": "error_handler",
        },
    )

    # Human approval routing
    builder.add_conditional_edges(
        "human_approval",
        after_approval_route,
        {
            "knowledge_agent": "knowledge_agent",
            "analytics_agent": "analytics_agent",
            "recommendation_agent": "recommendation_agent",
            "workflow_agent": "workflow_agent",
            "action_agent": "action_agent",
            "error_handler": "error_handler",
        },
    )

    # Agent to evaluation or END
    builder.add_conditional_edges(
        "knowledge_agent",
        should_evaluate,
        {"evaluation_agent": "evaluation_agent", END: END},
    )
    builder.add_conditional_edges(
        "analytics_agent",
        should_evaluate,
        {"evaluation_agent": "evaluation_agent", END: END},
    )
    builder.add_conditional_edges(
        "recommendation_agent",
        should_evaluate,
        {"evaluation_agent": "evaluation_agent", END: END},
    )
    builder.add_conditional_edges(
        "workflow_agent",
        should_evaluate,
        {"evaluation_agent": "evaluation_agent", END: END},
    )
    builder.add_conditional_edges(
        "action_agent",
        should_evaluate,
        {"evaluation_agent": "evaluation_agent", END: END},
    )

    # Evaluation and error handler to END
    builder.add_edge("evaluation_agent", END)
    builder.add_edge("error_handler", END)

    # Compile graph
    cp = checkpointer or MemorySaver()
    return builder.compile(checkpointer=cp)


# Module-level graph instance
agentic_graph = build_agentic_graph()
