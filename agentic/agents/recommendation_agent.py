"""Recommendation Agent - handles L3 offer recommendations and L5 product recommendations."""

from typing import Optional
from agentic.mcp import recommendation_server
from agentic.registry.tool_registry import get_registry
from agentic.memory.memory_manager import get_memory


class RecommendationAgent:
    """Handles recommendation workflows for both L3 and L5."""

    def __init__(self):
        self.registry = get_registry()
        self.memory = get_memory()

    def execute(self, task: dict, request_id: str) -> dict:
        """Execute recommendation task."""
        action = task.get("action", "").lower()

        # ── Level 5 actions ───────────────────────────────────────────────────
        if "segment_recommendation" in action or action == "segment_recommendations":
            return self._segment_recommendations(task, request_id)
        if "collaborative" in action:
            return self._collaborative_scores(task, request_id)
        if "behaviour" in action or "behavior" in action:
            return self._behaviour_scores(task, request_id)
        if "hybrid_recommend" in action or action == "hybrid_recommend":
            return self._hybrid_recommend(task, request_id)
        if "cold_start" in action:
            return self._cold_start_recommend(task, request_id)
        if "segment_batch" in action:
            return self._segment_batch_recommend(task, request_id)
        if "popularity" in action:
            return self._popularity_scores(task, request_id)
        if "explain" in action:
            return self._explain_recommendation(task, request_id)

        # ── Level 3 actions ───────────────────────────────────────────────────
        if "score" in action and "lead" in action:
            return self._score_leads(task, request_id)
        if "bulk" in action:
            return self._bulk_recommend(task, request_id)
        if "rank" in action:
            return self._rank_nba(task, request_id)
        if "recommend" in action or "nba" in action:
            return self._recommend_offer(task, request_id)

        return {"error": "unknown_action", "action": action}

    # ── Level 5 handlers ──────────────────────────────────────────────────────

    def _segment_recommendations(self, task: dict, request_id: str) -> dict:
        segment = task.get("segment", "")
        top_k = task.get("top_k", 10)
        result = recommendation_server.segment_recommendations(segment, top_k=top_k)
        self.memory.record_tool_usage(request_id, "segment_recommendations", task, result)
        return result

    def _collaborative_scores(self, task: dict, request_id: str) -> dict:
        customer_id = task.get("customer_id", "")
        top_k = task.get("top_k", 10)
        result = recommendation_server.collaborative_scores(customer_id, top_k=top_k)
        self.memory.record_tool_usage(request_id, "collaborative_scores", task, result)
        return result

    def _behaviour_scores(self, task: dict, request_id: str) -> dict:
        customer_id = task.get("customer_id", "")
        top_k = task.get("top_k", 10)
        result = recommendation_server.behaviour_scores(customer_id, top_k=top_k)
        self.memory.record_tool_usage(request_id, "behaviour_scores", task, result)
        return result

    def _hybrid_recommend(self, task: dict, request_id: str) -> dict:
        customer_id = task.get("customer_id", "")
        top_k = task.get("top_k", 10)
        result = recommendation_server.hybrid_recommend(customer_id, top_k=top_k)
        self.memory.record_tool_usage(request_id, "hybrid_recommend", task, result)
        return result

    def _cold_start_recommend(self, task: dict, request_id: str) -> dict:
        customer_id = task.get("customer_id", "CUST-NEW")
        segment = task.get("segment", "")
        top_k = task.get("top_k", 10)
        result = recommendation_server.cold_start_recommend(customer_id, segment, top_k=top_k)
        self.memory.record_tool_usage(request_id, "cold_start_recommend", task, result)
        return result

    def _segment_batch_recommend(self, task: dict, request_id: str) -> dict:
        segment = task.get("segment", "")
        top_k = task.get("top_k", 10)
        sample_size = task.get("sample_size", 15)
        result = recommendation_server.segment_batch_recommend(segment, top_k=top_k, sample_size=sample_size)
        self.memory.record_tool_usage(request_id, "segment_batch_recommend", task, result)
        return result

    def _popularity_scores(self, task: dict, request_id: str) -> dict:
        top_k = task.get("top_k", 10)
        result = recommendation_server.popularity_scores(top_k=top_k)
        self.memory.record_tool_usage(request_id, "popularity_scores", task, result)
        return result

    def _explain_recommendation(self, task: dict, request_id: str) -> dict:
        from agentic.mcp import llm_reasoning_server
        product_id = task.get("product_id", "")
        customer_id = task.get("customer_id", "")
        signals = task.get("signals", {})
        result = llm_reasoning_server.explain_recommendation(product_id, customer_id, signals)
        self.memory.record_tool_usage(request_id, "explain_recommendation", task, result)
        return result

    # ── Level 3 handlers ──────────────────────────────────────────────────────

    def _score_leads(self, task: dict, request_id: str) -> dict:
        offer_code = task.get("offer_code")
        if not offer_code:
            return {"error": "missing_offer_code"}
        result = recommendation_server.score_leads(offer_code, top_n=task.get("top_n", 20),
                                                    segment=task.get("segment"))
        self.memory.record_tool_usage(request_id, "score_leads", task, result)
        return result

    def _recommend_offer(self, task: dict, request_id: str) -> dict:
        customer_id = task.get("customer_id")
        if not customer_id:
            return {"error": "missing_customer_id"}
        result = recommendation_server.recommend_offer(customer_id, context=task.get("context", ""))
        self.memory.record_tool_usage(request_id, "recommend_offer", task, result)
        return result

    def _bulk_recommend(self, task: dict, request_id: str) -> dict:
        offer_code = task.get("offer_code")
        if not offer_code:
            return {"error": "missing_offer_code"}
        result = recommendation_server.bulk_recommend(offer_code, segment=task.get("segment"),
                                                       top_n=task.get("top_n", 50))
        self.memory.record_tool_usage(request_id, "bulk_recommend", task, result)
        return result

    def _rank_nba(self, task: dict, request_id: str) -> dict:
        customer_id = task.get("customer_id")
        if not customer_id:
            return {"error": "missing_customer_id"}
        result = recommendation_server.rank_next_best_action(customer_id)
        self.memory.record_tool_usage(request_id, "rank_next_best_action", task, result)
        return result


def create_recommendation_agent() -> RecommendationAgent:
    """Create recommendation agent instance."""
    return RecommendationAgent()
