# UC1: User-Based Recommendations - Specification

## Overview

**Use Case**: Recommend items to a customer based on what customers in the same segment tend to buy.

**Business Value**: Leverage peer behavior within customer segments to provide relevant recommendations.

**Complexity**: Medium | **Agentic Features**: Planning, Tool Discovery, Memory

---

## Business Scenario

A casual customer (CUST-001) has limited interaction history. The system should recommend products that are popular among other casual customers, providing segment-aware recommendations.

**Input**: Customer ID (e.g., CUST-001)
**Output**: Ranked list of 10 recommended products with scores and explanations

---

## Deterministic Approach (Version A)

### Algorithm

1. **Retrieve Customer Profile**
   - Load customer segment (e.g., "casual")
   - Load engagement score
   - Load purchase categories

2. **Identify Segment Peers**
   - Query all customers with same segment
   - Count: N segment peers

3. **Aggregate Segment Behavior**
   - For each product:
     - Count purchases by segment peers
     - Normalize by segment size
     - Compute segment score = (peer_purchases / segment_size)

4. **Rank and Return**
   - Sort products by segment score (descending)
   - Return top-K products
   - Exclude already-purchased items

### Data Flow

```
Customer ID
    ↓
[Get Customer Profile] → Segment, Engagement
    ↓
[Find Segment Peers] → List of peer customer IDs
    ↓
[Aggregate Peer Behavior] → Product scores
    ↓
[Rank Products] → Top-K recommendations
    ↓
Output: Ranked list
```

### Key Formulas

```
segment_score(product) = count(peers who purchased product) / count(segment peers)
```

### Implementation Details

- **Tool**: `segment_recommendations(segment, top_k=10)`
- **Data Source**: Customer table, Interaction table, Product table
- **Complexity**: O(P × S) where P = products, S = segment size
- **Caching**: Segment scores can be pre-computed and cached

### Edge Cases

1. **Empty Segment**: If segment has < 2 members, fall back to global popularity
2. **No Peer Purchases**: If no peers purchased any products, return empty list
3. **All Products Purchased**: If customer purchased all segment-popular items, return next tier

---

## Dynamic Agentic Approach (Version B)

### Architecture

```
User Request
    ↓
[Orchestrator Agent]
    ↓
[Recommendation Strategy Agent]
    ├─ Analyze customer profile
    ├─ Check interaction history
    └─ Decide: segment-based vs collaborative vs behavior-based
    ↓
[Recommendation Agent]
    ├─ Plan: [get_customer_profile, segment_recommendations]
    ├─ Execute: Call MCP tools
    ├─ Memory: Store plan, tool usage, observation
    └─ Return: Recommendations with metadata
    ↓
[Evaluation Agent]
    ├─ Validate recommendations
    ├─ Check for quality issues
    └─ Approve or request replan
    ↓
Output: Recommendations + metadata
```

### Planning

The recommendation strategy agent generates a plan:

```json
{
  "goal": "Recommend products based on segment peer behaviour",
  "intent": "user_based_recommendations",
  "requires_sql": false,
  "subtasks": [
    {
      "id": 1,
      "name": "get_customer_profile",
      "agent": "recommendation_agent",
      "description": "Retrieve customer segment and attributes"
    },
    {
      "id": 2,
      "name": "segment_recommendations",
      "agent": "recommendation_agent",
      "description": "Find top products popular among segment peers"
    }
  ]
}
```

### Tool Discovery

The recommendation agent queries the tool registry:

```
Registry Query: "Find tools for segment-based recommendations"
Registry Response: [
  {
    "tool": "get_customer_profile",
    "mcp_server": "customer_data_server",
    "params": ["customer_id"],
    "returns": ["segment", "engagement_score", "purchase_categories"]
  },
  {
    "tool": "segment_recommendations",
    "mcp_server": "recommendation_server",
    "params": ["segment", "top_k"],
    "returns": ["product_id", "score", "explanation"]
  }
]
```

### Memory Integration

**Memory Updates**:
1. **Plan Memory**: Store generated plan
2. **Tool Usage Memory**: Log each tool call with parameters and results
3. **Observation Memory**: Store insights (e.g., "segment has 30 peers", "top product is PROD-052")

**Memory Retrieval**:
- Check if similar request was processed before
- Reuse cached segment scores if available
- Learn from previous recommendations

### Execution Flow

1. **Receive Request**: "Recommend products for CUST-001"
2. **Generate Plan**: Strategy agent creates plan
3. **Execute Plan**:
   - Call `get_customer_profile(CUST-001)` → Returns segment="casual"
   - Call `segment_recommendations("casual", top_k=10)` → Returns ranked products
4. **Update Memory**: Store plan, tool calls, results
5. **Evaluate**: Check recommendation quality
6. **Return**: Recommendations with agent path and memory updates

### Key Differences from Deterministic

| Aspect | Deterministic | Dynamic |
|--------|---|---|
| **Tool Selection** | Fixed | Registry-based discovery |
| **Planning** | Implicit | Explicit plan generation |
| **Memory** | None | Multi-layer memory |
| **Flexibility** | Low | High (can adapt strategy) |
| **Observability** | Low | High (plan, tools, memory visible) |

---

## Agentic Features Demonstrated

### 1. Planning
- Strategy agent generates structured execution plan
- Plan includes subtasks, agents, and descriptions
- Plan is stored in memory for audit trail

### 2. Dynamic Tool Discovery
- Tools discovered from registry, not hardcoded
- Tool parameters and returns are introspectable
- New tools can be added without code changes

### 3. Memory System
- **Plan Memory**: Stores generated plan
- **Tool Usage Memory**: Logs tool calls and results
- **Observation Memory**: Stores insights and learnings
- Memory enables learning and optimization

### 4. Agent Coordination
- Orchestrator agent routes to strategy agent
- Strategy agent routes to recommendation agent
- Evaluation agent validates results
- Agents communicate via shared memory

### 5. Explainability
- Agent path visible: orchestrator → strategy → recommendation → evaluation
- Tool selection visible: which tools were called
- Memory updates visible: what was learned
- Dominant signal visible: "Popular in 'casual' segment"

---

## Performance Characteristics

### Deterministic (A)
- **Latency**: ~50ms (direct tool call)
- **Memory**: Minimal (no memory overhead)
- **Throughput**: High (no planning overhead)
- **Scalability**: O(P × S) where P = products, S = segment size

### Dynamic (B)
- **Latency**: ~150-200ms (planning + execution + evaluation)
- **Memory**: ~1-2KB per request (plan, tool calls, observations)
- **Throughput**: Medium (planning overhead)
- **Scalability**: Same O(P × S) but with planning overhead

### Optimization Opportunities
1. **Caching**: Pre-compute segment scores
2. **Batching**: Process multiple customers in one batch
3. **Async Evaluation**: Run evaluation in background
4. **Memory Pruning**: Archive old memory entries

---

## Integration Points

### With Other UCs
- **UC2 (Collaborative Filtering)**: Can be used as fallback if segment is too small
- **UC4 (Hybrid)**: Segment score is one component of hybrid score
- **UC5 (Cold Start)**: Used for new customers with known segment
- **UC6 (Cross-Segment)**: Batch version of UC1

### With System Components
- **Agent Registry**: Discovers recommendation_agent
- **Tool Registry**: Discovers segment_recommendations tool
- **Memory Manager**: Stores and retrieves memory entries
- **MCP Servers**: Calls recommendation_server for segment scores

---

## Testing Strategy

### Unit Tests
- Test segment score calculation
- Test edge cases (empty segment, no purchases)
- Test ranking algorithm

### Integration Tests
- Test with real customer data
- Test memory updates
- Test agent coordination

### Performance Tests
- Measure latency for different segment sizes
- Measure memory usage
- Measure throughput

### Validation Tests
- Verify recommendations are relevant
- Verify no data leakage
- Verify explanations are accurate

---

## Error Handling

### Deterministic (A)
- **Segment Not Found**: Return empty list
- **No Peer Purchases**: Return empty list
- **Database Error**: Propagate error

### Dynamic (B)
- **Planning Failure**: Log error, fall back to deterministic
- **Tool Execution Failure**: Retry with exponential backoff
- **Evaluation Failure**: Log warning, return recommendations anyway
- **Memory Error**: Continue without memory

---

## Configuration

### Parameters
- `top_k`: Number of recommendations to return (default: 10)
- `min_segment_size`: Minimum segment size to use segment strategy (default: 2)
- `cache_ttl`: Cache time-to-live in seconds (default: 3600)

### Feature Flags
- `use_dynamic_planning`: Enable/disable dynamic planning (default: true)
- `use_memory`: Enable/disable memory system (default: true)
- `use_evaluation`: Enable/disable evaluation agent (default: true)

---

## References

- **Notebook**: `notebooks/agentic/05_level5_recommendation.ipynb` - UC1-A and UC1-B implementations
- **Code**: `agentic/recommendation_agent.py` - Recommendation agent implementation
- **Tools**: `mcp_servers/recommendation_server.py` - Segment recommendations tool
- **Memory**: `memory/memory_manager.py` - Memory system implementation

---

**Status**: Specification Complete
**Last Updated**: [Current timestamp]
**Version**: 1.0
