# 📋 Level‑5 Recommendation Intelligence Agent Tasks

1. **Build Feature Extractor**: Extract user signals (purchase categories, view/click/search history, engagement score, segment) from the customer profile.
2. **Implement Collaborative Filter**: Compute user-user cosine similarity from interaction matrix. Return top-K similar users and their preferred items.
3. **Implement Behaviour Model**: Score candidate items using recency-weighted interaction history. Apply engagement multiplier.
4. **Implement Content Similarity**: Compute category overlap between customer purchase history and candidate item metadata.
5. **Implement Popularity Scorer**: Normalise item interaction counts across all users.
6. **Build Hybrid Ranker**: Combine all four scores using configurable weights. Return top-N ranked items with explanations.
7. **Handle Cold Start**: Detect new users (no interactions) and fall back to popular items filtered by segment. Detect new items and fall back to content similarity.
8. **Generate Explanations**: For each recommendation, produce a human-readable explanation based on the dominant scoring signal.
9. **Integrate with Orchestrator**: Add `recommendation` intent routing. Update `_rule_classify` and `_SYSTEM_PROMPT`.
10. **Add to Graph**: Register `level5_recommendation` node in `nonagentic/graph/graph.py`.
11. **Evaluation Harness**: Implement precision@k, recall@k, MAP, NDCG computation for offline evaluation.
12. **Create Demo Notebook**: Build `notebooks/level5_recommendation_agent.ipynb` with all use cases and visualisations.
