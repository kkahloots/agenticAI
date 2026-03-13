# Current State Analysis

## Agentic System Architecture (Actual Implementation)

### Core Components:
1. **Orchestrator Agent** (`agentic/orchestrator_agent.py`)
   - Intent classification (knowledge, analytics, recommendation, workflow, action)
   - Agent selection and routing
   - Memory context loading
   - Execution plan building

2. **Knowledge Agent** (`agentic/knowledge_agent.py`)
   - Customer profile retrieval via MCP
   - Product catalog access via MCP
   - Knowledge base search (RAG)
   - Answer synthesis with LLM

3. **Agent Registry** (`agentic/agent_registry.py`)
   - 8 agents: orchestrator, knowledge, analytics, recommendation, workflow, action, evaluation, memory
   - Metadata: capabilities, MCP servers, decision rules, autonomy levels

4. **MCP Servers** (`mcp_servers/`)
   - customer_data_server: customer profiles, identity, KYC
   - product_catalog_server: product data
   - analytics_server: SQL queries, segmentation
   - recommendation_server: ML recommendations
   - crm_server: CRM operations

5. **Memory Layer** (`memory/memory_manager.py`)
   - ConversationMemory: short-term chat history
   - UserProfileMemory: long-term user preferences
   - InteractionMemory: past interactions and outcomes
   - AgentObservationMemory: agent learnings

6. **LangGraph Workflow** (`graphs/agent_workflow_graph.py`)
   - State management with AgenticState
   - Dynamic routing between agents
   - Evaluation and replanning loops

## Documentation Issues Found:

### docs/ Structure Issues:
- Mixed structure: agentic/, nonagent/, and root level docs
- Incomplete agentic documentation
- Business docs don't reflect actual capabilities
- Developer guide missing key implementation details

### specs/ Structure Issues:
- Incomplete agentic specifications
- Missing detailed agent specs
- MCP server specs incomplete
- Memory layer specs incomplete

## Refactoring Plan:

### docs/ (User-Focused):
- docs/agentic/business/ - Business value, ROI, use cases
- docs/agentic/developer/ - How to use, examples, best practices
- docs/agentic/technical-non-dev/ - How it works without code
- docs/nonagent/ - Keep existing nonagent docs

### specs/ (Technical Specifications):
- specs/agentic/architecture.md - Overall architecture
- specs/agentic/agents/ - Detailed agent specifications
- specs/agentic/mcp_servers/ - MCP server specifications
- specs/agentic/memory/ - Memory layer specifications
- specs/agentic/workflows/ - LangGraph workflow specifications