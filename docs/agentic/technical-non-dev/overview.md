# Agentic AI System – Technical Overview (Non-Developer)

## What This System Does

The agentic system handles customer data requests, analytics, recommendations, and campaign actions using eight AI agents that collaborate dynamically. Unlike the nonagent pipeline — where requests follow a fixed path through five levels — the agentic system classifies what you're asking for and routes it to the right combination of agents automatically.

## How a Request Is Handled

1. **You send a request** — e.g. *"What is the KYC status of CUST-001?"* or *"Send retention offers to high-risk customers"*
2. **The Orchestrator classifies your intent** — it determines whether this is a knowledge lookup, analytics task, recommendation request, workflow goal, or action to execute
3. **If the system is unsure** (confidence below 60%), it pauses and asks a human approver before continuing
4. **The right agent takes over** — it calls the appropriate tools via MCP servers (standardised tool interfaces) and returns a result
5. **For actions and workflows**, an Evaluation Agent checks the outcome and can trigger replanning if the result is poor

## The Eight Agents

| Agent | What it handles |
|-------|----------------|
| Orchestrator | Classifies every request and decides which agent runs |
| Knowledge | Customer profiles, KYC/identity status, product catalogue, policy documents |
| Analytics | SQL queries, customer segmentation |
| Recommendation | Personalised product and offer suggestions |
| Workflow | Complex multi-step goals (e.g. "increase VIP engagement by 10%") |
| Action | Sends emails/notifications, creates CRM cases, schedules campaigns |
| Evaluation | Checks whether workflow and action outcomes met the goal |
| Memory | Stores conversation history, user preferences, interaction logs, and agent observations across sessions |

## Decision Flow

```
Your Request
    ↓
Orchestrator — "What kind of request is this?"
    ↓
Is confidence ≥ 60%?
  No  → Human Approval (approver accepts or rejects)
  Yes → Route to agent
    ↓
Agent runs (uses tools via MCP servers)
    ↓
Is this a workflow or action?
  Yes → Evaluation Agent checks outcome
  No  → Response returned directly
```

## Where Humans Are Involved

| Situation | What happens |
|-----------|-------------|
| Intent confidence < 60% | Request paused; human approver must accept or reject |
| Approver rejects | Request ends with rejection message |
| Approver accepts | Request continues to the appropriate agent |

All other routing and execution is automatic.

## Memory

The system remembers context across requests within a session:

- **Conversation memory** — what was said in this session
- **User profile memory** — preferences and settings per user
- **Interaction memory** — past actions taken for a user (purchases, notifications sent)
- **Agent observations** — notes agents record about patterns they noticed

Memory is held in-process only — it does not persist to an external database and resets when the system restarts.

## Tools (MCP Servers)

Agents access data and execute actions through five standardised tool servers:

| Server | What it provides |
|--------|-----------------|
| Customer Data | Customer profiles, KYC status, identity verification |
| Analytics | SQL queries against the customer database, segmentation |
| Recommendation | Product recommendations, offer selection |
| CRM | Email drafting, notifications, case creation, campaign scheduling |
| Product Catalogue | Product listings and details |

## Audit Trail

Every agent action is recorded in an append-only audit trail attached to the request state. This covers intent classification, tool calls, evaluation outcomes, and any human approval decisions.

## Comparison with the Nonagent System

Both systems are running in parallel and produce compatible outputs.

| | Nonagent Pipeline | Agentic System |
|-|------------------|----------------|
| Routing | Fixed 5-level hierarchy | Dynamic intent classification |
| Memory | Session only | 4-layer cross-session memory |
| Evaluation | None | Evaluation agent for workflow/action |
| Human oversight | Approval gates in Level 3/4 | Low-confidence routing to human approval |
| Complexity | Lower | Higher — more flexible |

Use the nonagent system for simple, predictable requests. Use the agentic system where context, dynamic routing, or outcome evaluation matters.

## Monitoring

- **Audit trail**: every request produces a structured audit trail accessible in the result state
- **Agent history**: `agent_history` field shows which agents ran for each request
- **Evaluation results**: `evaluation` field shows whether the outcome was satisfactory and whether replanning was triggered
- **Observability**: optional Langfuse integration via `LANGFUSE_SECRET_KEY` env var for trace dashboards

## Support

For technical issues, contact the development team. For business questions about use cases or rollout, see `docs/agentic/business/overview.md`.
