# Get Started — Agentic System

This guide covers setup and first run for the agentic system. For the nonagent pipeline, see `docs/nonagent/get-started.md`.

End-to-end setup takes about 10 minutes.

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

The rest of the `.env` defaults work out of the box for local development.

---

## 3. Generate synthetic data and seed the database

```bash
python scripts/cust_dataset_generator.py --output data/customers.json --count 100
```

Then seed SQLite (required for analytics agent SQL queries):

```bash
python scripts/seed_db.py
```

Or inline:

```python
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
```

---

## 4. Run the test suite

```bash
PYTHONPATH=. pytest tests/ --tb=short -q
```

Run agentic tests only:

```bash
PYTHONPATH=. pytest tests/test_agentic_state.py tests/test_memory_manager.py \
  tests/test_orchestrator_agent.py tests/test_agent_registry.py \
  tests/test_output_adapter.py tests/test_knowledge_agent.py \
  tests/test_analytics_agent.py tests/test_recommendation_agent.py -v
```

No API key required — all LLM calls are mocked in tests.

---

## 5. Run the agentic system

```python
from agentic.agentic_state import new_agentic_state
from graphs.agent_workflow_graph import agentic_graph

state = new_agentic_state(
    "What is the KYC status of CUST-001?",
    user_id="analyst@bank.com"
)
config = {"configurable": {"thread_id": state["request_id"]}}
result = agentic_graph.invoke(state, config=config)

print(result["messages"][-1].content)
print(result["agent_history"])
print(result["audit_trail"])
```

### Example requests by intent

| Intent | Example request |
|--------|----------------|
| `knowledge` | `"What is the identity verification status of CUST-001?"` |
| `analytics` | `"Segment customers by risk score"` |
| `analytics` | `"SELECT segment, COUNT(*) FROM customers GROUP BY segment"` |
| `recommendation` | `"Recommend products for CUST-042"` |
| `action` | `"Send a retention offer to CUST-042"` |
| `workflow` | `"Increase VIP customer engagement by 10%"` |

---

## 6. Stream step-by-step execution

```python
for step in agentic_graph.stream(state, config=config):
    node_name = list(step.keys())[0]
    node_state = step[node_name]
    print(f"[{node_name}]")
    if node_state.get("messages"):
        print(f"  {node_state['messages'][-1].content[:120]}")
```

---

## 7. (Optional) Enable Langfuse observability

```bash
git clone https://github.com/langfuse/langfuse
cd langfuse
sudo docker-compose up -d
# UI at http://localhost:3000
```

Add to `.env`:

```bash
LANGFUSE_PUBLIC_KEY=<your-public-key>
LANGFUSE_SECRET_KEY=<your-secret-key>
LANGFUSE_HOST=http://localhost:3000
```

---

## 8. (Optional) Ingest policy documents

The knowledge agent searches policy documents via vector similarity:

```bash
PYTHONPATH=. python scripts/ingest_folder.py --folder data/docs
```

---

## 9. Explore the comparison notebook

```bash
jupyter notebook notebooks/agentic/comparison.ipynb
```

Side-by-side comparison of nonagent pipeline vs agentic system on the same requests.

---

## Project structure (agentic components)

```
agentic/
  agentic_state.py        # AgenticState TypedDict + new_agentic_state()
  orchestrator_agent.py   # classify_intent(), route_to_agent()
  knowledge_agent.py
  analytics_agent.py
  recommendation_agent.py
  other_agents.py         # workflow, action, evaluation, memory agents
  agent_registry.py       # AGENTIC_REGISTRY

mcp_servers/
  customer_data_server.py
  analytics_server.py
  recommendation_server.py
  crm_server.py
  product_catalog_server.py

memory/
  memory_manager.py       # global memory_manager singleton

graphs/
  agent_workflow_graph.py # build_agentic_graph(), agentic_graph
```

---

## Troubleshooting

**`ModuleNotFoundError`**
Always run from the project root with `PYTHONPATH=.`:
```bash
PYTHONPATH=. python your_script.py
```

**LLM calls fail / timeout**
Orchestrator falls back to rule-based classification when LLM is unavailable. Check `LLM_PROVIDER` and credentials in `.env`. Use `LLM_PROVIDER=ollama` for fully offline operation.

**Recommendation agent returns error**
The recommendation agent requires a `CUST-XXXX` pattern in the request. Include the customer ID explicitly.

**Memory resets between runs**
Memory is in-process only (`MemorySaver`). It does not persist to disk — this is expected. For persistent memory, an external store would need to be wired in.

**`confidence < 0.6` routing to human approval in tests**
Set `AUTO_APPROVE_DEV=true` in `.env` to auto-approve in development. The test suite sets this automatically via `conftest.py`.
