# 📋 Level‑3 Functional Agent Tasks

## Implemented

1. **Lead Scoring** (`src/tools/leads.py: score_leads`): Rank customers as prospects for a given promotion using a multi-factor score (engagement, fraud, lifetime value, recency). Filters by verified/pending identity and marketing consent.

2. **Customer Enrichment** (`src/tools/leads.py: enrich_customer`): Simulate multi-source enrichment from credit bureau, business registry, and location API. Returns credit score, company type, location score, branch distance, and best offer match.

3. **NBA Recommendation** (`src/tools/functional.py: recommend_offer`): Score all eligible promotions for a customer using segment match, cross-sell trigger, engagement, and return-risk reliability. Returns ranked offer list with rationale.

4. **Consent-Gated Notification** (`src/tools/functional.py: send_notification`): Check `consent_flags.marketing`, `consent_flags.email`, and `consent_flags.sms` before sending. Returns `blocked` status with reason if consent is missing.

5. **Email Drafting** (`src/tools/functional.py: draft_email`): Generate personalised email from template (`T-PROMO-01`, `T-WINBACK-01`) using customer name and offer variables. Respects `preferred_language`.

6. **Identity Gate** (`src/tools/customer.py: get_identity_status`): Check `identity_status` and `identity_expiry_date`. If unverified or expired, open a remediation case via `create_case`.

7. **Case Management** (`src/tools/functional.py: create_case`): Open a support/compliance case with deduplication — returns existing open case if one already exists for the same customer and type.

8. **Bulk Campaign** (`src/tools/leads.py: bulk_recommend`): Generate a segment-level execution plan. Per-customer: check consent → check fraud gate → assign channel → flag for approval if needed. Returns `bulk_approval_needed` flag when total reach exceeds `APPROVAL_BULK_THRESHOLD`.

9. **Return Risk Intervention** (`notebooks/level3_functional_agent.ipynb UC7`): Filter customers by `return_risk > 0.7` and verified/pending identity, then send win-back offers via `send_notification`.

10. **Upsell Recommendation** (`src/tools/leads.py: upsell_recommend`): Recommend higher-tier categories based on current purchase history and segment.

11. **Collaborative Filtering** (`src/tools/leads.py: collaborative_recommend`): Cross-customer Jaccard similarity + engagement proximity to recommend new categories.

12. **User-Based Recommendation** (`src/tools/leads.py: user_based_recommend`): Segment-peer-based category recommendations weighted by engagement similarity.

## Notebook Utilities

All Level-3 notebook cells use utility functions from `notebooks/utils/visualization_helpers.py`:
- `display_lead_scoring_results`, `display_customer_enrichment`, `display_nba_recommendations`
- `display_consent_notification`, `display_blocked_example`, `display_kyc_gate`
- `display_campaign_execution_plan`, `display_return_risk_intervention`
- `display_campaign_results_dashboard`
