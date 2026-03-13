# Test Coverage Expansion Plan

## Current State
- Existing tests: 136 passing (121 nonagent + 15 agentic)
- Main gaps: Agentic system has minimal coverage

## Phase 1: Analysis (CHECKPOINT 1)
- [ ] Analyze agentic/ directory structure
- [ ] Identify untested modules
- [ ] Map dependencies
- [ ] Create coverage index in temp/coverage_index.json

## Phase 2: Core Agentic Tests (CHECKPOINT 2)
- [ ] test_agentic_state.py - State management
- [ ] test_memory_manager.py - Memory layer
- [ ] test_tool_registry.py - Tool registration
- [ ] test_orchestrator_agent.py - Orchestrator logic
- [ ] test_mcp_servers.py - MCP server implementations

## Phase 3: Agent Tests (CHECKPOINT 3)
- [ ] test_knowledge_agent.py - Knowledge retrieval
- [ ] test_analytics_agent.py - Analytics operations
- [ ] test_recommendation_agent.py - Recommendations
- [ ] test_evaluation_agent.py - Evaluation logic
- [ ] test_compliance_agent.py - Compliance checks

## Phase 4: Integration Tests (CHECKPOINT 4)
- [ ] test_agent_workflow.py - Full workflow
- [ ] test_agent_collaboration.py - Multi-agent scenarios
- [ ] test_error_handling.py - Error cases
- [ ] test_edge_cases.py - Edge cases

## Phase 5: Merge & Validate (CHECKPOINT 5)
- [ ] Merge all test files
- [ ] Run full test suite
- [ ] Generate coverage report
- [ ] Document results

## Target Coverage
- Agentic: 80%+ coverage
- Overall: 85%+ coverage
