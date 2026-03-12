"""Level 5 recommendation chart helpers."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
from pathlib import Path

from .display_helpers import show_chart


def plot_similarity_heatmap(MATRIX, cosine_fn, sample_n=20, charts_dir="data/charts"):
    sample_ids = list(MATRIX.keys())[:sample_n]
    sim_matrix = np.array([[cosine_fn(MATRIX[u1], MATRIX[u2]) for u2 in sample_ids] for u1 in sample_ids])
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(sim_matrix, cmap="Blues", vmin=0, vmax=1)
    ax.set_title(f"User Similarity Heatmap (sample {sample_n} users)", fontsize=13, fontweight="bold")
    ax.set_xlabel("User Index"); ax.set_ylabel("User Index")
    plt.colorbar(im, ax=ax, label="Cosine Similarity")
    plt.tight_layout()
    show_chart(fig, Path(charts_dir) / "rec_user_similarity.png")


def plot_score_distribution(recommend_fn, customer_id="CUST-001", charts_dir="data/charts"):
    r      = recommend_fn(customer_id, top_k=20)
    scores = [rec["score"] for rec in r["recommendations"]]
    labels = [rec["product_id"] for rec in r["recommendations"]]
    fig, ax = plt.subplots(figsize=(10, 4))
    colors = ["#667eea" if i < 3 else "#94a3b8" for i in range(len(scores))]
    ax.barh(labels[::-1], scores[::-1], color=colors[::-1])
    ax.set_xlabel("Hybrid Score")
    ax.set_title(f"Top-20 Hybrid Recommendation Scores - {customer_id}", fontsize=12, fontweight="bold")
    ax.axvline(x=0.3, color="#ef4444", linestyle="--", alpha=0.6, label="Score threshold 0.3")
    ax.legend(fontsize=9)
    plt.tight_layout()
    show_chart(fig, Path(charts_dir) / "rec_score_distribution.png")


def plot_category_coverage(MATRIX, PROD_MAP, recommend_fn, sample_n=30, charts_dir="data/charts"):
    counts = Counter(
        PROD_MAP.get(rec["product_id"], {}).get("category", "unknown")
        for cid in list(MATRIX.keys())[:sample_n]
        for rec in recommend_fn(cid, top_k=5)["recommendations"]
    )
    cats_sorted = sorted(counts.items(), key=lambda x: -x[1])
    fig, ax = plt.subplots(figsize=(9, 4))
    palette = plt.cm.Set3(np.linspace(0, 1, len(cats_sorted)))
    ax.bar([c[0] for c in cats_sorted], [c[1] for c in cats_sorted], color=palette)
    ax.set_xlabel("Category"); ax.set_ylabel("Times Recommended")
    ax.set_title(f"Category Coverage ({sample_n} users, top-5 each)", fontsize=12, fontweight="bold")
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    show_chart(fig, Path(charts_dir) / "rec_category_coverage.png")
