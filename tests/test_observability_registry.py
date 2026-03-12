import pytest
from src.core.observability import (
    node_trace,
    record_tokens,
    get_event_log,
    clear_event_log,
    _token_accumulator,
)
from src.orchestration.registry import get_agent, list_agents, describe_all


def test_observability_node_trace_success():
    clear_event_log()
    
    @node_trace("test_node")
    def dummy_node(state):
        return {"result": "ok", "tool_calls": []}
    
    result = dummy_node({"request_id": "req-123"})
    assert result["result"] == "ok"
    
    events = get_event_log()
    assert len(events) == 2
    assert events[0]["event"] == "node_start"
    assert events[1]["event"] == "node_end"
    assert events[1]["tokens_used"] >= 0


def test_observability_node_trace_with_error():
    clear_event_log()
    
    @node_trace("error_node")
    def failing_node(state):
        raise ValueError("test error")
    
    result = failing_node({"request_id": "req-456"})
    assert "error" in result
    
    events = get_event_log()
    end_event = [e for e in events if e["event"] == "node_end"][0]
    assert end_event["error"] == "test error"


def test_record_tokens_accumulates():
    _token_accumulator.clear()
    record_tokens("req-1", 100)
    record_tokens("req-1", 50)
    assert _token_accumulator["req-1"] == 150


def test_clear_event_log():
    clear_event_log()
    assert len(get_event_log()) == 0


def test_registry_get_agent():
    agent = get_agent("level1_knowledge")
    assert agent is not None
    assert agent.name == "Knowledge Assistant"
    assert agent.intent == "informational"


def test_registry_get_agent_not_found():
    agent = get_agent("nonexistent")
    assert agent is None


def test_registry_list_agents():
    agents = list_agents()
    assert len(agents) >= 4
    assert any(a.node_id == "level1_knowledge" for a in agents)


def test_registry_describe_all():
    description = describe_all()
    assert "Knowledge Assistant" in description
    assert "Analytics Copilot" in description
    assert "informational" in description
