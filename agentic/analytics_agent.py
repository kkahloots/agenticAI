"""Analytics Agent - performs data analysis and generates insights."""

from __future__ import annotations
import re
from langchain_core.messages import AIMessage
from agentic.agentic_state import AgenticState
from mcp_servers.analytics_server import AnalyticsServer
from memory.memory_manager import memory_manager
from nonagentic.tools.audit import log_audit_event


def analytics_agent(state: AgenticState) -> dict:
    """Analytics agent - perform data analysis."""
    request = state["original_request"]

    # Initialize MCP server
    analytics_server = AnalyticsServer()

    result = {}
    mcp_calls = []

    # Determine analytics operation - check SQL first to avoid keyword conflicts
    sql = _extract_sql_query(request)

    if sql:
        # SQL query provided
        result = analytics_server.invoke_tool("run_sql_query", sql=sql, max_rows=100)
        mcp_calls.append(
            {
                "server": "analytics",
                "tool": "run_sql_query",
                "params": {"sql": sql},
                "result": result,
            }
        )
    elif any(w in request.lower() for w in ["segment", "cluster", "group"]):
        # Segmentation
        filters = _extract_filters(request)
        result = analytics_server.invoke_tool(
            "generate_segment", filters=filters, algorithm="rules"
        )
        mcp_calls.append(
            {
                "server": "analytics",
                "tool": "generate_segment",
                "params": {"filters": filters, "algorithm": "rules"},
                "result": result,
            }
        )
    else:
        # Default: use a simple query
        sql = "SELECT segment, COUNT(*) as count FROM customers GROUP BY segment"
        result = analytics_server.invoke_tool("run_sql_query", sql=sql, max_rows=100)
        mcp_calls.append(
            {
                "server": "analytics",
                "tool": "run_sql_query",
                "params": {"sql": sql},
                "result": result,
            }
        )

    # Generate insights
    insights = _generate_insights(result)
    answer = _format_analytics_result(result, insights)

    # Log audit
    log_audit_event(
        "analytics_agent",
        "perform_analysis",
        {"request": request},
        {"result_type": type(result).__name__},
        user_id=state["user_id"],
        request_id=state["request_id"],
    )

    # Record to memory
    memory_manager.conversation.add_message(state["session_id"], "assistant", answer)
    memory_manager.agent_observation.record_observation(
        "analytics",
        f"Performed analysis: {insights[0] if insights else 'No insights'}",
        {"request": request},
    )

    return {
        "active_agent": "analytics",
        "agent_history": ["analytics"],
        "mcp_calls": mcp_calls,
        "intermediate_results": [
            {"agent": "analytics", "result": result, "insights": insights}
        ],
        "final_result": result,
        "messages": [
            AIMessage(content=answer + "\n\n⚠️ *Please review before taking action.*")
        ],
        "audit_trail": [
            {
                "agent": "analytics",
                "action": "perform_analysis",
                "mcp_calls": len(mcp_calls),
            }
        ],
    }


def _extract_sql_query(request: str) -> str | None:
    """Extract SQL query from request if provided."""
    # Pattern 1: SQL in code block
    match = re.search(r"```sql\s*(.*?)\s*```", request, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()

    # Pattern 2: Multi-line SQL starting with SELECT and ending with semicolon or newline
    match = re.search(r"(SELECT\s+.*?)(?:;|\n\n|$)", request, re.IGNORECASE | re.DOTALL)
    if match:
        sql = match.group(1).strip()
        # Clean up whitespace
        sql = " ".join(sql.split())
        return sql

    return None


def _extract_filters(request: str) -> dict | None:
    """Extract filters from request."""
    filters = {}
    if "unverified" in request.lower():
        filters["identity_status"] = "unverified"
    if "vip" in request.lower():
        filters["segment"] = "vip"
    return filters if filters else None


def _generate_insights(result: dict) -> list[str]:
    """Generate insights from analytics result."""
    insights = []

    if "segments" in result:
        segments = result["segments"]
        if segments:
            largest = max(segments, key=lambda s: s.get("size", 0))
            insights.append(
                f"Largest segment: {largest['label']} with {largest['size']} customers"
            )

    if "rows" in result and result.get("row_count", 0) > 0:
        insights.append(f"Query returned {result['row_count']} rows")

    return insights


def _format_analytics_result(result: dict, insights: list[str]) -> str:
    """Format analytics result for display."""
    if "error" in result:
        return f"Analytics error: {result['error']}"

    output = []

    if "segments" in result:
        output.append(f"Generated {len(result['segments'])} segments:")
        for seg in result["segments"][:5]:
            output.append(f"  - {seg['label']}: {seg['size']} customers")

    if "rows" in result:
        output.append(f"Query results ({result.get('row_count', 0)} rows)")

    if insights:
        output.append("\nInsights:")
        for insight in insights:
            output.append(f"  • {insight}")

    return "\n".join(output) if output else str(result)
