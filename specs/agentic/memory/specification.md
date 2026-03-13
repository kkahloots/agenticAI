# Memory Layer Specification

## Overview

The memory layer provides persistent, multi-type storage for the agentic system. It is implemented as a single in-process `MemoryManager` instance shared across all agents within a session.

## Implementation

- **File**: `memory/memory_manager.py`
- **Global instance**: `from memory.memory_manager import memory_manager`
- **Scope**: In-process (resets on restart; no external DB)

---

## Memory Types

### 1. ConversationMemory

Short-term chat history keyed by `session_id`.

| Method | Signature | Description |
|--------|-----------|-------------|
| `add_message` | `(session_id, role, content)` | Append a message to the session |
| `get_conversation` | `(session_id) -> list[dict]` | Return all messages for the session |

**Storage key**: `conv:{session_id}`

**Message schema**:
```python
{
    "role": "user" | "assistant",
    "content": str,
    "timestamp": ISO8601
}
```

**Used by**: orchestrator_agent (load), knowledge_agent (write), analytics_agent (write), recommendation_agent (write)

---

### 2. UserProfileMemory

Long-term user preferences keyed by `user_id`.

| Method | Signature | Description |
|--------|-----------|-------------|
| `update_preference` | `(user_id, key, value)` | Set or update a preference key |
| `get_profile` | `(user_id) -> dict` | Return the full profile dict |

**Storage key**: `profile:{user_id}`

**Profile schema** (open-ended dict, common keys):
```python
{
    "preferred_categories": list[str],
    "communication_preferences": dict,
    "engagement_profile": dict,
    "language": str,
    ...  # any key set via update_preference
}
```

**Used by**: orchestrator_agent (load), recommendation_agent (load + write)

---

### 3. InteractionMemory

Historical interactions and outcomes keyed by `user_id`.

| Method | Signature | Description |
|--------|-----------|-------------|
| `record_interaction` | `(user_id, interaction_type, data)` | Append an interaction record |
| `get_interactions` | `(user_id) -> list[dict]` | Return all interactions for the user |

**Storage key**: `interactions:{user_id}`

**Interaction schema**:
```python
{
    "type": str,          # e.g. "knowledge_retrieval", "analytics_query"
    "data": dict,         # arbitrary payload
    "timestamp": ISO8601
}
```

**Common interaction types**:

| Type | Recorded by | Payload keys |
|------|-------------|--------------|
| `knowledge_retrieval` | knowledge_agent | `request`, `answer` |
| `analytics_query` | analytics_agent | `request`, `query_type`, `result_summary` |
| `recommendation_request` | recommendation_agent | `strategy`, `recommendation_count` |
| `preference_update` | memory_agent | `updated_preferences`, `change_source` |

**Used by**: knowledge_agent (write), analytics_agent (write), recommendation_agent (read + write), evaluation_agent (read)

---

### 4. AgentObservationMemory

Agent learnings and observations keyed by `agent_id`.

| Method | Signature | Description |
|--------|-----------|-------------|
| `record_observation` | `(agent_id, observation, context)` | Append an observation |
| `get_observations` | `(agent_id) -> list[dict]` | Return all observations for the agent |

**Storage key**: `observations:{agent_id}`

**Observation schema**:
```python
{
    "observation": str,   # human-readable learning
    "context": dict,      # supporting data
    "timestamp": ISO8601
}
```

**Common agents that record observations**:

| Agent | Example observation |
|-------|-------------------|
| `orchestrator` | `"Classified intent as knowledge with confidence 0.9"` |
| `analytics` | `"Executed sql_execution analysis"` |
| `evaluation` | `"High-performing workflow pattern identified"` |

**Used by**: orchestrator_agent (write), analytics_agent (write), evaluation_agent (read + write)

---

## MemoryManager

Central coordinator that holds one instance of each memory type.

```python
class MemoryManager:
    conversation: ConversationMemory
    user_profile: UserProfileMemory
    interaction: InteractionMemory
    agent_observation: AgentObservationMemory

    def clear_all() -> None   # clears all four stores
```

### Base MemoryStore

All four memory types inherit from `MemoryStore`:

```python
class MemoryStore:
    def set(key, value) -> None      # stores {value, timestamp}
    def get(key) -> Any | None       # returns value or None
    def delete(key) -> None
    def clear() -> None
```

---

## Usage Patterns

### Pattern 1 — Load context before agent execution (orchestrator)
```python
conversation = memory_manager.conversation.get_conversation(session_id)
user_profile  = memory_manager.user_profile.get_profile(user_id)
```

### Pattern 2 — Write after agent execution (knowledge_agent)
```python
memory_manager.conversation.add_message(session_id, "assistant", answer)
memory_manager.interaction.record_interaction(
    user_id,
    "knowledge_retrieval",
    {"request": request, "answer": answer}
)
```

### Pattern 3 — Record orchestrator observation
```python
memory_manager.agent_observation.record_observation(
    "orchestrator",
    f"Classified intent as {intent} with confidence {confidence}",
    {"request": request, "reasoning": reasoning}
)
```

### Pattern 4 — Read interaction history for model selection (recommendation_agent)
```python
interactions = memory_manager.interaction.get_interactions(customer_id)
interaction_count = len(interactions)
# cold start if interaction_count < 5
```

### Pattern 5 — Read observations for trend analysis (evaluation_agent)
```python
observations = memory_manager.agent_observation.get_observations("evaluation")
trend_analysis = analyze_evaluation_trends(observations, workflow_type)
```

---

## Notebook Verification (UC7 — Audit Trail)

The notebook `01_level1_knowledge_retrieval.ipynb` UC7 demonstrates memory directly:

```python
from memory.memory_manager import memory_manager

interactions = memory_manager.interaction.get_interactions("trustsafety@shop.com")
observations = memory_manager.agent_observation.get_observations("orchestrator")

# Outputs:
# Interactions Recorded: 1
# Orchestrator Observations: 25
```

---

## Limitations

| Limitation | Detail |
|------------|--------|
| **In-process only** | Memory does not persist across Python process restarts |
| **No external DB** | All data stored in Python dicts in RAM |
| **No TTL / eviction** | Data accumulates until `clear_all()` is called |
| **No concurrency control** | Not thread-safe for concurrent agent writes |
| **No encryption** | Sensitive data stored in plain dicts |

---

## Future Improvements (Phase 2)

- Persist to Redis or SQLite for cross-process durability
- Add TTL-based eviction per memory type
- Integrate vector search for semantic context retrieval (RAG over memory)
- Add thread-safe locking for concurrent agent execution
- Encrypt sensitive profile data at rest
