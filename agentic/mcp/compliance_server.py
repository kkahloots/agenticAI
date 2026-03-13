"""Compliance MCP Server - wraps compliance and guardrail tools."""

from nonagentic.tools.customer import search_customer_profile, get_kyc_status
from nonagentic.core.guardrails import guardrail_check as _guardrail


def check_marketing_consent(customer_id: str) -> dict:
    """Check if customer has marketing consent."""
    result = search_customer_profile(customer_id=customer_id)
    customer = result.get("customer")
    if not customer:
        return {
            "result": {"error": "customer_not_found", "consent": False},
            "tool_name": "check_marketing_consent",
            "execution_status": "failed",
            "audit": {"customer_id": customer_id}
        }
    
    consent = customer.get("consent_flags", {}).get("marketing", False)
    return {
        "result": {"customer_id": customer_id, "marketing_consent": consent},
        "tool_name": "check_marketing_consent",
        "execution_status": "success",
        "audit": {"customer_id": customer_id, "consent": consent}
    }


def check_identity_gate(customer_id: str) -> dict:
    """Check identity verification status."""
    result = get_kyc_status(customer_id)
    if result.get("error"):
        return {
            "result": result,
            "tool_name": "check_identity_gate",
            "execution_status": "failed",
            "audit": {"customer_id": customer_id}
        }
    
    status = result.get("identity_status") or result.get("kyc_status")
    passed = status in ("verified", "pending")
    
    return {
        "result": {
            "customer_id": customer_id,
            "identity_status": status,
            "gate_passed": passed,
            "requires_action": not passed
        },
        "tool_name": "check_identity_gate",
        "execution_status": "success",
        "audit": {"customer_id": customer_id, "status": status}
    }


def guardrail_check(text: str, request_id: str) -> dict:
    """Run guardrail check on text."""
    result = _guardrail(text, request_id=request_id)
    return {
        "result": {
            "passed": result.passed,
            "revised_text": result.revised_text,
            "violations": result.violations
        },
        "tool_name": "guardrail_check",
        "execution_status": "success",
        "audit": {"request_id": request_id, "violations_count": len(result.violations)}
    }


def redact_pii(text: str) -> dict:
    """Redact PII from text."""
    # Use guardrail check for PII redaction
    result = _guardrail(text, request_id="pii-redact")
    return {
        "result": {"redacted_text": result.revised_text},
        "tool_name": "redact_pii",
        "execution_status": "success",
        "audit": {"violations_found": len(result.violations)}
    }
