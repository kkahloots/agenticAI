"""Customer MCP Server - wraps customer data tools."""

from typing import Optional
from nonagentic.tools.customer import search_customer_profile as _search, get_kyc_status as _kyc


def search_customer_profile(customer_id: Optional[str] = None, full_name: Optional[str] = None, country: Optional[str] = None) -> dict:
    """Search for customer profile."""
    result = _search(customer_id=customer_id, full_name=full_name, country=country)
    return {
        "result": result,
        "tool_name": "search_customer_profile",
        "execution_status": "success" if result.get("customer") else "not_found",
        "audit": {"customer_id": customer_id, "full_name": full_name}
    }


def get_kyc_status(customer_id: str) -> dict:
    """Get KYC/identity status for customer."""
    result = _kyc(customer_id)
    return {
        "result": result,
        "tool_name": "get_kyc_status",
        "execution_status": "success" if not result.get("error") else "failed",
        "audit": {"customer_id": customer_id}
    }


def get_customer_attributes(customer_id: str) -> dict:
    """Get customer attributes (segment, engagement, etc)."""
    result = _search(customer_id=customer_id)
    customer = result.get("customer")
    if not customer:
        return {
            "result": {"error": "customer_not_found"},
            "tool_name": "get_customer_attributes",
            "execution_status": "failed",
            "audit": {"customer_id": customer_id}
        }
    
    attributes = {
        "customer_id": customer["customer_id"],
        "segment": customer.get("segment"),
        "engagement_score": customer.get("engagement_score"),
        "lifetime_value": customer.get("lifetime_value"),
        "fraud_score": customer.get("fraud_score"),
        "return_risk": customer.get("return_risk"),
        "purchase_categories": customer.get("purchase_categories", [])
    }
    
    return {
        "result": attributes,
        "tool_name": "get_customer_attributes",
        "execution_status": "success",
        "audit": {"customer_id": customer_id}
    }


def get_customer_segment(customer_id: str) -> dict:
    """Get customer segment."""
    result = _search(customer_id=customer_id)
    customer = result.get("customer")
    if not customer:
        return {
            "result": {"error": "customer_not_found"},
            "tool_name": "get_customer_segment",
            "execution_status": "failed",
            "audit": {"customer_id": customer_id}
        }
    
    return {
        "result": {"segment": customer.get("segment")},
        "tool_name": "get_customer_segment",
        "execution_status": "success",
        "audit": {"customer_id": customer_id}
    }
