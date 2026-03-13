# 💼 Business Case — Value, ROI, Risk & Operating Model

**TL;DR**: This system automates customer operations across 8 use cases, reduces manual effort, and enables proactive revenue growth — with human oversight built in at every high-risk step.

---

## Business Value by Use Case

| Use Case | Agent Level | Business Outcome |
|----------|------------|-----------------|
| Unified customer view | L1 | Faster agent response; single source of truth |
| KYC / compliance retrieval | L1 | Reduced compliance breach risk; faster remediation |
| Ad hoc analytics | L2 | Self-serve insights; reduced BI backlog |
| Customer segmentation | L2 | Precise targeting; lower campaign waste |
| Upsell recommendations | L3 | Higher conversion; personalised at scale |
| Customer communication automation | L3 | Faster outreach; consistent messaging |
| Collections / payment follow-up | L3 | Reduced delinquency; earlier intervention |
| Campaign orchestration | L4 | End-to-end automation; outcome-driven optimisation |

---

## ROI Indicators

- **Efficiency**: Automating KYC lookups and segmentation queries frees analyst time estimated at 2–4 hours/day per team.
- **Revenue uplift**: Personalised upsell campaigns driven by Level-3 targeting typically improve conversion rates by 15–25 % vs. batch campaigns.
- **Risk reduction**: Proactive payment-delay detection (Level-3) reduces collections cost by intervening 30+ days earlier.
- **Compliance**: Automated KYC expiry tracking eliminates manual monitoring and reduces regulatory exposure.

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| AI sends message to opted-out customer | Low | High | Consent check enforced in `send_notification` tool |
| Incorrect SQL query returns wrong segment | Medium | Medium | Human review required before Level-2 output triggers action |
| KYC-expired customer receives financial offer | Low | High | Level-3 blocks action and creates remediation case automatically |
| Campaign reaches unintended audience | Low | High | `schedule_campaign` requires human approval if reach > 1,000 |
| PII exposed in logs | Low | Critical | PII masking enforced at tool output layer |
| Agent acts on stale data | Medium | Medium | Customer cache TTL = 5 minutes; agents flag stale data |

---

## Operating Model

```
Human roles:
  - Business Owner    → sets strategic goals for Level-4
  - Compliance Officer → approves high-risk Level-3 actions
  - Data Analyst      → reviews Level-2 outputs before action
  - Customer Ops Agent → handles escalations from human_approval node

AI roles:
  - Orchestrator      → routes and classifies (no direct customer action)
  - Level 1–2         → read-only; outputs reviewed before action
  - Level 3           → acts within guardrails; escalates when in doubt
  - Level 4           → coordinates; never acts without sub-agent confirmation
```

**Approval gates**: Any action affecting > 100 customers, any financial action on expired KYC, and any campaign with reach > 1,000 requires explicit human sign-off before execution.

---

## Governance Principles

- **Auditability**: Every action is logged with actor, timestamp, inputs, and outputs. Retention: 7 years.
- **Human-in-the-loop**: High-risk actions pause and wait for approval. Default on timeout: reject.
- **Privacy**: PII masked in all outputs and logs. Consent flags respected unconditionally.
- **Cost awareness**: Token usage tracked per request. Expensive queries (> 10,000 rows) require user confirmation.
- **Graceful degradation**: If any agent is unavailable, the system returns a clear error and suggests alternatives rather than silently failing.
