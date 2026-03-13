# 🧰 Agent Tool Definitions

**TL;DR**: 12 tools across all agents. Each tool is stateless, returns JSON, and must log every call to the audit trail.

---

## `search_customer_profile`

**Purpose**: Retrieve a customer record by ID or fuzzy name match.
**Agent**: Level-1, Level-3
**Inputs**: `{ customer_id?: string, full_name?: string, country?: string }`
**Outputs**: `{ customer: CustomerRecord | null, match_confidence: float }`
**Auth**: Bearer token; role `agent:read`
**Failure modes**: customer not found → return `null`; DB timeout → raise `ToolTimeoutError`
**Retry**: 2 retries with 500 ms backoff; fallback → return cached record if < 5 min old

---

## `search_policy_docs`

**Purpose**: Semantic search over a named ChromaDB collection (policies, emails, or CRM notes).
**Agent**: Level-1
**Inputs**: `{ query: string, doc_type?: "policy" | "email" | "note", top_k?: int }`
**Outputs**: `{ chunks: [{ text, source, doc_type, score }] }`
**Auth**: Bearer token; role `agent:read`
**Failure modes**: vector store unavailable → raise `ToolUnavailableError`; empty result → return `[]`
**Retry**: 1 retry; fallback → return `{ chunks: [], message: "Policy store unavailable" }`
**Collections**: `policy_docs` (default), `emails`, `notes` — routed automatically by `doc_type`

---

## `get_identity_status` / `get_kyc_status`

**Purpose**: Fetch current identity verification status and expiry for a customer. `get_kyc_status` is a backwards-compatible alias that adds `kyc_status` and `kyc_expiry_date` keys to the response.
**Agent**: Level-1, Level-3
**Inputs**: `{ customer_id: string }`
**Outputs**: `{ identity_status: string, identity_expiry_date: date | null, days_until_expiry: int | null, kyc_status: string (alias), kyc_expiry_date: date (alias) }`
**Note**: Primary fields are `identity_status` and `identity_expiry_date`. The `kyc_*` fields are aliases for backwards compatibility.
**Auth**: Bearer token; role `agent:read`; PII access required
**Failure modes**: customer not found → `404`; data unavailable → `503`
**Retry**: 3 retries with exponential backoff; fallback → surface error to orchestrator for human review

---

## `multi_query_search`

**Purpose**: LLM-expanded multi-query retrieval across all ChromaDB collections. Generates query variants, deduplicates results, and synthesises a grounded answer via RAG generation.
**Agent**: Level-1
**Inputs**: `{ query: string, doc_type?: "policy" | "email" | "note", top_k?: int }`
**Outputs**: `{ chunks: [{ text, source, doc_type, score }], query_variants: [string] }`
**Auth**: Bearer token; role `agent:read`
**Failure modes**: LLM unavailable → falls back to 3 rule-based query rewrites; empty result → return `{ chunks: [], message: "No documents found." }`
**Collections searched**: all three (`policy_docs`, `emails`, `notes`) when no `doc_type` specified

---



## `run_sql_query`

**Purpose**: Execute a validated, read-only SQL query against the customer database.
**Agent**: Level-2
**Inputs**: `{ sql: string, params?: object, max_rows?: int }`
**Outputs**: `{ rows: array, row_count: int, truncated: bool }`
**Auth**: Read-only DB credentials; role `agent:analytics`
**Failure modes**: SQL injection detected → reject immediately; timeout > 30 s → cancel; schema mismatch → return error with suggestion
**Retry**: No retry on validation failure; 1 retry on transient DB error

---

## `generate_segment`

**Purpose**: Run a clustering or rule-based segmentation on a customer subset.
**Agent**: Level-2
**Inputs**: `{ filters?: object, algorithm?: "kmeans" | "rules", n_clusters?: int }`
**Outputs**: `{ segments: [{ label, customer_ids, size, avg_risk_score, avg_engagement_score }] }`
**Auth**: Role `agent:analytics`
**Failure modes**: insufficient data (< 10 records) → warn and return partial result; model error → fallback to rule-based segmentation
**Retry**: 1 retry; fallback → rule-based segmentation with default thresholds

---

## `visualise`

**Purpose**: Generate a matplotlib bar or line chart from segment or analytics data and save to disk.
**Agent**: Level-2
**Inputs**: `{ data: object, chart_type?: "bar" | "line", title?: string }`
**Outputs**: `{ file_path: string }`
**Auth**: Role `agent:analytics`
**Failure modes**: empty data → return error; matplotlib unavailable → return error with install hint
**Retry**: No retry

---

## `analyze_sentiment`

**Purpose**: Classify text sentiment as positive, neutral, or negative using RoBERTa.
**Agent**: Level-2
**Inputs**: `{ text: string }`
**Outputs**: `{ sentiment: "positive" | "neutral" | "negative", confidence: float, scores: object }`
**Auth**: Role `agent:analytics`
**Failure modes**: transformers/torch not installed → warn once and return `{ sentiment: "neutral", confidence: 0.0 }`; model download in progress → timeout error
**Retry**: No retry; graceful degradation on missing dependency

---

## `summarize_text`

**Purpose**: Generate a concise summary of long text using BART.
**Agent**: Level-2
**Inputs**: `{ text: string, max_length?: int, min_length?: int }`
**Outputs**: `{ summary: string, compression_ratio: float }`
**Auth**: Role `agent:analytics`
**Failure modes**: transformers/torch not installed → warn once and return truncated input; text too short → return as-is
**Retry**: No retry; graceful degradation on missing dependency

---

## `get_customer_360`

**Purpose**: Return a unified view of a customer aggregating CRM, sales, social media, and support data.
**Agent**: Level-2
**Inputs**: `{ customer_id: string }`
**Outputs**: `{ customer_profile, sales: { transactions, total_count, total_amount, channels }, social: { posts, sentiment_breakdown }, support: { tickets, open_tickets }, summary }`
**Auth**: Role `agent:analytics`; PII access required
**Failure modes**: customer not found → `{ error: "customer_not_found" }`; data file missing → return partial view with available sources
**Retry**: No retry

---

## `get_sales_analytics`

**Purpose**: Aggregate sales transaction data with optional filters for revenue and channel insights.
**Agent**: Level-2
**Inputs**: `{ filters?: { customer_id?, product?, channel? } }`
**Outputs**: `{ total_transactions, total_revenue, avg_transaction_value, by_product, by_channel, top_product }`
**Auth**: Role `agent:analytics`
**Failure modes**: data file missing → return empty result with warning
**Retry**: No retry

---

## `get_support_analytics`

**Purpose**: Aggregate support ticket data with optional filters for operational insights.
**Agent**: Level-2
**Inputs**: `{ filters?: { customer_id?, type?, priority?, status? } }`
**Outputs**: `{ total_tickets, by_type, by_status, open_tickets, avg_resolution_hours, high_priority }`
**Auth**: Role `agent:analytics`
**Failure modes**: data file missing → return empty result with warning
**Retry**: No retry

---

## `score_leads`

**Purpose**: Score and rank customers as prospects for a given offer using a multi-factor lead score.
**Agent**: Level-3
**Inputs**: `{ offer_code: string, top_n?: int, segment?: string }`
**Outputs**: `{ offer_code, offer_name, total_eligible, returned, prospects: [{ customer_id, full_name, segment, lead_score, rationale }] }`
**Score formula**: `engagement_score * 0.4 + (1 - fraud_score) * 0.3 + balance_factor(lifetime_value) * 0.2 + recency_factor(last_interaction_date) * 0.1`
**Filters**: excludes `identity_status = "unverified"` and `consent_flags.marketing = false`
**Auth**: Role `agent:functional`
**Failure modes**: no eligible customers → return empty list; data file missing → return error
**Retry**: No retry

---

## `upsell_recommend`

**Purpose**: Recommend higher-tier or complementary product categories for a customer based on their current purchase history and segment.
**Agent**: Level-3
**Inputs**: `{ customer_id: string }`
**Outputs**: `{ customer_id, segment, current_categories, upsell_targets: [string], recommended_promo, promo_name, upsell_score, rationale }`
**Score formula**: `engagement_score * 0.5 + balance_factor(lifetime_value) * 0.3 + (1 - fraud_score) * 0.2`
**Auth**: Role `agent:functional`
**Failure modes**: customer not found → `{ error: "customer_not_found" }`; no purchase history → returns segment-based default promo
**Retry**: No retry

---

## `user_based_recommend`

**Purpose**: Recommend product categories based on what segment peers buy that this customer doesn't, weighted by engagement similarity.
**Agent**: Level-3
**Inputs**: `{ customer_id: string, top_n?: int }`
**Outputs**: `{ customer_id, segment, current_categories, peer_count, recommendations: [{ category, confidence }], rationale }`
**Algorithm**: Finds segment peers, identifies categories they own that target doesn't, weights by `1 - abs(target_engagement - peer_engagement)`
**Auth**: Role `agent:functional`
**Failure modes**: customer not found → error; no peer data → empty recommendations with explanation
**Retry**: No retry

---

## `collaborative_recommend`

**Purpose**: Cross-customer collaborative filtering using Jaccard similarity (70%) + engagement proximity (30%) to recommend new categories.
**Agent**: Level-3
**Inputs**: `{ customer_id: string, top_n?: int }`
**Outputs**: `{ customer_id, segment, current_categories, top_similar_customers: [string], recommendations: [{ category, confidence }], rationale }`
**Algorithm**: Computes `jaccard(purchase_categories) * 0.7 + (1 - abs(engagement_diff)) * 0.3`, finds top 10 similar customers, aggregates their categories
**Auth**: Role `agent:functional`
**Failure modes**: customer not found → error; no similar customers → empty recommendations with explanation
**Retry**: No retry

---

## `enrich_customer`

**Purpose**: Return simulated multi-source enrichment data for a customer (credit bureau, business registry, location API).
**Agent**: Level-3
**Inputs**: `{ customer_id: string }`
**Outputs**: `{ customer_id, enrichment: { credit_bureau_score, company_type, employees, location_score, branch_distance_km, data_sources }, offer_scores, top_offer }`
**Auth**: Role `agent:functional`; PII access required
**Failure modes**: customer not found → `{ error: "customer_not_found" }`
**Retry**: No retry

---

## `bulk_recommend`

**Purpose**: Generate a bulk campaign execution plan for an offer, with per-customer consent and approval checks.
**Agent**: Level-3
**Inputs**: `{ offer_code: string, segment?: string, top_n?: int }`
**Outputs**: `{ total_prospects, to_send, blocked, approval_required, bulk_approval_needed, execution_plan: [{ customer_id, action, channel, reason }] }`
**Auth**: Role `agent:functional`; bulk approval required if `to_send > APPROVAL_BULK_THRESHOLD`
**Failure modes**: no prospects → return empty plan; data unavailable → return error
**Retry**: No retry

---

## `recommend_offer`

**Purpose**: Select the best eligible offer for a customer based on profile and eligibility list.
**Agent**: Level-3
**Inputs**: `{ customer_id: string, context?: string }`
**Outputs**: `{ offer_code: string, offer_name: string, rationale: string, confidence: float }`
**Auth**: Role `agent:functional`
**Failure modes**: no eligible offers → return `{ offer_code: null }`; model unavailable → fallback to rule-based top offer
**Retry**: 1 retry; fallback → return highest-priority offer from `offer_eligibility` list

---

## `draft_email`

**Purpose**: Generate a personalised email body using a template and customer data.
**Agent**: Level-3
**Inputs**: `{ customer_id: string, template_id: string, variables?: object, language?: string }`
**Outputs**: `{ subject: string, body: string, language: string }`
**Auth**: Role `agent:functional`
**Failure modes**: template not found → `404`; LLM timeout → fallback to static template
**Retry**: 1 retry on LLM timeout; fallback → static template with variable substitution only

---

## `send_notification`

**Purpose**: Send an email, SMS, or push notification to a customer.
**Agent**: Level-3
**Inputs**: `{ customer_id: string, channel: "email" | "sms" | "push", content: object, dry_run?: bool }`
**Outputs**: `{ message_id: string, status: "sent" | "queued" | "blocked", reason?: string }`
**Auth**: Role `agent:functional:send`; requires `consent_flags` check before execution
**Failure modes**: consent blocked → return `{ status: "blocked", reason: "consent" }`; channel down → queue for retry; rate limit → queue
**Retry**: 3 retries with 1 min intervals; fallback → queue in dead-letter queue and alert human

---

## `create_case`

**Purpose**: Open a support or compliance case in the CRM/ticketing system.
**Agent**: Level-3
**Inputs**: `{ customer_id: string, case_type: "identity_reverification" | "kyc_remediation" | "complaint" | "collections" | "general", description: string, priority?: "low" | "medium" | "high" }`
**Outputs**: `{ case_id: string, status: "open", assigned_to: string }`
**Note**: `identity_reverification` is the primary case type for identity issues. `kyc_remediation` is supported for backwards compatibility.
**Auth**: Role `agent:functional`
**Failure modes**: CRM unavailable → cache locally and retry; duplicate case → return existing case ID
**Retry**: 3 retries; fallback → log to local queue and notify human operator

---

## `schedule_campaign`

**Purpose**: Schedule a multi-step campaign for a customer segment.
**Agent**: Level-4
**Inputs**: `{ campaign_name: string, segment_id: string, steps: [{ channel, template_id, delay_days }], start_date: date }`
**Outputs**: `{ campaign_id: string, scheduled_steps: int, estimated_reach: int }`
**Auth**: Role `agent:strategic`; requires human approval if `estimated_reach > 1000`
**Failure modes**: approval not granted → abort and notify; segment empty → return error; scheduling conflict → suggest alternative date
**Retry**: No auto-retry; human must re-approve

---

## `log_audit_event`

**Purpose**: Write an immutable audit record for every agent action.
**Agent**: All agents (called automatically by the framework)
**Inputs**: `{ agent_id: string, action: string, customer_id?: string, inputs: object, outputs: object, timestamp: datetime, user_id: string }`
**Outputs**: `{ audit_id: string, status: "logged" }`
**Auth**: Internal service account; not callable by external clients
**Failure modes**: audit store unavailable → buffer in memory and flush on recovery; never silently drop
**Retry**: Infinite retry with backoff until audit store recovers

---

## `request_human_approval`

**Purpose**: Pause a workflow and request explicit human sign-off before proceeding.
**Agent**: Level-3, Level-4, Orchestrator
**Inputs**: `{ workflow_id: string, action_description: string, risk_level: "low" | "medium" | "high", timeout_minutes?: int }`
**Outputs**: `{ approved: bool, approver_id: string | null, decision_time: datetime | null, notes?: string }`
**Auth**: Role `agent:approval_request`
**Failure modes**: timeout with no response → default to `approved: false`; approver unavailable → escalate to next approver in chain
**Retry**: No retry — each approval is a unique human decision; timeout triggers escalation

---

## Common Constraints (all tools)

- All inputs validated before execution; reject malformed requests with `400`
- All calls emit a `log_audit_event` record
- PII fields masked in all log outputs
- Rate limit: 60 calls/min per agent per tool
- All responses include `request_id` for traceability


---

## `recommend`

**Purpose**: Generate personalized product recommendations using hybrid algorithms (collaborative filtering, behaviour signals, content matching, popularity).
**Agent**: Level-5
**Inputs**: `{ customer_id: string, top_k?: int, exclude_purchased?: bool }`
**Outputs**: `{ customer_id, cold_start: bool, recommendations: [{ product_id, score, confidence, explanation, source_model }], similar_users: [string] }`
**Algorithm**: Hybrid ranking with configurable weights (default: collab 0.4, behaviour 0.3, content 0.2, popularity 0.1)
**Cold Start**: If customer has < 3 interactions, returns segment-based or popular items with `cold_start: true`
**Auth**: Role `agent:recommendation`
**Failure modes**: customer not found → `{ error: "customer_not_found" }`; no interactions → cold-start fallback; no similar users → rely on behaviour + content + popularity
**Retry**: No retry; graceful degradation on missing data

---

## `evaluate_recommendations`

**Purpose**: Offline evaluation of recommendation quality using precision@k, recall@k, MAP, and NDCG metrics.
**Agent**: Level-5
**Inputs**: `{ test_interactions: [{ customer_id, product_id, interaction_type, timestamp }], k?: int, sample_users?: int }`
**Outputs**: `{ users_evaluated: int, precision@k: float, recall@k: float, MAP: float, NDCG: float }`
**Methodology**: Splits each user's interactions 80/20, generates recommendations on train set, evaluates against test set
**Auth**: Role `agent:analytics`
**Failure modes**: insufficient data → return error with minimum requirements; no test interactions → return error
**Retry**: No retry

---

## `get_kpi_report`

**Purpose**: Retrieve KPI baseline (conversion rate, open rate) for a customer segment from historical campaign outcomes.
**Agent**: Level-4
**Inputs**: `{ segment_id: string }`
**Outputs**: `{ segment_id, campaigns_run: int, avg_conversion_rate: float, avg_open_rate: float, last_updated: datetime, summary: string }`
**Auth**: Role `agent:strategic`
**Failure modes**: no prior campaigns → return zeros with `summary: "no prior data"`; outcomes file missing → return zeros
**Retry**: No retry

---

## `record_campaign_outcome`

**Purpose**: Persist campaign results and compute KPI deviation for self-reflection loop.
**Agent**: Level-4
**Inputs**: `{ campaign_id: string, segment_id: string, goal: string, estimated_reach: int, kpi_baseline: object, actual_conversions?: int, actual_opens?: int }`
**Outputs**: `{ status: "recorded", needs_reanalysis: bool, deviation: float }`
**Deviation Logic**: `deviation = abs(actual_conversion_rate - baseline_conversion_rate)`. If `deviation > KPI_DEVIATION_THRESHOLD`, sets `needs_reanalysis: true`
**Auth**: Role `agent:strategic`
**Failure modes**: outcomes file not writable → buffer in memory; data invalid → reject with validation error
**Retry**: 1 retry on write failure; fallback → log to stderr and continue

---

## `check_kpi_deviation`

**Purpose**: Compare current segment KPI against target and flag if deviation exceeds threshold.
**Agent**: Level-4
**Inputs**: `{ segment_id: string, target_conversion_rate?: float }`
**Outputs**: `{ segment_id, current_conversion_rate: float, target_conversion_rate: float, deviation: float, action_required: bool }`
**Auth**: Role `agent:strategic`
**Failure modes**: segment not found → return zeros; no prior data → return `action_required: false`
**Retry**: No retry

---

## `reflect_and_replan`

**Purpose**: Self-reflection entry point for Level-4 strategic agent. Evaluates KPI deviation and recent campaign outcomes to decide if re-planning is needed.
**Agent**: Level-4
**Inputs**: `{ segment_id: string, goal: string }`
**Outputs**: `{ should_replan: bool, reason: string, recommended_action: string, deviation_report: object }`
**Logic**: Triggers re-plan if `KPI_DEVIATION_THRESHOLD` exceeded OR recent outcome flagged `needs_reanalysis: true`
**Auth**: Role `agent:strategic`
**Failure modes**: no prior data → `should_replan: false`; outcomes file missing → `should_replan: false`
**Retry**: No retry

---

## Common Constraints (all tools)

- All inputs validated before execution; reject malformed requests with `400`
- All calls emit a `log_audit_event` record
- PII fields masked in all log outputs
- Rate limit: 60 calls/min per agent per tool
- All responses include `request_id` for traceability
