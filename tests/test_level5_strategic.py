import pytest
from unittest.mock import patch
from nonagentic.AI.level5 import level5_node
from nonagentic.core.state import new_state
from nonagentic.tools.strategic import (
    simulate_revenue_impact,
    run_scenario_simulation,
    run_pilot_test,
    prioritize_initiatives,
)


def test_level5_missing_customer_id():
    state = new_state("recommend products")
    result = level5_node(state)
    assert result["routed_to"] == "level5_recommendation"
    assert "error" in result["result"]


def test_level5_extracts_customer_from_request():
    state = new_state("recommend for cust-001")
    with patch("src.agents.level5.recommend") as mock_rec:
        mock_rec.return_value = {"recommendations": [], "cold_start": False}
        result = level5_node(state)
        assert result["routed_to"] == "level5_recommendation"


def test_simulate_revenue_impact():
    result = simulate_revenue_impact(
        segment_size=1000,
        conversion_rate=0.05,
        avg_order_value=100.0,
        campaign_cost=500.0,
    )
    assert result["projected_conversions"] == 50
    assert result["projected_revenue"] == 5000.0
    assert result["incremental_revenue"] == 4500.0


def test_simulate_revenue_impact_zero_cost():
    result = simulate_revenue_impact(100, 0.1, 50.0, 0.0)
    assert result["roi_pct"] == 0.0


def test_run_scenario_simulation():
    scenarios = [
        {
            "name": "A",
            "segment_size": 100,
            "conversion_rate": 0.1,
            "avg_order_value": 50,
            "risk": "low",
            "campaign_cost": 100,
        },
        {
            "name": "B",
            "segment_size": 200,
            "conversion_rate": 0.05,
            "avg_order_value": 100,
            "risk": "high",
            "campaign_cost": 200,
        },
    ]
    results = run_scenario_simulation("test goal", scenarios)
    assert len(results) == 2
    assert any(r["recommended"] for r in results)


def test_run_pilot_test_compliance_pass():
    result = run_pilot_test(["C1", "C2", "C3", "C4"], "OFFER-01", pilot_pct=0.25)
    assert result["compliance_passed"] is True
    assert result["pilot_size"] == 1
    assert result["control_size"] == 3


def test_run_pilot_test_compliance_fail():
    result = run_pilot_test(["C1", "C2"], "OFFER-02", pilot_pct=0.6)
    assert result["compliance_passed"] is False


def test_prioritize_initiatives():
    initiatives = [
        {"name": "A", "est_revenue": 1000, "effort": "high"},
        {"name": "B", "est_revenue": 600, "effort": "low"},
        {"name": "C", "est_revenue": 800, "effort": "medium"},
    ]
    ranked = prioritize_initiatives(initiatives)
    assert ranked[0]["name"] == "B"  # 600/1 = 600
    assert ranked[1]["name"] == "C"  # 800/2 = 400
    assert ranked[2]["name"] == "A"  # 1000/3 = 333
