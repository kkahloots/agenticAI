# Functional Agent Use Cases Specification

## UC1: Lead Scoring

**Intent**: `lead_scoring`
**Agents**: `recommendation_agent`
**Tools**: `score_leads(offer_code, top_n, segment)`
**Memory**: plan, tool_usage, observation

### Exact Code Path
```python
# Request parsing
offer_code = "PROMO-PREMIUM-MEMBERSHIP"
top_n = 10
segment = None

# Routing
agent = recommendation_agent
action = "score_leads"

# Tool execution
result = recommendation_server.score_leads(offer_code, top_n=top_n, segment=segment)

# Memory recording
memory.record_plan(request_id, {
    "goal": "Score and rank leads for offer",
    "intent": "lead_scoring",
    "requires_sql": False,
    "subtasks": [{"tool": "score_leads", "agent": "recommendation_agent"}]
})
memory.record_tool_usage(request_id, "score_leads", 
    {"offer_code": offer_code, "top_n": top_n}, result)
memory.record_observation(request_id, 
    f"Identified {len(result['prospects'])} prospects with avg score {avg_score}")

# Return
return result  # {prospects: [...], total: 10}
```

### MCP Tool Call
```
score_leads(
  offer_code: "PROMO-PREMIUM-MEMBERSHIP",
  top_n: 10,
  segment: None
) → {
  prospects: [
    {customer_id, name, segment, lead_score, rationale},
    ...
  ],
  total: 10
}
```

### Memory Recording
- **plan**: Goal, intent, subtasks
- **tool_usage**: score_leads call with args and result
- **observation**: "Identified 10 prospects with avg score 0.85"

### Expected Output
```json
{
  "prospects": [
    {
      "customer_id": "CUST-034",
      "name": "Customer CUST-034",
      "segment": "vip",
      "lead_score": 0.911,
      "rationale": "high engagement (84%); premium segment (vip)"
    },
    ...
  ],
  "total": 10
}
```

---

## UC2: Customer Enrichment

**Intent**: `customer_enrichment`
**Agents**: `functional_agent`
**Tools**: `enrich_customer(customer_id)`
**Memory**: plan, tool_usage, observation

### Exact Code Path
```python
# Request parsing
customer_id = "CUST-001"

# Routing
agent = functional_agent
action = "enrich"

# Tool execution
result = functional_server.enrich_customer(customer_id)

# Memory recording
memory.record_plan(request_id, {
    "goal": "Enrich customer profile with multi-source data",
    "intent": "customer_enrichment",
    "requires_sql": False,
    "subtasks": [
        {"tool": "lookup_customer", "agent": "functional_agent"},
        {"tool": "enrich_customer", "agent": "functional_agent"}
    ]
})
memory.record_tool_usage(request_id, "enrich_customer", 
    {"customer_id": customer_id}, result)
memory.record_observation(request_id, 
    f"Enriched {customer_id} with credit score, company type, location score")

# Return
return result  # {credit_score, company_type, location_score, ...}
```

### MCP Tool Call
```
enrich_customer(
  customer_id: "CUST-001"
) → {
  credit_score: 726,
  company_type: "Sole Trader",
  location_score: 0.80,
  ...
}
```

### Memory Recording
- **plan**: Goal, intent, subtasks
- **tool_usage**: enrich_customer call with args and result
- **observation**: "Enriched CUST-001 with 3 data sources"

### Expected Output
```json
{
  "credit_score": 726,
  "company_type": "Sole Trader",
  "location_score": 0.80,
  "enrichment_sources": 3
}
```

---

## UC3: NBA Recommendation

**Intent**: `nba_recommendation`
**Agents**: `recommendation_agent` → `compliance_agent`
**Tools**: `recommend_offer(customer_id)` → `check_marketing_consent(customer_id)`
**Memory**: plan, tool_usage (2x), compliance_decision, observation

### Exact Code Path
```python
# Request parsing
customer_id = "CUST-001"

# Routing
agent = recommendation_agent
action = "recommend"

# Step 1: Recommend offer
result = recommendation_server.recommend_offer(customer_id)
memory.record_tool_usage(request_id, "recommend_offer", 
    {"customer_id": customer_id}, result)

# Step 2: Check consent
compliance_agent = create_compliance_agent()
consent_result = compliance_agent.execute({
    "action": "consent",
    "customer_id": customer_id
}, request_id)

# Memory recording
memory.record_plan(request_id, {
    "goal": "Recommend next-best-action for customer",
    "intent": "nba_recommendation",
    "requires_sql": False,
    "subtasks": [
        {"tool": "lookup_customer", "agent": "recommendation_agent"},
        {"tool": "recommend_offer", "agent": "recommendation_agent"},
        {"tool": "check_consent", "agent": "compliance_agent"}
    ]
})
memory.record_observation(request_id, 
    f"Recommended {result['offer_name']} with confidence {result['confidence']}")

# Return
return result  # {offer_id, offer_name, confidence, rationale}
```

### MCP Tool Calls
```
Step 1: recommend_offer(customer_id: "CUST-001")
  → {offer_id, offer_name, confidence, rationale}

Step 2: check_marketing_consent(customer_id: "CUST-001")
  → {marketing_consent: true/false}
```

### Memory Recording
- **plan**: Goal, intent, subtasks
- **tool_usage**: recommend_offer call
- **tool_usage**: check_marketing_consent call
- **compliance_decision**: {customer_id, check_type: "marketing_consent", passed: true/false}
- **observation**: "Recommended Win-Back Offer with confidence 0.879"

### Expected Output
```json
{
  "offer_id": "OFFER-001",
  "offer_name": "Win-Back Offer",
  "confidence": 0.879,
  "rationale": "High engagement history, dormant for 3 months"
}
```

---

## UC4: Consent-Gated Notification

**Intent**: `consent_gated_notification`
**Agents**: `recommendation_agent` → `functional_agent` → `compliance_agent` → `functional_agent`
**Tools**: `recommend_offer()` → `draft_email()` → `check_marketing_consent()` → `send_notification()`
**Memory**: plan, tool_usage (4x), compliance_decision, observation

### Exact Code Path
```python
# Request parsing
customer_id = "CUST-001"

# Step 1: Recommend offer
offer_result = recommendation_server.recommend_offer(customer_id)
memory.record_tool_usage(request_id, "recommend_offer", {...}, offer_result)

# Step 2: Draft message
draft_result = notification_server.draft_email(customer_id, "T-PROMO-01", 
    variables={"offer_name": offer_result["offer_name"]})
memory.record_tool_usage(request_id, "draft_email", {...}, draft_result)

# Step 3: Check consent
consent_result = compliance_server.check_marketing_consent(customer_id)
decision = {
    "customer_id": customer_id,
    "check_type": "marketing_consent",
    "passed": consent_result.get("result", {}).get("marketing_consent", False)
}
memory.record_compliance_decision(request_id, decision)
memory.record_tool_usage(request_id, "check_marketing_consent", {...}, consent_result)

if not decision["passed"]:
    return {"status": "BLOCKED", "reason": "consent_email"}

# Step 4: Send notification
send_result = notification_server.send_notification(customer_id, "email", 
    {"subject": draft_result["subject"], "body": draft_result["body"]})
memory.record_tool_usage(request_id, "send_notification", {...}, send_result)

# Memory recording
memory.record_plan(request_id, {
    "goal": "Send notification with consent verification",
    "intent": "consent_gated_notification",
    "requires_sql": False,
    "subtasks": [
        {"tool": "recommend_offer", "agent": "recommendation_agent"},
        {"tool": "draft_message", "agent": "functional_agent"},
        {"tool": "check_consent", "agent": "compliance_agent"},
        {"tool": "send_notification", "agent": "functional_agent"}
    ]
})
memory.record_observation(request_id, 
    f"Sent notification to {customer_id} via email")

# Return
return send_result  # {status: "SENT", message_id}
```

### MCP Tool Calls
```
Step 1: recommend_offer(customer_id: "CUST-001")
  → {offer_id, offer_name, confidence}

Step 2: draft_email(customer_id: "CUST-001", template_id: "T-PROMO-01", variables: {...})
  → {subject, body, preview}

Step 3: check_marketing_consent(customer_id: "CUST-001")
  → {marketing_consent: true/false}

Step 4: send_notification(customer_id: "CUST-001", channel: "email", content: {...})
  → {status: "SENT", message_id}
```

### Memory Recording
- **plan**: Goal, intent, 4 subtasks
- **tool_usage**: recommend_offer, draft_email, check_marketing_consent, send_notification
- **compliance_decision**: {customer_id, check_type: "marketing_consent", passed: true}
- **observation**: "Sent notification to CUST-001 via email"

### Expected Output
```json
{
  "status": "SENT",
  "message_id": "MSG-12345",
  "channel": "email",
  "customer_id": "CUST-001"
}
```

---

## UC5: Identity Gate

**Intent**: `identity_gate`
**Agents**: `compliance_agent` → `functional_agent`
**Tools**: `check_identity_gate(customer_id)` → `create_case(customer_id, case_type, description, priority)`
**Memory**: plan, compliance_decision, tool_usage (2x), observation

### Exact Code Path
```python
# Request parsing
customer_id = "CUST-099"

# Step 1: Check identity
identity_result = compliance_server.check_identity_gate(customer_id)
decision = {
    "customer_id": customer_id,
    "check_type": "identity_gate",
    "passed": identity_result.get("result", {}).get("gate_passed", False)
}
memory.record_compliance_decision(request_id, decision)
memory.record_tool_usage(request_id, "check_identity_gate", {...}, identity_result)

# Step 2: Create case if needed
if not decision["passed"]:
    case_result = functional_server.create_case(customer_id, "identity_reverification", 
        "Identity unverified", priority="high")
    memory.record_tool_usage(request_id, "create_case", {...}, case_result)
else:
    case_result = None

# Memory recording
memory.record_plan(request_id, {
    "goal": "Verify identity status and create remediation case if needed",
    "intent": "identity_gate",
    "requires_sql": False,
    "subtasks": [
        {"tool": "check_identity", "agent": "compliance_agent"},
        {"tool": "create_case", "agent": "functional_agent"}
    ]
})
memory.record_observation(request_id, 
    f"Identity gate check completed for {customer_id}: {'VERIFIED' if decision['passed'] else 'UNVERIFIED'}")

# Return
return {
    "customer_id": customer_id,
    "kyc_status": identity_result.get("result", {}).get("kyc_status"),
    "gate_passed": decision["passed"],
    "case_created": case_result is not None
}
```

### MCP Tool Calls
```
Step 1: check_identity_gate(customer_id: "CUST-099")
  → {gate_passed: true/false, kyc_status: "VERIFIED"|"UNVERIFIED"|"EXPIRED"}

Step 2: create_case(customer_id: "CUST-099", case_type: "identity_reverification", 
                    description: "Identity unverified", priority: "high")
  → {case_id, status: "CREATED"}
```

### Memory Recording
- **plan**: Goal, intent, 2 subtasks
- **compliance_decision**: {customer_id, check_type: "identity_gate", passed: true/false}
- **tool_usage**: check_identity_gate, create_case (if needed)
- **observation**: "Identity gate check completed for CUST-099: VERIFIED"

### Expected Output
```json
{
  "customer_id": "CUST-099",
  "kyc_status": "VERIFIED",
  "gate_passed": true,
  "case_created": false
}
```

---

## UC6: Bulk Campaign Targeting

**Intent**: `bulk_campaign_targeting`
**Agents**: `recommendation_agent` → `functional_agent`
**Tools**: `bulk_recommend(offer_code, segment, top_n)` → `build_campaign_execution_plan(plan_data)`
**Memory**: plan, tool_usage (2x), observation

### Exact Code Path
```python
# Request parsing
offer_code = "PROMO-WINBACK"
segment = "dormant_vip"
top_n = 50

# Step 1: Bulk recommend
bulk_result = recommendation_server.bulk_recommend(offer_code, segment=segment, top_n=top_n)
memory.record_tool_usage(request_id, "bulk_recommend", 
    {"offer_code": offer_code, "segment": segment, "top_n": top_n}, bulk_result)

# Step 2: Build campaign plan
plan_result = functional_server.build_campaign_execution_plan(bulk_result)
memory.record_tool_usage(request_id, "build_campaign_execution_plan", 
    {"plan_data": bulk_result}, plan_result)

# Memory recording
memory.record_plan(request_id, {
    "goal": "Recommend next-best-action for customer",
    "intent": "nba_recommendation",
    "requires_sql": False,
    "subtasks": [
        {"tool": "lookup_customer", "agent": "recommendation_agent"},
        {"tool": "recommend_offer", "agent": "recommendation_agent"},
        {"tool": "check_consent", "agent": "compliance_agent"}
    ]
})
memory.record_observation(request_id, 
    f"Campaign plan created: {bulk_result['total']} prospects, {bulk_result['to_send']} to send")

# Return
return plan_result  # {plan: {...}, status: "ready", requires_approval: false}
```

### MCP Tool Calls
```
Step 1: bulk_recommend(offer_code: "PROMO-WINBACK", segment: "dormant_vip", top_n: 50)
  → {prospects: [...], total: 14, to_send: 12, blocked: 2}

Step 2: build_campaign_execution_plan(plan_data: {...})
  → {plan: {...}, status: "ready", requires_approval: false}
```

### Memory Recording
- **plan**: Goal, intent, 2 subtasks
- **tool_usage**: bulk_recommend, build_campaign_execution_plan
- **observation**: "Campaign plan created: 14 prospects, 12 to send"

### Expected Output
```json
{
  "plan": {
    "offer_code": "PROMO-WINBACK",
    "segment": "dormant_vip",
    "total_prospects": 14,
    "to_send": 12,
    "blocked": 2,
    "by_channel": {
      "email": 11,
      "sms": 1,
      "blocked": 2
    }
  },
  "status": "ready",
  "requires_approval": false
}
```

---

## UC7: Return Risk Intervention

**Intent**: `return_risk_intervention`
**Agents**: `analytics_agent` → `compliance_agent` (2x) → `functional_agent`
**Tools**: `run_sql_query()` → `check_identity_gate()` → `check_marketing_consent()` → `send_notification()`
**Memory**: plan, sql_generation, compliance_decision (2x per customer), tool_usage (3x per customer), observation

### Exact Code Path
```python
# Request parsing
threshold = 0.70

# Step 1: Identify at-risk customers
sql_query = f"SELECT * FROM customers WHERE return_risk > {threshold}"
memory.record_sql_generation(request_id, sql_query, "identify_high_return_risk")
at_risk_result = analytics_server.run_sql_query(sql_query, max_rows=100)
memory.record_tool_usage(request_id, "run_sql_query", {"sql": sql_query}, at_risk_result)

at_risk_customers = at_risk_result.get("result", [])

# Step 2-4: For each customer
sent_count = 0
blocked_count = 0

for customer in at_risk_customers:
    customer_id = customer["customer_id"]
    
    # Check identity
    identity_result = compliance_server.check_identity_gate(customer_id)
    identity_decision = {
        "customer_id": customer_id,
        "check_type": "identity_gate",
        "passed": identity_result.get("result", {}).get("gate_passed", False)
    }
    memory.record_compliance_decision(request_id, identity_decision)
    
    if not identity_decision["passed"]:
        blocked_count += 1
        continue
    
    # Check consent
    consent_result = compliance_server.check_marketing_consent(customer_id)
    consent_decision = {
        "customer_id": customer_id,
        "check_type": "marketing_consent",
        "passed": consent_result.get("result", {}).get("marketing_consent", False)
    }
    memory.record_compliance_decision(request_id, consent_decision)
    
    if not consent_decision["passed"]:
        blocked_count += 1
        continue
    
    # Send intervention
    send_result = notification_server.send_notification(customer_id, "email", 
        {"subject": "We miss you!", "body": "Special offer for valued customers"})
    memory.record_tool_usage(request_id, "send_notification", 
        {"customer_id": customer_id, "channel": "email"}, send_result)
    
    sent_count += 1

# Memory recording
memory.record_plan(request_id, {
    "goal": "Identify high-return-risk customers and intervene",
    "intent": "return_risk_intervention",
    "requires_sql": True,
    "subtasks": [
        {"tool": "identify_at_risk", "agent": "analytics_agent"},
        {"tool": "filter_by_identity", "agent": "compliance_agent"},
        {"tool": "filter_by_consent", "agent": "compliance_agent"},
        {"tool": "send_intervention", "agent": "functional_agent"}
    ]
})
memory.record_observation(request_id, 
    f"Return risk intervention: {sent_count} contacted, {blocked_count} blocked")

# Return
return {
    "at_risk_count": len(at_risk_customers),
    "sent": sent_count,
    "blocked": blocked_count
}
```

### MCP Tool Calls
```
Step 1: run_sql_query(sql: "SELECT * FROM customers WHERE return_risk > 0.70", max_rows: 100)
  → {result: [{customer_id, return_risk, ...}, ...]}

For each customer:
  Step 2: check_identity_gate(customer_id: "CUST-XXX")
    → {gate_passed: true/false}
  
  Step 3: check_marketing_consent(customer_id: "CUST-XXX")
    → {marketing_consent: true/false}
  
  Step 4: send_notification(customer_id: "CUST-XXX", channel: "email", content: {...})
    → {status: "SENT", message_id}
```

### Memory Recording
- **plan**: Goal, intent, 4 subtasks
- **sql_generation**: Query with intent
- **tool_usage**: run_sql_query
- **compliance_decision**: identity_gate (per customer)
- **compliance_decision**: marketing_consent (per customer)
- **tool_usage**: send_notification (per customer)
- **observation**: "Return risk intervention: 8 contacted, 3 blocked"

### Expected Output
```json
{
  "at_risk_count": 11,
  "sent": 8,
  "blocked": 3
}
```

---

## UC8: Campaign Results Dashboard

**Intent**: `campaign_dashboard`
**Agents**: `analytics_agent`
**Tools**: `run_sql_query()` → `analyze_campaign_results()`
**Memory**: plan, sql_generation, tool_usage (2x), observation

### Exact Code Path
```python
# Step 1: Query campaign results
sql_query = "SELECT * FROM campaign_results"
memory.record_sql_generation(request_id, sql_query, "campaign_dashboard")
query_result = analytics_server.run_sql_query(sql_query, max_rows=1000)
memory.record_tool_usage(request_id, "run_sql_query", {"sql": sql_query}, query_result)

# Step 2: Analyze results
analysis_result = analytics_server.analyze_campaign_results(query_result.get("result", []))
memory.record_tool_usage(request_id, "analyze_campaign_results", 
    {"results_count": len(query_result.get("result", []))}, analysis_result)

# Memory recording
memory.record_plan(request_id, {
    "goal": "Analyze campaign performance metrics",
    "intent": "campaign_dashboard",
    "requires_sql": True,
    "subtasks": [
        {"tool": "query_campaign_results", "agent": "analytics_agent"},
        {"tool": "analyze_results", "agent": "analytics_agent"}
    ]
})
memory.record_observation(request_id, 
    f"Campaign analysis: {analysis_result['total_sent']} sent, {analysis_result['converted']} converted, {analysis_result['conversion_rate']}% conversion")

# Return
return analysis_result  # {metrics: {...}, insights: [...]}
```

### MCP Tool Calls
```
Step 1: run_sql_query(sql: "SELECT * FROM campaign_results", max_rows: 1000)
  → {result: [{campaign_id, customer_id, status, ...}, ...]}

Step 2: analyze_campaign_results(results: [...])
  → {metrics: {total_sent, opened, clicked, converted, unsubscribed, conversion_rate}, insights: [...]}
```

### Memory Recording
- **plan**: Goal, intent, 2 subtasks
- **sql_generation**: Query with intent
- **tool_usage**: run_sql_query, analyze_campaign_results
- **observation**: "Campaign analysis: 103 sent, 22 converted, 21.4% conversion"

### Expected Output
```json
{
  "metrics": {
    "total_sent": 103,
    "opened": 25,
    "clicked": 11,
    "converted": 22,
    "unsubscribed": 13,
    "conversion_rate": 0.214
  },
  "insights": [
    "Email channel has highest conversion rate (25%)",
    "VIP segment converts 2x better than casual segment"
  ]
}
```

---

## UC9: Guardrails

**Intent**: `guardrails`
**Agents**: `compliance_agent`
**Tools**: `guardrail_check(text, request_id)` → `redact_pii(text)`
**Memory**: plan, compliance_decision, tool_usage (2x), observation

### Exact Code Path
```python
# Request parsing
text = "Customer email is john.doe@example.com and phone is 555-123-4567. We recommend buying shares."

# Step 1: Guardrail check
check_result = compliance_server.guardrail_check(text, request_id)
decision = {
    "check_type": "guardrail",
    "passed": check_result.get("result", {}).get("passed", True),
    "violations": len(check_result.get("result", {}).get("violations", []))
}
memory.record_compliance_decision(request_id, decision)
memory.record_tool_usage(request_id, "guardrail_check", {"text": text}, check_result)

# Step 2: Redact PII if violations
if not decision["passed"]:
    redact_result = compliance_server.redact_pii(text)
    memory.record_tool_usage(request_id, "redact_pii", {"text": text}, redact_result)
    final_text = redact_result.get("result", {}).get("redacted_text", text)
else:
    final_text = text

# Memory recording
memory.record_plan(request_id, {
    "goal": "Apply guardrails and redact PII",
    "intent": "guardrails",
    "requires_sql": False,
    "subtasks": [
        {"tool": "guardrail_check", "agent": "compliance_agent"}
    ]
})
memory.record_observation(request_id, 
    f"Guardrails check: {decision['violations']} violations found and redacted")

# Return
return {
    "original_text": text,
    "redacted_text": final_text,
    "violations": check_result.get("result", {}).get("violations", []),
    "passed": decision["passed"]
}
```

### MCP Tool Calls
```
Step 1: guardrail_check(text: "Customer email is john.doe@example.com...", request_id: "req-123")
  → {passed: false, violations: [{type: "email", value: "john.doe@example.com"}, {type: "phone", value: "555-123-4567"}]}

Step 2: redact_pii(text: "Customer email is john.doe@example.com...")
  → {redacted_text: "Customer email is [email redacted] and phone is [phone redacted]..."}
```

### Memory Recording
- **plan**: Goal, intent, 1 subtask
- **compliance_decision**: {check_type: "guardrail", passed: false, violations: 2}
- **tool_usage**: guardrail_check, redact_pii
- **observation**: "Guardrails check: 2 violations found and redacted"

### Expected Output
```json
{
  "original_text": "Customer email is john.doe@example.com and phone is 555-123-4567. We recommend buying shares.",
  "redacted_text": "Customer email is [email redacted] and phone is [phone redacted]. We recommend buying shares.",
  "violations": [
    {"type": "email", "value": "john.doe@example.com"},
    {"type": "phone", "value": "555-123-4567"}
  ],
  "passed": false
}
```
