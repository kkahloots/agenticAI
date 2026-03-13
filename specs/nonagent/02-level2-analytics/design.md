# ⚙️ Level‑2 Analytics Agent Design

### Processing Flow

1. **Intent Parsing**: Classify the question (e.g. aggregation, segmentation, correlation).
2. **Schema Mapping**: Map natural‑language terms to database columns defined in `customer-schema.md`.
3. **Query Generation**: Use LangChain's `create_sql_query_chain` with the live database schema to construct safe SQL queries. Falls back to a raw LLM prompt if the DB is unavailable.
4. **Execution & Retrieval**: Run the query via `run_sql_query` (SQLAlchemy, read-only) and fetch the result set. Row limit controlled by `SQL_MAX_ROWS` env var (default 10 000).
5. **Post‑Processing**: Compute statistics, generate charts (using matplotlib, saved to `data/charts/`) and summarise insights.
6. **Guardrail**: Pass all LLM-generated output through `guardrail_check` before returning to the user. PII and forbidden phrases are redacted automatically.

### Implementation Notes

- `create_sql_query_chain` binds the live DB schema so the LLM generates accurate column names.
- `_llm_fallback_sql` provides a raw-prompt fallback when the DB connection is unavailable.
- SQL injection guard (`_is_safe`) rejects any INSERT / UPDATE / DELETE / DROP before execution.
- All LLM calls go through `nonagentic/core/llm.py` universal factory — provider switchable via `LLM_PROVIDER`.
- For segmentation, apply K-means clustering (scikit-learn) when `algorithm="kmeans"` is specified.
- Sales analytics reads from `data/sales_transactions.json` (898 online store transactions). Generate with `python scripts/generate_sales_data.py`.
- Social and support analytics read from `data/social_media.json` and `data/support_tickets.json`.

### Configurable Parameters

| Env var | Default | Purpose |
|---------|---------|---------|
| `SQL_MAX_ROWS` | 10 000 | Maximum rows returned per query |
| `GUARDRAIL_ENABLED` | true | Toggle constitutional output guardrail |

### Constraints

- Queries must not modify tables (read‑only). Enforced by `_is_safe` regex guard.
- Limit query results to `SQL_MAX_ROWS` rows to ensure performance.
- Human must review analytics output before any downstream action is triggered.
