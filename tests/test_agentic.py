"""Tests for agentic AI system."""

import pytest
from agentic.agentic_state import new_agentic_state
from agentic.orchestrator_agent import orchestrator_agent, route_to_agent
from agentic.knowledge_agent import knowledge_agent
from agentic.analytics_agent import analytics_agent
from agentic.recommendation_agent import recommendation_agent
from graphs.agent_workflow_graph import build_agentic_graph


def test_new_agentic_state():
    """Test creating new agentic state."""
    state = new_agentic_state("Test request", user_id="test_user")
    assert state["original_request"] == "Test request"
    assert state["user_id"] == "test_user"
    assert state["intent"] == "unknown"
    assert state["confidence"] == 0.0


def test_orchestrator_classifies_knowledge_intent():
    """Test orchestrator classifies knowledge intent."""
    state = new_agentic_state("What is the customer profile for CUST-001?")
    updates = orchestrator_agent(state)
    assert updates["intent"] == "knowledge"
    assert updates["confidence"] > 0.6


def test_orchestrator_classifies_analytics_intent():
    """Test orchestrator classifies analytics intent."""
    state = new_agentic_state("Segment customers by risk score")
    updates = orchestrator_agent(state)
    assert updates["intent"] == "analytics"
    assert updates["confidence"] > 0.6


def test_orchestrator_classifies_recommendation_intent():
    """Test orchestrator classifies recommendation intent."""
    state = new_agentic_state("Recommend products for CUST-001")
    updates = orchestrator_agent(state)
    assert updates["intent"] == "recommendation"
    assert updates["confidence"] > 0.6


def test_route_to_agent_knowledge():
    """Test routing to knowledge agent."""
    state = new_agentic_state("Test")
    state["intent"] = "knowledge"
    state["confidence"] = 0.9
    route = route_to_agent(state)
    assert route == "knowledge_agent"


def test_route_to_agent_analytics():
    """Test routing to analytics agent."""
    state = new_agentic_state("Test")
    state["intent"] = "analytics"
    state["confidence"] = 0.9
    route = route_to_agent(state)
    assert route == "analytics_agent"


def test_route_to_agent_low_confidence():
    """Test routing to human approval for low confidence."""
    state = new_agentic_state("Test")
    state["intent"] = "unknown"
    state["confidence"] = 0.3
    route = route_to_agent(state)
    assert route == "human_approval"


def test_knowledge_agent_executes():
    """Test knowledge agent execution."""
    state = new_agentic_state("Show me customer CUST-001", user_id="test_user")
    state["intent"] = "knowledge"
    state["confidence"] = 0.9
    updates = knowledge_agent(state)
    assert updates["active_agent"] == "knowledge"
    assert len(updates["messages"]) > 0
    assert len(updates["audit_trail"]) > 0


def test_analytics_agent_executes():
    """Test analytics agent execution."""
    state = new_agentic_state("Segment customers", user_id="test_user")
    state["intent"] = "analytics"
    state["confidence"] = 0.9
    updates = analytics_agent(state)
    assert updates["active_agent"] == "analytics"
    assert len(updates["messages"]) > 0


def test_recommendation_agent_requires_customer_id():
    """Test recommendation agent requires customer ID."""
    state = new_agentic_state("Recommend products", user_id="test_user")
    state["intent"] = "recommendation"
    state["confidence"] = 0.9
    updates = recommendation_agent(state)
    assert "error" in updates


def test_recommendation_agent_with_customer_id():
    """Test recommendation agent with customer ID."""
    state = new_agentic_state("Recommend products for CUST-001", user_id="test_user")
    state["intent"] = "recommendation"
    state["confidence"] = 0.9
    updates = recommendation_agent(state)
    assert updates["active_agent"] == "recommendation"
    assert len(updates["messages"]) > 0


def test_agentic_graph_builds():
    """Test agentic graph can be built."""
    graph = build_agentic_graph()
    assert graph is not None


def test_agentic_graph_e2e_knowledge():
    """Test end-to-end knowledge request through agentic graph."""
    graph = build_agentic_graph()
    state = new_agentic_state("What is the profile for CUST-001?", user_id="test_user")
    config = {"configurable": {"thread_id": state["request_id"]}}
    result = graph.invoke(state, config=config)
    assert result["intent"] == "knowledge"
    assert len(result["messages"]) > 0


def test_agentic_graph_e2e_analytics():
    """Test end-to-end analytics request through agentic graph."""
    graph = build_agentic_graph()
    state = new_agentic_state("Segment customers by risk", user_id="test_user")
    config = {"configurable": {"thread_id": state["request_id"]}}
    result = graph.invoke(state, config=config)
    assert result["intent"] == "analytics"
    assert len(result["messages"]) > 0


def test_agentic_graph_e2e_recommendation():
    """Test end-to-end recommendation request through agentic graph."""
    graph = build_agentic_graph()
    state = new_agentic_state("Recommend products for CUST-005", user_id="test_user")
    config = {"configurable": {"thread_id": state["request_id"]}}
    result = graph.invoke(state, config=config)
    assert result["intent"] == "recommendation"
    assert len(result["messages"]) > 0
