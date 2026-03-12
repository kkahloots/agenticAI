"""
Comprehensive visualization utilities for notebooks.
Combines all visualization patterns into reusable functions.
"""

import pandas as pd
import json
from pathlib import Path

try:
    from IPython.display import display, HTML
except ImportError:
    def display(*args, **kwargs):
        pass
    class HTML:
        def __init__(self, data):
            self.data = data

from .display_helpers import display_card, display_metrics, display_bar_chart, display_chunks_table
from .notebook_helpers import display_customer_profile


def create_styled_dataframe(data):
    """Create a styled dataframe with standard formatting."""
    df = pd.DataFrame(data)
    return df.style.set_properties(**{"font-size": "12px"}).hide(axis="index")


def display_side_by_side(left_title, left_content, right_title, right_content,
                         left_color="#fee2e2", left_text_color="#dc2626",
                         right_color="#dcfce7", right_text_color="#16a34a"):
    """Render two columns side-by-side for comparison (e.g., before/after)."""
    html = f'''
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:16px 0">
        <div style="border:1px solid {left_color};border-radius:8px;padding:16px;background:{left_color}">
            <div style="font-weight:600;color:{left_text_color};margin-bottom:8px">{left_title}</div>
            <div style="font-family:monospace;font-size:13px;line-height:1.5">{left_content}</div>
        </div>
        <div style="border:1px solid {right_color};border-radius:8px;padding:16px;background:{right_color}">
            <div style="font-weight:600;color:{right_text_color};margin-bottom:8px">{right_title}</div>
            <div style="font-family:monospace;font-size:13px;line-height:1.5">{right_content}</div>
        </div>
    </div>
    '''
    display(HTML(html))


def display_violations_list(violations):
    """Render a list of violations with warning styling."""
    if not violations:
        return
    violations_html = "<br>".join([f"⚠️ {v}" for v in violations])
    html = f'<div style="margin:16px 0;padding:12px;background:#fef2f2;border-left:4px solid #dc2626;border-radius:4px"><strong>Violations:</strong><br>{violations_html}</div>'
    display(HTML(html))


def display_status_banner(message, status="success"):
    """Render a status banner (success/info/warning/error)."""
    colors = {
        "success": ("#f0fdf4", "#16a34a", "#15803d"),
        "info": ("#f0f9ff", "#0284c7", "#0c4a6e"),
        "warning": ("#fef3c7", "#d97706", "#92400e"),
        "error": ("#fef2f2", "#dc2626", "#7f1d1d"),
    }
    bg, border, text = colors.get(status, colors["info"])
    html = f'<div style="margin:16px 0;padding:12px;background:{bg};border-left:4px solid {border};border-radius:4px;color:{text}">{message}</div>'
    display(HTML(html))


def display_title(text, emoji=""):
    """Display a main title with emoji."""
    display(HTML(f'<div style="font-size:18px;font-weight:600;margin:16px 0">{emoji} {text}</div>'))


def display_segmentation_results(segments, title="Customer Segments Discovered"):
    """Display customer segmentation results with table and chart."""
    display(HTML(f'<div style="font-size:18px;font-weight:600;margin:16px 0">🎯 {title}</div>'))
    
    seg_data = [{"Segment": seg["label"], "Size": seg["size"],
                 "Avg Risk Score": f"{seg['avg_risk_score']:.3f}",
                 "Avg Engagement": f"{seg['avg_engagement_score']:.3f}"} for seg in segments]
    
    display(create_styled_dataframe(seg_data))
    
    largest_segment = max(segments, key=lambda x: x['size'])
    display_card("Business Insights", 
        f"Identified {len(segments)} distinct customer segments. "
        f"Largest segment: {largest_segment['label']} with {largest_segment['size']} customers. "
        "Use these segments for targeted marketing campaigns.",
        emoji="💡", color="#10b981")


def display_sql_analytics_results(result, title="SQL Analytics Results"):
    """Display SQL query results with formatted table and metrics."""
    if "rows" in result and result["rows"]:
        display(HTML(f'<div style="font-size:18px;font-weight:600;margin:16px 0">💰 {title}</div>'))
        
        rows = [{"Customer ID": r["customer_id"], "Name": r["full_name"][:20],
                 "Segment": r["segment"], "Lifetime Value": f"€{r['lifetime_value']:,.2f}",
                 "Fraud Score": f"{r['fraud_score']:.3f}",
                 "Engagement": f"{r['engagement_score']:.3f}"} for r in result["rows"]]
        
        display(create_styled_dataframe(rows))
        
        total_value = sum(float(r["lifetime_value"]) for r in result["rows"])
        display_metrics({"Total Value": f"€{total_value:,.2f}",
                        "Average Value": f"€{total_value / len(result['rows']):,.2f}",
                        "Customers": len(result["rows"])})
    else:
        display_card("Error", "No data returned", emoji="❌", color="#ef4444")


def display_fraud_risk_analysis(result, title="High-Fraud-Risk Customer Analysis"):
    """Display fraud risk analysis with table and charts."""
    if "rows" in result and result["rows"]:
        display(HTML(f'<div style="font-size:18px;font-weight:600;margin:16px 0">⚠️ {title}</div>'))
        
        df = pd.DataFrame(result["rows"])
        df["avg_risk"] = df["avg_risk"].apply(lambda x: f"{x:.3f}")
        df["avg_engagement"] = df["avg_engagement"].apply(lambda x: f"{x:.3f}")
        
        display(df.style.set_table_styles([
            {'selector': 'th', 'props': [('background', '#ef4444'), ('color', 'white'), ('padding', '10px')]},
            {'selector': 'td', 'props': [('padding', '10px')]}
        ]).hide(axis='index'))
        
        segments = {row["segment"]: row["count"] for row in result["rows"]}
        display_bar_chart(segments, "📊 High-Fraud-Risk Customers by Segment", color="#ef4444")
        
        total_high_risk = sum(row["count"] for row in result["rows"])
        display_card("Risk Alert", 
            f"Found {total_high_risk} high-fraud-risk customers (fraud score > 0.7). "
            "Recommend enhanced monitoring and identity verification.",
            emoji="🚨", color="#ef4444")
    else:
        display_card("Info", "No high-fraud-risk customers found", emoji="✅", color="#10b981")


def display_enhanced_sentiment_analysis(results, title="Sentiment Analysis Results", sample_posts=None):
    """Enhanced sentiment analysis with improved visualization and insights."""
    display(HTML(f'<div style="font-size:18px;font-weight:600;margin:16px 0">😊 {title}</div>'))
    
    df = pd.DataFrame(results)
    
    def color_sentiment(val):
        colors = {"positive": "background-color: #d1fae5; color: #065f46; font-weight: 600",
                  "negative": "background-color: #fee2e2; color: #991b1b; font-weight: 600",
                  "neutral": "background-color: #fef3c7; color: #92400e; font-weight: 600"}
        return colors.get(val, "")
    
    styled = (df.style.map(color_sentiment, subset=["Sentiment"])
        .set_table_styles([
            {'selector': 'th', 'props': [('background', '#667eea'), ('color', 'white'), ('padding', '12px')]},
            {'selector': 'td', 'props': [('padding', '12px'), ('font-size', '13px')]}
        ]).hide(axis='index'))
    
    display(styled)
    
    sentiment_counts = {}
    for r in results:
        sent = r["Sentiment"]
        sentiment_counts[sent] = sentiment_counts.get(sent, 0) + 1
    
    display_bar_chart(sentiment_counts, "📊 Sentiment Distribution", color="#8b5cf6")
    
    total = len(results)
    positive_pct = sentiment_counts.get("positive", 0) / total * 100
    negative_pct = sentiment_counts.get("negative", 0) / total * 100
    
    display_metrics({"Positive": f"{positive_pct:.1f}% ({sentiment_counts.get('positive', 0)})",
                    "Negative": f"{negative_pct:.1f}% ({sentiment_counts.get('negative', 0)})",
                    "Neutral": f"{(100-positive_pct-negative_pct):.1f}% ({sentiment_counts.get('neutral', 0)})"})


def display_customer_360_view(customer_360, customer_id):
    """Display comprehensive Customer 360 view with all sections."""
    if "error" not in customer_360:
        display(HTML(f'<div style="font-size:18px;font-weight:600;margin:16px 0">👤 Customer 360 View: {customer_id}</div>'))
        
        display_customer_profile(customer_360["customer_profile"], "Customer Profile")
        
        summary = customer_360["summary"]
        display_metrics({"Total Sales": f"€{summary['total_sales_value']:,.2f}",
                        "Transactions": summary['transaction_count'],
                        "Social Posts": summary['social_engagement'],
                        "Support Tickets": summary['support_tickets']})
        
        sales = customer_360["sales"]
        if sales["total_count"] > 0:
            display(HTML('<div style="margin-top:20px"><strong>💰 Sales Activity</strong></div>'))
            channel_data = {ch: sum(1 for t in sales["transactions"] if t["channel"] == ch) for ch in sales["channels"]}
            display_bar_chart(channel_data, "Transactions by Channel", color="#10b981")
    else:
        display_card("Error", f"Customer {customer_id} not found", emoji="❌", color="#ef4444")


def display_sales_analytics_dashboard(sales_analytics):
    """Display comprehensive sales analytics dashboard."""
    display(HTML('<div style="font-size:18px;font-weight:600;margin:16px 0">💼 Sales Analytics Dashboard</div>'))
    
    display_metrics({"Total Revenue": f"€{sales_analytics['total_revenue']:,.2f}",
                    "Transactions": sales_analytics['total_transactions'],
                    "Avg Transaction": f"€{sales_analytics['avg_transaction_value']:,.2f}"})
    
    display(HTML('<div style="margin-top:20px"><strong>📊 Revenue by Category</strong></div>'))
    display_bar_chart(sales_analytics['by_product'], "Revenue Distribution", color="#10b981")


def display_support_analytics_dashboard(support_analytics):
    """Display comprehensive support analytics dashboard."""
    display(HTML('<div style="font-size:18px;font-weight:600;margin:16px 0">🎫 Support Analytics Dashboard</div>'))
    
    display_metrics({"Total Tickets": support_analytics['total_tickets'],
                    "Open Tickets": support_analytics['open_tickets'],
                    "High Priority": support_analytics['high_priority']})
    
    display(HTML('<div style="margin-top:20px"><strong>📋 Tickets by Type</strong></div>'))
    display_bar_chart(support_analytics['by_type'], "Ticket Type Distribution", color="#ef4444")


def display_lead_scoring_results(result):
    """Display lead scoring results with formatted table and insights."""
    display(HTML(f'<div style="font-size:18px;font-weight:600;margin:16px 0">🎯 Lead Scoring: {result["offer_name"]}</div>'))
    display_metrics({"Total Eligible": result["total_eligible"], "Returned": result["returned"]})
    
    rows = [{"Customer ID": p["customer_id"], "Name": p["full_name"][:20],
             "Segment": p["segment"], "Lead Score": f'{p["lead_score"]:.3f}',
             "Rationale": p["rationale"][:50]} for p in result["prospects"]]
    
    display(pd.DataFrame(rows).style.set_properties(**{"font-size": "12px"}).hide(axis="index"))


def display_campaign_execution_plan(plan, offer_code, segment):
    """Display bulk campaign execution plan with charts and metrics."""
    display(HTML(f'<div style="font-size:18px;font-weight:600;margin:16px 0">📢 Bulk Campaign: {offer_code} → {segment}</div>'))
    
    display_metrics({"Total Prospects": plan["total_prospects"], "To Send": plan["to_send"],
                    "Blocked": plan["blocked"]})
    
    channel_counts = {}
    for item in plan["execution_plan"]:
        ch = item.get("channel") or "blocked"
        channel_counts[ch] = channel_counts.get(ch, 0) + 1
    
    if channel_counts:
        display_bar_chart(channel_counts, "Execution Plan by Channel", color="#8b5cf6")


def display_email_search_results(result, title="Email Search Results", emoji="📧", color="#8b5cf6"):
    """Display email search results with answer, sources, and metrics."""
    messages = result.get("messages", [])
    answer = messages[-1].content if messages else "(no answer)"
    display_card(title, answer, emoji=emoji, color=color)
    
    chunks = result["result"].get("chunks", [])
    if chunks:
        display(HTML('<div style="margin-top:16px;font-weight:600;color:#475569">📚 Retrieved Email Sources</div>'))
        display_chunks_table(chunks)
        display_metrics({"Emails Found": len(chunks),
                        "Avg Relevance": f"{sum(c.get('score', 0) for c in chunks) / len(chunks):.3f}"})


def display_outcome_analysis(chunks, title="Outcome Analysis"):
    """Display outcome analysis from retrieved chunks."""
    if not chunks:
        return
    
    outcomes = {}
    for c in chunks:
        text_lower = c['text'].lower()
        if "accepted" in text_lower:
            outcomes["Accepted"] = outcomes.get("Accepted", 0) + 1
        elif "declined" in text_lower:
            outcomes["Declined"] = outcomes.get("Declined", 0) + 1
        elif "pending" in text_lower:
            outcomes["Pending"] = outcomes.get("Pending", 0) + 1
    
    if outcomes:
        display_bar_chart(outcomes, f"📊 {title}", color="#8b5cf6")


def display_source_breakdown(chunks, title="Source Breakdown"):
    """Display breakdown of sources by collection type."""
    if not chunks:
        return
    
    from collections import Counter
    source_types = Counter(c.get("doc_type", "unknown") for c in chunks)
    
    display_metrics({"Total Sources": len(chunks), "Collections": len(source_types)})
    display_bar_chart(dict(source_types), f"📊 {title}", color="#06b6d4")


def display_audit_trail(trail_data, persistent_log_path=None):
    """Display audit trail with optional persistent log entries."""
    display(HTML('<div style="font-size:18px;font-weight:600;margin:16px 0">📋 Audit Trail</div>'))
    
    if trail_data:
        # Round confidence to 3 decimals if present
        for item in trail_data:
            if 'confidence' in item and isinstance(item['confidence'], (int, float)):
                item['confidence'] = round(item['confidence'], 3)
        
        df = pd.DataFrame(trail_data)
        display(df.style.set_table_styles([
            {'selector': 'th', 'props': [('background', '#667eea'), ('color', 'white'), ('padding', '10px')]},
            {'selector': 'td', 'props': [('padding', '10px'), ('font-family', 'monospace')]}
        ]).hide(axis='index'))
    
    if persistent_log_path:
        audit_path = Path(persistent_log_path)
        if audit_path.exists():
            lines = audit_path.read_text().strip().splitlines()
            recent = [json.loads(line) for line in lines[-5:]]
            df_log = pd.DataFrame(recent)[["timestamp", "agent_id", "action", "user_id"]]
            
            display(HTML('<div style="font-size:16px;font-weight:600;margin:24px 0 8px 0">📁 Recent Audit Log Entries</div>'))
            display(df_log.style.hide(axis='index'))


def display_guardrail_check(guardrail_result, test_output=None):
    """Display guardrail check results with before/after comparison."""
    display(HTML('<div style="font-size:18px;font-weight:600;margin:16px 0">🛡️ Guardrail Check</div>'))
    
    original = test_output or getattr(guardrail_result, 'original_text', '')
    revised = guardrail_result.revised_text if hasattr(guardrail_result, 'revised_text') else str(guardrail_result)
    
    comparison_html = f'''
<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
    <div style="border:1px solid #e2e8f0;border-radius:8px;padding:16px">
        <div style="font-weight:600;color:#ef4444;margin-bottom:8px">❌ Original Output</div>
        <div style="background:#fef2f2;padding:12px;border-radius:4px;font-family:monospace;font-size:13px">{original}</div>
    </div>
    <div style="border:1px solid #e2e8f0;border-radius:8px;padding:16px">
        <div style="font-weight:600;color:#10b981;margin-bottom:8px">✅ Sanitized Output</div>
        <div style="background:#f0fdf4;padding:12px;border-radius:4px;font-family:monospace;font-size:13px">{revised}</div>
    </div>
</div>
'''
    display(HTML(comparison_html))
    
    violations = getattr(guardrail_result, 'violations', [])
    if violations:
        display_violations_list(violations)
    
    display_metrics({"Guardrail Passed": "✅ Yes" if getattr(guardrail_result, 'passed', False) else "❌ No",
                    "Violations": len(violations)})


def display_text_summarization(ticket, summarize_fn):
    """Display text summarization results with before/after comparison."""
    display(HTML('<div style="font-size:18px;font-weight:600;margin:16px 0">📝 Support Ticket Summarization</div>'))
    
    display_card("Original Ticket",
        f"<strong>Ticket ID:</strong> {ticket['ticket_id']}<br>"
        f"<strong>Type:</strong> {ticket['type']}<br>"
        f"<strong>Description:</strong> {ticket['description']}",
        emoji="📋", color="#3b82f6")
    
    summary_result = summarize_fn(ticket['description'])
    
    if "summary" in summary_result:
        display_card("AI Summary", summary_result['summary'], emoji="✨", color="#10b981")


def display_customer_enrichment(enriched, customer_id):
    """Display customer enrichment data from multiple sources."""
    display(HTML(f'<div style="font-size:18px;font-weight:600;margin:16px 0">🔍 Customer Enrichment: {customer_id}</div>'))
    
    e = enriched.get("enrichment", {})
    display_card("Enrichment Data",
        f"<strong>Credit Bureau Score:</strong> {e.get('credit_bureau_score', 'N/A')}<br>"
        f"<strong>Company Type:</strong> {e.get('company_type', 'N/A').replace('_', ' ').title()}<br>"
        f"<strong>Location Score:</strong> {e.get('location_score', 0):.2f}",
        emoji="🔍", color="#8b5cf6")


def display_nba_recommendations(test_customers, recommend_fn, profile_fn):
    """Display Next-Best-Action recommendations for multiple customers."""
    display(HTML('<div style="font-size:18px;font-weight:600;margin:16px 0">🏆 Next-Best-Action Recommendations</div>'))
    
    rows = []
    for cid in test_customers:
        offer = recommend_fn(cid) or {}
        profile_result = profile_fn(customer_id=cid)
        profile = profile_result.get("customer", {}) if profile_result else {}
        rows.append({"Customer ID": cid, "Segment": profile.get("segment", "N/A"),
                    "Best Offer": offer.get("offer_name", "None"),
                    "Confidence": f"{offer.get('confidence', 0):.3f}"})
    
    display(pd.DataFrame(rows).style.set_properties(**{"font-size": "12px"}).hide(axis="index"))


def display_consent_notification(customer_id, send_result, draft):
    """Display consent-gated notification results."""
    display(HTML(f'<div style="font-size:18px;font-weight:600;margin:16px 0">📧 Consent-Gated Notification: {customer_id}</div>'))
    
    display_card("Email Draft",
        f"<strong>Subject:</strong> {draft.get('subject', 'N/A')}<br>"
        f"<strong>Body Preview:</strong><br><em>{draft.get('body', '')[:200]}...</em>",
        emoji="📧", color="#3b82f6")
    
    status_color = "#10b981" if send_result.get("status") == "sent" else "#ef4444"
    display_card("Send Result",
        f"<strong>Status:</strong> {send_result.get('status', 'unknown').upper()}<br>"
        f"<strong>Reason:</strong> {send_result.get('reason', 'Consent verified ✅')}",
        emoji="✅" if send_result.get("status") == "sent" else "🚫", color=status_color)


def display_kyc_gate(customer_id, kyc_status, case=None):
    """Display KYC gate status and remediation case if needed."""
    display(HTML(f'<div style="font-size:18px;font-weight:600;margin:16px 0">🔒 KYC Gate: {customer_id}</div>'))
    
    display_metrics({"KYC Status": kyc_status.get("kyc_status", "unknown").upper(),
                    "Expiry Date": kyc_status.get("kyc_expiry_date", "N/A")})
    
    if kyc_status.get("kyc_status") == "expired" and case:
        display_card("Action Blocked — KYC Remediation Case Opened",
            f"<strong>Case ID:</strong> {case.get('case_id', 'N/A')}<br>"
            f"<strong>Status:</strong> {case.get('status', 'unknown').upper()}",
            emoji="🔒", color="#ef4444")
    else:
        display_card("KYC Valid", f"Customer {customer_id} KYC is valid.", emoji="✅", color="#10b981")


def display_return_risk_intervention(at_risk, send_notification_fn):
    """Display return risk intervention: find high-return-risk customers and send win-back offers."""
    display(HTML('<div style="font-size:18px;font-weight:600;margin:16px 0">⚠️ Return Risk Intervention</div>'))
    display_metrics({"High Return-Risk Customers": len(at_risk), "Threshold": "> 0.70"})

    rows = []
    for c in at_risk[:8]:
        flags = c.get("consent_flags", {})
        channel = "email" if flags.get("email") else "sms" if flags.get("sms") else None
        if channel:
            send = send_notification_fn(c["customer_id"], channel, {"body": "We miss you! Here is a special win-back offer."})
        else:
            send = {"status": "blocked", "reason": "no_channel_consent"}
        rows.append({"Customer ID": c["customer_id"], "Segment": c.get("segment", "N/A"),
                    "Return Risk": f'{c["return_risk"]:.2f}', "Status": send["status"]})

    display(pd.DataFrame(rows).style.set_properties(**{"font-size": "12px"}).hide(axis="index"))


def display_blocked_example(customer_id, blocked_result):
    """Display blocked notification example."""
    display_card(f"Blocked Example ({customer_id})",
        f"<strong>Status:</strong> {blocked_result.get('status', 'unknown').upper()}<br>"
        f"<strong>Reason:</strong> {blocked_result.get('reason', 'N/A')}",
        emoji="🚫", color="#f59e0b")


def display_campaign_results_dashboard(campaign_results):
    """Display campaign results dashboard with performance metrics."""
    display(HTML('<div style="font-size:18px;font-weight:600;margin:16px 0">📊 Campaign Results Dashboard</div>'))
    
    total = len(campaign_results)
    converted = sum(1 for r in campaign_results if r.get("converted"))
    conversion_rate = converted / total * 100 if total else 0
    
    display_metrics({"Total Sent": total, "Converted": converted,
                    "Conversion Rate": f"{conversion_rate:.1f}%"})
    
    outcome_counts = {}
    for r in campaign_results:
        outcome = r.get("outcome", "unknown")
        outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1
    
    display_bar_chart(outcome_counts, "Outcomes Across All Campaigns", color="#3b82f6")


# ── Level 4 Strategic Agent display helpers ──────────────────────────────────

def display_goal_decomposition(sub_goals: list, goal: str = ""):
    """Display goal decomposition into sub-tasks."""
    display(HTML('<div style="font-size:18px;font-weight:600;margin:16px 0">🎯 Goal Decomposition</div>'))
    if goal:
        display_card("Strategic Goal", goal, emoji="🏆", color="#667eea")
    rows = [{"#": i + 1, "Sub-Task": t} for i, t in enumerate(sub_goals)]
    display(pd.DataFrame(rows).style.set_properties(**{"font-size": "13px"}).hide(axis="index"))


def display_strategic_orchestration(result: dict):
    """Display full strategic orchestration result with segment, campaign, KPI."""
    display(HTML('<div style="font-size:18px;font-weight:600;margin:16px 0">🔄 Strategic Orchestration Result</div>'))
    campaign = result.get("campaign") or {}
    kpi = result.get("kpi_baseline") or {}
    reflection = result.get("reflection") or {}
    display_metrics({
        "Segment": result.get("segment", "N/A"),
        "Campaign ID": campaign.get("campaign_id", "N/A"),
        "Est. Reach": campaign.get("estimated_reach", "N/A"),
        "KPI Baseline": kpi.get("summary", "no prior data"),
    })
    replanned = reflection.get("should_replan", False)
    status = "warning" if replanned else "success"
    msg = f"⚠️ Re-plan triggered: {reflection.get('reason', '')}" if replanned else "✅ KPI within range — no re-plan needed"
    display_status_banner(msg, status=status)
    if result.get("blocked"):
        display_status_banner(f"🚫 Blocked: {result['blocked']}", status="error")


def display_revenue_impact(impact: dict):
    """Display revenue impact projection."""
    display(HTML('<div style="font-size:18px;font-weight:600;margin:16px 0">💰 Revenue Impact Analysis</div>'))
    display_metrics({
        "Segment Size": impact.get("segment_size", 0),
        "Conversion Rate": f"{impact.get('conversion_rate', 0):.1%}",
        "Avg Order Value": f"€{impact.get('avg_order_value', 0):,.2f}",
        "Projected Revenue": f"€{impact.get('projected_revenue', 0):,.2f}",
        "Incremental Revenue": f"€{impact.get('incremental_revenue', 0):,.2f}",
        "ROI": f"{impact.get('roi_pct', 0):.1f}%",
    })


def display_scenario_comparison(scenarios: list):
    """Display side-by-side scenario simulation results."""
    display(HTML('<div style="font-size:18px;font-weight:600;margin:16px 0">🔬 Scenario Simulation</div>'))
    rows = [{
        "Scenario": s["name"],
        "Segment": s.get("segment", "N/A"),
        "Conv. Rate": f"{s.get('conversion_rate', 0):.1%}",
        "Projected Revenue": f"€{s.get('projected_revenue', 0):,.2f}",
        "Risk": s.get("risk", "medium"),
        "Recommended": "✅" if s.get("recommended") else "",
    } for s in scenarios]
    display(pd.DataFrame(rows).style.set_properties(**{"font-size": "13px"}).hide(axis="index"))
    best = next((s for s in scenarios if s.get("recommended")), None)
    if best:
        display_card("Recommended Scenario",
            f"<strong>{best['name']}</strong> — projected revenue €{best.get('projected_revenue', 0):,.2f} "
            f"at {best.get('conversion_rate', 0):.1%} conversion with {best.get('risk', 'medium')} risk.",
            emoji="🏆", color="#10b981")


def display_pilot_results(pilot: dict):
    """Display A/B pilot test split and compliance gate result."""
    display(HTML('<div style="font-size:18px;font-weight:600;margin:16px 0">🧪 Pilot Test Results</div>'))
    display_metrics({
        "Total Segment": pilot.get("total", 0),
        "Pilot Group": pilot.get("pilot_size", 0),
        "Control Group": pilot.get("control_size", 0),
        "Pilot %": f"{pilot.get('pilot_pct', 0):.0%}",
        "Compliance Gate": "✅ Passed" if pilot.get("compliance_passed") else "❌ Failed",
    })
    if pilot.get("compliance_notes"):
        display_status_banner(pilot["compliance_notes"],
                              status="success" if pilot.get("compliance_passed") else "warning")


def display_roadmap_priorities(initiatives: list):
    """Display ranked initiative roadmap by ROI."""
    display(HTML('<div style="font-size:18px;font-weight:600;margin:16px 0">🗺️ Initiative Roadmap</div>'))
    rows = [{
        "Priority": i + 1,
        "Initiative": init["name"],
        "Est. Revenue": f"€{init.get('est_revenue', 0):,.0f}",
        "Effort": init.get("effort", "medium"),
        "ROI Score": f"{init.get('roi_score', 0):.3f}",
        "Timeline": init.get("timeline", "Q?"),
    } for i, init in enumerate(initiatives)]
    display(pd.DataFrame(rows).style.set_properties(**{"font-size": "13px"}).hide(axis="index"))
    roi_data = {r["Initiative"][:20]: float(r["ROI Score"]) for r in rows}
    display_bar_chart(roi_data, "ROI Score by Initiative", color="#667eea")


def display_governance_dashboard(audit_path: str, event_log: list):
    """Display governance: recent audit entries + observability events."""
    display(HTML('<div style="font-size:18px;font-weight:600;margin:16px 0">🛡️ Governance & Observability Dashboard</div>'))
    # Audit trail
    try:
        lines = Path(audit_path).read_text().strip().splitlines()[-8:]
        records = [json.loads(l) for l in lines if l.strip()]
        if records:
            df = pd.DataFrame(records)[["timestamp", "agent_id", "action", "user_id"]]
            display(HTML('<div style="font-weight:600;margin:8px 0">📋 Recent Audit Events</div>'))
            display(df.style.hide(axis="index"))
    except Exception:
        display_status_banner("Audit log not available", status="warning")
    # Observability events
    if event_log:
        node_events = [e for e in event_log if e.get("event") == "node_end"]
        if node_events:
            display(HTML('<div style="font-weight:600;margin:16px 0 8px 0">⚡ Node Execution Metrics</div>'))
            rows = [{"Node": e["node"], "Duration (ms)": e["duration_ms"],
                     "Tokens": e.get("tokens_used", 0), "Error": e.get("error") or "—"}
                    for e in node_events]
            display(pd.DataFrame(rows).style.hide(axis="index"))


def display_kpi_deviation(deviation: dict):
    """Display KPI deviation check and self-reflection decision."""
    display(HTML('<div style="font-size:18px;font-weight:600;margin:16px 0">📈 KPI Deviation & Self-Reflection</div>'))
    display_metrics({
        "Segment": deviation.get("segment_id", "N/A"),
        "Current Conv. Rate": f"{deviation.get('current_conversion_rate', 0):.1%}",
        "Target Conv. Rate": f"{deviation.get('target_conversion_rate', 0):.1%}",
        "Deviation": f"{deviation.get('deviation', 0):.1%}",
        "Action Required": "⚠️ Yes" if deviation.get("action_required") else "✅ No",
    })
    status = "warning" if deviation.get("action_required") else "success"
    msg = ("⚠️ KPI deviation exceeds threshold — self-reflection will trigger re-plan"
           if deviation.get("action_required")
           else "✅ KPI within acceptable range")
    display_status_banner(msg, status=status)


def display_kpi_history(outcomes_path: str, segment_id: str):
    """Show per-campaign conversion & open rate history for a segment."""
    import json as _json
    from pathlib import Path as _Path

    try:
        records = [
            _json.loads(l) for l in _Path(outcomes_path).read_text().splitlines()
            if l.strip() and f'"segment_id": "{segment_id}"' in l
        ]
    except Exception:
        display_status_banner(f"Could not read {outcomes_path}", status="warning")
        return

    if not records:
        display_status_banner(f"No history found for segment '{segment_id}'", status="warning")
        return

    display(HTML(f'<div style="font-size:18px;font-weight:600;margin:16px 0">📊 Campaign History: {segment_id} ({len(records)} campaigns)</div>'))

    rows = [{
        "Campaign": r["campaign_id"],
        "Date": r["recorded_at"][:10],
        "Reach": r["estimated_reach"],
        "Conversions": r["actual_conversions"],
        "Opens": r["actual_opens"],
        "Conv. Rate": f"{r['conversion_rate']:.1%}",
        "Open Rate": f"{r['open_rate']:.1%}",
    } for r in records if r.get("actual_conversions", 0) > 0 or r.get("actual_opens", 0) > 0]

    if rows:
        df = pd.DataFrame(rows)

        def _color_conv(val):
            v = float(val.strip("%")) / 100
            if v >= 0.10: return "background-color:#d1fae5;color:#065f46"
            if v >= 0.05: return "background-color:#fef3c7;color:#92400e"
            return "background-color:#fee2e2;color:#991b1b"

        styled = (df.style
            .map(_color_conv, subset=["Conv. Rate"])
            .set_table_styles([{
                "selector": "th",
                "props": [("background", "#667eea"), ("color", "white"), ("padding", "8px")]
            }, {
                "selector": "td",
                "props": [("padding", "8px"), ("font-size", "12px")]
            }])
            .hide(axis="index")
        )
        display(styled)

    # Sparkline: conversion rate over time
    conv_rates = [r["conversion_rate"] for r in records]
    max_rate = max(conv_rates) if conv_rates else 1
    bars = []
    for r in records:
        rate = r["conversion_rate"]
        bar_len = int(rate / max_rate * 30) if max_rate > 0 else 0
        color = "#10b981" if rate >= 0.05 else "#ef4444"
        bars.append(
            f'<div style="display:flex;align-items:center;margin:3px 0;font-size:12px">'
            f'<span style="width:110px;color:#64748b">{r["recorded_at"][:10]}</span>'
            f'<span style="color:{color};letter-spacing:-1px">{"█" * bar_len}</span>'
            f'<span style="margin-left:6px;color:#374151;font-weight:600">{rate:.1%}</span>'
            f'</div>'
        )
    html = (
        '<div style="padding:12px;background:#f8fafc;border-radius:8px;margin:10px 0">'
        '<div style="font-weight:600;margin-bottom:8px">Conversion Rate Trend</div>'
        + "".join(bars) + "</div>"
    )
    display(HTML(html))

    # Summary
    active = [r for r in records if r["conversion_rate"] > 0]
    if active:
        avg_conv = sum(r["conversion_rate"] for r in active) / len(active)
        avg_open = sum(r["open_rate"] for r in active) / len(active)
        display_metrics({
            "Campaigns with Data": len(active),
            "Avg Conversion Rate": f"{avg_conv:.1%}",
            "Avg Open Rate": f"{avg_open:.1%}",
            "Best Campaign": max(active, key=lambda r: r["conversion_rate"])["campaign_id"],
        })
