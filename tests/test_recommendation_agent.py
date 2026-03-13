"""Tests for recommendation agent."""

import pytest
from agentic.agentic_state import new_agentic_state
from agentic.recommendation_agent import (
    recommendation_agent,
    _extract_customer_id,
    _extract_top_k,
    _format_recommendations,
)


class TestExtractCustomerId:
    """Test customer ID extraction."""

    def test_extract_cust_format(self):
        """Test extracting CUST-XXX format."""
        customer_id = _extract_customer_id("Recommend products for CUST-001")
        assert customer_id == "CUST-001"

    def test_extract_case_insensitive(self):
        """Test extraction is case insensitive."""
        customer_id = _extract_customer_id("Recommend for cust-001")
        assert customer_id == "CUST-001"

    def test_extract_multiple_returns_first(self):
        """Test that multiple IDs returns first."""
        customer_id = _extract_customer_id("Compare CUST-001 and CUST-002")
        assert customer_id == "CUST-001"

    def test_extract_returns_none_if_not_found(self):
        """Test returns None if not found."""
        customer_id = _extract_customer_id("Recommend products")
        assert customer_id is None


class TestExtractTopK:
    """Test top_k extraction."""

    def test_extract_top_k_with_underscore(self):
        """Test extracting top_k with underscore."""
        top_k = _extract_top_k("Recommend top_5 products")
        assert top_k == 5

    def test_extract_top_k_with_dash(self):
        """Test extracting top-k with dash."""
        top_k = _extract_top_k("Recommend top-10 products")
        assert top_k == 10

    def test_extract_top_k_with_space(self):
        """Test extracting top k with space."""
        top_k = _extract_top_k("Recommend top 3 products")
        assert top_k == 3

    def test_extract_top_k_default(self):
        """Test default top_k if not specified."""
        top_k = _extract_top_k("Recommend products")
        assert top_k == 10

    def test_extract_top_k_case_insensitive(self):
        """Test extraction is case insensitive."""
        top_k = _extract_top_k("Recommend TOP 5 products")
        assert top_k == 5


class TestFormatRecommendations:
    """Test recommendation formatting."""

    def test_format_error_result(self):
        """Test formatting error result."""
        result = {"error": "No recommendations"}
        formatted = _format_recommendations(result, "CUST-001")
        assert "Error" in formatted or "error" in formatted.lower()

    def test_format_no_recommendations(self):
        """Test formatting when no recommendations."""
        result = {"recommendations": []}
        formatted = _format_recommendations(result, "CUST-001")
        assert "No recommendations" in formatted

    def test_format_with_recommendations(self):
        """Test formatting with recommendations."""
        result = {
            "recommendations": [
                {"product_id": "PROD-001", "score": 0.95},
                {"product_id": "PROD-002", "score": 0.85},
            ]
        }
        formatted = _format_recommendations(result, "CUST-001")
        assert "2" in formatted or "recommendations" in formatted.lower()
        assert "PROD-001" in formatted

    def test_format_cold_start(self):
        """Test formatting cold start recommendations."""
        result = {
            "recommendations": [
                {"product_id": "PROD-001", "score": 0.95}
            ],
            "cold_start": True
        }
        formatted = _format_recommendations(result, "CUST-001")
        assert "Cold start" in formatted or "cold" in formatted.lower()

    def test_format_personalized(self):
        """Test formatting personalized recommendations."""
        result = {
            "recommendations": [
                {"product_id": "PROD-001", "score": 0.95}
            ],
            "cold_start": False
        }
        formatted = _format_recommendations(result, "CUST-001")
        assert "personalized" in formatted.lower()

    def test_format_shows_top_5(self):
        """Test that format shows top 5 recommendations."""
        result = {
            "recommendations": [
                {"product_id": f"PROD-{i:03d}", "score": 0.9 - i*0.01}
                for i in range(10)
            ]
        }
        formatted = _format_recommendations(result, "CUST-001")
        # Should show only top 5
        assert "PROD-000" in formatted
        assert "PROD-004" in formatted


class TestRecommendationAgent:
    """Test recommendation agent."""

    def test_recommendation_agent_requires_customer_id(self):
        """Test that recommendation agent requires customer ID."""
        state = new_agentic_state("Recommend products", user_id="user1")
        state["intent"] = "recommendation"
        state["confidence"] = 0.9
        
        result = recommendation_agent(state)
        assert "error" in result

    def test_recommendation_agent_with_customer_id(self):
        """Test recommendation agent with customer ID."""
        state = new_agentic_state("Recommend products for CUST-001", user_id="user1")
        state["intent"] = "recommendation"
        state["confidence"] = 0.9
        
        result = recommendation_agent(state)
        assert result["active_agent"] == "recommendation"

    def test_recommendation_agent_returns_dict(self):
        """Test that recommendation agent returns dict."""
        state = new_agentic_state("Recommend for CUST-001", user_id="user1")
        state["intent"] = "recommendation"
        state["confidence"] = 0.9
        
        result = recommendation_agent(state)
        assert isinstance(result, dict)

    def test_recommendation_agent_sets_active_agent(self):
        """Test that recommendation agent sets active_agent."""
        state = new_agentic_state("Recommend for CUST-001", user_id="user1")
        state["intent"] = "recommendation"
        state["confidence"] = 0.9
        
        result = recommendation_agent(state)
        assert result["active_agent"] == "recommendation"

    def test_recommendation_agent_has_messages(self):
        """Test that recommendation agent returns messages."""
        state = new_agentic_state("Recommend for CUST-001", user_id="user1")
        state["intent"] = "recommendation"
        state["confidence"] = 0.9
        
        result = recommendation_agent(state)
        assert "messages" in result
        assert len(result["messages"]) > 0

    def test_recommendation_agent_has_audit_trail(self):
        """Test that recommendation agent has audit trail."""
        state = new_agentic_state("Recommend for CUST-001", user_id="user1")
        state["intent"] = "recommendation"
        state["confidence"] = 0.9
        
        result = recommendation_agent(state)
        assert "audit_trail" in result
        assert len(result["audit_trail"]) > 0

    def test_recommendation_agent_has_mcp_calls(self):
        """Test that recommendation agent records MCP calls."""
        state = new_agentic_state("Recommend for CUST-001", user_id="user1")
        state["intent"] = "recommendation"
        state["confidence"] = 0.9
        
        result = recommendation_agent(state)
        assert "mcp_calls" in result
        assert len(result["mcp_calls"]) > 0

    def test_recommendation_agent_has_intermediate_results(self):
        """Test that recommendation agent has intermediate results."""
        state = new_agentic_state("Recommend for CUST-001", user_id="user1")
        state["intent"] = "recommendation"
        state["confidence"] = 0.9
        
        result = recommendation_agent(state)
        assert "intermediate_results" in result

    def test_recommendation_agent_has_final_result(self):
        """Test that recommendation agent has final result."""
        state = new_agentic_state("Recommend for CUST-001", user_id="user1")
        state["intent"] = "recommendation"
        state["confidence"] = 0.9
        
        result = recommendation_agent(state)
        assert "final_result" in result

    def test_recommendation_agent_with_top_k(self):
        """Test recommendation agent with top_k parameter."""
        state = new_agentic_state("Recommend top 5 for CUST-001", user_id="user1")
        state["intent"] = "recommendation"
        state["confidence"] = 0.9
        
        result = recommendation_agent(state)
        assert result["active_agent"] == "recommendation"

    def test_recommendation_agent_error_has_message(self):
        """Test that error result has message."""
        state = new_agentic_state("Recommend products", user_id="user1")
        state["intent"] = "recommendation"
        state["confidence"] = 0.9
        
        result = recommendation_agent(state)
        assert "messages" in result
        assert len(result["messages"]) > 0
