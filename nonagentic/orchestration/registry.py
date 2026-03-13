from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AgentMeta:
    name: str
    node_id: str
    intent: str
    description: str
    tools: list[str]
    requires_customer_id: bool = False
    max_autonomy_level: str = "low"   # low | medium | high


REGISTRY: dict[str, AgentMeta] = {
    "level1_knowledge": AgentMeta(
        name="Knowledge Assistant",
        node_id="level1_knowledge",
        intent="informational",
        description="Semantic search over customer profiles, KYC records, and policy documents. Read-only. No actions.",
        tools=["search_customer_profile", "search_policy_docs", "get_kyc_status"],
        requires_customer_id=False,
        max_autonomy_level="low",
    ),
    "level2_analytics": AgentMeta(
        name="Analytics Copilot",
        node_id="level2_analytics",
        intent="analytical",
        description="Text-to-SQL, segmentation, KPI calculation, and churn/risk insights. Outputs require human review before action.",
        tools=["run_sql_query", "generate_segment", "visualise"],
        requires_customer_id=False,
        max_autonomy_level="low",
    ),
    "level3_functional": AgentMeta(
        name="Functional Agent",
        node_id="level3_functional",
        intent="action",
        description="Executes bounded actions: fetch profiles, recommend offers, draft/send messages, create cases. Enforces consent and KYC gates.",
        tools=["search_customer_profile", "get_kyc_status", "recommend_offer",
               "draft_email", "send_notification", "create_case",
               "log_audit_event", "request_human_approval"],
        requires_customer_id=True,
        max_autonomy_level="medium",
    ),
    "level4_strategic": AgentMeta(
        name="Strategic Orchestrator",
        node_id="level4_strategic",
        intent="strategic",
        description="Decomposes high-level business goals, coordinates L2/L3 agents, schedules campaigns, monitors KPIs, and incorporates feedback.",
        tools=["generate_segment", "recommend_offer", "schedule_campaign",
               "request_human_approval", "log_audit_event", "get_kpi_report", "record_campaign_outcome"],
        requires_customer_id=False,
        max_autonomy_level="high",
    ),
}


def get_agent(node_id: str) -> AgentMeta | None:
    return REGISTRY.get(node_id)


def list_agents() -> list[AgentMeta]:
    return list(REGISTRY.values())


def describe_all() -> str:
    lines = []
    for a in REGISTRY.values():
        lines.append(f"- [{a.intent}] {a.name}: {a.description}")
    return "\n".join(lines)
