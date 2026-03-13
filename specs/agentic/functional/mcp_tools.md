# Functional Agent MCP Tools Specification

## Tool Catalogue

### 1. score_leads

**Module**: `recommendation_server`
**Delegates To**: `nonagentic.tools.leads.score_leads()`

**Signature**:
```python
def score_leads(
    offer_code: str,
    top_n: int = 20,
    segment: Optional[str] = None
) -> dict
```

**Parameters**:
- `offer_code` (str, required): Offer code to score leads for (e.g., "PROMO-PREMIUM-MEMBERSHIP")
- `top_n` (int, optional): Number of top prospects to return (default: 20)
- `segment` (str, optional): Customer segment to filter by (e.g., "vip", "dormant_vip")

**Return Schema**:
```json
{
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
```

**Algorithm**:
1. Query customers in segment (if provided)
2. Score each customer by engagement + fit
3. Sort by score descending
4. Return top_n prospects

**Constraints**:
- top_n max: 100
- segment must be valid (vip, casual, dormant_vip, at_risk)

**Performance**: O(n log n) where n = total customers

---

### 2. recommend_offer

**Module**: `recommendation_server`
**Delegates To**: `nonagentic.tools.functional.recommend_offer()`

**Signature**:
```python
def recommend_offer(
    customer_id: str,
    context: str = ""
) -> dict
```

**Parameters**:
- `customer_id` (str, required): Customer ID (e.g., "CUST-001")
- `context` (str, optional): Additional context for recommendation

**Return Schema**:
```json
{
  "offer_id": "OFFER-001",
  "offer_name": "Win-Back Offer",
  "confidence": 0.879,
  "rationale": "High engagement history, dormant for 3 months"
}
```

**Algorithm**:
1. Lookup customer profile
2. Score available offers
3. Rank by fit + engagement
4. Return top offer

**Constraints**:
- customer_id must exist
- confidence range: 0.0 - 1.0

**Performance**: O(1) lookup + O(m) scoring where m = number of offers

---

### 3. bulk_recommend

**Module**: `recommendation_server`
**Delegates To**: `nonagentic.tools.leads.bulk_recommend()`

**Signature**:
```python
def bulk_recommend(
    offer_code: str,
    segment: Optional[str] = None,
    top_n: int = 50
) -> dict
```

**Parameters**:
- `offer_code` (str, required): Offer code (e.g., "PROMO-WINBACK")
- `segment` (str, optional): Customer segment to target
- `top_n` (int, optional): Number of prospects to return (default: 50)

**Return Schema**:
```json
{
  "prospects": [
    {
      "customer_id": "CUST-089",
      "name": "Customer CUST-089",
      "segment": "dormant_vip",
      "score": 0.80,
      "channel": "email"
    }
  ],
  "total": 14,
  "to_send": 12,
  "blocked": 2,
  "by_channel": {
    "email": 11,
    "sms": 1,
    "blocked": 2
  }
}
```

**Algorithm**:
1. Query customers in segment
2. Score each customer
3. Filter by consent
4. Filter by identity
5. Sort by score
6. Return top_n with channel assignment

**Constraints**:
- top_n max: 500
- segment must be valid

**Performance**: O(n log n) where n = segment size

---

### 4. enrich_customer

**Module**: `functional_server`
**Delegates To**: `nonagentic.tools.leads.enrich_customer()`

**Signature**:
```python
def enrich_customer(customer_id: str) -> dict
```

**Parameters**:
- `customer_id` (str, required): Customer ID (e.g., "CUST-001")

**Return Schema**:
```json
{
  "credit_score": 726,
  "company_type": "Sole Trader",
  "location_score": 0.80,
  "enrichment_sources": 3,
  "last_updated": "2024-01-15T10:30:00Z"
}
```

**Algorithm**:
1. Lookup base profile
2. Fetch credit bureau data
3. Fetch business registry data
4. Fetch location enrichment
5. Merge all sources
6. Return enriched profile

**Data Sources**:
- Credit Bureau: credit_score, credit_history
- Business Registry: company_type, company_size, industry
- Location Enrichment: location_score, region, demographics

**Constraints**:
- customer_id must exist
- credit_score range: 300-850
- location_score range: 0.0-1.0

**Performance**: O(1) per source, ~100ms total

---

### 5. draft_email

**Module**: `notification_server`
**Delegates To**: `nonagentic.tools.functional.draft_email()`

**Signature**:
```python
def draft_email(
    customer_id: str,
    template_id: str,
    variables: dict = {}
) -> dict
```

**Parameters**:
- `customer_id` (str, required): Customer ID
- `template_id` (str, required): Email template ID (e.g., "T-PROMO-01")
- `variables` (dict, optional): Template variables to substitute

**Return Schema**:
```json
{
  "subject": "Exclusive promotion just for you",
  "body": "Dear Customer CUST-001,\n\nWe have a special promotion: Win-Back Offer.\n\nBest regards,\nMarketing Team",
  "preview": "Dear Customer CUST-001, We have a special promotion...",
  "template_id": "T-PROMO-01"
}
```

**Algorithm**:
1. Load template
2. Substitute variables
3. Personalize with customer data
4. Return draft

**Template Variables**:
- `{customer_name}` → Customer name
- `{offer_name}` → Offer name
- `{discount}` → Discount percentage
- `{expiry_date}` → Offer expiry date

**Constraints**:
- template_id must exist
- subject max: 100 chars
- body max: 5000 chars

**Performance**: O(1) template lookup + O(m) substitution where m = template size

---

### 6. send_notification

**Module**: `notification_server`
**Delegates To**: `nonagentic.tools.functional.send_notification()`

**Signature**:
```python
def send_notification(
    customer_id: str,
    channel: str,
    content: dict,
    dry_run: bool = False
) -> dict
```

**Parameters**:
- `customer_id` (str, required): Customer ID
- `channel` (str, required): Delivery channel ("email", "sms", "push")
- `content` (dict, required): Message content {subject, body}
- `dry_run` (bool, optional): Simulate send without actual delivery

**Return Schema**:
```json
{
  "status": "SENT",
  "message_id": "MSG-12345",
  "channel": "email",
  "customer_id": "CUST-001",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Algorithm**:
1. Validate customer exists
2. Validate channel
3. If dry_run: simulate send
4. Else: send via channel
5. Record delivery
6. Return status

**Channels**:
- `email`: Via email provider
- `sms`: Via SMS provider
- `push`: Via push notification service

**Constraints**:
- channel must be valid
- customer must have consent for channel
- content must have subject and body

**Performance**: O(1) for dry_run, ~500ms for actual send

---

### 7. create_case

**Module**: `functional_server`
**Delegates To**: `nonagentic.tools.functional.create_case()`

**Signature**:
```python
def create_case(
    customer_id: str,
    case_type: str,
    description: str,
    priority: str = "medium"
) -> dict
```

**Parameters**:
- `customer_id` (str, required): Customer ID
- `case_type` (str, required): Case type (e.g., "identity_reverification", "general")
- `description` (str, required): Case description
- `priority` (str, optional): Priority level ("low", "medium", "high")

**Return Schema**:
```json
{
  "case_id": "CASE-12345",
  "customer_id": "CUST-099",
  "case_type": "identity_reverification",
  "status": "CREATED",
  "priority": "high",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Algorithm**:
1. Generate case_id
2. Store case record
3. Assign to queue
4. Set priority
5. Return case details

**Case Types**:
- `identity_reverification` — Identity verification needed
- `consent_update` — Consent update needed
- `general` — General support case

**Priority Levels**:
- `low` — Standard processing
- `medium` — Normal priority
- `high` — Urgent processing

**Constraints**:
- customer_id must exist
- case_type must be valid
- priority must be valid

**Performance**: O(1) case creation

---

### 8. check_marketing_consent

**Module**: `compliance_server`
**Delegates To**: `nonagentic.core.guardrails.check_marketing_consent()`

**Signature**:
```python
def check_marketing_consent(customer_id: str) -> dict
```

**Parameters**:
- `customer_id` (str, required): Customer ID

**Return Schema**:
```json
{
  "result": {
    "marketing_consent": true,
    "email_consent": true,
    "sms_consent": false,
    "push_consent": true
  },
  "tool_name": "check_marketing_consent",
  "execution_status": "success"
}
```

**Algorithm**:
1. Lookup consent flags
2. Check marketing_consent flag
3. Check channel-specific flags
4. Return consent status

**Consent Flags**:
- `marketing_consent` — General marketing consent
- `email_consent` — Email channel consent
- `sms_consent` — SMS channel consent
- `push_consent` — Push notification consent

**Constraints**:
- customer_id must exist

**Performance**: O(1) lookup

---

### 9. check_identity_gate

**Module**: `compliance_server`
**Delegates To**: `nonagentic.core.guardrails.check_identity_gate()`

**Signature**:
```python
def check_identity_gate(customer_id: str) -> dict
```

**Parameters**:
- `customer_id` (str, required): Customer ID

**Return Schema**:
```json
{
  "result": {
    "gate_passed": true,
    "kyc_status": "VERIFIED",
    "kyc_expiry": "2027-11-11",
    "identity_verified": true
  },
  "tool_name": "check_identity_gate",
  "execution_status": "success"
}
```

**Algorithm**:
1. Lookup KYC status
2. Check if verified
3. Check if not expired
4. Return gate status

**KYC Status Values**:
- `VERIFIED` — Identity verified and valid
- `UNVERIFIED` — Identity not yet verified
- `EXPIRED` — Identity verification expired
- `PENDING` — Verification in progress

**Constraints**:
- customer_id must exist
- kyc_expiry must be in future for gate to pass

**Performance**: O(1) lookup

---

### 10. guardrail_check

**Module**: `compliance_server`
**Delegates To**: `nonagentic.core.guardrails.guardrail_check()`

**Signature**:
```python
def guardrail_check(text: str, request_id: str) -> dict
```

**Parameters**:
- `text` (str, required): Text to check
- `request_id` (str, required): Request ID for audit trail

**Return Schema**:
```json
{
  "result": {
    "passed": false,
    "violations": [
      {
        "type": "email",
        "value": "john.doe@example.com",
        "severity": "high"
      },
      {
        "type": "phone",
        "value": "555-123-4567",
        "severity": "high"
      }
    ]
  },
  "tool_name": "guardrail_check",
  "execution_status": "success"
}
```

**Algorithm**:
1. Scan for PII patterns
2. Scan for policy violations
3. Collect violations
4. Return status and violations

**PII Patterns Detected**:
- Email addresses
- Phone numbers
- Credit card numbers
- Social Security numbers
- Bank account numbers

**Policy Violations**:
- Discriminatory language
- Confidential information
- Malicious content

**Constraints**:
- text max: 10,000 chars
- request_id required for audit

**Performance**: O(n) where n = text length

---

### 11. redact_pii

**Module**: `compliance_server`
**Delegates To**: `nonagentic.core.guardrails.redact_pii()`

**Signature**:
```python
def redact_pii(text: str) -> dict
```

**Parameters**:
- `text` (str, required): Text to redact

**Return Schema**:
```json
{
  "result": {
    "redacted_text": "Customer email is [email redacted] and phone is [phone redacted]. We recommend buying shares.",
    "redactions": [
      {
        "type": "email",
        "original": "john.doe@example.com",
        "replacement": "[email redacted]"
      },
      {
        "type": "phone",
        "original": "555-123-4567",
        "replacement": "[phone redacted]"
      }
    ]
  },
  "tool_name": "redact_pii",
  "execution_status": "success"
}
```

**Algorithm**:
1. Identify PII patterns
2. Replace with redaction placeholders
3. Track redactions
4. Return redacted text

**Redaction Placeholders**:
- Email: `[email redacted]`
- Phone: `[phone redacted]`
- Credit card: `[card redacted]`
- SSN: `[ssn redacted]`

**Constraints**:
- text max: 10,000 chars

**Performance**: O(n) where n = text length

---

### 12. run_sql_query

**Module**: `analytics_server`
**Delegates To**: `nonagentic.tools.analytics.run_sql_query()`

**Signature**:
```python
def run_sql_query(
    sql: str,
    max_rows: int = 1000
) -> dict
```

**Parameters**:
- `sql` (str, required): SQL query to execute
- `max_rows` (int, optional): Maximum rows to return (default: 1000)

**Return Schema**:
```json
{
  "result": [
    {
      "customer_id": "CUST-014",
      "return_risk": 0.83,
      "segment": "at_risk"
    }
  ],
  "total_rows": 11,
  "query": "SELECT * FROM customers WHERE return_risk > 0.70"
}
```

**Algorithm**:
1. Parse SQL query
2. Validate query safety
3. Execute query
4. Limit results to max_rows
5. Return results

**Supported Queries**:
- SELECT with WHERE, ORDER BY, LIMIT
- Aggregations: COUNT, SUM, AVG, MIN, MAX
- Joins: INNER, LEFT, RIGHT

**Constraints**:
- max_rows: 1-10000
- Query timeout: 30 seconds
- No INSERT, UPDATE, DELETE

**Performance**: Depends on query complexity

---

## Tool Delegation Pattern

All MCP tools follow this pattern:

```python
def tool_name(params) -> dict:
    # Call nonagentic tool
    result = nonagentic.tools.module.tool_name(params)
    
    # Wrap in MCP response
    return {
        "result": result,
        "tool_name": "tool_name",
        "execution_status": "success" if not result.get("error") else "failed",
        "audit": {
            # Audit metadata
        }
    }
```

This maintains compatibility with nonagent system while adding:
- Agentic routing
- Memory recording
- Audit trail
