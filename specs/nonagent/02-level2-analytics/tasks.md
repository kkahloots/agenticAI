# 🛠️ Level‑2 Analytics Agent Tasks

## Implemented

1. **K-means Customer Segmentation** (`nonagentic/tools/analytics.py: generate_segment`): Cluster customers by `risk_score` and `engagement_score` using scikit-learn KMeans. Falls back to rule-based segmentation when data is insufficient or sklearn is unavailable.

2. **SQL Analytics** (`nonagentic/tools/analytics.py: run_sql_query`): Execute validated read-only SQL against `data/customers.db`. SQL injection guard rejects mutating statements. Row limit controlled by `SQL_MAX_ROWS` env var.

3. **Sentiment Analysis** (`nonagentic/tools/nlp.py: analyze_sentiment`): Classify text as positive/neutral/negative using RoBERTa (`cardiffnlp/twitter-roberta-base-sentiment-latest`). Batch variant: `analyze_batch_sentiment`.

4. **Text Summarization** (`nonagentic/tools/nlp.py: summarize_text`): Generate concise summaries using BART (`facebook/bart-large-cnn`). Returns `compression_ratio`. Skips texts shorter than `min_length` words.

5. **Customer 360 View** (`nonagentic/tools/customer360.py: get_customer_360`): Aggregate CRM profile + sales transactions + social media posts + support tickets into a unified view with summary metrics.

6. **Sales Analytics** (`nonagentic/tools/customer360.py: get_sales_analytics`): Aggregate `data/sales_transactions.json` by `product_category` and `channel`. Returns `total_revenue`, `by_product`, `by_channel`, `top_product`. Generate data with `python scripts/generate_sales_data.py` (898 transactions, 8 categories, 5 channels).

7. **Support Analytics** (`nonagentic/tools/customer360.py: get_support_analytics`): Aggregate `data/support_tickets.json` by type, status, and priority. Returns `avg_resolution_hours` and `high_priority` count.

8. **Visualisation** (`nonagentic/tools/visualisation.py: visualise`): Generate matplotlib bar/line charts saved to `data/charts/`.

## Data Generation Scripts

| Script | Output | Records |
|--------|--------|---------|
| `scripts/cust_dataset_generator.py` | `data/customers.json` | 208 customers |
| `scripts/generate_sales_data.py` | `data/sales_transactions.json` | 898 transactions |
| `scripts/generate_customer360_data.py` | `data/social_media.json`, `data/support_tickets.json` | ~79 posts, ~200 tickets |

## Notebook Utilities

All Level-2 notebook cells use utility functions from `notebooks/utils/visualization_helpers.py`:
- `display_segmentation_results`, `display_sql_analytics_results`, `display_fraud_risk_analysis`
- `display_enhanced_sentiment_analysis`, `display_text_summarization`
- `display_customer_360_view`, `display_sales_analytics_dashboard`, `display_support_analytics_dashboard`
