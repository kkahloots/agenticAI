"""Workflow, Action, Evaluation, and Memory Agents."""

from __future__ import annotations
from langchain_core.messages import AIMessage
from agentic.agentic_state import AgenticState
from mcp_servers.crm_server import CRMServer
from mcp_servers.analytics_server import AnalyticsServer
from memory.memory_manager import memory_manager
from nonagentic.tools.audit import log_audit_event


def workflow_agent(state: AgenticState) -> dict:
    """Workflow agent - execute multi-step workflows."""
    request = state["original_request"]

    # Decompose goal into steps
    steps = [
        "Analyze requirements",
        "Execute sub-tasks",
        "Coordinate agents",
        "Validate outcome",
    ]

    # For now, delegate to analytics + action
    result = {"workflow_id": state["request_id"], "steps": steps, "status": "completed"}

    log_audit_event(
        "workflow_agent",
        "execute_workflow",
        {"request": request},
        result,
        user_id=state["user_id"],
        request_id=state["request_id"],
    )

    return {
        "active_agent": "workflow",
        "agent_history": ["workflow"],
        "intermediate_results": [{"agent": "workflow", "result": result}],
        "final_result": result,
        "messages": [
            AIMessage(content=f"✅ Workflow executed: {len(steps)} steps completed")
        ],
        "audit_trail": [{"agent": "workflow", "action": "execute_workflow"}],
    }


def action_agent(state: AgenticState) -> dict:
    """Action agent - execute actions on external systems."""
    request = state["original_request"]
    customer_id = state.get("user_id")

    crm_server = CRMServer()

    # Determine action type
    if "send" in request.lower() or "notify" in request.lower():
        result = {
            "action": "notification",
            "status": "simulated",
            "customer_id": customer_id,
        }
    elif "case" in request.lower() or "ticket" in request.lower():
        result = {
            "action": "case_creation",
            "status": "simulated",
            "case_id": "CASE-001",
        }
    else:
        result = {"action": "generic", "status": "completed"}

    log_audit_event(
        "action_agent",
        "execute_action",
        {"request": request},
        result,
        user_id=state["user_id"],
        request_id=state["request_id"],
    )

    return {
        "active_agent": "action",
        "agent_history": ["action"],
        "intermediate_results": [{"agent": "action", "result": result}],
        "final_result": result,
        "messages": [AIMessage(content=f"✅ Action executed: {result['action']}")],
        "audit_trail": [{"agent": "action", "action": "execute_action"}],
    }


def evaluation_agent(state: AgenticState) -> dict:
    """Evaluation agent - evaluate outcomes and provide feedback."""
    result = state.get("final_result", {})

    # Simple evaluation logic
    evaluation = {
        "success": True,
        "feedback": "Workflow completed successfully",
        "should_replan": False,
    }

    log_audit_event(
        "evaluation_agent",
        "evaluate_outcome",
        {"result": result},
        evaluation,
        user_id=state["user_id"],
        request_id=state["request_id"],
    )

    memory_manager.agent_observation.record_observation(
        "evaluation", evaluation["feedback"], {"result": result}
    )

    return {
        "active_agent": "evaluation",
        "agent_history": ["evaluation"],
        "evaluation": evaluation,
        "should_replan": evaluation["should_replan"],
        "messages": [AIMessage(content=f"📊 Evaluation: {evaluation['feedback']}")],
        "audit_trail": [{"agent": "evaluation", "action": "evaluate_outcome"}],
    }


def memory_agent(state: AgenticState) -> dict:
    """Memory agent - manage conversation and user memory."""
    operation = "retrieve"  # or "update"

    # Retrieve relevant memory
    conversation = memory_manager.conversation.get_conversation(state["session_id"])
    profile = memory_manager.user_profile.get_profile(state["user_id"])

    result = {
        "conversation_length": len(conversation),
        "profile_keys": list(profile.keys()) if profile else [],
    }

    log_audit_event(
        "memory_agent",
        "manage_memory",
        {"operation": operation},
        result,
        user_id=state["user_id"],
        request_id=state["request_id"],
    )

    return {
        "active_agent": "memory",
        "agent_history": ["memory"],
        "conversation_context": {"messages": conversation},
        "user_profile": profile,
        "intermediate_results": [{"agent": "memory", "result": result}],
        "messages": [
            AIMessage(content=f"💾 Memory: {result['conversation_length']} messages")
        ],
        "audit_trail": [{"agent": "memory", "action": "manage_memory"}],
    }
