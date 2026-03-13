# Analytics Agent — Use Cases & Code Paths

## Overview

The Analytics Agent handles 5 primary use cases from the notebook. Each use case demonstrates a different aspect of the agent's routing logic and MCP tool selection.

---

## Use Case 1: Customer Segmentation (K-means Clustering)

**Business Scenario**: Marketing team wants to identify distinct customer groups based on risk and engagement scores.

**Request Example**:
```
"Segment customers by risk and engagement scores into 4 groups"
```

**Routing Decision**:
- Request contains keyword: `"segment"`
- Routing: `analytics_agent` → `generate_segment`

**Code Path**:
```python
# agentic/analytics_agent.py
analytics_agent(state)
    ↓
_extract_sql_query(request) → None (no SQL)
    ↓
any(w in request.lower() for w in ["segment", "cluster", "group"]) → True
    ↓
filters = _extract_filters(request) → {}
    ↓
analytics_server.invoke_tool("generate_segment", filters={}, algorithm="rules")
    ↓
mcp_servers/analytics_server.py → AnalyticsServer.invoke_tool()
    ↓
nonagentic.tools.analytics.generate_segment(filters={}, algorithm="rules")
```

**MCP Call**:
```python
{
    "server": "analytics",
    "tool": "generate_segment",
    "params": {"filters": {}, "algorithm": "rules"},
    "result": {
        "segments": [
            {"label": "casual", "size": 31, "avg_risk_score": 0.234, "avg_engagement": 0.444},
            {"label": "dormant_vip", "size": 53, "avg_risk_score": 0.255, "avg_engagement": 0.246},
            {"label": "at_risk", "size": 39, "avg_risk_score": 0.246, "avg_engagement": 0.335},
            {"label": "vip", "size": 53, "avg_risk_score": 0.126, "avg_engagement": 0.739},
            {"label": "new", "size": 32, "avg_risk_score": 0.350, "avg_engagement": 0.251}
        ],
        "segment_count": 5,
        "total_customers": 208
    }
}
```

**Memory Recording**:
```python
memory_manager.agent_observation.record_observation(
    "analytics",
    "Performed analysis: Largest segment: dormant_vip with 53 customers",
    {"request": "Segment customers by risk and engagement scores into 4 groups"}
)
```

**Response**:
```
Generated 5 segments:
  - casual: 31 customers
  - dormant_vip: 53 customers
  - at_risk: 39 customers
  - vip: 53 customers
  - new: 32 customers

Insights:
  • Largest segment: dormant_vip with 53 customers
```

---

## Use Case 2: SQL Analytics (Top Customers by Lifetime Value)

**Business Scenario**: Account manager needs to identify top customers by lifetime value for VIP treatment.

**Request Example**:
```
"Run this SQL query: SELECT customer_id, full_name, segment, lifetime_value, fraud_score, engagement_score FROM customers ORDER BY lifetime_value DESC LIMIT 10"
```

**Routing Decision**:
- Request contains SQL query (SELECT pattern detected)
- Routing: `analytics_agent` → `run_sql_query`

**Code Path**:
```python
# agentic/analytics_agent.py
analytics_agent(state)
    ↓
sql = _extract_sql_query(request)
    ↓
match = re.search(r"(SELECT\s+.*?)(?:;|\n\n|$)", request, re.IGNORECASE | re.DOTALL)
    ↓
sql = "SELECT customer_id, full_name, segment, lifetime_value, fraud_score, engagement_score FROM customers ORDER BY lifetime_value DESC LIMIT 10"
    ↓
analytics_server.invoke_tool("run_sql_query", sql=sql, max_rows=100)
    ↓
nonagentic.tools.analytics.run_sql_query(sql=sql, max_rows=100)
```

**MCP Call**:
```python
{
    "server": "analytics",
    "tool": "run_sql_query",
    "params": {"sql": "SELECT customer_id, full_name, segment, lifetime_value, fraud_score, engagement_score FROM customers ORDER BY lifetime_value DESC LIMIT 10"},
    "result": {
        "rows": [
            {"customer_id": "CUST-004", "full_name": "Sharon Kennedy", "segment": "at_risk", "lifetime_value": 89205.38, "fraud_score": 0.300, "engagement_score": 0.440},
            {"customer_id": "CUST-104", "full_name": "الأستاذ ثروت خندف", "segment": "dormant_vip", "lifetime_value": 88661.71, "fraud_score": 0.570, "engagement_score": 0.200},
            ...
        ],
        "row_count": 10,
        "columns": ["customer_id", "full_name", "segment", "lifetime_value", "fraud_score", "engagement_score"]
    }
}
```

**Memory Recording**:
```python
memory_manager.agent_observation.record_observation(
    "analytics",
    "Performed analysis: Query returned 10 rows",
    {"request": "Run this SQL query: ..."}
)
```

---

## Use Case 3: Fraud Risk Analysis (High-Fraud-Risk Customers)

**Business Scenario**: Trust & Safety needs to identify high-fraud-risk customers for enhanced verification.

**Request Example**:
```
"Run this SQL query: SELECT segment, COUNT(*) as count, AVG(fraud_score) as avg_risk, AVG(engagement_score) as avg_engagement FROM customers WHERE fraud_score > 0.7 GROUP BY segment ORDER BY count DESC"
```

**Routing Decision**:
- Request contains SQL query (SELECT pattern detected)
- Routing: `analytics_agent` → `run_sql_query`

**Code Path**: Same as UC2 (SQL extraction and execution)

**MCP Call**:
```python
{
    "server": "analytics",
    "tool": "run_sql_query",
    "params": {"sql": "SELECT segment, COUNT(*) as count, AVG(fraud_score) as avg_risk, AVG(engagement_score) as avg_engagement FROM customers WHERE fraud_score > 0.7 GROUP BY segment ORDER BY count DESC"},
    "result": {
        "rows": [
            {"segment": "at_risk", "count": 17, "avg_risk": 0.838, "avg_engagement": 0.448},
            {"segment": "dormant_vip", "count": 16, "avg_risk": 0.814, "avg_engagement": 0.143},
            ...
        ],
        "row_count": 5,
        "columns": ["segment", "count", "avg_risk", "avg_engagement"]
    }
}
```

**Memory Recording**:
```python
memory_manager.agent_observation.record_observation(
    "analytics",
    "Performed analysis: Query returned 5 rows",
    {"request": "Run this SQL query: ..."}
)
```

---

## Use Case 4: Sales Analytics (Revenue by Category)

**Business Scenario**: Sales team wants to understand which categories generate the most revenue.

**Request Example**:
```
"Analyze sales analytics by product category and channel"
```

**Routing Decision**:
- Request contains keyword: `"analytics"`
- No SQL query detected
- No segmentation keywords
- Routing: `analytics_agent` → default SQL query

**Code Path**:
```python
# agentic/analytics_agent.py
analytics_agent(state)
    ↓
sql = _extract_sql_query(request) → None
    ↓
any(w in request.lower() for w in ["segment", "cluster", "group"]) → False
    ↓
# Default fallback
sql = "SELECT segment, COUNT(*) as count FROM customers GROUP BY segment"
    ↓
analytics_server.invoke_tool("run_sql_query", sql=sql, max_rows=100)
```

**MCP Call**:
```python
{
    "server": "analytics",
    "tool": "run_sql_query",
    "params": {"sql": "SELECT segment, COUNT(*) as count FROM customers GROUP BY segment"},
    "result": {
        "rows": [...],
        "row_count": 5,
        "columns": ["segment", "count"]
    }
}
```

---

## Use Case 5: Support Analytics (Ticket Analysis)

**Business Scenario**: Support manager needs to understand ticket volume, types, and resolution times.

**Request Example**:
```
"Analyze support ticket volume, types, and resolution times"
```

**Routing Decision**: Same as UC4 (default SQL query)

**Code Path**: Same as UC4

---

## Decision Tree

```
analytics_agent(request)
    │
    ├─ _extract_sql_query(request) returns SQL?
    │  ├─ YES → invoke_tool("run_sql_query", sql=..., max_rows=100)
    │  │        (UC2, UC3, UC4, UC5)
    │  │
    │  └─ NO → Check for segmentation keywords
    │     │
    │     ├─ "segment" | "cluster" | "group" found?
    │     │  ├─ YES → invoke_tool("generate_segment", filters=..., algorithm="rules")
    │     │  │        (UC1)
    │     │  │
    │     │  └─ NO → Use default SQL query
    │     │           invoke_tool("run_sql_query", sql="SELECT segment, COUNT(*) FROM customers GROUP BY segment")
    │     │           (UC4, UC5)
    │
    └─ Record observation to memory
       memory_manager.agent_observation.record_observation(...)
```

---

## Summary Table

| UC | Business Goal | Request Pattern | Tool | Routing |
|----|---------------|-----------------|------|---------|
| 1 | Customer Segmentation | "segment customers" | `generate_segment` | Keyword match |
| 2 | Top Customers | "Run this SQL query: SELECT..." | `run_sql_query` | SQL extraction |
| 3 | Fraud Risk | "Run this SQL query: WHERE fraud_score > 0.7" | `run_sql_query` | SQL extraction |
| 4 | Sales Analytics | "Analyze sales analytics" | `run_sql_query` | Default fallback |
| 5 | Support Analytics | "Analyze support tickets" | `run_sql_query` | Default fallback |

---

## Key Insights

1. **SQL Priority**: SQL extraction is checked first to avoid keyword conflicts
2. **Keyword Matching**: Segmentation keywords trigger `generate_segment`
3. **Default Fallback**: Unmatched requests use a default segment query
4. **Memory Recording**: All analyses are recorded to `agent_observation` memory
5. **No Evaluation**: Analytics results are final; no evaluation agent is triggered
