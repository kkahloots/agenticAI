# UC2: Collaborative Filtering - Specification

## Overview

**Use Case**: Find customers with similar interaction patterns and use their preferences to recommend products.

**Business Value**: Discover hidden patterns in user behavior to provide personalized recommendations.

**Complexity**: High | **Agentic Features**: Dynamic Tool Selection, Model Choice, Memory

---

## Business Scenario

A customer (CUST-001) has a unique interaction pattern. The system finds 8 similar customers and recommends products they liked but CUST-001 hasn't purchased yet.

**Input**: Customer ID (e.g., CUST-001), top_k (e.g., 8)
**Output**: Ranked list of 10 recommended products with similarity scores

---

## Deterministic Approach (Version A)

### Algorithm

1. **Build User-Item Matrix**
   - Create sparse matrix: rows = customers, columns = products
   - Values = interaction counts (views, clicks, purchases)
   - Normalize by interaction type weights

2. **Compute Similarity**
   - For target customer, compute cosine similarity with all other customers
   - Formula: `similarity = dot(user_vector_1, user_vector_2) / (norm(user_vector_1) × norm(user_vector_2))`

3. **Find Similar Users**
   - Sort by similarity score (descending)
   - Select top-K similar users
   - Exclude target customer

4. **Aggregate Preferences**
   - For each product not purchased by target:
     - Compute weighted score = sum(similarity × similar_user_purchase_count)
     - Normalize by number of similar users

5. **Rank and Return**
   - Sort products by weighted score (descending)
   - Return top-K products

### Data Flow

```
Customer ID
    ↓
[Build User-Item Matrix] → Sparse matrix (customers × products)
    ↓
[Compute Cosine Similarity] → Similarity scores for all customers
    ↓
[Find Similar Users] → Top-K similar customers
    ↓
[Aggregate Preferences] → Product scores from similar users
    ↓
[Rank Products] → Top-K recommendations
    ↓
Output: Ranked list with similarity metadata
```

### Key Formulas

```
cosine_similarity(u1, u2) = dot(u1, u2) / (||u1|| × ||u2||)

collaborative_score(product) = sum(similarity(target, similar_user) × purchase_count(similar_user, product)) / count(similar_users)
```

### Implementation Details

- **Tool**: `collaborative_scores(customer_id, top_k=8)`
- **Data Source**: User-item matrix from interactions
- **Complexity**: O(U × P) where U = users, P = products
- **Optimization**: Use sparse matrix representation, pre-compute similarities

### Edge Cases

1. **New User**: No interaction history, similarity = 0 with all users
2. **Unique User**: No similar users found, return empty list
3. **All Products Purchased**: Return products with lowest similarity to avoid duplicates

---

## Dynamic Agentic Approach (Version B)

### Architecture

```
User Request
    ↓
[Orchestrator Agent]
    ↓
[Recommendation Strategy Agent]
    ├─ Analyze interaction history
    ├─ Check data availability
    └─ Decide: user-user vs item-item vs segment fallback
    ↓
[Recommendation Agent]
    ├─ Plan: [build_user_item_matrix, collaborative_scores]
    ├─ Execute: Call MCP tools
    ├─ Model Choice: Select collaborative_model
    ├─ Memory: Store plan, tool usage, observation
    └─ Return: Recommendations with metadata
    ↓
[Evaluation Agent]
    ├─ Validate similarity scores
    ├─ Check for quality issues
    └─ Approve or request replan
    ↓
Output: Recommendations + metadata
```

### Planning

```json
{
  "goal": "Find similar users and recommend products they liked",
  "intent": "collaborative_filtering",
  "requires_sql": false,
  "subtasks": [
    {
      "id": 1,
      "name": "build_user_item_matrix",
      "agent": "recommendation_agent",
      "description": "Compute interaction vectors for similarity"
    },
    {
      "id": 2,
      "name": "collaborative_scores",
      "agent": "recommendation_agent",
      "description": "Compute cosine similarity and score candidates"
    }
  ]
}
```

### Tool Discovery

```
Registry Query: "Find tools for collaborative filtering"
Registry Response: [
  {
    "tool": "build_user_item_matrix",
    "mcp_server": "recommendation_server",
    "params": ["interactions"],
    "returns": ["matrix", "customer_ids", "product_ids"]
  },
  {
    "tool": "collaborative_scores",
    "mcp_server": "recommendation_server",
    "params": ["customer_id", "matrix", "top_k"],
    "returns": ["product_id", "score", "similar_users"]
  }
]
```

### Model Selection

The agent selects `collaborative_model` which implements:
- Cosine similarity computation
- Sparse matrix operations
- Efficient top-K selection

### Memory Integration

**Memory Updates**:
1. **Plan Memory**: Store generated plan
2. **Tool Usage Memory**: Log matrix building and similarity computation
3. **Observation Memory**: Store similar users found, similarity scores

**Memory Retrieval**:
- Check if user-item matrix was recently computed
- Reuse cached similarity scores
- Learn from previous collaborative recommendations

### Key Differences from Deterministic

| Aspect | Deterministic | Dynamic |
|--------|---|---|
| **Strategy Selection** | Fixed (always collaborative) | Dynamic (can choose alternative) |
| **Model Selection** | Implicit | Explicit (collaborative_model) |
| **Similarity Computation** | Direct | Via MCP tool |
| **Fallback** | None | Can fall back to segment-based |
| **Observability** | Low | High (similar users visible) |

---

## Agentic Features Demonstrated

### 1. Dynamic Tool Selection
- Tools discovered from registry
- Tool parameters are introspectable
- Can switch between user-user and item-item similarity

### 2. Model Choice
- Agent selects collaborative_model
- Model can be swapped without code changes
- Model performance tracked in memory

### 3. Memory System
- Stores similar users found
- Stores similarity scores
- Enables learning from past recommendations

### 4. Fallback Strategy
- If collaborative filtering fails, can fall back to segment-based
- Fallback decision made by strategy agent
- Fallback tracked in memory

### 5. Explainability
- Similar users visible in output
- Similarity scores visible
- Agent path visible: orchestrator → strategy → recommendation → evaluation

---

## Performance Characteristics

### Deterministic (A)
- **Latency**: ~100-150ms (matrix building + similarity computation)
- **Memory**: O(U × P) for matrix storage
- **Throughput**: Medium (matrix operations are expensive)
- **Scalability**: O(U × P) complexity

### Dynamic (B)
- **Latency**: ~200-300ms (planning + execution + evaluation)
- **Memory**: O(U × P) + ~2-3KB for metadata
- **Throughput**: Lower (planning overhead)
- **Scalability**: Same O(U × P) but with planning overhead

### Optimization Opportunities
1. **Matrix Caching**: Pre-compute and cache user-item matrix
2. **Approximate Similarity**: Use LSH for approximate nearest neighbors
3. **Batch Processing**: Compute similarities for multiple users at once
4. **Incremental Updates**: Update matrix incrementally instead of recomputing

---

## Integration Points

### With Other UCs
- **UC1 (User-Based)**: Can be used as alternative to segment-based
- **UC3 (Behaviour-Based)**: Can combine collaborative + behavior scores
- **UC4 (Hybrid)**: Collaborative score is one component
- **UC5 (Cold Start)**: Not applicable (requires interaction history)

### With System Components
- **Agent Registry**: Discovers recommendation_agent
- **Tool Registry**: Discovers collaborative_scores tool
- **Memory Manager**: Stores similar users and similarity scores
- **MCP Servers**: Calls recommendation_server for matrix and scores

---

## Testing Strategy

### Unit Tests
- Test cosine similarity calculation
- Test matrix building
- Test edge cases (new user, unique user)

### Integration Tests
- Test with real customer data
- Test memory updates
- Test fallback to segment-based

### Performance Tests
- Measure latency for different matrix sizes
- Measure memory usage
- Measure throughput

### Validation Tests
- Verify similar users are actually similar
- Verify recommendations are relevant
- Verify no data leakage

---

## Error Handling

### Deterministic (A)
- **Matrix Build Failure**: Return empty list
- **Similarity Computation Error**: Propagate error
- **No Similar Users**: Return empty list

### Dynamic (B)
- **Planning Failure**: Log error, fall back to segment-based
- **Matrix Build Failure**: Retry with exponential backoff
- **Similarity Computation Error**: Use approximate similarity
- **Evaluation Failure**: Log warning, return recommendations anyway

---

## Configuration

### Parameters
- `top_k`: Number of similar users to find (default: 8)
- `min_similarity`: Minimum similarity threshold (default: 0.1)
- `matrix_cache_ttl`: Cache time-to-live in seconds (default: 3600)

### Feature Flags
- `use_dynamic_planning`: Enable/disable dynamic planning (default: true)
- `use_approximate_similarity`: Use LSH for approximate similarity (default: false)
- `use_memory`: Enable/disable memory system (default: true)

---

## References

- **Notebook**: `notebooks/agentic/05_level5_recommendation.ipynb` - UC2-A and UC2-B implementations
- **Code**: `agentic/recommendation_agent.py` - Recommendation agent implementation
- **Tools**: `mcp_servers/recommendation_server.py` - Collaborative filtering tools
- **Memory**: `memory/memory_manager.py` - Memory system implementation

---

**Status**: Specification Complete
**Last Updated**: [Current timestamp]
**Version**: 1.0
