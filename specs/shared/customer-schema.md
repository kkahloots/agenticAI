# 🧾 Customer Schema — Unified View

**TL;DR**: Single canonical record for a shopper, merging CRM, identity verification, purchase history, and engagement data. All agents read from this schema; only Level-3 (with approval) may write to it.

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `customer_id` | string | No | Unique customer identifier (e.g. `CUST-001`) |
| `full_name` | string | No | Customer's full name (EN / HU / AR / ZH / EL) |
| `email` | string | Yes | Primary email; null allowed |
| `phone` | string | Yes | Primary phone; duplicates possible across records |
| `preferred_language` | string | No | ISO 639-1 code: `en`, `hu`, `ar`, `zh`, `el` |
| `segment` | string | No | Behavioural label: `vip`, `casual`, `dormant_vip`, `at_risk`, `new` |
| `identity_status` | string | No | **Primary field**: `verified` \| `unverified` \| `pending` |
| `identity_expiry_date` | date | Yes | **Primary field**: Date identity verification expires; null if never completed |
| `kyc_status` | string | No | **Alias for `identity_status`** — backwards compatibility |
| `kyc_expiry_date` | date | Yes | **Alias for `identity_expiry_date`** — backwards compatibility |
| `country` | string | No | ISO 3166-1 alpha-2 country code (e.g. `HU`, `AE`, `GB`, `CN`, `GR`) |
| `fraud_score` | float | Yes | **Primary field**: 0.0–1.0; higher = more fraud risk; null → assign dataset average |
| `risk_score` | float | Yes | **Alias for `fraud_score`** used by the SQL analytics layer |
| `engagement_score` | float | Yes | 0.0–1.0; derived from browsing frequency, purchases, reviews |
| `purchase_categories` | array[string] | No | **Product categories purchased** (e.g. `["electronics", "clothing", "home", "sports", "beauty", "books", "food", "travel", "automotive", "toys"]`) |
| `lifetime_value` | float | Yes | **Total spend since account creation** (USD) — used in lead scoring instead of `account_balance` |
| `account_balance` | float | Yes | Current account balance (for backwards compatibility) |
| `return_risk` | float | Yes | **0.0–1.0 model score** for likelihood of product returns or chargebacks |
| `payment_delay_risk` | float | Yes | **Alias for `return_risk`** in some contexts |
| `consent_flags` | object | No | **Consent structure**: `{ marketing: bool, data_sharing: bool, sms: bool, email: bool }` |
| `last_interaction_date` | date | Yes | Date of most recent touchpoint (visit, purchase, support contact) |
| `promotion_eligibility` | array[string] | No | **Promotion codes** the customer qualifies for (e.g. `["PROMO-PREMIUM-MEMBERSHIP", "PROMO-LOYALTY-POINTS"]`) |
| `campaign_history` | array[object] | No | `[{ campaign_id, sent_date, channel, outcome }]` |
| `view_history` | array[string] | Yes | **Recommendation field**: Product IDs recently viewed (last 30 days) |
| `click_history` | array[string] | Yes | **Recommendation field**: Product IDs recently clicked |
| `search_history` | array[string] | Yes | **Recommendation field**: Recent search query strings |
| `user_embedding` | array[float] | Yes | **Recommendation field**: Normalised interaction vector for similarity computation |
| `interaction_matrix` | object | Yes | **Recommendation field**: Sparse `{ product_id: weight }` map of all interactions |

### Field Relationships

**Identity Fields**:
- **Primary**: `identity_status`, `identity_expiry_date`
- **Aliases**: `kyc_status`, `kyc_expiry_date` (backwards compatibility)
- Use `get_identity_status()` or `get_kyc_status()` to access

**Risk Fields**:
- **Primary**: `fraud_score` (0.0–1.0, fraud risk)
- **Alias**: `risk_score` (SQL layer compatibility)
- **Related**: `return_risk` (product return/chargeback risk)
- **Alias**: `payment_delay_risk` (some contexts)

**Value Fields**:
- **Primary**: `lifetime_value` (total historical spend)
- **Legacy**: `account_balance` (current balance)
- Lead scoring uses `lifetime_value`

**Consent Structure**:
```json
{
  "marketing": true,     // Can receive promotional messages
  "data_sharing": true,  // Allow data sharing with partners
  "sms": false,         // SMS notifications allowed
  "email": true         // Email notifications allowed
}
```

**Purchase Categories**:
Supported values: `electronics`, `clothing`, `home`, `sports`, `beauty`, `books`, `food`, `travel`, `automotive`, `toys`

**Upsell Category Mapping**:
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

### Recommendation Fields (Level‑5)

**Interaction Weights**:
- `purchase` → weight 3.0
- `click` → weight 1.0
- `view` → weight 0.5

**User Embedding**: Derived from the normalised row of the user–item interaction matrix. Used for cosine similarity in collaborative filtering.

**Cold Start Detection**: If `view_history`, `click_history`, and `interaction_matrix` are all null or empty, the customer is treated as a cold-start user.

### Notes

- `consent_flags.marketing = false` → Level-3 must not send promotional messages.
- `identity_status = "unverified"` → Level-3 must trigger identity re-verification before executing high-value actions. Use `get_identity_status()` (or the `get_kyc_status()` alias) to check.
- `fraud_score` and `return_risk` are model outputs; treat as read-only for agents.
- PII fields (`full_name`, `email`, `phone`) must be masked in logs and analytics outputs.
- `risk_score` in the SQLite `customers` table maps to `fraud_score` in `customers.json`.
