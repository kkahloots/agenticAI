"""LLM Feature Reasoner - reasons about which features to prioritize.

Falls back to rule-based logic when LLM is unavailable.
Simulation-only weight proposals are clearly marked.
"""

from typing import Optional
from agentic.mcp.llm_reasoning_server import suggest_feature_priority, propose_weight_adjustments


class LLMFeatureReasoner:
    """Reasons about feature selection and weight tuning for recommendations."""

    DEFAULT_WEIGHTS = {"collaborative": 0.4, "behaviour": 0.3, "content": 0.2, "popularity": 0.1}

    def suggest_features(self, customer_id: str, context: Optional[dict] = None) -> list[dict]:
        """Suggest which features to prioritize for a customer.

        Returns ordered list of {feature, priority, reason}.
        """
        result = suggest_feature_priority(customer_id, context or {})
        return result["result"]["features"]

    def propose_weights(self, current_weights: dict,
                        evaluation_metrics: Optional[dict] = None) -> dict:
        """[SIMULATION ONLY] Propose alternative hybrid weights.

        Does NOT replace production weights.  For comparison/display only.
        """
        result = propose_weight_adjustments(current_weights, evaluation_metrics or {})
        return result["result"]

    def select_feature_subset(self, customer_id: str, context: dict,
                               mode: str = "deterministic") -> list[str]:
        """Select feature subset for a customer.

        deterministic: rule-based
        dynamic: LLM-assisted
        """
        if mode == "dynamic":
            features = self.suggest_features(customer_id, context)
            return [f["feature"] for f in features]

        # Deterministic fallback
        selected = []
        if context.get("interaction_count", 0) >= 5:
            selected.append("behaviour")
        if context.get("purchase_categories"):
            selected.extend(["content", "category_affinity"])
        return selected or ["content"]


def create_llm_feature_reasoner() -> LLMFeatureReasoner:
    """Create LLM feature reasoner instance."""
    return LLMFeatureReasoner()
