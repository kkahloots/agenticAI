# ⚠️ Level‑2 Analytics Agent Edge Cases

### What Is NOT

- Not permitted to update, insert or delete data.
- Does not run machine‑learning training loops (beyond basic clustering for segmentation).

### Edge Cases and Handling

- **Ambiguous Metric**: When terms like “engagement” could have multiple definitions, ask the user to specify (e.g. “number of logins” or “purchase frequency”).
- **Insufficient Data**: If a subset has fewer than 10 records, warn that results may not be reliable.
- **Query Timeout**: If execution exceeds a threshold, cancel the query and ask for a narrower scope.
