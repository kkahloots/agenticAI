from __future__ import annotations

from langchain_core.messages import AIMessage

from nonagentic.core.state import AgentState
from nonagentic.core.config import load_config
from nonagentic.tools.customer import search_customer_profile, get_kyc_status
from nonagentic.tools.functional import (
    recommend_offer,
    draft_email,
    send_notification,
    create_case,
)
from nonagentic.tools.leads import score_leads, enrich_customer, bulk_recommend
from nonagentic.tools.approval import request_human_approval
from nonagentic.tools.audit import log_audit_event
from nonagentic.core.observability import node_trace


@node_trace("level3_functional")
def level3_node(state: AgentState) -> dict:
    cfg = load_config()
    request = state["original_request"].lower()
    customer_id = state.get("customer_id")
    steps: list[str] = []
    result: dict = {}

    # ── Lead scoring / prospect identification (no customer_id needed) ──
    if any(w in request for w in ["lead", "prospect", "score lead", "identify"]):
        offer_code = _extract_offer(request)
        segment = _extract_segment(request)
        leads = score_leads(offer_code, top_n=20, segment=segment)
        log_audit_event(
            "level3_functional",
            "score_leads",
            {"offer_code": offer_code, "segment": segment},
            leads,
            user_id=state["user_id"],
            request_id=state["request_id"],
        )
        steps.append(f"Scored {leads['total_eligible']} prospects for {offer_code}")
        return _done(state, steps, leads)

    # ── Bulk campaign targeting (no customer_id needed) ──
    if any(
        w in request for w in ["bulk", "campaign", "all customers", "segment target"]
    ):
        offer_code = _extract_offer(request)
        segment = _extract_segment(request)
        plan = bulk_recommend(offer_code, segment=segment)
        log_audit_event(
            "level3_functional",
            "bulk_recommend",
            {"offer_code": offer_code, "segment": segment},
            plan,
            user_id=state["user_id"],
            request_id=state["request_id"],
        )
        steps.append(f"Bulk plan: {plan['to_send']} to send, {plan['blocked']} blocked")
        if plan["bulk_approval_needed"]:
            steps.append(
                f"⚠️ Bulk approval required (>{plan['bulk_threshold']} recipients)"
            )
        return _done(state, steps, plan)

    # ── All remaining flows require customer_id ──
    if not customer_id:
        return _error(state, "customer_id required for this action")

    # ── Enrichment ──
    if any(w in request for w in ["enrich", "enrichment", "credit score", "bureau"]):
        enriched = enrich_customer(customer_id)
        log_audit_event(
            "level3_functional",
            "enrich_customer",
            {"customer_id": customer_id},
            enriched,
            user_id=state["user_id"],
            request_id=state["request_id"],
        )
        steps.append(
            f"Enriched {customer_id} from {len(enriched.get('enrichment', {}).get('data_sources', []))} sources"
        )
        return _done(state, steps, enriched)

    # ── Identity gate ──
    identity = get_kyc_status(customer_id)
    if (
        identity.get("kyc_status") == "expired"
        or identity.get("identity_status") == "unverified"
    ):
        case = create_case(
            customer_id,
            "identity_reverification",
            "Identity unverified — re-verification required before action",
            priority="high",
        )
        log_audit_event(
            "level3_functional",
            "create_case",
            {"customer_id": customer_id},
            case,
            user_id=state["user_id"],
            request_id=state["request_id"],
        )
        steps.append(
            f"Identity unverified → re-verification case opened: {case['case_id']}"
        )
        result = {"kyc_blocked": True, "case": case}
        return _done(state, steps, result)

    # ── Upsell / promotion / cross-sell / next-best-action ──
    if any(
        w in request
        for w in [
            "offer",
            "upsell",
            "recommend",
            "product",
            "cross-sell",
            "next best",
            "promo",
            "promotion",
        ]
    ):
        offer = recommend_offer(customer_id)
        log_audit_event(
            "level3_functional",
            "recommend_offer",
            {"customer_id": customer_id},
            offer,
            user_id=state["user_id"],
            request_id=state["request_id"],
        )
        steps.append(
            f"NBA promotion: {offer.get('offer_code')} (confidence {offer.get('confidence', 0):.0%})"
        )

        if offer.get("offer_code"):
            draft = draft_email(
                customer_id, "T-PROMO-01", variables={"offer_name": offer["offer_name"]}
            )
            log_audit_event(
                "level3_functional",
                "draft_email",
                {"customer_id": customer_id},
                {},
                user_id=state["user_id"],
                request_id=state["request_id"],
            )
            steps.append("Email drafted")

            send = send_notification(
                customer_id,
                "email",
                {"subject": draft.get("subject"), "body": draft.get("body")},
            )
            log_audit_event(
                "level3_functional",
                "send_notification",
                {"customer_id": customer_id, "channel": "email"},
                send,
                user_id=state["user_id"],
                request_id=state["request_id"],
            )
            steps.append(f"Notification: {send['status']}")
            result = {"offer": offer, "send": send}

    # ── Win-back / churn prevention ──
    elif any(
        w in request
        for w in [
            "payment",
            "reminder",
            "collection",
            "delay",
            "winback",
            "win-back",
            "churn",
        ]
    ):
        c_result = search_customer_profile(customer_id=customer_id)
        c = c_result.get("customer", {}) or {}
        return_risk = c.get("return_risk", 0)

        if return_risk > cfg.payment_delay_threshold:
            approval = request_human_approval(
                workflow_id=state["request_id"],
                action_description=f"Send win-back to {customer_id} (return risk {return_risk:.2f})",
                risk_level="high",
            )
            log_audit_event(
                "level3_functional",
                "request_human_approval",
                {"customer_id": customer_id, "return_risk": return_risk},
                approval,
                user_id=state["user_id"],
                request_id=state["request_id"],
            )
            if not approval["approved"]:
                return _error(
                    state, "Human approval rejected for high-risk win-back action"
                )
            steps.append(f"Approval granted by {approval['approver_id']}")

        send = send_notification(
            customer_id,
            "sms",
            {"body": "We miss you! Here's a special offer to come back."},
        )
        log_audit_event(
            "level3_functional",
            "send_notification",
            {"customer_id": customer_id, "channel": "sms"},
            send,
            user_id=state["user_id"],
            request_id=state["request_id"],
        )
        steps.append(f"SMS win-back: {send['status']}")
        result = {"send": send, "return_risk": return_risk}

    # ── Generic case creation ──
    elif any(w in request for w in ["case", "ticket", "complaint", "issue"]):
        case = create_case(customer_id, "general", state["original_request"])
        log_audit_event(
            "level3_functional",
            "create_case",
            {"customer_id": customer_id},
            case,
            user_id=state["user_id"],
            request_id=state["request_id"],
        )
        steps.append(f"Case created: {case['case_id']}")
        result = {"case": case}

    else:
        result = {"message": "No matching functional action for this request."}

    return _done(state, steps, result)


# ── helpers ───────────────────────────────────────────────────────────────────


def _extract_offer(request: str) -> str:
    offer_map = {
        "premium": "PROMO-PREMIUM-MEMBERSHIP",
        "loyalty": "PROMO-LOYALTY-POINTS",
        "bundle": "PROMO-BUNDLE-DEAL",
        "winback": "PROMO-WINBACK",
        "win-back": "PROMO-WINBACK",
        "win back": "PROMO-WINBACK",
    }
    for kw, code in offer_map.items():
        if kw in request:
            return code
    return "PROMO-PREMIUM-MEMBERSHIP"  # default


def _extract_segment(request: str) -> str | None:
    seg_map = {
        "dormant_vip": "dormant_vip",
        "dormant vip": "dormant_vip",
        "vip": "vip",
        "at_risk": "at_risk",
        "at-risk": "at_risk",
        "at risk": "at_risk",
        "casual": "casual",
        "new": "new",
    }
    for kw, seg in seg_map.items():
        if kw in request:
            return seg
    return None


def _done(state: AgentState, steps: list[str], result: dict) -> dict:
    summary = "\n".join(f"✅ {s}" for s in steps) if steps else str(result)
    return {
        "routed_to": "level3_functional",
        "result": result,
        "messages": [AIMessage(content=summary)],
        "tool_calls": [
            {
                "tool": "level3",
                "inputs": {"request": state["original_request"]},
                "outputs": result,
            }
        ],
        "audit_trail": [
            {"node": "level3_functional", "action": "completed", "steps": steps}
        ],
    }


def _error(state: AgentState, msg: str) -> dict:
    return {
        "routed_to": "level3_functional",
        "error": msg,
        "result": {"error": msg},
        "messages": [AIMessage(content=f"❌ {msg}")],
        "tool_calls": [],
        "audit_trail": [{"node": "level3_functional", "action": "error", "error": msg}],
    }
