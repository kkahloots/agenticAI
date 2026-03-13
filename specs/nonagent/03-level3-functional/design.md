# 🛠️ Level‑3 Functional Agent Design

### Use Cases Implemented

| UC | Name | Description |
|----|------|-------------|
| UC1 | Lead Scoring | Rank prospects for a promotion using multi-factor lead score |
| UC2 | Customer Enrichment | Multi-source enrichment: credit bureau, business registry, location API |
| UC3 | Next-Best-Action (NBA) | Ranked offer scoring per customer |
| UC4 | Consent-Gated Notification | Send offer email with consent check |
| UC5 | Identity Gate | Block action on unverified identity, open remediation case |
| UC6 | Bulk Campaign Targeting | Segment-level execution plan with approval gates |
| UC7 | Return Risk Intervention | Identify high-return-risk customers and send win-back offers |
| UC8 | Campaign Results Dashboard | Analyse past campaign performance |
| UC9 | Guardrails | PII redaction and policy enforcement |
| UC10 | Upsell Recommendations | Recommend higher-tier products based on purchase history |
| UC11 | User-Based Recommendations | Recommend products based on segment peer behavior |
| UC12 | Collaborative Filtering | Cross-customer recommendations using similarity scoring |

### Multi‑Tool Workflow

1. **Trigger**: Receive a task from the orchestrator that requires action.
2. **Data Fetch**: Use `search_customer_profile` or `score_leads` to retrieve customer data.
3. **Decision Logic**: Apply NBA scoring, lead scoring, or recommendation algorithms to select the best action.
4. **Gate Checks**: Verify `identity_status` (identity gate) and `consent_flags` (consent gate) before acting.
5. **Action Execution**: Call `send_notification`, `draft_email`, or `create_case`.
6. **Logging & Audit**: Every action is recorded via `log_audit_event`.

### NBA Scoring Formula

`score = segment_match * 0.35 + cross_sell_trigger * 0.25 + engagement_score * 0.25 + (1 - return_risk) * 0.15`

Cross-sell rules:
- Customer bought `electronics` → `PROMO-PREMIUM-MEMBERSHIP` gets +0.25
- Customer bought `home` → `PROMO-BUNDLE-DEAL` gets +0.25
- Customer bought `clothing` → `PROMO-WINBACK` gets +0.25

### Lead Score Formula

`score = engagement_score * 0.4 + (1 - fraud_score) * 0.3 + balance_factor(lifetime_value) * 0.2 + recency_factor(last_interaction_date) * 0.1`

Balance factor:
- `lifetime_value >= 50,000` → 1.0
- `lifetime_value >= 20,000` → 0.7
- `lifetime_value >= 5,000` → 0.4
- `lifetime_value < 5,000` → 0.1

Recency factor:
- `last_interaction <= 30 days` → 1.0
- `last_interaction <= 90 days` → 0.7
- `last_interaction <= 180 days` → 0.5
- `last_interaction > 180 days` → 0.2

### Upsell Score Formula

`score = engagement_score * 0.5 + balance_factor(lifetime_value) * 0.3 + (1 - fraud_score) * 0.2`

### Recommendation Algorithms

#### 1. Upsell Recommendations (upsell_recommend)
Recommends higher-tier or complementary products based on current purchase categories and segment.

**Category Mapping**:
- `electronics` → `premium_electronics`, `accessories`
- `clothing` → `premium_fashion`, `accessories`
- `home` → `premium_home`, `garden`
- `sports` → `premium_sports`, `outdoor`
- `beauty` → `premium_beauty`, `wellness`
- `books` → `premium_books`, `courses`
- `food` → `premium_food`, `gourmet`
- `travel` → `premium_travel`, `experiences`
- `automotive` → `premium_automotive`, `accessories`
- `toys` → `premium_toys`, `educational`

**Segment-to-Promo Mapping**:
- `vip` → `PROMO-PREMIUM-MEMBERSHIP`
- `dormant_vip` → `PROMO-WINBACK`
- `at_risk` → `PROMO-LOYALTY-POINTS`
- `casual` → `PROMO-BUNDLE-DEAL`
- `new` → `PROMO-LOYALTY-POINTS`

**Returns**: Target categories, recommended promotion, and upsell score.

#### 2. User-Based Recommendations (user_based_recommend)
Recommends categories based on what segment peers buy, weighted by engagement similarity.

**Algorithm**:
1. Find all customers in the same segment
2. Identify categories peers own that target customer doesn't
3. Weight each category by engagement similarity: `1 - abs(target_engagement - peer_engagement)`
4. Normalize scores and return top N
5. Return empty list if no peer data available

**Returns**: Ranked category recommendations with confidence scores (0-1).

#### 3. Collaborative Filtering (collaborative_recommend)
Cross-customer recommendations using Jaccard similarity + engagement proximity.

**Algorithm**:
1. Compute similarity for each other customer: `jaccard * 0.7 + engagement_similarity * 0.3`
   - Jaccard = `|owned AND other_cats| / |owned OR other_cats|`
   - Engagement similarity = `1 - abs(target_engagement - other_engagement)`
2. Find top 10 most similar customers (neighbours)
3. Aggregate categories they own that target doesn't
4. Weight by similarity score
5. Return top N recommendations
6. Return empty list if no similar customers found

**Returns**: Ranked category recommendations with confidence scores, list of top-3 similar customers.

### Promotion Catalogue

| Code | Name | Target Segments |
|------|------|-----------------|
| `PROMO-PREMIUM-MEMBERSHIP` | Premium Membership | vip, dormant_vip, at_risk |
| `PROMO-LOYALTY-POINTS` | Loyalty Points Boost | vip, new, at_risk |
| `PROMO-BUNDLE-DEAL` | Bundle Deal | vip, dormant_vip, new |
| `PROMO-WINBACK` | Win-Back Offer | at_risk, casual, dormant_vip |

### Email Templates

| Template ID | Subject | Use Case |
|-------------|---------|----------|
| `T-PROMO-01` | Exclusive promotion just for you | UC4 consent-gated offer |
| `T-WINBACK-01` | We miss you — come back for a special offer | UC7 return risk win-back |

### Implementation Notes

- All tools are in `nonagentic/tools/functional.py` and `nonagentic/tools/leads.py`.
- **Identity Terminology**: `identity_status` and `identity_expiry_date` are the primary fields. `get_kyc_status()` is a backwards-compatible alias that also returns `kyc_status` and `kyc_expiry_date`.
- `bulk_recommend()` calls `score_leads()` internally and applies per-customer consent + fraud gates.
- All LLM calls go through `nonagentic/core/llm.py` universal factory — provider switchable via `LLM_PROVIDER`.
- Notebook demo: `notebooks/level3_functional_agent.ipynb` — all cells use utility functions from `notebooks/utils/`.

### Configurable Thresholds

All approval thresholds are read from environment variables via `nonagentic/core/config.py` — never hardcoded:

| Env var | Default | Purpose |
|---------|---------|---------|
| `APPROVAL_BULK_THRESHOLD` | 100 | Require human approval when notifying more than this many customers |
| `APPROVAL_RISK_SCORE_THRESHOLD` | 0.8 | Require approval when customer `fraud_score` exceeds this |
| `APPROVAL_PAYMENT_DELAY_THRESHOLD` | 0.8 | Require approval when `return_risk` exceeds this |

### Constraints

- Spending limits and approval thresholds must be configurable via env vars — see table above.
- The agent cannot change `identity_status` without human approval.
- `consent_flags.marketing = false` → no promotional messages, no exceptions.
- All actions must be logged for audit purposes.
