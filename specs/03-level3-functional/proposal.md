# 🤝 Level‑3 Functional Agent Proposal

**TL;DR**: This agent has "hands." It can act on data by connecting to external systems, sending messages and updating records within predefined boundaries.

### What & Why (ELI5)

Think of this agent as an efficient marketing assistant who not only finds the right offer for a customer but can also send an email, open a support case, or run a bulk campaign. It takes the analysis from Level‑2 and turns it into action. It also includes three recommendation engines: upsell (higher-tier products), user-based (segment peer behavior), and collaborative filtering (cross-customer similarity).

### Formula Rule

`IF task requires executing a sequence of tool calls (e.g. customer lookup → score leads → draft email → send notification) THEN use functional agent ELSE fallback.`

### Explanation

The functional agent is responsible for multi‑step tasks that involve tool usage, such as lead generation, return-risk intervention, or identity remediation. It uses LangGraph to manage sequences of calls: fetch data, decide on an action, check gates (consent + identity), and execute. It operates within strict limits on reach and scope.

### What Is NOT

- ❌ Not authorised to make high‑risk decisions (e.g. approve refunds or change fraud scores).
- ❌ Does not set strategic goals; it implements discrete tasks.
- ❌ Cannot perform actions outside integrated tools (e.g. direct database writes).

### Edge Cases

- **Missing Consent**: If `consent_flags.marketing = false`, the agent blocks the notification and logs the skip.
- **Unverified Identity**: If `identity_status = "unverified"`, the agent opens an identity re-verification case instead of proceeding.
- **Action Failure**: When a tool call fails (e.g. notification service down), it retries once and then escalates.
- **High Fraud Score**: If `fraud_score > APPROVAL_RISK_SCORE_THRESHOLD`, the action is flagged for human approval.
- **No Peer Data**: If user-based recommendations find no segment peers, returns empty recommendations with explanation.
- **No Similar Customers**: If collaborative filtering finds no similar customers, returns empty recommendations.
- **Empty Purchase History**: If customer has no purchase categories, upsell returns default segment-based promo.

### Examples

✅ *"Score the top 10 prospects for the Premium Membership offer."* → `score_leads("PROMO-PREMIUM-MEMBERSHIP", top_n=10)`

✅ *"Send a win-back offer to high-return-risk customers."* → filter by `return_risk > 0.7`, check identity + consent, call `send_notification`.

✅ *"Run a bulk campaign for the dormant_vip segment."* → `bulk_recommend("PROMO-WINBACK", segment="dormant_vip")` → execution plan with consent + approval gates.

✅ *"Recommend upsell opportunities for customer CUST-001."* → `upsell_recommend("CUST-001")` → higher-tier categories + best promo.

✅ *"What products should we recommend to customer CUST-042 based on their segment?"* → `user_based_recommend("CUST-042")` → peer-based recommendations.

✅ *"Find similar customers and recommend products for CUST-099."* → `collaborative_recommend("CUST-099")` → collaborative filtering recommendations.

❌ *"Implement a new pricing model."* → outside functional scope.
