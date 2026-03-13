# 🎯 Level 5 — Recommendation Intelligence Agent

**TL;DR**: The recommendation engine generates personalised product suggestions for every customer by combining what similar customers bought, what the customer has browsed, and what is trending — returning a ranked list with explanations.

---

## Business Use Cases

### 1. Personalised Product Recommendations
A customer visits the store. The agent instantly surfaces the 10 products most likely to interest them, based on their purchase history and the behaviour of similar customers.

**Trigger**: Any request containing "recommend", "suggest", "next best offer", or "similar customers".

**Output**: Ranked product list with scores and plain-English explanations.

---

### 2. Re-engagement Campaigns (dormant_vip segment)
The CRM team wants to re-engage dormant VIP customers. The agent generates segment-level recommendations — the products most popular among dormant VIPs — to use as campaign hooks.

**Business value**: Higher relevance → higher open rates → higher conversion.

---

### 3. Cold Start — New Customer Onboarding
A brand-new customer has no purchase history. Instead of showing nothing, the agent falls back to the most popular items in their segment, ensuring a good first impression.

**Fallback chain**:
1. Segment-level popular items
2. Global popular items (if segment unknown)

---

### 4. Next Best Offer (NBA) for Level 3 Actions
Level 3 (Functional Agent) calls Level 5 to get the best product to include in a personalised email or push notification before sending it.

**Integration**: Level 3 → Level 5 → product ID → Level 3 sends notification.

---

### 5. Campaign Planning (Level 4 Integration)
The Strategic Agent uses Level 5 to identify which products to feature in a campaign for a given segment, then schedules the campaign via Level 3.

**Integration**: Level 4 → Level 5 → product list → Level 4 schedules campaign.

---

## Recommendation Models

### User-Based Recommendation
Aggregates interaction patterns from customers in the same segment. Items popular among segment peers (that the target customer hasn't seen) are surfaced.

**Best for**: Customers with limited personal history but a clear segment membership.

---

### Collaborative Filtering
Computes cosine similarity between user interaction vectors. Finds the K most similar users and surfaces items they interacted with.

```
similarity(userA, userB) = dot(A, B) / (||A|| × ||B||)
```

**Best for**: Customers with rich interaction history.

---

### Behaviour-Based Ranking
Scores items based on the customer's own recent activity:
- Purchases → weight 3.0
- Clicks → weight 1.0
- Views → weight 0.5

Multiplied by the customer's engagement score.

**Best for**: Active, high-engagement customers.

---

### Hybrid Ranking (Final Score)
Combines all signals into one ranked list:

```
score = 0.4 × collaborative
      + 0.3 × behaviour
      + 0.2 × content_similarity
      + 0.1 × popularity
```

Returns top-N items with explanations and confidence scores.

---

## Cold Start Handling

| Scenario | Detection | Strategy |
|----------|-----------|----------|
| New user | < 3 interactions | Segment-level popular items |
| Unknown segment | No segment label | Global top-K popular items |
| New product | 0 interactions | Content metadata similarity |
| Sparse data | < 3 interactions | Cluster-level aggregation |

---

## Evaluation Metrics

| Metric | What it measures | Target |
|--------|-----------------|--------|
| **Precision@10** | Of top-10 recommendations, fraction that are relevant | > 0.10 |
| **Recall@10** | Of all relevant items, fraction in top-10 | > 0.05 |
| **MAP** | Mean Average Precision — rewards correct items ranked higher | > 0.08 |
| **NDCG** | Position-sensitive ranking quality | > 0.15 |
| **CTR** | Click-through rate on served recommendations | > 2% |
| **Conversion Rate** | Purchase rate from recommendations | > 0.5% |

---

## Architecture

```
Request: "Recommend products for CUST-001"
         │
         ▼
Orchestrator (intent = recommendation)
         │
         ▼
Level 5 Recommendation Agent
   ├── Load customer profile + interactions
   ├── Collaborative filtering (cosine similarity)
   ├── Behaviour scoring (recency-weighted)
   ├── Content similarity (category overlap)
   ├── Hybrid ranking (weighted formula)
   └── Return top-K with explanations + audit log
```

---

## Escalation Paths

| From | To | When |
|------|----|------|
| Level 2 | Level 5 | Analytics discovers a segment → generate recommendations for it |
| Level 3 | Level 5 | Functional agent needs a product before sending a notification |
| Level 4 | Level 5 | Strategic agent needs next-best-offer candidates for a campaign |

---

## Demo Notebook

`notebooks/level5_recommendation_agent.ipynb`

| Section | What it shows |
|---------|--------------|
| Dataset Overview | Interaction distribution, segment breakdown |
| User-Based | Segment peer aggregation |
| Collaborative Filtering | Cosine similarity, similar users |
| Behaviour-Based | Click/view/purchase scoring |
| Hybrid Recommender | Combined ranking with explanations |
| Cold Start | Segment fallback for new users |
| Cross-User Segment | Aggregate recs for dormant_vip |
| Evaluation | Precision@10, Recall@10, MAP, NDCG |
| Visualisation | Similarity heatmap, score distribution, category coverage |
| Orchestrator Routing | Natural language → Level 5 intent |

---

## Key Business Benefits

- **Personalisation at scale** — every customer gets a unique ranked list
- **No dead-ends** — cold start always returns something relevant
- **Explainable** — every recommendation has a plain-English reason
- **Composable** — plugs into Level 3 (send) and Level 4 (campaign)
- **Measurable** — built-in evaluation harness for A/B testing
