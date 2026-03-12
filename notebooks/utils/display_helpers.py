"""Display helper functions for styled notebook outputs."""
import re

try:
    import pandas as pd
    from IPython.display import display, HTML
    IPYTHON_AVAILABLE = True
except ImportError:
    IPYTHON_AVAILABLE = False
    def display(*args, **kwargs):
        pass
    class HTML:
        def __init__(self, data):
            self.data = data


def _md_to_html(text):
    """Convert a subset of markdown to HTML for card rendering."""
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Collapse multiple blank lines, then split
    lines = re.sub(r'\n{2,}', '\n', text).split('\n')
    out, in_ol = [], False
    for line in lines:
        m = re.match(r'^(\d+)\.\s+(.*)', line)
        if m:
            if not in_ol:
                out.append('<ol style="margin:8px 0;padding-left:20px">')
                in_ol = True
            out.append(f'<li style="margin:6px 0">{m.group(2)}</li>')
        else:
            if in_ol:
                out.append('</ol>')
                in_ol = False
            if line.strip():
                out.append(f'<p style="margin:6px 0">{line}</p>')
    if in_ol:
        out.append('</ol>')
    return ''.join(out)


def display_card(title, content, emoji="💬", color="#667eea"):
    """Render a styled card with gradient header, with markdown rendered."""
    rendered = _md_to_html(content) if isinstance(content, str) else content
    html = f'''
    <div style="border:1px solid #e2e8f0;border-radius:8px;overflow:hidden;margin:15px 0;box-shadow:0 2px 4px rgba(0,0,0,0.1)">
        <div style="background:linear-gradient(135deg,{color},#764ba2);color:white;padding:12px 16px;font-weight:600">
            {emoji} {title}
        </div>
        <div style="padding:16px;background:white;font-size:14px;line-height:1.6">
            {rendered}
        </div>
    </div>
    '''
    display(HTML(html))


def display_metrics(metrics):
    """Render key metrics in a grid."""
    items = "".join([
        f'<div style="text-align:center"><div style="font-size:24px;font-weight:700;color:#667eea">{v}</div>'
        f'<div style="font-size:12px;color:#64748b;text-transform:uppercase">{k}</div></div>'
        for k, v in metrics.items()
    ])
    html = f'<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:16px;padding:16px;background:#f8fafc;border-radius:8px;margin:10px 0">{items}</div>'
    display(HTML(html))


def display_chunks_table(chunks, normalize_scores=False):
    """Render retrieved chunks as a styled pandas table.
    
    Args:
        chunks: List of chunk dicts with 'score' (distance), 'source', 'text', 'doc_type'
        normalize_scores: If True, convert distances to normalized relevance scores (sum to 1)
    """
    if not chunks:
        display(HTML('<em style="color:#94a3b8">No chunks retrieved</em>'))
        return
    
    # Normalize scores if requested (convert distances to probabilities)
    if normalize_scores and chunks:
        # Convert distances to similarities (inverse)
        max_dist = max(c.get('score', 0) for c in chunks)
        similarities = [max_dist - c.get('score', 0) + 0.01 for c in chunks]
        total_sim = sum(similarities)
        normalized_scores = [sim / total_sim for sim in similarities]
        
        # Update chunks with normalized scores
        for i, c in enumerate(chunks):
            c['normalized_score'] = normalized_scores[i]
    
    df = pd.DataFrame([{
        'Source': c['source'],
        'Type': c.get('doc_type', 'unknown'),
        'Relevance': c.get('normalized_score', c.get('score', 0)) if normalize_scores else c.get('score', 0),
        'Preview': c['text'][:100] + '...'
    } for c in chunks])
    
    # Color code relevance scores
    def color_relevance(val):
        if normalize_scores:
            # For normalized scores (0-1, higher is better)
            if val > 0.3:
                return 'background-color: #d1fae5; color: #065f46'
            elif val > 0.15:
                return 'background-color: #fef3c7; color: #92400e'
            else:
                return 'background-color: #fee2e2; color: #991b1b'
        else:
            # For raw distances (lower is better, typical range 0-2)
            if val < 0.8:
                return 'background-color: #d1fae5; color: #065f46'  # Highly relevant
            elif val < 1.5:
                return 'background-color: #fef3c7; color: #92400e'  # Moderately relevant
            else:
                return 'background-color: #fee2e2; color: #991b1b'  # Less relevant
    
    styled = (df.style
        .format({'Relevance': '{:.3f}'})
        .map(color_relevance, subset=['Relevance'])
        .set_table_styles([
            {'selector': 'th', 'props': [('background', '#667eea'), ('color', 'white'), ('font-weight', '600'), ('padding', '8px')]},
            {'selector': 'td', 'props': [('padding', '8px'), ('border-bottom', '1px solid #e2e8f0')]}
        ])
        .hide(axis='index')
    )
    display(styled)
    
    # Show sum if normalized
    if normalize_scores:
        total = sum(c.get('normalized_score', 0) for c in chunks)
        display(HTML(f'<div style="margin-top:8px;font-size:12px;color:#64748b">ℹ️ Normalized relevance scores sum to: {total:.3f}</div>'))


def display_bar_chart(data_dict, title, color="#10b981"):
    """Render a horizontal bar chart using Unicode blocks."""
    if not data_dict:
        return
    total = sum(data_dict.values())
    bars = []
    for label, count in sorted(data_dict.items(), key=lambda x: -x[1]):
        pct = count / total * 100 if total > 0 else 0
        bar_len = int(pct / 2)
        bar = '█' * bar_len
        count_str = f"{count:.3f}" if isinstance(count, float) else str(count)
        bars.append(
            f'<div style="margin:8px 0"><span style="display:inline-block;width:120px;font-weight:600">{label}</span>'
            f'<span style="color:{color}">{bar}</span> <span style="color:#64748b">{count_str} ({pct:.1f}%)</span></div>'
        )

    html = f'<div style="padding:12px;background:#f8fafc;border-radius:8px;margin:10px 0"><div style="font-weight:600;margin-bottom:8px">{title}</div>{"".join(bars)}</div>'
    display(HTML(html))


def display_section(title):
    """Render a bold section heading."""
    display(HTML(f'<div style="font-size:18px;font-weight:600;margin:16px 0">{title}</div>'))


def display_styled_table(df, gradient_col=None, fmt=None, header_color="#667eea", cmap="Blues"):
    """Render a styled pandas DataFrame with optional gradient and formatting."""
    styled = df.style.set_table_styles([
        {"selector": "th", "props": [("background", header_color), ("color", "white"), ("padding", "8px")]},
        {"selector": "td", "props": [("padding", "8px")]},
    ]).hide(axis="index")
    if gradient_col:
        styled = styled.background_gradient(subset=[gradient_col], cmap=cmap)
    if fmt:
        styled = styled.format(fmt)
    display(styled)


def show_chart(fig, path):
    """Save a matplotlib figure to disk and display it inline as base64."""
    import base64, io
    import matplotlib.pyplot as plt
    fig.savefig(path, dpi=100, bbox_inches="tight")
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    plt.close(fig)
    b64 = base64.b64encode(buf.getvalue()).decode()
    display(HTML(f'<img src="data:image/png;base64,{b64}" style="max-width:700px;border-radius:8px;margin:8px 0">'))
