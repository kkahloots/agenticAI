# 📊 Level‑2 Analytics Agent Proposal

**TL;DR**: This agent discovers patterns in data. It generates SQL or Python queries to segment customers, calculate metrics and visualise trends.

### What & Why (ELI5)

Think of this helper as a data detective. If you ask “Who are our most valuable customers?” it writes a query, crunches the numbers and shows you the result. It spots trends like customers likely to churn or segments with high value.

### Formula Rule

`IF request involves calculations, segmentation or pattern discovery THEN use analytics agent ELSE fallback.`

### Explanation

The analytics agent accepts natural‑language questions about data and transforms them into executable SQL or Python. It runs the query, processes the result and summarises the findings. It leverages text‑to‑SQL chains and data visualisation tools.

### What Is NOT

- ❌ Not responsible for sending emails or performing actions beyond calculations.
- ❌ Does not alter the source data; it only analyses.
- ❌ Does not handle cross‑system orchestration; that’s Level‑4’s role.

### Edge Cases

- **Schema Mismatch**: If the requested fields are not in the database, it suggests alternatives.
- **Long‑Running Queries**: For expensive joins, warns the user and asks for confirmation.
- **Data Sparsity**: If there isn’t enough data to support a pattern (e.g. very few customers in a segment), it alerts the user to interpret results cautiously.

### Examples

✅ *“Segment customers based on spending and risk score.”* → writes a SQL query and returns clusters.

✅ *“What is the average transaction volume for customers with expired KYC?”* → computes the metric.

❌ *“Send a marketing email.”* → not an analytics task.
