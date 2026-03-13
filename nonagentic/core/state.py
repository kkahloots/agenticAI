from __future__ import annotations

import uuid
from typing import Annotated, Any, Optional
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage
import operator


def _append(a: list, b: list) -> list:
    return a + b


class AgentState(TypedDict):
    request_id: str
    user_id: str
    original_request: str
    intent: str                          # informational | analytical | action | strategic | unknown
    routed_to: str
    customer_id: Optional[str]
    workflow_id: Optional[str]
    messages: Annotated[list[BaseMessage], operator.add]
    tool_calls: Annotated[list[dict], _append]
    approval_status: Optional[str]       # pending | approved | rejected
    approval_payload: Optional[dict]
    error: Optional[str]
    audit_trail: Annotated[list[dict], _append]
    confidence: float
    result: Optional[Any]


def new_state(request: str, user_id: str = "system") -> AgentState:
    return AgentState(
        request_id=str(uuid.uuid4()),
        user_id=user_id,
        original_request=request,
        intent="unknown",
        routed_to="",
        customer_id=None,
        workflow_id=None,
        messages=[],
        tool_calls=[],
        approval_status=None,
        approval_payload=None,
        error=None,
        audit_trail=[],
        confidence=0.0,
        result=None,
    )
