# ⚙️ Level 3 — Functional Agent / Lead Generation & Targeted Marketing

**TL;DR**: The functional agent executes business actions — lead scoring, customer enrichment, next-best-action recommendations, consent-gated notifications, identity-gated actions, bulk campaign targeting, and payment risk interventions.

---

## Business Use Cases

### 1. Lead Scoring
Rank prospects by likelihood to convert using multi-factor scoring: engagement, fraud score, lifetime value, and recency.

**Trigger**: Requests about "lead score", "prospect ranking", or "who should we contact".

**Output**: Ranked list of prospects with scores and reasoning.

**Factors**:
- Engagement score (0-1)
- Fraud score (0-1, inverted)
- Lifetime value (£)
- Recency (days since last interaction)

---

### 2. Customer Enrichment
Enhance customer profiles with external data: credit bureau scores, business registry info, location data.

**Trigger**: Requests about "enrich", "verify", or "get more info".

**Output**: Enhanced profile with credit score, business type, location, risk assessment.

**Data Sources** (simulated):
- Credit bureau API
- Business registry
- Location/geocoding API

---

### 3. Next-Best-Action (NBA) Recommendation
Recommend the best product or offer for each customer based on segment, purchase history, and engagement.

**Trigger**: Requests about "next best action", "what should we offer", or "recommend action".

**Output**: Recommended product/offer with confidence score and reasoning.

**Logic**:
- Cross-sell rules (if bought X, recommend Y)
- Segment scoring (what's popular in this segment)
- Engagement-based filtering (only active customers)

---

### 4. Upsell Recommendations
Identify higher-tier products based on purchase categories and engagement.

**Trigger**: Requests about "upsell", "upgrade", or "premium".

**Output**: Recommended premium products with expected uplift.

**Example**: Customer bought "basic card" → recommend "premium card" with 2x benefits.

---

### 5. User-Based Recommendations
Segment peer behavior analysis — what are similar customers buying?

**Trigger**: Requests about "similar customers" or "peer recommendations".

**Output**: Products popular in the customer's segment.

---

### 6. Collaborative Filtering
Cross-customer similarity recommendations — find customers most similar to the target and surface their purchases.

**Trigger**: Requests about "collaborative", "similar users", or "co-purchase".

**Output**: Products bought by similar customers, ranked by similarity.

---

### 7. Consent-Gated Notifications
Send notifications (email/SMS/push) only to customers who have opted in.

**Trigger**: Requests about "send", "notify", or "contact".

**Output**: Notification sent to consented channels, audit logged.

**Consent Checks**:
- Email consent required for email
- SMS consent required for SMS
- Push consent required for push
- Marketing consent required for promotional content

---

### 8. Identity-Gated Actions
Block actions on customers with expired identity verification; open remediation case instead.

**Trigger**: Any action on a customer with unverified/expired identity.

**Output**: Action blocked, remediation case created, customer notified.

**Remediation Flow**:
1. Check identity status
2. If expired/unverified → create case
3. Send identity renewal reminder
4. Block high-value actions until verified

---

### 9. Bulk Campaign Targeting
Execute segment-level campaigns with approval gates for high-reach initiatives.

**Trigger**: Requests about "campaign", "bulk send", or "segment targeting".

**Output**: Campaign execution plan with approval gate, audit logged.

**Approval Gates**:
- Campaigns > 100 customers require approval
- Campaigns > 1,000 reach require approval
- High-risk segments require approval

---

### 10. Payment Risk Intervention
Identify customers at risk of payment delays and proactively contact them.

**Trigger**: Automatic (runs on schedule) or manual request.

**Output**: List of at-risk customers, intervention actions (email, SMS, call).

**Risk Factors**:
- Days since last payment
- Payment failure rate
- Account balance trend
- Fraud score

---

## Architecture

```
Level 3 Agent (src/agents/level3.py)
│
├── Lead Scoring
│   ├── Multi-factor scoring
│   ├── Ranking
│   └── Explanation generation
│
├── Customer Enrichment
│   ├── Credit bureau lookup
│   ├── Business registry lookup
│   ├── Location API
│   └── Risk assessment
│
├── Next-Best-Action
│   ├── Cross-sell rules
│   ├── Segment scoring
│   ├── Engagement filtering
│   └── Recommendation ranking
│
├── Recommendations
│   ├── Upsell logic
│   ├── User-based (segment peers)
│   ├── Collaborative filtering
│   └── Hybrid ranking
│
├── Notifications
│   ├── Consent checking
│   ├── Channel selection
│   ├── Template rendering
│   └── Delivery tracking
│
├── Identity Gating
│   ├── Status checking
│   ├── Expiry validation
│   ├── Case creation
│   └── Remediation workflow
│
├── Campaign Execution
│   ├── Segment targeting
│   ├── Approval gates
│   ├── Batch execution
│   └── Result tracking
│
├── Payment Risk
│   ├── Risk scoring
│   ├── Intervention selection
│   ├── Action execution
│   └── Outcome tracking
│
└── Guardrails
    ├── Consent validation
    ├── Identity verification
    ├── Approval gates
    └── Audit logging
```

---

## Key Features

### Multi-Factor Lead Scoring
Combines engagement, fraud risk, lifetime value, and recency into a single score:

```
score = (engagement × 0.3) 
      + ((1 - fraud_score) × 0.2)
      + (normalized_ltv × 0.3)
      + (recency_factor × 0.2)
```

### Consent-Aware Notifications
Automatically respects customer preferences:
- Checks consent flags before sending
- Selects appropriate channels
- Logs all sends to audit trail
- Handles opt-out requests

### Identity Verification Gating
Blocks high-value actions on unverified customers:
- Checks identity status
- Validates expiry date
- Creates remediation case
- Sends renewal reminder

### Approval Gates
High-reach campaigns require human approval:
- Campaigns > 100 customers
- Campaigns > 1,000 reach
- High-risk segments
- Approval logged to audit trail

### Payment Risk Intervention
Proactive outreach to at-risk customers:
- Identifies payment delays early
- Suggests payment plans
- Offers support resources
- Tracks intervention outcomes

---

## Configuration

### Environment Variables

```bash
# Lead Scoring
LEAD_SCORE_WEIGHTS="engagement:0.3,fraud:0.2,ltv:0.3,recency:0.2"

# Notifications
NOTIFICATION_CHANNELS="email,sms,push"
NOTIFICATION_TEMPLATE_DIR=data/templates/

# Identity Gating
IDENTITY_VERIFICATION_REQUIRED=true
IDENTITY_EXPIRY_DAYS=730              # 2 years

# Campaign Approval
CAMPAIGN_APPROVAL_THRESHOLD=100       # Customers
CAMPAIGN_REACH_THRESHOLD=1000         # Total reach

# Payment Risk
PAYMENT_RISK_THRESHOLD=0.7
PAYMENT_DELAY_DAYS=30
```

### Notification Templates

Create templates in `data/templates/`:
- `email_offer.html` - Email template
- `sms_offer.txt` - SMS template
- `push_offer.txt` - Push notification template

Variables available:
- `{customer_name}`
- `{product_name}`
- `{offer_value}`
- `{expiry_date}`

---

## Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Lead scoring (100 customers) | <500ms | Multi-factor calculation |
| Customer enrichment (1 customer) | ~1-2s | External API calls |
| NBA recommendation | <200ms | Rule-based |
| Consent check | <50ms | Database lookup |
| Identity gate check | <50ms | Database lookup |
| Bulk campaign (1,000 customers) | ~5s | Batch processing |
| Payment risk scan (10,000 customers) | ~10s | Batch scoring |

---

## Troubleshooting

### "Notification not sent"
**Cause**: Customer doesn't have consent for that channel.

**Solution**: Check consent flags in customer profile. Verify `NOTIFICATION_CHANNELS` config.

### "Identity gate blocking legitimate action"
**Cause**: Customer's identity verification expired.

**Solution**: Send identity renewal reminder. Customer must re-verify before action proceeds.

### "Campaign approval stuck"
**Cause**: Approval gate triggered but no approver available.

**Solution**: Set `CAMPAIGN_APPROVAL_THRESHOLD` higher or assign approvers in config.

### "Lead scores all the same"
**Cause**: Weights not configured or data missing.

**Solution**: Check `LEAD_SCORE_WEIGHTS` config. Verify engagement/fraud/LTV data exists.

### "Enrichment API timeout"
**Cause**: External API slow or unavailable.

**Solution**: Increase timeout in config or use cached enrichment data.

---

## API Reference

### Lead Scoring

```python
from src.tools.leads import score_leads

scores = score_leads(customer_ids=["CUST-001", "CUST-002"])
# Returns: [{customer_id, score, factors, rank}, ...]
```

### Customer Enrichment

```python
from src.tools.customer import enrich_customer

enriched = enrich_customer("CUST-001")
# Returns: {credit_score, business_type, location, risk_level}
```

### Next-Best-Action

```python
from src.tools.functional import get_next_best_action

nba = get_next_best_action("CUST-001")
# Returns: {product_id, offer_value, confidence, reasoning}
```

### Recommendations

```python
from src.tools.recommender import (
    get_upsell_recommendations,
    get_user_based_recommendations,
    get_collaborative_recommendations
)

upsell = get_upsell_recommendations("CUST-001", top_k=5)
user_based = get_user_based_recommendations("CUST-001", top_k=5)
collab = get_collaborative_recommendations("CUST-001", top_k=5)
```

### Notifications

```python
from src.tools.functional import send_notification

result = send_notification(
    customer_id="CUST-001",
    channel="email",
    template="offer",
    variables={"product_name": "Premium Card"}
)
# Returns: {sent, channel, timestamp, audit_id}
```

### Identity Gating

```python
from src.tools.functional import check_identity_gate

gate = check_identity_gate("CUST-001")
# Returns: {passed, status, expiry_date, days_remaining}
```

### Campaign Execution

```python
from src.tools.functional import execute_campaign

campaign = execute_campaign(
    segment="high_value",
    action="send_offer",
    offer_id="PROMO-001",
    dry_run=False
)
# Returns: {executed, count, approval_required, audit_id}
```

### Payment Risk Intervention

```python
from src.tools.functional import identify_payment_risk

at_risk = identify_payment_risk()
# Returns: [{customer_id, risk_score, days_overdue, recommended_action}, ...]
```

---

## Testing

### Unit Tests

```bash
pytest tests/test_tools.py::test_lead_scoring -v
pytest tests/test_tools.py::test_notifications -v
pytest tests/test_tools.py::test_identity_gate -v
```

### Integration Tests

```bash
python -m pytest tests/test_graph.py::test_level3 -v
```

### Notebook Tests

Run all cells in `notebooks/level3_functional_agent.ipynb`

---

## Deployment

### Production Checklist

- [ ] Configure lead scoring weights
- [ ] Set up notification templates
- [ ] Configure identity verification requirements
- [ ] Set approval thresholds
- [ ] Test consent checking with production data
- [ ] Test identity gating with expired customers
- [ ] Test campaign approval workflow
- [ ] Set up payment risk monitoring
- [ ] Configure audit trail retention
- [ ] Test guardrails

### Scaling Considerations

- Batch lead scoring for large customer bases
- Cache enrichment data (credit scores, location)
- Use async notification delivery
- Implement rate limiting for external APIs
- Monitor approval queue for bottlenecks
- Use read replicas for customer lookups

---

## Resources

- `notebooks/level3_functional_agent.ipynb` - Interactive demo
- `tests/test_tools.py` - Feature tests
- `specs/03-level3-functional/` - Detailed specifications
- `data/audit.jsonl` - Audit trail log

---

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review test output: `pytest tests/test_tools.py -v`
3. Check logs in `data/audit.jsonl`
4. Review Langfuse traces (if enabled)

---

**Last Updated**: 2026-03-12  
**Version**: 1.0  
**Status**: Production Ready
