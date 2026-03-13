# 🎯 Level‑5 Recommendation Agent Design

### Recommendation Pipeline

1. **Load Data**: Fetch customer profile, interaction history, and product catalogue.
2. **Cold-Start Check**: If customer has < 3 interactions, use segment-based fallback.
3. **Build User-Item Matrix**: Aggregate weighted interactions (purchase=3.0, click=1.0, view=0.5) with time decay.
4. **Compute Signals**:
   - **Collaborative**: Find similar users via cosine similarity, aggregate their items.
   - **Behaviour**: Score items based on customer's own clicks, views, purchases.
   - **Content**: Score items by category overlap with purchase history.
   - **Popularity**: Global item popularity across all users.
5. **Hybrid Ranking**: Combine signals with configurable weights.
6. **Exclude Purchased**: Remove already-interacted items (configurable).
7. **Return Top-K**: Ranked recommendations with scores, explanations, and source model.

### Hybrid Ranking Formula

`final_score = w_collab * collab_score + w_behaviour * behaviour_score + w_content * content_score + w_popularity * popularity_score`

**Default Weights** (configurable via `RECOMMENDATION_WEIGHTS` env var):
- `collab`: 0.4 (collaborative filtering)
- `behaviour`: 0.3 (user's own signals)
- `content`: 0.2 (category matching)
- `popularity`: 0.1 (trending items)

### Signal Computation

#### 1. Collaborative Filtering
**Algorithm**:
1. Build sparse user→{item: weight} matrix from all interactions.
2. For target customer, compute cosine similarity with all other users.
3. Filter neighbours with similarity ≥ `RECOMMENDATION_MIN_SIMILARITY` (default 0.05).
4. Take top 50 neighbours (configurable).
5. Aggregate items from neighbours (weighted by similarity).
6. Normalize scores to [0, 1].

**Time Decay**: Interactions older than 90 days are exponentially downweighted: `weight = 0.5^(age_days / 90)`.

#### 2. Behaviour Signals
**Algorithm**:
1. Extract customer's click history, view history, and purchase categories.
2. For each product:
   - If in click history: +0.5
   - If in view history: +0.2
   - If category matches purchase history: +0.3
3. Multiply by engagement score (0.5 + engagement * 0.5).
4. Add small random variation (normal distribution) for diversity.

#### 3. Content Matching
**Algorithm**:
1. Extract customer's purchase categories.
2. For each product, compute category overlap: `overlap = |customer_cats ∩ product_cats| / |customer_cats|`.
3. Score = min(overlap, 1.0).
4. Add small random variation for diversity.

#### 4. Popularity
**Algorithm**:
1. Count weighted interactions per product across all users.
2. Normalize to [0, 1] by dividing by max count.

### Cold-Start Handling

**Trigger**: Customer has < 3 interactions.

**Fallback Strategy**:
1. Find all customers in the same segment.
2. Aggregate their interactions (weighted by type).
3. If segment has data: return top-K segment-based recommendations (source: `segment_fallback`).
4. If segment has no data: return top-K global popular items (source: `cold_start`).
5. Confidence reduced to 0.7x for cold-start recommendations.

### Offline Evaluation

**Function**: `evaluate_recommendations(test_interactions, k=10, sample_users=50)`

**Metrics**:
- **Precision@K**: `|hits| / k` — fraction of top-K recommendations that were relevant.
- **Recall@K**: `|hits| / |ground_truth|` — fraction of relevant items in top-K.
- **MAP (Mean Average Precision)**: Average precision across all relevant items.
- **NDCG (Normalized Discounted Cumulative Gain)**: Ranking quality accounting for position.

**Methodology**:
1. Split each user's interactions: 80% train, 20% test.
2. Generate recommendations using train set.
3. Check if test items appear in top-K recommendations.
4. Compute metrics and average across sample users.

### Recommendation Output

```json
{
  "customer_id": "CUST-042",
  "cold_start": false,
  "recommendations": [
    {
      "product_id": "PROD-001",
      "score": 0.8234,
      "confidence": 0.9057,
      "explanation": "Customers similar to you purchased this item",
      "source_model": "hybrid"
    },
    ...
  ],
  "similar_users": ["CUST-015", "CUST-089", "CUST-042"],
  "error": null
}
```

### Implementation Notes

- All tools are in `nonagentic/tools/recommender.py`.
- Interaction data: `data/interactions.json` (customer_id, product_id, interaction_type, timestamp).
- Product data: `data/products.json` (product_id, category, tags, price, etc.).
- Customer data: `data/customers.json` (customer_id, segment, purchase_categories, engagement_score, etc.).
- Generate demo data: `python scripts/generate_recommendation_data.py`.
- Notebook demo: `notebooks/level5_recommendation_agent.ipynb`.

### Configurable Parameters

All parameters are read from environment variables via `nonagentic/core/config.py`:

| Env var | Default | Purpose |
|---------|---------|---------|
| `RECOMMENDATION_TOP_K` | 10 | Number of recommendations to return |
| `RECOMMENDATION_MIN_SIMILARITY` | 0.05 | Minimum cosine similarity threshold for neighbours |
| `RECOMMENDATION_COLD_START_K` | 5 | Number of recommendations for cold-start customers |
| `RECOMMENDATION_WEIGHTS` | `{"collab":0.4,"behaviour":0.3,"content":0.2,"popularity":0.1}` | Hybrid ranking weights (JSON) |

### Constraints

- Recommendations exclude already-interacted items by default (configurable).
- Cold-start recommendations have lower confidence (0.7x multiplier).
- Time decay ensures recent interactions are weighted more heavily.
- Similarity threshold prevents low-quality neighbours from influencing recommendations.
- All recommendations include explanations for transparency.
