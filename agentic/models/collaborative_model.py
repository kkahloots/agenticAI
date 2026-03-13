"""Collaborative Model - wraps nonagentic collaborative filtering."""

from nonagentic.recommenders import get_similar_users
from nonagentic.tools.recommender import _collaborative_scores


class CollaborativeModel:
    """User-user cosine similarity collaborative filtering."""

    def score(self, customer_id: str, matrix: dict, top_k: int = 10) -> dict:
        similar_users, _ = get_similar_users(customer_id, matrix, min_sim=0.05, top_k=8)
        scores, _ = _collaborative_scores(customer_id, matrix)
        top = sorted(scores.items(), key=lambda x: -x[1])[:top_k]
        return {
            "similar_users": similar_users,
            "scores": dict(top),
            "model": "collaborative",
        }
