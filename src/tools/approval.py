from __future__ import annotations

import uuid
from datetime import datetime, timezone

# In tests / dev mode, auto-approve unless overridden
_AUTO_APPROVE: bool = True
_PENDING: dict[str, dict] = {}


def request_human_approval(
    workflow_id: str,
    action_description: str,
    risk_level: str = "medium",
    timeout_minutes: int = 60,
) -> dict:
    approval_id = str(uuid.uuid4())
    record = {
        "approval_id": approval_id,
        "workflow_id": workflow_id,
        "action_description": action_description,
        "risk_level": risk_level,
        "timeout_minutes": timeout_minutes,
        "requested_at": datetime.now(timezone.utc).isoformat(),
    }
    _PENDING[approval_id] = record

    if _AUTO_APPROVE:
        return {
            "approved": True,
            "approver_id": "auto-approve",
            "decision_time": datetime.now(timezone.utc).isoformat(),
            "notes": "Auto-approved in dev mode",
        }

    # Production: return pending — caller must poll or use interrupt
    return {
        "approved": False,
        "approver_id": None,
        "decision_time": None,
        "notes": "Awaiting human decision",
        "approval_id": approval_id,
    }


def set_auto_approve(value: bool) -> None:
    """Toggle auto-approve for testing."""
    global _AUTO_APPROVE
    _AUTO_APPROVE = value
