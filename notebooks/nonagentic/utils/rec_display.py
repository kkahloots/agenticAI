"""Level 5 recommendation display helpers."""
import pandas as pd
from IPython.display import display, HTML
from .display_helpers import display_section, display_styled_table, display_metrics, display_card


def show_rec_table(rows, gradient_col="Score", header_color="#667eea", cmap="RdYlGn", fmt=None):
    if rows:
        display_styled_table(pd.DataFrame(rows), gradient_col=gradient_col,
                             fmt=fmt, header_color=header_color, cmap=cmap)
    else:
        display(HTML('<div style="color:#ef4444">No recommendations found</div>'))


def show_sim_table(rows):
    display_styled_table(pd.DataFrame(rows), gradient_col="Similarity",
                         fmt={"Similarity": "{:.3f}"}, header_color="#3b82f6", cmap="Blues")


def show_eval_metrics(metrics, k):
    display_section(f"📐 Offline Evaluation Metrics (K={k}, n={metrics['users_evaluated']} users)")
    display_metrics({k_: str(v) for k_, v in metrics.items() if k_ != "users_evaluated"})


def show_leakage_table(rows):
    display_section("🔍 Data Leakage Check (sample 10 users)")
    display_styled_table(pd.DataFrame(rows), header_color="#6366f1")
    display_metrics({
        "Users checked":        len(rows),
        "GT∩Train overlaps":    sum(r["GT∩Train (overlap)"] for r in rows),
        "Zero-hit (excl=True)": sum(1 for r in rows if r["Hits excl=True"] == 0),
        "Fix":                  "exclude_purchased=False",
    })
    display_card("Leakage Findings",
        "**What was wrong**\n"
        "recommend() defaults to exclude_purchased=True, filtering every item the user\n"
        "ever touched — including the ground-truth test items. Result: exact hits = 0.\n\n"
        "**Fix**: pass exclude_purchased=False for offline evaluation.")
