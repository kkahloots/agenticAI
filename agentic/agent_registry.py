"""Agentic Agent Registry - metadata and discovery for autonomous agents."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class AgenticAgentMeta:
    """Metadata for an agentic agent."""
    agent_id: str
    name: str
    purpose: str
    capabilities: list[str]
    mcp_servers: list[str]
    input_schema: dict
    output_schema: dict
    decision_rules: list[str] = field(default_factory=list)
    memory_access: list[str] = field(default_factory=list)
    autonomy_level: str = "medium"  # low | medium | high


# Agentic Agent Registry
AGENTIC_REGISTRY: dict[str, AgenticAgentMeta] = {
    "orchestrator": AgenticAgentMeta(
        agent_id="orchestrator",
        name="Orchestrator Agent",
        purpose="Detect user intent, select agents, build execution plans, invoke workflows",
        capabilities=["intent_detection", "agent_selection", "plan_building", "workflow_invocation"],
        mcp_servers=[],
        input_schema={"request": "string", "user_id": "string"},
        output_schema={"intent": "string", "selected_agents": "array", "plan": "object"},
        decision_rules=[
            "IF knowledge_retrieval THEN knowledge_agent",
            "IF analytics THEN analytics_agent",
            "IF recommendation THEN recommendation_agent",
            "IF workflow_execution THEN workflow_agent"
        ],
        memory_access=["conversation", "user_profile", "interaction"],
        autonomy_level="high"
    ),
    
    "knowledge": AgenticAgentMeta(
        agent_id="knowledge",
        name="Knowledge Agent",
        purpose="Retrieve and synthesize information from knowledge bases",
        capabilities=["semantic_search", "document_retrieval", "information_synthesis"],
        mcp_servers=["customer_data", "product_catalog"],
        input_schema={"query": "string", "context": "object"},
        output_schema={"answer": "string", "sources": "array", "confidence": "float"},
        decision_rules=[
            "IF customer_query THEN customer_data_server",
            "IF product_query THEN product_catalog_server"
        ],
        memory_access=["conversation", "interaction"],
        autonomy_level="low"
    ),
    
    "analytics": AgenticAgentMeta(
        agent_id="analytics",
        name="Analytics Agent",
        purpose="Perform data analysis, segmentation, and generate insights",
        capabilities=["sql_generation", "segmentation", "kpi_calculation", "trend_analysis"],
        mcp_servers=["analytics"],
        input_schema={"query": "string", "parameters": "object"},
        output_schema={"results": "object", "insights": "array", "visualizations": "array"},
        decision_rules=[
            "IF sql_query THEN analytics_server.run_sql_query",
            "IF segmentation THEN analytics_server.generate_segment"
        ],
        memory_access=["conversation", "agent_observation"],
        autonomy_level="medium"
    ),
    
    "recommendation": AgenticAgentMeta(
        agent_id="recommendation",
        name="Recommendation Agent",
        purpose="Generate personalized recommendations using ML models",
        capabilities=["collaborative_filtering", "content_based", "hybrid_recommendation"],
        mcp_servers=["recommendation", "customer_data", "product_catalog"],
        input_schema={"customer_id": "string", "context": "object", "top_k": "integer"},
        output_schema={"recommendations": "array", "explanations": "array", "confidence": "float"},
        decision_rules=[
            "IF cold_start THEN use_popularity_based",
            "IF sufficient_history THEN use_collaborative_filtering"
        ],
        memory_access=["user_profile", "interaction"],
        autonomy_level="medium"
    ),
    
    "workflow": AgenticAgentMeta(
        agent_id="workflow",
        name="Workflow Agent",
        purpose="Execute multi-step workflows and coordinate sub-tasks",
        capabilities=["task_decomposition", "workflow_execution", "sub_agent_coordination"],
        mcp_servers=["crm", "analytics", "customer_data"],
        input_schema={"goal": "string", "constraints": "object"},
        output_schema={"workflow_id": "string", "steps": "array", "status": "string"},
        decision_rules=[
            "IF complex_goal THEN decompose_into_subtasks",
            "IF requires_approval THEN request_human_approval"
        ],
        memory_access=["conversation", "interaction", "agent_observation"],
        autonomy_level="high"
    ),
    
    "action": AgenticAgentMeta(
        agent_id="action",
        name="Action Agent",
        purpose="Execute actions on external systems with safety checks",
        capabilities=["notification_sending", "case_creation", "campaign_execution"],
        mcp_servers=["crm", "customer_data"],
        input_schema={"action_type": "string", "parameters": "object", "customer_id": "string"},
        output_schema={"action_id": "string", "status": "string", "result": "object"},
        decision_rules=[
            "IF high_risk THEN require_approval",
            "IF identity_unverified THEN block_action"
        ],
        memory_access=["interaction", "agent_observation"],
        autonomy_level="medium"
    ),
    
    "evaluation": AgenticAgentMeta(
        agent_id="evaluation",
        name="Evaluation Agent",
        purpose="Evaluate outcomes, provide feedback, trigger replanning",
        capabilities=["outcome_evaluation", "feedback_generation", "replan_triggering"],
        mcp_servers=["analytics"],
        input_schema={"workflow_id": "string", "expected_outcome": "object", "actual_outcome": "object"},
        output_schema={"evaluation": "object", "feedback": "string", "should_replan": "boolean"},
        decision_rules=[
            "IF deviation_high THEN trigger_replan",
            "IF success THEN record_positive_observation"
        ],
        memory_access=["interaction", "agent_observation"],
        autonomy_level="high"
    ),
    
    "memory": AgenticAgentMeta(
        agent_id="memory",
        name="Memory Agent",
        purpose="Manage conversation context and long-term user memory",
        capabilities=["context_management", "memory_retrieval", "memory_update"],
        mcp_servers=[],
        input_schema={"operation": "string", "data": "object"},
        output_schema={"status": "string", "data": "object"},
        decision_rules=[
            "IF new_preference THEN update_user_profile",
            "IF important_interaction THEN record_to_long_term"
        ],
        memory_access=["conversation", "user_profile", "interaction", "agent_observation"],
        autonomy_level="low"
    )
}


def get_agentic_agent(agent_id: str) -> AgenticAgentMeta | None:
    """Get agent metadata by ID."""
    return AGENTIC_REGISTRY.get(agent_id)


def list_agentic_agents() -> list[AgenticAgentMeta]:
    """List all agentic agents."""
    return list(AGENTIC_REGISTRY.values())


def describe_agentic_agents() -> str:
    """Describe all agentic agents."""
    lines = []
    for agent in AGENTIC_REGISTRY.values():
        lines.append(f"- [{agent.agent_id}] {agent.name}: {agent.purpose}")
    return "\n".join(lines)
