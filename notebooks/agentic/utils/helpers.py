"""Helper functions for agentic notebooks."""
import pandas as pd
from IPython.display import display, HTML
from agentic.agentic_state import new_agentic_state
from graphs.agent_workflow_graph import agentic_graph
from memory.memory_manager import memory_manager


def agentic_ask(request: str, user_id: str = "demo_user", session_id: str = None, **kwargs):
    """Execute an agentic request and return the result."""
    state = new_agentic_state(request, user_id=user_id, session_id=session_id)
    config = {"configurable": {"thread_id": state["request_id"]}}
    result = agentic_graph.invoke(state, config=config)
    return result


def display_agentic_customer_profile(result: dict, title: str = "Customer Profile"):
    """Display customer profile from agentic result."""
    final_result = result.get("final_result", {})
    customer_data = final_result.get("customer", final_result)
    
    if not customer_data or not customer_data.get("customer_id"):
        display(HTML('<div style="padding:16px;background:#fee2e2;border-left:4px solid #ef4444;border-radius:4px;color:#991b1b">❌ Customer not found</div>'))
        return
    
    metrics = {}
    if "customer_id" in customer_data:
        metrics["Customer ID"] = customer_data["customer_id"]
    if "segment" in customer_data:
        metrics["Segment"] = customer_data["segment"]
    if "engagement_score" in customer_data:
        metrics["Engagement"] = f"{customer_data['engagement_score']:.3f}"
    if "identity_status" in customer_data:
        metrics["Identity Status"] = customer_data["identity_status"]
    if "fraud_score" in customer_data:
        metrics["Fraud Score"] = f"{customer_data['fraud_score']:.3f}"
    
    html = '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:16px;padding:16px;background:#f8fafc;border-radius:8px;margin:10px 0">'
    for k, v in metrics.items():
        html += f'<div style="text-align:center"><div style="font-size:20px;font-weight:700;color:#667eea">{v}</div><div style="font-size:12px;color:#64748b;text-transform:uppercase">{k}</div></div>'
    html += '</div>'
    display(HTML(html))
    
    optional = {k: customer_data[k] for k in ["full_name", "country", "preferred_language", "lifetime_value", "last_interaction_date"] if k in customer_data}
    if optional:
        html = f'<div style="border:1px solid #e2e8f0;border-radius:8px;overflow:hidden;margin:15px 0"><div style="background:linear-gradient(135deg,#3b82f6,#764ba2);color:white;padding:12px 16px;font-weight:600">👤 {title}</div><div style="padding:16px;background:white;display:grid;grid-template-columns:1fr 1fr;gap:12px;font-size:14px">'
        for k, v in optional.items():
            html += f'<div><strong>{k.replace("_", " ").title()}:</strong> {v}</div>'
        html += '</div></div>'
        display(HTML(html))
    
    if customer_data.get("purchase_categories"):
        df = pd.DataFrame({"Category": customer_data["purchase_categories"]})
        display(HTML('<div style="margin-top:16px;font-weight:600">Purchase Categories</div>'))
        display(df)


def display_agentic_identity_analysis(customers: list, title: str = "Identity Verification Status Analysis"):
    """Display identity status for multiple customers."""
    display(HTML(f'<div style="font-size:18px;font-weight:600;margin:16px 0">🔐 {title}</div>'))
    
    results = []
    for cid in customers:
        result = agentic_ask(f"What is the identity status of {cid}?")
        final_result = result.get("final_result", {})
        customer_data = final_result.get("customer", final_result)
        
        results.append({
            "Customer": cid,
            "Status": customer_data.get("identity_status", "unknown"),
            "Fraud Score": f"{customer_data.get('fraud_score', 0):.3f}" if "fraud_score" in customer_data else "N/A"
        })
    
    df = pd.DataFrame(results)
    display(df.style.hide(axis="index").set_table_styles([
        {"selector": "th", "props": [("background", "#667eea"), ("color", "white"), ("font-weight", "600"), ("padding", "10px")]},
        {"selector": "td", "props": [("padding", "10px"), ("border-bottom", "1px solid #e2e8f0")]}
    ]))
    
    return results


def display_agentic_search_results(result: dict, title: str = "Search Results", emoji: str = "📧", color: str = "#8b5cf6"):
    """Display search results with chunks."""
    from notebooks.nonagentic.utils.display_helpers import display_card, display_metrics
    
    messages = result.get("messages", [])
    answer = messages[-1].content if messages else "(no answer)"
    
    display_card(title, answer, emoji=emoji, color=color)
    
    final_result = result.get("final_result", {})
    chunks = final_result.get("chunks", [])
    if chunks:
        display(HTML('<div style="margin-top:16px;font-weight:600;color:#475569">📚 Retrieved Sources</div>'))
        df = pd.DataFrame([{"Source": c.get("source", ""), "Type": c.get("type", ""), "Relevance": f"{c.get('score', 0):.3f}", "Preview": c.get("content", "")[:100] + "..."} for c in chunks])
        display(df.style.hide(axis="index").set_table_styles([
            {"selector": "th", "props": [("background", "#667eea"), ("color", "white"), ("font-weight", "600"), ("padding", "8px")]},
            {"selector": "td", "props": [("padding", "8px"), ("border-bottom", "1px solid #e2e8f0")]}
        ]))
        
        display_metrics({
            "Results Found": len(chunks),
            "Avg Relevance": f"{sum(c.get('score', 0) for c in chunks) / len(chunks):.3f}",
            "MCP Calls": len(result.get("mcp_calls", []))
        })


def display_agentic_source_breakdown(result: dict, title: str = "Source Breakdown"):
    """Display source breakdown by collection."""
    final_result = result.get("final_result", {})
    chunks = final_result.get("chunks", [])
    if not chunks:
        return
    
    from collections import Counter
    sources = [c.get("source", "").split(".")[-1] for c in chunks]
    counts = Counter(sources)
    
    html = f'<div style="padding:12px;background:#f8fafc;border-radius:8px;margin:10px 0"><div style="font-weight:600;margin-bottom:8px">{title}</div>'
    max_count = max(counts.values())
    for src, count in counts.most_common():
        pct = count / len(chunks) * 100
        bar_width = int(count / max_count * 40)
        html += f'<div style="margin:8px 0"><span style="display:inline-block;width:120px;font-weight:600">{src}</span><span style="color:#06b6d4">{"█" * bar_width}</span> <span style="color:#64748b">{count} ({pct:.1f}%)</span></div>'
    html += '</div>'
    display(HTML(html))
    
    from notebooks.nonagentic.utils.display_helpers import display_metrics
    display_metrics({
        "Total Sources": len(chunks),
        "Collections": len(counts)
    })


def display_agentic_policy_qa(questions: list, title: str = "Policy Q&A"):
    """Display policy questions and answers."""
    display(HTML(f'<div style="font-size:18px;font-weight:600;margin:16px 0">📋 {title}</div>'))
    
    for i, q in enumerate(questions, 1):
        result = agentic_ask(q)
        messages = result.get("messages", [])
        answer = messages[-1].content if messages else "(no answer)"
        
        display(HTML(f'<div style="font-size:16px;font-weight:600;margin:20px 0 8px 0">📋 Policy Question {i}</div>'))
        display(HTML(f'<div style="color:#64748b;font-style:italic;margin-bottom:12px">{q}</div>'))
        
        html = f'<div style="border:1px solid #e2e8f0;border-radius:8px;overflow:hidden;margin:15px 0;box-shadow:0 2px 4px rgba(0,0,0,0.1)"><div style="background:linear-gradient(135deg,#3b82f6,#764ba2);color:white;padding:12px 16px;font-weight:600">📖 Policy Answer</div><div style="padding:16px;background:white;font-size:14px;line-height:1.6"><p style="margin:6px 0">{answer}</p></div></div>'
        display(HTML(html))
        
        final_result = result.get("final_result", {})
        chunks = final_result.get("chunks", [])
        if chunks:
            sources = list(set(c.get("source", "") for c in chunks))
            sources_html = ", ".join([f'<code style="background:#f1f5f9;padding:2px 6px;border-radius:4px">{s}</code>' for s in sources])
            display(HTML(f'<div style="margin-top:8px;font-size:13px;color:#64748b">📚 Sources: {sources_html}</div>'))


def display_agentic_audit_trail(result: dict):
    """Display audit trail with MCP calls."""
    display(HTML('<div style="font-size:18px;font-weight:600;margin:16px 0">📋 Agentic Audit Trail</div>'))
    
    audit_trail = result.get("audit_trail", [])
    if audit_trail:
        df = pd.DataFrame(audit_trail)
        display(df.style.set_table_styles([
            {"selector": "th", "props": [("background", "#667eea"), ("color", "white"), ("padding", "10px")]},
            {"selector": "td", "props": [("padding", "10px"), ("font-family", "monospace")]}
        ]).hide(axis="index"))
    
    from notebooks.nonagentic.utils.display_helpers import display_metrics
    display_metrics({
        "Agent Path": " → ".join(result.get("agent_history", [])),
        "MCP Calls": len(result.get("mcp_calls", [])),
        "Audit Entries": len(audit_trail)
    })
    
    mcp_calls = result.get("mcp_calls", [])
    if mcp_calls:
        display(HTML('<div style="font-size:16px;font-weight:600;margin:16px 0 8px 0">🔧 MCP Tool Calls</div>'))
        df = pd.DataFrame([{"Server": c["server"], "Tool": c["tool"], "Params": str(c["params"])} for c in mcp_calls])
        display(df.style.set_table_styles([
            {"selector": "th", "props": [("background", "#8b5cf6"), ("color", "white"), ("padding", "8px")]},
            {"selector": "td", "props": [("padding", "8px"), ("border-bottom", "1px solid #e2e8f0")]}
        ]).hide(axis="index"))


def run_agentic_guardrail_demo(test_output: str = None):
    """Run guardrail demo."""
    import os
    from nonagentic.core.guardrails import guardrail_check
    
    os.environ["GUARDRAIL_ENABLED"] = "true"
    if test_output is None:
        test_output = "Customer email is john.doe@example.com and phone is 555-123-4567. We recommend buying shares."
    
    gr = guardrail_check(test_output, request_id="demo-001")
    
    from notebooks.nonagentic.utils.visualization import display_guardrail_check
    display_guardrail_check(gr, test_output=test_output)
    
    os.environ["GUARDRAIL_ENABLED"] = "false"
    display(HTML('<div style="margin-top:16px;padding:12px;background:#f0fdf4;border-left:4px solid #10b981;border-radius:4px;color:#065f46">✅ Guardrails disabled for remaining demos</div>'))


def display_outcome_analysis(chunks, title="Outcome Analysis"):
    """Display outcome analysis from retrieved chunks."""
    from notebooks.nonagentic.utils.visualization import display_outcome_analysis as _display_outcome_analysis
    _display_outcome_analysis(chunks, title)


def show_agentic_result(result: dict, title: str = "Result"):
    """Display agentic result with routing information."""
    intent = result.get("intent", "unknown")
    confidence = result.get("confidence", 0.0)
    active_agent = result.get("active_agent", "unknown")
    mcp_calls = result.get("mcp_calls", [])
    
    # Display metrics
    html = f"""<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:16px;padding:16px;background:#f8fafc;border-radius:8px;margin:10px 0">"""
    html += f"""<div style="text-align:center"><div style="font-size:24px;font-weight:700;color:#667eea">{active_agent}</div><div style="font-size:12px;color:#64748b;text-transform:uppercase">Agent</div></div>"""
    html += f"""<div style="text-align:center"><div style="font-size:24px;font-weight:700;color:#667eea">{intent}</div><div style="font-size:12px;color:#64748b;text-transform:uppercase">Intent</div></div>"""
    html += f"""<div style="text-align:center"><div style="font-size:24px;font-weight:700;color:#667eea">{confidence:.3f}</div><div style="font-size:12px;color:#64748b;text-transform:uppercase">Confidence</div></div>"""
    html += f"""<div style="text-align:center"><div style="font-size:24px;font-weight:700;color:#667eea">{len(mcp_calls)}</div><div style="font-size:12px;color:#64748b;text-transform:uppercase">MCP Calls</div></div>"""
    html += "</div>"
    display(HTML(html))
    
    # Display result message
    messages = result.get("messages", [])
    if messages:
        content = messages[-1].content
        html = f"""
    <div style="border:1px solid #e2e8f0;border-radius:8px;overflow:hidden;margin:15px 0;box-shadow:0 2px 4px rgba(0,0,0,0.1)">
        <div style="background:linear-gradient(135deg,#10b981,#764ba2);color:white;padding:12px 16px;font-weight:600">
            🤖 {title}
        </div>
        <div style="padding:16px;background:white;font-size:14px;line-height:1.6">
            <p style="margin:6px 0">{"</p><p style=\"margin:6px 0\">".join(content.split("\\n"))}</p>
        </div>
    </div>
    """
        display(HTML(html))


def show_agentic_extras(result: dict):
    """Display agent path, MCP calls, and memory observations."""
    agent_history = result.get("agent_history", [])
    mcp_calls = result.get("mcp_calls", [])
    
    # Extract MCP info
    mcp_server = mcp_calls[0]["server"] if mcp_calls else "none"
    mcp_tool = mcp_calls[0]["tool"] if mcp_calls else "none"
    
    # Display agent path and MCP info
    agent_path = " → ".join(agent_history) if agent_history else "none"
    html = f"""<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:16px;padding:16px;background:#f8fafc;border-radius:8px;margin:10px 0">"""
    html += f"""<div style="text-align:center"><div style="font-size:24px;font-weight:700;color:#667eea">{agent_path}</div><div style="font-size:12px;color:#64748b;text-transform:uppercase">Agent Path</div></div>"""
    html += f"""<div style="text-align:center"><div style="font-size:24px;font-weight:700;color:#667eea">{mcp_server}</div><div style="font-size:12px;color:#64748b;text-transform:uppercase">MCP Server</div></div>"""
    html += f"""<div style="text-align:center"><div style="font-size:24px;font-weight:700;color:#667eea">{mcp_tool}</div><div style="font-size:12px;color:#64748b;text-transform:uppercase">MCP Tool</div></div>"""
    html += f"""<div style="text-align:center"><div style="font-size:24px;font-weight:700;color:#667eea">{len(mcp_calls)}</div><div style="font-size:12px;color:#64748b;text-transform:uppercase">MCP Calls Total</div></div>"""
    html += "</div>"
    display(HTML(html))
    
    # Display memory observation
    active_agent = result.get("active_agent", "unknown")
    observations = memory_manager.agent_observation.get_observations(active_agent)
    if observations:
        latest = observations[-1]["observation"]
        html = f"""<div style="margin-top:12px;padding:10px 14px;background:#f0fdf4;border-left:4px solid #10b981;border-radius:4px;color:#065f46">🧠 <strong>Memory recorded:</strong> {latest}</div>"""
        display(HTML(html))


def record_nlp_observation(task: str, result: str):
    """Record NLP task observation to memory."""
    memory_manager.agent_observation.record_observation(
        "analytics",
        f"{task}: {result}",
        {"task": task, "result": result}
    )



def show_agent_plan(plan: dict):
    """Display execution plan with steps and reasoning."""
    from IPython.display import display, HTML
    
    html = f"""
    <div style="border:1px solid #e2e8f0;border-radius:8px;overflow:hidden;margin:15px 0;box-shadow:0 2px 4px rgba(0,0,0,0.1)">
        <div style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:12px 16px;font-weight:600">
            🎯 Execution Plan
        </div>
        <div style="padding:16px;background:white;font-size:14px;line-height:1.6">
            <p style="margin:6px 0"><strong>Reasoning:</strong> {plan.get('reasoning', 'N/A')}</p>
            <p style="margin:6px 0"><strong>Complexity:</strong> {plan.get('estimated_complexity', 'N/A')}</p>
            <p style="margin:6px 0"><strong>Selected Agents:</strong> {', '.join(plan.get('selected_agents', []))}</p>
            <p style="margin:12px 0 6px 0"><strong>Steps:</strong></p>
    """
    
    for step in plan.get("plan", []):
        html += f"""
            <div style="margin:8px 0;padding:8px;background:#f8fafc;border-left:3px solid #667eea;border-radius:4px">
                <strong>Step {step.get('step')}:</strong> {step.get('action', 'N/A')}<br>
                <span style="color:#64748b;font-size:12px">Agent: {step.get('agent', 'N/A')} | Tool: {step.get('tool', 'N/A')}</span>
            </div>
        """
    
    html += """
        </div>
    </div>
    """
    display(HTML(html))


def show_agent_reasoning(reasoning: str, analysis: dict = None):
    """Display agent reasoning and query analysis."""
    from IPython.display import display, HTML
    
    html = f"""
    <div style="border:1px solid #e2e8f0;border-radius:8px;overflow:hidden;margin:15px 0;box-shadow:0 2px 4px rgba(0,0,0,0.1)">
        <div style="background:linear-gradient(135deg,#8b5cf6,#764ba2);color:white;padding:12px 16px;font-weight:600">
            🧠 Agent Reasoning
        </div>
        <div style="padding:16px;background:white;font-size:14px;line-height:1.6">
            <p style="margin:6px 0">{reasoning}</p>
    """
    
    if analysis:
        keywords = ', '.join(analysis.get('keywords', [])) or 'None'
        entities_list = []
        for k, v in analysis.get('entities', {}).items():
            if isinstance(v, list):
                entities_list.extend([str(x) for x in v])
            else:
                entities_list.append(str(v))
        entities = ', '.join(entities_list) if entities_list else 'None'
        
        # Get active signals
        signals_dict = analysis.get('intent_signals', {})
        active_signals = [k.replace('_', ' ').title() for k, v in signals_dict.items() if v]
        signals = ', '.join(active_signals) if active_signals else 'None detected'
        
        html += f"""
            <p style="margin:12px 0 6px 0"><strong>Query Analysis:</strong></p>
            <div style="margin:8px 0;padding:8px;background:#f8fafc;border-radius:4px">
                <strong>Keywords:</strong> {keywords}<br>
                <strong>Entities:</strong> {entities}<br>
                <strong>Signals:</strong> {signals}
            </div>
        """
    
    html += """
        </div>
    </div>
    """
    display(HTML(html))


def show_tool_selection(tools: list, selected: str = None):
    """Display available tools and selection."""
    from IPython.display import display, HTML
    
    html = f"""
    <div style="border:1px solid #e2e8f0;border-radius:8px;overflow:hidden;margin:15px 0;box-shadow:0 2px 4px rgba(0,0,0,0.1)">
        <div style="background:linear-gradient(135deg,#10b981,#764ba2);color:white;padding:12px 16px;font-weight:600">
            🔧 Tool Selection
        </div>
        <div style="padding:16px;background:white;font-size:14px;line-height:1.6">
    """
    
    if isinstance(tools, list) and tools:
        html += f"<p style='margin:6px 0'><strong>Available Tools:</strong> {len(tools)}</p>"
        for tool in tools[:5]:  # Show first 5
            tool_name = tool if isinstance(tool, str) else tool.get('key', 'N/A')
            is_selected = selected and selected in str(tool)
            style = "background:#d1fae5;border-left:3px solid #10b981" if is_selected else "background:#f8fafc;border-left:3px solid #cbd5e1"
            html += f"""
            <div style="margin:8px 0;padding:8px;{style};border-radius:4px">
                <strong>{tool_name}</strong>
                {' ✅ SELECTED' if is_selected else ''}
            </div>
            """
    else:
        html += f"<p style='margin:6px 0'>Tool: <strong>{tools}</strong></p>"
    
    html += """
        </div>
    </div>
    """
    display(HTML(html))


def show_sql_generated(sql: str, explanation: str = None):
    """Display generated SQL with explanation."""
    from IPython.display import display, HTML
    
    html = f"""
    <div style="border:1px solid #e2e8f0;border-radius:8px;overflow:hidden;margin:15px 0;box-shadow:0 2px 4px rgba(0,0,0,0.1)">
        <div style="background:linear-gradient(135deg,#3b82f6,#764ba2);color:white;padding:12px 16px;font-weight:600">
            💾 Generated SQL
        </div>
        <div style="padding:16px;background:white;font-size:14px;line-height:1.6">
            <div style="background:#1e293b;color:#e2e8f0;padding:12px;border-radius:4px;font-family:monospace;font-size:13px;overflow-x:auto">
                {sql}
            </div>
    """
    
    if explanation:
        html += f"""
            <p style="margin:12px 0 6px 0"><strong>Explanation:</strong></p>
            <p style="margin:6px 0;color:#64748b">{explanation}</p>
        """
    
    html += """
        </div>
    </div>
    """
    display(HTML(html))


def verify_outputs_match(result_a: dict, result_b: dict):
    """Verify that deterministic and dynamic outputs match."""
    from IPython.display import display, HTML
    
    # Compare final results
    final_a = result_a.get("final_result", {})
    final_b = result_b.get("final_result", {})
    
    match = final_a == final_b
    
    html = f"""
    <div style="border:1px solid #e2e8f0;border-radius:8px;overflow:hidden;margin:15px 0;box-shadow:0 2px 4px rgba(0,0,0,0.1)">
        <div style="background:{'#10b981' if match else '#ef4444'};color:white;padding:12px 16px;font-weight:600">
            {'✅ Outputs Match' if match else '❌ Outputs Differ'}
        </div>
        <div style="padding:16px;background:white;font-size:14px;line-height:1.6">
            <p style="margin:6px 0">Deterministic and dynamic execution produced {'identical' if match else 'different'} results.</p>
        </div>
    </div>
    """
    display(HTML(html))
    
    return match


def agentic_ask_dynamic(request: str, user_id: str = "demo_user", session_id: str = None, **kwargs):
    """Execute an agentic request with dynamic planning and tool selection."""
    from agentic.planner import generate_plan
    from agentic.registry import tool_registry
    from agentic.agentic_state import new_agentic_state
    from graphs.agent_workflow_graph import agentic_graph
    
    # Generate plan first
    plan = generate_plan(request)
    
    # Execute through graph
    state = new_agentic_state(request, user_id=user_id, session_id=session_id)
    state["agent_plan"] = plan  # Inject plan into state
    
    config = {"configurable": {"thread_id": state["request_id"]}}
    result = agentic_graph.invoke(state, config=config)
    
    # Add plan to result for display
    result["plan"] = plan
    
    return result
