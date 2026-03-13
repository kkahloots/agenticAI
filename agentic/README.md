# Agentic AI System

Modern autonomous multi-agent architecture with dynamic routing, MCP tool servers, multi-layer memory, and evaluation loops.

## 🏗️ Architecture

```
User Request
    ↓
Orchestrator Agent (Dynamic Routing & Coordination)
    ↓
┌─────────────────────────────────────────┐
│   Specialized Agents (Collaborative)    │
│   - Knowledge Agent                     │
│   - Analytics Agent                     │
│   - Recommendation Agent                │
│   - Action Agent                        │
│   - Workflow Agent                      │
│   - Evaluation Agent                    │
│   - Memory Agent                        │
│   - Compliance Agent                    │
└─────────────────────────────────────────┘
    ↓
MCP Tool Servers (Standardized Interface)
    ↓
Memory Layer (Multi-Layer Storage)
    ↓
Evaluation & Replanning Loop
    ↓
Response
```

## 📁 Directory Structure

```
agentic/
├── orchestrator/              # Request routing and coordination
│   └── orchestrator_agent.py
├── agents/                    # Specialized agents
│   ├── knowledge_agent.py
│   ├── analytics_agent.py
│   ├── recommendation_agent.py
│   ├── functional_agent.py
│   ├── compliance_agent.py
│   ├── evaluation_agent.py
│   └── recommendation_strategy_agent.py
├── mcp/                       # MCP tool servers
│   ├── customer_server.py
│   ├── analytics_server.py
│   ├── recommendation_server.py
│   ├── compliance_server.py
│   ├── functional_server.py
│   ├── notification_server.py
│   ├── product_server.py
│   ├── feature_server.py
│   └── llm_reasoning_server.py
├── memory/                    # Memory management
│   └── memory_manager.py
├── registry/                  # Tool discovery
│   └── tool_registry.py
├── sql/                       # SQL generation
│   └── sql_generator.py
├── models/                    # ML models
│   ├── behaviour_model.py
│   ├── collaborative_model.py
│   ├── content_model.py
│   └── hybrid_ranker.py
├── features/                  # Feature engineering
│   ├── feature_builder.py
│   └── feature_selector.py
├── planner/                   # Multi-step planning
│   └── planner_agent.py
├── utils/                     # Utilities
│   ├── agentic_api.py
│   └── agentic_display.py
├── agentic_state.py           # State management
├── agent_registry.py          # Agent metadata
├── output_adapter.py          # Output compatibility
└── README.md                  # This file
```

## 🤖 Agents

### 1. Orchestrator Agent
**Dynamic Coordination & Routing**

Analyzes requests and dynamically routes to specialized agents based on context.

- Intent classification (knowledge, analytics, recommendation, workflow, action)
- Agent selection and planning
- Multi-agent coordination
- Memory-informed decisions

**Status**: ✅ Production Ready

### 2. Knowledge Agent
**Intelligent Information Retrieval**

Retrieves customer data, policies, and history with memory-enhanced context.

- Customer profile retrieval
- Identity verification
- Email & CRM search
- Policy document RAG
- Cross-source integration

**Status**: ✅ Production Ready

### 3. Analytics Agent
**Advanced Data Intelligence**

Performs analytics with observation recording and insight generation.

- Customer segmentation
- SQL analytics
- Fraud risk analysis
- Sentiment analysis
- Insight generation

**Status**: ✅ Production Ready

### 4. Recommendation Agent
**Personalized Intelligence**

Generates personalized recommendations using collaborative filtering.

- User-based recommendations
- Collaborative filtering
- Behavior-based ranking
- Hybrid recommender
- Cold start handling

**Status**: ✅ Production Ready

### 5. Action Agent
**Autonomous Execution**

Executes business actions with consent validation and identity verification.

- Lead scoring
- Customer enrichment
- Next-best-action
- Notification delivery
- Campaign execution

**Status**: ✅ Production Ready

### 6. Workflow Agent
**Strategic Orchestration**

Plans and executes complex multi-step workflows.

- Campaign planning
- Multi-agent coordination
- Workflow decomposition
- Scenario simulation
- A/B testing

**Status**: ✅ Production Ready

### 7. Evaluation Agent
**Quality Assurance & Learning**

Evaluates responses and triggers replanning when needed.

- Response quality assessment
- Completeness validation
- Accuracy verification
- Replan triggering
- Continuous learning

**Status**: ✅ Production Ready

### 8. Compliance Agent
**Safety & Compliance**

Ensures all outputs meet security and compliance standards.

- PII redaction
- Content filtering
- Compliance validation
- Output sanitization
- Risk assessment

**Status**: ✅ Production Ready

## 🛠️ MCP Tool Servers

Model Context Protocol servers expose tools and data to agents:

- **customer_server.py** - Customer profiles and interactions
- **analytics_server.py** - Analytics and reporting
- **recommendation_server.py** - Recommendation engine
- **compliance_server.py** - Compliance checks
- **functional_server.py** - Business operations
- **notification_server.py** - Notification delivery
- **product_server.py** - Product catalog
- **feature_server.py** - Feature engineering
- **llm_reasoning_server.py** - LLM-based reasoning

## 🧠 Memory Layer

Multi-layer memory system for context and learning:

- **Conversation Memory** - Short-term conversation context
- **User Profile Memory** - Long-term user preferences
- **Interaction Memory** - Past interactions and outcomes
- **Agent Observation Memory** - Agent learnings and patterns

## 🔄 State Management

**AgenticState** - Comprehensive state for agentic workflows:

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

## 🚀 Key Features

### Dynamic Routing
Context-aware agent selection based on intent classification and confidence scores.

### MCP Tool Abstraction
Standardized tool protocol for consistent agent-tool interaction.

### Multi-Layer Memory
Conversation, profile, interaction, and observation memory for continuous learning.

### Evaluation & Replanning
Automatic quality assessment with intelligent replanning when thresholds aren't met.

### Audit Trail
Complete audit trail for compliance and debugging.

### Output Compatibility
Agentic outputs compatible with nonagent pipeline for seamless migration.

## 📊 Agent Registry

Central registry of agent metadata:

```python
from agentic.agent_registry import get_agentic_agent, list_agentic_agents

# Get specific agent
agent = get_agentic_agent("knowledge")

# List all agents
agents = list_agentic_agents()

# Get agent description
description = agent.purpose
```

## 🔧 Usage

### Quick Start

```python
from agentic.agentic_state import new_agentic_state
from agentic.orchestrator_agent import orchestrator_agent
from agentic.knowledge_agent import knowledge_agent

# Create state
state = new_agentic_state("What is the profile for CUST-001?", user_id="user1")

# Route through orchestrator
orchestrator_result = orchestrator_agent(state)
state.update(orchestrator_result)

# Execute knowledge agent
knowledge_result = knowledge_agent(state)
state.update(knowledge_result)

# Get response
print(state["messages"][-1].content)
```

### Using Output Adapter

```python
from agentic.output_adapter import adapt_agentic_to_nonagent

# Convert agentic state to nonagent format
nonagent_state = adapt_agentic_to_nonagent(agentic_state)
```

## 🧪 Testing

Run agentic tests:

```bash
pytest tests/test_agentic_state.py \
  tests/test_memory_manager.py \
  tests/test_orchestrator_agent.py \
  tests/test_agent_registry.py \
  tests/test_output_adapter.py \
  tests/test_knowledge_agent.py \
  tests/test_analytics_agent.py \
  tests/test_recommendation_agent.py -v
```

**Test Coverage**: 215 tests, 98%+ coverage on core modules

## 📚 Documentation

- [Main README](../README.md) - Project overview
- [Agentic System Overview](../UC_AGENTIC_README.md) - Detailed system description
- [Test Coverage Report](../TEST_COVERAGE_REPORT.md) - Testing details
- [Developer Guide](../docs/agentic/developer/guide.md) - API and examples

## 🔄 Migration from Nonagent

The agentic system wraps existing nonagent tools via MCP servers:

1. **Phase 1**: Run deterministic mode (minimal changes)
2. **Phase 2**: Enable dynamic mode for specific use cases
3. **Phase 3**: Add custom tools to registry
4. **Phase 4**: Implement advanced planning strategies

## 🎯 Future Enhancements

- [ ] LLM-based planning (currently rule-based)
- [ ] Advanced tool ranking algorithms
- [ ] Distributed agent execution
- [ ] Real-time evaluation metrics
- [ ] Custom agent creation UI
- [ ] Vector-based memory search
- [ ] Multi-agent collaboration patterns

---

**Status**: ✅ Production Ready | **Version**: 1.0 | **Last Updated**: 2024
