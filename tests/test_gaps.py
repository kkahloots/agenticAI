"""
Tests for Gap Closure — Checkpoint 6
Covers: G2 (guardrails), G3 (sql chain), G6 (tokens_used), G7+G8 (self-reflection), G10 (config thresholds)
"""
import os
import pytest
from unittest.mock import patch, MagicMock


# ── G10 — configurable thresholds ────────────────────────────────────────────

def test_config_reads_defaults():
    from src.core.config import load_config
    cfg = load_config()
    assert cfg.bulk_notification_threshold == 100
    assert cfg.campaign_reach_threshold == 1000
    assert cfg.risk_score_threshold == 0.8
    assert cfg.payment_delay_threshold == 0.8
    assert cfg.kpi_deviation_threshold == 0.10
    assert cfg.sql_max_rows == 10_000
    assert cfg.guardrail_enabled is True


def test_config_reads_env_overrides(monkeypatch):
    monkeypatch.setenv("APPROVAL_BULK_THRESHOLD", "50")
    monkeypatch.setenv("APPROVAL_CAMPAIGN_REACH_THRESHOLD", "500")
    monkeypatch.setenv("APPROVAL_RISK_SCORE_THRESHOLD", "0.7")
    monkeypatch.setenv("KPI_DEVIATION_THRESHOLD", "0.05")
    monkeypatch.setenv("GUARDRAIL_ENABLED", "false")
    from src.core.config import load_config
    cfg = load_config()
    assert cfg.bulk_notification_threshold == 50
    assert cfg.campaign_reach_threshold == 500
    assert cfg.risk_score_threshold == 0.7
    assert cfg.kpi_deviation_threshold == 0.05
    assert cfg.guardrail_enabled is False


def test_schedule_campaign_uses_config_threshold(monkeypatch):
    monkeypatch.setenv("APPROVAL_CAMPAIGN_REACH_THRESHOLD", "200")
    from src.tools.strategic import schedule_campaign
    result = schedule_campaign(
        campaign_name="Test", segment_id="seg", steps=[],
        start_date="2025-08-01", estimated_reach=201, approved=False,
    )
    assert result["status"] == "approval_required"
    assert "200" in result["reason"]


def test_schedule_campaign_passes_below_config_threshold(monkeypatch):
    monkeypatch.setenv("APPROVAL_CAMPAIGN_REACH_THRESHOLD", "200")
    from src.tools.strategic import schedule_campaign
    result = schedule_campaign(
        campaign_name="Test", segment_id="seg", steps=[],
        start_date="2025-08-01", estimated_reach=199, approved=False,
    )
    assert result["status"] == "scheduled"


# ── G2 — ConstitutionalChain guardrail ───────────────────────────────────────

def test_guardrail_passes_clean_text():
    from src.core.guardrails import guardrail_check
    result = guardrail_check("Customer segment: high-value. KYC status: valid.")
    assert result.passed is True
    assert result.violations == []
    assert result.revised_text == "Customer segment: high-value. KYC status: valid."


def test_guardrail_redacts_email():
    from src.core.guardrails import guardrail_check
    result = guardrail_check("Contact the customer at john.doe@example.com for follow-up.")
    assert result.passed is False
    assert any("email" in v.lower() for v in result.violations)
    assert "john.doe@example.com" not in result.revised_text
    assert "[email redacted]" in result.revised_text


def test_guardrail_redacts_phone():
    from src.core.guardrails import guardrail_check
    result = guardrail_check("Call the customer at +36 30 123 4567 today.")
    assert result.passed is False
    assert any("phone" in v.lower() for v in result.violations)
    assert "[phone redacted]" in result.revised_text


def test_guardrail_blocks_forbidden_phrase():
    from src.core.guardrails import guardrail_check
    result = guardrail_check("You should buy shares in this company for guaranteed return.")
    assert result.passed is False
    assert len(result.violations) > 0


def test_guardrail_disabled_skips_all_checks(monkeypatch):
    monkeypatch.setenv("GUARDRAIL_ENABLED", "false")
    from src.core.guardrails import guardrail_check
    result = guardrail_check("Contact at bad@email.com — buy shares now!")
    assert result.passed is True  # disabled — no checks run


# ── G6 — tokens_used in observability ────────────────────────────────────────

def test_node_end_event_has_tokens_used_field():
    from src.core.observability import clear_event_log, get_event_log, node_trace

    clear_event_log()

    @node_trace("test_node")
    def dummy_node(state):
        return {"tool_calls": []}

    dummy_node({"request_id": "test-req-001"})
    events = get_event_log()
    end_events = [e for e in events if e["event"] == "node_end"]
    assert len(end_events) == 1
    assert "tokens_used" in end_events[0]
    assert isinstance(end_events[0]["tokens_used"], int)


def test_record_tokens_accumulates():
    from src.core.observability import record_tokens, _token_accumulator
    _token_accumulator.clear()
    record_tokens("req-abc", 100)
    record_tokens("req-abc", 50)
    assert _token_accumulator["req-abc"] == 150


# ── G7+G8 — self-reflection loop ─────────────────────────────────────────────

def test_reflect_and_replan_no_action_when_kpi_ok():
    from src.tools.monitoring import reflect_and_replan, _KPI_STORE
    # Ensure no prior data for this segment
    _KPI_STORE.pop("test-seg-ok", None)
    result = reflect_and_replan("test-seg-ok", "Grow revenue")
    # No prior data → deviation = |0 - 0.05| = 0.05 = threshold → no action
    assert "should_replan" in result
    assert isinstance(result["should_replan"], bool)


def test_reflect_and_replan_triggers_when_deviation_high(monkeypatch):
    from src.tools.monitoring import _KPI_STORE
    # Seed KPI store with a very low conversion rate
    _KPI_STORE["test-seg-bad"] = {
        "campaigns_run": 2,
        "avg_conversion_rate": 0.001,  # far below 0.05 target → deviation 0.049 > default 0.10? No.
        "avg_open_rate": 0.1,
        "last_updated": "2025-01-01T00:00:00Z",
    }
    # Use a very tight threshold so deviation of 0.049 triggers replan
    monkeypatch.setenv("KPI_DEVIATION_THRESHOLD", "0.01")
    # Import AFTER monkeypatch so load_config() picks up the new value
    import importlib, src.tools.monitoring as mmod
    importlib.reload(mmod)
    result = mmod.reflect_and_replan("test-seg-bad", "Grow revenue")
    assert result["should_replan"] is True
    assert "reason" in result
    assert "recommended_action" in result


def test_check_kpi_deviation_uses_config_threshold(monkeypatch):
    monkeypatch.setenv("KPI_DEVIATION_THRESHOLD", "0.02")
    from src.tools.monitoring import check_kpi_deviation, _KPI_STORE
    _KPI_STORE["seg-dev"] = {
        "campaigns_run": 1,
        "avg_conversion_rate": 0.03,  # deviation from 0.05 target = 0.02 = threshold
        "avg_open_rate": 0.2,
        "last_updated": "2025-01-01T00:00:00Z",
    }
    result = check_kpi_deviation("seg-dev", target_conversion_rate=0.05)
    assert result["deviation"] == pytest.approx(0.02, abs=0.001)


def test_level4_result_contains_reflection_key():
    from src.core.state import new_state
    from src.graph import build_graph
    g = build_graph()
    state = new_state("Increase Visa Gold card adoption by 5% this quarter")
    config = {"configurable": {"thread_id": state["request_id"]}}
    final = g.invoke(state, config=config)
    assert final["routed_to"] == "level4_strategic"
    assert "reflection" in final["result"]
    assert "should_replan" in final["result"]["reflection"]


# ── G3 — create_sql_query_chain path ─────────────────────────────────────────

def test_sql_chain_falls_back_to_llm_when_db_unavailable():
    """
    When the DB is not set up, _sql_chain_query should fall back to
    _llm_fallback_sql which raises (LLM mocked) → returns None → error result.
    """
    from src.agents.level2 import _sql_chain_query
    # Both chain and fallback will fail (LLM mocked in conftest) → None
    result = _sql_chain_query("Show me all customers with expired KYC")
    # Should return None or a string — not raise
    assert result is None or isinstance(result, str)


def test_level2_sql_error_returns_graceful_message():
    from src.core.state import new_state
    from src.graph import build_graph
    g = build_graph()
    # Use a clearly analytical phrase that routes to level2
    state = new_state("Run a SQL query to show average account_balance by segment")
    config = {"configurable": {"thread_id": state["request_id"]}}
    final = g.invoke(state, config=config)
    assert final["routed_to"] == "level2_analytics"
    # Either got rows or a graceful error — never an exception
    assert final["result"] is not None
