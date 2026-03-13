"""Agentic State - state management for agentic AI workflows."""
from __future__ import annotations
import uuid
from typing import Annotated, Any, Optional
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
import operator


def _append(a: list, b: list) -> list:
    return a + b


class AgenticState(TypedDict):
    """State for agentic AI workflows."""
    # Core identifiers
    request_id: str
    user_id: str
    session_id: str
    
    # Request and intent
    original_request: str
    intent: str
    confidence: float
    
    # Agent coordination
    active_agent: str
    agent_plan: Optional[dict]
    agent_history: Annotated[list[str], _append]
    
    # Memory context
    conversation_context: Optional[dict]
    user_profile: Optional[dict]
    
    # MCP tool interactions
    mcp_calls: Annotated[list[dict], _append]
    
    # Results and outputs
    intermediate_results: Annotated[list[dict], _append]
    final_result: Optional[Any]
    
    # Messages
    messages: Annotated[list[BaseMessage], operator.add]
    
    # Evaluation and feedback
    evaluation: Optional[dict]
    should_replan: bool
    replan_count: int
    
    # Error handling
    error: Optional[str]
    
    # Audit
    audit_trail: Annotated[list[dict], _append]


def new_agentic_state(request: str, user_id: str = "system", session_id: str | None = None) -> AgenticState:
    """Create a new agentic state."""
    return AgenticState(
        request_id=str(uuid.uuid4()),
        user_id=user_id,
        session_id=session_id or str(uuid.uuid4()),
        original_request=request,
        intent="unknown",
        confidence=0.0,
        active_agent="",
        agent_plan=None,
        agent_history=[],
        conversation_context=None,
        user_profile=None,
        mcp_calls=[],
        intermediate_results=[],
        final_result=None,
        messages=[],
        evaluation=None,
        should_replan=False,
        replan_count=0,
        error=None,
        audit_trail=[]
    )
