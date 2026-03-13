# Agentic AI System – Developer Guide

## Quick Start

```python
from agentic.agentic_state import new_agentic_state
from graphs.agent_workflow_graph import agentic_graph

state = new_agentic_state(
    "What is the KYC status of CUST-001?",
    user_id="analyst@bank.com",
    session_id="session-abc"
)
config = {"configurable": {"thread_id": state["request_id"]}}
result = agentic_graph.invoke(state, config=config)

print(result["final_result"])
print(result["messages"][-1].content)
print(result["audit_trail"])
```

## Project Layout

```
agentic/
  agentic_state.py        # AgenticState TypedDict + new_agentic_state()
  orchestrator_agent.py   # classify_intent(), route_to_agent(), orchestrator_agent()
  knowledge_agent.py      # knowledge_agent()
  analytics_agent.py      # analytics_agent()
  recommendation_agent.py # recommendation_agent()
  other_agents.py         # workflow_agent(), action_agent(), evaluation_agent(), memory_agent()
  agent_registry.py       # AGENTIC_REGISTRY — AgenticAgentMeta dataclasses

mcp_servers/
  __init__.py             # MCPServer, MCPTool base classes
  customer_data_server.py # search_customer_profile, get_identity_status, get_kyc_status
  analytics_server.py     # run_sql_query, generate_segment
  recommendation_server.py# recommend_products, recommend_offer
  crm_server.py           # draft_email, send_notification, create_case, schedule_campaign
  product_catalog_server.py # get_products, get_product_by_id

memory/
  memory_manager.py       # ConversationMemory, UserProfileMemory, InteractionMemory,
                          # AgentObservationMemory + global memory_manager instance

graphs/
  agent_workflow_graph.py # build_agentic_graph(), agentic_graph (module-level instance)
```

## State Schema

`AgenticState` is a `TypedDict` defined in `agentic/agentic_state.py`. Append-only fields use `Annotated[list, _append]`; messages use `operator.add`.

```python
{
    # Identifiers
    "request_id": str,           # uuid4, set by new_agentic_state()
    "user_id": str,              # defaults to "system"
    "session_id": str,           # uuid4 if not provided

    # Request
    "original_request": str,
    "intent": str,               # knowledge | analytics | recommendation | workflow | action | unknown
    "confidence": float,         # 0.0–1.0; < 0.6 → human_approval node

    # Agent coordination
    "active_agent": str,
    "agent_plan": dict | None,   # {"agents": [...], "steps": [...], "mcp_servers": [...]}
    "agent_history": list[str],  # append-only

    # Memory context (loaded by orchestrator)
    "conversation_context": dict | None,
    "user_profile": dict | None,

    # Tool calls
    "mcp_calls": list[dict],     # append-only

    # Results
    "intermediate_results": list[dict],  # append-only
    "final_result": Any | None,

    # Messages
    "messages": list[BaseMessage],       # operator.add

    # Evaluation
    "evaluation": dict | None,
    "should_replan": bool,
    "replan_count": int,

    # Error
    "error": str | None,

    # Audit
    "audit_trail": list[dict],   # append-only
}
```

## Intent Classification

`orchestrator_agent.py` classifies intent in two stages:

1. **Pattern pre-classification** (`_pre_classify`) — catches SQL patterns and segmentation keywords before the LLM call (confidence 0.95).
2. **LLM classification** — sends request to `get_llm(temperature=0.0)` with a system prompt; parses JSON response.
3. **Rule-based fallback** (`_rule_based_classify`) — keyword matching if LLM fails (confidence 0.85).

Routing: `route_to_agent()` maps intent → graph node name. Confidence < 0.6 → `human_approval`.

## Graph Structure

Defined in `graphs/agent_workflow_graph.py`. Built with `StateGraph(AgenticState)`.

**Nodes** (10 total):
- `orchestrator` → `knowledge_agent` → `analytics_agent` → `recommendation_agent` → `workflow_agent` → `action_agent` → `evaluation_agent` → `memory_agent` → `human_approval` → `error_handler`

**Routing**:
- `orchestrator` → conditional edges via `route_to_agent()`
- `human_approval` → conditional edges via `after_approval_route()` (same logic as `route_to_agent`)
- Each agent → `should_evaluate()`: returns `evaluation_agent` if `active_agent` is `workflow` or `action`, else `END`
- `evaluation_agent` → `END`
- `error_handler` → `END`

**Checkpointer**: `MemorySaver` (in-process, per-thread state persistence).

## MCP Servers

All agents call tools via `server.invoke_tool(name, **kwargs)`. Never call underlying tool functions directly.

| Server | Class | Tools |
|--------|-------|-------|
| `customer_data_server.py` | `CustomerDataServer` | `search_customer_profile`, `get_identity_status`, `get_kyc_status` |
| `analytics_server.py` | `AnalyticsServer` | `run_sql_query`, `generate_segment` |
| `recommendation_server.py` | `RecommendationServer` | `recommend_products`, `recommend_offer` |
| `crm_server.py` | `CRMServer` | `draft_email`, `send_notification`, `create_case`, `schedule_campaign` |
| `product_catalog_server.py` | `ProductCatalogServer` | `get_products`, `get_product_by_id` |

All servers delegate to `nonagentic.tools.*` functions (except `ProductCatalogServer`, which reads `data/products.json` directly).

## Memory Layer

Global singleton `memory_manager` in `memory/memory_manager.py`. Four in-process stores — no external DB, no TTL, no thread safety.

```python
from memory.memory_manager import memory_manager

# Conversation (keyed by session_id)
memory_manager.conversation.add_message(session_id, "user", "Hello")
messages = memory_manager.conversation.get_conversation(session_id)

# User profile (keyed by user_id)
memory_manager.user_profile.update_preference(user_id, "language", "en")
profile = memory_manager.user_profile.get_profile(user_id)

# Interaction log (keyed by user_id)
memory_manager.interaction.record_interaction(user_id, "purchase", {"product_id": "P123"})
interactions = memory_manager.interaction.get_interactions(user_id)

# Agent observations (keyed by agent name)
memory_manager.agent_observation.record_observation("analytics", "High churn risk", {"segment": "vip"})
observations = memory_manager.agent_observation.get_observations("analytics")
```

## Writing a New Agent

```python
from langchain_core.messages import AIMessage
from agentic.agentic_state import AgenticState
from mcp_servers.your_server import YourServer
from memory.memory_manager import memory_manager
from nonagentic.tools.audit import log_audit_event

def your_agent(state: AgenticState) -> dict:
    request = state["original_request"]
    server = YourServer()
    result = server.invoke_tool("your_tool", param="value")

    memory_manager.interaction.record_interaction(
        state["user_id"], "your_action", {"result": result}
    )
    log_audit_event(
        "your_agent", "your_action", {"request": request}, {"result": result},
        user_id=state["user_id"], request_id=state["request_id"]
    )

    return {
        "active_agent": "your_agent",
        "agent_history": ["your_agent"],
        "mcp_calls": [{"server": "your_server", "tool": "your_tool", "result": result}],
        "final_result": result,
        "messages": [AIMessage(content=str(result))],
        "audit_trail": [{"agent": "your_agent", "action": "your_action"}],
    }
```

Then register in `agent_registry.py` and add a node + edges in `graphs/agent_workflow_graph.py`.

## Testing

```bash
# All tests
pytest tests/ -v

# Agentic tests only
pytest tests/test_agentic_state.py tests/test_memory_manager.py \
  tests/test_orchestrator_agent.py tests/test_agent_registry.py \
  tests/test_output_adapter.py tests/test_knowledge_agent.py \
  tests/test_analytics_agent.py tests/test_recommendation_agent.py -v

# With coverage
pytest tests/ --cov=agentic --cov=memory --cov-report=html
```

## Debugging

```python
# Stream step-by-step
for step in agentic_graph.stream(state, config=config):
    node_name = list(step.keys())[0]
    node_state = step[node_name]
    print(f"[{node_name}] active_agent={node_state.get('active_agent')}")
    if node_state.get("messages"):
        print(f"  → {node_state['messages'][-1].content[:120]}")

# Inspect audit trail
result = agentic_graph.invoke(state, config=config)
for entry in result["audit_trail"]:
    print(entry)
```

## Environment Variables

| Variable | Default | Used by |
|----------|---------|---------|
| `LLM_PROVIDER` | `openai` | `get_llm()` in orchestrator intent classification |
| `OPENAI_API_KEY` | — | OpenAI provider |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama provider |
| `DATABASE_URL` | `sqlite:///data/customers.db` | Analytics MCP server (SQL queries) |
| `GUARDRAILS_ENABLED` | `true` | Output validation |
| `AUTO_APPROVE_DEV` | `true` | Human approval node (auto-approves in dev) |

## References

- State schema: `agentic/agentic_state.py`
- Graph definition: `graphs/agent_workflow_graph.py`
- Agent registry: `agentic/agent_registry.py`
- Technical specs: `specs/agentic/`
