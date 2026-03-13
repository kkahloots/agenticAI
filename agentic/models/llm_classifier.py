"""LLM Classifier - classifies recommendation requests.

Falls back to rule-based logic when LLM is unavailable.
"""

from typing import Optional
from agentic.mcp.llm_reasoning_server import classify_recommendation_request


class LLMClassifier:
    """Classifies recommendation requests into strategy types."""

    STRATEGIES = [
        "collaborative", "behaviour", "content", "hybrid",
        "cold_start", "segment_batch", "evaluation", "visualization",
    ]

    def classify(self, request: str, context: Optional[dict] = None) -> dict:
        """Classify a recommendation request.

        Returns one of: collaborative, behaviour, content, hybrid,
        cold_start, segment_batch, evaluation, visualization.
        """
        result = classify_recommendation_request(request, context)
        return result["result"]

    def is_cold_start(self, context: dict) -> bool:
        """Determine if a customer is in cold-start state."""
        return context.get("interaction_count", 0) < 3

    def is_collaborative_ready(self, context: dict) -> bool:
        """Determine if collaborative filtering is viable."""
        return context.get("interaction_count", 0) >= 10

    def is_segment_driven(self, context: dict) -> bool:
        """Determine if segment-based recommendation is appropriate."""
        return bool(context.get("segment")) and not self.is_collaborative_ready(context)


def create_llm_classifier() -> LLMClassifier:
    """Create LLM classifier instance."""
    return LLMClassifier()
