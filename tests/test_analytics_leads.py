import pytest
from unittest.mock import patch, MagicMock
from nonagentic.tools.analytics import run_sql_query, generate_segment, _is_safe, _avg
from nonagentic.tools.leads import (
    score_leads,
    enrich_customer,
    upsell_recommend,
    user_based_recommend,
    collaborative_recommend,
    bulk_recommend,
    _recency_factor,
    _balance_factor,
)


# ── Analytics Tests ──


def test_is_safe_query():
    assert _is_safe("SELECT * FROM customers") is True
    assert _is_safe("DROP TABLE customers") is False
    assert _is_safe("INSERT INTO customers VALUES (1)") is False
    assert _is_safe("UPDATE customers SET name='x'") is False


def test_run_sql_query_unsafe():
    result = run_sql_query("DELETE FROM customers")
    assert result["error"] == "unsafe_query"


def test_run_sql_query_exception():
    result = run_sql_query("SELECT * FROM nonexistent_table")
    assert "error" in result


def test_generate_segment_rules():
    result = generate_segment(algorithm="rules")
    assert "segments" in result
    assert isinstance(result["segments"], list)


def test_generate_segment_insufficient_data():
    result = generate_segment(filters={"segment": "nonexistent"})
    assert "warning" in result or "segments" in result


def test_generate_segment_kmeans():
    result = generate_segment(algorithm="kmeans", n_clusters=2)
    assert "segments" in result


def test_avg_helper():
    assert _avg([1, 2, 3]) == 2.0
    assert _avg([]) == 0.0


# ── Leads Tests ──


def test_recency_factor():
    from datetime import date, timedelta

    recent = (date.today() - timedelta(days=15)).isoformat()
    assert _recency_factor(recent) > 0.5
    assert _recency_factor(None) == 0.3


def test_balance_factor():
    assert _balance_factor(60000) == 1.0
    assert _balance_factor(25000) == 0.7
    assert _balance_factor(1000) == 0.1


def test_score_leads():
    result = score_leads("PROMO-PREMIUM-MEMBERSHIP", top_n=5)
    assert "prospects" in result
    assert "total_eligible" in result
    assert result["offer_code"] == "PROMO-PREMIUM-MEMBERSHIP"


def test_score_leads_with_segment():
    result = score_leads("PROMO-LOYALTY-POINTS", top_n=5, segment="vip")
    assert result["segment_filter"] == "vip"


def test_enrich_customer_not_found():
    result = enrich_customer("CUST-NONEXISTENT")
    assert result["error"] == "customer_not_found"


def test_enrich_customer_found():
    with patch("src.tools.leads._load_lead_scores") as mock_load:
        mock_load.return_value = [
            {
                "customer_id": "CUST-001",
                "full_name": "Test User",
                "segment": "vip",
                "enrichment": {"credit_score": 750},
            }
        ]
        result = enrich_customer("CUST-001")
        assert result["customer_id"] == "CUST-001"
        assert "enrichment" in result


def test_upsell_recommend_not_found():
    result = upsell_recommend("CUST-NONEXISTENT")
    assert result["error"] == "customer_not_found"


def test_upsell_recommend_found():
    with patch("src.tools.leads._load_customers") as mock_load:
        mock_load.return_value = [
            {
                "customer_id": "CUST-001",
                "full_name": "Test User",
                "segment": "vip",
                "purchase_categories": ["electronics"],
                "engagement_score": 0.8,
                "lifetime_value": 30000,
                "fraud_score": 0.1,
            }
        ]
        result = upsell_recommend("CUST-001")
        assert result["customer_id"] == "CUST-001"
        assert "upsell_targets" in result
        assert "recommended_promo" in result


def test_user_based_recommend_not_found():
    result = user_based_recommend("CUST-NONEXISTENT")
    assert result["error"] == "customer_not_found"


def test_user_based_recommend_no_peers():
    with patch("src.tools.leads._load_customers") as mock_load:
        mock_load.return_value = [
            {
                "customer_id": "CUST-001",
                "full_name": "Test User",
                "segment": "vip",
                "purchase_categories": ["electronics"],
                "engagement_score": 0.8,
                "lifetime_value": 30000,
            }
        ]
        result = user_based_recommend("CUST-001")
        assert result["customer_id"] == "CUST-001"
        assert "recommendations" in result


def test_collaborative_recommend_not_found():
    result = collaborative_recommend("CUST-NONEXISTENT")
    assert result["error"] == "customer_not_found"


def test_collaborative_recommend_found():
    with patch("src.tools.leads._load_customers") as mock_load:
        mock_load.return_value = [
            {
                "customer_id": "CUST-001",
                "full_name": "User 1",
                "segment": "vip",
                "purchase_categories": ["electronics"],
                "engagement_score": 0.8,
                "lifetime_value": 30000,
            },
            {
                "customer_id": "CUST-002",
                "full_name": "User 2",
                "segment": "vip",
                "purchase_categories": ["electronics", "home"],
                "engagement_score": 0.75,
                "lifetime_value": 25000,
            },
        ]
        result = collaborative_recommend("CUST-001", top_n=3)
        assert result["customer_id"] == "CUST-001"
        assert "recommendations" in result


def test_bulk_recommend():
    with patch("src.tools.leads.score_leads") as mock_score, patch(
        "src.tools.leads._load_customers"
    ) as mock_load:
        mock_score.return_value = {
            "prospects": [
                {"customer_id": "CUST-001", "lead_score": 0.9},
                {"customer_id": "CUST-002", "lead_score": 0.8},
            ]
        }
        mock_load.return_value = [
            {
                "customer_id": "CUST-001",
                "consent_flags": {"email": True, "marketing": True},
                "fraud_score": 0.1,
            },
            {
                "customer_id": "CUST-002",
                "consent_flags": {"sms": True, "marketing": True},
                "fraud_score": 0.2,
            },
        ]
        result = bulk_recommend("PROMO-PREMIUM-MEMBERSHIP", top_n=10)
        assert "execution_plan" in result
        assert result["to_send"] >= 0
