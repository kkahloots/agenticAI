"""Functional MCP Server - wraps functional workflow tools."""

from nonagentic.tools.leads import enrich_customer as _enrich
from nonagentic.tools.functional import create_case as _create_case


def enrich_customer(customer_id: str) -> dict:
    """Enrich customer with multi-source data."""
    result = _enrich(customer_id)
    return {
        "result": result,
        "tool_name": "enrich_customer",
        "execution_status": "success" if not result.get("error") else "failed",
        "audit": {"customer_id": customer_id}
    }


def create_case(customer_id: str, case_type: str, description: str, priority: str = "medium") -> dict:
    """Create support/remediation case."""
    result = _create_case(customer_id, case_type, description, priority=priority)
    return {
        "result": result,
        "tool_name": "create_case",
        "execution_status": "success",
        "audit": {"customer_id": customer_id, "case_type": case_type, "priority": priority}
    }


def build_campaign_execution_plan(plan_data: dict) -> dict:
    """Build campaign execution plan from bulk recommendation data."""
    # This wraps the bulk_recommend output into an execution plan format
    return {
        "result": {
            "plan": plan_data,
            "status": "ready",
            "requires_approval": plan_data.get("bulk_approval_needed", False)
        },
        "tool_name": "build_campaign_execution_plan",
        "execution_status": "success",
        "audit": {"prospects": plan_data.get("total_prospects", 0)}
    }
