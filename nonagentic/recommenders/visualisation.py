"""Recommendation visualisation charts."""
import numpy as np
from pathlib import Path


def plot_user_similarity_heatmap(matrix, sample_ids, output_path):
    """
    Plot user similarity heatmap.
    
    Args:
        matrix: User-item interaction matrix {user_id: {product_id: weight}}
        sample_ids: List of user IDs to include
        output_path: Path to save PNG
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("⚠️  matplotlib not available, skipping heatmap")
        return
    
    from .collaborative import _cosine
    
    n = len(sample_ids)
    sim_matrix = np.zeros((n, n))
    
    for i, u1 in enumerate(sample_ids):
        for j, u2 in enumerate(sample_ids):
            sim_matrix[i, j] = _cosine(matrix.get(u1, {}), matrix.get(u2, {}))
    
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(sim_matrix, cmap="Blues", vmin=0, vmax=1)
    ax.set_title("User Similarity Heatmap", fontsize=13, fontweight="bold")
    ax.set_xlabel("User Index")
    ax.set_ylabel("User Index")
    plt.colorbar(im, ax=ax, label="Cosine Similarity")
    plt.tight_layout()
    plt.savefig(output_path, dpi=100, bbox_inches="tight")
    plt.close()


def plot_score_distribution(scores, labels, output_path):
    """
    Plot score distribution bar chart.
    
    Args:
        scores: List of scores
        labels: List of labels (product IDs)
        output_path: Path to save PNG
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("⚠️  matplotlib not available, skipping distribution")
        return
    
    fig, ax = plt.subplots(figsize=(10, 4))
    colors = ["#667eea" if i < 3 else "#94a3b8" for i in range(len(scores))]
    ax.barh(labels[::-1], scores[::-1], color=colors[::-1])
    ax.set_xlabel("Hybrid Score")
    ax.set_title("Top Recommendation Scores", fontsize=12, fontweight="bold")
    ax.axvline(x=0.3, color="#ef4444", linestyle="--", alpha=0.6, label="Threshold 0.3")
    ax.legend(fontsize=9)
    plt.tight_layout()
    plt.savefig(output_path, dpi=100, bbox_inches="tight")
    plt.close()


def plot_category_coverage(recommendations, products, output_path):
    """
    Plot category coverage bar chart.
    
    Args:
        recommendations: List of (product_id, score) tuples
        products: List of product dicts
        output_path: Path to save PNG
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("⚠️  matplotlib not available, skipping coverage")
        return
    
    from collections import Counter
    
    prod_map = {p["product_id"]: p for p in products}
    cat_counts = Counter()
    
    for pid, _ in recommendations:
        cat = prod_map.get(pid, {}).get("category", "unknown")
        cat_counts[cat] += 1
    
    cats_sorted = sorted(cat_counts.items(), key=lambda x: -x[1])
    cat_labels = [c[0] for c in cats_sorted]
    cat_vals = [c[1] for c in cats_sorted]
    
    fig, ax = plt.subplots(figsize=(9, 4))
    palette = plt.cm.Set3(np.linspace(0, 1, len(cat_labels)))
    ax.bar(cat_labels, cat_vals, color=palette)
    ax.set_xlabel("Category")
    ax.set_ylabel("Times Recommended")
    ax.set_title("Category Coverage in Recommendations", fontsize=12, fontweight="bold")
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=100, bbox_inches="tight")
    plt.close()
