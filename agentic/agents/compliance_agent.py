"""Compliance Agent - handles consent, identity checks, and guardrails."""

from typing import Optional
from agentic.mcp import compliance_server
from agentic.registry.tool_registry import get_registry
from agentic.memory.memory_manager import get_memory


class ComplianceAgent:
    """Handles compliance checks."""
    
    def __init__(self):
        self.registry = get_registry()
        self.memory = get_memory()
    
    def execute(self, task: dict, request_id: str) -> dict:
        """Execute compliance task."""
        action = task.get("action", "")
        
        if "consent" in action.lower():
            return self._check_consent(task, request_id)
        elif "identity" in action.lower() or "kyc" in action.lower():
            return self._check_identity(task, request_id)
        elif "guardrail" in action.lower():
            return self._guardrail_check(task, request_id)
        elif "redact" in action.lower() or "pii" in action.lower():
            return self._redact_pii(task, request_id)
        else:
            return {"error": "unknown_action", "action": action}
    
    def _check_consent(self, task: dict, request_id: str) -> dict:
        """Check marketing consent."""
        customer_id = task.get("customer_id")
        if not customer_id:
            return {"error": "missing_customer_id"}
        
        result = compliance_server.check_marketing_consent(customer_id)
        decision = {
            "customer_id": customer_id,
            "check_type": "marketing_consent",
            "passed": result.get("result", {}).get("marketing_consent", False)
        }
        self.memory.record_compliance_decision(request_id, decision)
        self.memory.record_tool_usage(request_id, "check_marketing_consent", task, result)
        return result
    
    def _check_identity(self, task: dict, request_id: str) -> dict:
        """Check identity verification."""
        customer_id = task.get("customer_id")
        if not customer_id:
            return {"error": "missing_customer_id"}
        
        result = compliance_server.check_identity_gate(customer_id)
        decision = {
            "customer_id": customer_id,
            "check_type": "identity_gate",
            "passed": result.get("result", {}).get("gate_passed", False)
        }
        self.memory.record_compliance_decision(request_id, decision)
        self.memory.record_tool_usage(request_id, "check_identity_gate", task, result)
        return result
    
    def _guardrail_check(self, task: dict, request_id: str) -> dict:
        """Run guardrail check."""
        text = task.get("text", "")
        if not text:
            return {"error": "missing_text"}
        
        result = compliance_server.guardrail_check(text, request_id)
        decision = {
            "check_type": "guardrail",
            "passed": result.get("result", {}).get("passed", True),
            "violations": len(result.get("result", {}).get("violations", []))
        }
        self.memory.record_compliance_decision(request_id, decision)
        self.memory.record_tool_usage(request_id, "guardrail_check", task, result)
        return result
    
    def _redact_pii(self, task: dict, request_id: str) -> dict:
        """Redact PII from text."""
        text = task.get("text", "")
        if not text:
            return {"error": "missing_text"}
        
        result = compliance_server.redact_pii(text)
        self.memory.record_tool_usage(request_id, "redact_pii", task, result)
        return result


def create_compliance_agent() -> ComplianceAgent:
    """Create compliance agent instance."""
    return ComplianceAgent()
