# Functional Agent Compliance Gates Specification

## Overview

Compliance gates are inline checks that enforce business rules and regulatory requirements. They are applied during functional workflows to ensure actions comply with consent, identity, and policy requirements.

**Three Gate Types**:
1. **Consent Gate** — Verify marketing consent before sending notifications
2. **Identity Gate** — Verify customer identity before sensitive actions
3. **Guardrails Gate** — Scan for PII and policy violations

---

## Consent Gate

### Purpose
Verify that customer has given consent for marketing communications before sending notifications.

### Decision Tree

```
check_marketing_consent(customer_id)
  ├─ Lookup consent flags from customer profile
  ├─ Check marketing_consent flag
  │  ├─ If true: return {passed: true}
  │  └─ If false: return {passed: false, reason: "consent_email"}
  └─ Check channel-specific flags
     ├─ email_consent for email channel
     ├─ sms_consent for SMS channel
     └─ push_consent for push channel
```

### Consent Flags

| Flag | Type | Default | Meaning |
|------|------|---------|---------|
| `marketing_consent` | bool | false | General marketing consent |
| `email_consent` | bool | false | Email channel consent |
| `sms_consent` | bool | false | SMS channel consent |
| `push_consent` | bool | false | Push notification consent |

### Enforcement Rules

**Rule 1**: Cannot send email without `email_consent`
```python
if channel == "email" and not customer.email_consent:
    return {"status": "BLOCKED", "reason": "consent_email"}
```

**Rule 2**: Cannot send SMS without `sms_consent`
```python
if channel == "sms" and not customer.sms_consent:
    return {"status": "BLOCKED", "reason": "consent_sms"}
```

**Rule 3**: Cannot send push without `push_consent`
```python
if channel == "push" and not customer.push_consent:
    return {"status": "BLOCKED", "reason": "consent_push"}
```

### Use Cases

**UC3: NBA Recommendation**
- Check: `check_marketing_consent(customer_id)`
- Block: If not passed, return error
- Record: `compliance_decision` with passed=false

**UC4: Consent-Gated Notification**
- Check: `check_marketing_consent(customer_id)` before `send_notification()`
- Block: If not passed, return {status: "BLOCKED", reason: "consent_email"}
- Record: `compliance_decision` with passed=false

**UC6: Bulk Campaign Targeting**
- Check: Applied during `bulk_recommend()` to filter prospects
- Filter: Remove prospects without consent
- Record: Blocked count in campaign plan

**UC7: Return Risk Intervention**
- Check: `check_marketing_consent(customer_id)` for each prospect
- Filter: Remove prospects without consent
- Record: `compliance_decision` per customer

### Memory Recording

```python
decision = {
    "customer_id": customer_id,
    "check_type": "marketing_consent",
    "passed": result.get("marketing_consent", False),
    "channel": channel,  # Optional
    "timestamp": datetime.utcnow().isoformat()
}
memory.record_compliance_decision(request_id, decision)
```

---

## Identity Gate

### Purpose
Verify that customer identity is verified before sensitive actions like case creation or high-value transactions.

### Decision Tree

```
check_identity_gate(customer_id)
  ├─ Lookup KYC status from customer profile
  ├─ Check kyc_status
  │  ├─ If "VERIFIED":
  │  │  ├─ Check kyc_expiry
  │  │  ├─ If expiry > today: return {passed: true}
  │  │  └─ If expiry <= today: return {passed: false, reason: "kyc_expired"}
  │  ├─ If "UNVERIFIED": return {passed: false, reason: "kyc_unverified"}
  │  ├─ If "EXPIRED": return {passed: false, reason: "kyc_expired"}
  │  └─ If "PENDING": return {passed: false, reason: "kyc_pending"}
  └─ Return gate_passed status
```

### KYC Status Values

| Status | Meaning | Gate Passes |
|--------|---------|-------------|
| `VERIFIED` | Identity verified and valid | Yes (if not expired) |
| `UNVERIFIED` | Identity not yet verified | No |
| `EXPIRED` | Verification expired | No |
| `PENDING` | Verification in progress | No |

### Enforcement Rules

**Rule 1**: Cannot proceed with unverified identity
```python
if kyc_status != "VERIFIED":
    return {"passed": false, "reason": f"kyc_{kyc_status.lower()}"}
```

**Rule 2**: Cannot proceed with expired identity
```python
if kyc_status == "VERIFIED" and kyc_expiry <= today:
    return {"passed": false, "reason": "kyc_expired"}
```

**Rule 3**: Create remediation case if identity not verified
```python
if not gate_passed:
    create_case(customer_id, "identity_reverification", 
        "Identity unverified", priority="high")
```

### Use Cases

**UC5: Identity Gate**
- Check: `check_identity_gate(customer_id)`
- Action: If not passed, create remediation case
- Record: `compliance_decision` with passed=false

**UC6: Bulk Campaign Targeting**
- Check: Applied during `bulk_recommend()` to filter prospects
- Filter: Remove prospects with unverified identity
- Record: Blocked count in campaign plan

**UC7: Return Risk Intervention**
- Check: `check_identity_gate(customer_id)` for each prospect
- Filter: Remove prospects with unverified identity
- Record: `compliance_decision` per customer

### Memory Recording

```python
decision = {
    "customer_id": customer_id,
    "check_type": "identity_gate",
    "passed": result.get("gate_passed", False),
    "kyc_status": result.get("kyc_status"),
    "kyc_expiry": result.get("kyc_expiry"),
    "timestamp": datetime.utcnow().isoformat()
}
memory.record_compliance_decision(request_id, decision)
```

### Remediation Case Creation

When identity gate fails, create case:

```python
if not gate_passed:
    case = create_case(
        customer_id=customer_id,
        case_type="identity_reverification",
        description=f"Identity verification required. Current status: {kyc_status}",
        priority="high"
    )
    return {
        "passed": False,
        "reason": f"kyc_{kyc_status.lower()}",
        "case_created": True,
        "case_id": case["case_id"]
    }
```

---

## Guardrails Gate

### Purpose
Scan text for personally identifiable information (PII) and policy violations before sending or storing.

### Decision Tree

```
guardrail_check(text, request_id)
  ├─ Scan for PII patterns
  │  ├─ Email addresses: john.doe@example.com
  │  ├─ Phone numbers: 555-123-4567
  │  ├─ Credit card numbers: 4532-1234-5678-9010
  │  ├─ Social Security numbers: 123-45-6789
  │  └─ Bank account numbers
  ├─ Scan for policy violations
  │  ├─ Discriminatory language
  │  ├─ Confidential information
  │  └─ Malicious content
  ├─ Collect violations
  ├─ If violations found: return {passed: false, violations: [...]}
  └─ Else: return {passed: true, violations: []}
```

### PII Patterns

| Pattern | Regex | Example | Severity |
|---------|-------|---------|----------|
| Email | `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}` | john.doe@example.com | High |
| Phone | `\d{3}-\d{3}-\d{4}` | 555-123-4567 | High |
| Credit Card | `\d{4}-\d{4}-\d{4}-\d{4}` | 4532-1234-5678-9010 | Critical |
| SSN | `\d{3}-\d{2}-\d{4}` | 123-45-6789 | Critical |
| Bank Account | `\d{8,17}` | 123456789 | High |

### Policy Violations

| Violation | Pattern | Severity |
|-----------|---------|----------|
| Discriminatory | Slurs, hate speech | Critical |
| Confidential | Trade secrets, passwords | High |
| Malicious | Injection attacks, exploits | Critical |

### Enforcement Rules

**Rule 1**: Block if critical violations found
```python
critical_violations = [v for v in violations if v["severity"] == "critical"]
if critical_violations:
    return {"passed": false, "violations": violations}
```

**Rule 2**: Redact if high violations found
```python
high_violations = [v for v in violations if v["severity"] in ("high", "critical")]
if high_violations:
    redacted_text = redact_pii(text)
    return {"passed": false, "violations": violations, "redacted_text": redacted_text}
```

**Rule 3**: Allow if no violations
```python
if not violations:
    return {"passed": true, "violations": []}
```

### Use Cases

**UC9: Guardrails**
- Check: `guardrail_check(text, request_id)`
- Action: If violations found, redact PII
- Record: `compliance_decision` with violations count

### Memory Recording

```python
decision = {
    "check_type": "guardrail",
    "passed": result.get("passed", True),
    "violations": len(result.get("violations", [])),
    "violation_types": [v["type"] for v in result.get("violations", [])],
    "timestamp": datetime.utcnow().isoformat()
}
memory.record_compliance_decision(request_id, decision)
```

### Redaction

When violations found, redact PII:

```python
if not gate_passed:
    redact_result = redact_pii(text)
    return {
        "passed": False,
        "violations": violations,
        "original_text": text,
        "redacted_text": redact_result["redacted_text"]
    }
```

**Redaction Placeholders**:
- Email: `[email redacted]`
- Phone: `[phone redacted]`
- Credit card: `[card redacted]`
- SSN: `[ssn redacted]`
- Bank account: `[account redacted]`

---

## Gate Application Matrix

| Use Case | Consent Gate | Identity Gate | Guardrails Gate |
|----------|--------------|---------------|-----------------|
| UC1: Lead Scoring | No | No | No |
| UC2: Enrichment | No | No | No |
| UC3: NBA | Yes | No | No |
| UC4: Notification | Yes | No | Yes |
| UC5: Identity Gate | No | Yes | No |
| UC6: Bulk Campaign | Yes | Yes | No |
| UC7: Return Risk | Yes | Yes | No |
| UC8: Dashboard | No | No | No |
| UC9: Guardrails | No | No | Yes |

---

## Gate Failure Handling

### Consent Gate Failure

**Response**:
```json
{
  "status": "BLOCKED",
  "reason": "consent_email",
  "message": "Customer has not consented to email marketing"
}
```

**Action**: Do not send notification

**Memory**: Record compliance_decision with passed=false

### Identity Gate Failure

**Response**:
```json
{
  "status": "BLOCKED",
  "reason": "kyc_unverified",
  "message": "Customer identity not verified",
  "case_created": true,
  "case_id": "CASE-12345"
}
```

**Action**: Create remediation case

**Memory**: Record compliance_decision with passed=false

### Guardrails Gate Failure

**Response**:
```json
{
  "status": "REDACTED",
  "violations": [
    {"type": "email", "value": "john.doe@example.com", "severity": "high"}
  ],
  "original_text": "Customer email is john.doe@example.com",
  "redacted_text": "Customer email is [email redacted]"
}
```

**Action**: Redact PII and proceed

**Memory**: Record compliance_decision with violations count

---

## Audit Trail

All gate checks recorded to memory:

```python
# Consent gate
memory.record_compliance_decision(request_id, {
    "customer_id": customer_id,
    "check_type": "marketing_consent",
    "passed": True/False,
    "channel": "email"
})

# Identity gate
memory.record_compliance_decision(request_id, {
    "customer_id": customer_id,
    "check_type": "identity_gate",
    "passed": True/False,
    "kyc_status": "VERIFIED"
})

# Guardrails gate
memory.record_compliance_decision(request_id, {
    "check_type": "guardrail",
    "passed": True/False,
    "violations": 2
})
```

Enables:
- Compliance audit
- Regulatory reporting
- Pattern analysis
- Debugging
