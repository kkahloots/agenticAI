# UC4: Hybrid Recommender - Specification

## Overview

**Use Case**: Combine collaborative filtering, behaviour signals, content similarity, and popularity into one ranked list.

**Business Value**: Leverage multiple signals for robust, high-quality recommendations.

**Complexity**: High | **Agentic Features**: Strategy Selection, LLM Explanation, Model Combination, Memory

---

## Business Scenario

A customer (CUST-001) has rich interaction history. The system combines:
- Collaborative filtering (0.4): Similar users' preferences
- Behaviour signals (0.3): Customer's own behavior
- Content similarity (0.2): Product category affinity
- Popularity (0.1): Global popularity

**Input**: Customer ID (e.g., CUST-001), top_k (e.g., 10)
**Output**: Ranked list of 10 products with combined scores and explanations

---

## Deterministic Approach (Version A)

### Algorithm

1. **Compute Collaborative Score**
   - Use UC2 algorithm: cosine similarity + weighted aggregation
   - Result: `cf_score(product)` ∈ [0, 1]

2. **Compute Behaviour Score**
   - Use UC3 algorithm: behavior + content combination
   - Result: `behaviour_score(product)` ∈ [0, 1]

3. **Compute Content Score**
   - Category affinity from customer's purchase history
   - Result: `content_score(product)` ∈ [0, 1]

4. **Compute Popularity Score**
   - Global purchase count normalized
   - Result: `popularity_score(product)` ∈ [0, 1]

5. **Combine Scores**
   - `hybrid_score = 0.4 × cf_score + 0.3 × behaviour_score + 0.2 × content_score + 0.1 × popularity_score`

6. **Rank and Return**
   - Sort products by hybrid score (descending)
   - Return top-K products
   - Compute confidence = max(cf_score, behaviour_score, content_score)

### Data Flow

```
Customer ID
    ↓
[Compute CF Score] → Collaborative filtering score
    ↓
[Compute Behaviour Score] → Behavior + content score
    ↓
[Compute Content Score] → Category affinity
    ↓
[Compute Popularity Score] → Global popularity
    ↓
[Combine Scores] → Weighted combination
    ↓
[Rank Products] → Top-K recommendations
    ↓
Output: Ranked list with component scores
```

### Key Formulas

```
hybrid_score(product) = 0.4 × cf_score + 0.3 × behaviour_score + 0.2 × content_score + 0.1 × popularity_score

confidence(product) = max(cf_score, behaviour_score, content_score)

dominant_signal(product) = argmax(cf_score, behaviour_score, content_score)
```

### Implementation Details

- **Tool**: `recommend(customer_id, top_k=10)`
- **Data Source**: Interactions, Products, Customers
- **Complexity**: O(U × P + I × P) where U = users, I = interactions, P = products
- **Optimization**: Cache component scores, pre-compute weights

### Edge Cases

1. **Cold Start**: If no interactions, use popularity + segment
2. **No Similar Users**: Use behaviour + content + popularity
3. **All Products Scored Zero**: Return products with highest popularity

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
    ├─ Check data availability
    └─ Decide: which signals to emphasize
    ↓
[Recommendation Agent]
    ├─ Plan: [choose_strategy, hybrid_recommend, explain_recommendations]
    ├─ Execute: Call MCP tools
    ├─ Model Choice: Select hybrid_ranker
    ├─ Memory: Store plan, tool usage, strategy
    └─ Return: Recommendations with explanations
    ↓
[LLM Reasoning Server]
    ├─ Suggest weight adjustments
    ├─ Generate explanations
    └─ Return: Weights and explanations
    ↓
[Evaluation Agent]
    ├─ Validate recommendations
    ├─ Check for quality issues
    └─ Approve or request replan
    ↓
Output: Recommendations + explanations + metadata
```

### Planning

```json
{
  "goal": "Generate hybrid recommendations combining all signals",
  "intent": "hybrid_recommender",
  "requires_sql": false,
  "subtasks": [
    {
      "id": 1,
      "name": "choose_strategy",
      "agent": "recommendation_strategy_agent",
      "description": "Determine best combination of signals"
    },
    {
      "id": 2,
      "name": "hybrid_recommend",
      "agent": "recommendation_agent",
      "description": "Run weighted hybrid scoring"
    },
    {
      "id": 3,
      "name": "explain_recommendations",
      "agent": "recommendation_agent",
      "description": "Generate explanation for dominant signal"
    }
  ]
}
```

### LLM Strategy Selection

The LLM reasoning server analyzes customer profile and suggests strategy:

```
Input: {
  "interaction_count": 50,
  "engagement_score": 0.6,
  "purchase_categories": ["home", "books", "clothing"],
  "similar_users_found": 8,
  "cold_start": false
}

LLM Analysis:
- Rich interaction history → use collaborative filtering
- Multiple categories → use content affinity
- Similar users found → collaborative is reliable
- Not cold start → all signals available

Output: {
  "strategy": "collaborative",
  "reason": "Rich interaction history enables collaborative filtering",
  "method": "rule_based",
  "weights": {
    "collaborative": 0.4,
    "behaviour": 0.3,
    "content": 0.2,
    "popularity": 0.1
  }
}
```

### Tool Discovery

```
Registry Query: "Find tools for hybrid recommendation"
Registry Response: [
  {
    "tool": "choose_recommendation_strategy",
    "mcp_server": "llm_reasoning_server",
    "params": ["customer_profile"],
    "returns": ["strategy", "weights", "reason"]
  },
  {
    "tool": "hybrid_recommend",
    "mcp_server": "recommendation_server",
    "params": ["customer_id", "weights", "top_k"],
    "returns": ["product_id", "score", "cf_score", "behaviour_score", "content_score", "popularity_score"]
  },
  {
    "tool": "explain_recommendation",
    "mcp_server": "llm_reasoning_server",
    "params": ["product_id", "customer_id", "signals"],
    "returns": ["explanation", "dominant_signal"]
  }
]
```

### Model Selection

The agent selects `hybrid_ranker` which:
- Combines multiple scoring models
- Weights scores based on strategy
- Computes confidence scores
- Identifies dominant signals

### LLM Explanation

For each top recommendation, LLM generates explanation:

```
Input: {
  "product_id": "PROD-053",
  "customer_id": "CUST-001",
  "signals": {
    "collaborative": 0.983,
    "behaviour": 0.887,
    "content": 0.776,
    "popularity": 0.671
  }
}

LLM Analysis:
- Collaborative score is highest (0.983)
- Similar users purchased this item
- This is the dominant signal

Output: {
  "explanation": "Customers similar to you purchased this item",
  "dominant_signal": "collaborative",
  "confidence": 0.983
}
```

### Memory Integration

**Memory Updates**:
1. **Plan Memory**: Store generated plan
2. **Tool Usage Memory**: Log strategy selection and scoring
3. **Strategy Memory**: Store chosen strategy and weights
4. **Observation Memory**: Store dominant signals and explanations

**Memory Retrieval**:
- Check if similar customer was processed before
- Reuse strategy if applicable
- Learn from previous recommendations

### Key Differences from Deterministic

| Aspect | Deterministic | Dynamic |
|--------|---|---|
| **Weights** | Fixed (0.4/0.3/0.2/0.1) | Dynamic (LLM-suggested) |
| **Strategy** | Always hybrid | Dynamic (can choose alternative) |
| **Explanation** | None | LLM-generated |
| **Fallback** | None | Can fall back to simpler strategy |
| **Observability** | Low | High (strategy, weights, explanations visible) |

---

## Agentic Features Demonstrated

### 1. Strategy Selection
- LLM analyzes customer profile
- LLM suggests best strategy
- Strategy can be changed without code changes

### 2. Model Combination
- Multiple models combined (CF, behavior, content, popularity)
- Weights adjusted based on strategy
- Model performance tracked in memory

### 3. LLM Explanation
- LLM generates natural language explanations
- Explanations identify dominant signal
- Explanations improve user trust

### 4. Confidence Scoring
- Confidence computed from component scores
- Confidence indicates recommendation quality
- Confidence used for ranking

### 5. Explainability
- Strategy visible
- Weights visible
- Component scores visible
- Explanations visible
- Agent path visible

---

## Performance Characteristics

### Deterministic (A)
- **Latency**: ~150-200ms (all component scores)
- **Memory**: Minimal (no memory overhead)
- **Throughput**: Medium (multiple scoring operations)
- **Scalability**: O(U × P + I × P)

### Dynamic (B)
- **Latency**: ~300-400ms (LLM reasoning + execution + evaluation)
- **Memory**: ~3-5KB for strategy and explanations
- **Throughput**: Lower (LLM reasoning overhead)
- **Scalability**: Same O(U × P + I × P) but with LLM overhead

### Optimization Opportunities
1. **Component Score Caching**: Cache UC1, UC2, UC3 scores
2. **LLM Batching**: Batch LLM requests for multiple customers
3. **Async Explanation**: Generate explanations in background
4. **Approximate Scoring**: Use pre-computed scores

---

## Integration Points

### With Other UCs
- **UC1 (User-Based)**: Provides segment score (0.4 weight)
- **UC2 (Collaborative)**: Provides CF score (0.4 weight)
- **UC3 (Behaviour)**: Provides behavior score (0.3 weight)
- **UC5 (Cold Start)**: Used for new customers with interactions
- **UC6 (Cross-Segment)**: Batch version for segments
- **UC7 (Evaluation)**: Evaluated by evaluation UC
- **UC9 (Orchestrator)**: Primary recommendation UC

### With System Components
- **Agent Registry**: Discovers recommendation_agent, strategy_agent
- **Tool Registry**: Discovers hybrid_recommend tool
- **LLM Reasoning Server**: Suggests strategy and explanations
- **Memory Manager**: Stores strategy and explanations
- **MCP Servers**: Calls recommendation_server for scoring

---

## Testing Strategy

### Unit Tests
- Test score combination
- Test confidence computation
- Test dominant signal identification

### Integration Tests
- Test with real customer data
- Test LLM strategy selection
- Test LLM explanations
- Test memory updates

### Performance Tests
- Measure latency for different customer profiles
- Measure LLM reasoning time
- Measure memory usage
- Measure throughput

### Validation Tests
- Verify hybrid scores are accurate
- Verify explanations are reasonable
- Verify dominant signals are correct
- Verify no data leakage

---

## Error Handling

### Deterministic (A)
- **Component Score Failure**: Use available scores
- **Scoring Error**: Propagate error
- **Invalid Product**: Skip product

### Dynamic (B)
- **LLM Strategy Failure**: Use default weights (0.4/0.3/0.2/0.1)
- **LLM Explanation Failure**: Use generic explanation
- **Scoring Error**: Retry with exponential backoff
- **Evaluation Failure**: Log warning, return recommendations anyway

---

## Configuration

### Parameters
- `top_k`: Number of recommendations to return (default: 10)
- `cf_weight`: Collaborative filtering weight (default: 0.4)
- `behaviour_weight`: Behaviour score weight (default: 0.3)
- `content_weight`: Content score weight (default: 0.2)
- `popularity_weight`: Popularity weight (default: 0.1)

### Feature Flags
- `use_dynamic_planning`: Enable/disable dynamic planning (default: true)
- `use_llm_strategy`: Enable/disable LLM strategy selection (default: true)
- `use_llm_explanation`: Enable/disable LLM explanations (default: true)
- `use_memory`: Enable/disable memory system (default: true)

---

## References

- **Notebook**: `notebooks/agentic/05_level5_recommendation.ipynb` - UC4-A and UC4-B implementations
- **Code**: `agentic/recommendation_agent.py` - Recommendation agent implementation
- **Tools**: `mcp_servers/recommendation_server.py` - Hybrid recommendation tools
- **LLM**: `mcp_servers/llm_reasoning_server.py` - LLM strategy and explanation
- **Memory**: `memory/memory_manager.py` - Memory system implementation

---

**Status**: Specification Complete
**Last Updated**: [Current timestamp]
**Version**: 1.0
