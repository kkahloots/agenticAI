# Analytics Agent — Use Cases & Examples

## Overview

This guide shows 5 real-world use cases for the Analytics Agent with practical examples and expected outputs.

---

## Use Case 1: Customer Segmentation

### Business Goal
Marketing team wants to identify distinct customer groups for targeted campaigns.

### How to Use

**Request**:
```
"Segment customers by risk and engagement scores"
```

**What the agent does**:
1. Detects "segment" keyword
2. Routes to `generate_segment` tool
3. Generates 5 customer segments
4. Returns segment sizes and metrics

### Expected Output

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

### Behind the Scenes

```
Agent Path: orchestrator → analytics_agent
MCP Server: analytics
MCP Tool: generate_segment
MCP Calls: 1

Memory Recorded:
  "Performed analysis: Largest segment: dormant_vip with 53 customers"
```

### Use This When
- You need to identify customer groups for marketing campaigns
- You want to understand customer distribution by risk/engagement
- You're planning segment-specific offers or messaging

---

## Use Case 2: Top Customers by Lifetime Value

### Business Goal
Account manager needs to identify high-value customers for VIP treatment.

### How to Use

**Request Option 1 (Provide SQL)**:
```
"Run this SQL query: SELECT customer_id, full_name, segment, lifetime_value FROM customers ORDER BY lifetime_value DESC LIMIT 10"
```

**Request Option 2 (Natural language)**:
```
"Show me top 10 customers by lifetime value"
```

**What the agent does**:
1. Detects SQL query (or generates one)
2. Routes to `run_sql_query` tool
3. Executes query against customer database
4. Returns 10 rows with customer data

### Expected Output

```
Query results (10 rows)

Insights:
  • Query returned 10 rows

Top 10 Customers:
  1. CUST-004 (Sharon Kennedy) - €89,205.38
  2. CUST-104 (الأستاذ ثروت خندف) - €88,661.71
  3. CUST-149 (Michelle Wallace) - €88,343.24
  ...
```

### Behind the Scenes

```
Agent Path: orchestrator → analytics_agent
MCP Server: analytics
MCP Tool: run_sql_query
MCP Calls: 1

SQL Executed:
  SELECT customer_id, full_name, segment, lifetime_value 
  FROM customers 
  ORDER BY lifetime_value DESC 
  LIMIT 10

Memory Recorded:
  "Performed analysis: Query returned 10 rows"
```

### Use This When
- You need to identify high-value customers
- You want to prioritize VIP treatment
- You're planning account management outreach

---

## Use Case 3: Fraud Risk Analysis

### Business Goal
Trust & Safety team needs to identify high-fraud-risk customers for enhanced verification.

### How to Use

**Request**:
```
"Find customers with fraud score > 0.7"
```

**What the agent does**:
1. Detects analytics intent
2. Generates SQL query with fraud filter
3. Routes to `run_sql_query` tool
4. Returns customers grouped by segment with fraud metrics

### Expected Output

```
Query results (5 rows)

Insights:
  • Query returned 5 rows

High-Fraud-Risk Customers by Segment:
  - at_risk: 17 customers (avg fraud: 0.838)
  - dormant_vip: 16 customers (avg fraud: 0.814)
  - casual: 11 customers (avg fraud: 0.822)
  - new: 10 customers (avg fraud: 0.797)
  - vip: 9 customers (avg fraud: 0.890)

Total: 63 high-fraud-risk customers
```

### Behind the Scenes

```
Agent Path: orchestrator → analytics_agent
MCP Server: analytics
MCP Tool: run_sql_query
MCP Calls: 1

SQL Generated:
  SELECT segment, COUNT(*) as count, AVG(fraud_score) as avg_risk
  FROM customers
  WHERE fraud_score > 0.7
  GROUP BY segment
  ORDER BY count DESC

Memory Recorded:
  "Performed analysis: Query returned 5 rows"
```

### Use This When
- You need to identify fraud risks
- You're implementing enhanced verification
- You want to monitor fraud trends by segment

---

## Use Case 4: Sales Analytics

### Business Goal
Sales team wants to understand revenue distribution by product category.

### How to Use

**Request**:
```
"Analyze sales by product category"
```

**What the agent does**:
1. Detects analytics intent
2. Uses default segment query (no SQL provided, no segmentation keywords)
3. Routes to `run_sql_query` tool
4. Returns segment breakdown

### Expected Output

```
Query results (5 rows)

Insights:
  • Query returned 5 rows

Revenue by Category:
  - electronics: €208,955.81 (65.3%)
  - sports_outdoors: €42,016.45 (13.1%)
  - home_garden: €29,771.51 (9.3%)
  - clothing: €19,861.79 (6.2%)
  - beauty_health: €7,033.41 (2.2%)

Total Revenue: €320,213.26
```

### Behind the Scenes

```
Agent Path: orchestrator → analytics_agent
MCP Server: analytics
MCP Tool: run_sql_query
MCP Calls: 1

SQL Generated (default):
  SELECT segment, COUNT(*) as count FROM customers GROUP BY segment

Memory Recorded:
  "Performed analysis: Query returned 5 rows"
```

### Use This When
- You need to understand revenue distribution
- You're analyzing product performance
- You want to identify top-performing categories

---

## Use Case 5: Support Analytics

### Business Goal
Support manager needs to understand ticket volume and types.

### How to Use

**Request**:
```
"Show ticket volume by type"
```

**What the agent does**:
1. Detects analytics intent
2. Generates SQL query for ticket analysis
3. Routes to `run_sql_query` tool
4. Returns ticket metrics grouped by type

### Expected Output

```
Query results (8 rows)

Insights:
  • Query returned 8 rows

Tickets by Type:
  - payment_billing: 29 tickets (14.5%)
  - account_access: 27 tickets (13.5%)
  - returns_exchanges: 27 tickets (13.5%)
  - product_inquiry: 26 tickets (13.0%)
  - shipping_delivery: 26 tickets (13.0%)
  - complaint: 25 tickets (12.5%)
  - order_issue: 22 tickets (11.0%)
  - technical_support: 18 tickets (9.0%)

Total: 200 tickets
Open: 84 tickets
High Priority: 41 tickets
```

### Behind the Scenes

```
Agent Path: orchestrator → analytics_agent
MCP Server: analytics
MCP Tool: run_sql_query
MCP Calls: 1

SQL Generated:
  SELECT type, COUNT(*) as count FROM support_tickets GROUP BY type ORDER BY count DESC

Memory Recorded:
  "Performed analysis: Query returned 8 rows"
```

### Use This When
- You need to understand support ticket distribution
- You're analyzing support team workload
- You want to identify common issue types

---

## Routing Decision Tree

```
Your Request
    │
    ├─ Contains SQL query?
    │  ├─ YES → Execute SQL directly
    │  │        (UC2, UC3, UC4, UC5)
    │  │
    │  └─ NO → Check for keywords
    │     │
    │     ├─ "segment" | "cluster" | "group"?
    │     │  ├─ YES → Generate segments
    │     │  │        (UC1)
    │     │  │
    │     │  └─ NO → Use default query
    │     │           (UC4, UC5)
    │
    └─ Record observation to memory
```

---

## Common Patterns

### Pattern 1: Provide Your Own SQL

```
"Run this SQL query: SELECT ... FROM customers WHERE ..."
```

**Agent behavior**:
- Extracts SQL from request
- Validates it's a SELECT query
- Executes it
- Returns results

### Pattern 2: Use Keywords

```
"Segment customers by ..."
"Cluster customers into ..."
"Group customers by ..."
```

**Agent behavior**:
- Detects segmentation keyword
- Routes to `generate_segment`
- Returns 5 segments with metrics

### Pattern 3: Natural Language

```
"Show me top customers by ..."
"Analyze ... by ..."
"Find customers with ..."
```

**Agent behavior**:
- Generates SQL query
- Executes it
- Returns results

---

## Tips & Tricks

### Tip 1: Be Specific with SQL

Instead of:
```
"Show me customers"
```

Use:
```
"Show me top 10 customers by lifetime value"
```

Or provide SQL:
```
"Run this SQL query: SELECT customer_id, lifetime_value FROM customers ORDER BY lifetime_value DESC LIMIT 10"
```

### Tip 2: Use Segmentation for Quick Insights

Instead of writing complex SQL:
```
"Segment customers by risk and engagement"
```

This gives you 5 segments with metrics instantly.

### Tip 3: Check the Audit Trail

Every response includes:
- **Agent Path**: Which agents ran
- **MCP Calls**: Which tools were invoked
- **Memory**: What was recorded

Use this to understand how the agent processed your request.

### Tip 4: Combine with Other Agents

Analytics results can feed into other agents:
- **Recommendation Agent**: Use segments to recommend products
- **Action Agent**: Use segments to send targeted campaigns
- **Workflow Agent**: Use analytics to decompose complex goals

---

## Next Steps

- **Best practices**: See `best_practices.md` for when to use analytics
- **Technical details**: See `specs/agentic/analytics/` for implementation
- **Developer guide**: See `docs/agentic/developer/` for extending the agent
