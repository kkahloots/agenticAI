"""Notification MCP Server - wraps notification and messaging tools."""

from typing import Optional
from nonagentic.tools.functional import draft_email as _draft, send_notification as _send


def draft_email(customer_id: str, template_id: str, variables: Optional[dict] = None, language: Optional[str] = None) -> dict:
    """Draft email notification."""
    result = _draft(customer_id, template_id, variables=variables, language=language)
    return {
        "result": result,
        "tool_name": "draft_email",
        "execution_status": "success" if not result.get("error") else "failed",
        "audit": {"customer_id": customer_id, "template_id": template_id}
    }


def send_notification(customer_id: str, channel: str, content: dict, dry_run: bool = False) -> dict:
    """Send notification via channel."""
    result = _send(customer_id, channel, content, dry_run=dry_run)
    return {
        "result": result,
        "tool_name": "send_notification",
        "execution_status": result.get("status", "unknown"),
        "audit": {"customer_id": customer_id, "channel": channel, "dry_run": dry_run}
    }


def simulate_notification(customer_id: str, channel: str, content: dict) -> dict:
    """Simulate notification without actually sending."""
    result = _send(customer_id, channel, content, dry_run=True)
    return {
        "result": result,
        "tool_name": "simulate_notification",
        "execution_status": result.get("status", "unknown"),
        "audit": {"customer_id": customer_id, "channel": channel, "simulated": True}
    }
