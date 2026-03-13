from __future__ import annotations

import os

from langchain_core.messages import AIMessage

from nonagentic.core.state import AgentState
from nonagentic.tools.customer import search_customer_profile, get_identity_status, get_kyc_status
from nonagentic.tools.knowledge import search_policy_docs, multi_query_search
from nonagentic.tools.audit import log_audit_event
from nonagentic.core.observability import node_trace
from nonagentic.core.guardrails import guardrail_check
from nonagentic.core.llm import get_llm


def _rag_generate(question: str, chunks: list[dict]) -> str:
    """Synthesise a grounded answer from retrieved chunks using the LLM."""
    if not chunks:
        return "No relevant documents found."
    context = "\n\n".join(
        f"[{c.get('doc_type','doc')}] {c['source']}:\n{c['text'][:400]}"
        for c in chunks
    )
    try:
        from langchain_core.messages import HumanMessage, SystemMessage
        llm = get_llm(temperature=0.0)
        resp = llm.invoke([
            SystemMessage(content=(
                "You are a helpful online store assistant. Answer the question using the "
                "provided sources. Cite the source filename in your answer. "
                "Treat escalation notes, support notes, and agent notes as equivalent. "
                "If the sources contain relevant information, summarise it clearly."
            )),
            HumanMessage(content=f"Sources:\n{context}\n\nQuestion: {question}"),
        ])
        return resp.content.strip()
    except Exception:
        lines = [f"[{i+1}] [{c['source']}] {c['text'][:200]}" for i, c in enumerate(chunks)]
        return "**Sources:**\n" + "\n".join(lines)


@node_trace("level1_knowledge")
def level1_node(state: AgentState) -> dict:
    request = state["original_request"].lower()
    customer_id = state.get("customer_id")
    result: dict = {}
    answer: str = ""

    if (any(w in request for w in ["identity", "verification", "verified", "unverified", "kyc", "status"]) 
        and any(w in request for w in ["status", "check", "what", "is", "verify"])
        and customer_id):
        result = get_identity_status(customer_id)
        log_audit_event("level1_knowledge", "get_identity_status", {"customer_id": customer_id}, result,
                        user_id=state["user_id"], request_id=state["request_id"])
        answer = _format(result)

    elif any(w in request for w in ["email", "emails", "message", "correspondence"]):
        result = multi_query_search(query=state["original_request"], doc_type="email")
        log_audit_event("level1_knowledge", "search_emails", {"query": state["original_request"]}, {},
                        user_id=state["user_id"], request_id=state["request_id"])
        answer = _rag_generate(state["original_request"], result.get("chunks", []))

    elif any(w in request for w in ["note", "notes", "support", "agent note", "case comment", "escalation"]):
        result = multi_query_search(query=state["original_request"], doc_type="note")
        log_audit_event("level1_knowledge", "search_notes", {"query": state["original_request"]}, {},
                        user_id=state["user_id"], request_id=state["request_id"])
        answer = _rag_generate(state["original_request"], result.get("chunks", []))

    elif customer_id or any(w in request for w in ["profile", "account", "segment", "engagement"]):
        result = search_customer_profile(customer_id=customer_id)
        log_audit_event("level1_knowledge", "search_customer_profile", {"customer_id": customer_id}, {},
                        user_id=state["user_id"], request_id=state["request_id"])
        answer = _format(result)

    else:
        doc_type = None
        if any(w in request for w in ["identity", "verification", "fraud", "compliance"]):
            doc_type = "policy"
        elif any(w in request for w in ["promotion", "offer", "discount"]):
            doc_type = "policy"
        result = multi_query_search(query=state["original_request"], doc_type=doc_type)
        log_audit_event("level1_knowledge", "multi_query_search", {"query": state["original_request"]}, {},
                        user_id=state["user_id"], request_id=state["request_id"])
        answer = _rag_generate(state["original_request"], result.get("chunks", []))

    gr = guardrail_check(answer, request_id=state["request_id"])
    if not gr.passed:
        log_audit_event("level1_knowledge", "guardrail_violation",
                        {"violations": gr.violations}, {},
                        user_id=state["user_id"], request_id=state["request_id"])
        answer = gr.revised_text

    return {
        "routed_to": "level1_knowledge",
        "result": result,
        "messages": [AIMessage(content=answer)],
        "tool_calls": [{"tool": "level1", "inputs": {"request": state["original_request"]}, "outputs": result}],
        "audit_trail": [{"node": "level1_knowledge", "action": "completed",
                         "guardrail_passed": gr.passed, "violations": gr.violations}],
    }


def _format(result: dict) -> str:
    if "error" in result:
        return f"I could not retrieve that information: {result['error']}"
    if "identity_status" in result:
        return (
            f"Identity status: **{result['identity_status']}** | "
            f"Expiry: {result.get('identity_expiry_date', 'N/A')} | "
            f"Days until expiry: {result.get('days_until_expiry', 'N/A')}"
        )
    # legacy alias support
    if "kyc_status" in result and "identity_status" not in result:
        return (
            f"Identity status: **{result['kyc_status']}** | "
            f"Expiry: {result.get('kyc_expiry_date', 'N/A')} | "
            f"Days until expiry: {result.get('days_until_expiry', 'N/A')}"
        )
    if "customer" in result:
        c = result["customer"]
        if not c:
            return "No customer record found."
        return (
            f"Customer: {c['customer_id']} | Segment: {c.get('segment')} | "
            f"Identity: {c.get('identity_status')} | Fraud score: {c.get('fraud_score')} | "
            f"Engagement: {c.get('engagement_score')}"
        )
    if "chunks" in result:
        chunks = result["chunks"]
        if not chunks:
            return result.get("message", "No documents found.")
        lines = [f"[{i+1}] [{c['source']}] {c['text'][:200]}" for i, c in enumerate(chunks)]
        return "**Sources:**\n" + "\n".join(lines)
    return str(result)
