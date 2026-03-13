"""Display helpers for Level 5 agentic recommendation notebook."""
from IPython.display import display, HTML

_CARD = 'border:1px solid #e2e8f0;border-radius:8px;padding:16px;margin:10px 0'
_TITLE_STYLE = 'font-weight:600;margin-bottom:8px;color:#667eea'
_PRE_STYLE = 'background:#f1f5f9;padding:12px;border-radius:4px;font-size:12px'


def show_llm_feature_priority(features):
    """UC3-B: LLM feature priority suggestion."""
    rows = ''.join(
        f'<div style="margin:4px 0"><strong>#{f["priority"]}</strong> {f["feature"]} — '
        f'<span style="color:#64748b">{f["reason"]}</span></div>'
        for f in features
    )
    display(HTML(
        f'<div style="{_CARD}">'
        f'<div style="{_TITLE_STYLE}">🔬 LLM Feature Priority (Dynamic)</div>'
        f'{rows}</div>'
    ))


def show_llm_strategy_selection(strat):
    """UC4-B / UC5-B: LLM strategy selection or fallback decision."""
    label = strat.get('label', '🤖 LLM Strategy Selection (Dynamic)')
    html = (
        f'<div style="{_CARD}">'
        f'<div style="{_TITLE_STYLE}">{label}</div>'
        f'<div><strong>Strategy:</strong> {strat["strategy"]}</div>'
        f'<div><strong>Reason:</strong> {strat["reason"]}</div>'
    )
    if 'method' in strat:
        html += f'<div><strong>Method:</strong> {strat["method"]}</div>'
    html += '</div>'
    display(HTML(html))


def show_llm_explanation(top_rec, expl):
    """UC4-B: LLM explanation for top recommendation."""
    display(HTML(
        f'<div style="{_CARD}">'
        f'<div style="{_TITLE_STYLE}">💬 LLM Explanation (Dynamic)</div>'
        f'<div><strong>Top Product:</strong> {top_rec["product_id"]}</div>'
        f'<div><strong>Explanation:</strong> {expl["explanation"]}</div>'
        f'<div><strong>Dominant Signal:</strong> {expl["dominant_signal"]}</div>'
        f'</div>'
    ))


def show_running_banner(n_customers):
    """UC6-A: Running banner for batch recommendations."""
    display(HTML(
        f'<div style="color:#64748b;margin-bottom:12px">'
        f'Running recommendations for {n_customers} customers...</div>'
    ))


def show_generated_sql(sql_query, title='💾 Generated SQL (Dynamic)'):
    """UC6-B / UC7-B: Generated SQL block."""
    display(HTML(
        f'<div style="{_CARD}">'
        f'<div style="{_TITLE_STYLE}">{title}</div>'
        f'<pre style="{_PRE_STYLE}">{sql_query}</pre>'
        f'</div>'
    ))


def show_llm_weight_proposal(w):
    """UC7-B: LLM weight adjustment proposal."""
    display(HTML(
        f'<div style="{_CARD}">'
        f'<div style="{_TITLE_STYLE}">⚖️ LLM Weight Proposal [SIMULATION ONLY] (Dynamic)</div>'
        f'<div><strong>Current:</strong> {w["current_weights"]}</div>'
        f'<div><strong>Proposed:</strong> {w["proposed_weights"]}</div>'
        f'<div><strong>Reason:</strong> {w["reason"]}</div>'
        f'<div style="color:#ef4444;font-size:12px;margin-top:6px">⚠️ {w["warning"]}</div>'
        f'</div>'
    ))


def show_llm_request_classification(vc):
    """UC8-B: LLM request classification result."""
    display(HTML(
        f'<div style="{_CARD}">'
        f'<div style="{_TITLE_STYLE}">🤖 LLM Request Classification (Dynamic)</div>'
        f'<div><strong>Classified as:</strong> {vc["strategy"]}</div>'
        f'<div><strong>Confidence:</strong> {vc["confidence"]}</div>'
        f'<div><strong>Method:</strong> {vc["method"]}</div>'
        f'</div>'
    ))


def show_routing_request_header(req):
    """UC9-B: Request header for routing loop."""
    display(HTML(f'<div style="font-weight:600;margin:12px 0 4px;color:#334155">Request: "{req}"</div>'))


def show_routing_divider():
    """UC9-B: Divider between routing results."""
    display(HTML('<hr style="border:none;border-top:1px solid #e2e8f0;margin:16px 0">'))
