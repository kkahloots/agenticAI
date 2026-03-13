# LangGraph Workflow Specification

## Overview

The agentic system uses LangGraph to define a stateful, conditional execution graph. The graph manages agent routing, state transitions, and evaluation loops.

## Implementation

- **File**: `graphs/agent_workflow_graph.py`
- **Graph instance**: `agentic_graph = build_agentic_graph()`
- **State type**: `AgenticState` (TypedDict from `agentic/agentic_state.py`)
- **Checkpointer**: `MemorySaver` (in-process LangGraph checkpointing)

---

## Graph Structure

```
                    ┌─────────────────┐
                    │   orchestrator  │  ← entry point
                    └────────┬────────┘
                             │ route_to_agent()
          ┌──────────────────┼──────────────────────┐
          │                  │                       │
          ▼                  ▼                       ▼
  knowledge_agent   analytics_agent   recommendation_agent
          │                  │                       │
          └──────────────────┼───────────────────────┘
                             │ should_evaluate()
                    ┌────────┴────────┐
                    │                 │
                    ▼                 ▼
           evaluation_agent          END

  workflow_agent ──┐
                   ├── should_evaluate() ──► evaluation_agent ──► END
  action_agent ───┘                    └──► END

  human_approval ──► after_approval_route() ──► (same agents as orchestrator)

  error_handler ──► END
```

---

## Nodes

| Node | Function | Description |
|------|----------|-------------|
| `orchestrator` | `orchestrator_agent` | Entry point; classifies intent and routes |
| `knowledge_agent` | `knowledge_agent` | Information retrieval |
| `analytics_agent` | `analytics_agent` | Data analysis and SQL |
| `recommendation_agent` | `recommendation_agent` | ML recommendations |
| `workflow_agent` | `workflow_agent` | Multi-step workflow execution |
| `action_agent` | `action_agent` | CRM and notification actions |
| `evaluation_agent` | `evaluation_agent` | Outcome evaluation |
| `memory_agent` | `memory_agent` | Memory management |
| `human_approval` | `human_approval_node` | Human-in-the-loop approval |
| `error_handler` | `error_handler_node` | Error handling and reporting |

---

## Routing Functions

### `route_to_agent(state) -> str`
Called after `orchestrator`. Maps `state["intent"]` to a node name.

```python
intent_to_agent = {
    "knowledge":       "knowledge_agent",
    "analytics":       "analytics_agent",
    "recommendation":  "recommendation_agent",
    "workflow":        "workflow_agent",
    "action":          "action_agent",
}
```

Special cases:
- `state["error"]` is set → `"error_handler"`
- `state["confidence"] < 0.6` → `"human_approval"`
- Unknown intent → `"knowledge_agent"` (default)

---

### `should_evaluate(state) -> str`
Called after each primary agent. Determines whether to run evaluation.

```python
if state["active_agent"] in ["workflow", "action"]:
    return "evaluation_agent"
return END
```

`knowledge_agent`, `analytics_agent`, and `recommendation_agent` route directly to `END` (no evaluation step).

---

### `after_approval_route(state) -> str`
Called after `human_approval`. Re-runs `route_to_agent` with updated confidence.

- If `state["error"]` → `"error_handler"`
- Otherwise → same routing as `route_to_agent`

---

## Special Nodes

### `human_approval_node`
Invokes `nonagentic.tools.approval.request_human_approval`.

- **Approved**: sets `confidence = 0.9`, appends audit entry
- **Rejected**: sets `error = "Request rejected by human approver"`

### `error_handler_node`
Reads `state["error"]`, returns a structured error response with an `AIMessage`.

---

## State Contract

The graph uses `AgenticState` (TypedDict). Key fields written by the graph infrastructure:

| Field | Written by | Purpose |
|-------|-----------|---------|
| `intent` | orchestrator | Drives routing |
| `confidence` | orchestrator | Triggers human_approval if < 0.6 |
| `active_agent` | each agent | Drives `should_evaluate` |
| `error` | any agent | Triggers error_handler |
| `should_replan` | evaluation_agent | Reserved for future replanning loop |
| `agent_history` | each agent | Accumulated execution path |
| `audit_trail` | each agent | Accumulated audit entries |
| `mcp_calls` | each agent | Accumulated MCP call records |

---

## Checkpointing

The graph uses `MemorySaver` by default. This provides:
- State persistence across `graph.stream()` steps within a single process
- Thread-level isolation via `config["configurable"]["thread_id"]`

```python
config = {"configurable": {"thread_id": state["request_id"]}}
result = agentic_graph.invoke(state, config=config)
```

---

## Invocation

### Standard invocation
```python
from agentic.agentic_state import new_agentic_state
from graphs.agent_workflow_graph import agentic_graph

state = new_agentic_state("What is the profile for CUST-001?", customer_id="CUST-001")
config = {"configurable": {"thread_id": state["request_id"]}}
result = agentic_graph.invoke(state, config=config)

print(result["final_result"])
print(result["agent_history"])   # e.g. ["orchestrator", "knowledge"]
print(result["mcp_calls"])
```

### Streaming invocation
```python
for step in agentic_graph.stream(state, config=config):
    node_name = list(step.keys())[0]
    node_output = step[node_name]
    print(f"[{node_name}] active_agent={node_output.get('active_agent')}")
```

---

## Execution Paths by Intent

| Intent | Path |
|--------|------|
| `knowledge` | orchestrator → knowledge_agent → END |
| `analytics` | orchestrator → analytics_agent → END |
| `recommendation` | orchestrator → recommendation_agent → END |
| `workflow` | orchestrator → workflow_agent → evaluation_agent → END |
| `action` | orchestrator → action_agent → evaluation_agent → END |
| low confidence | orchestrator → human_approval → (agent) → END |
| error | orchestrator → error_handler → END |

---

## Building a Custom Graph

```python
from graphs.agent_workflow_graph import build_agentic_graph
from langgraph.checkpoint.memory import MemorySaver

# Default (MemorySaver)
graph = build_agentic_graph()

# Custom checkpointer
graph = build_agentic_graph(checkpointer=MemorySaver())
```

---

## Adding a New Agent Node

1. Implement the agent function in `agentic/`
2. Import it in `graphs/agent_workflow_graph.py`
3. Add `builder.add_node("your_agent", your_agent_fn)`
4. Add the node name to `route_to_agent` mapping
5. Add edges: `builder.add_conditional_edges("your_agent", should_evaluate, {...})`
6. Register the agent in `agentic/agent_registry.py`
