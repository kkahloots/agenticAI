# 🛠️ Workflows, Decisions, Handoffs & Monitoring

**TL;DR**: This page explains how requests flow through the system, where humans are involved, and how to know if something is going wrong.

---

## How a Request Flows

### Example 1 — "What is the KYC status of customer CUST-007?"

```
You → Orchestrator → Level 1 (Knowledge)
                         ↓
                   Looks up KYC record
                         ↓
                   Returns: "Expired since 2024-03-15"
                         ↓
                   Orchestrator → You
```
No human approval needed. Read-only. Result returned in seconds.

---

### Example 2 — "Send a payment reminder to all at-risk customers"

```
You → Orchestrator → Level 3 (Functional)
                         ↓
                   Checks consent flags for each customer
                         ↓
                   Finds 150 eligible customers
                         ↓
                   ⏸ PAUSE — needs human approval (> 100 customers)
                         ↓
                   Compliance Officer approves ✅
                         ↓
                   Sends SMS/email to 150 customers
                         ↓
                   Logs every send to audit trail
                         ↓
                   You receive: "150 reminders sent, 12 blocked (no consent)"
```

---

### Example 3 — "Increase Visa Gold card adoption by 5% this quarter"

```
You → Orchestrator → Level 4 (Strategic)
                         ↓
                   Breaks goal into sub-goals:
                   1. Segment eligible customers (→ Level 2)
                   2. Select best offer per customer (→ Level 3)
                   3. Schedule campaign (→ Level 3)
                         ↓
                   Level 2 runs segmentation query
                         ↓
                   Level 3 drafts personalised emails
                         ↓
                   ⏸ PAUSE — campaign reach > 1,000 → human approval
                         ↓
                   Business Owner approves ✅
                         ↓
                   Campaign scheduled; progress monitored weekly
```

---

## Decision Points (Where Humans Are Involved)

| Situation | What happens | Who decides |
|-----------|-------------|-------------|
| Action affects > 100 customers | System pauses and asks for approval | Compliance Officer |
| Campaign reach > 1,000 | System pauses and asks for approval | Business Owner |
| Customer has expired KYC | Action blocked; remediation case opened | Customer Ops Agent |
| Customer opted out of marketing | Message blocked automatically | No human needed |
| System is unsure what you want | Asks you to clarify | You |
| Risk score > 0.8 | Action paused; flagged to compliance | Compliance Officer |

---

## Handoffs Between Agents

```
Orchestrator → Level 1   : "Just look this up for me"
Orchestrator → Level 2   : "Analyse this data"
Orchestrator → Level 3   : "Do something for a customer"
Orchestrator → Level 4   : "Achieve this business goal"
Level 4      → Level 2   : "Segment these customers first"
Level 4      → Level 3   : "Now execute the campaign"
Any agent    → Human     : "I need your approval to continue"
```

Handoffs are automatic. You only see the final result unless an approval is needed.

---

## Monitoring — What to Watch

### Green (all good)
- Requests completing in < 10 seconds
- Approval requests being responded to within 30 minutes
- Zero blocked messages due to system errors (only consent blocks are expected)

### Amber (investigate)
- Routing confidence consistently below 0.7 (users may be asking unclear questions)
- Query timeouts increasing (database may need optimisation)
- Approval queue growing (approvers may be unavailable)

### Red (act now)
- Audit log not receiving events (compliance risk — escalate to technical team immediately)
- `send_notification` failing repeatedly (customers not being reached)
- Level-3 actions proceeding without audit records

---

## How to Check System Health

- **Approval queue**: Check the human_approval dashboard for pending decisions
- **Audit trail**: All actions visible in the compliance audit log (access: compliance role)
- **Error alerts**: Configured via `OBSERVABILITY_VERBOSE=1` (stdout) or Langfuse UI at `http://localhost:3000` — alerts sent to ops team on repeated failures
- **Campaign progress**: Level-4 reports progress weekly; deviations > 10% from target trigger automatic re-analysis

---

## What to Do If Something Goes Wrong

| Problem | First step |
|---------|-----------|
| Customer received a message they shouldn't have | Check audit trail for `send_notification` record; review consent flags |
| Campaign sent to wrong segment | Check Level-2 segmentation query in audit trail; review with data analyst |
| System not responding | Check error_handler logs; contact technical team |
| Approval request timed out | System defaulted to "rejected" — re-submit the request |
