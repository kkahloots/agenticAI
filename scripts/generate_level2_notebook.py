#!/usr/bin/env python3
"""Generate Level 2 Analytics Agent notebook with business use cases."""

import json


def md_cell(text, cell_id):
    """Create a markdown cell."""
    lines = text.split("\n")
    source = [line + "\n" for line in lines[:-1]] + [lines[-1]] if lines else []
    return {"cell_type": "markdown", "id": cell_id, "metadata": {}, "source": source}


def code_cell(code, cell_id):
    """Create a code cell."""
    lines = code.split("\n")
    source = [line + "\n" for line in lines[:-1]] + [lines[-1]] if lines else []
    return {
        "cell_type": "code",
        "execution_count": None,
        "id": cell_id,
        "metadata": {},
        "outputs": [],
        "source": source,
    }


# Notebook structure
notebook = {
    "cells": [],
    "metadata": {
        "kernelspec": {
            "display_name": "venv (3.13.12)",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "codemirror_mode": {"name": "ipython", "version": 3},
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": "3.13.12",
        },
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

# Title
notebook["cells"].append(
    md_cell(
        """# Level 2 — Analytics & Pattern Discovery Agent
### Business Analytics Demo

---

## What is the Level 2 Agent?

The **Level 2 Analytics Agent** is your data science co-pilot. It transforms natural language questions into SQL queries, performs customer segmentation using machine learning, analyzes sentiment from social media, and generates actionable insights.

| What you can ask | What it does |
|---|---|
| "Segment customers by risk and engagement" | K-means clustering with visualizations |
| "What's the average balance for high-value customers?" | SQL analytics with aggregations |
| "Analyze sentiment from customer feedback" | RoBERTa-based sentiment analysis |
| "Summarize this support ticket" | BERT text summarization |
| "Show me Customer 360 view for CUST-005" | Unified view across CRM, sales, social, support |

**No coding required.** Ask in plain English — the agent does the analysis.

---

## How it works

```
Your question
     │
     ▼
Orchestrator routes to Level 2
     │
     ▼
Level 2 decides: SQL query? Segmentation? Sentiment analysis?
     │
     ▼
Executes analysis (SQL/K-means/NLP)
     │
     ▼
Generates visualizations (charts, tables)
     │
     ▼
Guardrail checks output for PII
     │
     ▼
Returns insights + charts
```

Every query is logged to the audit trail with full traceability.

---""",
        "title",
    )
)

# Setup
notebook["cells"].append(
    md_cell(
        """## Setup

Run this cell once to initialize the system.""",
        "setup-header",
    )
)

notebook["cells"].append(
    code_cell(
        """import sys, os
from pathlib import Path

# Resolve project root
_here = Path(os.getcwd())
_root = _here.parent if _here.name == "notebooks" else _here
_notebooks = _root / "notebooks" if _here.name != "notebooks" else _here
os.chdir(_root)
sys.path.insert(0, str(_root))
sys.path.insert(0, str(_notebooks))

from dotenv import load_dotenv
load_dotenv()

# Import all necessary modules
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display, HTML, Markdown, Image
import json

# Import Level 2 tools
from nonagentic.tools.analytics import run_sql_query, generate_segment
from nonagentic.tools.customer360 import get_customer_360, get_sales_analytics, get_sentiment_analytics, get_support_analytics
from nonagentic.tools.nlp import analyze_sentiment, summarize_text, analyze_batch_sentiment
from nonagentic.tools.visualisation import visualise

# Import display helpers
from utils.display_helpers import display_card, display_metrics, display_bar_chart

print("✅ Level 2 Analytics Agent Ready")
print(f"📁 Project root: {_root}")""",
        "setup",
    )
)

# Use Case 1: Customer Segmentation
notebook["cells"].append(
    md_cell(
        """---
## Use Case 1 — Customer Segmentation (K-means Clustering)

**Business scenario**: The marketing team wants to identify distinct customer groups based on risk and engagement scores to tailor campaigns.

The agent uses **K-means clustering** to automatically discover customer segments. No manual rules needed — the algorithm finds natural groupings in the data.""",
        "uc1-header",
    )
)

notebook["cells"].append(
    code_cell(
        """# Perform K-means segmentation
result = generate_segment(algorithm="kmeans", n_clusters=4)

segments = result.get("segments", [])

# Display segment summary
display(HTML('<div style="font-size:18px;font-weight:600;margin:16px 0">🎯 Customer Segments Discovered</div>'))

# Create summary table
seg_data = []
for seg in segments:
    seg_data.append({
        "Segment": seg["label"],
        "Size": seg["size"],
        "Avg Risk Score": f"{seg['avg_risk_score']:.3f}",
        "Avg Engagement": f"{seg['avg_engagement_score']:.3f}"
    })

df = pd.DataFrame(seg_data)
styled = df.style.set_table_styles([
    {'selector': 'th', 'props': [('background', '#667eea'), ('color', 'white'), ('padding', '10px')]},
    {'selector': 'td', 'props': [('padding', '10px'), ('border-bottom', '1px solid #e2e8f0')]}
]).hide(axis='index')

display(styled)

# Generate visualization
chart_path = visualise(segments, chart_type="bar", title="Customer Segments", request_id="demo-seg")
if chart_path:
    display(HTML(f'<div style="margin:20px 0"><strong>📊 Visualization:</strong></div>'))
    display(Image(filename=chart_path))

# Business insights
display_card("Business Insights", 
    f"Identified {len(segments)} distinct customer segments. "
    f"Largest segment: {max(segments, key=lambda x: x['size'])['label']} with {max(segments, key=lambda x: x['size'])['size']} customers. "
    "Use these segments for targeted marketing campaigns.",
    emoji="💡", color="#10b981")""",
        "uc1-code",
    )
)

# Use Case 2: SQL Analytics
notebook["cells"].append(
    md_cell(
        """---
## Use Case 2 — SQL Analytics (Top Customers by Balance)

**Business scenario**: The relationship manager needs to identify top customers by account balance for VIP treatment.

The agent generates and executes SQL queries automatically from natural language.""",
        "uc2-header",
    )
)

notebook["cells"].append(
    code_cell(
        """# Query top customers by balance
sql = \"\"\"
SELECT customer_id, full_name, segment, account_balance, risk_score, engagement_score
FROM customers
WHERE account_balance > 10000
ORDER BY account_balance DESC
LIMIT 10
\"\"\"

result = run_sql_query(sql)

if "rows" in result and result["rows"]:
    display(HTML('<div style="font-size:18px;font-weight:600;margin:16px 0">💰 Top 10 Customers by Balance</div>'))
    
    df = pd.DataFrame(result["rows"])
    
    # Format currency
    df["account_balance"] = df["account_balance"].apply(lambda x: f"${x:,.2f}")
    df["risk_score"] = df["risk_score"].apply(lambda x: f"{x:.3f}")
    df["engagement_score"] = df["engagement_score"].apply(lambda x: f"{x:.3f}")
    
    styled = df.style.set_table_styles([
        {'selector': 'th', 'props': [('background', '#667eea'), ('color', 'white'), ('padding', '8px')]},
        {'selector': 'td', 'props': [('padding', '8px'), ('font-size', '13px')]}
    ]).hide(axis='index')
    
    display(styled)
    
    # Calculate metrics
    total_balance = sum(float(r["account_balance"]) for r in result["rows"])
    avg_balance = total_balance / len(result["rows"])
    
    display_metrics({
        "Total Balance": f"${total_balance:,.2f}",
        "Average Balance": f"${avg_balance:,.2f}",
        "Customers": len(result["rows"])
    })
else:
    display_card("Error", "No data returned", emoji="❌", color="#ef4444")""",
        "uc2-code",
    )
)

# Use Case 3: Risk Analysis
notebook["cells"].append(
    md_cell(
        """---
## Use Case 3 — Risk Analysis (High-Risk Customers)

**Business scenario**: Compliance needs to identify high-risk customers for enhanced due diligence.

The agent filters customers by risk score and analyzes their characteristics.""",
        "uc3-header",
    )
)

notebook["cells"].append(
    code_cell(
        """# Query high-risk customers
sql = \"\"\"
SELECT segment, COUNT(*) as count, AVG(risk_score) as avg_risk, AVG(engagement_score) as avg_engagement
FROM customers
WHERE risk_score > 0.7
GROUP BY segment
ORDER BY count DESC
\"\"\"

result = run_sql_query(sql)

if "rows" in result and result["rows"]:
    display(HTML('<div style="font-size:18px;font-weight:600;margin:16px 0">⚠️ High-Risk Customer Analysis</div>'))
    
    df = pd.DataFrame(result["rows"])
    df["avg_risk"] = df["avg_risk"].apply(lambda x: f"{x:.3f}")
    df["avg_engagement"] = df["avg_engagement"].apply(lambda x: f"{x:.3f}")
    
    styled = df.style.set_table_styles([
        {'selector': 'th', 'props': [('background', '#ef4444'), ('color', 'white'), ('padding', '10px')]},
        {'selector': 'td', 'props': [('padding', '10px')]}
    ]).hide(axis='index')
    
    display(styled)
    
    # Visualization
    segments = {row["segment"]: row["count"] for row in result["rows"]}
    display_bar_chart(segments, "📊 High-Risk Customers by Segment", color="#ef4444")
    
    total_high_risk = sum(row["count"] for row in result["rows"])
    display_card("Risk Alert", 
        f"Found {total_high_risk} high-risk customers (risk score > 0.7). "
        "Recommend enhanced monitoring and KYC verification.",
        emoji="🚨", color="#ef4444")
else:
    display_card("Info", "No high-risk customers found", emoji="✅", color="#10b981")""",
        "uc3-code",
    )
)

# Use Case 4: Sentiment Analysis
notebook["cells"].append(
    md_cell(
        """---
## Use Case 4 — Sentiment Analysis (Social Media Feedback)

**Business scenario**: The brand team wants to understand customer sentiment from social media posts.

The agent uses **RoBERTa** (a state-of-the-art NLP model) to analyze sentiment automatically.""",
        "uc4-header",
    )
)

notebook["cells"].append(
    code_cell(
        """# Load social media data
with open("data/social_media.json") as f:
    social_data = json.load(f)

# Analyze sentiment for sample posts
sample_posts = social_data[:10]

display(HTML('<div style="font-size:18px;font-weight:600;margin:16px 0">😊 Sentiment Analysis Results</div>'))

# Analyze each post
results = []
for post in sample_posts:
    sentiment_result = analyze_sentiment(post["text"])
    results.append({
        "Text": post["text"][:60] + "..." if len(post["text"]) > 60 else post["text"],
        "Platform": post["platform"],
        "Sentiment": sentiment_result.get("sentiment", "unknown"),
        "Confidence": f"{sentiment_result.get('confidence', 0):.2%}"
    })

df = pd.DataFrame(results)

# Color code sentiment
def color_sentiment(val):
    colors = {
        "positive": "background-color: #d1fae5; color: #065f46",
        "negative": "background-color: #fee2e2; color: #991b1b",
        "neutral": "background-color: #fef3c7; color: #92400e"
    }
    return colors.get(val, "")

styled = df.style.map(color_sentiment, subset=["Sentiment"]).set_table_styles([
    {'selector': 'th', 'props': [('background', '#667eea'), ('color', 'white'), ('padding', '8px')]},
    {'selector': 'td', 'props': [('padding', '8px'), ('font-size', '13px')]}
]).hide(axis='index')

display(styled)

# Overall sentiment breakdown
sentiment_counts = {}
for r in results:
    sent = r["Sentiment"]
    sentiment_counts[sent] = sentiment_counts.get(sent, 0) + 1

display_bar_chart(sentiment_counts, "📊 Overall Sentiment Distribution", color="#8b5cf6")

# Business insight
positive_pct = sentiment_counts.get("positive", 0) / len(results) * 100
display_card("Sentiment Insights",
    f"Positive sentiment: {positive_pct:.1f}%. "
    f"Analyzed {len(results)} posts across {len(set(p['platform'] for p in sample_posts))} platforms. "
    "Monitor negative sentiment for brand reputation management.",
    emoji="📈", color="#8b5cf6")""",
        "uc4-code",
    )
)

# Use Case 5: Text Summarization
notebook["cells"].append(
    md_cell(
        """---
## Use Case 5 — Text Summarization (Support Tickets)

**Business scenario**: Support managers need quick summaries of lengthy support tickets.

The agent uses **BART** (a transformer model) to generate concise summaries.""",
        "uc5-header",
    )
)

notebook["cells"].append(
    code_cell(
        """# Load support tickets
with open("data/support_tickets.json") as f:
    support_data = json.load(f)

# Get a sample ticket with longer description
sample_ticket = support_data[0]

display(HTML('<div style="font-size:18px;font-weight:600;margin:16px 0">📝 Support Ticket Summarization</div>'))

# Display original ticket
display_card("Original Ticket",
    f"<strong>Ticket ID:</strong> {sample_ticket['ticket_id']}<br>"
    f"<strong>Type:</strong> {sample_ticket['type']}<br>"
    f"<strong>Priority:</strong> {sample_ticket['priority']}<br>"
    f"<strong>Description:</strong> {sample_ticket['description']}",
    emoji="📋", color="#3b82f6")

# Summarize (for demo, we'll show the description as-is since it's already short)
# In production, this would summarize longer text
summary_result = summarize_text(sample_ticket['description'])

if "summary" in summary_result:
    display_card("AI Summary",
        summary_result['summary'],
        emoji="✨", color="#10b981")
    
    if "compression_ratio" in summary_result:
        display_metrics({
            "Original Length": f"{summary_result['original_length']} words",
            "Summary Length": f"{summary_result['summary_length']} words",
            "Compression": f"{summary_result['compression_ratio']:.0%}"
        })
else:
    display_card("Note", "Text is already concise, no summarization needed", emoji="ℹ️", color="#3b82f6")""",
        "uc5-code",
    )
)

# Use Case 6: Customer 360 View
notebook["cells"].append(
    md_cell(
        """---
## Use Case 6 — Customer 360 View (Unified Data)

**Business scenario**: A relationship manager needs a complete view of a customer before a meeting.

The agent combines data from **CRM, sales, social media, and support** into one unified view.""",
        "uc6-header",
    )
)

notebook["cells"].append(
    code_cell(
        """# Get Customer 360 view
customer_id = "CUST-001"
customer_360 = get_customer_360(customer_id)

if "error" not in customer_360:
    display(HTML(f'<div style="font-size:18px;font-weight:600;margin:16px 0">👤 Customer 360 View: {customer_id}</div>'))
    
    # Customer Profile
    profile = customer_360["customer_profile"]
    display_card("Customer Profile",
        f"<strong>Name:</strong> {profile['full_name']}<br>"
        f"<strong>Segment:</strong> {profile['segment']}<br>"
        f"<strong>KYC Status:</strong> {profile['kyc_status']}<br>"
        f"<strong>Risk Score:</strong> {profile['risk_score']:.3f}<br>"
        f"<strong>Engagement:</strong> {profile['engagement_score']:.3f}<br>"
        f"<strong>Balance:</strong> ${profile['account_balance']:,.2f}",
        emoji="👤", color="#3b82f6")
    
    # Summary Metrics
    summary = customer_360["summary"]
    display_metrics({
        "Total Sales": f"${summary['total_sales_value']:,.2f}",
        "Transactions": summary['transaction_count'],
        "Social Posts": summary['social_engagement'],
        "Support Tickets": summary['support_tickets'],
        "Open Issues": summary['open_issues'],
        "Sentiment": summary['overall_sentiment'].upper()
    })
    
    # Sales Activity
    sales = customer_360["sales"]
    if sales["total_count"] > 0:
        display(HTML('<div style="margin-top:20px"><strong>💰 Sales Activity</strong></div>'))
        display_bar_chart(
            {ch: sum(1 for t in sales["transactions"] if t["channel"] == ch) for ch in sales["channels"]},
            "Transactions by Channel",
            color="#10b981"
        )
    
    # Social Media
    social = customer_360["social"]
    if social["total_count"] > 0:
        display(HTML('<div style="margin-top:20px"><strong>📱 Social Media Activity</strong></div>'))
        display_bar_chart(
            social["sentiment_breakdown"],
            "Sentiment Breakdown",
            color="#8b5cf6"
        )
    
    # Support Tickets
    support = customer_360["support"]
    if support["total_count"] > 0:
        display(HTML('<div style="margin-top:20px"><strong>🎫 Support Tickets</strong></div>'))
        display_bar_chart(
            {t: sum(1 for tk in support["tickets"] if tk["type"] == t) for t in support["ticket_types"]},
            "Tickets by Type",
            color="#ef4444"
        )
    
    # Business Insight
    display_card("360° Insights",
        f"Customer {customer_id} has generated ${summary['total_sales_value']:,.2f} in revenue across {summary['transaction_count']} transactions. "
        f"Overall sentiment is {summary['overall_sentiment']}. "
        f"{'⚠️ Has ' + str(summary['open_issues']) + ' open support issues.' if summary['open_issues'] > 0 else '✅ No open support issues.'}",
        emoji="🎯", color="#667eea")
else:
    display_card("Error", f"Customer {customer_id} not found", emoji="❌", color="#ef4444")""",
        "uc6-code",
    )
)

# Use Case 7: Sales Analytics
notebook["cells"].append(
    md_cell(
        """---
## Use Case 7 — Sales Analytics (Revenue by Product)

**Business scenario**: The sales team wants to understand which products generate the most revenue.

The agent analyzes sales transactions and identifies top-performing products.""",
        "uc7-header",
    )
)

notebook["cells"].append(
    code_cell(
        """# Get sales analytics
sales_analytics = get_sales_analytics()

display(HTML('<div style="font-size:18px;font-weight:600;margin:16px 0">💼 Sales Analytics Dashboard</div>'))

# Overall metrics
display_metrics({
    "Total Revenue": f"${sales_analytics['total_revenue']:,.2f}",
    "Transactions": sales_analytics['total_transactions'],
    "Avg Transaction": f"${sales_analytics['avg_transaction_value']:,.2f}",
    "Top Product": sales_analytics['top_product'].replace('_', ' ').title()
})

# Revenue by product
display(HTML('<div style="margin-top:20px"><strong>📊 Revenue by Product</strong></div>'))
display_bar_chart(
    sales_analytics['by_product'],
    "Revenue Distribution",
    color="#10b981"
)

# Transactions by channel
display(HTML('<div style="margin-top:20px"><strong>📱 Transactions by Channel</strong></div>'))
display_bar_chart(
    sales_analytics['by_channel'],
    "Channel Distribution",
    color="#3b82f6"
)

# Business insights
top_product = sales_analytics['top_product']
top_revenue = sales_analytics['by_product'][top_product]
display_card("Sales Insights",
    f"Top performing product: {top_product.replace('_', ' ').title()} with ${top_revenue:,.2f} in revenue. "
    f"Total of {sales_analytics['total_transactions']} transactions across {len(sales_analytics['by_channel'])} channels. "
    "Focus marketing efforts on top-performing products.",
    emoji="📈", color="#10b981")""",
        "uc7-code",
    )
)

# Use Case 8: Support Analytics
notebook["cells"].append(
    md_cell(
        """---
## Use Case 8 — Support Analytics (Ticket Analysis)

**Business scenario**: The support manager needs to understand ticket volume, types, and resolution times.

The agent analyzes support tickets to identify bottlenecks and improvement areas.""",
        "uc8-header",
    )
)

notebook["cells"].append(
    code_cell(
        """# Get support analytics
support_analytics = get_support_analytics()

display(HTML('<div style="font-size:18px;font-weight:600;margin:16px 0">🎫 Support Analytics Dashboard</div>'))

# Overall metrics
display_metrics({
    "Total Tickets": support_analytics['total_tickets'],
    "Open Tickets": support_analytics['open_tickets'],
    "High Priority": support_analytics['high_priority'],
    "Avg Resolution": f"{support_analytics['avg_resolution_hours']:.1f}h"
})

# Tickets by type
display(HTML('<div style="margin-top:20px"><strong>📋 Tickets by Type</strong></div>'))
display_bar_chart(
    support_analytics['by_type'],
    "Ticket Type Distribution",
    color="#ef4444"
)

# Tickets by status
display(HTML('<div style="margin-top:20px"><strong>📊 Tickets by Status</strong></div>'))
display_bar_chart(
    support_analytics['by_status'],
    "Ticket Status Distribution",
    color="#f59e0b"
)

# Business insights
most_common_type = max(support_analytics['by_type'].items(), key=lambda x: x[1])
display_card("Support Insights",
    f"Most common ticket type: {most_common_type[0].replace('_', ' ').title()} ({most_common_type[1]} tickets). "
    f"Average resolution time: {support_analytics['avg_resolution_hours']:.1f} hours. "
    f"{'⚠️ ' + str(support_analytics['open_tickets']) + ' tickets still open.' if support_analytics['open_tickets'] > 0 else '✅ All tickets resolved.'}",
    emoji="🎯", color="#ef4444")""",
        "uc8-code",
    )
)

# Summary
notebook["cells"].append(
    md_cell(
        """---
## Summary

| Use Case | What the agent does | Technology |
|---|---|---|
| **1. Customer Segmentation** | K-means clustering by risk & engagement | scikit-learn |
| **2. SQL Analytics** | Text-to-SQL query generation | LangChain + SQLAlchemy |
| **3. Risk Analysis** | Identify high-risk customers | SQL aggregations |
| **4. Sentiment Analysis** | Analyze social media sentiment | RoBERTa (transformers) |
| **5. Text Summarization** | Summarize support tickets | BART (transformers) |
| **6. Customer 360 View** | Unified view across all data sources | Multi-source integration |
| **7. Sales Analytics** | Revenue and product analysis | Pandas aggregations |
| **8. Support Analytics** | Ticket volume and resolution metrics | Pandas aggregations |

---

### Key Business Benefits

- **Data-Driven Decisions** — Discover patterns and insights automatically
- **No SQL Required** — Ask questions in plain English
- **ML-Powered** — K-means clustering, sentiment analysis, text summarization
- **Unified View** — Customer 360 across CRM, sales, social, support
- **Visualizations** — Automatic chart generation for presentations
- **Audit Trail** — Every query logged for compliance

---

### What Comes Next

Level 2 is the **analytical** layer. When you need to *act* on insights:

- **Level 3** — Execute actions (send emails, create cases, update records)
- **Level 4** — Strategic campaigns (multi-step workflows, A/B testing, KPI tracking)

---

### Technical Notes

**Models Used**:
- K-means clustering (scikit-learn)
- RoBERTa for sentiment analysis (cardiffnlp/twitter-roberta-base-sentiment-latest)
- BART for summarization (facebook/bart-large-cnn)

**Data Sources**:
- `data/customers.db` — Customer profiles (SQLite)
- `data/sales_transactions.json` — Sales data
- `data/social_media.json` — Social media posts
- `data/support_tickets.json` — Support tickets

**Charts Saved To**: `data/charts/`

**Audit Log**: `data/audit.jsonl`""",
        "summary",
    )
)

# Write notebook
output_path = "notebooks/level2_analytics_agent.ipynb"
with open(output_path, "w") as f:
    json.dump(notebook, f, indent=1, ensure_ascii=False)

print(f"✅ Level 2 Analytics notebook generated: {output_path}")
