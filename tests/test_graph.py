import pytest
from src.core.state import new_state
from src.graph import build_graph


@pytest.fixture(scope="module")
def g():
    return build_graph()


def _invoke(g, request: str, customer_id: str | None = None) -> dict:
    state = new_state(request)
    if customer_id:
        state["customer_id"] = customer_id
    config = {"configurable": {"thread_id": state["request_id"]}}
    final = g.invoke(state, config=config)
    return final


# ── Level 1 ───────────────────────────────────────────────────────────────────

def test_e2e_kyc_lookup_routes_to_level1(g):
    result = _invoke(g, "What is the identity verification status of CUST-001?", customer_id="CUST-001")
    assert result["routed_to"] == "level1_knowledge"
    assert result["result"] is not None
    assert "identity_status" in result["result"] or "customer" in result["result"]


def test_e2e_profile_lookup(g):
    result = _invoke(g, "Show me the profile for customer CUST-002", customer_id="CUST-002")
    assert result["routed_to"] == "level1_knowledge"
    assert result["result"]["customer"] is not None


# ── Level 2 ───────────────────────────────────────────────────────────────────

def test_e2e_segmentation_routes_to_level2(g):
    result = _invoke(g, "Segment customers by risk score")
    assert result["routed_to"] == "level2_analytics"
    assert "segments" in result["result"]


def test_e2e_analytics_result_has_review_warning(g):
    result = _invoke(g, "Segment customers by risk score")
    last_msg = result["messages"][-1].content
    assert "review" in last_msg.lower() or "⚠️" in last_msg


# ── Level 3 ───────────────────────────────────────────────────────────────────

def test_e2e_upsell_offer_routes_to_level3(g):
    result = _invoke(g, "Send an upsell offer to CUST-005", customer_id="CUST-005")
    assert result["routed_to"] == "level3_functional"


def test_e2e_level3_blocks_expired_kyc(g, monkeypatch):
    """Force a customer to have unverified identity and verify case is created."""
    from src.tools import customer as cmod
    unverified_customer = {
        "customer_id": "CUST-EXP",
        "identity_status": "unverified",
        "identity_expiry_date": "2024-01-01",
        "consent_flags": {"marketing": True, "email": True, "sms": True, "data_sharing": True},
        "promotion_eligibility": [],
        "segment": "at_risk",
        "return_risk": 0.3,
    }
    monkeypatch.setattr(cmod, "_find", lambda *a, **kw: unverified_customer)

    state = new_state("Send an upsell offer to CUST-EXP")
    state["customer_id"] = "CUST-EXP"
    config = {"configurable": {"thread_id": state["request_id"]}}
    final = build_graph().invoke(state, config=config)

    assert final["result"].get("kyc_blocked") is True
    assert "case" in final["result"]


def test_e2e_level3_no_customer_id_returns_error(g):
    result = _invoke(g, "Send a payment reminder")
    # No customer_id → level3 returns error
    assert result.get("error") or "error" in result.get("result", {})


# ── Level 4 ───────────────────────────────────────────────────────────────────

def test_e2e_strategic_goal_routes_to_level4(g):
    result = _invoke(g, "Increase Visa Gold card adoption by 5% this quarter")
    assert result["routed_to"] == "level4_strategic"
    assert "campaign" in result["result"]


def test_e2e_level4_produces_sub_goals(g):
    result = _invoke(g, "Grow portfolio value by 10% this year")
    assert "sub_goals" in result["result"]
    assert len(result["result"]["sub_goals"]) >= 2


# ── Audit trail ───────────────────────────────────────────────────────────────

def test_e2e_audit_trail_populated(g):
    result = _invoke(g, "What is the KYC status of CUST-001?", customer_id="CUST-001")
    assert len(result["audit_trail"]) > 0


def test_e2e_tool_calls_recorded(g):
    result = _invoke(g, "Segment customers by risk score")
    assert len(result["tool_calls"]) > 0


# ── Error handler ─────────────────────────────────────────────────────────────

def test_e2e_error_handler_on_forced_error(g):
    state = new_state("some request")
    state["error"] = "forced test error"
    state["intent"] = "unknown"
    state["confidence"] = 0.9  # skip human_approval path
    config = {"configurable": {"thread_id": state["request_id"]}}
    final = build_graph().invoke(state, config=config)
    assert final["routed_to"] == "error_handler"
    assert "error" in final["result"]
