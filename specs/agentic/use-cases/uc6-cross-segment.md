# UC6: Cross-User Segment Recommendations - Specification

## Overview

**Use Case**: Generate recommendations for an entire customer segment at once — e.g. all `dormant_vip` customers — to plan a re-engagement campaign.

**Business Value**: Enable batch recommendations for campaign planning and segment-level insights.

**Complexity**: High | **Agentic Features**: SQL Generation, Batch Processing, Analytics Coordination, Memory

---

## Business Scenario

Marketing team wants to re-engage dormant VIP customers. The system generates recommendations for all 53 dormant_vip customers, identifies top products for the segment, and provides insights for campaign planning.

**Input**: Segment name (e.g., "dormant_vip"), sample_size (e.g., 15), top_k (e.g., 10)
**Output**: Top 10 products for segment with average scores and category distribution

---

## Deterministic Approach (Version A)

### Algorithm

1. **Identify Segment Members**
   - Query all customers with target segment
   - Sample N customers (for performance)

2. **Generate Recommendations**
   - For each sampled customer:
     - Call UC1 (segment-based) or UC4 (hybrid)
     - Get top-K recommendations

3. **Aggregate Results**
   - For each product:
     - Compute average score across all customers
     - Count how many customers recommended it
   - Sort by average score (descending)

4. **Return Top Products**
   - Return top-K products with aggregated scores
   - Include category distribution

### Data Flow

```
Segment Name
    ↓
[Identify Segment Members] → List of customer IDs
    ↓
[Sample Customers] → N sampled customers
    ↓
[Generate Recommendations] → For each customer, get top-K
    ↓
[Aggregate Results] → Average scores, counts
    ↓
[Rank Products] → Top-K for segment
    ↓
Output: Segment-level recommendations
```

### Key Formulas

```
segment_avg_score(product) = sum(score(product, customer) for customer in segment) / count(segment)

segment_coverage(product) = count(customers who recommended product) / count(segment)
```

### Implementation Details

- **Tool**: `get_segment_recommendations_batch(segment, top_k=10, sample_size=15)`
- **Data Source**: Customer table, Interaction table, Product table
- **Complexity**: O(S × K × P) where S = sample size, K = top-K, P = products
- **Optimization**: Parallelize customer recommendations, cache segment scores

### Edge Cases

1. **Segment Too Small**: Use all customers
2. **No Recommendations**: Return empty list
3. **All Products Scored Zero**: Return products with highest popularity

---

## Dynamic Agentic Approach (Version B)

### Architecture

```
User Request
    ↓
[Orchestrator Agent]
    ↓
[Analytics Agent]
    ├─ Plan: [identify_segment_members, segment_batch_recommend, aggregate_results]
    ├─ Generate SQL: "SELECT * FROM customers WHERE segment = ?"
    ├─ Execute SQL: Get segment members
    ├─ Memory: Store SQL, results
    └─ Return: Segment members
    ↓
[Recommendation Agent]
    ├─ Batch Process: Generate recommendations for sampled customers
    ├─ Memory: Store recommendations
    └─ Return: Per-customer recommendations
    ↓
[Analytics Agent]
    ├─ Aggregate: Compute average scores, counts
    ├─ Memory: Store aggregation results
    └─ Return: Segment-level recommendations
    ↓
[Evaluation Agent]
    ├─ Validate recommendations
    ├─ Check for quality issues
    └─ Approve or request replan
    ↓
Output: Segment recommendations + metadata
```

### Planning

```json
{
  "goal": "Generate recommendations for all customers in a segment",
  "intent": "cross_user_segment_recommendations",
  "requires_sql": true,
  "subtasks": [
    {
      "id": 1,
      "name": "identify_segment_members",
      "agent": "analytics_agent",
      "description": "Find all customers in target segment"
    },
    {
      "id": 2,
      "name": "segment_batch_recommend",
      "agent": "recommendation_agent",
      "description": "Run recommendations for sampled segment members"
    },
    {
      "id": 3,
      "name": "aggregate_results",
      "agent": "analytics_agent",
      "description": "Aggregate top products across segment"
    }
  ]
}
```

### SQL Generation

The analytics agent generates SQL to identify segment members:

```sql
-- Generated SQL
SELECT customer_id, segment, engagement_score, purchase_categories
FROM customers
WHERE segment = 'dormant_vip'
ORDER BY engagement_score DESC
LIMIT 15;
```

### Tool Discovery

```
Registry Query: "Find tools for cross-segment recommendations"
Registry Response: [
  {
    "tool": "run_sql_query",
    "mcp_server": "analytics_server",
    "params": ["sql_query"],
    "returns": ["results"]
  },
  {
    "tool": "get_customer_segment",
    "mcp_server": "customer_data_server",
    "params": ["segment"],
    "returns": ["customer_ids"]
  },
  {
    "tool": "segment_batch_recommend",
    "mcp_server": "recommendation_server",
    "params": ["customer_ids", "top_k"],
    "returns": ["recommendations_per_customer"]
  },
  {
    "tool": "build_segment_recommendation_stats",
    "mcp_server": "analytics_server",
    "params": ["recommendations_per_customer"],
    "returns": ["product_id", "avg_score", "coverage", "category"]
  }
]
```

### Agent Coordination

1. **Analytics Agent**:
   - Generates SQL to identify segment members
   - Executes SQL
   - Stores results in memory

2. **Recommendation Agent**:
   - Receives segment members from analytics agent
   - Generates recommendations for each customer
   - Stores recommendations in memory

3. **Analytics Agent** (again):
   - Receives recommendations from recommendation agent
   - Aggregates results
   - Computes statistics
   - Stores aggregation in memory

### Memory Integration

**Memory Updates**:
1. **Plan Memory**: Store generated plan
2. **SQL Memory**: Store generated SQL and results
3. **Recommendation Memory**: Store per-customer recommendations
4. **Aggregation Memory**: Store aggregated results and statistics

**Memory Retrieval**:
- Check if segment was recently processed
- Reuse cached segment members if available
- Reuse cached recommendations if available

### Key Differences from Deterministic

| Aspect | Deterministic | Dynamic |
|--------|---|---|
| **SQL Generation** | None (hardcoded query) | Dynamic SQL generation |
| **Agent Coordination** | Implicit | Explicit (analytics → recommendation → analytics) |
| **Memory** | None | Multi-layer memory |
| **Flexibility** | Low | High (can adapt query) |
| **Observability** | Low | High (SQL, coordination visible) |

---

## Agentic Features Demonstrated

### 1. SQL Generation
- Analytics agent generates SQL dynamically
- SQL is safe (read-only, parameterized)
- SQL can be audited and logged

### 2. Batch Processing
- Recommendation agent processes multiple customers
- Batch processing can be parallelized
- Results aggregated by analytics agent

### 3. Agent Coordination
- Analytics agent coordinates with recommendation agent
- Agents communicate via memory
- Agents can run in sequence or parallel

### 4. Memory System
- SQL stored for audit trail
- Recommendations stored for analysis
- Aggregation results stored for reporting

### 5. Explainability
- SQL visible for audit
- Agent coordination visible
- Aggregation logic visible
- Agent path visible

---

## Performance Characteristics

### Deterministic (A)
- **Latency**: ~500-1000ms (depends on sample size)
- **Memory**: O(S × K) for recommendations
- **Throughput**: Low (batch processing)
- **Scalability**: O(S × K × P) where S = sample size

### Dynamic (B)
- **Latency**: ~1000-2000ms (SQL generation + execution + batch processing + aggregation)
- **Memory**: O(S × K) + ~5-10KB for metadata
- **Throughput**: Lower (SQL generation overhead)
- **Scalability**: Same O(S × K × P)

### Optimization Opportunities
1. **Parallel Processing**: Process customers in parallel
2. **Caching**: Cache segment members and recommendations
3. **Incremental Aggregation**: Aggregate as recommendations arrive
4. **Approximate Aggregation**: Use sampling for large segments

---

## Integration Points

### With Other UCs
- **UC1 (User-Based)**: Used for per-customer recommendations
- **UC4 (Hybrid)**: Alternative for per-customer recommendations
- **UC7 (Evaluation)**: Evaluated separately (segment-level metrics)
- **UC8 (Visualisation)**: Results visualized for campaign planning
- **UC9 (Orchestrator)**: Used for campaign planning

### With System Components
- **Agent Registry**: Discovers analytics_agent, recommendation_agent
- **Tool Registry**: Discovers SQL generation and batch recommendation tools
- **Memory Manager**: Stores SQL, recommendations, aggregation results
- **MCP Servers**: Calls analytics_server and recommendation_server

---

## Testing Strategy

### Unit Tests
- Test SQL generation
- Test aggregation logic
- Test edge cases

### Integration Tests
- Test with real segment data
- Test agent coordination
- Test memory updates
- Test SQL execution

### Performance Tests
- Measure latency for different sample sizes
- Measure memory usage
- Measure throughput
- Measure parallelization speedup

### Validation Tests
- Verify SQL is correct and safe
- Verify aggregation is accurate
- Verify recommendations are relevant
- Verify no data leakage

---

## Error Handling

### Deterministic (A)
- **Segment Not Found**: Return empty list
- **SQL Error**: Propagate error
- **Aggregation Error**: Return partial results

### Dynamic (B)
- **SQL Generation Failure**: Use default query
- **SQL Execution Failure**: Retry with exponential backoff
- **Batch Processing Failure**: Process remaining customers
- **Aggregation Failure**: Return partial results
- **Evaluation Failure**: Log warning, return results anyway

---

## Configuration

### Parameters
- `top_k`: Number of recommendations per customer (default: 10)
- `sample_size`: Number of customers to sample (default: 15)
- `batch_size`: Number of customers to process in parallel (default: 5)
- `sql_timeout`: SQL execution timeout in seconds (default: 30)

### Feature Flags
- `use_dynamic_planning`: Enable/disable dynamic planning (default: true)
- `use_sql_generation`: Enable/disable SQL generation (default: true)
- `use_parallel_processing`: Enable/disable parallel processing (default: true)
- `use_memory`: Enable/disable memory system (default: true)

---

## SQL Safety

### Read-Only Queries
- Only SELECT statements allowed
- No INSERT, UPDATE, DELETE
- No DDL statements

### Parameterized Queries
- All parameters are parameterized
- No string concatenation
- Protection against SQL injection

### Query Validation
- Queries validated before execution
- Queries logged for audit trail
- Queries can be reviewed by humans

---

## References

- **Notebook**: `notebooks/agentic/05_level5_recommendation.ipynb` - UC6-A and UC6-B implementations
- **Code**: `agentic/analytics_agent.py` - Analytics agent implementation
- **Tools**: `mcp_servers/analytics_server.py` - SQL generation and execution tools
- **Tools**: `mcp_servers/recommendation_server.py` - Batch recommendation tools
- **Memory**: `memory/memory_manager.py` - Memory system implementation

---

**Status**: Specification Complete
**Last Updated**: [Current timestamp]
**Version**: 1.0
