from __future__ import annotations

import json
import re

from langchain_core.messages import AIMessage

from src.core.state import AgentState
from src.tools.audit import log_audit_event
from src.orchestration.registry import REGISTRY, describe_all
from src.core.observability import node_trace
from src.core.llm import get_llm

_SYSTEM_PROMPT = """You are an intent classifier for an online store customer operations AI system.
Classify the user request into exactly one of these intents:
- informational: factual lookup, identity verification status, policy retrieval, customer profile
- analytical: segmentation, SQL queries, KPIs, churn analysis, fraud scoring
- action: send promotion, recommend offer, create support case, win-back campaign, upsell
- strategic: campaign orchestration, revenue growth, multi-step business goals
- recommendation: product recommendation, next best offer, similar customers, collaborative filtering, suggest products

Also extract customer_id if present (format CUST-NNN or similar).

Respond with valid JSON only:
{"intent": "<intent>", "confidence": <0.0-1.0>, "customer_id": "<id or null>"}"""


def _classify(request: str) -> tuple[str, float, str | None]:
    try:
        from langchain_core.messages import HumanMessage, SystemMessage
        llm = get_llm(temperature=0.0)
        resp = llm.invoke([
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(content=request),
        ])
        raw = re.sub(r"```(?:json)?", "", resp.content.strip()).strip().strip("```")
        data = json.loads(raw)
        cid = data.get("customer_id")
        if isinstance(cid, str) and cid.lower() in ("null", "none", ""):
            cid = None
        return data["intent"], float(data["confidence"]), cid
    except Exception:
        return _rule_classify(request)


def _rule_classify(request: str) -> tuple[str, float, str | None]:
    """Deterministic fallback — no LLM required."""
    r = request.lower()
    customer_id = None
    match = re.search(r"cust-\d+", r)
    if match:
        customer_id = match.group(0).upper()

    recommendation_words = ["recommend", "suggestion", "next best", "similar customer",
                             "collaborative", "what product", "suggest product", "suggest offer",
                             "cross-user", "personali"]
    if any(w in r for w in recommendation_words):
        return "recommendation", 0.85, customer_id
    strategic_words = ["campaign", "grow", "increase adoption", "portfolio", "orchestrat",
                       "adoption", "reduce churn", "improve nps", "increase", "quarter",
                       "this month", "this year", "revenue", "retention", "sales"]
    if any(w in r for w in strategic_words):
        return "strategic", 0.85, customer_id
    if any(w in r for w in ["send", "offer", "upsell", "remind", "case", "ticket", "notify", "promo", "promotion", "winback", "win-back"]):
        return "action", 0.85, customer_id
    if any(w in r for w in ["segment", "sql", "query", "kpi", "churn", "analys", "cluster", "fraud"]):
        return "analytical", 0.85, customer_id
    if any(w in r for w in ["identity", "verification", "policy", "profile", "status", "what is", "show me", "retrieve"]):
        return "informational", 0.85, customer_id
    return "unknown", 0.4, customer_id


@node_trace("orchestrator")
def orchestrator_node(state: AgentState) -> dict:
    if not state.get("original_request", "").strip():
        return {
            "intent": "unknown",
            "confidence": 0.0,
            "error": "Empty request",
            "messages": [AIMessage(content="Please provide a request.")],
            "audit_trail": [{"node": "orchestrator", "action": "empty_request"}],
        }

    intent, confidence, customer_id = _classify(state["original_request"])

    log_audit_event(
        "orchestrator", "classify_intent",
        {"request": state["original_request"]},
        {"intent": intent, "confidence": confidence, "customer_id": customer_id},
        user_id=state["user_id"],
        request_id=state["request_id"],
    )

    updates: dict = {
        "intent": intent,
        "confidence": confidence,
        "audit_trail": [{"node": "orchestrator", "intent": intent, "confidence": round(confidence, 3)}],
    }
    if customer_id:
        updates["customer_id"] = customer_id
    return updates


def route(state: AgentState) -> str:
    if state.get("error"):
        return "error_handler"
    if state["confidence"] < 0.6:
        return "human_approval"
    mapping = {
        "informational":  "level1_knowledge",
        "analytical":     "level2_analytics",
        "action":         "level3_functional",
        "strategic":      "level4_strategic",
        "recommendation": "level5_recommendation",
    }
    return mapping.get(state["intent"], "human_approval")
