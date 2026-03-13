"""Tests for output adapter."""

import pytest
from agentic.agentic_state import new_agentic_state
from agentic.output_adapter import (
    adapt_agentic_to_nonagent,
    _extract_customer_id,
    _convert_mcp_to_tool_calls,
    compare_outputs,
)


class TestExtractCustomerId:
    """Test customer ID extraction."""

    def test_extract_from_user_profile(self):
        """Test extracting customer ID from user profile."""
        state = new_agentic_state("test")
        state["user_profile"] = {"customer_id": "CUST-001"}
        customer_id = _extract_customer_id(state)
        assert customer_id == "CUST-001"

    def test_extract_from_intermediate_results(self):
        """Test extracting customer ID from intermediate results."""
        state = new_agentic_state("test")
        state["intermediate_results"] = [
            {"result": {"customer_id": "CUST-002"}}
        ]
        customer_id = _extract_customer_id(state)
        assert customer_id == "CUST-002"

    def test_extract_from_request(self):
        """Test extracting customer ID from request."""
        state = new_agentic_state("Show me CUST-003")
        customer_id = _extract_customer_id(state)
        assert customer_id == "CUST-003"

    def test_extract_case_insensitive(self):
        """Test that extraction is case insensitive."""
        state = new_agentic_state("Show me cust-004")
        customer_id = _extract_customer_id(state)
        assert customer_id == "CUST-004"

    def test_extract_returns_none_if_not_found(self):
        """Test that extraction returns None if not found."""
        state = new_agentic_state("test")
        customer_id = _extract_customer_id(state)
        assert customer_id is None

    def test_extract_multiple_ids_returns_first(self):
        """Test that extraction returns first ID if multiple."""
        state = new_agentic_state("Compare CUST-001 and CUST-002")
        customer_id = _extract_customer_id(state)
        assert customer_id == "CUST-001"


class TestConvertMcpToToolCalls:
    """Test MCP to tool call conversion."""

    def test_convert_single_mcp_call(self):
        """Test converting single MCP call."""
        mcp_calls = [
            {
                "server": "customer_data",
                "tool": "search_customer_profile",
                "params": {"customer_id": "CUST-001"},
                "result": {"customer": {"id": "CUST-001"}},
            }
        ]
        tool_calls = _convert_mcp_to_tool_calls(mcp_calls)
        assert len(tool_calls) == 1
        assert tool_calls[0]["tool"] == "customer_data.search_customer_profile"
        assert tool_calls[0]["inputs"]["customer_id"] == "CUST-001"

    def test_convert_multiple_mcp_calls(self):
        """Test converting multiple MCP calls."""
        mcp_calls = [
            {
                "server": "customer_data",
                "tool": "search_customer_profile",
                "params": {"customer_id": "CUST-001"},
                "result": {},
            },
            {
                "server": "analytics",
                "tool": "run_sql_query",
                "params": {"sql": "SELECT * FROM customers"},
                "result": {},
            },
        ]
        tool_calls = _convert_mcp_to_tool_calls(mcp_calls)
        assert len(tool_calls) == 2

    def test_convert_empty_mcp_calls(self):
        """Test converting empty MCP calls."""
        tool_calls = _convert_mcp_to_tool_calls([])
        assert tool_calls == []

    def test_convert_preserves_params(self):
        """Test that conversion preserves parameters."""
        mcp_calls = [
            {
                "server": "analytics",
                "tool": "run_sql_query",
                "params": {"sql": "SELECT * FROM customers", "max_rows": 100},
                "result": {},
            }
        ]
        tool_calls = _convert_mcp_to_tool_calls(mcp_calls)
        assert tool_calls[0]["inputs"]["sql"] == "SELECT * FROM customers"
        assert tool_calls[0]["inputs"]["max_rows"] == 100

    def test_convert_preserves_results(self):
        """Test that conversion preserves results."""
        result = {"rows": [{"id": 1}]}
        mcp_calls = [
            {
                "server": "analytics",
                "tool": "run_sql_query",
                "params": {},
                "result": result,
            }
        ]
        tool_calls = _convert_mcp_to_tool_calls(mcp_calls)
        assert tool_calls[0]["outputs"] == result


class TestAdaptAgenticToNonagent:
    """Test agentic to nonagent adaptation."""

    def test_adapt_basic_state(self):
        """Test adapting basic agentic state."""
        state = new_agentic_state("test", user_id="user1")
        state["intent"] = "knowledge"
        state["active_agent"] = "knowledge"
        state["confidence"] = 0.9
        
        adapted = adapt_agentic_to_nonagent(state)
        
        assert adapted["request_id"] == state["request_id"]
        assert adapted["user_id"] == "user1"
        assert adapted["original_request"] == "test"
        assert adapted["intent"] == "knowledge"

    def test_adapt_maps_agent_names(self):
        """Test that adaptation maps agent names correctly."""
        state = new_agentic_state("test")
        state["active_agent"] = "knowledge"
        adapted = adapt_agentic_to_nonagent(state)
        assert adapted["routed_to"] == "level1_knowledge"

    def test_adapt_analytics_agent_mapping(self):
        """Test analytics agent mapping."""
        state = new_agentic_state("test")
        state["active_agent"] = "analytics"
        adapted = adapt_agentic_to_nonagent(state)
        assert adapted["routed_to"] == "level2_analytics"

    def test_adapt_recommendation_agent_mapping(self):
        """Test recommendation agent mapping."""
        state = new_agentic_state("test")
        state["active_agent"] = "recommendation"
        adapted = adapt_agentic_to_nonagent(state)
        assert adapted["routed_to"] == "level5_recommendation"

    def test_adapt_workflow_agent_mapping(self):
        """Test workflow agent mapping."""
        state = new_agentic_state("test")
        state["active_agent"] = "workflow"
        adapted = adapt_agentic_to_nonagent(state)
        assert adapted["routed_to"] == "level4_strategic"

    def test_adapt_action_agent_mapping(self):
        """Test action agent mapping."""
        state = new_agentic_state("test")
        state["active_agent"] = "action"
        adapted = adapt_agentic_to_nonagent(state)
        assert adapted["routed_to"] == "level3_functional"

    def test_adapt_extracts_customer_id(self):
        """Test that adaptation extracts customer ID."""
        state = new_agentic_state("Show me CUST-001")
        adapted = adapt_agentic_to_nonagent(state)
        assert adapted["customer_id"] == "CUST-001"

    def test_adapt_converts_mcp_calls(self):
        """Test that adaptation converts MCP calls."""
        state = new_agentic_state("test")
        state["mcp_calls"] = [
            {
                "server": "customer_data",
                "tool": "search_customer_profile",
                "params": {"customer_id": "CUST-001"},
                "result": {},
            }
        ]
        adapted = adapt_agentic_to_nonagent(state)
        assert len(adapted["tool_calls"]) == 1

    def test_adapt_preserves_error(self):
        """Test that adaptation preserves error."""
        state = new_agentic_state("test")
        state["error"] = "Some error"
        adapted = adapt_agentic_to_nonagent(state)
        assert adapted["error"] == "Some error"

    def test_adapt_preserves_audit_trail(self):
        """Test that adaptation preserves audit trail."""
        state = new_agentic_state("test")
        state["audit_trail"] = [{"agent": "orchestrator", "action": "classify"}]
        adapted = adapt_agentic_to_nonagent(state)
        assert len(adapted["audit_trail"]) == 1

    def test_adapt_has_all_required_fields(self):
        """Test that adapted state has all required fields."""
        state = new_agentic_state("test")
        adapted = adapt_agentic_to_nonagent(state)
        
        required_fields = [
            "request_id", "user_id", "original_request", "intent",
            "routed_to", "customer_id", "workflow_id", "messages",
            "tool_calls", "approval_status", "approval_payload",
            "error", "audit_trail", "confidence", "result"
        ]
        for field in required_fields:
            assert field in adapted


class TestCompareOutputs:
    """Test output comparison."""

    def test_compare_identical_dicts(self):
        """Test comparing identical dicts."""
        result1 = {"key": "value"}
        result2 = {"key": "value"}
        comparison = compare_outputs(result1, result2)
        assert comparison["match"] is True
        assert len(comparison["differences"]) == 0

    def test_compare_different_dicts(self):
        """Test comparing different dicts."""
        result1 = {"key": "value1"}
        result2 = {"key": "value2"}
        comparison = compare_outputs(result1, result2)
        assert comparison["match"] is False
        assert len(comparison["differences"]) > 0

    def test_compare_different_keys(self):
        """Test comparing dicts with different keys."""
        result1 = {"key1": "value"}
        result2 = {"key2": "value"}
        comparison = compare_outputs(result1, result2)
        assert comparison["match"] is False

    def test_compare_different_types(self):
        """Test comparing different types."""
        result1 = {"key": "value"}
        result2 = ["key", "value"]
        comparison = compare_outputs(result1, result2)
        assert comparison["match"] is False
        assert "Type mismatch" in comparison["differences"][0]

    def test_compare_identical_lists(self):
        """Test comparing identical lists."""
        result1 = [1, 2, 3]
        result2 = [1, 2, 3]
        comparison = compare_outputs(result1, result2)
        assert comparison["match"] is True

    def test_compare_different_length_lists(self):
        """Test comparing lists with different lengths."""
        result1 = [1, 2, 3]
        result2 = [1, 2]
        comparison = compare_outputs(result1, result2)
        assert comparison["match"] is False

    def test_compare_identical_strings(self):
        """Test comparing identical strings."""
        result1 = "test"
        result2 = "test"
        comparison = compare_outputs(result1, result2)
        assert comparison["match"] is True

    def test_compare_different_strings(self):
        """Test comparing different strings."""
        result1 = "test1"
        result2 = "test2"
        comparison = compare_outputs(result1, result2)
        assert comparison["match"] is False

    def test_compare_returns_comparison_dict(self):
        """Test that compare returns proper comparison dict."""
        result1 = {"key": "value"}
        result2 = {"key": "value"}
        comparison = compare_outputs(result1, result2)
        
        assert "match" in comparison
        assert "differences" in comparison
        assert "agentic_type" in comparison
        assert "nonagent_type" in comparison
