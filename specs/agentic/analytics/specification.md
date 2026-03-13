# Analytics Agent Specification

## Overview

The **Analytics Agent** is a specialized agent that performs data analysis, segmentation, and SQL queries. It is invoked by the Orchestrator when the intent is classified as `analytics`.

**Agent ID**: `analytics`  
**MCP Servers**: `analytics_server`  
**Autonomy Level**: `medium`  
**Memory Access**: `conversation`, `agent_observation`

---

## Routing Logic

The analytics agent determines which tool to invoke based on request content:

```python
# Priority 1: SQL query extraction
if _extract_sql_query(request):
    → invoke_tool("run_sql_query", sql=..., max_rows=100)

# Priority 2: Segmentation keywords
elif any(w in request.lower() for w in ["segment", "cluster", "group"]):
    → invoke_tool("generate_segment", filters=..., algorithm="rules")

# Priority 3: Default fallback
else:
    → invoke_tool("run_sql_query", sql="SELECT segment, COUNT(*) FROM customers GROUP BY segment")
```

### SQL Extraction Patterns

1. **Code block**: ` ```sql ... ``` `
2. **Multi-line SELECT**: `SELECT ... (;|newline|EOF)`
3. **None found**: Return `None`

### Filter Extraction

Keyword-based filter extraction from request:

| Keyword | Filter | Value |
|---------|--------|-------|
| `unverified` | `identity_status` | `unverified` |
| `vip` | `segment` | `vip` |

---

## MCP Tools

### Tool 1: `run_sql_query`

**Purpose**: Execute read-only SQL queries on the customer database.

**Signature**:
```python
run_sql_query(sql: str, max_rows: int = 100) -> dict
```

**Parameters**:
- `sql` (string, required): SQL SELECT query
- `max_rows` (integer, optional): Maximum rows to return (default: 100)

**Returns**:
```python
{
    "rows": list[dict],           # Query results
    "row_count": int,             # Number of rows returned
    "columns": list[str],         # Column names
    "error": str | None           # Error message if query failed
}
```

**Constraints**:
- SELECT queries only (read-only)
- Max 100 rows by default
- SQL injection protection via parameterized queries

**Delegates To**: `nonagentic.tools.analytics.run_sql_query`

---

### Tool 2: `generate_segment`

**Purpose**: Generate customer segments using rules or ML algorithms.

**Signature**:
```python
generate_segment(filters: dict | None = None, algorithm: str = "rules") -> dict
```

**Parameters**:
- `filters` (object, optional): Filter criteria (e.g. `{"segment": "vip"}`)
- `algorithm` (string, optional): `"rules"` or `"kmeans"` (default: `"rules"`)

**Returns**:
```python
{
    "segments": list[dict],       # Segment definitions
    "segment_count": int,         # Number of segments
    "total_customers": int,       # Total customers in segments
    "error": str | None           # Error message if segmentation failed
}
```

**Segment Object**:
```python
{
    "label": str,                 # Segment name (e.g. "vip", "at_risk")
    "size": int,                  # Number of customers in segment
    "avg_risk_score": float,      # Average risk score
    "avg_engagement": float       # Average engagement score
}
```

**Algorithms**:
- `"rules"`: Rule-based segmentation (fast, deterministic)
- `"kmeans"`: K-means clustering (ML-based, 4-5 clusters)

**Delegates To**: `nonagentic.tools.analytics.generate_segment`

---

## Decision Rules

| Condition | Action | Tool |
|-----------|--------|------|
| SQL query detected in request | Execute SQL | `run_sql_query` |
| Keywords: segment, cluster, group | Generate segments | `generate_segment` |
| No SQL, no keywords | Default segment query | `run_sql_query` |
| Error in tool execution | Return error dict | N/A |

---

## State Updates

The analytics agent returns the following state updates:

```python
{
    "active_agent": "analytics",
    "agent_history": ["analytics"],
    "mcp_calls": [
        {
            "server": "analytics",
            "tool": "run_sql_query" | "generate_segment",
            "params": {...},
            "result": {...}
        }
    ],
    "intermediate_results": [
        {
            "agent": "analytics",
            "result": {...},
            "insights": [...]
        }
    ],
    "final_result": {...},
    "messages": [AIMessage(content=...)],
    "audit_trail": [
        {
            "agent": "analytics",
            "action": "perform_analysis",
            "mcp_calls": 1
        }
    ]
}
```

---

## Memory Recording

After analysis, the agent records an observation to `agent_observation` memory:

```python
memory_manager.agent_observation.record_observation(
    agent_name="analytics",
    observation=f"Performed analysis: {insights[0]}",
    metadata={"request": request}
)
```

This allows the system to learn from past analyses and track patterns over time.

---

## Insight Generation

The agent generates insights from the result:

**For segmentation results**:
- Identifies the largest segment by customer count
- Example: "Largest segment: dormant_vip with 53 customers"

**For SQL results**:
- Reports row count
- Example: "Query returned 10 rows"

---

## Error Handling

If a tool execution fails:

```python
{
    "error": "Analytics error: <error_message>",
    "final_result": None,
    "messages": [AIMessage(content="Analytics error: ...")]
}
```

---

## Use Cases

| Use Case | Request Pattern | Tool | Result |
|----------|-----------------|------|--------|
| Customer Segmentation | "Segment customers by..." | `generate_segment` | 5 segments with metrics |
| Top Customers | "Top 10 customers by..." | `run_sql_query` | 10 rows with customer data |
| Fraud Risk | "High-fraud-risk customers" | `run_sql_query` | Filtered rows by fraud score |
| Sales Analytics | "Revenue by category" | `run_sql_query` | Aggregated sales data |
| Support Analytics | "Ticket volume by type" | `run_sql_query` | Aggregated ticket data |

---

## Evaluation

The analytics agent does **not** trigger evaluation. Results are returned directly to the user.

**Routing After Analytics**:
```
analytics_agent → should_evaluate() → END
```

Only `workflow` and `action` agents trigger the evaluation agent.

---

## Limitations

- **Read-only**: No INSERT, UPDATE, DELETE operations
- **Max rows**: Limited to 100 rows by default
- **In-process memory**: Observations are not persisted to external storage
- **No replanning**: Analytics results are final; no automatic replanning
