# ⚠️ Level‑5 Recommendation Intelligence Agent Edge Cases

### What Is NOT

- Not authorised to send recommendations directly to customers — delegate to Level‑3.
- Does not create or modify promotions — that is Level‑4's responsibility.
- Does not alter customer records or interaction data.

### Edge Cases and Handling

**Cold Start — New User**
- Condition: Customer has no `view_history`, `click_history`, or purchase interactions.
- Handling: Return top-K popular items filtered by the customer's `segment`. If segment is also unknown, return global top-K popular items.
- Output flag: `"cold_start": true`, `"source_model": "popularity"`

**Cold Start — New Item**
- Condition: A product has zero interactions in the interaction matrix.
- Handling: Use content metadata similarity (category tags, description keywords) to find similar items that do have interactions.
- Output flag: `"source_model": "content_similarity"`

**Sparse Interactions**
- Condition: Customer has fewer than 3 interactions.
- Handling: Fall back to cluster/segment-level aggregated preferences. Use the average interaction vector of all customers in the same segment.
- Output flag: `"source_model": "segment_fallback"`

**No Similar Users Found**
- Condition: All cosine similarity scores fall below `RECOMMENDATION_MIN_SIMILARITY` threshold.
- Handling: Skip collaborative score (set to 0), rely on behaviour + content + popularity scores only.
- Log: Warning in audit trail.

**Consent Restrictions**
- Condition: `consent_flags.data_sharing = false`.
- Handling: Do not use cross-user data for this customer. Fall back to behaviour-based and content-based recommendations only.

**All Items Already Purchased**
- Condition: All top-ranked items are already in the customer's purchase history.
- Handling: Filter out already-purchased items before returning results. If fewer than `top_k` items remain, supplement with next-best items.

**Empty Product Catalog**
- Condition: No products available in the catalog.
- Handling: Return empty recommendations with explanation `"No products available"`.

**High Fraud Score**
- Condition: `fraud_score > 0.8`.
- Handling: Still generate recommendations but flag result with `"fraud_risk": true`. Downstream Level‑3 agent must check before acting.
