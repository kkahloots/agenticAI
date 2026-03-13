# 🎯 Level 4 — Strategic Agent / Workflow Orchestration

**TL;DR**: The strategic agent plans campaigns to achieve business outcomes (increase card adoption, reduce churn), coordinates multi-level actions, and self-corrects when KPIs deviate from targets.

---

## Business Use Cases

### 1. Campaign Planning & Decomposition
Break down a high-level business goal into concrete, executable tasks.

**Trigger**: Requests like "increase card adoption by 10%", "reduce churn in at-risk segment", or "grow revenue from dormant customers".

**Output**: Multi-step campaign plan with:
- Target segment
- Recommended actions (email, SMS, offer)
- Expected conversions and revenue
- Risk assessment
- Approval gates

**Example**:
```
Goal: "Increase card adoption by 10% in next quarter"
  ├── Step 1: Segment high-value, non-card customers
  ├── Step 2: Score by engagement and lifetime value
  ├── Step 3: Generate personalized offers (Level 5)
  ├── Step 4: Send targeted emails (Level 3)
  ├── Step 5: Track conversions (Level 2)
  └── Step 6: Adjust strategy if KPI misses
```

---

### 2. Multi-Agent Orchestration
Coordinate actions across Levels 2, 3, and 5:
- Level 2 segments customers and analyzes trends
- Level 3 sends notifications and tracks engagement
- Level 5 generates personalized recommendations

**Trigger**: Complex campaigns requiring multiple agent types.

**Output**: Orchestrated workflow with audit trail.

---

### 3. Revenue Impact Analysis
Project conversions, revenue, and ROI from campaign parameters.

**Trigger**: Requests about "what's the ROI", "how much revenue", or "what's the impact".

**Output**: Financial projection with:
- Estimated conversions
- Revenue impact (£)
- Cost (if applicable)
- ROI (%)
- Confidence interval

**Formula**:
```
conversions = segment_size × conversion_rate
revenue = conversions × avg_order_value
roi = (revenue - cost) / cost × 100%
```

---

### 4. Scenario Simulation
Compare strategy options and recommend the highest-ROI path.

**Trigger**: Requests like "should we email or SMS", "which segment first", or "compare strategies".

**Output**: Side-by-side comparison with recommendation.

**Example**:
```
Strategy A: Email to high-value segment
  - Conversions: 150
  - Revenue: £7,500
  - ROI: 250%

Strategy B: SMS to at-risk segment
  - Conversions: 80
  - Revenue: £3,200
  - ROI: 160%

Recommendation: Strategy A (higher ROI)
```

---

### 5. Pilot Testing
Run A/B split with compliance gate (pilot ≤ 50% enforced).

**Trigger**: Requests about "test", "pilot", or "A/B test".

**Output**: Pilot execution plan with:
- Control group (50%)
- Treatment group (50%)
- Duration
- Success metrics
- Approval gate

---

### 6. Roadmap Prioritization
Rank initiatives by ROI score (revenue / effort weight).

**Trigger**: Requests like "what should we do first", "prioritize", or "roadmap".

**Output**: Ranked list of initiatives with:
- ROI score
- Effort estimate
- Timeline
- Dependencies
- Risk level

---

### 7. Self-Reflection Loop
KPI deviation above threshold triggers automatic goal re-decomposition.

**Trigger**: Automatic (runs on schedule) or manual request.

**Output**: Updated campaign plan with:
- Current KPI vs. target
- Deviation analysis
- Recommended adjustments
- New action plan

**Example**:
```
Goal: Increase card adoption by 10%
Current: 3% (target: 10%)
Deviation: -7% (MISS)

Analysis:
  - Email open rate: 15% (expected 20%)
  - Click rate: 2% (expected 3%)
  - Conversion rate: 1% (expected 2%)

Recommendations:
  1. Improve email subject lines (A/B test)
  2. Simplify offer (reduce friction)
  3. Increase frequency (weekly → bi-weekly)
  4. Target higher-engagement segment first
```

---

### 8. Governance Dashboard
Immutable audit trail + Langfuse observability metrics.

**Trigger**: Requests about "audit", "history", or "compliance".

**Output**: Dashboard showing:
- All campaigns executed
- Approvals and rejections
- KPI tracking
- Audit trail
- Compliance status

---

## Architecture

```
Level 4 Agent (src/agents/level4.py)
│
├── Goal Decomposition
│   ├── LLM breaks goal into sub-tasks
│   ├── Identifies required agents (L2, L3, L5)
│   └── Creates execution plan
│
├── Multi-Agent Orchestration
│   ├── Calls Level 2 (segmentation, analytics)
│   ├── Calls Level 3 (notifications, actions)
│   ├── Calls Level 5 (recommendations)
│   └── Coordinates results
│
├── Revenue Impact Analysis
│   ├── Estimates conversions
│   ├── Projects revenue
│   ├── Calculates ROI
│   └── Confidence intervals
│
├── Scenario Simulation
│   ├── Generates alternatives
│   ├── Scores each scenario
│   ├── Recommends best path
│   └── Risk assessment
│
├── Pilot Testing
│   ├── A/B split (50/50)
│   ├── Compliance gate (≤50%)
│   ├── Duration tracking
│   └── Result analysis
│
├── Roadmap Prioritization
│   ├── ROI scoring
│   ├── Effort estimation
│   ├── Dependency analysis
│   └── Timeline planning
│
├── Self-Reflection Loop
│   ├── KPI tracking
│   ├── Deviation detection
│   ├── Root cause analysis
│   └── Plan adjustment
│
├── Governance
│   ├── Audit trail
│   ├── Approval tracking
│   ├── Compliance checks
│   └── Langfuse integration
│
└── Guardrails
    ├── Approval gates
    ├── Risk assessment
    ├── Compliance validation
    └── Audit logging
```

---

## Key Features

### Goal Decomposition
The LLM breaks high-level business goals into 2-4 concrete, executable sub-tasks:

```
Input: "Increase card adoption by 10% in next quarter"

Output:
  1. Segment high-value, non-card customers (Level 2)
  2. Score by engagement and lifetime value (Level 2)
  3. Generate personalized offers (Level 5)
  4. Send targeted emails (Level 3)
  5. Track conversions and adjust (Level 2)
```

### Multi-Agent Coordination
Seamlessly calls other agents and combines results:

```
Level 4 (Strategic)
  ├─→ Level 2: Segment customers
  ├─→ Level 5: Generate recommendations
  ├─→ Level 3: Send notifications
  └─→ Level 2: Track KPIs
```

### Revenue Projection
Estimates financial impact with confidence intervals:

```
Base case: £50,000 revenue
Optimistic: £75,000 (75th percentile)
Pessimistic: £25,000 (25th percentile)
```

### Scenario Comparison
Generates and scores multiple strategies:

```
Strategy A: Email to high-value
  - ROI: 250%
  - Risk: Low
  - Timeline: 2 weeks

Strategy B: SMS to at-risk
  - ROI: 160%
  - Risk: Medium
  - Timeline: 1 week

Recommendation: Strategy A
```

### Pilot Testing
Enforces 50% compliance gate for safe testing:

```
Total segment: 10,000 customers
Control: 5,000 (no action)
Treatment: 5,000 (new strategy)
Duration: 2 weeks
Success metric: 2% conversion rate
```

### Self-Correction
Automatically adjusts strategy when KPIs miss:

```
Target: 10% adoption
Actual: 3%
Deviation: -7%

Trigger: Re-decompose goal
  1. Improve email subject lines
  2. Simplify offer
  3. Increase frequency
  4. Target higher-engagement segment
```

---

## Configuration

### Environment Variables

```bash
# Goal Decomposition
GOAL_DECOMPOSITION_MAX_STEPS=5
GOAL_DECOMPOSITION_TIMEOUT=30s

# Revenue Projection
REVENUE_PROJECTION_CONFIDENCE=0.95
REVENUE_PROJECTION_SCENARIOS=3

# Pilot Testing
PILOT_SPLIT_RATIO=0.5              # 50/50
PILOT_MAX_REACH=0.5                # Max 50% of segment
PILOT_DURATION_DAYS=14

# KPI Tracking
KPI_DEVIATION_THRESHOLD=0.2        # 20% deviation triggers re-decomposition
KPI_CHECK_INTERVAL_DAYS=7

# Approval Gates
APPROVAL_REQUIRED_REACH=1000       # Campaigns > 1,000 reach
APPROVAL_REQUIRED_RISK=0.8         # Risk score > 0.8

# Governance
AUDIT_RETENTION_DAYS=2555          # 7 years
LANGFUSE_ENABLED=true
```

### Scenario Templates

Define scenario templates in `config/scenarios.yaml`:

```yaml
scenarios:
  email_high_value:
    channel: email
    segment: high_value
    offer: premium
    expected_conversion: 0.02
    cost: 0.50
    
  sms_at_risk:
    channel: sms
    segment: at_risk
    offer: retention
    expected_conversion: 0.01
    cost: 0.10
```

---

## Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Goal decomposition | ~5-10s | LLM call |
| Segment analysis (Level 2) | ~2s | SQL + clustering |
| Recommendation generation (Level 5) | ~3s | Collaborative filtering |
| Campaign execution (Level 3) | ~5s | Batch notifications |
| Revenue projection | <1s | Formula-based |
| Scenario simulation (3 scenarios) | ~15s | Parallel execution |
| KPI tracking | <1s | Database query |
| Self-reflection loop | ~20s | Full re-decomposition |

---

## Troubleshooting

### "Goal decomposition too complex"
**Cause**: Goal has too many sub-tasks.

**Solution**: Simplify goal or increase `GOAL_DECOMPOSITION_MAX_STEPS`.

### "Revenue projection unrealistic"
**Cause**: Conversion rate assumptions wrong.

**Solution**: Calibrate with historical data. Adjust `REVENUE_PROJECTION_CONFIDENCE`.

### "Pilot testing blocked"
**Cause**: Segment too small or reach > 50%.

**Solution**: Increase segment size or reduce pilot scope.

### "KPI tracking not updating"
**Cause**: Metrics not being collected.

**Solution**: Verify Level 2 is tracking KPIs. Check `data/audit.jsonl`.

### "Self-reflection loop not triggering"
**Cause**: Deviation below threshold.

**Solution**: Lower `KPI_DEVIATION_THRESHOLD` or wait for next check interval.

---

## API Reference

### Goal Decomposition

```python
from nonagentic.AI.level4 import decompose_goal

plan = decompose_goal("Increase card adoption by 10% in next quarter")
# Returns: {goal, steps, agents_required, timeline, risks}
```

### Multi-Agent Orchestration

```python
from nonagentic.AI.level4 import execute_campaign

result = execute_campaign(
    goal="Increase card adoption by 10%",
    segment="high_value",
    dry_run=False
)
# Returns: {executed, conversions, revenue, roi, audit_id}
```

### Revenue Impact Analysis

```python
from nonagentic.AI.level4 import project_revenue

projection = project_revenue(
    segment_size=10000,
    conversion_rate=0.02,
    avg_order_value=500
)
# Returns: {base_case, optimistic, pessimistic, confidence}
```

### Scenario Simulation

```python
from nonagentic.AI.level4 import simulate_scenarios

scenarios = simulate_scenarios(
    goal="Increase card adoption",
    options=["email", "sms", "push"]
)
# Returns: [{strategy, roi, risk, recommendation}, ...]
```

### Pilot Testing

```python
from nonagentic.AI.level4 import run_pilot

pilot = run_pilot(
    segment="high_value",
    strategy="email_offer",
    duration_days=14
)
# Returns: {control_group, treatment_group, duration, success_metric}
```

### Roadmap Prioritization

```python
from nonagentic.AI.level4 import prioritize_roadmap

roadmap = prioritize_roadmap(initiatives=[...])
# Returns: [{initiative, roi_score, effort, timeline, rank}, ...]
```

### Self-Reflection Loop

```python
from nonagentic.AI.level4 import check_kpi_and_adjust

adjustment = check_kpi_and_adjust(
    goal="Increase card adoption by 10%",
    current_kpi=0.03,
    target_kpi=0.10
)
# Returns: {deviation, analysis, recommendations, new_plan}
```

### Governance Dashboard

```python
from nonagentic.AI.level4 import get_governance_dashboard

dashboard = get_governance_dashboard()
# Returns: {campaigns, approvals, kpis, audit_trail, compliance}
```

---

## Testing

### Unit Tests

```bash
pytest tests/test_agents.py::test_goal_decomposition -v
pytest tests/test_agents.py::test_revenue_projection -v
pytest tests/test_agents.py::test_scenario_simulation -v
```

### Integration Tests

```bash
python -m pytest tests/test_graph.py::test_level4 -v
```

### Notebook Tests

Run all cells in `notebooks/level4_strategic_agent.ipynb`

---

## Deployment

### Production Checklist

- [ ] Configure goal decomposition parameters
- [ ] Set up revenue projection models
- [ ] Define scenario templates
- [ ] Configure pilot testing rules
- [ ] Set KPI tracking metrics
- [ ] Configure approval thresholds
- [ ] Set up Langfuse integration
- [ ] Test multi-agent orchestration
- [ ] Test self-reflection loop
- [ ] Configure audit trail retention

### Scaling Considerations

- Cache goal decompositions for common objectives
- Parallelize scenario simulations
- Use async KPI tracking
- Implement rate limiting for LLM calls
- Monitor approval queue for bottlenecks
- Archive old audit trails (7-year retention)

---

## Resources

- `notebooks/level4_strategic_agent.ipynb` - Interactive demo
- `tests/test_agents.py` - Feature tests
- `specs/04-level4-strategic/` - Detailed specifications
- `data/audit.jsonl` - Audit trail log

---

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review test output: `pytest tests/test_agents.py -v`
3. Check logs in `data/audit.jsonl`
4. Review Langfuse traces (if enabled)

---

**Last Updated**: 2026-03-12  
**Version**: 1.0  
**Status**: Production Ready
