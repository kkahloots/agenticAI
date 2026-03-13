# Analytics MCP Server — Tool Catalogue

## Server Overview

**Server ID**: `analytics`  
**Description**: SQL queries, segmentation, and analytics  
**Location**: `mcp_servers/analytics_server.py`  
**Base Class**: `MCPServer`

---

## Tool 1: `run_sql_query`

### Purpose
Execute read-only SQL queries on the customer database.

### Signature
```python
run_sql_query(sql: str, max_rows: int = 100) -> dict
```

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `sql` | string | Yes | — | SQL SELECT query to execute |
| `max_rows` | integer | No | 100 | Maximum number of rows to return |

### Return Schema

```python
{
    "rows": list[dict],           # Query result rows
    "row_count": int,             # Number of rows returned
    "columns": list[str],         # Column names from query
    "error": str | None           # Error message if query failed
}
```

### Example Usage

**Request**:
```python
analytics_server.invoke_tool(
    "run_sql_query",
    sql="SELECT customer_id, segment, lifetime_value FROM customers ORDER BY lifetime_value DESC LIMIT 10",
    max_rows=100
)
```

**Response**:
```python
{
    "rows": [
        {"customer_id": "CUST-004", "segment": "at_risk", "lifetime_value": 89205.38},
        {"customer_id": "CUST-104", "segment": "dormant_vip", "lifetime_value": 88661.71},
        ...
    ],
    "row_count": 10,
    "columns": ["customer_id", "segment", "lifetime_value"],
    "error": None
}
```

### Constraints

- **Read-only**: Only SELECT queries allowed
- **Max rows**: Limited to `max_rows` parameter (default 100)
- **SQL injection protection**: Parameterized queries
- **Timeout**: Query execution timeout (implementation-dependent)

### Error Handling

**Invalid SQL**:
```python
{
    "rows": [],
    "row_count": 0,
    "columns": [],
    "error": "SQL syntax error: ..."
}
```

**Non-SELECT query**:
```python
{
    "rows": [],
    "row_count": 0,
    "columns": [],
    "error": "Only SELECT queries are allowed"
}
```

### Delegates To
`nonagentic.tools.analytics.run_sql_query(sql, max_rows)`

---

## Tool 2: `generate_segment`

### Purpose
Generate customer segments using rules or ML algorithms (K-means clustering).

### Signature
```python
generate_segment(filters: dict | None = None, algorithm: str = "rules") -> dict
```

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `filters` | object | No | None | Filter criteria (e.g. `{"segment": "vip"}`) |
| `algorithm` | string | No | "rules" | Segmentation algorithm: `"rules"` or `"kmeans"` |

### Return Schema

```python
{
    "segments": list[dict],       # Segment definitions
    "segment_count": int,         # Number of segments
    "total_customers": int,       # Total customers in all segments
    "error": str | None           # Error message if segmentation failed
}
```

### Segment Object Schema

```python
{
    "label": str,                 # Segment name (e.g. "vip", "at_risk", "casual")
    "size": int,                  # Number of customers in segment
    "avg_risk_score": float,      # Average risk score (0.0-1.0)
    "avg_engagement": float       # Average engagement score (0.0-1.0)
}
```

### Example Usage

**Request (Rules-based)**:
```python
analytics_server.invoke_tool(
    "generate_segment",
    filters={"segment": "vip"},
    algorithm="rules"
)
```

**Response**:
```python
{
    "segments": [
        {
            "label": "vip",
            "size": 53,
            "avg_risk_score": 0.126,
            "avg_engagement": 0.739
        },
        {
            "label": "at_risk",
            "size": 39,
            "avg_risk_score": 0.246,
            "avg_engagement": 0.335
        },
        ...
    ],
    "segment_count": 5,
    "total_customers": 208,
    "error": None
}
```

### Algorithms

#### `"rules"` (Default)
- **Type**: Rule-based segmentation
- **Speed**: Fast (deterministic)
- **Clusters**: 5 fixed segments (casual, dormant_vip, at_risk, vip, new)
- **Logic**: Based on risk_score and engagement_score thresholds
- **Reproducibility**: Deterministic (same input → same output)

#### `"kmeans"`
- **Type**: K-means clustering (ML-based)
- **Speed**: Slower (iterative algorithm)
- **Clusters**: 4-5 clusters (configurable)
- **Logic**: Unsupervised learning on risk_score and engagement_score
- **Reproducibility**: May vary slightly due to random initialization

### Filters

Filters are applied before segmentation:

| Filter Key | Type | Example | Effect |
|------------|------|---------|--------|
| `segment` | string | `"vip"` | Include only customers in segment |
| `identity_status` | string | `"unverified"` | Include only customers with status |
| `risk_score_min` | float | `0.7` | Include only customers with risk >= value |
| `engagement_min` | float | `0.5` | Include only customers with engagement >= value |

### Error Handling

**Invalid algorithm**:
```python
{
    "segments": [],
    "segment_count": 0,
    "total_customers": 0,
    "error": "Unknown algorithm: 'invalid'. Use 'rules' or 'kmeans'"
}
```

**No customers match filters**:
```python
{
    "segments": [],
    "segment_count": 0,
    "total_customers": 0,
    "error": "No customers match the specified filters"
}
```

### Delegates To
`nonagentic.tools.analytics.generate_segment(filters, algorithm)`

---

## Tool Registration

Both tools are registered in `AnalyticsServer.initialize()`:

```python
class AnalyticsServer(MCPServer):
    def initialize(self) -> None:
        self.register_tool(
            MCPTool(
                name="run_sql_query",
                description="Execute SQL query on customer database",
                func=run_sql_query,
                schema={"sql": "string", "max_rows": "integer"}
            )
        )
        
        self.register_tool(
            MCPTool(
                name="generate_segment",
                description="Generate customer segments using rules or ML",
                func=generate_segment,
                schema={"filters": "object", "algorithm": "string"}
            )
        )
```

---

## Tool Invocation Pattern

All tools are invoked via the MCP protocol:

```python
# In analytics_agent.py
analytics_server = AnalyticsServer()

# Invoke tool
result = analytics_server.invoke_tool(
    tool_name="run_sql_query",
    sql="SELECT ...",
    max_rows=100
)

# Result is a dict with the schema defined above
```

---

## Performance Characteristics

| Tool | Typical Latency | Max Rows | Complexity |
|------|-----------------|----------|-----------|
| `run_sql_query` | 100-500ms | 100 | O(n) where n = row count |
| `generate_segment` (rules) | 50-200ms | N/A | O(n) where n = customer count |
| `generate_segment` (kmeans) | 500-2000ms | N/A | O(n*k*i) where k=clusters, i=iterations |

---

## Limitations

- **SQL**: Read-only, max 100 rows, no complex joins
- **Segmentation**: Rules-based is deterministic, K-means may vary
- **Memory**: Results not cached; each call executes fresh
- **Concurrency**: Single-threaded execution
