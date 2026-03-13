"""Notebook utilities for consistent display and data handling."""

# Display helpers
from .display_helpers import (
    display_card,
    display_metrics,
    display_chunks_table,
    display_bar_chart,
    display_section,
    display_styled_table,
    show_chart,
)

# Visualization
from .visualization import (
    display_side_by_side,
    display_violations_list,
    display_status_banner,
    display_title,
    display_segmentation_results,
    display_sql_analytics_results,
    display_fraud_risk_analysis,
    display_enhanced_sentiment_analysis,
    display_customer_360_view,
    display_sales_analytics_dashboard,
    display_support_analytics_dashboard,
    display_lead_scoring_results,
    display_campaign_execution_plan,
    display_email_search_results,
    display_outcome_analysis,
    display_source_breakdown,
    display_audit_trail,
    display_guardrail_check,
    display_text_summarization,
    display_customer_enrichment,
    display_nba_recommendations,
    display_consent_notification,
    display_kyc_gate,
    display_return_risk_intervention,
    display_blocked_example,
    display_campaign_results_dashboard,
    display_goal_decomposition,
    display_strategic_orchestration,
    display_revenue_impact,
    display_scenario_comparison,
    display_pilot_results,
    display_roadmap_priorities,
    display_governance_dashboard,
    display_kpi_deviation,
    display_kpi_history,
)

# Notebook helpers
from .notebook_helpers import (
    ask,
    show_result,
    display_customer_profile,
    display_identity_status_analysis,
    display_search_results,
    display_policy_qa,
    setup_notebook,
    run_guardrail_demo,
)

# Level 4 strategic helpers
from .strategic_helpers import (
    run_uc2_orchestration,
    run_uc5_pilot,
    run_uc7_reflection,
    run_uc8_langfuse,
    run_uc8_governance,
)

# Level 3 functional helpers
from .level3_helpers import (
    run_lead_scoring,
    run_customer_enrichment,
    run_nba_recommendations,
    run_consent_notification,
    run_identity_gate,
    run_bulk_campaign,
    run_return_risk_intervention,
    run_campaign_dashboard,
    run_guardrails_demo,
)

# Level 5 recommendation helpers
from .rec_charts import plot_similarity_heatmap, plot_score_distribution, plot_category_coverage
from .rec_display import (
    show_rec_table,
    show_sim_table,
    show_eval_metrics,
    show_leakage_table,
)
from .rec_helpers import (
    build_seg_rows,
    build_sim_rows,
    build_collab_rows,
    build_behav_rows,
    build_hybrid_rows,
    build_cold_rows,
    build_seg_batch_rows,
    build_precision_buckets,
)

# Demo data
from .demo_data import (
    get_demo_customers,
    get_test_queries,
    get_high_return_risk_customers
)

__all__ = [
    # Display helpers
    'display_card', 'display_metrics', 'display_chunks_table', 'display_bar_chart',
    'display_section', 'display_styled_table', 'show_chart',
    # Visualization
    'display_side_by_side', 'display_violations_list', 'display_status_banner', 'display_title',
    'display_segmentation_results', 'display_sql_analytics_results', 'display_fraud_risk_analysis',
    'display_enhanced_sentiment_analysis', 'display_customer_360_view',
    'display_sales_analytics_dashboard', 'display_support_analytics_dashboard',
    'display_lead_scoring_results', 'display_campaign_execution_plan',
    'display_email_search_results', 'display_outcome_analysis', 'display_source_breakdown',
    'display_audit_trail', 'display_guardrail_check', 'display_text_summarization',
    'display_customer_enrichment', 'display_nba_recommendations', 'display_consent_notification',
    'display_kyc_gate', 'display_return_risk_intervention', 'display_blocked_example',
    'display_campaign_results_dashboard',
    'display_goal_decomposition', 'display_strategic_orchestration',
    'display_revenue_impact', 'display_scenario_comparison',
    'display_pilot_results', 'display_roadmap_priorities',
    'display_governance_dashboard', 'display_kpi_deviation', 'display_kpi_history',
    # Notebook helpers  
    'ask', 'show_result', 'display_customer_profile', 'display_identity_status_analysis',
    'display_search_results', 'display_policy_qa', 'setup_notebook', 'run_guardrail_demo',
    # Demo data
    'get_demo_customers', 'get_test_queries', 'get_high_return_risk_customers',
    # Level 4 strategic helpers
    'run_uc2_orchestration', 'run_uc5_pilot', 'run_uc7_reflection',
    'run_uc8_langfuse', 'run_uc8_governance',
    # Level 3 functional helpers
    'run_lead_scoring', 'run_customer_enrichment', 'run_nba_recommendations',
    'run_consent_notification', 'run_identity_gate', 'run_bulk_campaign',
    'run_return_risk_intervention', 'run_campaign_dashboard', 'run_guardrails_demo',
    # Level 5 rec display
    'show_rec_table', 'show_sim_table', 'show_eval_metrics', 'show_leakage_table',
    # Level 5 rec charts
    'plot_similarity_heatmap', 'plot_score_distribution', 'plot_category_coverage',
    # Level 5 rec helpers
    'build_seg_rows', 'build_sim_rows', 'build_collab_rows', 'build_behav_rows',
    'build_hybrid_rows', 'build_cold_rows', 'build_seg_batch_rows', 'build_precision_buckets',
]
