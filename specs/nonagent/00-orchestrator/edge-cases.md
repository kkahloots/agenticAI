# ⚠️ Orchestrator Edge Cases

### What Is NOT

- The orchestrator is not responsible for data storage or external API calls.
- It does not infer sensitive personal attributes or make decisions based on protected data.
- It does not override predefined spending limits or compliance rules.

### Edge Cases and Handling

- **Rate Limit Exceeded**: If an underlying agent hits an API rate limit, the orchestrator backs off and retries after a delay, or asks the user to try later.
- **Tool Failure**: When an agent fails due to tool errors, the orchestrator attempts one retry; if the error persists, it escalates to a human for resolution.
- **Conflicting Histories**: If multiple recent goals conflict, the orchestrator prioritises the latest goal but logs a warning for a human to review.
- **Unknown Intent**: When the classifier cannot determine intent, the orchestrator returns to the user with clarifying questions.
