import pytest
from nonagentic.core.state import new_state
from nonagentic.orchestration.orchestrator import orchestrator_node, route


def _run(request: str) -> dict:
    state = new_state(request)
    updates = orchestrator_node(state)
    state.update(updates)
    return state


def test_routes_kyc_to_level1():
    state = _run("What is the identity verification status of CUST-001?")
    assert state["intent"] == "informational"
    assert route(state) == "level1_knowledge"


def test_routes_segment_to_level2():
    state = _run("Segment customers by risk score")
    assert state["intent"] == "analytical"
    assert route(state) == "level2_analytics"


def test_routes_send_offer_to_level3():
    state = _run("Send an upsell offer to CUST-005")
    assert state["intent"] == "action"
    assert route(state) == "level3_functional"


def test_routes_campaign_to_level4():
    state = _run("Increase Visa Gold card adoption by 5% this quarter")
    assert state["intent"] == "strategic"
    assert route(state) == "level4_strategic"


def test_low_confidence_routes_to_human_approval():
    state = new_state("xyz abc 123")
    state["intent"] = "unknown"
    state["confidence"] = 0.3
    assert route(state) == "human_approval"


def test_empty_request_returns_error():
    state = new_state("")
    updates = orchestrator_node(state)
    assert updates.get("error") is not None


def test_customer_id_extracted():
    state = _run("Show me the profile for CUST-042")
    assert state.get("customer_id") == "CUST-042"
