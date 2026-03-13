# Functional Agent Specification

## Overview

The **Functional Agent** (Level 3) coordinates functional workflows including customer enrichment, notifications, case creation, and campaign planning. It routes requests to specialized agents (recommendation, compliance, functional) and records all execution details to memory for audit and learning.

**Key Characteristics**:
- **Routing**: Action-based routing to specialized agents
- **Compliance**: Inline consent, identity, and guardrail gates
- **Memory**: Records plans, tool usage, compliance decisions, observations
- **No Evaluation**: Results are final (unlike workflow agent)
- **Delegation**: All MCP tools delegate to `nonagentic.tools.*`

---

## Architecture

### Agent Hierarchy

```
Functional Agent (Orchestrator)
├── Recommendation Agent (Lead scoring, NBA, bulk recommendations)
├── Functional Agent (Enrichment, notifications, case creation, campaign planning)
├── Compliance Agent (Consent, identity, guardrails)
└── Analytics Agent (Campaign analysis, return risk identification)
```

### Routing Logic

```python
FunctionalAgent.execute(task, request_id):
  action = task.get("action")
  
  if "enrich" in action:
    return _enrich_customer(task, request_id)
  elif "notif" or "send" in action:
    return _send_notification(task, request_id)
  elif "draft" in action:
    return _draft_message(task, request_id)
  elif "case" in action:
    return _create_case(task, request_id)
  elif "campaign" and "plan" in action:
    return _build_campaign_plan(task, request_id)
  else:
    return {"error": "unknown_action"}
```

### Execution Flow

```
1. Parse Request
   ├─ Extract action, parameters
   └─ Validate required fields

2. Route to Handler
   ├─ Determine agent (recommendation, functional, compliance)
   └─ Select tool

3. Execute Tool
   ├─ Call MCP server function
   ├─ Handle errors
   └─ Return result

4. Record to Memory
   ├─ Record tool_usage
   ├─ Record compliance_decision (if applicable)
   └─ Record observation

5. Return Result
   └─ Return tool result to caller
```

---

## Use Case Decision Trees

### UC1: Lead Scoring

**Intent**: `lead_scoring`
**Requires SQL**: No
**Agents**: `recommendation_agent`

```
Request: "Score leads for PROMO-PREMIUM-MEMBERSHIP"
  ├─ Parse: offer_code="PROMO-PREMIUM-MEMBERSHIP", top_n=10
  ├─ Route: recommendation_agent
  ├─ Action: "score_leads"
  ├─ Tool: score_leads(offer_code, top_n=10)
  ├─ Memory: record_plan, record_tool_usage, record_observation
  └─ Return: {prospects: [{customer_id, name, segment, lead_score, rationale}]}
```

**Decision Tree**:
```
score_leads(offer_code, top_n, segment=None)
  ├─ If segment provided:
  │  └─ Filter prospects by segment
  ├─ Score prospects by engagement + fit
  ├─ Sort by score descending
  ├─ Return top_n prospects
  └─ Record observation: "Identified {n} prospects with avg score {score}"
```

### UC2: Customer Enrichment

**Intent**: `customer_enrichment`
**Requires SQL**: No
**Agents**: `functional_agent`

```
Request: "Enrich customer profile for CUST-001"
  ├─ Parse: customer_id="CUST-001"
  ├─ Route: functional_agent
  ├─ Action: "enrich"
  ├─ Tool: enrich_customer(customer_id)
  ├─ Memory: record_plan, record_tool_usage, record_observation
  └─ Return: {credit_score, company_type, location_score, ...}
```

**Decision Tree**:
```
enrich_customer(customer_id)
  ├─ Lookup base profile
  ├─ Fetch credit bureau data
  ├─ Fetch business registry data
  ├─ Fetch location enrichment
  ├─ Merge all sources
  └─ Record observation: "Enriched {customer_id} with {n} data sources"
```

### UC3: NBA Recommendation

**Intent**: `nba_recommendation`
**Requires SQL**: No
**Agents**: `recommendation_agent` → `compliance_agent`

```
Request: "Recommend next best action for CUST-001"
  ├─ Parse: customer_id="CUST-001"
  ├─ Route: recommendation_agent
  ├─ Action: "recommend"
  ├─ Tool: recommend_offer(customer_id)
  ├─ Memory: record_plan, record_tool_usage
  ├─ Check Consent: compliance_agent
  │  ├─ Action: "consent"
  │  ├─ Tool: check_marketing_consent(customer_id)
  │  ├─ Memory: record_compliance_decision, record_tool_usage
  │  └─ If not passed: return {error: "consent_required"}
  └─ Return: {offer_id, offer_name, confidence, rationale}
```

**Decision Tree**:
```
recommend_offer(customer_id, context="")
  ├─ Lookup customer profile
  ├─ Score available offers
  ├─ Rank by fit + engagement
  ├─ Return top offer
  └─ Record observation: "Recommended {offer_name} with confidence {score}"

check_marketing_consent(customer_id)
  ├─ Lookup consent flags
  ├─ Check marketing_consent flag
  ├─ If false: return {passed: false}
  └─ If true: return {passed: true}
```

### UC4: Consent-Gated Notification

**Intent**: `consent_gated_notification`
**Requires SQL**: No
**Agents**: `recommendation_agent` → `functional_agent` → `compliance_agent` → `functional_agent`

```
Request: "Send notification to CUST-001 with offer"
  ├─ Step 1: Recommend Offer
  │  ├─ Route: recommendation_agent
  │  ├─ Tool: recommend_offer(customer_id)
  │  └─ Memory: record_tool_usage
  ├─ Step 2: Draft Message
  │  ├─ Route: functional_agent
  │  ├─ Tool: draft_email(customer_id, template_id, variables)
  │  └─ Memory: record_tool_usage
  ├─ Step 3: Check Consent
  │  ├─ Route: compliance_agent
  │  ├─ Tool: check_marketing_consent(customer_id)
  │  ├─ Memory: record_compliance_decision
  │  └─ If not passed: return {status: "BLOCKED", reason: "consent_email"}
  ├─ Step 4: Send Notification
  │  ├─ Route: functional_agent
  │  ├─ Tool: send_notification(customer_id, channel, content)
  │  ├─ Memory: record_tool_usage
  │  └─ Return: {status: "SENT", message_id}
  └─ Record observation: "Sent notification to {customer_id} via {channel}"
```

**Decision Tree**:
```
draft_email(customer_id, template_id, variables)
  ├─ Load template
  ├─ Substitute variables
  ├─ Return {subject, body, preview}
  └─ Record observation: "Drafted email for {customer_id}"

send_notification(customer_id, channel, content, dry_run=False)
  ├─ If dry_run: simulate send
  ├─ Else: send via channel (email, sms, push)
  ├─ Record delivery
  └─ Return {status: "SENT", message_id}
```

### UC5: Identity Gate

**Intent**: `identity_gate`
**Requires SQL**: No
**Agents**: `compliance_agent` → `functional_agent`

```
Request: "Verify identity for CUST-099"
  ├─ Step 1: Check Identity
  │  ├─ Route: compliance_agent
  │  ├─ Tool: check_identity_gate(customer_id)
  │  ├─ Memory: record_compliance_decision
  │  └─ If not passed: proceed to Step 2
  ├─ Step 2: Create Remediation Case
  │  ├─ Route: functional_agent
  │  ├─ Tool: create_case(customer_id, "identity_reverification", description, priority="high")
  │  ├─ Memory: record_tool_usage
  │  └─ Return: {case_id, status: "CREATED"}
  └─ Record observation: "Identity gate check completed for {customer_id}"
```

**Decision Tree**:
```
check_identity_gate(customer_id)
  ├─ Lookup KYC status
  ├─ Check if verified
  ├─ Check if not expired
  ├─ If verified and not expired: return {passed: true}
  └─ Else: return {passed: false, reason: "unverified|expired"}

create_case(customer_id, case_type, description, priority)
  ├─ Generate case_id
  ├─ Store case record
  ├─ Assign to queue
  └─ Return {case_id, status: "CREATED"}
```

### UC6: Bulk Campaign Targeting

**Intent**: `bulk_campaign_targeting`
**Requires SQL**: No (deterministic) / Yes (dynamic)
**Agents**: `recommendation_agent` → `functional_agent`

```
Request: "Plan bulk campaign PROMO-WINBACK for dormant_vip segment"
  ├─ Step 1: Bulk Recommend
  │  ├─ Route: recommendation_agent
  │  ├─ Tool: bulk_recommend(offer_code, segment, top_n=50)
  │  ├─ Memory: record_tool_usage
  │  └─ Return: {prospects: [...], total: 14, to_send: 12, blocked: 2}
  ├─ Step 2: Build Campaign Plan
  │  ├─ Route: functional_agent
  │  ├─ Tool: build_campaign_execution_plan(plan_data)
  │  ├─ Memory: record_tool_usage
  │  └─ Return: {plan: {...}, status: "ready", requires_approval: false}
  └─ Record observation: "Campaign plan created: {total} prospects, {to_send} to send"
```

**Decision Tree**:
```
bulk_recommend(offer_code, segment, top_n)
  ├─ Query customers in segment
  ├─ Score each customer
  ├─ Filter by consent
  ├─ Filter by identity
  ├─ Sort by score
  ├─ Return top_n
  └─ Record observation: "Bulk recommendation: {total} prospects, {to_send} eligible"

build_campaign_execution_plan(plan_data)
  ├─ Organize by channel (email, sms, push)
  ├─ Set execution order
  ├─ Calculate timing
  └─ Return {plan: {...}, status: "ready"}
```

### UC7: Return Risk Intervention

**Intent**: `return_risk_intervention`
**Requires SQL**: Yes
**Agents**: `analytics_agent` → `compliance_agent` (2x) → `functional_agent`

```
Request: "Identify and intervene on high-return-risk customers (threshold > 0.70)"
  ├─ Step 1: Identify At-Risk
  │  ├─ Route: analytics_agent
  │  ├─ Tool: run_sql_query("SELECT * FROM customers WHERE return_risk > 0.70")
  │  ├─ Memory: record_sql_generation, record_tool_usage
  │  └─ Return: {customers: [...], count: 11}
  ├─ Step 2: Filter by Identity
  │  ├─ Route: compliance_agent
  │  ├─ Tool: check_identity_gate(customer_id) for each
  │  ├─ Memory: record_compliance_decision (per customer)
  │  └─ Filter: keep only verified
  ├─ Step 3: Filter by Consent
  │  ├─ Route: compliance_agent
  │  ├─ Tool: check_marketing_consent(customer_id) for each
  │  ├─ Memory: record_compliance_decision (per customer)
  │  └─ Filter: keep only consented
  ├─ Step 4: Send Intervention
  │  ├─ Route: functional_agent
  │  ├─ Tool: send_notification(customer_id, channel, content) for each
  │  ├─ Memory: record_tool_usage (per customer)
  │  └─ Return: {sent: 8, blocked: 3}
  └─ Record observation: "Return risk intervention: {sent} contacted, {blocked} blocked"
```

**Decision Tree**:
```
identify_high_return_risk(threshold)
  ├─ Query: SELECT * FROM customers WHERE return_risk > threshold
  ├─ Return: list of at-risk customers
  └─ Record observation: "Identified {n} high-return-risk customers"

filter_by_identity(customers)
  ├─ For each customer:
  │  ├─ Check identity gate
  │  └─ Keep if verified
  └─ Return: filtered list

filter_by_consent(customers)
  ├─ For each customer:
  │  ├─ Check marketing consent
  │  └─ Keep if consented
  └─ Return: filtered list

send_intervention(customers)
  ├─ For each customer:
  │  ├─ Draft intervention message
  │  ├─ Send notification
  │  └─ Record delivery
  └─ Return: {sent: n, blocked: m}
```

### UC8: Campaign Results Dashboard

**Intent**: `campaign_dashboard`
**Requires SQL**: Yes
**Agents**: `analytics_agent`

```
Request: "Analyze campaign performance"
  ├─ Step 1: Query Campaign Results
  │  ├─ Route: analytics_agent
  │  ├─ Tool: run_sql_query("SELECT * FROM campaign_results")
  │  ├─ Memory: record_sql_generation, record_tool_usage
  │  └─ Return: {results: [...], total_sent: 103}
  ├─ Step 2: Analyze Results
  │  ├─ Route: analytics_agent
  │  ├─ Tool: analyze_campaign_results(results)
  │  ├─ Memory: record_observation
  │  └─ Return: {metrics: {...}, insights: [...]}
  └─ Record observation: "Campaign analysis: {total_sent} sent, {converted} converted, {rate}% conversion"
```

**Decision Tree**:
```
query_campaign_results()
  ├─ Query: SELECT * FROM campaign_results
  ├─ Return: {results: [...], total_sent: n}
  └─ Record observation: "Queried campaign results: {n} records"

analyze_campaign_results(results)
  ├─ Calculate metrics:
  │  ├─ Total sent
  │  ├─ Opened
  │  ├─ Clicked
  │  ├─ Converted
  │  ├─ Unsubscribed
  │  └─ Conversion rate
  ├─ Generate insights
  └─ Return: {metrics: {...}, insights: [...]}
```

### UC9: Guardrails

**Intent**: `guardrails`
**Requires SQL**: No
**Agents**: `compliance_agent`

```
Request: "Check and redact PII from text"
  ├─ Step 1: Guardrail Check
  │  ├─ Route: compliance_agent
  │  ├─ Tool: guardrail_check(text, request_id)
  │  ├─ Memory: record_compliance_decision
  │  └─ Return: {passed: false, violations: [{type: "email", value: "john.doe@example.com"}]}
  ├─ Step 2: Redact PII
  │  ├─ Route: compliance_agent
  │  ├─ Tool: redact_pii(text)
  │  ├─ Memory: record_tool_usage
  │  └─ Return: {redacted_text: "Customer email is [email redacted]..."}
  └─ Record observation: "Guardrails check: {n} violations found and redacted"
```

**Decision Tree**:
```
guardrail_check(text, request_id)
  ├─ Scan for PII patterns:
  │  ├─ Email addresses
  │  ├─ Phone numbers
  │  ├─ Credit card numbers
  │  ├─ SSN
  │  └─ Other sensitive data
  ├─ Scan for policy violations
  ├─ If violations found: return {passed: false, violations: [...]}
  └─ Else: return {passed: true, violations: []}

redact_pii(text)
  ├─ Replace email with [email redacted]
  ├─ Replace phone with [phone redacted]
  ├─ Replace credit card with [card redacted]
  ├─ Replace SSN with [ssn redacted]
  └─ Return: {redacted_text: "..."}
```

---

## Tool Selection Patterns

### Deterministic Mode
- Fixed tool paths per use case
- No dynamic tool discovery
- Predictable execution

### Dynamic Mode (UC6-UC8)
- Dynamic tool discovery from registry
- SQL generation for complex queries
- Planner selects tools based on intent

### Tool Selection Algorithm
```
1. Parse intent from request
2. Query registry for matching tools
3. Score tools by relevance
4. Select top tool
5. Execute tool
6. Record to memory
```

---

## Memory Recording Schema

### Entry Types

#### 1. Plan Entry
```json
{
  "entry_type": "plan",
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

#### 2. Tool Usage Entry
```json
{
  "entry_type": "tool_usage",
  "data": {
    "tool_name": "score_leads",
    "args": {
      "offer_code": "PROMO-PREMIUM-MEMBERSHIP",
      "top_n": 10
    },
    "result": {
      "prospects": [...],
      "total": 10
    }
  }
}
```

#### 3. Compliance Decision Entry
```json
{
  "entry_type": "compliance_decision",
  "data": {
    "customer_id": "CUST-001",
    "check_type": "marketing_consent",
    "passed": true
  }
}
```

#### 4. SQL Generation Entry
```json
{
  "entry_type": "sql_generation",
  "data": {
    "query": "SELECT * FROM customers WHERE return_risk > 0.70",
    "intent": "identify_high_return_risk"
  }
}
```

#### 5. Observation Entry
```json
{
  "entry_type": "observation",
  "data": {
    "observation": "Identified 10 prospects with avg score 0.85"
  }
}
```

### Recording Methods

```python
# Record plan
memory.record_plan(request_id, plan)

# Record tool execution
memory.record_tool_usage(request_id, tool_name, args, result)

# Record compliance decision
memory.record_compliance_decision(request_id, decision)

# Record SQL generation
memory.record_sql_generation(request_id, query, intent)

# Record observation
memory.record_observation(request_id, observation)
```

---

## Error Handling

### Missing Required Fields
```python
if not customer_id:
    return {"error": "missing_customer_id"}
```

### Unknown Actions
```python
return {"error": "unknown_action", "action": action}
```

### Tool Execution Errors
```python
result = tool_function(...)
if result.get("error"):
    return result  # Propagate error
```

### Compliance Gate Failures
```python
if not compliance_result.get("passed"):
    return {
        "status": "BLOCKED",
        "reason": compliance_result.get("reason")
    }
```

---

## Compliance Gates

### Consent Gate
- **Check**: `check_marketing_consent(customer_id)`
- **Decision**: `passed = result.get("marketing_consent", False)`
- **Blocks**: Notification sending
- **Fallback**: Return blocked status

### Identity Gate
- **Check**: `check_identity_gate(customer_id)`
- **Decision**: `passed = result.get("gate_passed", False)`
- **Action**: Create remediation case if not passed
- **Fallback**: Return unverified status

### Guardrails Gate
- **Check**: `guardrail_check(text, request_id)`
- **Decision**: `passed = result.get("passed", True)`
- **Action**: Redact PII if violations found
- **Fallback**: Return violations list

---

## State Updates

### After Tool Execution
```python
# Update request state
state["tool_results"].append({
    "tool": tool_name,
    "result": result,
    "timestamp": datetime.utcnow().isoformat()
})

# Update memory
memory.record_tool_usage(request_id, tool_name, args, result)

# Update compliance decisions
if compliance_check:
    memory.record_compliance_decision(request_id, decision)
```

---

## No Evaluation Trigger

**Important**: Functional Agent does NOT trigger evaluation agent.

- Results are final
- No replanning
- Compliance gates are inline
- Audit trail recorded for compliance review

---

## Audit Trail

All execution details recorded to memory:
- Plans generated
- Tools executed
- Compliance decisions made
- SQL queries generated
- Observations recorded

Enables:
- Compliance audit
- Pattern learning
- Performance analysis
- Debugging
