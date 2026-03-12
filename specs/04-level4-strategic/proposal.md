# 🚀 Level‑4 Strategic Agent Proposal

**TL;DR**: This agent acts like a business strategist. It manages high‑level objectives and orchestrates multiple agents to achieve outcomes such as growing revenue or improving customer satisfaction.

### What & Why (ELI5)

Picture a coach who sets the game plan rather than playing each position. You tell the coach “increase portfolio value by 5 %,” and it coordinates the analysts, marketers and functional assistants to reach that goal. It watches progress and adjusts tactics along the way.

### Formula Rule

`IF goal is broad, outcome‑oriented and spans multiple workflows THEN use strategic agent ELSE fallback.`

### Explanation

The strategic agent is given a high‑level target (e.g. increase adoption or reduce churn). It breaks the objective into sub‑goals, assigns them to lower‑level agents and monitors performance. It uses self‑reflection to refine plans, akin to multi‑agent orchestration described in the overview’s Level 4.

### What Is NOT

- ❌ Not authorised to set its own goals beyond what the user provides.
- ❌ Does not operate completely without oversight; human supervision is still expected.
- ❌ Not a general AI (AGI); it focuses on defined business objectives.

### Edge Cases

- **Goal Ambiguity**: If the goal lacks a clear metric (e.g. “make customers happier”), request a quantifiable target.
- **Resource Conflict**: If multiple campaigns compete for the same customer segment, prioritise based on expected ROI or ask a human to decide.
- **Negative Impact**: If the strategy inadvertently increases churn or risk, pause and notify a human.

### Examples

✅ *“Increase Visa Gold card adoption by 5 % this month.”* → segments customers, selects promotions, orchestrates campaign and monitors results.

✅ *“Improve net promoter score (NPS) by 3 points.”* → initiates a satisfaction survey, analyses feedback and triggers remediation actions.

❌ *“Take over marketing without any human input.”* → not allowed.
