"""Build the final Level 5 agentic notebook from chunks."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).parent

def load(name):
    with open(ROOT / name) as f:
        return json.load(f)["cells"]

# ── Load existing chunks ──────────────────────────────────────────────────────
cells_A = load("nb_chunk_A_header.json")
cells_B = load("nb_chunk_B_uc1_uc2.json")
cells_C = load("nb_chunk_C_uc3_uc4.json")
cells_D = load("nb_chunk_D_uc5_uc6.json")

# ── UC7 cells ─────────────────────────────────────────────────────────────────
uc7_header = {
    "cell_type": "markdown", "id": "uc7-header", "metadata": {},
    "source": [
        "---\n",
        "## Use Case 7 — Recommendation Evaluation\n",
        "\n",
        "**Business scenario**: The data science team needs to measure how good the recommendations are before deploying to production.\n",
        "\n",
        "**Offline evaluation protocol**:\n",
        "1. For each user with ≥ 10 interactions, hold out the last 20% as ground truth\n",
        "2. Generate top-K recommendations using the remaining 80%\n",
        "3. Compute precision@K, recall@K, MAP, and NDCG\n",
        "\n",
        "| Version | Approach |\n",
        "|---|---|\n",
        "| **A — Deterministic** | Fixed offline evaluation pipeline |\n",
        "| **B — Dynamic** | Planner generates SQL to identify evaluation cohort, then runs metrics + LLM-assisted weight proposal |"
    ]
}

uc7a = {
    "cell_type": "code", "execution_count": None, "id": "uc7a", "metadata": {}, "outputs": [],
    "source": [
        "# ── UC7-A: Deterministic ──────────────────────────────────────────────────────\n",
        "display_section('🅐 UC7-A — Recommendation Evaluation (Deterministic)')\n",
        "\n",
        "leakage_rows = check_data_leakage(INTERACTIONS, recommend, sample_users=10)\n",
        "show_leakage_table(leakage_rows)\n",
        "\n",
        "K       = 10\n",
        "metrics = evaluate_batch(INTERACTIONS, lambda uid: recommend(uid, exclude_purchased=False), k=K, sample_users=40)\n",
        "show_eval_metrics(metrics, K)\n",
        "\n",
        "by_user  = defaultdict(list)\n",
        "for rec in INTERACTIONS:\n",
        "    by_user[rec['customer_id']].append(rec)\n",
        "eligible   = {uid: recs for uid, recs in by_user.items() if len(recs) >= 10}\n",
        "eval_users = list(eligible.keys())[:40]\n",
        "buckets = build_precision_buckets(eval_users, eligible, recommend, k=K)\n",
        "display_bar_chart(buckets, f'📊 Precision@{K} Distribution Across Users', color='#8b5cf6')"
    ]
}

uc7b = {
    "cell_type": "code", "execution_count": None, "id": "uc7b", "metadata": {}, "outputs": [],
    "source": [
        "# ── UC7-B: Dynamic (SQL cohort + LLM weight proposal) ────────────────────────\n",
        "display_section('🅑 UC7-B — Recommendation Evaluation (Dynamic Agentic)')\n",
        "\n",
        "result_b = api.execute_rec_uc7_evaluation(sample_users=40, k=10, mode='dynamic')\n",
        "\n",
        "show_agentic_result(result_b)\n",
        "show_agent_plan(result_b)\n",
        "show_agent_reasoning(result_b)\n",
        "show_tool_selection(result_b)\n",
        "show_agent_path(result_b)\n",
        "show_memory_updates(result_b)\n",
        "show_mcp_calls(result_b)\n",
        "\n",
        "# Dynamic: SQL to identify evaluation cohort\n",
        "from agentic.sql.sql_generator import create_sql_generator\n",
        "sql_gen   = create_sql_generator()\n",
        "sql_result = sql_gen.generate('Find customers with enough interactions for evaluation', {'min_interactions': 10})\n",
        "sql_query  = sql_result.get('query', 'SELECT customer_id FROM customers WHERE interaction_count >= 10 ORDER BY interaction_count DESC')\n",
        "display(HTML('<div style=\"border:1px solid #e2e8f0;border-radius:8px;padding:16px;margin:10px 0\">'\n",
        "             '<div style=\"font-weight:600;margin-bottom:8px;color:#667eea\">💾 Generated SQL — Evaluation Cohort (Dynamic)</div>'\n",
        "             f'<pre style=\"background:#f1f5f9;padding:12px;border-radius:4px;font-size:12px\">{sql_query}</pre>'\n",
        "             '</div>'))\n",
        "\n",
        "# Dynamic: LLM proposes weight adjustments based on metrics\n",
        "current_weights = {'collaborative': 0.4, 'behaviour': 0.3, 'content': 0.2, 'popularity': 0.1}\n",
        "weight_result   = llm_mcp.propose_weight_adjustments(current_weights, metrics)\n",
        "w               = weight_result['result']\n",
        "display(HTML('<div style=\"border:1px solid #e2e8f0;border-radius:8px;padding:16px;margin:10px 0\">'\n",
        "             '<div style=\"font-weight:600;margin-bottom:8px;color:#667eea\">⚖️ LLM Weight Proposal [SIMULATION ONLY] (Dynamic)</div>'\n",
        "             f'<div><strong>Current:</strong> {w[\"current_weights\"]}</div>'\n",
        "             f'<div><strong>Proposed:</strong> {w[\"proposed_weights\"]}</div>'\n",
        "             f'<div><strong>Reason:</strong> {w[\"reason\"]}</div>'\n",
        "             f'<div style=\"color:#ef4444;font-size:12px;margin-top:6px\">⚠️ {w[\"warning\"]}</div>'\n",
        "             '</div>'))\n",
        "\n",
        "# Output compatibility: same evaluation view\n",
        "show_eval_metrics(metrics, K)"
    ]
}

# ── UC8 cells ─────────────────────────────────────────────────────────────────
uc8_header = {
    "cell_type": "markdown", "id": "uc8-header", "metadata": {},
    "source": [
        "---\n",
        "## Use Case 8 — Visualisation\n",
        "\n",
        "**Business scenario**: The analytics team wants visual summaries of the recommendation engine — user similarity patterns, score distributions, and category coverage.\n",
        "\n",
        "| Version | Approach |\n",
        "|---|---|\n",
        "| **A — Deterministic** | Fixed chart pipeline |\n",
        "| **B — Dynamic** | Planner selects which charts to generate based on data profile; LLM classifies request type |"
    ]
}

uc8a = {
    "cell_type": "code", "execution_count": None, "id": "uc8a", "metadata": {}, "outputs": [],
    "source": [
        "# ── UC8-A: Deterministic ──────────────────────────────────────────────────────\n",
        "display_section('🅐 UC8-A — Visualisation (Deterministic)')\n",
        "\n",
        "customer_id = 'CUST-001'\n",
        "plot_user_similarity_heatmap(customer_id, MATRIX, CUST_MAP, top_k=8)\n",
        "plot_score_distribution(customer_id, MATRIX, CUST_MAP, PRODUCTS)\n",
        "plot_category_coverage(customer_id, MATRIX, CUST_MAP, PRODUCTS)"
    ]
}

uc8b = {
    "cell_type": "code", "execution_count": None, "id": "uc8b", "metadata": {}, "outputs": [],
    "source": [
        "# ── UC8-B: Dynamic ────────────────────────────────────────────────────────────\n",
        "display_section('🅑 UC8-B — Visualisation (Dynamic Agentic)')\n",
        "\n",
        "result_b = api.execute_rec_uc8_visualisation(customer_id='CUST-001', mode='dynamic')\n",
        "\n",
        "show_agentic_result(result_b)\n",
        "show_agent_plan(result_b)\n",
        "show_agent_reasoning(result_b)\n",
        "show_tool_selection(result_b)\n",
        "show_agent_path(result_b)\n",
        "show_memory_updates(result_b)\n",
        "show_mcp_calls(result_b)\n",
        "\n",
        "# Dynamic: LLM classifies the visualisation request\n",
        "viz_class = llm_mcp.classify_recommendation_request(\n",
        "    'Show similarity heatmap and score distribution for CUST-001',\n",
        "    {'customer_id': 'CUST-001'}\n",
        ")\n",
        "vc = viz_class['result']\n",
        "display(HTML('<div style=\"border:1px solid #e2e8f0;border-radius:8px;padding:16px;margin:10px 0\">'\n",
        "             '<div style=\"font-weight:600;margin-bottom:8px;color:#667eea\">🤖 LLM Request Classification (Dynamic)</div>'\n",
        "             f'<div><strong>Classified as:</strong> {vc[\"strategy\"]}</div>'\n",
        "             f'<div><strong>Confidence:</strong> {vc[\"confidence\"]}</div>'\n",
        "             f'<div><strong>Method:</strong> {vc[\"method\"]}</div>'\n",
        "             '</div>'))\n",
        "\n",
        "# Output compatibility: same charts\n",
        "plot_user_similarity_heatmap('CUST-001', MATRIX, CUST_MAP, top_k=8)\n",
        "plot_score_distribution('CUST-001', MATRIX, CUST_MAP, PRODUCTS)\n",
        "plot_category_coverage('CUST-001', MATRIX, CUST_MAP, PRODUCTS)"
    ]
}

# ── UC9 cells ─────────────────────────────────────────────────────────────────
uc9_header = {
    "cell_type": "markdown", "id": "uc9-header", "metadata": {},
    "source": [
        "---\n",
        "## Use Case 9 — Orchestrator Routing\n",
        "\n",
        "**Business scenario**: The orchestrator receives a free-text request and must decide which recommendation strategy to invoke.\n",
        "\n",
        "| Version | Approach |\n",
        "|---|---|\n",
        "| **A — Deterministic** | Rule-based keyword routing |\n",
        "| **B — Dynamic** | LLM classifies intent → registry discovers tools → planner builds execution plan |"
    ]
}

uc9a = {
    "cell_type": "code", "execution_count": None, "id": "uc9a", "metadata": {}, "outputs": [],
    "source": [
        "# ── UC9-A: Deterministic (rule-based routing) ─────────────────────────────────\n",
        "display_section('🅐 UC9-A — Orchestrator Routing (Deterministic)')\n",
        "\n",
        "test_requests = [\n",
        "    'Recommend products for CUST-001',\n",
        "    'Find similar users to CUST-042',\n",
        "    'Cold start recommendations for new customer',\n",
        "    'Evaluate recommendation quality',\n",
        "    'Segment batch recommendations for dormant_vip',\n",
        "]\n",
        "\n",
        "rows = []\n",
        "for req in test_requests:\n",
        "    result = llm_mcp.classify_recommendation_request(req)\n",
        "    r = result['result']\n",
        "    rows.append({'Request': req, 'Strategy': r['strategy'], 'Confidence': r['confidence'], 'Method': r['method']})\n",
        "\n",
        "import pandas as pd\n",
        "df = pd.DataFrame(rows)\n",
        "display(df.style.set_table_styles([{'selector': 'th', 'props': [('background', '#667eea'), ('color', 'white'), ('padding', '8px')]}]))"
    ]
}

uc9b = {
    "cell_type": "code", "execution_count": None, "id": "uc9b", "metadata": {}, "outputs": [],
    "source": [
        "# ── UC9-B: Dynamic (planner + registry + LLM) ────────────────────────────────\n",
        "display_section('🅑 UC9-B — Orchestrator Routing (Dynamic Agentic)')\n",
        "\n",
        "routing_requests = [\n",
        "    'Recommend products for CUST-001',\n",
        "    'Cold start recommendations for new customer in dormant_vip segment',\n",
        "    'Evaluate recommendation quality for 40 users',\n",
        "]\n",
        "\n",
        "for req in routing_requests:\n",
        "    result_b = api.execute_rec_uc9_routing(req, mode='dynamic')\n",
        "    display(HTML(f'<div style=\"font-weight:600;margin:12px 0 4px;color:#334155\">Request: \"{req}\"</div>'))\n",
        "    show_agentic_result(result_b)\n",
        "    show_agent_plan(result_b)\n",
        "    show_agent_reasoning(result_b)\n",
        "    show_tool_selection(result_b)\n",
        "    show_agent_path(result_b)\n",
        "    show_mcp_calls(result_b)\n",
        "    display(HTML('<hr style=\"border:none;border-top:1px solid #e2e8f0;margin:16px 0\">'))"
    ]
}

# ── Comparison cell ───────────────────────────────────────────────────────────
comparison_header = {
    "cell_type": "markdown", "id": "comparison-header", "metadata": {},
    "source": [
        "---\n",
        "## Summary — Nonagentic vs Agentic Comparison\n",
        "\n",
        "| Capability | Nonagentic (A) | Agentic (B) |\n",
        "|---|---|---|\n",
        "| **Routing** | Fixed keyword rules | LLM intent classification |\n",
        "| **Tool selection** | Hardcoded calls | Registry-based dynamic discovery |\n",
        "| **SQL** | None | Dynamic safe SQL generation |\n",
        "| **Feature selection** | Fixed weights | LLM-reasoned priority |\n",
        "| **Explainability** | Source model label | Dominant signal + LLM explanation |\n",
        "| **Memory** | None | Plan history, tool usage, observations |\n",
        "| **Weight tuning** | Manual | LLM simulation proposal |\n",
        "| **Cold start** | Segment fallback | LLM-selected strategy |\n"
    ]
}

comparison_cell = {
    "cell_type": "code", "execution_count": None, "id": "comparison-cell", "metadata": {}, "outputs": [],
    "source": [
        "# Three-way comparison: nonagentic baseline vs deterministic agentic vs dynamic agentic\n",
        "result_det = api.execute_rec_uc4_hybrid('CUST-001', top_k=10, mode='deterministic')\n",
        "result_dyn = api.execute_rec_uc4_hybrid('CUST-001', top_k=10, mode='dynamic')\n",
        "\n",
        "show_comparison(\n",
        "    nonagent_result={'source': 'nonagentic', 'tools': ['recommend()']},\n",
        "    deterministic_result=result_det,\n",
        "    dynamic_result=result_dyn,\n",
        ")"
    ]
}

# ── Assemble all cells ────────────────────────────────────────────────────────
all_cells = (
    cells_A +
    cells_B +
    cells_C +
    cells_D +
    [uc7_header, uc7a, uc7b] +
    [uc8_header, uc8a, uc8b] +
    [uc9_header, uc9a, uc9b] +
    [comparison_header, comparison_cell]
)

notebook = {
    "cells": all_cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.10.0"}
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

out = Path("/home/kahloka/projects/agenticAI/notebooks/agentic/05_level5_recommendation.ipynb")
with open(out, "w") as f:
    json.dump(notebook, f, indent=1)

print(f"✅ Written {len(all_cells)} cells → {out}")
