from __future__ import annotations

import os
from typing import Optional

_CHART_DIR = os.getenv("CHART_OUTPUT_DIR", "data/charts")


def visualise(
    segments: list[dict],
    chart_type: str = "bar",
    title: str = "Chart",
    request_id: Optional[str] = None,
) -> Optional[str]:
    """
    Generate a chart from segment data and save to disk.
    Returns the file path, or None if matplotlib is unavailable or data is empty.
    """
    if not segments:
        return None

    try:
        import matplotlib
        matplotlib.use("Agg")  # non-interactive backend
        import matplotlib.pyplot as plt

        labels = [s["label"] for s in segments]
        sizes = [s["size"] for s in segments]
        risk_scores = [s.get("avg_risk_score", 0) for s in segments]

        fig, axes = plt.subplots(1, 2, figsize=(10, 4))

        # Chart 1 — segment sizes
        if chart_type == "bar":
            axes[0].bar(labels, sizes)
        else:
            axes[0].plot(labels, sizes, marker="o")
        axes[0].set_title(f"{title} — Size")
        axes[0].set_xlabel("Segment")
        axes[0].set_ylabel("Customers")
        axes[0].tick_params(axis="x", rotation=30)

        # Chart 2 — avg risk score per segment
        axes[1].bar(labels, risk_scores)
        axes[1].set_title(f"{title} — Avg Risk Score")
        axes[1].set_xlabel("Segment")
        axes[1].set_ylabel("Risk Score")
        axes[1].tick_params(axis="x", rotation=30)

        plt.tight_layout()

        os.makedirs(_CHART_DIR, exist_ok=True)
        suffix = request_id[:8] if request_id else "chart"
        path = os.path.join(_CHART_DIR, f"{suffix}.png")
        plt.savefig(path)
        plt.close(fig)
        return path

    except Exception:
        return None
