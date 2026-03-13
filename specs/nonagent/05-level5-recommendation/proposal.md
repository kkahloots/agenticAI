# 🎁 Level‑5 Recommendation Agent Proposal

**TL;DR**: This agent generates personalized product recommendations using hybrid algorithms combining collaborative filtering, behaviour signals, content matching, and popularity. It handles cold-start scenarios and provides explainable recommendations.

### What & Why (ELI5)

When you ask "What should we recommend to customer CUST-042?", this agent looks at what similar customers bought, what this customer has browsed and purchased, what categories they prefer, and what's trending. It combines all these signals into a ranked list of products with confidence scores and explanations.

### Formula Rule

`IF request is for product recommendations OR next-best-product suggestions THEN use recommendation agent ELSE fallback.`

### Explanation

The recommendation agent is responsible for generating personalized product suggestions. It uses a hybrid approach:
- **Collaborative Filtering**: Find similar customers and recommend what they bought
- **Behaviour Signals**: Weight customer's own clicks, views, and purchases
- **Content Matching**: Score products by category overlap with purchase history
- **Popularity**: Include trending items as a baseline signal

For new customers with insufficient interaction history (cold start), it falls back to segment-based or global popularity recommendations.

### What Is NOT

- ❌ Not responsible for executing recommendations (sending emails, etc.) — that's Level 3.
- ❌ Does not modify customer data or create cases.
- ❌ Does not perform strategic planning or campaign orchestration.

### Edge Cases

- **Cold Start**: Customer has < 3 interactions → return segment-based or popular items.
- **No Similar Users**: Collaborative filtering finds no neighbours → rely on behaviour + content + popularity.
- **No Interactions**: Customer has no purchase/click/view history → return segment-based recommendations.
- **All Products Purchased**: Customer has bought everything → return empty list with explanation.
- **Sparse Data**: Few products in system → return all available items ranked by relevance.

### Examples

✅ *"Generate top 10 recommendations for customer CUST-042."* → hybrid recommendations with explanations.

✅ *"What products should we recommend to CUST-099 based on similar customers?"* → collaborative filtering + hybrid ranking.

✅ *"Recommend top 5 items for a new customer in the VIP segment."* → cold-start segment-based recommendations.

✅ *"Evaluate recommendation quality for the past month."* → offline evaluation (precision@k, recall@k, MAP, NDCG).

❌ *"Send recommendations to all customers."* → not a Level 5 task (that's Level 3/4).
