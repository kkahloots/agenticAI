# Analytics Agent — Overview

## What is the Analytics Agent?

The **Analytics Agent** is a specialized agent that performs data analysis, customer segmentation, and SQL queries. It is automatically invoked when the Orchestrator detects an analytics intent in your request.

Unlike the nonagent Level-2 Analytics, the agentic analytics agent:
- **Routes dynamically** based on request content (SQL vs segmentation vs default)
- **Records observations** to memory for learning
- **Provides full audit trail** of all MCP tool calls
- **Integrates with memory layer** to track analysis patterns

---

## When to Use the Analytics Agent

Use the analytics agent when you need to:

| Goal | Example Request |
|------|-----------------|
| **Segment customers** | "Segment customers by risk and engagement" |
| **Query customer data** | "Show me top 10 customers by lifetime value" |
| **Analyze fraud risk** | "Find high-fraud-risk customers" |
| **Revenue analysis** | "Analyze sales by product category" |
| **Support metrics** | "Show ticket volume by type" |

---

## How It Works

```
Your Request
    ↓
Orchestrator (classifies intent as "analytics")
    ↓
Analytics Agent (determines which tool to use)
    ├─ SQL query detected? → run_sql_query
    ├─ Segmentation keywords? → generate_segment
    └─ Neither? → Default segment query
    ↓
MCP Analytics Server (executes tool)
    ↓
Memory Layer (records observation)
    ↓
Response + Agent Path + MCP Calls + Audit Trail
```

---

## Key Features

### 1. Intelligent Routing

The agent automatically detects what you're asking for:

- **SQL Queries**: If you provide a SQL query, it executes it directly
- **Segmentation**: If you mention "segment", "cluster", or "group", it generates segments
- **Default**: If neither, it runs a default segment query

### 2. Two Segmentation Algorithms

- **Rules-based** (default): Fast, deterministic, 5 fixed segments
- **K-means**: ML-based clustering, 4-5 dynamic clusters

### 3. Memory Integration

Every analysis is recorded to memory:
- Observations are stored for future reference
- System learns from past analyses
- Enables pattern recognition over time

### 4. Full Audit Trail

Every request produces:
- Agent path (which agents ran)
- MCP calls (which tools were invoked)
- Audit log (what happened)
- Intermediate results (step-by-step output)

---

## Use Cases

### Use Case 1: Customer Segmentation

**Goal**: Identify distinct customer groups for targeted marketing

**Request**:
```
"Segment customers by risk and engagement scores"
```

**What Happens**:
1. Orchestrator detects "segment" keyword
2. Analytics agent routes to `generate_segment`
3. Agent generates 5 segments (casual, dormant_vip, at_risk, vip, new)
4. Results include segment size and average metrics
5. Observation recorded: "Largest segment: dormant_vip with 53 customers"

**Output**:
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

### Use Case 2: Top Customers by Lifetime Value

**Goal**: Identify high-value customers for VIP treatment

**Request**:
```
"Show me top 10 customers by lifetime value"
```

**What Happens**:
1. Orchestrator detects analytics intent
2. Analytics agent extracts SQL query (or generates one)
3. Agent executes `run_sql_query`
4. Returns 10 rows with customer data
5. Observation recorded: "Query returned 10 rows"

**Output**:
```
Query results (10 rows)

Insights:
  • Query returned 10 rows
```

---

### Use Case 3: Fraud Risk Analysis

**Goal**: Identify high-fraud-risk customers for enhanced verification

**Request**:
```
"Find customers with fraud score > 0.7"
```

**What Happens**:
1. Orchestrator detects analytics intent
2. Analytics agent generates SQL query with fraud filter
3. Agent executes `run_sql_query`
4. Returns customers grouped by segment with fraud metrics
5. Observation recorded: "Query returned 5 rows"

---

### Use Case 4: Sales Analytics

**Goal**: Understand revenue distribution by product category

**Request**:
```
"Analyze sales by product category"
```

**What Happens**:
1. Orchestrator detects analytics intent
2. Analytics agent uses default segment query
3. Agent executes `run_sql_query`
4. Returns segment breakdown
5. Observation recorded

---

### Use Case 5: Support Analytics

**Goal**: Understand support ticket volume and types

**Request**:
```
"Show ticket volume by type"
```

**What Happens**:
1. Orchestrator detects analytics intent
2. Analytics agent generates SQL query
3. Agent executes `run_sql_query`
4. Returns ticket metrics grouped by type
5. Observation recorded

---

## Comparison: Analytics Agent vs Level-2 Analytics

| Feature | Level-2 Analytics | Analytics Agent |
|---------|------------------|-----------------|
| **Routing** | Fixed: always calls tool directly | Dynamic: routes based on request |
| **Tool Access** | Direct function import | MCP protocol (abstracted) |
| **Memory** | None | Agent observations recorded |
| **Audit Trail** | Basic log | Full agent path + MCP calls |
| **Autonomy** | Low | Medium |
| **Replanning** | None | N/A (analytics doesn't trigger evaluation) |

---

## Important Limitations

- **Read-only**: Only SELECT queries allowed (no INSERT, UPDATE, DELETE)
- **Max rows**: Limited to 100 rows by default
- **In-process memory**: Observations not persisted to external storage
- **No evaluation**: Analytics results are final; no automatic replanning
- **No approval gates**: Analytics queries execute immediately

---

## Next Steps

- **See examples**: Check `examples.md` for code samples
- **Best practices**: Read `best_practices.md` for when to use analytics
- **Technical details**: See `specs/agentic/analytics/` for implementation details
