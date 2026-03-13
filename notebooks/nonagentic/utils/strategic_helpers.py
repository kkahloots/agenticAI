"""Orchestration helpers for level4_strategic_agent notebook."""

import os
import sys
import uuid
from datetime import date, timedelta
from pathlib import Path

try:
    from IPython.display import display, HTML
except ImportError:

    def display(*a, **k):
        pass

    class HTML:
        def __init__(self, d):
            self.data = d


# Get project root - notebooks/nonagent/utils/strategic_helpers.py -> agenticAI (4 parents)
_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()


def _ensure_src_path():
    """Ensure src module can be imported."""
    project_root = str(_PROJECT_ROOT)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)


def run_uc2_orchestration(goal: str) -> dict:
    """
    Full UC2 multi-agent orchestration:
    segmentation → KPI baseline → approval gate → schedule campaign.
    Returns dict with keys: segments, segment_id, estimated_reach, kpi, approval, campaign.
    """
    _ensure_src_path()
    import nonagentic.tools.monitoring as _mon
    from nonagentic.tools.analytics import generate_segment
    from nonagentic.tools.monitoring import get_kpi_report
    from nonagentic.tools.approval import request_human_approval, set_auto_approve
    from nonagentic.tools.strategic import schedule_campaign
    from .visualization import (
        display_title,
        display_status_banner,
        display_kpi_history,
        display_strategic_orchestration,
    )
    from .display_helpers import display_metrics

    # Fix outcomes path relative to project root
    _mon._OUTCOMES_PATH = str(_PROJECT_ROOT / "data" / "campaign_outcomes.jsonl")
    _mon._KPI_STORE.clear()
    _mon._KPI_STORE_LOADED = False

    set_auto_approve(True)

    # Step 1 — segmentation
    seg_result = generate_segment(algorithm="rules")
    segments = seg_result.get("segments", [])
    top = max(segments, key=lambda s: s["size"])
    segment_id, estimated_reach = top["label"], top["size"]

    display_title("Step 1 — Level 2: Customer Segmentation", emoji="🔍")
    display_metrics(
        {
            "Segments Found": len(segments),
            "Top Segment": segment_id,
            "Reach": estimated_reach,
        }
    )

    # Step 2 — KPI baseline
    kpi = get_kpi_report(segment_id)
    display_title("Step 2 — KPI Baseline", emoji="📊")
    display_metrics(
        {
            "Campaigns Run": kpi["campaigns_run"],
            "Avg Conversion": f"{kpi['avg_conversion_rate']:.1%}",
            "Summary": kpi["summary"],
        }
    )
    display_kpi_history(
        str(_PROJECT_ROOT / "data" / "campaign_outcomes.jsonl"), segment_id
    )

    # Step 3 — approval gate
    approval = request_human_approval(
        workflow_id="demo-uc2",
        action_description=f"Schedule campaign for {estimated_reach} customers in '{segment_id}'",
        risk_level="medium",
    )
    display_title("Step 3 — Human Approval Gate", emoji="🔐")
    display_status_banner(
        (
            f"✅ Approved by: {approval['approver_id']}"
            if approval["approved"]
            else "🚫 Approval rejected"
        ),
        status="success" if approval["approved"] else "error",
    )

    # Step 4 — schedule campaign
    campaign = {}
    if approval["approved"]:
        start = (date.today() + timedelta(days=3)).isoformat()
        campaign = schedule_campaign(
            campaign_name=goal[:60],
            segment_id=segment_id,
            steps=[
                {"channel": "email", "template_id": "T-PROMO-01", "delay_days": 0},
                {"channel": "sms", "template_id": "T-WINBACK-01", "delay_days": 3},
            ],
            start_date=start,
            estimated_reach=estimated_reach,
            approved=True,
        )
        display_title("Step 4 — Level 3: Campaign Scheduled", emoji="📣")
        display_strategic_orchestration(
            {
                "segment": segment_id,
                "campaign": campaign,
                "kpi_baseline": kpi,
                "reflection": {"should_replan": False},
            }
        )

    return {
        "segments": segments,
        "segment_id": segment_id,
        "estimated_reach": estimated_reach,
        "kpi": kpi,
        "approval": approval,
        "campaign": campaign,
    }


def run_uc5_pilot(segments: list) -> dict:
    """Run UC5 pilot test + compliance failure example."""
    _ensure_src_path()
    from nonagentic.tools.strategic import run_pilot_test
    from .visualization import display_pilot_results, display_title

    vip_segs = [s for s in segments if s["label"] == "vip"]
    vip_ids = (
        vip_segs[0]["customer_ids"]
        if vip_segs
        else [f"CUST-{i:03d}" for i in range(1, 46)]
    )

    pilot = run_pilot_test(vip_ids, "PROMO-PREMIUM-MEMBERSHIP", pilot_pct=0.20)
    display_pilot_results(pilot)

    display_title("Compliance Gate Failure Example (pilot_pct=0.6)", emoji="🚫")
    bad_pilot = run_pilot_test(vip_ids, "PROMO-PREMIUM-MEMBERSHIP", pilot_pct=0.6)
    display_pilot_results(bad_pilot)
    return pilot


def run_uc7_reflection(segment_id: str, goal: str, kpi: dict, campaign: dict) -> dict:
    """Run UC7 self-reflection: deviation checks + conditional replan."""
    _ensure_src_path()
    from nonagentic.tools.monitoring import check_kpi_deviation, reflect_and_replan
    from nonagentic.AI.level4 import _decompose
    from .visualization import (
        display_title,
        display_kpi_deviation,
        display_strategic_orchestration,
        display_goal_decomposition,
    )

    display_title("Scenario A — KPI Within Range", emoji="✅")
    display_kpi_deviation(check_kpi_deviation(segment_id, target_conversion_rate=0.10))

    display_title("Scenario B — KPI Deviation Exceeds Threshold", emoji="⚠️")
    display_kpi_deviation(check_kpi_deviation(segment_id, target_conversion_rate=0.50))

    display_title("Self-Reflection Decision", emoji="🔄")
    reflection = reflect_and_replan(segment_id, goal)
    display_strategic_orchestration(
        {
            "segment": segment_id,
            "campaign": campaign,
            "kpi_baseline": kpi,
            "reflection": reflection,
        }
    )

    if reflection["should_replan"]:
        display_title("Re-Plan: Refined Goal Decomposition", emoji="🔁")
        refined = f"{goal} [refined: focus on high-engagement low-risk customers]"
        display_goal_decomposition(_decompose(refined), refined)

    return reflection


def run_uc8_langfuse(goal: str) -> None:
    """Run UC8 Langfuse trace."""
    _ensure_src_path()
    from dotenv import load_dotenv
    from nonagentic.graph import graph
    from nonagentic.core.state import new_state
    from nonagentic.core.observability import clear_event_log
    from .visualization import display_status_banner

    load_dotenv(dotenv_path=str(_PROJECT_ROOT / ".env"), override=True)
    lf_host = os.getenv("LANGFUSE_HOST", "http://localhost:3000")
    lf_project = os.getenv("LANGFUSE_PROJECT", "agenticAI")

    clear_event_log()
    state = new_state(goal, user_id="demo-user")
    graph.invoke(state, config={"configurable": {"thread_id": state["request_id"]}})
    display_status_banner(
        f"✅ Trace sent — open {lf_host}/traces (project: {lf_project}) "
        f"and search for request_id: {state['request_id']}",
        status="success",
    )


def run_uc8_governance(
    goal: str,
    sub_goals: list,
    segments: list,
    segment_id: str,
    campaign: dict,
    reflection: dict,
) -> None:
    """Log audit events and display governance dashboard."""
    _ensure_src_path()
    from nonagentic.tools.audit import log_audit_event
    from nonagentic.core.observability import get_event_log
    from .visualization import display_governance_dashboard

    request_id = str(uuid.uuid4())
    log_audit_event(
        "level4_strategic",
        "decompose_goal",
        {"goal": goal},
        {"sub_goals": sub_goals},
        user_id="demo-user",
        request_id=request_id,
    )
    log_audit_event(
        "level4_strategic",
        "generate_segment",
        {"filters": None},
        {"segments": len(segments)},
        user_id="demo-user",
        request_id=request_id,
    )
    log_audit_event(
        "level4_strategic",
        "schedule_campaign",
        {"segment_id": segment_id},
        {"status": "scheduled"},
        user_id="demo-user",
        request_id=request_id,
    )
    log_audit_event(
        "level4_strategic",
        "reflect_and_replan",
        {"segment_id": segment_id},
        reflection,
        user_id="demo-user",
        request_id=request_id,
    )

    display_governance_dashboard(
        audit_path=str(_PROJECT_ROOT / "data" / "audit.jsonl"),
        event_log=get_event_log(),
    )
