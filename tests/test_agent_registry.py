"""Tests for agent registry."""

import pytest
from agentic.agent_registry import (
    AgenticAgentMeta,
    AGENTIC_REGISTRY,
    get_agentic_agent,
    list_agentic_agents,
    describe_agentic_agents,
)


class TestAgenticAgentMeta:
    """Test AgenticAgentMeta dataclass."""

    def test_create_agent_meta(self):
        """Test creating agent metadata."""
        meta = AgenticAgentMeta(
            agent_id="test_agent",
            name="Test Agent",
            purpose="Test purpose",
            capabilities=["cap1", "cap2"],
            mcp_servers=["server1"],
            input_schema={"input": "string"},
            output_schema={"output": "string"},
        )
        assert meta.agent_id == "test_agent"
        assert meta.name == "Test Agent"
        assert meta.purpose == "Test purpose"
        assert meta.capabilities == ["cap1", "cap2"]
        assert meta.mcp_servers == ["server1"]

    def test_agent_meta_defaults(self):
        """Test agent metadata defaults."""
        meta = AgenticAgentMeta(
            agent_id="test",
            name="Test",
            purpose="Test",
            capabilities=[],
            mcp_servers=[],
            input_schema={},
            output_schema={},
        )
        assert meta.decision_rules == []
        assert meta.memory_access == []
        assert meta.autonomy_level == "medium"

    def test_agent_meta_custom_autonomy(self):
        """Test agent metadata with custom autonomy level."""
        meta = AgenticAgentMeta(
            agent_id="test",
            name="Test",
            purpose="Test",
            capabilities=[],
            mcp_servers=[],
            input_schema={},
            output_schema={},
            autonomy_level="high",
        )
        assert meta.autonomy_level == "high"


class TestAgenticRegistry:
    """Test agentic agent registry."""

    def test_registry_has_orchestrator(self):
        """Test that registry has orchestrator agent."""
        assert "orchestrator" in AGENTIC_REGISTRY
        agent = AGENTIC_REGISTRY["orchestrator"]
        assert agent.agent_id == "orchestrator"
        assert agent.name == "Orchestrator Agent"

    def test_registry_has_knowledge_agent(self):
        """Test that registry has knowledge agent."""
        assert "knowledge" in AGENTIC_REGISTRY
        agent = AGENTIC_REGISTRY["knowledge"]
        assert agent.agent_id == "knowledge"

    def test_registry_has_analytics_agent(self):
        """Test that registry has analytics agent."""
        assert "analytics" in AGENTIC_REGISTRY
        agent = AGENTIC_REGISTRY["analytics"]
        assert agent.agent_id == "analytics"

    def test_registry_has_recommendation_agent(self):
        """Test that registry has recommendation agent."""
        assert "recommendation" in AGENTIC_REGISTRY
        agent = AGENTIC_REGISTRY["recommendation"]
        assert agent.agent_id == "recommendation"

    def test_registry_has_workflow_agent(self):
        """Test that registry has workflow agent."""
        assert "workflow" in AGENTIC_REGISTRY
        agent = AGENTIC_REGISTRY["workflow"]
        assert agent.agent_id == "workflow"

    def test_registry_has_action_agent(self):
        """Test that registry has action agent."""
        assert "action" in AGENTIC_REGISTRY
        agent = AGENTIC_REGISTRY["action"]
        assert agent.agent_id == "action"

    def test_registry_has_evaluation_agent(self):
        """Test that registry has evaluation agent."""
        assert "evaluation" in AGENTIC_REGISTRY
        agent = AGENTIC_REGISTRY["evaluation"]
        assert agent.agent_id == "evaluation"

    def test_registry_has_memory_agent(self):
        """Test that registry has memory agent."""
        assert "memory" in AGENTIC_REGISTRY
        agent = AGENTIC_REGISTRY["memory"]
        assert agent.agent_id == "memory"

    def test_all_agents_have_required_fields(self):
        """Test that all agents have required fields."""
        for agent_id, agent in AGENTIC_REGISTRY.items():
            assert agent.agent_id is not None
            assert agent.name is not None
            assert agent.purpose is not None
            assert isinstance(agent.capabilities, list)
            assert isinstance(agent.mcp_servers, list)
            assert isinstance(agent.input_schema, dict)
            assert isinstance(agent.output_schema, dict)

    def test_all_agents_have_autonomy_level(self):
        """Test that all agents have autonomy level."""
        for agent_id, agent in AGENTIC_REGISTRY.items():
            assert agent.autonomy_level in ["low", "medium", "high"]

    def test_orchestrator_has_high_autonomy(self):
        """Test that orchestrator has high autonomy."""
        agent = AGENTIC_REGISTRY["orchestrator"]
        assert agent.autonomy_level == "high"

    def test_knowledge_agent_has_low_autonomy(self):
        """Test that knowledge agent has low autonomy."""
        agent = AGENTIC_REGISTRY["knowledge"]
        assert agent.autonomy_level == "low"


class TestGetAgenticAgent:
    """Test get_agentic_agent function."""

    def test_get_existing_agent(self):
        """Test getting existing agent."""
        agent = get_agentic_agent("orchestrator")
        assert agent is not None
        assert agent.agent_id == "orchestrator"

    def test_get_nonexistent_agent(self):
        """Test getting non-existent agent returns None."""
        agent = get_agentic_agent("nonexistent")
        assert agent is None

    def test_get_all_agents(self):
        """Test getting all agents."""
        for agent_id in AGENTIC_REGISTRY.keys():
            agent = get_agentic_agent(agent_id)
            assert agent is not None
            assert agent.agent_id == agent_id


class TestListAgenticAgents:
    """Test list_agentic_agents function."""

    def test_list_returns_list(self):
        """Test that list_agentic_agents returns a list."""
        agents = list_agentic_agents()
        assert isinstance(agents, list)

    def test_list_has_all_agents(self):
        """Test that list has all agents."""
        agents = list_agentic_agents()
        agent_ids = [a.agent_id for a in agents]
        assert len(agent_ids) == len(AGENTIC_REGISTRY)
        for agent_id in AGENTIC_REGISTRY.keys():
            assert agent_id in agent_ids

    def test_list_returns_agent_meta_objects(self):
        """Test that list returns AgenticAgentMeta objects."""
        agents = list_agentic_agents()
        for agent in agents:
            assert isinstance(agent, AgenticAgentMeta)


class TestDescribeAgenticAgents:
    """Test describe_agentic_agents function."""

    def test_describe_returns_string(self):
        """Test that describe_agentic_agents returns a string."""
        description = describe_agentic_agents()
        assert isinstance(description, str)

    def test_describe_contains_all_agents(self):
        """Test that description contains all agents."""
        description = describe_agentic_agents()
        for agent_id in AGENTIC_REGISTRY.keys():
            assert agent_id in description

    def test_describe_contains_agent_names(self):
        """Test that description contains agent names."""
        description = describe_agentic_agents()
        for agent in AGENTIC_REGISTRY.values():
            assert agent.name in description

    def test_describe_contains_agent_purposes(self):
        """Test that description contains agent purposes."""
        description = describe_agentic_agents()
        for agent in AGENTIC_REGISTRY.values():
            assert agent.purpose in description

    def test_describe_format(self):
        """Test that description has proper format."""
        description = describe_agentic_agents()
        lines = description.split("\n")
        assert len(lines) == len(AGENTIC_REGISTRY)
        for line in lines:
            assert line.startswith("- [")
