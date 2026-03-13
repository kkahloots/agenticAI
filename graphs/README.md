# LangGraph Workflows

LangGraph execution graphs for agentic AI workflows with dynamic routing and state management.

## Overview

LangGraph provides a framework for building stateful, multi-agent workflows. The agentic system uses LangGraph to orchestrate agent execution, manage state transitions, and handle conditional routing.

## Graphs

### Main Agentic Workflow Graph
**File**: `agent_workflow_graph.py`

The primary execution graph for agentic workflows.

**Architecture**:
```
START
  ↓
orchestrator_node (Intent classification & routing)
  ↓
conditional_router (Route to appropriate agent)
  ↓
┌─────────────────────────────────────────┐
│ Agent Nodes (Conditional Execution)     │
│ - knowledge_node                        │
│ - analytics_node                        │
│ - recommendation_node                   │
│ - action_node                           │
│ - workflow_node                         │
└─────────────────────────────────────────┘
  ↓
evaluation_node (Quality assessment)
  ↓
conditional_replan (Replan if needed)
  ↓
END
```

**Nodes**:
- `orchestrator_node` - Intent classification and planning
- `knowledge_node` - Knowledge retrieval
- `analytics_node` - Data analysis
- `recommendation_node` - Recommendations
- `action_node` - Action execution
- `workflow_node` - Complex workflows
- `evaluation_node` - Quality assessment

**Edges**:
- `START → orchestrator_node` - Always start with orchestrator
- `orchestrator_node → conditional_router` - Route based on intent
- `conditional_router → agent_nodes` - Route to appropriate agent
- `agent_nodes → evaluation_node` - Always evaluate
- `evaluation_node → conditional_replan` - Replan if needed
- `conditional_replan → END or orchestrator_node` - End or replan

**Usage**:
```python
from graphs.agent_workflow_graph import build_agentic_graph
from agentic.agentic_state import new_agentic_state

# Build graph
graph = build_agentic_graph()

# Create state
state = new_agentic_state("What is the customer profile?", user_id="user1")

# Execute
config = {"configurable": {"thread_id": state["request_id"]}}
result = graph.invoke(state, config=config)

# Get response
print(result["messages"][-1].content)
```

## State Management

**AgenticState** - Comprehensive state for workflows:

```python
{
    "request_id": str,              # Unique request ID
    "user_id": str,                 # User identifier
    "session_id": str,              # Session identifier
    "original_request": str,        # User request
    "intent": str,                  # Classified intent
    "confidence": float,            # Classification confidence
    "active_agent": str,            # Currently active agent
    "agent_plan": dict,             # Execution plan
    "agent_history": list,          # Agent execution history
    "conversation_context": dict,   # Memory context
    "user_profile": dict,           # User profile
    "mcp_calls": list,              # MCP tool calls
    "intermediate_results": list,   # Agent results
    "final_result": any,            # Final result
    "messages": list,               # Message history
    "evaluation": dict,             # Evaluation results
    "should_replan": bool,          # Replan flag
    "replan_count": int,            # Replan count
    "error": str,                   # Error message
    "audit_trail": list,            # Audit trail
}
```

## Conditional Routing

Routing logic determines which agent executes:

```python
def route_to_agent(state: AgenticState) -> str:
    """Route to next agent based on intent and confidence."""
    
    # Check for errors
    if state.get("error"):
        return "error_handler"
    
    # Check confidence threshold
    if state["confidence"] < 0.6:
        return "human_approval"
    
    # Route by intent
    intent_to_agent = {
        "knowledge": "knowledge_agent",
        "analytics": "analytics_agent",
        "recommendation": "recommendation_agent",
        "workflow": "workflow_agent",
        "action": "action_agent",
    }
    
    return intent_to_agent.get(state["intent"], "knowledge_agent")
```

## Replanning Logic

Evaluation agent triggers replanning when needed:

```python
def should_replan(state: AgenticState) -> bool:
    """Determine if replanning is needed."""
    
    evaluation = state.get("evaluation", {})
    
    # Check quality metrics
    if evaluation.get("quality_score", 1.0) < 0.7:
        return True
    
    # Check completeness
    if not evaluation.get("is_complete", True):
        return True
    
    # Check replan count
    if state["replan_count"] >= 3:
        return False  # Max replans reached
    
    return False
```

## Execution Flow

### Example: Knowledge Retrieval

```
1. START
   ↓
2. orchestrator_node
   - Classify intent: "knowledge"
   - Confidence: 0.95
   - Plan: ["knowledge_agent"]
   ↓
3. conditional_router
   - Route to: "knowledge_agent"
   ↓
4. knowledge_node
   - Extract customer ID: "CUST-001"
   - Retrieve profile
   - Synthesize answer
   ↓
5. evaluation_node
   - Quality score: 0.95
   - Is complete: true
   - Should replan: false
   ↓
6. conditional_replan
   - No replan needed
   ↓
7. END
   - Return result
```

### Example: With Replanning

```
1. START
   ↓
2. orchestrator_node
   - Classify intent: "analytics"
   - Confidence: 0.85
   - Plan: ["analytics_agent"]
   ↓
3. conditional_router
   - Route to: "analytics_agent"
   ↓
4. analytics_node
   - Generate segments
   - Quality score: 0.6 (low)
   ↓
5. evaluation_node
   - Quality score: 0.6 (below threshold)
   - Should replan: true
   - Replan count: 1
   ↓
6. conditional_replan
   - Replan needed
   ↓
7. orchestrator_node (replan)
   - Adjust plan
   - Increase detail level
   ↓
8. analytics_node (retry)
   - Generate detailed segments
   - Quality score: 0.9
   ↓
9. evaluation_node
   - Quality score: 0.9 (acceptable)
   - Should replan: false
   ↓
10. conditional_replan
    - No more replans
    ↓
11. END
    - Return result
```

## Checkpointing

LangGraph provides checkpointing for fault tolerance:

```python
from langgraph.checkpoint.sqlite import SqliteSaver

# Create graph with checkpointing
checkpointer = SqliteSaver.from_conn_string(":memory:")
graph = build_agentic_graph(checkpointer=checkpointer)

# Execute with checkpointing
config = {"configurable": {"thread_id": "thread-123"}}
result = graph.invoke(state, config=config)

# Resume from checkpoint
result = graph.invoke(state, config=config)  # Resumes from last checkpoint
```

## Visualization

Visualize graph structure:

```python
from graphs.agent_workflow_graph import build_agentic_graph

graph = build_agentic_graph()

# Get graph structure
print(graph.get_graph().draw_ascii())

# Get graph schema
schema = graph.get_graph().get_schema()
```

## Testing

Test workflows:

```bash
pytest tests/test_agentic.py -v
```

**Test Coverage**: 15+ tests for workflow execution

## Performance

Graph execution is optimized:

- **Parallel Execution**: Agents can run in parallel
- **Caching**: Results cached to avoid recomputation
- **Streaming**: Stream results as they become available
- **Checkpointing**: Resume from checkpoints

## Advanced Features

### Custom Nodes

Add custom nodes to the graph:

```python
def custom_node(state: AgenticState) -> dict:
    """Custom processing node."""
    # Process state
    return {"custom_field": "value"}

# Add to graph
graph.add_node("custom_node", custom_node)
graph.add_edge("orchestrator_node", "custom_node")
```

### Conditional Edges

Add conditional routing:

```python
def route_function(state: AgenticState) -> str:
    """Determine next node."""
    if state["confidence"] > 0.8:
        return "high_confidence_path"
    else:
        return "low_confidence_path"

# Add conditional edge
graph.add_conditional_edges(
    "orchestrator_node",
    route_function,
    {
        "high_confidence_path": "agent_node",
        "low_confidence_path": "human_approval_node"
    }
)
```

## Documentation

- [Main README](../README.md) - Project overview
- [Agentic Architecture](../agentic/README.md) - System architecture
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/) - LangGraph docs

---

**Status**: ✅ Production Ready | **Version**: 1.0
