"""
tests/agentic/test_level5_agentic.py

Covers all Step 15 test categories:
  1. Planner tests
  2. Registry discovery tests
  3. SQL generation safety tests
  4. MCP tool tests
  5. LLM classifier / feature reasoner contract tests
  6. Output parity tests (UC1–UC9)
"""

import os
import pytest

os.environ["GUARDRAIL_ENABLED"] = "false"

# ─────────────────────────────────────────────────────────────────────────────
# 1. PLANNER TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestPlanner:
    """Planner routes all 9 Level 5 intents correctly."""

    @pytest.fixture(autouse=True)
    def planner(self):
        from agentic.planner.planner_agent import create_planner
        self.p = create_planner()

    def _plan(self, req):
        return self.p.plan(req)

    def test_uc1_user_based(self):
        plan = self._plan("User-based segment recommendations for CUST-001")
        assert plan["intent"] == "user_based_recommendations"
        assert any("segment" in t["action"] for t in plan["subtasks"])

    def test_uc2_collaborative(self):
        plan = self._plan("Collaborative filtering recommendations for CUST-001")
        assert plan["intent"] == "collaborative_filtering"
        assert any("collaborative" in t["action"] for t in plan["subtasks"])

    def test_uc3_behaviour(self):
        plan = self._plan("Behaviour-based ranking for CUST-001")
        assert plan["intent"] == "behaviour_based_ranking"
        assert plan["requires_llm_reasoning"] is True

    def test_uc4_hybrid(self):
        plan = self._plan("Hybrid recommendations for CUST-001")
        assert plan["intent"] == "hybrid_recommender"
        assert "hybrid_ranker" in plan["selected_models"]

    def test_uc5_cold_start(self):
        plan = self._plan("Cold start recommendations for CUST-NEW")
        assert plan["intent"] == "cold_start_handling"

    def test_uc6_cross_segment(self):
        plan = self._plan("Cross-user segment batch recommendations for dormant_vip")
        assert plan["intent"] == "cross_user_segment_recommendations"
        assert plan["requires_sql"] is True

    def test_uc7_evaluation(self):
        plan = self._plan("Evaluate recommendation metrics")
        assert plan["intent"] == "recommendation_evaluation"
        assert "analytics_agent" in plan["selected_agents"]

    def test_uc8_visualisation(self):
        plan = self._plan("Visualise recommendation engine for CUST-001")
        assert plan["intent"] == "recommendation_visualisation"

    def test_uc9_routing(self):
        plan = self._plan("Routing test: orchestrator routing for recommendations")
        assert plan["intent"] == "orchestrator_routing"

    def test_plan_schema_complete(self):
        plan = self._plan("Hybrid recommendations for CUST-001")
        for key in ("goal", "intent", "subtasks", "requires_sql",
                    "requires_llm_reasoning", "selected_agents",
                    "selected_models", "risk_flags", "expected_output_type"):
            assert key in plan, f"Missing key: {key}"

    def test_subtask_schema_complete(self):
        plan = self._plan("Collaborative filtering recommendations for CUST-001")
        for subtask in plan["subtasks"]:
            for key in ("step_id", "action", "reason", "agent", "candidate_tools"):
                assert key in subtask, f"Missing subtask key: {key}"


# ─────────────────────────────────────────────────────────────────────────────
# 2. REGISTRY DISCOVERY TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestRegistry:
    """Tool registry supports dynamic discovery."""

    @pytest.fixture(autouse=True)
    def registry(self):
        from agentic.registry.tool_registry import ToolRegistry, ToolMetadata
        self.reg = ToolRegistry()
        # Register sample tools
        for name, cat, model in [
            ("collaborative_scores",   "recommendation", "collaborative"),
            ("behaviour_scores",       "recommendation", "behaviour"),
            ("hybrid_recommend",       "recommendation", "hybrid"),
            ("segment_recommendations","recommendation", "segment"),
            ("popularity_scores",      "recommendation", "popularity"),
            ("run_sql_query",          "analytics",      ""),
            ("evaluate_recommendations","analytics",     ""),
        ]:
            self.reg.register(ToolMetadata(
                tool_name=name, category=cat, description=f"{name} tool",
                input_schema={}, output_schema={}, model_type=model,
            ))

    def test_list_tools_returns_all(self):
        assert len(self.reg.list_tools()) == 7

    def test_list_by_category(self):
        rec_tools = self.reg.list_tools_by_category("recommendation")
        assert "collaborative_scores" in rec_tools
        assert "run_sql_query" not in rec_tools

    def test_find_tools_for_action(self):
        matches = self.reg.find_tools_for_action("collaborative")
        assert "collaborative_scores" in matches

    def test_find_tools_for_model_type(self):
        hybrids = self.reg.find_tools_for_model_type("hybrid")
        assert "hybrid_recommend" in hybrids

    def test_get_tool_metadata(self):
        meta = self.reg.get_tool_metadata("behaviour_scores")
        assert meta is not None
        assert meta.model_type == "behaviour"

    def test_get_unknown_tool_returns_none(self):
        assert self.reg.get_tool_metadata("nonexistent") is None

    def test_execute_tool_no_handler(self):
        result = self.reg.execute_tool("collaborative_scores", {})
        assert result.get("error") == "no_handler" or result.get("execution_status") == "failed"

    def test_execute_unknown_tool(self):
        result = self.reg.execute_tool("ghost_tool", {})
        assert result.get("error") == "tool_not_found"


# ─────────────────────────────────────────────────────────────────────────────
# 3. SQL GENERATION SAFETY TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestSQLGenerator:
    """SQL generator produces safe read-only queries."""

    @pytest.fixture(autouse=True)
    def gen(self):
        from agentic.sql.sql_generator import create_sql_generator
        self.gen = create_sql_generator()

    def test_dormant_vip_query(self):
        result = self.gen.generate("Find all customers in dormant_vip segment")
        assert result.get("safe") is True
        assert "dormant_vip" in result["query"].lower()

    def test_segment_query(self):
        result = self.gen.generate("Find customers in vip segment")
        assert result.get("safe") is True

    def test_return_risk_query(self):
        result = self.gen.generate("Find high return risk customers", {"threshold": 0.7})
        assert result.get("safe") is True

    def test_campaign_performance_query(self):
        result = self.gen.generate("Show campaign performance results")
        assert result.get("safe") is True

    def test_rejects_insert(self):
        result = self.gen.generate("INSERT INTO customers VALUES (1)")
        assert result.get("error") == "forbidden_operation"

    def test_rejects_delete(self):
        result = self.gen.generate("DELETE FROM customers")
        assert result.get("error") == "forbidden_operation"

    def test_rejects_drop(self):
        result = self.gen.generate("DROP TABLE customers")
        assert result.get("error") == "forbidden_operation"

    def test_rejects_update(self):
        result = self.gen.generate("UPDATE customers SET segment='vip'")
        assert result.get("error") == "forbidden_operation"

    def test_validate_select_is_valid(self):
        q = "SELECT customer_id FROM customers WHERE segment = 'vip'"
        result = self.gen.validate(q)
        assert result["valid"] is True

    def test_validate_non_select_is_invalid(self):
        q = "DELETE FROM customers"
        result = self.gen.validate(q)
        assert result["valid"] is False


# ─────────────────────────────────────────────────────────────────────────────
# 4. MCP TOOL TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestMCPTools:
    """All MCP tools return execution_status: success."""

    def test_segment_recommendations(self):
        from agentic.mcp.recommendation_server import segment_recommendations
        r = segment_recommendations("casual", top_k=5)
        assert r["execution_status"] == "success"
        assert isinstance(r["result"], list)

    def test_collaborative_scores(self):
        from agentic.mcp.recommendation_server import collaborative_scores
        r = collaborative_scores("CUST-001", top_k=5)
        assert r["execution_status"] == "success"
        assert "similar_users" in r["result"]

    def test_behaviour_scores(self):
        from agentic.mcp.recommendation_server import behaviour_scores
        r = behaviour_scores("CUST-001", top_k=5)
        assert r["execution_status"] == "success"

    def test_hybrid_recommend(self):
        from agentic.mcp.recommendation_server import hybrid_recommend
        r = hybrid_recommend("CUST-001", top_k=5)
        assert r["execution_status"] == "success"
        assert "recommendations" in r["result"]

    def test_cold_start_recommend(self):
        from agentic.mcp.recommendation_server import cold_start_recommend
        r = cold_start_recommend("CUST-NEW", "dormant_vip", top_k=5)
        assert r["execution_status"] == "success"

    def test_segment_batch_recommend(self):
        from agentic.mcp.recommendation_server import segment_batch_recommend
        r = segment_batch_recommend("dormant_vip", top_k=5, sample_size=5)
        assert r["execution_status"] == "success"

    def test_popularity_scores(self):
        from agentic.mcp.recommendation_server import popularity_scores
        r = popularity_scores(top_k=5)
        assert r["execution_status"] == "success"
        assert len(r["result"]) <= 5

    def test_evaluate_recommendations(self):
        from agentic.mcp.recommendation_server import evaluate_recommendations
        r = evaluate_recommendations(sample_users=5, k=5)
        assert r["execution_status"] == "success"

    def test_detect_data_leakage(self):
        from agentic.mcp.recommendation_server import detect_data_leakage
        r = detect_data_leakage(sample_users=3)
        assert r["execution_status"] == "success"

    def test_analytics_run_sql(self):
        from agentic.mcp.analytics_server import run_sql_query
        r = run_sql_query("SELECT customer_id FROM customers WHERE segment = 'dormant_vip'")
        assert r["execution_status"] == "success"

    def test_analytics_similarity_stats(self):
        from agentic.mcp.analytics_server import build_similarity_matrix_stats
        r = build_similarity_matrix_stats("CUST-001", top_k=5)
        assert r["execution_status"] == "success"
        assert "top_similar" in r["result"]

    def test_analytics_segment_stats(self):
        from agentic.mcp.analytics_server import build_segment_recommendation_stats
        r = build_segment_recommendation_stats("casual", sample_size=5)
        assert r["execution_status"] == "success"

    def test_mcp_tool_audit_metadata(self):
        from agentic.mcp.recommendation_server import segment_recommendations
        r = segment_recommendations("casual", top_k=3)
        assert "tool_name" in r
        assert "audit" in r


# ─────────────────────────────────────────────────────────────────────────────
# 5. LLM CLASSIFIER / FEATURE REASONER CONTRACT TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestLLMClassifier:
    """LLM classifier returns valid strategy classifications."""

    VALID_STRATEGIES = {
        "collaborative", "behaviour", "content", "hybrid",
        "cold_start", "segment_batch", "evaluation", "visualization",
    }

    @pytest.fixture(autouse=True)
    def clf(self):
        from agentic.models.llm_classifier import create_llm_classifier
        self.clf = create_llm_classifier()

    def test_classify_collaborative(self):
        r = self.clf.classify("Find similar users to CUST-001")
        assert r["strategy"] in self.VALID_STRATEGIES

    def test_classify_cold_start(self):
        r = self.clf.classify("Cold start recommendations", {"interaction_count": 0})
        assert r["strategy"] == "cold_start"

    def test_classify_evaluation(self):
        r = self.clf.classify("Evaluate recommendation metrics")
        assert r["strategy"] == "evaluation"

    def test_classify_visualization(self):
        r = self.clf.classify("Show similarity chart")
        assert r["strategy"] == "visualization"

    def test_is_cold_start_true(self):
        assert self.clf.is_cold_start({"interaction_count": 2}) is True

    def test_is_cold_start_false(self):
        assert self.clf.is_cold_start({"interaction_count": 10}) is False

    def test_is_collaborative_ready(self):
        assert self.clf.is_collaborative_ready({"interaction_count": 15}) is True
        assert self.clf.is_collaborative_ready({"interaction_count": 5}) is False

    def test_classify_returns_confidence(self):
        r = self.clf.classify("Recommend products for CUST-001")
        assert "confidence" in r


class TestLLMFeatureReasoner:
    """LLM feature reasoner returns valid feature suggestions."""

    @pytest.fixture(autouse=True)
    def reasoner(self):
        from agentic.models.llm_feature_reasoner import create_llm_feature_reasoner
        self.r = create_llm_feature_reasoner()

    def test_suggest_features_returns_list(self):
        features = self.r.suggest_features("CUST-001", {"engagement_score": 0.6,
                                                         "purchase_categories": ["books"]})
        assert isinstance(features, list)
        assert len(features) > 0

    def test_suggest_features_have_priority(self):
        features = self.r.suggest_features("CUST-001", {"engagement_score": 0.6,
                                                         "purchase_categories": ["books"]})
        for f in features:
            assert "feature" in f
            assert "priority" in f

    def test_propose_weights_simulation_only(self):
        weights = {"collaborative": 0.4, "behaviour": 0.3, "content": 0.2, "popularity": 0.1}
        result = self.r.propose_weights(weights, {"ndcg": 0.05})
        assert "simulation_only" in result
        assert result["simulation_only"] is True
        assert "proposed_weights" in result

    def test_select_features_deterministic(self):
        features = self.r.select_feature_subset(
            "CUST-001",
            {"interaction_count": 10, "purchase_categories": ["books"]},
            mode="deterministic",
        )
        assert isinstance(features, list)
        assert "behaviour" in features

    def test_select_features_dynamic(self):
        features = self.r.select_feature_subset(
            "CUST-001",
            {"interaction_count": 10, "purchase_categories": ["books"]},
            mode="dynamic",
        )
        assert isinstance(features, list)


# ─────────────────────────────────────────────────────────────────────────────
# 6. OUTPUT PARITY TESTS (UC1–UC9)
# ─────────────────────────────────────────────────────────────────────────────

class TestOutputParity:
    """Dynamic agentic results are structurally compatible with baseline."""

    @pytest.fixture(autouse=True)
    def api(self):
        from agentic.utils.agentic_api import create_api
        self.api = create_api()

    def _check_result(self, result):
        """Assert common result schema."""
        assert "request_id" in result
        assert "mode" in result
        assert "plan" in result
        assert "agent_path" in result
        assert isinstance(result["agent_path"], list)

    def test_uc1_deterministic(self):
        r = self.api.execute_rec_uc1_user_based("CUST-001", "casual", top_k=5, mode="deterministic")
        self._check_result(r)
        assert r["mode"] == "deterministic"

    def test_uc1_dynamic(self):
        r = self.api.execute_rec_uc1_user_based("CUST-001", "casual", top_k=5, mode="dynamic")
        self._check_result(r)
        assert r["mode"] == "dynamic"

    def test_uc2_deterministic(self):
        r = self.api.execute_rec_uc2_collaborative("CUST-001", top_k=5, mode="deterministic")
        self._check_result(r)

    def test_uc2_dynamic(self):
        r = self.api.execute_rec_uc2_collaborative("CUST-001", top_k=5, mode="dynamic")
        self._check_result(r)

    def test_uc3_deterministic(self):
        r = self.api.execute_rec_uc3_behaviour("CUST-001", top_k=5, mode="deterministic")
        self._check_result(r)

    def test_uc3_dynamic(self):
        r = self.api.execute_rec_uc3_behaviour("CUST-001", top_k=5, mode="dynamic")
        self._check_result(r)

    def test_uc4_deterministic(self):
        r = self.api.execute_rec_uc4_hybrid("CUST-001", top_k=5, mode="deterministic")
        self._check_result(r)

    def test_uc4_dynamic(self):
        r = self.api.execute_rec_uc4_hybrid("CUST-001", top_k=5, mode="dynamic")
        self._check_result(r)

    def test_uc5_deterministic(self):
        r = self.api.execute_rec_uc5_cold_start("CUST-NEW", "dormant_vip", top_k=5, mode="deterministic")
        self._check_result(r)

    def test_uc5_dynamic(self):
        r = self.api.execute_rec_uc5_cold_start("CUST-NEW", "dormant_vip", top_k=5, mode="dynamic")
        self._check_result(r)

    def test_uc6_deterministic(self):
        r = self.api.execute_rec_uc6_cross_segment("dormant_vip", top_k=5, sample_size=5, mode="deterministic")
        self._check_result(r)

    def test_uc6_dynamic(self):
        r = self.api.execute_rec_uc6_cross_segment("dormant_vip", top_k=5, sample_size=5, mode="dynamic")
        self._check_result(r)

    def test_uc7_deterministic(self):
        r = self.api.execute_rec_uc7_evaluation(sample_users=5, k=5, mode="deterministic")
        self._check_result(r)

    def test_uc7_dynamic(self):
        r = self.api.execute_rec_uc7_evaluation(sample_users=5, k=5, mode="dynamic")
        self._check_result(r)

    def test_uc8_deterministic(self):
        r = self.api.execute_rec_uc8_visualisation(customer_id="CUST-001", mode="deterministic")
        self._check_result(r)

    def test_uc8_dynamic(self):
        r = self.api.execute_rec_uc8_visualisation(customer_id="CUST-001", mode="dynamic")
        self._check_result(r)

    def test_uc9_deterministic(self):
        r = self.api.execute_rec_uc9_routing("Recommend products for CUST-001", mode="deterministic")
        self._check_result(r)

    def test_uc9_dynamic(self):
        r = self.api.execute_rec_uc9_routing("Recommend products for CUST-001", mode="dynamic")
        self._check_result(r)

    def test_dynamic_has_tool_selections(self):
        r = self.api.execute_rec_uc4_hybrid("CUST-001", top_k=5, mode="dynamic")
        assert "tool_selections" in r

    def test_dynamic_sql_not_destructive(self):
        """Dynamic SQL generation must never produce destructive queries."""
        from agentic.sql.sql_generator import create_sql_generator
        gen = create_sql_generator()
        for intent in [
            "Find dormant_vip customers",
            "Show campaign performance",
            "Find high return risk customers",
        ]:
            result = gen.generate(intent)
            if result.get("query"):
                assert result.get("safe") is True
                assert not any(
                    kw in result["query"].upper()
                    for kw in ("INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE")
                )

    def test_memory_records_entries(self):
        """Memory must record entries after each UC execution."""
        from agentic.memory.memory_manager import get_memory
        mem = get_memory()
        r = self.api.execute_rec_uc1_user_based("CUST-001", "casual", top_k=3, mode="dynamic")
        entries = mem.get_request_history(r["request_id"])
        assert len(entries) > 0

    def test_routing_classifies_recommendation_intent(self):
        """UC9 routing must classify recommendation requests correctly."""
        from agentic.mcp.llm_reasoning_server import classify_recommendation_request
        for req in [
            "Recommend products for CUST-001",
            "Cold start recommendations for new customer",
            "Evaluate recommendation quality",
        ]:
            r = classify_recommendation_request(req)
            assert r["execution_status"] == "success"
            assert r["result"]["strategy"] in {
                "collaborative", "behaviour", "content", "hybrid",
                "cold_start", "segment_batch", "evaluation", "visualization",
            }
