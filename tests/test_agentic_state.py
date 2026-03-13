"""Tests for agentic state management."""

import pytest
from agentic.agentic_state import new_agentic_state, AgenticState, _append


def test_new_agentic_state_defaults():
    """Test creating new agentic state with defaults."""
    state = new_agentic_state("Test request")
    assert state["original_request"] == "Test request"
    assert state["user_id"] == "system"
    assert state["intent"] == "unknown"
    assert state["confidence"] == 0.0
    assert state["active_agent"] == ""
    assert state["agent_plan"] is None
    assert state["agent_history"] == []
    assert state["conversation_context"] is None
    assert state["user_profile"] is None
    assert state["mcp_calls"] == []
    assert state["intermediate_results"] == []
    assert state["final_result"] is None
    assert state["messages"] == []
    assert state["evaluation"] is None
    assert state["should_replan"] is False
    assert state["replan_count"] == 0
    assert state["error"] is None
    assert state["audit_trail"] == []


def test_new_agentic_state_with_user_id():
    """Test creating agentic state with custom user_id."""
    state = new_agentic_state("Test", user_id="user123")
    assert state["user_id"] == "user123"


def test_new_agentic_state_with_session_id():
    """Test creating agentic state with custom session_id."""
    state = new_agentic_state("Test", session_id="session456")
    assert state["session_id"] == "session456"


def test_new_agentic_state_generates_unique_ids():
    """Test that each state gets unique request_id and session_id."""
    state1 = new_agentic_state("Test")
    state2 = new_agentic_state("Test")
    assert state1["request_id"] != state2["request_id"]
    assert state1["session_id"] != state2["session_id"]


def test_agentic_state_type_dict():
    """Test that AgenticState is a TypedDict."""
    state = new_agentic_state("Test")
    assert isinstance(state, dict)
    assert "request_id" in state
    assert "user_id" in state
    assert "original_request" in state


def test_append_function():
    """Test the _append reducer function."""
    result = _append([1, 2], [3, 4])
    assert result == [1, 2, 3, 4]


def test_append_empty_lists():
    """Test _append with empty lists."""
    assert _append([], []) == []
    assert _append([1], []) == [1]
    assert _append([], [1]) == [1]


def test_state_mutability():
    """Test that state can be modified."""
    state = new_agentic_state("Test")
    state["intent"] = "knowledge"
    state["confidence"] = 0.95
    assert state["intent"] == "knowledge"
    assert state["confidence"] == 0.95


def test_state_list_fields_are_mutable():
    """Test that list fields in state can be modified."""
    state = new_agentic_state("Test")
    state["agent_history"].append("agent1")
    assert "agent1" in state["agent_history"]
    
    state["mcp_calls"].append({"server": "test"})
    assert len(state["mcp_calls"]) == 1


def test_state_dict_fields_are_mutable():
    """Test that dict fields in state can be modified."""
    state = new_agentic_state("Test")
    state["agent_plan"] = {"agents": ["knowledge"]}
    assert state["agent_plan"]["agents"] == ["knowledge"]


def test_state_with_all_parameters():
    """Test creating state with all custom parameters."""
    state = new_agentic_state(
        "Complex request",
        user_id="user789",
        session_id="session789"
    )
    assert state["original_request"] == "Complex request"
    assert state["user_id"] == "user789"
    assert state["session_id"] == "session789"
    assert state["request_id"] is not None
    assert len(state["request_id"]) > 0
