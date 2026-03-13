# UC3: Behaviour-Based Ranking - Specification

## Overview

**Use Case**: Rank products based on a customer's own clicks, views, and purchases, weighted by engagement.

**Business Value**: Personalize recommendations based on individual customer behavior patterns.

**Complexity**: Medium | **Agentic Features**: LLM Feature Priority, Dynamic Strategy Selection, Memory

---

## Business Scenario

A customer (CUST-001) has clicked on home products, viewed books, and purchased clothing. The system ranks products by combining behavior signals (clicks, views, purchases) with content similarity.

**Input**: Customer ID (e.g., CUST-001), top_k (e.g., 10)
**Output**: Ranked list of products with behavior and content scores

---

## Deterministic Approach (Version A)

### Algorithm

1. **Extract Customer Behavior**
   - Get all interactions (views, clicks, purchases)
   - Categorize by interaction type
   - Extract purchase categories

2. **Compute Behavior Scores**
   - For each product:
     - `behavior_score = (views × w_view + clicks × w_click + purchases × w_purchase) / total_interactions`
     - Weights: w_view=0.1, w_click=0.3, w_purchase=0.6

3. **Compute Content Scores**
   - For each product:
     - `content_score = 1.0 if category in purchase_categories else 0.0`
     - Normalize by number of categories

4. **Combine Scores**
   - `combined_score = 0.7 × behavior_score + 0.3 × content_score`

5. **Rank and Return**
   - Sort products by combined score (descending)
   - Return top-K products

### Data Flow

```
Customer ID
    ↓
[Extract Behavior] → Views, clicks, purchases by product
    ↓
[Compute Behavior Scores] → Weighted interaction scores
    ↓
[Compute Content Scores] → Category affinity scores
    ↓
[Combine Scores] → Weighted combination
    ↓
[Rank Products] → Top-K recommendations
    ↓
Output: Ranked list with behavior and content scores
```

### Key Formulas

```
behavior_score(product) = (views × 0.1 + clicks × 0.3 + purchases × 0.6) / total_interactions

content_score(product) = 1.0 if category in purchase_categories else 0.0

combined_score(product) = 0.7 × behavior_score + 0.3 × content_score
```

### Implementation Details

- **Tool**: `behaviour_scores(customer_id, products)`
- **Data Source**: Interaction table, Product table
- **Complexity**: O(I × P) where I = interactions, P = products
- **Optimization**: Pre-compute behavior scores, cache category affinity

### Edge Cases

1. **No Interactions**: Return empty list
2. **No Purchase Categories**: Use all categories with equal weight
3. **All Products Scored Zero**: Return products with highest content score

---

## Dynamic Agentic Approach (Version B)

### Architecture

```
User Request
    ↓
[Orchestrator Agent]
    ↓
[Recommendation Strategy Agent]
    ├─ Analyze customer behavior
    ├─ Check feature availability
    └─ Decide: which features to emphasize
    ↓
[LLM Reasoning Server]
    ├─ Suggest feature priority
    ├─ Propose weight adjustments
    └─ Return: feature importance scores
    ↓
[Recommendation Agent]
    ├─ Plan: [select_features, behaviour_scores]
    ├─ Execute: Call MCP tools with LLM-suggested weights
    ├─ Model Choice: Select behaviour_model or content_model
    ├─ Memory: Store plan, tool usage, feature selection
    └─ Return: Recommendations with feature attribution
    ↓
[Evaluation Agent]
    ├─ Validate feature selection
    ├─ Check for quality issues
    └─ Approve or request replan
    ↓
Output: Recommendations + feature attribution
```

### Planning

```json
{
  "goal": "Rank products by customer behaviour and content signals",
  "intent": "behaviour_based_ranking",
  "requires_sql": false,
  "subtasks": [
    {
      "id": 1,
      "name": "select_features",
      "agent": "recommendation_agent",
      "description": "Choose relevant features for this customer"
    },
    {
      "id": 2,
      "name": "behaviour_scores",
      "agent": "recommendation_agent",
      "description": "Compute behaviour and content scores"
    }
  ]
}
```

### LLM Feature Priority

The LLM reasoning server analyzes customer behavior and suggests feature priorities:

```
Input: {
  "engagement_score": 0.6,
  "purchase_categories": ["home", "books", "clothing"],
  "interaction_counts": {"views": 50, "clicks": 30, "purchases": 20}
}

LLM Analysis:
- High engagement (0.6) → emphasize behavior signals
- Multiple categories → use content affinity
- Balanced interactions → use all interaction types

Output: {
  "features": [
    {"name": "behaviour", "priority": 1, "weight": 0.7, "reason": "High engagement"},
    {"name": "content", "priority": 2, "weight": 0.3, "reason": "Category preferences known"},
    {"name": "category_affinity", "priority": 3, "weight": 0.2, "reason": "Affinity computable"}
  ]
}
```

### Tool Discovery

```
Registry Query: "Find tools for behaviour-based ranking"
Registry Response: [
  {
    "tool": "select_features",
    "mcp_server": "recommendation_server",
    "params": ["customer_id", "available_features"],
    "returns": ["selected_features", "weights"]
  },
  {
    "tool": "behaviour_scores",
    "mcp_server": "recommendation_server",
    "params": ["customer_id", "products", "weights"],
    "returns": ["product_id", "behaviour_score", "content_score", "combined_score"]
  }
]
```

### Model Selection

The agent can select:
- `behaviour_model`: Emphasizes behavior signals
- `content_model`: Emphasizes content similarity
- `hybrid_model`: Combines both (default)

Selection based on:
- Customer engagement level
- Number of purchase categories
- Interaction history size

### Memory Integration

**Memory Updates**:
1. **Plan Memory**: Store generated plan
2. **Tool Usage Memory**: Log feature selection and scoring
3. **Feature Selection Memory**: Store which features were selected and why
4. **Observation Memory**: Store insights (e.g., "customer prefers home products")

**Memory Retrieval**:
- Check if similar customer was processed before
- Reuse feature selection if applicable
- Learn from previous feature selections

### Key Differences from Deterministic

| Aspect | Deterministic | Dynamic |
|--------|---|---|
| **Feature Selection** | Fixed (all features) | Dynamic (LLM-suggested) |
| **Weights** | Fixed (0.7/0.3) | Dynamic (LLM-proposed) |
| **Model Selection** | Implicit | Explicit (behaviour/content/hybrid) |
| **LLM Reasoning** | None | LLM suggests feature priority |
| **Observability** | Low | High (feature attribution visible) |

---

## Agentic Features Demonstrated

### 1. LLM Feature Priority
- LLM analyzes customer behavior
- LLM suggests which features to emphasize
- LLM provides reasoning for suggestions

### 2. Dynamic Strategy Selection
- Strategy agent decides which model to use
- Model selection based on customer profile
- Model can be changed without code changes

### 3. Feature Attribution
- Memory stores which features were selected
- Memory stores feature weights
- Output includes feature attribution

### 4. Hybrid ML + LLM
- Classical ML (behavior scoring)
- LLM reasoning (feature priority)
- Deterministic fallback (fixed weights)

### 5. Explainability
- Feature selection visible
- Feature weights visible
- Feature attribution in output
- Agent path visible

---

## Performance Characteristics

### Deterministic (A)
- **Latency**: ~50-75ms (behavior + content scoring)
- **Memory**: Minimal (no memory overhead)
- **Throughput**: High (no LLM overhead)
- **Scalability**: O(I × P) where I = interactions, P = products

### Dynamic (B)
- **Latency**: ~200-300ms (LLM reasoning + execution + evaluation)
- **Memory**: ~2-3KB for feature selection and metadata
- **Throughput**: Lower (LLM reasoning overhead)
- **Scalability**: Same O(I × P) but with LLM overhead

### Optimization Opportunities
1. **Feature Caching**: Cache feature selection for similar customers
2. **LLM Batching**: Batch LLM requests for multiple customers
3. **Approximate Scoring**: Use pre-computed behavior scores
4. **Async LLM**: Run LLM reasoning in background

---

## Integration Points

### With Other UCs
- **UC1 (User-Based)**: Can combine segment score with behavior score
- **UC2 (Collaborative)**: Can combine collaborative score with behavior score
- **UC4 (Hybrid)**: Behavior score is one component
- **UC5 (Cold Start)**: Can use behavior score for new customers with interactions

### With System Components
- **Agent Registry**: Discovers recommendation_agent
- **Tool Registry**: Discovers behaviour_scores tool
- **LLM Reasoning Server**: Suggests feature priority
- **Memory Manager**: Stores feature selection and insights
- **MCP Servers**: Calls recommendation_server for scoring

---

## Testing Strategy

### Unit Tests
- Test behavior score calculation
- Test content score calculation
- Test score combination
- Test edge cases

### Integration Tests
- Test with real customer data
- Test LLM feature priority suggestions
- Test memory updates
- Test model selection

### Performance Tests
- Measure latency for different interaction sizes
- Measure LLM reasoning time
- Measure memory usage
- Measure throughput

### Validation Tests
- Verify behavior scores are accurate
- Verify content scores are accurate
- Verify LLM suggestions are reasonable
- Verify feature attribution is correct

---

## Error Handling

### Deterministic (A)
- **No Interactions**: Return empty list
- **Scoring Error**: Propagate error
- **Invalid Product**: Skip product

### Dynamic (B)
- **LLM Reasoning Failure**: Use default weights (0.7/0.3)
- **Feature Selection Failure**: Use all features
- **Scoring Error**: Retry with exponential backoff
- **Evaluation Failure**: Log warning, return recommendations anyway

---

## Configuration

### Parameters
- `top_k`: Number of recommendations to return (default: 10)
- `behaviour_weight`: Weight for behavior score (default: 0.7)
- `content_weight`: Weight for content score (default: 0.3)
- `w_view`: Weight for views (default: 0.1)
- `w_click`: Weight for clicks (default: 0.3)
- `w_purchase`: Weight for purchases (default: 0.6)

### Feature Flags
- `use_dynamic_planning`: Enable/disable dynamic planning (default: true)
- `use_llm_feature_priority`: Enable/disable LLM feature priority (default: true)
- `use_memory`: Enable/disable memory system (default: true)
- `use_evaluation`: Enable/disable evaluation agent (default: true)

---

## References

- **Notebook**: `notebooks/agentic/05_level5_recommendation.ipynb` - UC3-A and UC3-B implementations
- **Code**: `agentic/recommendation_agent.py` - Recommendation agent implementation
- **Tools**: `mcp_servers/recommendation_server.py` - Behavior scoring tools
- **LLM**: `mcp_servers/llm_reasoning_server.py` - LLM feature priority suggestions
- **Memory**: `memory/memory_manager.py` - Memory system implementation

---

**Status**: Specification Complete
**Last Updated**: [Current timestamp]
**Version**: 1.0
