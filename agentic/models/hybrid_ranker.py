"""Hybrid Ranker - wraps nonagentic hybrid recommendation."""

from typing import Optional
from nonagentic.tools.recommender import recommend


class HybridRanker:
    """Weighted hybrid recommender: collaborative + behaviour + content + popularity."""

    DEFAULT_WEIGHTS = {"collaborative": 0.4, "behaviour": 0.3, "content": 0.2, "popularity": 0.1}

    def rank(self, customer_id: str, top_k: int = 10, exclude_purchased: bool = True,
             weights: Optional[dict] = None) -> dict:
        """Run hybrid ranking. weights are for simulation only if overridden."""
        result = recommend(customer_id, top_k=top_k, exclude_purchased=exclude_purchased)
        return {
            "recommendations": result.get("recommendations", []),
            "similar_users": result.get("similar_users", []),
            "cold_start": result.get("cold_start", False),
            "weights_used": weights or self.DEFAULT_WEIGHTS,
            "model": "hybrid_ranker",
        }
