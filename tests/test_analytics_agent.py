"""Tests for analytics agent."""

import pytest
from agentic.agentic_state import new_agentic_state
from agentic.analytics_agent import (
    analytics_agent,
    _extract_sql_query,
    _extract_filters,
    _generate_insights,
    _format_analytics_result,
)


class TestExtractSqlQuery:
    """Test SQL query extraction."""

    def test_extract_sql_code_block(self):
        """Test extracting SQL from code block."""
        request = "```sql\nSELECT * FROM customers\n```"
        sql = _extract_sql_query(request)
        assert sql is not None
        assert "SELECT" in sql
        assert "customers" in sql

    def test_extract_sql_multiline(self):
        """Test extracting multiline SQL."""
        request = "SELECT * FROM customers WHERE segment = 'VIP'"
        sql = _extract_sql_query(request)
        assert sql is not None
        assert "SELECT" in sql

    def test_extract_sql_with_semicolon(self):
        """Test extracting SQL with semicolon."""
        request = "SELECT * FROM customers;"
        sql = _extract_sql_query(request)
        assert sql is not None

    def test_extract_sql_case_insensitive(self):
        """Test SQL extraction is case insensitive."""
        request = "select * from customers"
        sql = _extract_sql_query(request)
        assert sql is not None

    def test_extract_sql_returns_none_if_not_found(self):
        """Test returns None if no SQL found."""
        request = "What is the customer profile?"
        sql = _extract_sql_query(request)
        assert sql is None

    def test_extract_sql_cleans_whitespace(self):
        """Test that extraction cleans whitespace."""
        request = "SELECT   *   FROM   customers"
        sql = _extract_sql_query(request)
        assert "  " not in sql  # No double spaces


class TestExtractFilters:
    """Test filter extraction."""

    def test_extract_unverified_filter(self):
        """Test extracting unverified filter."""
        filters = _extract_filters("Show unverified customers")
        assert filters is not None
        assert filters["identity_status"] == "unverified"

    def test_extract_vip_filter(self):
        """Test extracting VIP filter."""
        filters = _extract_filters("Show VIP customers")
        assert filters is not None
        assert filters["segment"] == "vip"

    def test_extract_multiple_filters(self):
        """Test extracting multiple filters."""
        filters = _extract_filters("Show unverified VIP customers")
        assert filters is not None
        assert "identity_status" in filters
        assert "segment" in filters

    def test_extract_no_filters(self):
        """Test extracting when no filters present."""
        filters = _extract_filters("Show all customers")
        assert filters is None or filters == {}


class TestGenerateInsights:
    """Test insight generation."""

    def test_generate_insights_from_segments(self):
        """Test generating insights from segments."""
        result = {
            "segments": [
                {"label": "VIP", "size": 100},
                {"label": "Standard", "size": 50},
            ]
        }
        insights = _generate_insights(result)
        assert len(insights) > 0
        assert "VIP" in insights[0]

    def test_generate_insights_from_rows(self):
        """Test generating insights from rows."""
        result = {"rows": [{"id": 1}, {"id": 2}], "row_count": 2}
        insights = _generate_insights(result)
        assert len(insights) > 0
        assert "2 rows" in insights[0]

    def test_generate_insights_empty_result(self):
        """Test generating insights from empty result."""
        result = {}
        insights = _generate_insights(result)
        assert insights == []

    def test_generate_insights_no_segments(self):
        """Test generating insights with no segments."""
        result = {"segments": []}
        insights = _generate_insights(result)
        assert insights == []


class TestFormatAnalyticsResult:
    """Test result formatting."""

    def test_format_error_result(self):
        """Test formatting error result."""
        result = {"error": "Query failed"}
        insights = []
        formatted = _format_analytics_result(result, insights)
        assert "error" in formatted.lower()

    def test_format_segments_result(self):
        """Test formatting segments result."""
        result = {
            "segments": [
                {"label": "VIP", "size": 100},
                {"label": "Standard", "size": 50},
            ]
        }
        insights = []
        formatted = _format_analytics_result(result, insights)
        assert "2 segments" in formatted
        assert "VIP" in formatted

    def test_format_rows_result(self):
        """Test formatting rows result."""
        result = {"rows": [{"id": 1}], "row_count": 1}
        insights = []
        formatted = _format_analytics_result(result, insights)
        assert "1 rows" in formatted

    def test_format_with_insights(self):
        """Test formatting with insights."""
        result = {"segments": [{"label": "VIP", "size": 100}]}
        insights = ["Largest segment: VIP"]
        formatted = _format_analytics_result(result, insights)
        assert "Insights:" in formatted
        assert "VIP" in formatted

    def test_format_empty_result(self):
        """Test formatting empty result."""
        result = {}
        insights = []
        formatted = _format_analytics_result(result, insights)
        assert formatted is not None


class TestAnalyticsAgent:
    """Test analytics agent."""

    def test_analytics_agent_returns_dict(self):
        """Test that analytics agent returns dict."""
        state = new_agentic_state("Segment customers", user_id="user1")
        state["intent"] = "analytics"
        state["confidence"] = 0.9
        
        result = analytics_agent(state)
        assert isinstance(result, dict)

    def test_analytics_agent_sets_active_agent(self):
        """Test that analytics agent sets active_agent."""
        state = new_agentic_state("Segment customers", user_id="user1")
        state["intent"] = "analytics"
        state["confidence"] = 0.9
        
        result = analytics_agent(state)
        assert result["active_agent"] == "analytics"

    def test_analytics_agent_has_messages(self):
        """Test that analytics agent returns messages."""
        state = new_agentic_state("Segment customers", user_id="user1")
        state["intent"] = "analytics"
        state["confidence"] = 0.9
        
        result = analytics_agent(state)
        assert "messages" in result
        assert len(result["messages"]) > 0

    def test_analytics_agent_has_audit_trail(self):
        """Test that analytics agent has audit trail."""
        state = new_agentic_state("Segment customers", user_id="user1")
        state["intent"] = "analytics"
        state["confidence"] = 0.9
        
        result = analytics_agent(state)
        assert "audit_trail" in result
        assert len(result["audit_trail"]) > 0

    def test_analytics_agent_has_mcp_calls(self):
        """Test that analytics agent records MCP calls."""
        state = new_agentic_state("Segment customers", user_id="user1")
        state["intent"] = "analytics"
        state["confidence"] = 0.9
        
        result = analytics_agent(state)
        assert "mcp_calls" in result

    def test_analytics_agent_has_intermediate_results(self):
        """Test that analytics agent has intermediate results."""
        state = new_agentic_state("Segment customers", user_id="user1")
        state["intent"] = "analytics"
        state["confidence"] = 0.9
        
        result = analytics_agent(state)
        assert "intermediate_results" in result

    def test_analytics_agent_has_final_result(self):
        """Test that analytics agent has final result."""
        state = new_agentic_state("Segment customers", user_id="user1")
        state["intent"] = "analytics"
        state["confidence"] = 0.9
        
        result = analytics_agent(state)
        assert "final_result" in result

    def test_analytics_agent_with_sql_query(self):
        """Test analytics agent with SQL query."""
        state = new_agentic_state("SELECT * FROM customers", user_id="user1")
        state["intent"] = "analytics"
        state["confidence"] = 0.9
        
        result = analytics_agent(state)
        assert result["active_agent"] == "analytics"

    def test_analytics_agent_with_segment_request(self):
        """Test analytics agent with segment request."""
        state = new_agentic_state("Segment customers by risk", user_id="user1")
        state["intent"] = "analytics"
        state["confidence"] = 0.9
        
        result = analytics_agent(state)
        assert result["active_agent"] == "analytics"

    def test_analytics_agent_with_generic_request(self):
        """Test analytics agent with generic request."""
        state = new_agentic_state("Analyze data", user_id="user1")
        state["intent"] = "analytics"
        state["confidence"] = 0.9
        
        result = analytics_agent(state)
        assert result["active_agent"] == "analytics"

    def test_analytics_agent_has_warning_message(self):
        """Test that analytics agent includes warning message."""
        state = new_agentic_state("Segment customers", user_id="user1")
        state["intent"] = "analytics"
        state["confidence"] = 0.9
        
        result = analytics_agent(state)
        message_content = result["messages"][0].content
        assert "⚠️" in message_content or "warning" in message_content.lower()
