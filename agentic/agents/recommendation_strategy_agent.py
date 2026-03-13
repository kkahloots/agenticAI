"""Recommendation Strategy Agent - selects recommendation strategy dynamically."""

from typing import Optional
from agentic.mcp import llm_reasoning_server
from agentic.registry.tool_registry import get_registry
from agentic.memory.memory_manager import get_memory


class RecommendationStrategyAgent:
    """Selects recommendation strategy based on customer context."""

    def __init__(self):
        self.registry = get_registry()
        self.memory = get_memory()

    def select_strategy(self, customer_id: str, context: dict, request_id: str, mode: str = "deterministic") -> dict:
        """Select recommendation strategy for a customer.
        
        In deterministic mode: rule-based selection.
        In dynamic mode: uses LLM reasoning server (with fallback).
        """
        if mode == "dynamic":
            result = llm_reasoning_server.choose_recommendation_strategy(customer_id, context)
        else:
            result = self._rule_based_strategy(customer_id, context)

        self.memory.record_tool_usage(request_id, "select_strategy", {"customer_id": customer_id}, result)
        return result

    def _rule_based_strategy(self, customer_id: str, context: dict) -> dict:
        """Deterministic rule-based strategy selection."""
        interaction_count = context.get("interaction_count", 0)
        engagement = context.get("engagement_score", 0)
        purchase_cats = context.get("purchase_categories", [])

        if interaction_count < 3:
            strategy = "cold_start"
            reason = "Insufficient interaction history"
        elif interaction_count >= 10 and engagement > 0.4:
            strategy = "collaborative"
            reason = "Rich interaction history enables collaborative filtering"
        elif purchase_cats and engagement > 0.3:
            strategy = "hybrid"
            reason = "Good engagement and category data supports hybrid approach"
        elif purchase_cats:
            strategy = "content"
            reason = "Category preferences available"
        else:
            strategy = "behaviour"
            reason = "Behaviour signals available"

        return {
            "result": {"strategy": strategy, "reason": reason, "method": "rule_based"},
            "tool_name": "select_strategy",
            "execution_status": "success",
            "audit": {"customer_id": customer_id, "strategy": strategy},
        }

    def execute(self, task: dict, request_id: str) -> dict:
        """Execute strategy task — used by the execution graph."""
        action = task.get("action", "").lower()
        customer_id = task.get("customer_id", "")
        context = {k: v for k, v in task.items()
                   if k not in ("action", "candidate_tools")}

        if "classify" in action or "intent" in action:
            return self.classify_request(
                task.get("original_request", action), context, request_id
            )
        # Default: choose strategy
        return self.select_strategy(customer_id, context, request_id)

    def classify_request(self, request: str, context: Optional[dict] = None, request_id: str = "") -> dict:
        """Classify recommendation request type."""
        result = llm_reasoning_server.classify_recommendation_request(request, context)
        if request_id:
            self.memory.record_tool_usage(request_id, "classify_request", {"request": request}, result)
        return result


def create_recommendation_strategy_agent() -> RecommendationStrategyAgent:
    """Create recommendation strategy agent instance."""
    return RecommendationStrategyAgent()
