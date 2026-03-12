"""
Notebook helper functions to reduce code duplication across level1-3 notebooks.
Provides high-level functions for common notebook patterns.
"""
import json
import pandas as pd

try:
    from IPython.display import display, HTML
except ImportError:
    def display(*args, **kwargs):
        pass
    class HTML:
        def __init__(self, data):
            self.data = data

from .display_helpers import display_card, display_metrics, display_bar_chart, display_chunks_table

# Import system components
import sys
import os
from pathlib import Path

# Add project root to path if not already there
_here = Path(os.getcwd())
_root = _here.parent if _here.name == "notebooks" else _here
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from src.graph import graph
from src.core.state import new_state
from src.core.observability import clear_event_log


def ask(question: str, customer_id: str = None, user_id: str = "manager@shop.com"):
    """
    Send a question through the agent graph and return result (suppresses event logs).
    Standardized wrapper with error handling.
    """
    clear_event_log()
    state = new_state(question, user_id=user_id)
    if customer_id:
        state["customer_id"] = customer_id
    
    # Suppress stdout during invoke
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            result = graph.invoke(state, config={"configurable": {"thread_id": state["request_id"]}})
            return result
        except Exception as e:
            return {"error": str(e), "messages": []}


def show_result(result, show_chunks=False, title="Answer"):
    """Display agent result in a beautiful card format with routing info."""
    messages = result.get("messages", [])
    answer = messages[-1].content if messages else "(no answer)"
    
    # Routing info
    display_metrics({
        "Routed To": result.get("routed_to", "unknown"),
        "Confidence": f"{result.get('confidence', 0):.3f}",
        "Tools Used": len(result.get("tool_calls", []))
    })
    
    # Answer card
    display_card(title, answer, emoji="💬", color="#10b981")
    
    # Optional: show retrieved chunks
    if show_chunks and "result" in result:
        chunks = result["result"].get("chunks", [])
        if chunks:
            display(HTML('<div style="margin-top:16px;font-weight:600;color:#475569">📚 Retrieved Sources</div>'))
            display_chunks_table(chunks)


def display_customer_profile(customer_data, title="Customer Profile"):
    """Display a customer profile in a standardized format."""
    if not customer_data:
        display_card("Error", "Customer not found", emoji="❌", color="#ef4444")
        return

    metrics = {"Customer ID": customer_data.get("customer_id", "—"),
               "Segment": customer_data.get("segment", "—")}
    if "engagement_score" in customer_data:
        metrics["Engagement"] = f"{customer_data['engagement_score']:.3f}"
    for key in ("identity_status", "fraud_score", "full_name", "country"):
        if key in customer_data:
            val = customer_data[key]
            if key == "fraud_score" and isinstance(val, (int, float)):
                metrics[key.replace("_", " ").title()] = f"{val:.3f}"
            else:
                metrics[key.replace("_", " ").title()] = val
    display_metrics(metrics)

    # Optional rich fields
    optional = {k: customer_data[k] for k in
                ("full_name", "country", "preferred_language", "lifetime_value",
                 "last_interaction_date", "return_risk") if k in customer_data}
    if optional:
        rows = "".join(f'<div><strong>{k.replace("_"," ").title()}:</strong> {v}</div>'
                       for k, v in optional.items())
        display_card(title, f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;font-size:14px">{rows}</div>',
                     emoji="👤", color="#3b82f6")

    if customer_data.get("purchase_categories"):
        categories_df = pd.DataFrame({"Category": customer_data["purchase_categories"]})
        display(HTML('<div style="margin-top:16px"><strong>Purchase Categories</strong></div>'))
        display(categories_df.style.hide(axis='index').set_table_styles([
            {'selector': 'th', 'props': [('background', '#3b82f6'), ('color', 'white')]},
            {'selector': 'td', 'props': [('padding', '6px')]}
        ]))

    if customer_data.get("consent_flags"):
        consent_df = pd.DataFrame([customer_data["consent_flags"]]).T.reset_index()
        consent_df.columns = ["Channel", "Consent"]
        display(HTML('<div style="margin-top:16px"><strong>Consent Flags</strong></div>'))
        display(consent_df.style.hide(axis='index').set_table_styles([
            {'selector': 'th', 'props': [('background', '#10b981'), ('color', 'white')]},
            {'selector': 'td', 'props': [('padding', '6px')]}
        ]))


def display_identity_status_analysis(customers_to_check, title="Identity Verification Status Analysis"):
    """Display identity verification status for multiple customers (reads directly from DB)."""
    import sqlite3
    display(HTML(f'<div style="font-size:18px;font-weight:600;margin:16px 0">🔐 {title}</div>'))

    def color_status(val):
        colors = {"verified": "background-color: #d1fae5; color: #065f46",
                  "unverified": "background-color: #fee2e2; color: #991b1b",
                  "pending": "background-color: #fef3c7; color: #92400e"}
        return colors.get(val, "")

    db_path = _root / "data" / "customers.db"
    placeholders = ",".join("?" * len(customers_to_check))
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            f"SELECT customer_id, identity_status, fraud_score FROM customers WHERE customer_id IN ({placeholders})",
            customers_to_check
        ).fetchall()

    row_map = {r[0]: r for r in rows}
    identity_results = []
    for cid in customers_to_check:
        row = row_map.get(cid, (cid, "unknown", None))
        fraud_score = row[2]
        if isinstance(fraud_score, (int, float)):
            fraud_score = f"{fraud_score:.3f}"
        elif fraud_score is None:
            fraud_score = "N/A"
        identity_results.append({
            "Customer": cid,
            "Status": row[1],
            "Fraud Score": fraud_score
        })

    df = pd.DataFrame(identity_results)
    styled = (df.style
        .map(color_status, subset=["Status"])
        .set_table_styles([
            {'selector': 'th', 'props': [('background', '#667eea'), ('color', 'white'), ('font-weight', '600'), ('padding', '10px')]},
            {'selector': 'td', 'props': [('padding', '10px'), ('border-bottom', '1px solid #e2e8f0')]}
        ])
        .hide(axis='index')
    )
    display(styled)

    status_counts = df["Status"].value_counts().to_dict()
    display_bar_chart(status_counts, "Identity Status Distribution", color="#f59e0b")
    return identity_results


def display_search_results(result, result_type="Search Results", emoji="📧", color="#8b5cf6"):
    """Display search results with chunks and statistics."""
    messages = result.get("messages", [])
    answer = messages[-1].content if messages else "(no answer)"
    display_card(result_type, answer, emoji=emoji, color=color)

    # Show retrieved sources
    chunks = result["result"].get("chunks", [])
    if chunks:
        display(HTML('<div style="margin-top:16px;font-weight:600;color:#475569">📚 Retrieved Sources</div>'))
        display_chunks_table(chunks)
        
        # Statistics
        display_metrics({
            "Results Found": len(chunks),
            "Avg Relevance": f"{sum(c.get('score', 0) for c in chunks) / len(chunks):.3f}",
            "Date Range": "2025-2026"
        })


def display_policy_qa(questions, title="Policy Q&A"):
    """Display policy questions and answers in a standardized format."""
    display(HTML(f'<div style="font-size:18px;font-weight:600;margin:16px 0">📋 {title}</div>'))
    
    for i, q in enumerate(questions, 1):
        result = ask(q)
        messages = result.get("messages", [])
        answer = messages[-1].content if messages else "(no answer)"
        
        display(HTML(f'<div style="font-size:16px;font-weight:600;margin:20px 0 8px 0">📋 Policy Question {i}</div>'))
        display(HTML(f'<div style="color:#64748b;font-style:italic;margin-bottom:12px">{q}</div>'))
        display_card("Policy Answer", answer, emoji="📖", color="#3b82f6")
        
        # Show source documents
        chunks = result["result"].get("chunks", [])
        if chunks:
            sources = list(set(c['source'] for c in chunks))
            sources_html = ", ".join([f'<code style="background:#f1f5f9;padding:2px 6px;border-radius:4px">{s}</code>' for s in sources])
            display(HTML(f'<div style="margin-top:8px;font-size:13px;color:#64748b">📚 Sources: {sources_html}</div>'))


def setup_notebook():
    """Bootstrap path, env, and imports. Returns project root path."""
    import os, sys
    from pathlib import Path
    from dotenv import load_dotenv
    _here = Path(os.getcwd())
    _root = _here.parent if _here.name == "notebooks" else _here
    os.chdir(_root)
    sys.path.insert(0, str(_root))
    sys.path.insert(0, str(_root / "notebooks"))
    load_dotenv()
    os.environ["GUARDRAIL_ENABLED"] = "false"
    return _root


def run_guardrail_demo(test_output=None):
    """Enable guardrails, run a PII/policy check demo, then disable."""
    import os
    from src.core.guardrails import guardrail_check
    os.environ["GUARDRAIL_ENABLED"] = "true"
    if test_output is None:
        test_output = "Customer email is john.doe@example.com and phone is 555-123-4567. We recommend buying shares."
    gr = guardrail_check(test_output, request_id="demo-001")
    # Import display helper lazily to avoid circular imports
    from .visualization import display_guardrail_check
    display_guardrail_check(gr, test_output=test_output)
    os.environ["GUARDRAIL_ENABLED"] = "false"
    display(HTML('<div style="margin-top:16px;padding:12px;background:#f0fdf4;border-left:4px solid #10b981;border-radius:4px;color:#065f46">✅ Guardrails disabled for remaining demos</div>'))



