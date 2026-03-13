# Agentic AI Architecture Specification

## Overview

The Agentic AI system is a collaborative multi-agent architecture where autonomous agents work together to handle complex user requests. Unlike traditional pipeline systems, agents make dynamic decisions, share context through memory, and can replan when outcomes don't meet expectations.

## Core Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User Request                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Orchestrator Agent                         │
│  • Intent Classification (LLM + Rules)                       │
│  • Agent Selection & Routing                                 │
│  • Execution Plan Building                                   │
│  • Memory Context Loading                                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              LangGraph Execution Workflow                    │
│  • Dynamic State Management (AgenticState)                   │
│  • Conditional Agent Routing                                 │
│  • Evaluation & Replanning Loops                             │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌────────────┐  ┌────────────┐  ┌────────────┐
│ Knowledge  │  │ Analytics  │  │Recommend-  │
│   Agent    │  │   Agent    │  │ation Agent │
│            │  │            │  │            │
│ • Customer │  │ • SQL Gen  │  │ • ML Models│
│   Profiles │  │ • Segment  │  │ • Collab   │
│ • RAG      │  │ • KPIs     │  │   Filter   │
│ • Synthesis│  │ • Insights │  │ • Hybrid   │
└─────┬──────┘  └─────┬──────┘  └─────┬──────┘
      │               │               │
      └───────────────┼───────────────┘
                      │
         ┌────────────┼────────────┐
         │            │            │
         ▼            ▼            ▼
┌────────────┐  ┌────────────┐  ┌────────────┐
│ Workflow   │  │  Action    │  │ Evaluation │
│   Agent    │  │   Agent    │  │   Agent    │
│            │  │            │  │            │
│ • Multi-   │  │ • CRM Ops  │  │ • Outcome  │
│   Step     │  │ • Notifs   │  │   Analysis │
│ • Coord    │  │ • Safety   │  │ • Replan   │
│ • Decomp   │  │   Checks   │  │   Trigger  │
└─────┬──────┘  └─────┬──────┘  └─────┬──────┘
      │               │               │
      └───────────────┼───────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    MCP Tool Servers                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │Customer  │ │Analytics │ │Recommend │ │   CRM    │      │
│  │  Data    │ │          │ │          │ │          │      │
│  │          │ │ • SQL    │ │ • ML     │ │ • Cases  │      │
│  │ • Profile│ │ • Segment│ │ • Collab │ │ • Notifs │      │
│  │ • KYC    │ │ • KPIs   │ │ • Content│ │ • Tickets│      │
│  │ • Identity│ │ • Viz   │ │ • Hybrid │ │          │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      Memory Layer                            │
│  • ConversationMemory (session-based chat history)          │
│  • UserProfileMemory (long-term preferences)                │
│  • InteractionMemory (past actions and outcomes)            │
│  • AgentObservationMemory (agent learnings)                 │
└─────────────────────────────────────────────────────────────┘
```

## Agent Specifications

### 1. Orchestrator Agent
- **File**: `agentic/orchestrator_agent.py`
- **Purpose**: Central coordinator for all agent interactions
- **Autonomy**: High
- **Key Functions**:
  - Intent classification using LLM + rule-based fallback
  - Agent selection based on intent and context
  - Execution plan building
  - Memory context loading
- **Decision Rules**:
  - `knowledge` → knowledge_agent
  - `analytics` → analytics_agent  
  - `recommendation` → recommendation_agent
  - `workflow` → workflow_agent
  - `action` → action_agent
- **Memory Access**: conversation, user_profile, interaction

### 2. Knowledge Agent
- **File**: `agentic/knowledge_agent.py`
- **Purpose**: Information retrieval and synthesis
- **Autonomy**: Low (follows clear retrieval patterns)
- **MCP Servers**: customer_data, product_catalog
- **Key Functions**:
  - Customer profile retrieval
  - Product catalog access
  - Knowledge base search (RAG)
  - Answer synthesis with LLM
- **Decision Rules**:
  - IF customer_id detected → customer_data_server
  - IF product query → product_catalog_server
  - ELSE → knowledge_base search

### 3. Analytics Agent
- **File**: `agentic/analytics_agent.py`
- **Purpose**: Data analysis and insights generation
- **Autonomy**: Medium
- **MCP Servers**: analytics
- **Key Functions**:
  - SQL query generation and execution
  - Customer segmentation
  - KPI calculation
  - Trend analysis
- **Decision Rules**:
  - IF SQL detected → direct execution
  - IF segmentation request → generate_segment
  - IF KPI request → calculate_metrics

### 4. Recommendation Agent
- **File**: `agentic/recommendation_agent.py`
- **Purpose**: Personalized recommendations using ML
- **Autonomy**: Medium
- **MCP Servers**: recommendation, customer_data, product_catalog
- **Key Functions**:
  - Collaborative filtering
  - Content-based recommendations
  - Hybrid model selection
  - Cold start handling
- **Decision Rules**:
  - IF cold_start → popularity_based
  - IF sufficient_history → collaborative_filtering
  - IF content_rich → content_based

### 5. Workflow Agent
- **File**: `agentic/other_agents.py`
- **Purpose**: Multi-step workflow execution
- **Autonomy**: High
- **MCP Servers**: crm, analytics, customer_data
- **Key Functions**:
  - Goal decomposition
  - Sub-task coordination
  - Agent orchestration
  - Progress monitoring
- **Decision Rules**:
  - IF complex_goal → decompose_into_subtasks
  - IF requires_approval → request_human_approval

### 6. Action Agent
- **File**: `agentic/other_agents.py`
- **Purpose**: Execute actions with safety checks
- **Autonomy**: Medium
- **MCP Servers**: crm, customer_data
- **Key Functions**:
  - CRM operations
  - Notification sending
  - Case creation
  - Safety validation
- **Decision Rules**:
  - IF high_risk → require_approval
  - IF identity_unverified → block_action

### 7. Evaluation Agent
- **File**: `agentic/other_agents.py`
- **Purpose**: Outcome evaluation and replanning
- **Autonomy**: High
- **MCP Servers**: analytics
- **Key Functions**:
  - Outcome assessment
  - Deviation detection
  - Replan triggering
  - Learning capture
- **Decision Rules**:
  - IF deviation_high → trigger_replan
  - IF success → record_positive_observation

### 8. Memory Agent
- **File**: `agentic/other_agents.py`
- **Purpose**: Memory management and context
- **Autonomy**: Low
- **Key Functions**:
  - Context retrieval
  - Memory updates
  - Preference management
  - History tracking
- **Decision Rules**:
  - IF new_preference → update_user_profile
  - IF important_interaction → record_to_long_term

## State Management

### AgenticState Schema
```python
{
    "request_id": str,           # Unique request identifier
    "user_id": str,              # User identifier
    "session_id": str,           # Session identifier
    "original_request": str,     # User's original request
    "intent": str,               # Classified intent
    "confidence": float,         # Intent confidence (0.0-1.0)
    "active_agent": str,         # Currently executing agent
    "agent_plan": dict,          # Execution plan from orchestrator
    "agent_history": list,       # Agent execution history
    "conversation_context": dict, # Conversation memory
    "user_profile": dict,        # User profile from memory
    "mcp_calls": list,           # MCP tool invocations
    "intermediate_results": list, # Results from each agent
    "final_result": Any,         # Final output
    "messages": list,            # Human-readable messages
    "evaluation": dict,          # Evaluation results
    "should_replan": bool,       # Replan trigger flag
    "replan_count": int,         # Number of replans
    "error": str,                # Error message if any
    "audit_trail": list          # Complete audit log
}
```

## MCP Server Architecture

### Customer Data Server
- **File**: `mcp_servers/customer_data_server.py`
- **Tools**:
  - `search_customer_profile`: Get full customer profile
  - `get_identity_status`: Identity verification status
  - `get_kyc_status`: KYC compliance status

### Analytics Server
- **File**: `mcp_servers/analytics_server.py`
- **Tools**:
  - `run_sql_query`: Execute SQL queries
  - `generate_segment`: Customer segmentation
  - `calculate_kpis`: KPI computation

### Recommendation Server
- **File**: `mcp_servers/recommendation_server.py`
- **Tools**:
  - `recommend_products`: ML-based recommendations
  - `get_similar_customers`: Collaborative filtering
  - `get_content_recommendations`: Content-based

### CRM Server
- **File**: `mcp_servers/crm_server.py`
- **Tools**:
  - `create_case`: Create support cases
  - `send_notification`: Send customer notifications
  - `update_customer`: Update customer records

### Product Catalog Server
- **File**: `mcp_servers/product_catalog_server.py`
- **Tools**:
  - `get_products`: Retrieve product information
  - `search_products`: Product search
  - `get_categories`: Product categories

## Memory Architecture

### Memory Types
1. **ConversationMemory**: Short-term chat history per session
2. **UserProfileMemory**: Long-term user preferences and settings
3. **InteractionMemory**: Historical interactions and outcomes
4. **AgentObservationMemory**: Agent learnings and insights

### Memory Manager
- **File**: `memory/memory_manager.py`
- **Global Instance**: `memory_manager`
- **Operations**: set, get, delete, clear per memory type

## Workflow Execution

### LangGraph Integration
- **File**: `graphs/agent_workflow_graph.py`
- **State Type**: AgenticState
- **Routing**: Conditional edges based on intent and context
- **Checkpointing**: State persistence across agent transitions

### Execution Flow
1. User request → Orchestrator Agent
2. Intent classification → Agent selection
3. Memory context loading → Agent execution
4. MCP tool invocation → Result processing
5. Memory updates → Response generation
6. Evaluation → Replanning if needed

## Key Differences from Nonagent

| Aspect | Nonagent Pipeline | Agentic System |
|--------|------------------|----------------|
| **Routing** | Fixed intent→level mapping | Dynamic agent selection |
| **Collaboration** | Sequential execution | Parallel coordination |
| **Memory** | Session checkpointer only | Multi-layer persistent memory |
| **Tools** | Direct function calls | MCP protocol abstraction |
| **Evaluation** | No feedback loop | Evaluation agent with replanning |
| **Autonomy** | Rule-based | Decision-making agents |
| **State** | Simple dict | Rich AgenticState schema |

## Implementation Files

### Core Agents
- `agentic/orchestrator_agent.py` - Orchestrator
- `agentic/knowledge_agent.py` - Knowledge retrieval
- `agentic/analytics_agent.py` - Data analysis
- `agentic/recommendation_agent.py` - ML recommendations
- `agentic/other_agents.py` - Workflow, action, evaluation, memory

### Infrastructure
- `agentic/agent_registry.py` - Agent metadata
- `agentic/agentic_state.py` - State management
- `graphs/agent_workflow_graph.py` - LangGraph workflow
- `memory/memory_manager.py` - Memory layer
- `mcp_servers/` - MCP server implementations
