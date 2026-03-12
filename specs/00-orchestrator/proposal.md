# 🎯 Orchestrator Proposal

**TL;DR**: The orchestrator is a smart supervisor that decides which specialist agent should handle a user’s goal. It analyses the objective, routes the task to the most appropriate agent, then collects and returns the result.

### What & Why (ELI5)

Imagine a helpful boss who listens to what you want done and then chooses the right assistant for the job. When you say “increase customer engagement,” the boss decides whether to ask the analyst, the marketer, or the strategist. This ensures tasks are handled efficiently without you micromanaging every step.

### Formula Rule

`IF goal complexity ≤ 1 step THEN delegate to Level‑1 agent
ELSE IF goal requires analysis THEN delegate to Level‑2 agent
ELSE IF goal involves performing actions (e.g. emails, offers) THEN delegate to Level‑3 agent
ELSE IF goal is high‑level business objective THEN delegate to Level‑4 agent
ELSE fallback: ask human for clarification.`

### Explanation

The orchestrator uses simple conditions: if the request is just to fetch information, it chooses the knowledge agent; if it needs data analysis, it calls the analytics agent; if it must take an action (like sending an offer), it chooses the functional agent; for open‑ended goals (“grow revenue by 5 %”), it invokes the strategic agent. When the request is unclear, the orchestrator asks a human for more details.

### What Is NOT

- ❌ The orchestrator does **not** perform the tasks itself. It routes tasks but doesn’t query databases or send emails.
- ❌ It is **not** a replacement for human approval on critical decisions (e.g. regulatory compliance or large financial commitments).
- ❌ It does **not** override safety rules or spend outside predefined limits.

### Edge Cases

- **Incomplete Goals**: If the goal lacks key details, the orchestrator asks the user to clarify before routing.
- **Conflicting Objectives**: When multiple objectives clash (e.g. “reduce cost” and “increase service quality” without trade‑off guidance), the orchestrator escalates to a human.
- **Unavailable Agents**: If an agent is offline or fails repeatedly, the orchestrator triggers a safe fallback and notifies the user.

### Examples

✅ *“Retrieve the current credit policy”* → Level‑1 knowledge agent

✅ *“Segment customers with high risk and create an SQL query”* → Level‑2 analytics agent

✅ *“Send a personalised upsell email to John Doe”* → Level‑3 functional agent

✅ *“Grow card adoption by 5 % this quarter”* → Level‑4 strategic agent

❌ *“Buy shares in a company”* → Fallback (outside allowed domain)
