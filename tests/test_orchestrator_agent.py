"""Tests for orchestrator agent."""

import pytest
from agentic.agentic_state import new_agentic_state
from agentic.orchestrator_agent import (
    classify_intent,
    _pre_classify,
    _rule_based_classify,
    build_agent_plan,
    orchestrator_agent,
    route_to_agent,
)


class TestPreClassify:
    """Test pre-classification patterns."""

    def test_sql_select_from_pattern(self):
        """Test SQL SELECT FROM pattern recognition."""
        intent, confidence = _pre_classify("SELECT * FROM customers")
        assert intent == "analytics"
        assert confidence == 0.95

    def test_sql_query_prefix(self):
        """Test SQL query prefix patterns."""
        intent, confidence = _pre_classify("run this sql: SELECT * FROM users")
        assert intent == "analytics"
        assert confidence == 0.95

    def test_segment_customers_pattern(self):
        """Test segment customers pattern."""
        intent, confidence = _pre_classify("segment customers by risk")
        assert intent == "analytics"
        assert confidence == 0.95

    def test_cluster_pattern(self):
        """Test cluster pattern."""
        intent, confidence = _pre_classify("cluster customers")
        assert intent == "analytics"
        assert confidence == 0.95

    def test_no_match_returns_none(self):
        """Test that non-matching patterns return None."""
        result = _pre_classify("What is the customer profile?")
        assert result is None


class TestRuleBasedClassify:
    """Test rule-based classification fallback."""

    def test_recommendation_keywords(self):
        """Test recommendation keyword detection."""
        intent, confidence, reasoning = _rule_based_classify("recommend products")
        assert intent == "recommendation"
        assert confidence == 0.85

    def test_workflow_keywords(self):
        """Test workflow keyword detection."""
        intent, confidence, reasoning = _rule_based_classify("execute multi-step campaign")
        assert intent == "workflow"
        assert confidence == 0.85

    def test_analytics_keywords(self):
        """Test analytics keyword detection."""
        intent, confidence, reasoning = _rule_based_classify("analyze kpi metrics")
        assert intent == "analytics"
        assert confidence == 0.85

    def test_action_keywords(self):
        """Test action keyword detection."""
        intent, confidence, reasoning = _rule_based_classify("send notification")
        assert intent == "action"
        assert confidence == 0.85

    def test_knowledge_keywords(self):
        """Test knowledge keyword detection."""
        intent, confidence, reasoning = _rule_based_classify("what is the status")
        assert intent == "knowledge"
        assert confidence == 0.85

    def test_unknown_intent(self):
        """Test unknown intent fallback."""
        intent, confidence, reasoning = _rule_based_classify("xyz abc def")
        assert intent == "unknown"
        assert confidence == 0.4


class TestClassifyIntent:
    """Test intent classification."""

    def test_classify_knowledge_intent(self):
        """Test classifying knowledge intent."""
        intent, confidence, reasoning = classify_intent("What is customer CUST-001?")
        assert intent in ["knowledge", "analytics"]  # Could be either
        assert 0.0 <= confidence <= 1.0

    def test_classify_analytics_intent(self):
        """Test classifying analytics intent."""
        intent, confidence, reasoning = classify_intent("SELECT * FROM customers")
        assert intent == "analytics"
        assert confidence >= 0.85

    def test_classify_recommendation_intent(self):
        """Test classifying recommendation intent."""
        intent, confidence, reasoning = classify_intent("recommend products for CUST-001")
        assert intent in ["recommendation", "knowledge"]
        assert 0.0 <= confidence <= 1.0

    def test_confidence_is_float(self):
        """Test that confidence is a float."""
        intent, confidence, reasoning = classify_intent("test query")
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0

    def test_reasoning_is_string(self):
        """Test that reasoning is a string."""
        intent, confidence, reasoning = classify_intent("test query")
        assert isinstance(reasoning, str)


class TestBuildAgentPlan:
    """Test agent plan building."""

    def test_knowledge_plan(self):
        """Test building knowledge plan."""
        state = new_agentic_state("test")
        plan = build_agent_plan("knowledge", "test", state)
        assert "agents" in plan
        assert "knowledge" in plan["agents"]
        assert "steps" in plan
        assert "mcp_servers" in plan

    def test_analytics_plan(self):
        """Test building analytics plan."""
        state = new_agentic_state("test")
        plan = build_agent_plan("analytics", "test", state)
        assert "analytics" in plan["agents"]
        assert "analytics" in plan["mcp_servers"]

    def test_recommendation_plan(self):
        """Test building recommendation plan."""
        state = new_agentic_state("test")
        plan = build_agent_plan("recommendation", "test", state)
        assert "recommendation" in plan["agents"]
        assert "recommendation" in plan["mcp_servers"]

    def test_workflow_plan(self):
        """Test building workflow plan."""
        state = new_agentic_state("test")
        plan = build_agent_plan("workflow", "test", state)
        assert "workflow" in plan["agents"]
        assert len(plan["agents"]) > 1  # Multiple agents

    def test_action_plan(self):
        """Test building action plan."""
        state = new_agentic_state("test")
        plan = build_agent_plan("action", "test", state)
        assert "action" in plan["agents"]

    def test_unknown_intent_defaults_to_knowledge(self):
        """Test that unknown intent defaults to knowledge."""
        state = new_agentic_state("test")
        plan = build_agent_plan("unknown", "test", state)
        assert "knowledge" in plan["agents"]

    def test_plan_has_required_fields(self):
        """Test that plan has all required fields."""
        state = new_agentic_state("test")
        plan = build_agent_plan("knowledge", "test", state)
        assert "agents" in plan
        assert "steps" in plan
        assert "mcp_servers" in plan
        assert isinstance(plan["agents"], list)
        assert isinstance(plan["steps"], list)
        assert isinstance(plan["mcp_servers"], list)


class TestOrchestratorAgent:
    """Test orchestrator agent."""

    def test_orchestrator_returns_dict(self):
        """Test that orchestrator returns a dict."""
        state = new_agentic_state("test")
        result = orchestrator_agent(state)
        assert isinstance(result, dict)

    def test_orchestrator_sets_intent(self):
        """Test that orchestrator sets intent."""
        state = new_agentic_state("What is customer CUST-001?")
        result = orchestrator_agent(state)
        assert "intent" in result
        assert result["intent"] != "unknown"

    def test_orchestrator_sets_confidence(self):
        """Test that orchestrator sets confidence."""
        state = new_agentic_state("test")
        result = orchestrator_agent(state)
        assert "confidence" in result
        assert 0.0 <= result["confidence"] <= 1.0

    def test_orchestrator_sets_active_agent(self):
        """Test that orchestrator sets active agent."""
        state = new_agentic_state("test")
        result = orchestrator_agent(state)
        assert "active_agent" in result
        assert result["active_agent"] != ""

    def test_orchestrator_builds_plan(self):
        """Test that orchestrator builds plan."""
        state = new_agentic_state("test")
        result = orchestrator_agent(state)
        assert "agent_plan" in result
        assert result["agent_plan"] is not None

    def test_orchestrator_records_audit(self):
        """Test that orchestrator records audit trail."""
        state = new_agentic_state("test")
        result = orchestrator_agent(state)
        assert "audit_trail" in result
        assert len(result["audit_trail"]) > 0

    def test_orchestrator_with_custom_user_id(self):
        """Test orchestrator with custom user_id."""
        state = new_agentic_state("test", user_id="user123")
        result = orchestrator_agent(state)
        assert result["audit_trail"][0].get("user_id") is None  # Not in audit trail


class TestRouteToAgent:
    """Test agent routing."""

    def test_route_knowledge_intent(self):
        """Test routing knowledge intent."""
        state = new_agentic_state("test")
        state["intent"] = "knowledge"
        state["confidence"] = 0.9
        route = route_to_agent(state)
        assert route == "knowledge_agent"

    def test_route_analytics_intent(self):
        """Test routing analytics intent."""
        state = new_agentic_state("test")
        state["intent"] = "analytics"
        state["confidence"] = 0.9
        route = route_to_agent(state)
        assert route == "analytics_agent"

    def test_route_recommendation_intent(self):
        """Test routing recommendation intent."""
        state = new_agentic_state("test")
        state["intent"] = "recommendation"
        state["confidence"] = 0.9
        route = route_to_agent(state)
        assert route == "recommendation_agent"

    def test_route_workflow_intent(self):
        """Test routing workflow intent."""
        state = new_agentic_state("test")
        state["intent"] = "workflow"
        state["confidence"] = 0.9
        route = route_to_agent(state)
        assert route == "workflow_agent"

    def test_route_action_intent(self):
        """Test routing action intent."""
        state = new_agentic_state("test")
        state["intent"] = "action"
        state["confidence"] = 0.9
        route = route_to_agent(state)
        assert route == "action_agent"

    def test_route_low_confidence_to_human(self):
        """Test routing low confidence to human approval."""
        state = new_agentic_state("test")
        state["intent"] = "knowledge"
        state["confidence"] = 0.3
        route = route_to_agent(state)
        assert route == "human_approval"

    def test_route_error_to_error_handler(self):
        """Test routing error to error handler."""
        state = new_agentic_state("test")
        state["error"] = "Some error"
        route = route_to_agent(state)
        assert route == "error_handler"

    def test_route_unknown_intent_defaults_to_knowledge(self):
        """Test that unknown intent defaults to knowledge agent."""
        state = new_agentic_state("test")
        state["intent"] = "unknown"
        state["confidence"] = 0.9
        route = route_to_agent(state)
        assert route == "knowledge_agent"
