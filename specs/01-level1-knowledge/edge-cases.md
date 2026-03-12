# 🚧 Level‑1 Knowledge Agent Edge Cases

### What Is NOT

- Not suitable for performing pattern analysis or executing actions.
- Does not make decisions or recommendations.

### Edge Cases and Handling

- **Ambiguous Query**: If the question could refer to multiple documents, ask the user to specify the domain (e.g. “Are you referring to KYC or product catalogue?”).
- **Large Response**: If the summary would exceed a reasonable length, return only key points and provide a link or reference for further reading.
- **Rate‑Limited Source**: When an external API rate limit is hit, inform the user and suggest retrying later.
