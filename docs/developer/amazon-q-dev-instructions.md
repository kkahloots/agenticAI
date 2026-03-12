# 🧑‍💻 Amazon Q `/dev` Implementation Guide

**TL;DR**: Copy-paste these `/dev` prompts into Amazon Q chat to scaffold and implement each layer. Run them in order.

---

## Prerequisites

```bash
python -m venv venv && source venv/bin/activate
pip install langgraph langchain langchain-openai langchain-community \
            sqlalchemy chromadb faker pytest pytest-asyncio python-dotenv \
            langfuse pypdf python-docx pandas matplotlib \
            scikit-learn numpy transformers torch sentencepiece

# Optional — only needed for Ollama provider
pip install langchain-ollama
```

## LLM Provider Setup

Copy `.env.example` to `.env` and set `LLM_PROVIDER` to one of:

**OpenAI (default)**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=<your-key>
OPENAI_MODEL=gpt-4o-mini
```

**Ollama (local — no API key needed)**
```bash
# 1. Install Ollama: https://ollama.com
# 2. Pull a model: ollama pull llama3
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

**GPTec / custom OpenAI-compatible endpoint**
```bash
LLM_PROVIDER=gptec
GPTEC_API_URL=https://your-gptec-host/v1
GPTEC_API_KEY=<your-key>
GPTEC_MODEL=your-model-name
```

The factory at `src/llm.py` handles all three. No code changes needed to switch.

---

## Prompt 1 — Scaffold Repo

```
/dev Create a Python project scaffold for a 4-level LangGraph multi-agent system.

Structure:
- src/orchestrator.py       — routing node
- src/agents/level1.py      — RAG knowledge agent
- src/agents/level2.py      — analytics/text-to-SQL agent
- src/agents/level3.py      — functional tool-using agent
- src/agents/level4.py      — strategic multi-agent orchestrator
- src/tools/                — one file per tool (12 tools total)
- src/state.py              — AgentState TypedDict
- src/graph.py              — LangGraph graph assembly
- tests/                    — pytest test stubs
- requirements.txt

Use LangGraph StateGraph. Each agent is a node function: (state: AgentState) -> AgentState.
```

---

## Prompt 2 — Implement Orchestrator

```
/dev Implement src/orchestrator.py using the spec in specs/00-orchestrator/.

Requirements:
- Classify intent into: informational | analytical | action | strategic
- Use get_llm() from src/llm.py — NOT ChatOpenAI directly
- Return routing decision + confidence score (0–1)
- If confidence < 0.6, route to human_approval node
- Fall back to rule-based classification if LLM is unavailable
- Call log_audit_event after every routing decision
- Handle: null input, missing customer_id, unknown intent

Reference: docs/developer/langgraph-architecture.md router logic section.
Reference: src/llm.py for the universal LLM factory.
```

---

## Prompt 3 — Implement Level 1 RAG Agent

```
/dev Implement src/agents/level1.py using the spec in specs/01-level1-knowledge/.

Requirements:
- Use LangChain MultiQueryRetriever with local ChromaDB (three collections: policy_docs, emails, notes)
- Tools: search_customer_profile, search_policy_docs, get_kyc_status, multi_query_search
- Route by intent: email queries → emails collection, CRM note queries → notes collection, policy/compliance → policy_docs
- After retrieval, synthesise a grounded answer via LLM RAG generation with source citations
- Mask PII fields (full_name, email, phone) in all outputs
- Run guardrail_check on every output before returning
- Max 5 document chunks per query
- Handle: no results found, confidential field access, large document truncation

Reference: docs/developer/agent-tool-definitions.md for tool contracts.
Reference: src/tools/knowledge.py for collection routing logic.
```

---

## Prompt 4 — Implement Level 2 Text-to-SQL Agent

```
/dev Implement src/agents/level2.py using the spec in specs/02-level2-analytics/.

Requirements:
- Use LangChain create_sql_query_chain with read-only SQLAlchemy connection
- Tools: run_sql_query, generate_segment
- Validate SQL before execution: reject any INSERT/UPDATE/DELETE/DROP
- Limit results to 10,000 rows; warn user if truncated
- For segmentation: support kmeans (sklearn) and rule-based fallback
- Human must review output before any downstream action is triggered
- Handle: schema mismatch, query timeout (30 s), insufficient data (< 10 rows)

Reference: specs/shared/customer-schema.md for column names.
```

---

## Prompt 5 — Implement Level 3 Functional Agent

```
/dev Implement src/agents/level3.py using the spec in specs/03-level3-functional/.

Requirements:
- Tools: search_customer_profile, get_kyc_status, recommend_offer, draft_email,
         send_notification, create_case, log_audit_event, request_human_approval
- Before send_notification: check consent_flags; block if marketing=false
- Before any action on expired KYC customer: create_case(type="kyc_remediation") first
- Trigger request_human_approval if action affects > 100 customers or risk_score > 0.8
- All actions must be logged via log_audit_event
- Handle: customer opt-out, API failure (retry + escalate), fraud flag (pause + compliance)

Reference: docs/developer/agent-tool-definitions.md for all tool contracts.
```

---

## Prompt 6 — Implement Level 4 Strategic Agent

```
/dev Implement src/agents/level4.py using the spec in specs/04-level4-strategic/.

Requirements:
- Accept a high-level goal string (e.g. "Increase Visa Gold adoption by 5%")
- Decompose into sub-goals using LLM planning prompt
- Assign sub-goals to level2 (segmentation) and level3 (execution) nodes
- Tools: generate_segment, recommend_offer, schedule_campaign, request_human_approval
- Monitor sub-goal completion; adjust if KPI deviates > 10% from target
- Require human approval before schedule_campaign if reach > 1000
- Handle: conflicting goals (surface to human), data drift (re-segment), budget exceeded (pause)

Reference: docs/developer/langgraph-architecture.md graph edges section.
```

---

## Prompt 7 — Assemble LangGraph and Add Tests

```
/dev Implement src/graph.py to assemble the full LangGraph StateGraph.

Requirements:
- Nodes: orchestrator, level1_knowledge, level2_analytics, level3_functional,
         level4_strategic, human_approval, error_handler
- Edges as defined in docs/developer/langgraph-architecture.md
- Compile graph with checkpointer (MemorySaver for dev, PostgresSaver for prod)
- Add interrupt_before=["human_approval"] for approval checkpoints

Then in tests/, write pytest tests for:
- Orchestrator routes "What is the KYC status of CUST-001?" → level1_knowledge
- Orchestrator routes "Segment customers by risk" → level2_analytics
- Level-3 blocks send_notification when consent_flags.marketing = false
- Level-3 triggers request_human_approval when action affects > 100 customers
- Full end-to-end: "Increase card adoption" → level4_strategic → sub-goals → END
```

---

## Prompt 8 — Upgrade Fake Data Generator

```
/dev Upgrade scripts/cust_dataset_generator.py to match specs/shared/cust-data-rules.md.

New requirements:
- Add fields: preferred_language, segment, kyc_expiry_date, country, engagement_score,
              product_holdings, account_balance, consent_flags, last_interaction_date,
              payment_delay_risk, offer_eligibility, campaign_history
- KYC distribution: 60% valid, 30% expired, 10% pending
- Segment distribution: 15% high-value-low-engagement, 20% at-risk, 15% new,
                        20% low-engagement, 30% high-value
- Multilingual names: ~34% EN (Faker en_US), ~33% HU (Faker hu_HU), ~33% AR (Faker ar_AA)
- ~10% null email, ~5% duplicate phone, ~15% consent_flags.marketing=false
- payment_delay_risk: 0.0–0.4 for valid KYC; 0.5–1.0 for expired KYC
- Keep CLI: --output and --count flags
```

---

## Prompt 9 — Add README

```
/dev Update README.md for the agenticAI project.

Include:
- Project overview: 4-level agentic AI system for customer operations
- Folder structure tree
- Quick start: venv setup, pip install, generate fake data, run graph
- How to use each /dev prompt (reference this file)
- How to run tests: pytest tests/
- How to generate the zip: zip -r agentic-specs-v1.zip . --exclude "venv/*" "data/*" "__pycache__/*"
- Links to key docs: langgraph-architecture.md, agent-tool-definitions.md, plan.md
- Non-functional notes: audit trail, PII masking, human approval, cost awareness
```

---

## Utility Commands

```bash
# Generate fake data
python scripts/cust_dataset_generator.py --output data/customers.json --count 100

# Generate and ingest documents (emails, notes, policies)
python scripts/generate_docs.py
PYTHONPATH=. python scripts/ingest_folder.py

# Run tests
PYTHONPATH=. pytest tests/ -v

# Package everything
zip -r agentic-specs-v1.zip . \
  --exclude "venv/*" "data/*" "__pycache__/*" "*.pyc" ".git/*"
```
