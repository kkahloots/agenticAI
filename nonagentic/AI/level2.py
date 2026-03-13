from __future__ import annotations

import os

from langchain_core.messages import AIMessage

from nonagentic.core.state import AgentState
from nonagentic.core.config import load_config
from nonagentic.tools.analytics import run_sql_query, generate_segment
from nonagentic.tools.audit import log_audit_event
from nonagentic.core.observability import node_trace
from nonagentic.core.guardrails import guardrail_check
from nonagentic.core.llm import get_llm

_DB_URL = os.getenv("DATABASE_URL", "sqlite:///data/customers.db")


def _sql_chain_query(request: str) -> str | None:
    """
    Use LangChain's create_sql_query_chain with QuerySQLDataBaseTool.
    Falls back to raw LLM prompt if SQLAlchemy DB is unavailable.
    """
    try:
        from langchain_community.utilities import SQLDatabase
        from langchain.chains import create_sql_query_chain

        db = SQLDatabase.from_uri(_DB_URL)
        llm = get_llm(temperature=0.0)
        chain = create_sql_query_chain(llm, db)
        sql = chain.invoke({"question": request})
        # Strip markdown fences if present
        sql = sql.strip().strip("```sql").strip("```").strip()
        return sql
    except Exception:
        return _llm_fallback_sql(request)


def _llm_fallback_sql(request: str) -> str | None:
    """Raw LLM prompt fallback when create_sql_query_chain is unavailable."""
    try:
        from langchain_core.messages import HumanMessage, SystemMessage

        schema = (
            "Table: customers(customer_id, full_name, segment, identity_status, country, "
            "fraud_score, engagement_score, lifetime_value, return_risk, preferred_language)"
        )
        llm = get_llm(temperature=0.0)
        response = llm.invoke(
            [
                SystemMessage(
                    content=f"You are a SQL expert. Generate a safe, read-only SELECT query. {schema}. Return ONLY the SQL, no explanation."
                ),
                HumanMessage(content=request),
            ]
        )
        return response.content.strip().strip("```sql").strip("```").strip()
    except Exception:
        return None


@node_trace("level2_analytics")
def level2_node(state: AgentState) -> dict:
    cfg = load_config()
    request = state["original_request"].lower()
    result: dict = {}

    if any(w in request for w in ["segment", "cluster", "group"]):
        filters = {}
        if "unverified" in request:
            filters["identity_status"] = "unverified"
        algo = "kmeans" if "kmeans" in request else "rules"
        result = generate_segment(filters=filters or None, algorithm=algo)
        log_audit_event(
            "level2_analytics",
            "generate_segment",
            {"filters": filters, "algorithm": algo},
            {},
            user_id=state["user_id"],
            request_id=state["request_id"],
        )

        from nonagentic.tools.visualisation import visualise

        chart_path = visualise(
            result.get("segments", []),
            chart_type="bar",
            title="Customer Segments",
            request_id=state["request_id"],
        )
        if chart_path:
            result["chart_path"] = chart_path
    else:
        # G3 + G9 — use create_sql_query_chain
        sql = _sql_chain_query(state["original_request"])
        if sql:
            result = run_sql_query(sql, max_rows=cfg.sql_max_rows)
            log_audit_event(
                "level2_analytics",
                "run_sql_query",
                {"sql": sql},
                {},
                user_id=state["user_id"],
                request_id=state["request_id"],
            )
        else:
            result = {
                "error": "Could not generate SQL — please rephrase your question."
            }

    answer = _format(result)

    # G2 — guardrail on analytics output
    gr = guardrail_check(answer, request_id=state["request_id"])
    if not gr.passed:
        log_audit_event(
            "level2_analytics",
            "guardrail_violation",
            {"violations": gr.violations},
            {},
            user_id=state["user_id"],
            request_id=state["request_id"],
        )
        answer = gr.revised_text

    return {
        "routed_to": "level2_analytics",
        "result": result,
        "messages": [
            AIMessage(
                content=f"{answer}\n\n⚠️ *Please review before taking any action.*"
            )
        ],
        "tool_calls": [
            {
                "tool": "level2",
                "inputs": {"request": state["original_request"]},
                "outputs": result,
            }
        ],
        "audit_trail": [
            {
                "node": "level2_analytics",
                "action": "completed",
                "guardrail_passed": gr.passed,
            }
        ],
    }


def _format(result: dict) -> str:
    if "error" in result:
        return f"Analytics error: {result['error']}"
    if "segments" in result:
        segs = result["segments"]
        lines = [
            f"- {s['label']}: {s['size']} customers (avg fraud {s['avg_risk_score']}, avg engagement {s['avg_engagement_score']})"
            for s in segs
        ]
        warn = f"\n⚠️ {result['warning']}" if "warning" in result else ""
        chart = (
            f"\n📊 Chart saved: {result['chart_path']}"
            if result.get("chart_path")
            else ""
        )
        return "Segmentation results:\n" + "\n".join(lines) + warn + chart
    if "rows" in result:
        rows = result["rows"]
        trunc = " (truncated)" if result.get("truncated") else ""
        return (
            f"Query returned {result['row_count']} rows{trunc}:\n"
            + str(rows[:5])
            + ("..." if len(rows) > 5 else "")
        )
    return str(result)
