# Agentic System – Workflows, Decisions & Monitoring

## How a Request Flows

### Example 1 — "What is the KYC status of CUST-001?"

```
You → Orchestrator (classifies: knowledge, confidence 0.95)
           ↓
      Knowledge Agent
           ↓
      CustomerDataServer.get_kyc_status("CUST-001")
           ↓
      should_evaluate() → END (knowledge agents skip evaluation)
           ↓
      You receive: "KYC status: verified / expired since 2024-03-15"
```

No human approval needed. Read-only. Audit trail appended to state.

---

### Example 2 — "Send retention offers to high-risk VIP customers"

```
You → Orchestrator (classifies: action, confidence 0.88)
           ↓
      Action Agent
           ↓
      CRMServer.draft_email(...)
      CRMServer.send_notification(...)
           ↓
      should_evaluate() → Evaluation Agent
           ↓
      Evaluation Agent checks outcome
        → success: True, should_replan: False
           ↓
      You receive: "✅ Action executed: notification"
```

---

### Example 3 — "Increase VIP customer engagement by 10%"

```
You → Orchestrator (classifies: workflow, confidence 0.85)
           ↓
      Workflow Agent
           ↓
      Decomposes into steps:
        1. Analyze requirements
        2. Execute sub-tasks
        3. Coordinate agents
        4. Validate outcome
           ↓
      should_evaluate() → Evaluation Agent
           ↓
      Evaluation Agent:
        → success: True / False
        → should_replan: True if outcome deviates from goal
           ↓
      You receive: "✅ Workflow executed: 4 steps completed"
```

---

### Example 4 — Ambiguous request (low confidence)

```
You → Orchestrator (classifies: unknown, confidence 0.45)
           ↓
      confidence < 0.6 → Human Approval node
           ↓
      Approver accepts ✅ → route_to_agent() re-runs → correct agent
      Approver rejects ❌ → error: "Request rejected by human approver"
```

---

## Decision Points

| Situation | What happens | Who decides |
|-----------|-------------|-------------|
| Intent confidence < 0.6 | Request paused; human approval required | Human approver |
| Approver rejects | Request ends with rejection message | Human approver |
| `active_agent` is `workflow` or `action` | Evaluation agent runs after | Evaluation agent (automatic) |
| `active_agent` is `knowledge`, `analytics`, or `recommendation` | Goes directly to END | No evaluation needed |
| Evaluation sets `should_replan: True` | `replan_count` incremented; state updated | Evaluation agent (automatic) |
| Agent encounters an error | `error` field set; routed to `error_handler` node | Automatic |

---

## Agent Handoffs

```
orchestrator     → knowledge_agent      : intent = "knowledge"
orchestrator     → analytics_agent      : intent = "analytics"
orchestrator     → recommendation_agent : intent = "recommendation"
orchestrator     → workflow_agent       : intent = "workflow"
orchestrator     → action_agent         : intent = "action"
orchestrator     → human_approval       : confidence < 0.6
orchestrator     → error_handler        : state["error"] is set
human_approval   → [any agent]          : after approval, re-routes via route_to_agent()
workflow_agent   → evaluation_agent     : always (via should_evaluate)
action_agent     → evaluation_agent     : always (via should_evaluate)
[other agents]   → END                  : directly
evaluation_agent → END                  : always
error_handler    → END                  : always
```

---

## Monitoring — What to Watch

### Green (all good)
- Requests completing with `final_result` populated and no `error` field
- `confidence` consistently above 0.6 (orchestrator classifying clearly)
- `evaluation.success: True` for workflow and action requests
- `should_replan: False` after evaluation

### Amber (investigate)
- `confidence` frequently between 0.6–0.75 — users may be sending ambiguous requests
- `replan_count` > 0 on multiple requests — evaluation agent finding poor outcomes
- Human approval queue growing — approvers may be unavailable or requests are consistently unclear

### Red (act now)
- `error` field populated repeatedly — agent or MCP server failures
- `audit_trail` not growing — audit logging broken (compliance risk)
- `evaluation.should_replan: True` on every workflow/action — systematic outcome failure

---

## Inspecting a Request

All diagnostic information is in the result state:

```python
result = agentic_graph.invoke(state, config=config)

# Which agents ran
print(result["agent_history"])       # e.g. ["orchestrator", "knowledge_agent"]

# What tools were called
print(result["mcp_calls"])           # list of {server, tool, params, result}

# Evaluation outcome (workflow/action only)
print(result["evaluation"])          # {success, feedback, should_replan}

# Full audit trail
for entry in result["audit_trail"]:
    print(entry)

# Error (if any)
print(result.get("error"))
```

---

## What to Do If Something Goes Wrong

| Problem | First step |
|---------|-----------|
| Request routed to wrong agent | Check `intent` and `confidence` in result state; review orchestrator classification |
| Action executed but no notification sent | Check `mcp_calls` for `crm_server.send_notification`; verify customer consent flags |
| Evaluation always triggering replan | Check `evaluation.feedback` in result state; review workflow/action agent logic |
| Human approval queue not clearing | Check `AUTO_APPROVE_DEV` env var; confirm approver has access |
| `error_handler` firing repeatedly | Check `error` field in state; review MCP server connectivity |
| Memory not persisting across requests | Memory is in-process only — resets on restart; this is expected behaviour |
