# Get Started

This guide takes you from a fresh clone to a running system. End-to-end setup takes about 10 minutes.

---

## Prerequisites

- Python 3.10+
- Git
- One of: an OpenAI API key, a running [Ollama](https://ollama.com) instance, or a GPTec endpoint
- Docker (optional — only needed for Langfuse observability)

---

## 1. Clone and create a virtual environment

```bash
git clone <repo-url>
cd agenticAI

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
                                # Note: if activation is unsupported in your shell,
                                # use venv/bin/python and venv/bin/pip directly
pip install -r requirements.txt
```

---

## 2. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and set your LLM provider. Pick one:

**Option A — OpenAI (default)**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=<your-key>
OPENAI_MODEL=gpt-4o-mini
```

**Option B — Ollama (fully local, no API key)**
```bash
# Install Ollama from https://ollama.com, then:
ollama pull llama3

LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

**Option C — GPTec / custom OpenAI-compatible endpoint**
```bash
LLM_PROVIDER=gptec
GPTEC_API_URL=https://your-host/v1
GPTEC_API_KEY=<your-key>
GPTEC_MODEL=<model-name>
```

The rest of the `.env` defaults (SQLite, ChromaDB paths, thresholds) work out of the box — no changes needed for local development.

---

## 3. Generate synthetic data

```bash
python scripts/cust_dataset_generator.py --output data/customers.json --count 100
```

This creates 100 synthetic customer records in `data/customers.json` conforming to the shared schema.

**Generate Level 2 sample data** (sales, social, support):
```bash
python scripts/generate_customer360_data.py
```

This creates:
- `data/sales_transactions.json` — 898 sales transactions across 5 channels
- `data/social_media.json` — ~79 social media posts with sentiment labels
- `data/support_tickets.json` — ~200 support tickets with resolution times

---

## 4. Seed the SQLite database

The analytics agent queries customers via SQL. Load the JSON into SQLite:

```python
# run once from the project root
import json, sqlite3, pathlib

records = json.loads(pathlib.Path("data/customers.json").read_text())
con = sqlite3.connect("data/customers.db")
con.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        customer_id TEXT PRIMARY KEY,
        full_name TEXT, segment TEXT, kyc_status TEXT,
        risk_score REAL, engagement_score REAL,
        account_balance REAL, payment_delay_risk REAL,
        country TEXT, preferred_language TEXT
    )
""")
con.executemany(
    "INSERT OR REPLACE INTO customers VALUES (?,?,?,?,?,?,?,?,?,?)",
    [(r["customer_id"], r["full_name"], r["segment"], r["kyc_status"],
      r["risk_score"], r["engagement_score"], r["account_balance"],
      r["payment_delay_risk"], r["country"], r["preferred_language"])
     for r in records]
)
con.commit(); con.close()
print("Database seeded.")
```

Or save the snippet as `scripts/seed_db.py` and run `python scripts/seed_db.py`.

---

## 5. Run the test suite

Verify everything is wired up correctly before running the system:

```bash
PYTHONPATH=. venv/bin/pytest --tb=short -q
```

Expected output: `64 passed`. No API key is required — all LLM calls are mocked in tests.

---

## 6. Run the graph

Invoke the system from a Python shell or script:

```python
from nonagentic.graph import graph
from nonagentic.state import new_state

state = new_state("What is the KYC status of customer CUST-001?", user_id="analyst@bank.com")
result = graph.invoke(state, config={"configurable": {"thread_id": state["request_id"]}})

print(result["result"])
print(result["audit_trail"])
```

The orchestrator classifies the intent and routes to the appropriate agent automatically.

### Example requests by intent

| Intent | Example request |
|--------|----------------|
| Informational | `"What is the identity verification status of customer CUST-001?"` |
| Analytical | `"Show me a segment breakdown of high-risk customers"` |
| Action | `"Send a retention offer to customer CUST-042"` |
| Strategic | `"Increase product adoption among low-engagement customers this quarter"` |

---

## 7. (Optional) Enable Langfuse observability

Langfuse gives you a local UI with traces, token usage, and latency per node.

**Start Langfuse with Docker:**
```bash
git clone https://github.com/langfuse/langfuse
cd langfuse
sudo docker-compose up -d
# UI available at http://localhost:3000
```

1. Open `http://localhost:3000`, create a project, and copy the public/secret keys.
2. Add to your `.env`:

```bash
LANGFUSE_PUBLIC_KEY=<your-public-key>
LANGFUSE_SECRET_KEY=<your-secret-key>
LANGFUSE_HOST=http://localhost:3000
LANGFUSE_PROJECT=agenticAI
```

3. Run the graph again — traces will appear in the Langfuse UI under the `agenticAI` project.

To also print events to stdout during development:
```bash
OBSERVABILITY_VERBOSE=1
```

---

## 8. (Optional) Ingest policy documents into ChromaDB

The Level-1 knowledge agent searches policy documents via vector similarity. To populate it:

```bash
python scripts/ingest_folder.py --folder data/docs
```

Or programmatically:
```python
from nonagentic.tools.knowledge import ingest_documents

ingest_documents([
    {"id": "doc-001", "text": "KYC must be renewed every 2 years...", "source": "kyc-policy.pdf", "doc_type": "kyc"},
    {"id": "doc-002", "text": "Customers with risk score > 0.8 require manual review...", "source": "risk-policy.pdf", "doc_type": "risk"},
])
```

Documents are persisted to `data/chroma/` and survive restarts.

---

## 9. Explore Interactive Notebooks

**Level 1 - Knowledge Retrieval**:
```bash
jupyter notebook notebooks/nonagent/01_level1_knowledge_retrieval.ipynb
```
- Customer profile lookup
- KYC status checks
- Email and CRM notes search
- Policy document search

**Level 2 - Analytics**:
```bash
jupyter notebook notebooks/nonagent/02_level2_analytics.ipynb
```
- K-means customer segmentation
- SQL analytics
- Risk analysis
- Sentiment analysis (requires transformers)
- Text summarization (requires transformers)
- Customer 360 view
- Sales and support analytics

**Level 3 - Functional Agent**:
```bash
jupyter notebook notebooks/level3_functional_agent.ipynb
```
- Lead scoring — multi-factor prospect ranking
- Customer enrichment — credit bureau, business registry, location
- Next-Best-Action (NBA) recommendation with cross-sell rules
- **Upsell recommendations** — higher-tier products based on purchase categories
- **User-based recommendations** — segment peer behavior analysis
- **Collaborative filtering** — cross-customer similarity recommendations
- Consent-gated notifications
- Identity gate — block actions, open remediation cases
- Bulk campaign targeting with approval gates
- Payment risk intervention
- Campaign results dashboard

**Quick Test Level 2**:
```bash
pytest tests/test_analytics.py -v
```

---

## Project structure

```
src/
  graph.py          # build_graph() — assembles all 7 nodes
  orchestrator.py   # intent classification + routing
  state.py          # AgentState TypedDict + new_state() factory
  llm.py            # universal LLM factory (openai / ollama / gptec)
  config.py         # load_config() — all thresholds from env vars
  guardrails.py     # guardrail_check() — PII redaction + principle check
  observability.py  # @node_trace decorator + Langfuse integration
  agents/           # level1.py  level2.py  level3.py  level4.py
  tools/            # one file per tool group
data/
  customers.json    # synthetic dataset (generated in step 3)
  customers.db      # SQLite (seeded in step 4)
  chroma/           # ChromaDB vector store
  audit.jsonl       # append-only audit log
  campaign_outcomes.jsonl
scripts/
  cust_dataset_generator.py
docs/
  developer/        # architecture, tool definitions, LangGraph design
  business/
  technical-non-dev/
specs/              # OpenSpec per agent + shared schema
```

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'src'`**
Always run from the project root with `PYTHONPATH=.`:
```bash
PYTHONPATH=. python your_script.py
```

**LLM calls fail / timeout**
All agents fall back to rule-based logic when the LLM is unavailable. Check `LLM_PROVIDER` and credentials in `.env`. Use `LLM_PROVIDER=ollama` for fully offline operation.

**ChromaDB returns empty results**
The vector store starts empty. Run the `ingest_documents` snippet in step 8 to populate it.

**`GUARDRAIL_ENABLED=true` is slow in tests**
Set `GUARDRAIL_ENABLED=false` in your test environment to skip the LLM constitutional check. The pytest suite does this automatically via `conftest.py`.
