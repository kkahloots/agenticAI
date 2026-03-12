# Level 2 Analytics Agent - Documentation

## Overview

The Level 2 Analytics Agent is your data science co-pilot. It transforms natural language questions into actionable insights using SQL analytics, machine learning, and NLP.

**Key Capabilities**:
- 🎯 K-means customer segmentation
- 📊 Text-to-SQL query generation
- 😊 Sentiment analysis (RoBERTa)
- 📝 Text summarization (BART)
- 👤 Customer 360 view (multi-source integration)
- 📈 Automated visualizations

---

## Quick Start

### 1. Install Dependencies

**Core features** (K-means, SQL, Customer 360, visualizations):
```bash
pip install matplotlib pandas scikit-learn numpy ipywidgets
```

**NLP features** (Sentiment analysis, Summarization — optional, ~2.5GB model download on first use):
```bash
pip install transformers torch sentencepiece
```

### 2. Generate Sample Data

```bash
python scripts/generate_customer360_data.py
```

Creates:
- `data/sales_transactions.json` (229 transactions)
- `data/social_media.json` (79 posts)
- `data/support_tickets.json` (58 tickets)

### 3. Run the Notebook

```bash
jupyter notebook notebooks/level2_analytics_agent.ipynb
```

### 4. Test Features

```bash
python test_level2.py
```

---

## Features

### 1. K-means Customer Segmentation

**What it does**: Automatically discovers customer groups based on risk and engagement scores.

**Example**:
```python
from src.tools.analytics import generate_segment

segments = generate_segment(algorithm='kmeans', n_clusters=4)
# Returns: 4 clusters with avg risk/engagement scores
```

**Use Cases**:
- Identify high-value, low-engagement customers for retention
- Find high-risk segments for enhanced monitoring
- Discover natural customer groupings for targeted campaigns

**Technology**: scikit-learn KMeans clustering

---

### 2. SQL Analytics

**What it does**: Converts natural language to SQL queries and executes them safely.

**Example**:
```python
from src.tools.analytics import run_sql_query

sql = "SELECT segment, AVG(account_balance) FROM customers GROUP BY segment"
result = run_sql_query(sql)
# Returns: {rows: [...], row_count: 5, truncated: False}
```

**Safety Features**:
- SQL injection protection (blocks INSERT/UPDATE/DELETE)
- Read-only queries enforced
- Row limit (default 10,000)
- Automatic schema binding

**Technology**: LangChain + SQLAlchemy

---

### 3. Sentiment Analysis

**What it does**: Analyzes customer sentiment from social media posts and feedback.

**Example**:
```python
from src.tools.nlp import analyze_sentiment

result = analyze_sentiment("Great banking app!")
# Returns: {sentiment: 'positive', confidence: 0.95, scores: {...}}
```

**Use Cases**:
- Monitor brand reputation on social media
- Analyze customer feedback sentiment
- Identify negative sentiment for proactive support

**Technology**: RoBERTa (cardiffnlp/twitter-roberta-base-sentiment-latest)

**Requirements**: `pip install transformers torch`

---

### 4. Text Summarization

**What it does**: Generates concise summaries of long text (support tickets, emails).

**Example**:
```python
from src.tools.nlp import summarize_text

result = summarize_text(long_text, max_length=130)
# Returns: {summary: "...", compression_ratio: 0.3}
```

**Use Cases**:
- Summarize lengthy support tickets
- Create executive summaries of customer feedback
- Condense email threads

**Technology**: BART (facebook/bart-large-cnn)

**Requirements**: `pip install transformers torch`

---

### 5. Customer 360 View

**What it does**: Unified view combining CRM, sales, social media, and support data.

**Example**:
```python
from src.tools.customer360 import get_customer_360

customer = get_customer_360("CUST-001")
# Returns: {customer_profile, sales, social, support, summary}
```

**Data Sources**:
- **CRM**: Customer profile, KYC status, risk scores
- **Sales**: Transaction history, revenue, channels
- **Social**: Posts, sentiment, engagement
- **Support**: Tickets, resolution times, types

**Use Cases**:
- Pre-meeting customer briefings
- Relationship manager dashboards
- Holistic customer health scoring

---

### 6. Sales Analytics

**What it does**: Analyzes sales transactions for revenue insights.

**Example**:
```python
from src.tools.customer360 import get_sales_analytics

analytics = get_sales_analytics()
# Returns: {total_revenue, by_product, by_channel, top_product}
```

**Metrics**:
- Total revenue and transaction count
- Revenue by product
- Transactions by channel
- Average transaction value

---

### 7. Support Analytics

**What it does**: Analyzes support tickets for operational insights.

**Example**:
```python
from src.tools.customer360 import get_support_analytics

analytics = get_support_analytics()
# Returns: {total_tickets, by_type, by_status, avg_resolution_hours}
```

**Metrics**:
- Ticket volume by type
- Open vs resolved tickets
- Average resolution time
- High priority ticket count

---

### 8. Visualizations

**What it does**: Automatically generates charts from segment data.

**Example**:
```python
from src.tools.visualisation import visualise

chart_path = visualise(segments, chart_type="bar", title="Customer Segments")
# Saves to: data/charts/{request_id}.png
```

**Chart Types**:
- Bar charts (segment sizes, risk scores)
- Line charts (trends)
- Dual charts (size + metrics)

**Technology**: matplotlib

---

## Architecture

```
Level 2 Agent (src/agents/level2.py)
│
├── SQL Analytics
│   ├── Text-to-SQL (LangChain)
│   ├── Query execution (SQLAlchemy)
│   └── Safety guards
│
├── Machine Learning
│   ├── K-means clustering (scikit-learn)
│   └── Rule-based segmentation
│
├── NLP (Optional)
│   ├── Sentiment analysis (RoBERTa)
│   ├── Text summarization (BART)
│   └── Key phrase extraction
│
├── Customer 360
│   ├── CRM integration
│   ├── Sales data
│   ├── Social media
│   └── Support tickets
│
├── Visualization
│   └── Chart generation (matplotlib)
│
└── Guardrails
    ├── PII redaction
    └── Audit logging
```

---

## Use Cases

### Business Scenarios

| Scenario | Solution | Feature |
|----------|----------|---------|
| "Identify customers for retention campaign" | K-means segmentation | Segmentation |
| "What's the average balance of high-value customers?" | SQL query | SQL Analytics |
| "How do customers feel about our new app?" | Sentiment analysis | NLP |
| "Summarize this 500-word support ticket" | Text summarization | NLP |
| "Show me everything about customer CUST-001" | Customer 360 view | Integration |
| "Which products generate most revenue?" | Sales analytics | Analytics |
| "What's our average ticket resolution time?" | Support analytics | Analytics |

---

## Configuration

### Environment Variables

```bash
# SQL Analytics
SQL_MAX_ROWS=10000              # Max rows per query

# Guardrails
GUARDRAIL_ENABLED=true          # Enable PII redaction

# Charts
CHART_OUTPUT_DIR=data/charts    # Chart save location

# Database
DATABASE_URL=sqlite:///data/customers.db
```

### Model Configuration

**Sentiment Analysis**:
- Model: `cardiffnlp/twitter-roberta-base-sentiment-latest`
- Size: ~500MB
- First load: 5-10 seconds

**Text Summarization**:
- Model: `facebook/bart-large-cnn`
- Size: ~1.5GB
- First load: 10-15 seconds

Models are cached after first load.

---

## Performance

### Benchmarks

| Operation | Time | Notes |
|-----------|------|-------|
| K-means (100 customers) | <1s | Fast |
| SQL query | <100ms | Depends on complexity |
| Sentiment analysis (1 text) | ~200ms | After model load |
| Sentiment analysis (batch 100) | ~5s | Efficient batching |
| Text summarization | ~1-2s | Depends on length |
| Customer 360 view | <500ms | Multi-source aggregation |

### Memory Requirements

- Core features: ~500MB RAM
- With NLP models: ~2.5GB RAM

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'sklearn'"

**Solution**:
```bash
pip install scikit-learn
```

### "ModuleNotFoundError: No module named 'transformers'"

**Solution**: NLP features are optional. Either:
1. Install: `pip install transformers torch`
2. Skip NLP use cases (6 of 8 still work)

### "K-means returns empty segments"

**Cause**: Not enough customers in filtered data

**Solution**: Reduce filters or increase customer count

### "Charts not displaying in notebook"

**Solution**: Ensure matplotlib is installed and use `Image(filename=path)`

### "Sentiment analysis is slow"

**Cause**: Model downloads on first use

**Solution**: Wait for initial download (5-10 min), subsequent calls are fast

---

## API Reference

### Analytics Module

```python
from src.tools.analytics import run_sql_query, generate_segment

# SQL query
result = run_sql_query(sql, params=None, max_rows=10000)

# Segmentation
segments = generate_segment(filters=None, algorithm='kmeans', n_clusters=3)
```

### NLP Module

```python
from src.tools.nlp import analyze_sentiment, summarize_text

# Sentiment
result = analyze_sentiment(text)

# Summarization
summary = summarize_text(text, max_length=130, min_length=30)
```

### Customer 360 Module

```python
from src.tools.customer360 import (
    get_customer_360,
    get_sales_analytics,
    get_sentiment_analytics,
    get_support_analytics
)

# Customer 360
customer = get_customer_360(customer_id)

# Analytics
sales = get_sales_analytics(filters=None)
sentiment = get_sentiment_analytics(filters=None)
support = get_support_analytics(filters=None)
```

---

## Testing

### Unit Tests

```bash
pytest tests/test_analytics.py -v
```

### Integration Tests

```bash
python test_level2.py
```

### Notebook Tests

Run all cells in `notebooks/level2_analytics_agent.ipynb`

---

## Deployment

### Production Checklist

- [ ] Install all dependencies
- [ ] Configure environment variables
- [ ] Test with production data
- [ ] Set up monitoring (Langfuse)
- [ ] Configure audit trail retention
- [ ] Test guardrails
- [ ] Benchmark performance
- [ ] Document model versions

### Scaling Considerations

- Use batch processing for sentiment analysis
- Cache frequently accessed Customer 360 views
- Consider model quantization for memory savings
- Use read replicas for SQL queries
- Implement rate limiting for API endpoints

---

## Resources

- `notebooks/level2_analytics_agent.ipynb` - Interactive demo
- `test_level2.py` - Feature tests
- `scripts/generate_level2_notebook.py` - Notebook generator
- `specs/02-level2-analytics/` - Detailed specifications

---

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review test output: `python test_level2.py`
3. Check logs in `data/audit.jsonl`
4. Review Langfuse traces (if enabled)

---

**Last Updated**: 2026-03-12  
**Version**: 1.0  
**Status**: Production Ready
