# Agentic AI System – Business Overview

## Purpose

The agentic system replaces the nonagent pipeline's fixed routing with a dynamic, memory-aware multi-agent architecture. Eight specialised agents collaborate to handle customer data management, analytics, recommendations, and campaign execution — with an evaluation loop that detects poor outcomes and triggers replanning.

## What Changed from the Nonagent System

| Capability | Nonagent Pipeline | Agentic System |
|-----------|------------------|----------------|
| Routing | Fixed rules (5 levels) | Dynamic intent classification (LLM + pattern rules) |
| Agents | 5 sequential levels | 8 collaborative agents |
| Tools | Direct function calls | MCP protocol servers (5 servers, 15+ tools) |
| Memory | Session only | 4-layer memory (conversation, profile, interaction, observation) |
| Evaluation | None | Evaluation agent with replanning for workflow/action intents |
| Human oversight | Approval gates in Level 3/4 | Low-confidence requests (< 0.6) routed to human approval |

## The Eight Agents

| Agent | What it does |
|-------|-------------|
| **Orchestrator** | Classifies intent, builds execution plan, routes to the right agent |
| **Knowledge** | Retrieves customer profiles, KYC/identity status, product catalogue, policy documents |
| **Analytics** | Runs SQL queries, generates customer segments |
| **Recommendation** | Generates personalised product and offer recommendations |
| **Workflow** | Decomposes complex multi-step goals and coordinates other agents |
| **Action** | Executes operations: draft emails, send notifications, create CRM cases, schedule campaigns |
| **Evaluation** | Assesses outcomes for workflow and action requests; triggers replanning if needed |
| **Memory** | Manages cross-session memory: conversation history, user profiles, interaction logs, agent observations |

## How a Request Flows

```
User Request
    ↓
Orchestrator — classifies intent, builds plan
    ↓
Intent routing (knowledge / analytics / recommendation / workflow / action)
    ↓ (if confidence < 0.6)
Human Approval — approver accepts or rejects
    ↓
Specialised Agent — executes using MCP tool servers
    ↓ (workflow or action only)
Evaluation Agent — checks outcome, sets should_replan if needed
    ↓
Response
```

## Use Cases

### Customer Information Lookup
Request: *"What is the KYC status of CUST-001?"*
- Orchestrator classifies as `knowledge`
- Knowledge agent calls `CustomerDataServer.get_kyc_status`
- Result returned directly — no evaluation needed

### Customer Segmentation
Request: *"Segment customers by risk score"*
- Orchestrator classifies as `analytics`
- Analytics agent calls `AnalyticsServer.generate_segment`
- Result returned directly

### Product Recommendations
Request: *"Recommend products for CUST-042"*
- Orchestrator classifies as `recommendation`
- Recommendation agent calls `RecommendationServer.recommend_products` and `CustomerDataServer.search_customer_profile`
- Personalised list returned

### Campaign Execution
Request: *"Send retention offers to high-risk VIP customers"*
- Orchestrator classifies as `action`
- Action agent calls `CRMServer.draft_email`, `CRMServer.send_notification`
- Evaluation agent checks outcome; replans if delivery rate is low

### Complex Business Goal
Request: *"Increase VIP customer engagement by 10%"*
- Orchestrator classifies as `workflow`
- Workflow agent decomposes into sub-tasks: segment → recommend → action
- Evaluation agent assesses result and triggers replanning if target not met

## Safeguards

- Requests with intent confidence below 0.6 are paused for human approval before execution.
- Every agent action is appended to an immutable audit trail in state.
- The evaluation agent only activates for `workflow` and `action` intents — read-only agents (knowledge, analytics, recommendation) go directly to response.
- Memory is in-process only — no external database, no data leaves the runtime.

## Running Both Systems in Parallel

Both systems are fully operational and produce compatible outputs via a shared output adapter. Use the nonagent system for simple, predictable requests; use the agentic system where dynamic routing, memory context, or evaluation is needed.

- Nonagent: `docs/nonagent/` and `specs/nonagent/`
- Agentic: `docs/agentic/` and `specs/agentic/`
- Side-by-side comparison: `notebooks/agentic/comparison.ipynb`
