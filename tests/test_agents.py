import pytest
from unittest.mock import patch, MagicMock
from src.agents.level1 import level1_node, _format
from src.agents.level3 import level3_node, _extract_offer, _extract_segment
from src.core.state import new_state


# ── Level 1 Tests ──

def test_level1_identity_status_query():
    state = new_state("What is the identity verification status?")
    state["customer_id"] = "CUST-001"
    result = level1_node(state)
    assert result["routed_to"] == "level1_knowledge"
    assert "identity_status" in result["result"] or "kyc_status" in result["result"]


def test_level1_email_search():
    with patch("src.agents.level1.multi_query_search") as mock_search:
        mock_search.return_value = {"chunks": [{"text": "test email", "source": "email.txt", "doc_type": "email", "score": 0.1}]}
        state = new_state("Show me emails about refunds")
        result = level1_node(state)
        assert result["routed_to"] == "level1_knowledge"
        mock_search.assert_called_once()


def test_level1_notes_search():
    with patch("src.agents.level1.multi_query_search") as mock_search:
        mock_search.return_value = {"chunks": []}
        state = new_state("Show me support notes")
        result = level1_node(state)
        assert result["routed_to"] == "level1_knowledge"


def test_level1_profile_lookup():
    state = new_state("Show me the profile")
    state["customer_id"] = "CUST-001"
    result = level1_node(state)
    assert result["routed_to"] == "level1_knowledge"
    assert "customer" in result["result"]


def test_level1_policy_search():
    with patch("src.agents.level1.multi_query_search") as mock_search:
        mock_search.return_value = {"chunks": []}
        state = new_state("What is the fraud policy?")
        result = level1_node(state)
        assert result["routed_to"] == "level1_knowledge"


def test_level1_format_error():
    result = _format({"error": "not found"})
    assert "not found" in result


def test_level1_format_identity():
    result = _format({"identity_status": "verified", "identity_expiry_date": "2025-12-31", "days_until_expiry": 365})
    assert "verified" in result
    assert "2025-12-31" in result


def test_level1_format_customer():
    result = _format({"customer": {"customer_id": "CUST-001", "segment": "vip", "identity_status": "verified", "fraud_score": 0.1, "engagement_score": 0.9}})
    assert "CUST-001" in result
    assert "vip" in result


# ── Level 3 Tests ──

def test_level3_lead_scoring():
    with patch("src.agents.level3.score_leads") as mock_score:
        mock_score.return_value = {"total_eligible": 10, "leads": []}
        state = new_state("Score leads for premium offer")
        result = level3_node(state)
        assert result["routed_to"] == "level3_functional"
        assert "total_eligible" in result["result"]


def test_level3_bulk_campaign():
    with patch("src.agents.level3.bulk_recommend") as mock_bulk:
        mock_bulk.return_value = {"to_send": 50, "blocked": 5, "bulk_approval_needed": False, "bulk_threshold": 100}
        state = new_state("Run bulk campaign for loyalty offer")
        result = level3_node(state)
        assert result["routed_to"] == "level3_functional"


def test_level3_missing_customer_id():
    state = new_state("Send an offer")
    result = level3_node(state)
    assert "error" in result


def test_level3_enrichment():
    state = new_state("Enrich customer data")
    state["customer_id"] = "CUST-001"
    with patch("src.agents.level3.enrich_customer") as mock_enrich:
        mock_enrich.return_value = {"enrichment": {"data_sources": ["bureau", "social"]}}
        result = level3_node(state)
        assert result["routed_to"] == "level3_functional"


def test_level3_kyc_blocked():
    state = new_state("Send upsell offer")
    state["customer_id"] = "CUST-001"
    with patch("src.agents.level3.get_kyc_status") as mock_kyc:
        mock_kyc.return_value = {"kyc_status": "expired", "identity_status": "unverified"}
        result = level3_node(state)
        assert result["result"].get("kyc_blocked") is True


def test_level3_upsell_offer():
    state = new_state("Send upsell offer")
    state["customer_id"] = "CUST-001"
    with patch("src.agents.level3.get_kyc_status") as mock_kyc, \
         patch("src.agents.level3.recommend_offer") as mock_offer, \
         patch("src.agents.level3.draft_email") as mock_draft, \
         patch("src.agents.level3.send_notification") as mock_send:
        mock_kyc.return_value = {"kyc_status": "verified", "identity_status": "verified"}
        mock_offer.return_value = {"offer_code": "PROMO-01", "offer_name": "Premium", "confidence": 0.8}
        mock_draft.return_value = {"subject": "Special offer", "body": "Hi there"}
        mock_send.return_value = {"status": "sent"}
        result = level3_node(state)
        assert result["routed_to"] == "level3_functional"
        assert "offer" in result["result"]


def test_level3_case_creation():
    state = new_state("Create a case for complaint")
    state["customer_id"] = "CUST-001"
    with patch("src.agents.level3.get_kyc_status") as mock_kyc, \
         patch("src.agents.level3.create_case") as mock_case:
        mock_kyc.return_value = {"kyc_status": "verified"}
        mock_case.return_value = {"case_id": "CASE-001", "status": "open"}
        result = level3_node(state)
        assert "case" in result["result"]


def test_extract_offer():
    assert _extract_offer("send premium offer") == "PROMO-PREMIUM-MEMBERSHIP"
    assert _extract_offer("loyalty points") == "PROMO-LOYALTY-POINTS"
    assert _extract_offer("winback campaign") == "PROMO-WINBACK"


def test_extract_segment():
    assert _extract_segment("target vip customers") == "vip"
    assert _extract_segment("at-risk segment") == "at_risk"
    assert _extract_segment("dormant vip") == "dormant_vip"
    assert _extract_segment("random text") is None
