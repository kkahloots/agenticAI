# 🔍 Level 1 — Knowledge & Retrieval Agent

**TL;DR**: The knowledge agent answers questions about customers, policies, and history by searching across customer databases, email archives, CRM notes, and policy documents — all in plain English, no SQL required.

---

## Business Use Cases

### 1. Customer Profile Lookup
A account manager needs a quick overview of a customer before a call — segment, fraud score, identity verification status, categories purchased.

**Trigger**: Any request containing "profile", "customer info", "show me", or "tell me about".

**Output**: Structured customer summary with segment, risk scores, purchase history, and consent flags.

---

### 2. Identity Verification Status Check
Trust & Safety needs to verify whether a customer's identity verification is valid before approving a high-value purchase or product application.

**Trigger**: Requests about "identity", "KYC", "verification", or "expiry".

**Output**: Current status (verified/unverified/pending), expiry date, days remaining, or expiry alert.

---

### 3. Email Correspondence Search
A customer calls claiming they never received a renewal reminder. The agent searches the email archive and surfaces relevant correspondence in seconds.

**Trigger**: Requests about "emails", "messages", "correspondence", or "what did we send".

**Output**: Ranked list of relevant emails with relevance scores, dates, and previews.

**Technology**: Semantic search using vector embeddings (ChromaDB).

---

### 4. CRM Agent Notes Search
A senior manager wants to understand the history of escalations and complaints before a customer review meeting. Instead of manually reading hundreds of CRM notes, the agent surfaces the most relevant ones.

**Trigger**: Requests about "notes", "history", "escalations", "complaints", or "retention".

**Output**: Ranked list of relevant notes with relevance scores, dates, and summaries.

**Technology**: Semantic search using vector embeddings (ChromaDB).

---

### 5. Policy Document Search (RAG)
A product manager needs to quickly check the eligibility rules for the Premium Membership promotion, or a trust & safety officer needs to verify the identity verification policy — without digging through PDF folders.

**Trigger**: Requests about "policy", "rules", "eligibility", "requirements", or "compliance".

**Output**: Synthesised answer with cited sources (Retrieval-Augmented Generation).

**Technology**: Vector search + LLM synthesis.

---

### 6. Cross-Source Search
A manager asks a broad question that spans multiple data sources — policies, emails, and notes. The agent searches all three collections simultaneously and synthesises a unified answer.

**Trigger**: Complex questions requiring multiple sources.

**Output**: Unified answer with source breakdown and relevance scores.

---

### 7. Audit Trail
Trust & Safety requires a full record of every data access — who queried what, when, and what was returned. The audit trail is immutable and written to `data/audit.jsonl`.

**Trigger**: Automatic on every Level 1 action.

**Output**: Immutable log entry with timestamp, user, action, and guardrail status.

---

### 8. Output Guardrails
Before any answer reaches a user, it passes through an automatic guardrail check. This protects against:
- **PII leakage** — email addresses and phone numbers are automatically redacted
- **Forbidden content** — phrases like "financial advice" or "buy shares" are blocked

**Trigger**: Automatic on every response.

**Output**: Sanitised response with violations logged to audit trail.

---

## Data Sources

| Source | What's stored | Search method |
|--------|---------------|---------------|
| **Customer DB** | Profiles, segments, risk scores, consent flags | SQL lookup |
| **Email Archive** | Sent emails, templates, correspondence | Vector search (ChromaDB) |
| **CRM Notes** | Agent notes, escalations, retention history | Vector search (ChromaDB) |
| **Policy Library** | Compliance docs, eligibility rules, procedures | Vector search (ChromaDB) |

---

## How It Works

```
Your question
     │
     ▼
Orchestrator classifies intent → routes to Level 1
     │
     ▼
Level 1 decides: customer lookup? Identity check? email search? policy search?
     │
     ▼
Retrieves relevant data from the right source
     │
     ▼
LLM synthesises a clear, cited answer
     │
     ▼
Guardrail checks output for PII leaks or policy violations
     │
     ▼
Answer returned + audit trail logged
```

---

## Architecture

```
Level 1 Agent (src/agents/level1.py)
│
├── Customer Lookup
│   ├── Profile retrieval (SQL)
│   ├── Identity verification status
│   └── Consent flags
│
├── Email Search
│   ├── Vector embedding (ChromaDB)
│   ├── Semantic similarity ranking
│   └── Result synthesis
│
├── CRM Notes Search
│   ├── Vector embedding (ChromaDB)
│   ├── Semantic similarity ranking
│   └── Result synthesis
│
├── Policy Search (RAG)
│   ├── Vector embedding (ChromaDB)
│   ├── Retrieval-Augmented Generation
│   └── Citation tracking
│
└── Guardrails
    ├── PII redaction (email, phone)
    ├── Forbidden content blocking
    └── Audit logging
```

---

## Key Features

### Semantic Search
Instead of keyword matching, the agent understands meaning. So "renewal reminder" will match emails about "identity verification expiry notice" even if the exact words differ.

### Multi-Collection Search
One question can search across customer data, emails, notes, and policies simultaneously, returning a unified answer.

### Retrieval-Augmented Generation (RAG)
For policy questions, the agent:
1. Searches the policy library for relevant sections
2. Passes those sections to the LLM
3. Returns a synthesised, cited answer — not just a raw document dump

### Automatic Guardrails
Every response is checked for:
- **PII leakage** — email addresses, phone numbers, names
- **Forbidden content** — financial advice, investment recommendations
- **Policy violations** — compliance breaches

Violations are logged but don't block the response (configurable).

### Immutable Audit Trail
Every action is logged to `data/audit.jsonl`:
- Timestamp
- User ID
- Action (customer lookup, email search, etc.)
- Customer ID (if applicable)
- Guardrail status
- Violations (if any)

---

## Configuration

### Environment Variables

```bash
# Guardrails
GUARDRAIL_ENABLED=true              # Enable PII redaction
GUARDRAIL_BLOCK_ON_VIOLATION=false  # Block response or just log

# Vector Search
CHROMA_COLLECTION_EMAILS=emails
CHROMA_COLLECTION_NOTES=notes
CHROMA_COLLECTION_POLICIES=policies

# Audit Trail
AUDIT_LOG_PATH=data/audit.jsonl
AUDIT_RETENTION_DAYS=2555           # 7 years
```

### Adding New Documents

1. Place documents in `data/docs/` (emails, notes, policies)
2. Run the ingestion script:
   ```bash
   python scripts/ingest_folder.py data/docs/
   ```
3. Documents are immediately searchable

---

## Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Customer profile lookup | <100ms | SQL query |
| Email search (100 emails) | ~500ms | Vector search + ranking |
| CRM notes search (500 notes) | ~1s | Vector search + ranking |
| Policy search (50 policies) | ~500ms | Vector search + RAG |
| Cross-source search | ~2s | All sources in parallel |

---

## Troubleshooting

### "Customer not found"
**Cause**: Customer ID doesn't exist in database.

**Solution**: Verify customer ID format (e.g., CUST-001).

### "No emails found"
**Cause**: Email archive not ingested or search term too specific.

**Solution**: Run `python scripts/ingest_folder.py data/docs/emails/` to ingest emails.

### "PII redaction too aggressive"
**Cause**: Guardrail blocking legitimate content.

**Solution**: Set `GUARDRAIL_BLOCK_ON_VIOLATION=false` to log only, or adjust patterns in `src/core/guardrails.py`.

### "Audit trail not writing"
**Cause**: File permissions or path issue.

**Solution**: Ensure `data/` directory exists and is writable: `mkdir -p data && chmod 755 data`.

---

## API Reference

### Customer Lookup

```python
from src.tools.customer import get_customer_profile

profile = get_customer_profile("CUST-001")
# Returns: {id, name, segment, fraud_score, identity_status, categories, consent}
```

### Email Search

```python
from src.tools.knowledge import search_emails

results = search_emails("renewal reminder", top_k=5)
# Returns: [{source, relevance, date, preview}, ...]
```

### CRM Notes Search

```python
from src.tools.knowledge import search_notes

results = search_notes("escalation", top_k=5)
# Returns: [{source, relevance, date, preview}, ...]
```

### Policy Search (RAG)

```python
from src.tools.knowledge import search_policies

answer = search_policies("What is the identity verification renewal policy?")
# Returns: {answer, sources, citations}
```

### Audit Trail

```python
from src.core.observability import log_audit

log_audit(
    agent_id="level1_knowledge",
    action="customer_lookup",
    customer_id="CUST-001",
    user_id="manager@shop.com",
    guardrail_passed=True,
    violations=[]
)
```

---

## Testing

### Unit Tests

```bash
pytest tests/test_tools.py::test_customer_lookup -v
pytest tests/test_tools.py::test_email_search -v
pytest tests/test_tools.py::test_policy_search -v
```

### Integration Tests

```bash
python -m pytest tests/test_graph.py -v
```

### Notebook Tests

Run all cells in `notebooks/level1_knowledge_agent.ipynb`

---

## Deployment

### Production Checklist

- [ ] Ingest all documents: `python scripts/ingest_folder.py data/docs/`
- [ ] Configure guardrails: `GUARDRAIL_ENABLED=true`
- [ ] Set audit trail path: `AUDIT_LOG_PATH=data/audit.jsonl`
- [ ] Test customer lookup with production data
- [ ] Test email/notes search with sample queries
- [ ] Verify PII redaction works
- [ ] Set up audit log rotation (7-year retention)
- [ ] Monitor Langfuse traces (if enabled)

### Scaling Considerations

- Cache frequently accessed customer profiles
- Use read replicas for customer database queries
- Batch vector search requests
- Implement rate limiting per user
- Monitor ChromaDB memory usage

---

## Resources

- `notebooks/level1_knowledge_agent.ipynb` - Interactive demo
- `tests/test_tools.py` - Feature tests
- `specs/01-level1-knowledge/` - Detailed specifications
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
