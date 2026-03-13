# UC5: Cold Start Handling - Specification

## Overview

**Use Case**: A brand-new customer has no purchase history. The system must still return useful recommendations.

**Business Value**: Enable recommendations for new customers, improving onboarding experience.

**Complexity**: Medium | **Agentic Features**: Cold Start Detection, Dynamic Strategy Selection, Fallback Strategy

---

## Business Scenario

A new customer (CUST-NEW) has just signed up with segment "dormant_vip" but no interactions. The system detects cold start and returns recommendations based on segment popularity.

**Input**: Customer ID (e.g., CUST-NEW), segment (e.g., "dormant_vip")
**Output**: Ranked list of 10 recommended products (segment-popular items)

---

## Deterministic Approach (Version A)

### Algorithm

1. **Detect Cold Start**
   - Count customer interactions
   - If interactions < 3: cold start = true

2. **Choose Fallback Strategy**
   - If segment known: use segment popularity
   - Else: use global popularity

3. **Compute Fallback Scores**
   - For segment fallback:
     - `fallback_score(product) = count(segment peers who purchased) / count(segment peers)`
   - For global fallback:
     - `fallback_score(product) = count(all customers who purchased) / count(all customers)`

4. **Rank and Return**
   - Sort products by fallback score (descending)
   - Return top-K products

### Data Flow

```
Customer ID
    ↓
[Detect Cold Start] → Check interaction count
    ↓
[Choose Fallback] → Segment or global?
    ↓
[Compute Scores] → Segment or global popularity
    ↓
[Rank Products] → Top-K recommendations
    ↓
Output: Ranked list with fallback source
```

### Key Formulas

```
cold_start = interactions < 3

fallback_score_segment(product) = count(segment peers who purchased) / count(segment peers)

fallback_score_global(product) = count(all customers who purchased) / count(all customers)
```

### Implementation Details

- **Tool**: `get_cold_start_recommendations(customer, top_k=10)`
- **Data Source**: Customer table, Interaction table, Product table
- **Complexity**: O(S × P) for segment fallback, O(P) for global fallback
- **Optimization**: Pre-compute segment and global popularity scores

### Edge Cases

1. **Unknown Segment**: Fall back to global popularity
2. **Segment Too Small**: Fall back to global popularity
3. **No Popular Products**: Return random products

---

## Dynamic Agentic Approach (Version B)

### Architecture

```
User Request
    ↓
[Orchestrator Agent]
    ↓
[Recommendation Agent]
    ├─ Plan: [detect_cold_start, cold_start_recommend]
    ├─ Execute: Call MCP tools
    ├─ Detect: Cold start = true
    ├─ Choose: Segment fallback (segment known)
    ├─ Memory: Store plan, detection, strategy
    └─ Return: Recommendations with fallback source
    ↓
[LLM Reasoning Server] (optional)
    ├─ Suggest alternative strategies
    ├─ Propose personalization hints
    └─ Return: Suggestions
    ↓
[Evaluation Agent]
    ├─ Validate recommendations
    ├─ Check for quality issues
    └─ Approve or request replan
    ↓
Output: Recommendations + metadata
```

### Planning

```json
{
  "goal": "Handle cold start with fallback recommendations",
  "intent": "cold_start_handling",
  "requires_sql": false,
  "subtasks": [
    {
      "id": 1,
      "name": "detect_cold_start",
      "agent": "recommendation_agent",
      "description": "Check interaction history to confirm cold start"
    },
    {
      "id": 2,
      "name": "cold_start_recommend",
      "agent": "recommendation_agent",
      "description": "Apply segment fallback or popularity fallback"
    }
  ]
}
```

### Tool Discovery

```
Registry Query: "Find tools for cold start handling"
Registry Response: [
  {
    "tool": "get_customer_history",
    "mcp_server": "customer_data_server",
    "params": ["customer_id"],
    "returns": ["interaction_count", "segment", "purchase_categories"]
  },
  {
    "tool": "cold_start_recommend",
    "mcp_server": "recommendation_server",
    "params": ["customer_id", "segment", "top_k"],
    "returns": ["product_id", "score", "fallback_source"]
  },
  {
    "tool": "popularity_scores",
    "mcp_server": "recommendation_server",
    "params": ["top_k"],
    "returns": ["product_id", "score"]
  },
  {
    "tool": "segment_recommendations",
    "mcp_server": "recommendation_server",
    "params": ["segment", "top_k"],
    "returns": ["product_id", "score"]
  }
]
```

### Cold Start Detection

The agent detects cold start:

```
Input: customer_id = "CUST-NEW"

Step 1: get_customer_history("CUST-NEW")
Output: {
  "interaction_count": 0,
  "segment": "dormant_vip",
  "purchase_categories": []
}

Step 2: Detect cold start
cold_start = (interaction_count < 3) = true

Step 3: Choose strategy
if segment known:
  strategy = "segment_fallback"
else:
  strategy = "global_fallback"
```

### Strategy Selection

The agent chooses fallback strategy:

```
If segment known and segment_size >= 2:
  Use segment_recommendations(segment, top_k)
Else if segment known but segment_size < 2:
  Use popularity_scores(top_k)
Else:
  Use popularity_scores(top_k)
```

### Memory Integration

**Memory Updates**:
1. **Plan Memory**: Store generated plan
2. **Detection Memory**: Store cold start detection result
3. **Strategy Memory**: Store chosen fallback strategy
4. **Observation Memory**: Store fallback source and reasoning

**Memory Retrieval**:
- Check if similar new customer was processed before
- Reuse strategy if applicable
- Learn from previous cold start recommendations

### LLM Fallback Decision (Optional)

The LLM reasoning server can suggest alternative strategies:

```
Input: {
  "interaction_count": 0,
  "segment": "dormant_vip",
  "segment_size": 53,
  "available_strategies": ["segment_fallback", "global_fallback", "content_only"]
}

LLM Analysis:
- No interactions → cold start confirmed
- Segment known and large → segment fallback is reliable
- Could also use content-only if customer provides preferences

Output: {
  "strategy": "cold_start",
  "reason": "Insufficient interaction history",
  "method": "rule_based",
  "recommended_strategy": "segment_fallback",
  "alternative_strategies": ["global_fallback", "content_only"]
}
```

### Key Differences from Deterministic

| Aspect | Deterministic | Dynamic |
|--------|---|---|
| **Detection** | Implicit | Explicit (stored in memory) |
| **Strategy** | Fixed | Dynamic (can choose alternative) |
| **Fallback** | Single level | Multi-level (segment → global) |
| **LLM Reasoning** | None | Optional (suggest alternatives) |
| **Observability** | Low | High (detection, strategy visible) |

---

## Agentic Features Demonstrated

### 1. Cold Start Detection
- Agent explicitly detects cold start
- Detection stored in memory
- Detection can be used by other agents

### 2. Dynamic Strategy Selection
- Agent chooses between segment and global fallback
- Strategy based on customer profile
- Strategy can be changed without code changes

### 3. Multi-Level Fallback
- Primary: Segment fallback
- Secondary: Global fallback
- Tertiary: Random products

### 4. Memory Integration
- Detection stored for audit trail
- Strategy stored for learning
- Observations stored for future reference

### 5. Explainability
- Fallback source visible
- Strategy visible
- Detection result visible
- Agent path visible

---

## Performance Characteristics

### Deterministic (A)
- **Latency**: ~30-50ms (detection + fallback scoring)
- **Memory**: Minimal (no memory overhead)
- **Throughput**: High (simple operations)
- **Scalability**: O(S × P) for segment, O(P) for global

### Dynamic (B)
- **Latency**: ~100-150ms (detection + strategy selection + evaluation)
- **Memory**: ~1-2KB for detection and strategy
- **Throughput**: High (no LLM overhead unless optional)
- **Scalability**: Same O(S × P) or O(P)

### Optimization Opportunities
1. **Pre-compute Popularity**: Cache segment and global popularity scores
2. **Batch Detection**: Detect cold start for multiple customers at once
3. **Async Evaluation**: Run evaluation in background
4. **Memory Pruning**: Archive old detection records

---

## Integration Points

### With Other UCs
- **UC1 (User-Based)**: Used as fallback if segment is known
- **UC2 (Collaborative)**: Not applicable (requires interaction history)
- **UC3 (Behaviour)**: Not applicable (requires interaction history)
- **UC4 (Hybrid)**: Used for new customers with known segment
- **UC6 (Cross-Segment)**: Can identify cold start customers in segment
- **UC7 (Evaluation)**: Evaluated separately (different metrics)
- **UC9 (Orchestrator)**: Used for new customers

### With System Components
- **Agent Registry**: Discovers recommendation_agent
- **Tool Registry**: Discovers cold_start_recommend tool
- **Memory Manager**: Stores detection and strategy
- **MCP Servers**: Calls recommendation_server for fallback scores

---

## Testing Strategy

### Unit Tests
- Test cold start detection
- Test fallback score computation
- Test strategy selection

### Integration Tests
- Test with real new customer data
- Test memory updates
- Test fallback to global popularity

### Performance Tests
- Measure latency for detection
- Measure memory usage
- Measure throughput

### Validation Tests
- Verify cold start detection is accurate
- Verify fallback recommendations are relevant
- Verify no data leakage

---

## Error Handling

### Deterministic (A)
- **Detection Failure**: Assume not cold start
- **Fallback Score Failure**: Return empty list
- **Invalid Product**: Skip product

### Dynamic (B)
- **Detection Failure**: Log error, assume not cold start
- **Strategy Selection Failure**: Use default (segment fallback)
- **Fallback Score Failure**: Retry with exponential backoff
- **Evaluation Failure**: Log warning, return recommendations anyway

---

## Configuration

### Parameters
- `top_k`: Number of recommendations to return (default: 10)
- `cold_start_threshold`: Interaction count threshold (default: 3)
- `min_segment_size`: Minimum segment size for segment fallback (default: 2)

### Feature Flags
- `use_dynamic_planning`: Enable/disable dynamic planning (default: true)
- `use_llm_fallback_decision`: Enable/disable LLM fallback suggestions (default: false)
- `use_memory`: Enable/disable memory system (default: true)

---

## References

- **Notebook**: `notebooks/agentic/05_level5_recommendation.ipynb` - UC5-A and UC5-B implementations
- **Code**: `agentic/recommendation_agent.py` - Recommendation agent implementation
- **Tools**: `mcp_servers/recommendation_server.py` - Cold start recommendation tools
- **Memory**: `memory/memory_manager.py` - Memory system implementation

---

**Status**: Specification Complete
**Last Updated**: [Current timestamp]
**Version**: 1.0
