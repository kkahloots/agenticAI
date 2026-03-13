# Agentic Agents — Specification Index

This directory contains one specification file per agent. Each file documents the agent's purpose, decision logic, MCP server usage, state contract, and error handling as implemented in the codebase.

## Agent Files

| File | Agent | Implementation |
|------|-------|---------------|
| [orchestrator.md](orchestrator.md) | Orchestrator Agent | `agentic/orchestrator_agent.py` |
| [knowledge.md](knowledge.md) | Knowledge Agent | `agentic/knowledge_agent.py` |
| [analytics.md](analytics.md) | Analytics Agent | `agentic/analytics_agent.py` |
| [recommendation.md](recommendation.md) | Recommendation Agent | `agentic/recommendation_agent.py` |
| [workflow.md](workflow.md) | Workflow Agent | `agentic/other_agents.py` |
| [action.md](action.md) | Action Agent | `agentic/other_agents.py` |
| [evaluation.md](evaluation.md) | Evaluation Agent | `agentic/other_agents.py` |
| [memory.md](memory.md) | Memory Agent | `agentic/other_agents.py` |

## Quick Reference

| Agent | Intent | Autonomy | MCP Servers |
|-------|--------|----------|-------------|
| orchestrator | — (entry point) | High | none |
| knowledge | `knowledge` | Low | customer_data, product_catalog |
| analytics | `analytics` | Medium | analytics |
| recommendation | `recommendation` | Medium | recommendation, customer_data |
| workflow | `workflow` | High | crm, analytics, customer_data |
| action | `action` | Medium | crm, customer_data |
| evaluation | post-workflow/action | High | analytics |
| memory | on-demand | Low | none |

## Agent Registry

All agents are registered in `agentic/agent_registry.py` as `AgenticAgentMeta` dataclasses with:
- `agent_id`, `name`, `purpose`
- `capabilities: list[str]`
- `mcp_servers: list[str]`
- `input_schema`, `output_schema`
- `decision_rules: list[str]`
- `memory_access: list[str]`
- `autonomy_level: "low" | "medium" | "high"`
