"""Output Adapter - ensures agentic outputs match nonagent format."""

from __future__ import annotations
from typing import Any
from agentic.agentic_state import AgenticState
from nonagentic.core.state import AgentState


def adapt_agentic_to_nonagent(agentic_state: AgenticState) -> AgentState:
    """Convert agentic state to nonagent state format for compatibility."""

    # Map agentic agent names to nonagent routing
    agent_mapping = {
        "knowledge": "level1_knowledge",
        "analytics": "level2_analytics",
        "recommendation": "level5_recommendation",
        "workflow": "level4_strategic",
        "action": "level3_functional",
    }

    routed_to = agent_mapping.get(agentic_state.get("active_agent", ""), "")

    # Build compatible state
    nonagent_state = {
        "request_id": agentic_state["request_id"],
        "user_id": agentic_state["user_id"],
        "original_request": agentic_state["original_request"],
        "intent": agentic_state["intent"],
        "routed_to": routed_to,
        "customer_id": _extract_customer_id(agentic_state),
        "workflow_id": agentic_state.get("session_id"),
        "messages": agentic_state["messages"],
        "tool_calls": _convert_mcp_to_tool_calls(agentic_state.get("mcp_calls", [])),
        "approval_status": None,
        "approval_payload": None,
        "error": agentic_state.get("error"),
        "audit_trail": agentic_state["audit_trail"],
        "confidence": agentic_state["confidence"],
        "result": agentic_state.get("final_result"),
    }

    return nonagent_state


def _extract_customer_id(state: AgenticState) -> str | None:
    """Extract customer ID from agentic state."""
    # Check user_profile
    if state.get("user_profile"):
        return state["user_profile"].get("customer_id")

    # Check intermediate results
    for result in state.get("intermediate_results", []):
        if "customer_id" in result.get("result", {}):
            return result["result"]["customer_id"]

    # Parse from request
    import re

    match = re.search(r"CUST-\d+", state["original_request"], re.IGNORECASE)
    return match.group(0).upper() if match else None


def _convert_mcp_to_tool_calls(mcp_calls: list[dict]) -> list[dict]:
    """Convert MCP calls to nonagent tool call format."""
    tool_calls = []
    for mcp_call in mcp_calls:
        tool_calls.append(
            {
                "tool": f"{mcp_call.get('server', 'unknown')}.{mcp_call.get('tool', 'unknown')}",
                "inputs": mcp_call.get("params", {}),
                "outputs": mcp_call.get("result", {}),
            }
        )
    return tool_calls


def compare_outputs(agentic_result: Any, nonagent_result: Any) -> dict:
    """Compare agentic and nonagent outputs for validation."""
    comparison = {
        "match": False,
        "differences": [],
        "agentic_type": type(agentic_result).__name__,
        "nonagent_type": type(nonagent_result).__name__,
    }

    # Type check
    if type(agentic_result) != type(nonagent_result):
        comparison["differences"].append(
            f"Type mismatch: {comparison['agentic_type']} vs {comparison['nonagent_type']}"
        )
        return comparison

    # Dict comparison
    if isinstance(agentic_result, dict) and isinstance(nonagent_result, dict):
        agentic_keys = set(agentic_result.keys())
        nonagent_keys = set(nonagent_result.keys())

        if agentic_keys != nonagent_keys:
            missing_in_agentic = nonagent_keys - agentic_keys
            missing_in_nonagent = agentic_keys - nonagent_keys
            if missing_in_agentic:
                comparison["differences"].append(
                    f"Missing in agentic: {missing_in_agentic}"
                )
            if missing_in_nonagent:
                comparison["differences"].append(
                    f"Missing in nonagent: {missing_in_nonagent}"
                )

        # Check common keys
        for key in agentic_keys & nonagent_keys:
            if agentic_result[key] != nonagent_result[key]:
                comparison["differences"].append(f"Value mismatch for '{key}'")

    # List comparison
    elif isinstance(agentic_result, list) and isinstance(nonagent_result, list):
        if len(agentic_result) != len(nonagent_result):
            comparison["differences"].append(
                f"Length mismatch: {len(agentic_result)} vs {len(nonagent_result)}"
            )

    # Direct comparison
    else:
        if agentic_result != nonagent_result:
            comparison["differences"].append("Direct value mismatch")

    comparison["match"] = len(comparison["differences"]) == 0
    return comparison
