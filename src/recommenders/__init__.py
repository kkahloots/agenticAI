"""Recommendation engine modules for Level 5 agent."""

from .dataset import get_interaction_stats, get_category_stats, get_segment_stats as get_segment_stats_dataset
from .segment_analysis import get_segment_recommendations, get_segment_stats
from .collaborative import get_similar_users, get_collaborative_recommendations
from .behaviour import get_behaviour_scores, get_content_scores, get_category_affinity
from .cold_start import get_cold_start_recommendations
from .cold_start import get_cold_start_recommendations
from .segment_aggregation import get_segment_recommendations_batch
from .evaluation import compute_precision_recall, compute_map, compute_ndcg, evaluate_batch, check_data_leakage
from .visualisation import plot_user_similarity_heatmap, plot_score_distribution, plot_category_coverage

__all__ = [
    "get_interaction_stats",
    "get_category_stats",
    "get_segment_stats_dataset",
    "get_segment_recommendations",
    "get_segment_stats",
    "get_similar_users",
    "get_collaborative_recommendations",
    "get_behaviour_scores",
    "get_content_scores",
    "get_category_affinity",
    "get_cold_start_recommendations",
    "get_segment_recommendations_batch",
    "compute_precision_recall",
    "compute_map",
    "compute_ndcg",
    "evaluate_batch",
    "plot_user_similarity_heatmap",
    "plot_score_distribution",
    "plot_category_coverage",
]
