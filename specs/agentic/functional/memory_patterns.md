# Functional Agent Memory Patterns Specification

## Overview

The memory layer records all execution details for audit, learning, and debugging. Every functional workflow generates memory entries that track plans, tool usage, compliance decisions, and observations.

**Memory Entry Types**:
1. **plan** — Generated plan with goal, intent, subtasks
2. **tool_usage** — Tool execution with args and result
3. **compliance_decision** — Compliance check outcome
4. **sql_generation** — Generated SQL query
5. **observation** — Agent observation/insight

---

## Memory Entry Schema

### Base Entry Structure

```python
@dataclass
class MemoryEntry:
    timestamp: str  # ISO 8601 format
    entry_type: str  # plan, tool_usage, compliance_decision, sql_generation, observation
    data: dict  # Entry-specific data
    request_id: Optional[str]  # Links to request
```

### Entry Lifecycle

```
1. Create entry with timestamp
2. Add to memory manager
3. Index by request_id
4. Retrieve for audit/analysis
```

---

## Plan Entry

### Purpose
Record the plan generated for a request, including goal, intent, and subtasks.

### Schema

```json
{
  "entry_type": "plan",
  "timestamp": "2024-01-15T10:30:00.123456Z",
  "request_id": "req-87f668dc",
  "data": {
    "goal": "Score and rank leads for offer",
    "intent": "lead_scoring",
    "requires_sql": false,
    "subtasks": [
      {
        "tool": "score_leads",
        "agent": "recommendation_agent",
        "description": "Identify top prospects based on engagement and fit"
      }
    ]
  }
}
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `goal` | str | Yes | High-level goal of the request |
| `intent` | str | Yes | Intent classification (lead_scoring, customer_enrichment, etc.) |
| `requires_sql` | bool | Yes | Whether SQL generation is needed |
| `subtasks` | list | Yes | List of subtasks with tool, agent, description |

### Recording Method

```python
memory.record_plan(request_id, {
    "goal": "Score and rank leads for offer",
    "intent": "lead_scoring",
    "requires_sql": False,
    "subtasks": [
        {
            "tool": "score_leads",
            "agent": "recommendation_agent",
            "description": "Identify top prospects based on engagement and fit"
        }
    ]
})
```

### Examples

**UC1: Lead Scoring**
```json
{
  "goal": "Score and rank leads for offer",
  "intent": "lead_scoring",
  "requires_sql": false,
  "subtasks": [
    {
      "tool": "score_leads",
      "agent": "recommendation_agent",
      "description": "Identify top prospects based on engagement and fit"
    }
  ]
}
```

**UC4: Consent-Gated Notification**
```json
{
  "goal": "Send notification with consent verification",
  "intent": "consent_gated_notification",
  "requires_sql": false,
  "subtasks": [
    {
      "tool": "recommend_offer",
      "agent": "recommendation_agent",
      "description": "Determine best offer for customer"
    },
    {
      "tool": "draft_message",
      "agent": "functional_agent",
      "description": "Create notification content"
    },
    {
      "tool": "check_consent",
      "agent": "compliance_agent",
      "description": "Verify consent before sending"
    },
    {
      "tool": "send_notification",
      "agent": "functional_agent",
      "description": "Deliver notification via approved channel"
    }
  ]
}
```

---

## Tool Usage Entry

### Purpose
Record tool execution with arguments and results for audit trail.

### Schema

```json
{
  "entry_type": "tool_usage",
  "timestamp": "2024-01-15T10:30:01.234567Z",
  "request_id": "req-87f668dc",
  "data": {
    "tool_name": "score_leads",
    "args": {
      "offer_code": "PROMO-PREMIUM-MEMBERSHIP",
      "top_n": 10,
      "segment": null
    },
    "result": {
      "prospects": [
        {
          "customer_id": "CUST-034",
          "name": "Customer CUST-034",
          "segment": "vip",
          "lead_score": 0.911,
          "rationale": "high engagement (84%); premium segment (vip)"
        }
      ],
      "total": 10,
      "offer_code": "PROMO-PREMIUM-MEMBERSHIP"
    }
  }
}
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tool_name` | str | Yes | Name of tool executed |
| `args` | dict | Yes | Arguments passed to tool |
| `result` | dict | Yes | Result returned by tool |

### Recording Method

```python
memory.record_tool_usage(request_id, tool_name, args, result)
```

### Examples

**score_leads**
```json
{
  "tool_name": "score_leads",
  "args": {
    "offer_code": "PROMO-PREMIUM-MEMBERSHIP",
    "top_n": 10,
    "segment": null
  },
  "result": {
    "prospects": [...],
    "total": 10
  }
}
```

**enrich_customer**
```json
{
  "tool_name": "enrich_customer",
  "args": {
    "customer_id": "CUST-001"
  },
  "result": {
    "credit_score": 726,
    "company_type": "Sole Trader",
    "location_score": 0.80
  }
}
```

**send_notification**
```json
{
  "tool_name": "send_notification",
  "args": {
    "customer_id": "CUST-001",
    "channel": "email",
    "content": {
      "subject": "Exclusive promotion just for you",
      "body": "Dear Customer CUST-001, We have a special promotion..."
    }
  },
  "result": {
    "status": "SENT",
    "message_id": "MSG-12345",
    "channel": "email"
  }
}
```

---

## Compliance Decision Entry

### Purpose
Record compliance check decisions for audit and regulatory reporting.

### Schema

```json
{
  "entry_type": "compliance_decision",
  "timestamp": "2024-01-15T10:30:02.345678Z",
  "request_id": "req-87f668dc",
  "data": {
    "customer_id": "CUST-001",
    "check_type": "marketing_consent",
    "passed": true,
    "channel": "email"
  }
}
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `customer_id` | str | Conditional | Customer ID (for consent/identity checks) |
| `check_type` | str | Yes | Type of check (marketing_consent, identity_gate, guardrail) |
| `passed` | bool | Yes | Whether check passed |
| `channel` | str | Conditional | Channel (for consent checks) |
| `kyc_status` | str | Conditional | KYC status (for identity checks) |
| `violations` | int | Conditional | Number of violations (for guardrail checks) |

### Recording Method

```python
memory.record_compliance_decision(request_id, decision)
```

### Check Types

#### marketing_consent

```json
{
  "customer_id": "CUST-001",
  "check_type": "marketing_consent",
  "passed": true,
  "channel": "email"
}
```

#### identity_gate

```json
{
  "customer_id": "CUST-099",
  "check_type": "identity_gate",
  "passed": true,
  "kyc_status": "VERIFIED",
  "kyc_expiry": "2027-11-11"
}
```

#### guardrail

```json
{
  "check_type": "guardrail",
  "passed": false,
  "violations": 2,
  "violation_types": ["email", "phone"]
}
```

### Examples

**Consent Check - Passed**
```json
{
  "customer_id": "CUST-001",
  "check_type": "marketing_consent",
  "passed": true,
  "channel": "email"
}
```

**Consent Check - Failed**
```json
{
  "customer_id": "CUST-050",
  "check_type": "marketing_consent",
  "passed": false,
  "channel": "email",
  "reason": "consent_not_given"
}
```

**Identity Check - Passed**
```json
{
  "customer_id": "CUST-099",
  "check_type": "identity_gate",
  "passed": true,
  "kyc_status": "VERIFIED",
  "kyc_expiry": "2027-11-11"
}
```

**Identity Check - Failed**
```json
{
  "customer_id": "CUST-099",
  "check_type": "identity_gate",
  "passed": false,
  "kyc_status": "UNVERIFIED",
  "reason": "kyc_unverified"
}
```

**Guardrail Check - Violations Found**
```json
{
  "check_type": "guardrail",
  "passed": false,
  "violations": 2,
  "violation_types": ["email", "phone"]
}
```

---

## SQL Generation Entry

### Purpose
Record SQL queries generated for audit and query optimization.

### Schema

```json
{
  "entry_type": "sql_generation",
  "timestamp": "2024-01-15T10:30:03.456789Z",
  "request_id": "req-8b1c04cf",
  "data": {
    "query": "SELECT * FROM customers WHERE return_risk > 0.70",
    "intent": "identify_high_return_risk"
  }
}
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | str | Yes | Generated SQL query |
| `intent` | str | Yes | Intent of the query |

### Recording Method

```python
memory.record_sql_generation(request_id, query, intent)
```

### Examples

**UC7: Return Risk Intervention**
```json
{
  "query": "SELECT * FROM customers WHERE return_risk > 0.70",
  "intent": "identify_high_return_risk"
}
```

**UC8: Campaign Dashboard**
```json
{
  "query": "SELECT * FROM campaign_results",
  "intent": "campaign_dashboard"
}
```

---

## Observation Entry

### Purpose
Record agent observations and insights for pattern learning.

### Schema

```json
{
  "entry_type": "observation",
  "timestamp": "2024-01-15T10:30:04.567890Z",
  "request_id": "req-87f668dc",
  "data": {
    "observation": "Identified 10 prospects with avg score 0.85"
  }
}
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `observation` | str | Yes | Observation text |

### Recording Method

```python
memory.record_observation(request_id, observation)
```

### Examples

**UC1: Lead Scoring**
```json
{
  "observation": "Identified 10 prospects with avg score 0.85"
}
```

**UC2: Enrichment**
```json
{
  "observation": "Enriched CUST-001 with credit score, company type, location score"
}
```

**UC4: Notification**
```json
{
  "observation": "Sent notification to CUST-001 via email"
}
```

**UC7: Return Risk**
```json
{
  "observation": "Return risk intervention: 8 contacted, 3 blocked"
}
```

---

## Memory Recording Patterns

### Pattern 1: Simple Tool Execution

```python
# UC1: Lead Scoring
memory.record_plan(request_id, plan)
memory.record_tool_usage(request_id, "score_leads", args, result)
memory.record_observation(request_id, f"Identified {n} prospects with avg score {score}")
```

### Pattern 2: Tool + Compliance Gate

```python
# UC3: NBA Recommendation
memory.record_plan(request_id, plan)
memory.record_tool_usage(request_id, "recommend_offer", args, result)
memory.record_tool_usage(request_id, "check_marketing_consent", args, result)
memory.record_compliance_decision(request_id, decision)
memory.record_observation(request_id, f"Recommended {offer_name}")
```

### Pattern 3: Multi-Step Workflow

```python
# UC4: Consent-Gated Notification
memory.record_plan(request_id, plan)
memory.record_tool_usage(request_id, "recommend_offer", args, result)
memory.record_tool_usage(request_id, "draft_email", args, result)
memory.record_tool_usage(request_id, "check_marketing_consent", args, result)
memory.record_compliance_decision(request_id, decision)
memory.record_tool_usage(request_id, "send_notification", args, result)
memory.record_observation(request_id, f"Sent notification to {customer_id}")
```

### Pattern 4: SQL + Compliance Gates

```python
# UC7: Return Risk Intervention
memory.record_plan(request_id, plan)
memory.record_sql_generation(request_id, query, intent)
memory.record_tool_usage(request_id, "run_sql_query", args, result)

for customer in at_risk_customers:
    memory.record_compliance_decision(request_id, identity_decision)
    memory.record_compliance_decision(request_id, consent_decision)
    memory.record_tool_usage(request_id, "send_notification", args, result)

memory.record_observation(request_id, f"Return risk intervention: {sent} contacted, {blocked} blocked")
```

---

## Memory Retrieval

### Get Request History

```python
entries = memory.get_request_history(request_id)
# Returns all entries for request in chronological order
```

### Get Recent Entries

```python
entries = memory.get_recent_entries(n=10)
# Returns n most recent entries across all requests
```

### Filter by Entry Type

```python
plans = [e for e in entries if e.entry_type == "plan"]
tools = [e for e in entries if e.entry_type == "tool_usage"]
decisions = [e for e in entries if e.entry_type == "compliance_decision"]
```

---

## Memory Analytics

### Compliance Audit

```python
# Get all compliance decisions for customer
decisions = [e for e in entries 
             if e.entry_type == "compliance_decision" 
             and e.data.get("customer_id") == customer_id]

# Analyze pass/fail rate
passed = sum(1 for d in decisions if d.data.get("passed"))
failed = len(decisions) - passed
pass_rate = passed / len(decisions) if decisions else 0
```

### Tool Usage Analysis

```python
# Get all tool executions
tools = [e for e in entries if e.entry_type == "tool_usage"]

# Count by tool
tool_counts = {}
for t in tools:
    tool_name = t.data.get("tool_name")
    tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1

# Most used tools
sorted_tools = sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)
```

### Pattern Learning

```python
# Get observations
observations = [e for e in entries if e.entry_type == "observation"]

# Extract insights
for obs in observations:
    text = obs.data.get("observation")
    # Parse and learn patterns
```

---

## Memory Lifecycle

### Creation
- Entry created when event occurs
- Timestamp recorded
- Request ID linked

### Storage
- Entry added to memory manager
- Indexed by request_id
- Stored in chronological order

### Retrieval
- Query by request_id
- Filter by entry_type
- Analyze patterns

### Retention
- Entries retained for audit trail
- Configurable retention period
- Archived for compliance

### Cleanup
- Clear memory when needed
- Batch delete old entries
- Archive to external storage
