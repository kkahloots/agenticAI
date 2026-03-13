# ⚠️ Level‑3 Functional Agent Edge Cases

### What Is NOT

- Not allowed to modify `fraud_score`, `return_risk`, or `identity_status` directly.
- Does not decide long‑term strategy or set campaign KPIs.
- Cannot initiate financial transactions or issue refunds.

### Edge Cases and Handling

- **Customer Opt‑Out** (`consent_flags.marketing = false`): `send_notification` returns `{ status: "blocked", reason: "consent_marketing" }`. The action is logged and skipped — no retry.

- **Channel Consent Missing** (`consent_flags.email = false` and `consent_flags.sms = false`): `bulk_recommend` marks the customer as `blocked` with reason `no_channel_consent` in the execution plan.

- **Unverified Identity** (`identity_status = "unverified"`): `score_leads` excludes these customers entirely. If encountered in UC5/UC7, `create_case` opens an `identity_reverification` case instead of proceeding with the action.

- **High Fraud Score** (`fraud_score > APPROVAL_RISK_SCORE_THRESHOLD`): `bulk_recommend` marks the customer as `approval_required` rather than `send`. Human must approve before the notification is sent.

- **High Return Risk with No Consent Channel**: Customer is filtered out of the win-back list in UC7 — `send` is not attempted.

- **Duplicate Case**: `create_case` checks for an existing open case of the same type for the same customer and returns the existing `case_id` rather than creating a duplicate.

- **No Eligible Promotions**: `recommend_offer` returns `{ offer_code: null, confidence: 0.0, rationale: "No eligible promotions" }`. Callers must handle the null offer gracefully.

- **Bulk Approval Threshold Exceeded**: When `(to_send + approval_required) > APPROVAL_BULK_THRESHOLD`, `bulk_recommend` sets `bulk_approval_needed: true`. The orchestrator must pause and call `request_human_approval` before proceeding.

- **Template Not Found**: `draft_email` returns `{ error: "template_not_found: <id>" }` if the `template_id` is not in the catalogue.
