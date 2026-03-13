"""Agentic Display Utilities - show plans, reasoning, tool selection, SQL, etc."""

try:
    from IPython.display import display, HTML
    import pandas as pd
    IPYTHON_AVAILABLE = True
except ImportError:
    IPYTHON_AVAILABLE = False
    def display(*args, **kwargs):
        pass
    class HTML:
        def __init__(self, data):
            self.data = data


def show_agentic_result(result: dict, title: str = None):
    """Show complete agentic result."""
    if title:
        display(HTML(f'<div style="font-size:20px;font-weight:700;margin:20px 0;color:#667eea">{title}</div>'))
    
    mode = result.get("mode", "unknown")
    request_id = result.get("request_id", "N/A")
    
    html = f'''
    <div style="border:1px solid #e2e8f0;border-radius:8px;padding:16px;margin:10px 0;background:#f8fafc">
        <div style="font-weight:600;margin-bottom:8px">Execution Summary</div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px">
            <div><span style="color:#64748b">Mode:</span> <strong>{mode}</strong></div>
            <div><span style="color:#64748b">Request ID:</span> <code style="font-size:11px">{request_id[:8]}</code></div>
            <div><span style="color:#64748b">Memory Entries:</span> <strong>{result.get("memory_entries", 0)}</strong></div>
        </div>
    </div>
    '''
    display(HTML(html))


def show_agent_plan(result: dict):
    """Show generated plan."""
    plan = result.get("plan", {})
    if not plan:
        return
    
    html = '<div style="border:1px solid #e2e8f0;border-radius:8px;padding:16px;margin:10px 0">'
    html += '<div style="font-weight:600;margin-bottom:12px;color:#667eea">📋 Generated Plan</div>'
    html += f'<div style="margin-bottom:8px"><strong>Goal:</strong> {plan.get("goal", "N/A")}</div>'
    html += f'<div style="margin-bottom:8px"><strong>Intent:</strong> {plan.get("intent", "N/A")}</div>'
    html += f'<div style="margin-bottom:8px"><strong>Requires SQL:</strong> {"✅ Yes" if plan.get("requires_sql") else "❌ No"}</div>'
    
    subtasks = plan.get("subtasks", [])
    if subtasks:
        html += '<div style="margin-top:12px"><strong>Subtasks:</strong></div>'
        html += '<ol style="margin:8px 0;padding-left:20px">'
        for task in subtasks:
            html += f'<li style="margin:6px 0"><strong>{task.get("action")}</strong> → {task.get("agent")} <br/>'
            html += f'<span style="color:#64748b;font-size:12px">{task.get("reason")}</span></li>'
        html += '</ol>'
    
    html += '</div>'
    display(HTML(html))


def show_agent_reasoning(result: dict):
    """Show agent reasoning."""
    plan = result.get("plan", {})
    subtasks = plan.get("subtasks", [])
    
    if not subtasks:
        return
    
    html = '<div style="border:1px solid #e2e8f0;border-radius:8px;padding:16px;margin:10px 0">'
    html += '<div style="font-weight:600;margin-bottom:12px;color:#667eea">🧠 Agent Reasoning</div>'
    
    for i, task in enumerate(subtasks, 1):
        html += f'<div style="margin:8px 0;padding:8px;background:#f8fafc;border-radius:4px">'
        html += f'<div style="font-weight:600">Step {i}: {task.get("action")}</div>'
        html += f'<div style="color:#64748b;font-size:13px;margin-top:4px">{task.get("reason")}</div>'
        html += '</div>'
    
    html += '</div>'
    display(HTML(html))


def show_tool_selection(result: dict):
    """Show tool selection."""
    if result.get("mode") != "dynamic":
        return
    
    tool_selections = result.get("tool_selections", [])
    if not tool_selections or not any(tool_selections):
        return
    
    html = '<div style="border:1px solid #e2e8f0;border-radius:8px;padding:16px;margin:10px 0">'
    html += '<div style="font-weight:600;margin-bottom:12px;color:#667eea">🔧 Tool Selection (Dynamic)</div>'
    
    for i, tools in enumerate(tool_selections, 1):
        if tools:
            html += f'<div style="margin:8px 0"><strong>Step {i}:</strong> '
            html += ', '.join(f'<code style="background:#f1f5f9;padding:2px 6px;border-radius:3px">{t}</code>' for t in tools)
            html += '</div>'
    
    html += '</div>'
    display(HTML(html))


def show_generated_sql(result: dict):
    """Show generated SQL queries."""
    from agentic.memory.memory_manager import get_memory
    
    memory = get_memory()
    request_id = result.get("request_id")
    if not request_id:
        return
    
    entries = memory.get_request_history(request_id)
    sql_entries = [e for e in entries if e.entry_type == "sql_generation"]
    
    if not sql_entries:
        return
    
    html = '<div style="border:1px solid #e2e8f0;border-radius:8px;padding:16px;margin:10px 0">'
    html += '<div style="font-weight:600;margin-bottom:12px;color:#667eea">💾 Generated SQL</div>'
    
    for entry in sql_entries:
        query = entry.data.get("query", "")
        intent = entry.data.get("intent", "")
        html += f'<div style="margin:8px 0"><strong>Intent:</strong> {intent}</div>'
        html += f'<pre style="background:#f1f5f9;padding:12px;border-radius:4px;overflow-x:auto;font-size:12px">{query}</pre>'
    
    html += '</div>'
    display(HTML(html))


def show_agent_path(result: dict):
    """Show agent execution path."""
    agent_path = result.get("agent_path", [])
    if not agent_path:
        return
    
    html = '<div style="border:1px solid #e2e8f0;border-radius:8px;padding:16px;margin:10px 0">'
    html += '<div style="font-weight:600;margin-bottom:12px;color:#667eea">🔀 Agent Path</div>'
    html += '<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">'
    
    for i, agent in enumerate(agent_path):
        if i > 0:
            html += '<span style="color:#94a3b8">→</span>'
        html += f'<div style="background:#667eea;color:white;padding:6px 12px;border-radius:4px;font-size:13px">{agent}</div>'
    
    html += '</div></div>'
    display(HTML(html))


def show_memory_updates(result: dict):
    """Show memory updates."""
    from agentic.memory.memory_manager import get_memory
    
    memory = get_memory()
    request_id = result.get("request_id")
    if not request_id:
        return
    
    entries = memory.get_request_history(request_id)
    if not entries:
        return
    
    html = '<div style="border:1px solid #e2e8f0;border-radius:8px;padding:16px;margin:10px 0">'
    html += '<div style="font-weight:600;margin-bottom:12px;color:#667eea">💭 Memory Updates</div>'
    
    type_counts = {}
    for entry in entries:
        type_counts[entry.entry_type] = type_counts.get(entry.entry_type, 0) + 1
    
    html += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px">'
    for entry_type, count in type_counts.items():
        html += f'<div style="background:#f8fafc;padding:8px;border-radius:4px;text-align:center">'
        html += f'<div style="font-size:20px;font-weight:700;color:#667eea">{count}</div>'
        html += f'<div style="font-size:11px;color:#64748b;text-transform:uppercase">{entry_type}</div>'
        html += '</div>'
    html += '</div></div>'
    display(HTML(html))


def show_mcp_calls(result: dict):
    """Show MCP tool calls."""
    from agentic.memory.memory_manager import get_memory
    
    memory = get_memory()
    request_id = result.get("request_id")
    if not request_id:
        return
    
    entries = memory.get_request_history(request_id)
    tool_entries = [e for e in entries if e.entry_type == "tool_usage"]
    
    if not tool_entries:
        return
    
    html = '<div style="border:1px solid #e2e8f0;border-radius:8px;padding:16px;margin:10px 0">'
    html += '<div style="font-weight:600;margin-bottom:12px;color:#667eea">🔌 MCP Tool Calls</div>'
    
    for entry in tool_entries:
        tool_name = entry.data.get("tool_name", "unknown")
        html += f'<div style="margin:6px 0;padding:6px;background:#f8fafc;border-radius:4px">'
        html += f'<code style="color:#667eea">{tool_name}</code>'
        html += '</div>'
    
    html += '</div>'
    display(HTML(html))


def show_model_choice(result: dict):
    """Show selected model(s) from plan."""
    plan = result.get("plan", {})
    models = plan.get("selected_models", [])
    if not models:
        return

    html = '<div style="border:1px solid #e2e8f0;border-radius:8px;padding:16px;margin:10px 0">'
    html += '<div style="font-weight:600;margin-bottom:12px;color:#667eea">🤖 Selected Models</div>'
    html += '<div style="display:flex;gap:8px;flex-wrap:wrap">'
    for m in models:
        html += f'<div style="background:#f1f5f9;padding:6px 12px;border-radius:4px;font-size:13px"><code>{m}</code></div>'
    html += '</div></div>'
    display(HTML(html))


def show_feature_selection(result: dict):
    """Show selected features from plan or memory."""
    from agentic.memory.memory_manager import get_memory
    memory = get_memory()
    request_id = result.get("request_id")
    if not request_id:
        return

    entries = memory.get_request_history(request_id)
    feat_entries = [e for e in entries if "feature" in e.entry_type.lower() or
                    (e.entry_type == "tool_usage" and "feature" in str(e.data.get("tool_name", "")))]
    if not feat_entries:
        return

    html = '<div style="border:1px solid #e2e8f0;border-radius:8px;padding:16px;margin:10px 0">'
    html += '<div style="font-weight:600;margin-bottom:12px;color:#667eea">🔬 Feature Selection</div>'
    for entry in feat_entries:
        data = entry.data
        selected = data.get("output", {}).get("result", {}).get("features", [])
        if selected:
            html += '<div style="display:flex;gap:8px;flex-wrap:wrap">'
            for f in selected:
                name = f.get("feature", f) if isinstance(f, dict) else f
                html += f'<div style="background:#f0fdf4;padding:4px 10px;border-radius:4px;font-size:12px;color:#16a34a">{name}</div>'
            html += '</div>'
    html += '</div>'
    display(HTML(html))


def show_comparison(nonagent_result: dict, deterministic_result: dict, dynamic_result: dict):
    """Show side-by-side comparison of three approaches."""
    html = '<div style="border:1px solid #e2e8f0;border-radius:8px;padding:16px;margin:10px 0">'
    html += '<div style="font-weight:600;margin-bottom:12px;color:#667eea">📊 Three-Way Comparison</div>'
    html += '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px">'
    
    # Nonagent
    html += '<div style="border:1px solid #e2e8f0;padding:12px;border-radius:4px">'
    html += '<div style="font-weight:600;margin-bottom:8px;color:#64748b">Nonagent Pipeline</div>'
    html += f'<div style="font-size:12px">Direct tool calls</div>'
    html += '</div>'
    
    # Deterministic
    html += '<div style="border:1px solid #e2e8f0;padding:12px;border-radius:4px">'
    html += '<div style="font-weight:600;margin-bottom:8px;color:#667eea">Deterministic Agentic</div>'
    html += f'<div style="font-size:12px">Fixed tool paths</div>'
    html += f'<div style="font-size:12px">Memory: {deterministic_result.get("memory_entries", 0)} entries</div>'
    html += '</div>'
    
    # Dynamic
    html += '<div style="border:1px solid #e2e8f0;padding:12px;border-radius:4px">'
    html += '<div style="font-weight:600;margin-bottom:8px;color:#10b981">Dynamic Agentic</div>'
    html += f'<div style="font-size:12px">Dynamic tool discovery</div>'
    html += f'<div style="font-size:12px">Memory: {dynamic_result.get("memory_entries", 0)} entries</div>'
    html += '</div>'
    
    html += '</div></div>'
    display(HTML(html))
