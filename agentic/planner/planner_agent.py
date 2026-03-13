"""Planner Agent for multi-step reasoning and task decomposition."""

from typing import Optional
import json


class PlannerAgent:
    """Generates execution plans from user requests."""

    def __init__(self, llm=None):
        self.llm = llm

    def plan(self, request: str, context: Optional[dict] = None) -> dict:
        """Generate execution plan from request."""
        if not isinstance(request, str):
            request = str(request)
        request_lower = request.lower()
        context = context or {}

        # ── Level 5 recommendation intents ───────────────────────────────────
        if "user-based" in request_lower or ("segment" in request_lower and "recommend" in request_lower and "batch" not in request_lower):
            return self._plan_user_based_recommendations(request, context)

        if "collaborat" in request_lower:
            return self._plan_collaborative_filtering(request, context)

        if "behaviour" in request_lower or "behavior" in request_lower:
            return self._plan_behaviour_ranking(request, context)

        if "hybrid" in request_lower:
            return self._plan_hybrid_recommender(request, context)

        if "cold start" in request_lower or "cold_start" in request_lower:
            return self._plan_cold_start(request, context)

        if "cross-user" in request_lower or ("segment" in request_lower and "batch" in request_lower):
            return self._plan_cross_segment(request, context)

        if "evaluat" in request_lower and ("recommend" in request_lower or "metric" in request_lower):
            return self._plan_recommendation_evaluation(request, context)

        if "visuali" in request_lower and "recommend" in request_lower:
            return self._plan_recommendation_visualisation(request, context)

        if "routing" in request_lower or ("orchestrat" in request_lower and "recommend" in request_lower):
            return self._plan_orchestrator_routing(request, context)

        # ── Level 3 functional intents ────────────────────────────────────────
        if "lead" in request_lower and "scor" in request_lower:
            return self._plan_lead_scoring(request, context)

        if "enrich" in request_lower:
            return self._plan_enrichment(request, context)

        if "recommend" in request_lower or "nba" in request_lower or "next-best" in request_lower:
            return self._plan_nba(request, context)

        if "notif" in request_lower or "send" in request_lower or "email" in request_lower:
            return self._plan_notification(request, context)

        if "identity" in request_lower or "kyc" in request_lower or "verif" in request_lower:
            return self._plan_identity_gate(request, context)

        if "bulk" in request_lower or ("campaign" in request_lower and "target" in request_lower):
            return self._plan_bulk_campaign(request, context)

        if "return" in request_lower and "risk" in request_lower:
            return self._plan_return_risk(request, context)

        if "dashboard" in request_lower or ("campaign" in request_lower and "result" in request_lower):
            return self._plan_campaign_dashboard(request, context)

        if "guardrail" in request_lower or "pii" in request_lower or "redact" in request_lower:
            return self._plan_guardrails(request, context)

        return self._plan_generic(request, context)

    # ── Level 5 plan methods ──────────────────────────────────────────────────

    def _plan_user_based_recommendations(self, request: str, context: Optional[dict]) -> dict:
        return {
            "goal": "Recommend products based on segment peer behaviour",
            "intent": "user_based_recommendations",
            "subtasks": [
                {"step_id": 1, "action": "get_customer_profile",
                 "reason": "Retrieve customer segment and attributes",
                 "agent": "recommendation_agent",
                 "candidate_tools": ["get_customer_profile", "get_customer_segment"]},
                {"step_id": 2, "action": "segment_recommendations",
                 "reason": "Find top products popular among segment peers",
                 "agent": "recommendation_agent",
                 "candidate_tools": ["segment_recommendations"]},
            ],
            "requires_sql": False,
            "requires_llm_reasoning": False,
            "selected_agents": ["recommendation_agent"],
            "selected_models": ["segment_model"],
            "risk_flags": [],
            "expected_output_type": "recommendation_list",
        }

    def _plan_collaborative_filtering(self, request: str, context: Optional[dict]) -> dict:
        return {
            "goal": "Find similar users and recommend products they liked",
            "intent": "collaborative_filtering",
            "subtasks": [
                {"step_id": 1, "action": "build_user_item_matrix",
                 "reason": "Compute interaction vectors for similarity",
                 "agent": "recommendation_agent",
                 "candidate_tools": ["build_user_item_matrix"]},
                {"step_id": 2, "action": "collaborative_scores",
                 "reason": "Compute cosine similarity and score candidates",
                 "agent": "recommendation_agent",
                 "candidate_tools": ["collaborative_scores"]},
            ],
            "requires_sql": False,
            "requires_llm_reasoning": False,
            "selected_agents": ["recommendation_agent"],
            "selected_models": ["collaborative_model"],
            "risk_flags": [],
            "expected_output_type": "recommendation_list",
        }

    def _plan_behaviour_ranking(self, request: str, context: Optional[dict]) -> dict:
        return {
            "goal": "Rank products by customer behaviour and content signals",
            "intent": "behaviour_based_ranking",
            "subtasks": [
                {"step_id": 1, "action": "select_features",
                 "reason": "Choose relevant features for this customer",
                 "agent": "recommendation_agent",
                 "candidate_tools": ["select_features", "suggest_feature_priority"]},
                {"step_id": 2, "action": "behaviour_scores",
                 "reason": "Compute behaviour and content scores",
                 "agent": "recommendation_agent",
                 "candidate_tools": ["behaviour_scores"]},
            ],
            "requires_sql": False,
            "requires_llm_reasoning": True,
            "selected_agents": ["recommendation_agent"],
            "selected_models": ["behaviour_model", "content_model"],
            "risk_flags": [],
            "expected_output_type": "scored_product_list",
        }

    def _plan_hybrid_recommender(self, request: str, context: Optional[dict]) -> dict:
        return {
            "goal": "Generate hybrid recommendations combining all signals",
            "intent": "hybrid_recommender",
            "subtasks": [
                {"step_id": 1, "action": "choose_strategy",
                 "reason": "Determine best combination of signals",
                 "agent": "recommendation_strategy_agent",
                 "candidate_tools": ["choose_recommendation_strategy", "classify_recommendation_request"]},
                {"step_id": 2, "action": "hybrid_recommend",
                 "reason": "Run weighted hybrid scoring",
                 "agent": "recommendation_agent",
                 "candidate_tools": ["hybrid_recommend"]},
                {"step_id": 3, "action": "explain_recommendations",
                 "reason": "Generate explanation for dominant signal",
                 "agent": "recommendation_agent",
                 "candidate_tools": ["explain_recommendation"]},
            ],
            "requires_sql": False,
            "requires_llm_reasoning": True,
            "selected_agents": ["recommendation_strategy_agent", "recommendation_agent"],
            "selected_models": ["hybrid_ranker"],
            "risk_flags": [],
            "expected_output_type": "recommendation_list_with_explanations",
        }

    def _plan_cold_start(self, request: str, context: Optional[dict]) -> dict:
        return {
            "goal": "Handle cold start with fallback recommendations",
            "intent": "cold_start_handling",
            "subtasks": [
                {"step_id": 1, "action": "detect_cold_start",
                 "reason": "Check interaction history to confirm cold start",
                 "agent": "recommendation_agent",
                 "candidate_tools": ["get_customer_history"]},
                {"step_id": 2, "action": "cold_start_recommend",
                 "reason": "Apply segment fallback or popularity fallback",
                 "agent": "recommendation_agent",
                 "candidate_tools": ["cold_start_recommend", "popularity_scores", "segment_recommendations"]},
            ],
            "requires_sql": False,
            "requires_llm_reasoning": True,
            "selected_agents": ["recommendation_agent"],
            "selected_models": ["segment_model", "popularity_model"],
            "risk_flags": [],
            "expected_output_type": "fallback_recommendation_list",
        }

    def _plan_cross_segment(self, request: str, context: Optional[dict]) -> dict:
        return {
            "goal": "Generate recommendations for all customers in a segment",
            "intent": "cross_user_segment_recommendations",
            "subtasks": [
                {"step_id": 1, "action": "identify_segment_members",
                 "reason": "Find all customers in target segment",
                 "agent": "analytics_agent",
                 "candidate_tools": ["run_sql_query", "get_customer_segment"]},
                {"step_id": 2, "action": "segment_batch_recommend",
                 "reason": "Run recommendations for sampled segment members",
                 "agent": "recommendation_agent",
                 "candidate_tools": ["segment_batch_recommend"]},
                {"step_id": 3, "action": "aggregate_results",
                 "reason": "Aggregate top products across segment",
                 "agent": "analytics_agent",
                 "candidate_tools": ["build_segment_recommendation_stats"]},
            ],
            "requires_sql": True,
            "requires_llm_reasoning": False,
            "selected_agents": ["analytics_agent", "recommendation_agent"],
            "selected_models": ["hybrid_ranker"],
            "risk_flags": [],
            "expected_output_type": "segment_recommendation_table",
        }

    def _plan_recommendation_evaluation(self, request: str, context: Optional[dict]) -> dict:
        return {
            "goal": "Evaluate recommendation quality with offline metrics",
            "intent": "recommendation_evaluation",
            "subtasks": [
                {"step_id": 1, "action": "detect_data_leakage",
                 "reason": "Check for train/test overlap before evaluation",
                 "agent": "analytics_agent",
                 "candidate_tools": ["detect_data_leakage"]},
                {"step_id": 2, "action": "evaluate_recommendations",
                 "reason": "Compute precision, recall, MAP, NDCG",
                 "agent": "analytics_agent",
                 "candidate_tools": ["evaluate_recommendations"]},
            ],
            "requires_sql": False,
            "requires_llm_reasoning": False,
            "selected_agents": ["analytics_agent", "evaluation_agent"],
            "selected_models": [],
            "risk_flags": [],
            "expected_output_type": "evaluation_metrics",
        }

    def _plan_recommendation_visualisation(self, request: str, context: Optional[dict]) -> dict:
        return {
            "goal": "Generate visual summaries of recommendation engine",
            "intent": "recommendation_visualisation",
            "subtasks": [
                {"step_id": 1, "action": "compute_similarity_stats",
                 "reason": "Build user similarity data for heatmap",
                 "agent": "analytics_agent",
                 "candidate_tools": ["build_similarity_matrix_stats"]},
                {"step_id": 2, "action": "compute_score_distribution",
                 "reason": "Compute score distribution across customers",
                 "agent": "analytics_agent",
                 "candidate_tools": ["build_segment_recommendation_stats"]},
                {"step_id": 3, "action": "plot_charts",
                 "reason": "Render visualisations",
                 "agent": "analytics_agent",
                 "candidate_tools": ["plot_user_similarity_heatmap", "plot_score_distribution",
                                     "plot_category_coverage"]},
            ],
            "requires_sql": False,
            "requires_llm_reasoning": False,
            "selected_agents": ["analytics_agent"],
            "selected_models": [],
            "risk_flags": [],
            "expected_output_type": "charts",
        }

    def _plan_orchestrator_routing(self, request: str, context: Optional[dict]) -> dict:
        return {
            "goal": "Route recommendation request to correct agent",
            "intent": "orchestrator_routing",
            "subtasks": [
                {"step_id": 1, "action": "classify_intent",
                 "reason": "Determine recommendation intent from request",
                 "agent": "recommendation_strategy_agent",
                 "candidate_tools": ["classify_recommendation_request"]},
                {"step_id": 2, "action": "route_to_agent",
                 "reason": "Dispatch to appropriate recommendation agent",
                 "agent": "orchestrator",
                 "candidate_tools": ["recommendation_agent", "analytics_agent"]},
            ],
            "requires_sql": False,
            "requires_llm_reasoning": True,
            "selected_agents": ["recommendation_strategy_agent", "orchestrator"],
            "selected_models": [],
            "risk_flags": [],
            "expected_output_type": "routing_decision",
        }

    # ── Level 3 plan methods (unchanged) ─────────────────────────────────────

    def _plan_lead_scoring(self, request: str, context: Optional[dict]) -> dict:
        return {
            "goal": "Score and rank leads for offer",
            "intent": "lead_scoring",
            "subtasks": [
                {"step_id": 1, "action": "score_leads",
                 "reason": "Identify top prospects based on engagement and fit",
                 "agent": "recommendation_agent",
                 "candidate_tools": ["score_leads", "customer_search"]},
            ],
            "requires_sql": False,
            "selected_agents": ["recommendation_agent"],
            "risk_flags": [],
            "expected_output_type": "lead_list",
        }

    def _plan_enrichment(self, request: str, context: Optional[dict]) -> dict:
        return {
            "goal": "Enrich customer profile with multi-source data",
            "intent": "customer_enrichment",
            "subtasks": [
                {"step_id": 1, "action": "lookup_customer",
                 "reason": "Get base customer profile",
                 "agent": "functional_agent",
                 "candidate_tools": ["search_customer_profile"]},
                {"step_id": 2, "action": "enrich_customer",
                 "reason": "Add enrichment data from external sources",
                 "agent": "functional_agent",
                 "candidate_tools": ["enrich_customer"]},
            ],
            "requires_sql": False,
            "selected_agents": ["functional_agent"],
            "risk_flags": [],
            "expected_output_type": "enriched_profile",
        }

    def _plan_nba(self, request: str, context: Optional[dict]) -> dict:
        return {
            "goal": "Recommend next-best-action for customer",
            "intent": "nba_recommendation",
            "subtasks": [
                {"step_id": 1, "action": "lookup_customer",
                 "reason": "Get customer profile and preferences",
                 "agent": "recommendation_agent",
                 "candidate_tools": ["search_customer_profile"]},
                {"step_id": 2, "action": "recommend_offer",
                 "reason": "Score and rank offers for customer",
                 "agent": "recommendation_agent",
                 "candidate_tools": ["recommend_offer", "rank_next_best_action"]},
                {"step_id": 3, "action": "check_consent",
                 "reason": "Verify marketing consent before recommendation",
                 "agent": "compliance_agent",
                 "candidate_tools": ["check_marketing_consent"]},
            ],
            "requires_sql": False,
            "selected_agents": ["recommendation_agent", "compliance_agent"],
            "risk_flags": [],
            "expected_output_type": "offer_recommendation",
        }

    def _plan_notification(self, request: str, context: Optional[dict]) -> dict:
        return {
            "goal": "Send notification with consent verification",
            "intent": "consent_gated_notification",
            "subtasks": [
                {"step_id": 1, "action": "recommend_offer",
                 "reason": "Determine best offer for customer",
                 "agent": "recommendation_agent",
                 "candidate_tools": ["recommend_offer"]},
                {"step_id": 2, "action": "draft_message",
                 "reason": "Create notification content",
                 "agent": "functional_agent",
                 "candidate_tools": ["draft_email"]},
                {"step_id": 3, "action": "check_consent",
                 "reason": "Verify consent before sending",
                 "agent": "compliance_agent",
                 "candidate_tools": ["check_marketing_consent"]},
                {"step_id": 4, "action": "send_notification",
                 "reason": "Deliver notification via approved channel",
                 "agent": "functional_agent",
                 "candidate_tools": ["send_notification", "simulate_notification"]},
            ],
            "requires_sql": False,
            "selected_agents": ["recommendation_agent", "functional_agent", "compliance_agent"],
            "risk_flags": ["requires_consent"],
            "expected_output_type": "notification_result",
        }

    def _plan_identity_gate(self, request: str, context: Optional[dict]) -> dict:
        return {
            "goal": "Verify identity status and create remediation case if needed",
            "intent": "identity_gate",
            "subtasks": [
                {"step_id": 1, "action": "check_identity",
                 "reason": "Verify customer identity status",
                 "agent": "compliance_agent",
                 "candidate_tools": ["get_kyc_status", "check_identity_gate"]},
                {"step_id": 2, "action": "create_case",
                 "reason": "Open remediation case if identity unverified",
                 "agent": "functional_agent",
                 "candidate_tools": ["create_case"]},
            ],
            "requires_sql": False,
            "selected_agents": ["compliance_agent", "functional_agent"],
            "risk_flags": ["requires_identity_check"],
            "expected_output_type": "identity_verification",
        }

    def _plan_bulk_campaign(self, request: str, context: Optional[dict]) -> dict:
        return {
            "goal": "Generate bulk campaign targeting plan",
            "intent": "bulk_campaign_targeting",
            "subtasks": [
                {"step_id": 1, "action": "identify_audience",
                 "reason": "Find target customers matching criteria",
                 "agent": "analytics_agent",
                 "candidate_tools": ["generate_segment", "run_sql_query"]},
                {"step_id": 2, "action": "bulk_recommend",
                 "reason": "Score and rank all prospects",
                 "agent": "recommendation_agent",
                 "candidate_tools": ["bulk_recommend", "score_leads"]},
                {"step_id": 3, "action": "validate_compliance",
                 "reason": "Check consent and identity for all targets",
                 "agent": "compliance_agent",
                 "candidate_tools": ["check_marketing_consent", "check_identity_gate"]},
                {"step_id": 4, "action": "build_execution_plan",
                 "reason": "Create campaign execution summary",
                 "agent": "functional_agent",
                 "candidate_tools": ["build_campaign_execution_plan"]},
            ],
            "requires_sql": True,
            "selected_agents": ["analytics_agent", "recommendation_agent", "compliance_agent", "functional_agent"],
            "risk_flags": ["bulk_operation"],
            "expected_output_type": "campaign_plan",
        }

    def _plan_return_risk(self, request: str, context: Optional[dict]) -> dict:
        return {
            "goal": "Identify high-return-risk customers and intervene",
            "intent": "return_risk_intervention",
            "subtasks": [
                {"step_id": 1, "action": "identify_at_risk",
                 "reason": "Find customers with high return risk",
                 "agent": "analytics_agent",
                 "candidate_tools": ["identify_high_return_risk", "run_sql_query"]},
                {"step_id": 2, "action": "filter_by_identity",
                 "reason": "Ensure identity verified",
                 "agent": "compliance_agent",
                 "candidate_tools": ["check_identity_gate"]},
                {"step_id": 3, "action": "filter_by_consent",
                 "reason": "Verify marketing consent",
                 "agent": "compliance_agent",
                 "candidate_tools": ["check_marketing_consent"]},
                {"step_id": 4, "action": "send_intervention",
                 "reason": "Contact at-risk customers",
                 "agent": "functional_agent",
                 "candidate_tools": ["send_notification", "simulate_notification"]},
            ],
            "requires_sql": True,
            "selected_agents": ["analytics_agent", "compliance_agent", "functional_agent"],
            "risk_flags": ["high_risk_customers"],
            "expected_output_type": "intervention_list",
        }

    def _plan_campaign_dashboard(self, request: str, context: Optional[dict]) -> dict:
        return {
            "goal": "Analyze campaign performance metrics",
            "intent": "campaign_dashboard",
            "subtasks": [
                {"step_id": 1, "action": "query_campaign_results",
                 "reason": "Retrieve campaign performance data",
                 "agent": "analytics_agent",
                 "candidate_tools": ["campaign_performance_summary", "run_sql_query"]},
                {"step_id": 2, "action": "analyze_results",
                 "reason": "Generate insights and visualizations",
                 "agent": "analytics_agent",
                 "candidate_tools": ["generate_segment"]},
            ],
            "requires_sql": True,
            "selected_agents": ["analytics_agent"],
            "risk_flags": [],
            "expected_output_type": "dashboard_data",
        }

    def _plan_guardrails(self, request: str, context: Optional[dict]) -> dict:
        return {
            "goal": "Apply guardrails and redact PII",
            "intent": "guardrails",
            "subtasks": [
                {"step_id": 1, "action": "guardrail_check",
                 "reason": "Scan for PII and policy violations",
                 "agent": "compliance_agent",
                 "candidate_tools": ["guardrail_check", "redact_pii"]},
            ],
            "requires_sql": False,
            "selected_agents": ["compliance_agent"],
            "risk_flags": ["pii_present"],
            "expected_output_type": "sanitized_output",
        }

    def _plan_generic(self, request: str, context: Optional[dict]) -> dict:
        return {
            "goal": "Process generic request",
            "intent": "generic",
            "subtasks": [
                {"step_id": 1, "action": "process_request",
                 "reason": "Handle request with appropriate agent",
                 "agent": "functional_agent",
                 "candidate_tools": []},
            ],
            "requires_sql": False,
            "selected_agents": ["functional_agent"],
            "risk_flags": [],
            "expected_output_type": "generic",
        }


def create_planner(llm=None) -> PlannerAgent:
    """Create a planner agent instance."""
    return PlannerAgent(llm=llm)
