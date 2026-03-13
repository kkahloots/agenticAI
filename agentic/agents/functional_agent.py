"""Functional Agent - coordinates functional workflows."""

from typing import Optional
from agentic.mcp import customer_server, notification_server, functional_server
from agentic.registry.tool_registry import get_registry
from agentic.memory.memory_manager import get_memory


class FunctionalAgent:
    """Handles functional workflows like enrichment, notifications, case creation."""
    
    def __init__(self):
        self.registry = get_registry()
        self.memory = get_memory()
    
    def execute(self, task: dict, request_id: str) -> dict:
        """Execute functional task."""
        action = task.get("action", "")
        
        if "enrich" in action.lower():
            return self._enrich_customer(task, request_id)
        elif "notif" in action.lower() or "send" in action.lower():
            return self._send_notification(task, request_id)
        elif "draft" in action.lower():
            return self._draft_message(task, request_id)
        elif "case" in action.lower():
            return self._create_case(task, request_id)
        elif "campaign" in action.lower() and "plan" in action.lower():
            return self._build_campaign_plan(task, request_id)
        else:
            return {"error": "unknown_action", "action": action}
    
    def _enrich_customer(self, task: dict, request_id: str) -> dict:
        """Enrich customer profile."""
        customer_id = task.get("customer_id")
        if not customer_id:
            return {"error": "missing_customer_id"}
        
        result = functional_server.enrich_customer(customer_id)
        self.memory.record_tool_usage(request_id, "enrich_customer", {"customer_id": customer_id}, result)
        return result
    
    def _send_notification(self, task: dict, request_id: str) -> dict:
        """Send notification."""
        customer_id = task.get("customer_id")
        channel = task.get("channel", "email")
        content = task.get("content", {})
        dry_run = task.get("dry_run", False)
        
        if not customer_id:
            return {"error": "missing_customer_id"}
        
        result = notification_server.send_notification(customer_id, channel, content, dry_run=dry_run)
        self.memory.record_tool_usage(request_id, "send_notification", task, result)
        return result
    
    def _draft_message(self, task: dict, request_id: str) -> dict:
        """Draft message."""
        customer_id = task.get("customer_id")
        template_id = task.get("template_id", "T-PROMO-01")
        variables = task.get("variables", {})
        
        if not customer_id:
            return {"error": "missing_customer_id"}
        
        result = notification_server.draft_email(customer_id, template_id, variables=variables)
        self.memory.record_tool_usage(request_id, "draft_email", task, result)
        return result
    
    def _create_case(self, task: dict, request_id: str) -> dict:
        """Create support case."""
        customer_id = task.get("customer_id")
        case_type = task.get("case_type", "general")
        description = task.get("description", "")
        priority = task.get("priority", "medium")
        
        if not customer_id:
            return {"error": "missing_customer_id"}
        
        result = functional_server.create_case(customer_id, case_type, description, priority=priority)
        self.memory.record_tool_usage(request_id, "create_case", task, result)
        return result
    
    def _build_campaign_plan(self, task: dict, request_id: str) -> dict:
        """Build campaign execution plan."""
        plan_data = task.get("plan_data", {})
        result = functional_server.build_campaign_execution_plan(plan_data)
        self.memory.record_tool_usage(request_id, "build_campaign_execution_plan", task, result)
        return result


def create_functional_agent() -> FunctionalAgent:
    """Create functional agent instance."""
    return FunctionalAgent()
