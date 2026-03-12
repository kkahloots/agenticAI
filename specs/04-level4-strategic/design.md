# 🧠 Level‑4 Strategic Agent Design

### Orchestration Workflow

1. **Goal Decomposition**: Break the high‑level target into measurable sub‑goals (e.g. segmentation, offer creation, outreach). Uses `get_llm()` via the universal LLM factory with a heuristic fallback.
2. **Agent Assignment**: Assign each sub‑goal to the appropriate agent: Level‑2 for segmentation, Level‑3 for executing campaigns.
3. **Coordination Loop**: Monitor the performance of sub‑agents; if a sub‑goal is off track, adjust parameters or reassign resources.
4. **Self‑Reflection**: After each campaign cycle, call `reflect_and_replan(segment_id, goal)`. If KPI deviation exceeds `KPI_DEVIATION_THRESHOLD` or a prior outcome flagged `needs_reanalysis`, re‑decompose the goal and re‑run the campaign cycle with a tighter segment filter.
5. **Reporting**: Summarise progress and recommend next steps to the user.

### Self-Reflection Loop (G7 + G8)

```
AFTER campaign cycle:
  deviation = check_kpi_deviation(segment_id)
  IF deviation.action_required OR _has_pending_reanalysis(segment_id):
    re-decompose goal with refined context
    re-run campaign cycle with filters = { segment: "high-value" }
    log re-plan event to audit trail
  ELSE:
    proceed — KPI within acceptable range
```

- Deviation threshold: `KPI_DEVIATION_THRESHOLD` env var (default `0.10` = 10 %).
- Maximum re-plan cycles: 1 (prevents infinite loops).
- All reflection decisions logged via `log_audit_event`.

### Implementation Notes

- Use a graph structure (LangGraph) where nodes represent tasks and edges represent dependencies.
- SQL generation uses `create_sql_query_chain` (Level‑2) with schema binding and injection guard.
- Integrate analytics feedback loops so that poor-performing segments are re‑analysed and new offers are created.
- All LLM calls go through `src/llm.py` universal factory — provider switchable via `LLM_PROVIDER`.

### Configurable Thresholds

All thresholds are read from environment variables via `src/config.py`:

| Env var | Default | Purpose |
|---------|---------|---------|
| `APPROVAL_CAMPAIGN_REACH_THRESHOLD` | 1000 | Require human approval above this reach |
| `KPI_DEVIATION_THRESHOLD` | 0.10 | Trigger self-reflection above this deviation |
| `TARGET_CONVERSION_RATE` | 0.05 | Baseline target for KPI comparison |

### Constraints

- The agent must respect campaign budgets and compliance limits.
- It cannot override legal constraints or user's explicit instructions.
- Approval thresholds are configurable — never hardcoded.
