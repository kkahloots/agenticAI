"""Orchestrator Agent - routes requests and coordinates agent collaboration."""

from __future__ import annotations
import json
import re
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from agentic.agentic_state import AgenticState
from memory.memory_manager import memory_manager
from nonagentic.core.llm import get_llm
from nonagentic.tools.audit import log_audit_event


_INTENT_SYSTEM = """You are an intent classifier for an agentic AI system.
Classify the user request into one of these intents:
- knowledge: factual lookup, information retrieval
- analytics: data analysis, segmentation, SQL queries, insights, metrics
- recommendation: personalized suggestions, next best action
- workflow: multi-step processes, complex goals
- action: execute operations, send notifications

Respond with JSON: {"intent": "<intent>", "confidence": <0.0-1.0>, "reasoning": "<brief explanation>"}"""


def _pre_classify(request: str) -> tuple[str, float] | None:
    """Fast pre-classification for unambiguous patterns before LLM call."""
    r = request.lower()
    # SQL queries always analytics — check before LLM to avoid misclassification
    if re.search(r"\bselect\b", r) and re.search(r"\bfrom\b", r):
        return "analytics", 0.95
    if "run this sql" in r or "execute this sql" in r or "sql query:" in r:
        return "analytics", 0.95
    if any(w in r for w in ["segment customers", "cluster customers", "segmentation"]):
        return "analytics", 0.95
    return None


def classify_intent(request: str) -> tuple[str, float, str]:
    """Classify user intent using LLM."""
    # Pre-classify unambiguous patterns first
    pre = _pre_classify(request)
    if pre:
        return pre[0], pre[1], "Pre-classified by pattern match"

    try:
        llm = get_llm(temperature=0.0)
        resp = llm.invoke(
            [SystemMessage(content=_INTENT_SYSTEM), HumanMessage(content=request)]
        )
        raw = re.sub(r"```(?:json)?", "", resp.content.strip()).strip().strip("```")
        data = json.loads(raw)
        return data["intent"], float(data["confidence"]), data.get("reasoning", "")
    except Exception:
        return _rule_based_classify(request)


def _rule_based_classify(request: str) -> tuple[str, float, str]:
    """Fallback rule-based classification."""
    r = request.lower()
    if any(w in r for w in ["recommend", "suggest", "next best", "similar"]):
        return "recommendation", 0.85, "Contains recommendation keywords"
    if any(w in r for w in ["campaign", "workflow", "orchestrate", "multi-step"]):
        return "workflow", 0.85, "Contains workflow keywords"
    if any(w in r for w in ["segment", "analyze", "sql", "kpi", "select", "query"]):
        return "analytics", 0.85, "Contains analytics keywords"
    if any(w in r for w in ["send", "notify", "create case", "execute"]):
        return "action", 0.85, "Contains action keywords"
    if any(w in r for w in ["what", "show", "retrieve", "find", "status"]):
        return "knowledge", 0.85, "Contains knowledge keywords"
    return "unknown", 0.4, "No clear intent detected"


def build_agent_plan(intent: str, request: str, state: AgenticState) -> dict:
    """Build execution plan based on intent."""
    plans = {
        "knowledge": {
            "agents": ["knowledge"],
            "steps": ["Retrieve information", "Synthesize answer"],
            "mcp_servers": ["customer_data", "product_catalog"],
        },
        "analytics": {
            "agents": ["analytics"],
            "steps": ["Analyze data", "Generate insights"],
            "mcp_servers": ["analytics"],
        },
        "recommendation": {
            "agents": ["recommendation"],
            "steps": ["Load user profile", "Generate recommendations", "Rank results"],
            "mcp_servers": ["recommendation", "customer_data"],
        },
        "workflow": {
            "agents": ["workflow", "analytics", "action", "evaluation"],
            "steps": [
                "Decompose goal",
                "Execute sub-tasks",
                "Coordinate agents",
                "Evaluate outcome",
            ],
            "mcp_servers": ["crm", "analytics", "customer_data"],
        },
        "action": {
            "agents": ["action"],
            "steps": ["Validate preconditions", "Execute action", "Record outcome"],
            "mcp_servers": ["crm", "customer_data"],
        },
    }
    return plans.get(
        intent,
        {"agents": ["knowledge"], "steps": ["Handle request"], "mcp_servers": []},
    )


def orchestrator_agent(state: AgenticState) -> dict:
    """Orchestrator agent - main entry point for agentic system."""
    request = state["original_request"]
    user_id = state["user_id"]
    session_id = state["session_id"]

    # Load memory context
    conversation = memory_manager.conversation.get_conversation(session_id)
    user_profile = memory_manager.user_profile.get_profile(user_id)

    # Classify intent
    intent, confidence, reasoning = classify_intent(request)

    # Build execution plan
    plan = build_agent_plan(intent, request, state)

    # Select first agent to execute
    next_agent = plan["agents"][0] if plan["agents"] else "knowledge"

    # Log audit
    log_audit_event(
        "orchestrator_agent",
        "classify_and_plan",
        {"request": request, "intent": intent, "confidence": confidence},
        {"plan": plan, "next_agent": next_agent},
        user_id=user_id,
        request_id=state["request_id"],
    )

    # Record to memory
    memory_manager.conversation.add_message(session_id, "user", request)
    memory_manager.agent_observation.record_observation(
        "orchestrator",
        f"Classified intent as {intent} with confidence {confidence}",
        {"request": request, "reasoning": reasoning},
    )

    return {
        "intent": intent,
        "confidence": confidence,
        "active_agent": next_agent,
        "agent_plan": plan,
        "agent_history": ["orchestrator"],
        "conversation_context": {"messages": conversation},
        "user_profile": user_profile,
        "audit_trail": [
            {
                "agent": "orchestrator",
                "action": "classify_and_plan",
                "intent": intent,
                "confidence": confidence,
                "next_agent": next_agent,
            }
        ],
    }


def route_to_agent(state: AgenticState) -> str:
    """Route to next agent based on intent and plan."""
    if state.get("error"):
        return "error_handler"

    if state["confidence"] < 0.6:
        return "human_approval"

    intent_to_agent = {
        "knowledge": "knowledge_agent",
        "analytics": "analytics_agent",
        "recommendation": "recommendation_agent",
        "workflow": "workflow_agent",
        "action": "action_agent",
    }

    return intent_to_agent.get(state["intent"], "knowledge_agent")
