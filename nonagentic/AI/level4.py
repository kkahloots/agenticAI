from __future__ import annotations

from datetime import date, timedelta

from langchain_core.messages import AIMessage

from nonagentic.core.state import AgentState
from nonagentic.core.config import load_config
from nonagentic.tools.analytics import generate_segment
from nonagentic.tools.strategic import schedule_campaign
from nonagentic.tools.approval import request_human_approval
from nonagentic.tools.audit import log_audit_event
from nonagentic.tools.monitoring import (
    get_kpi_report,
    record_campaign_outcome,
    reflect_and_replan,
)
from nonagentic.core.observability import node_trace
from nonagentic.core.llm import get_llm

_MAX_REPLAN_CYCLES = 1  # guard against infinite loops


def _decompose(goal: str) -> list[str]:
    try:
        from langchain_core.messages import HumanMessage, SystemMessage

        llm = get_llm(temperature=0.0)
        resp = llm.invoke(
            [
                SystemMessage(
                    content="Break the business goal into 2-4 concrete sub-tasks. Return a numbered list only."
                ),
                HumanMessage(content=goal),
            ]
        )
        return [l.strip() for l in resp.content.strip().splitlines() if l.strip()]
    except Exception:
        return [
            "1. Segment target customers",
            "2. Select best offer per segment",
            "3. Schedule outreach campaign",
            "4. Monitor KPIs and adjust",
        ]


def _run_campaign_cycle(
    goal: str,
    state: AgentState,
    steps: list[str],
    seg_filters: dict | None = None,
) -> dict:
    """
    Single campaign cycle: segment → KPI check → approve → schedule → record.
    Returns result dict. Extracted so the self-reflection loop can call it twice.
    """
    cfg = load_config()

    seg_result = generate_segment(filters=seg_filters, algorithm="rules")
    segments = seg_result.get("segments", [])
    segment_id = segments[0]["label"] if segments else "all"
    estimated_reach = segments[0]["size"] if segments else 0
    steps.append(
        f"Segmentation: {len(segments)} segments, top '{segment_id}' ({estimated_reach} customers)"
    )
    log_audit_event(
        "level4_strategic",
        "generate_segment",
        {"filters": seg_filters},
        seg_result,
        user_id=state["user_id"],
        request_id=state["request_id"],
    )

    kpi = get_kpi_report(segment_id)
    steps.append(f"KPI baseline: {kpi.get('summary', 'no prior data')}")
    log_audit_event(
        "level4_strategic",
        "get_kpi_report",
        {"segment_id": segment_id},
        kpi,
        user_id=state["user_id"],
        request_id=state["request_id"],
    )

    approved = True
    if estimated_reach > cfg.campaign_reach_threshold:
        approval = request_human_approval(
            workflow_id=state["request_id"],
            action_description=f"Schedule campaign for {estimated_reach} customers",
            risk_level="high",
        )
        log_audit_event(
            "level4_strategic",
            "request_human_approval",
            {"estimated_reach": estimated_reach},
            approval,
            user_id=state["user_id"],
            request_id=state["request_id"],
        )
        approved = approval["approved"]
        steps.append(f"Approval: {'granted' if approved else 'rejected'}")

    if not approved:
        return {
            "segment": segment_id,
            "campaign": None,
            "blocked": "approval_rejected",
            "kpi_baseline": kpi,
        }

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
    log_audit_event(
        "level4_strategic",
        "schedule_campaign",
        {"segment_id": segment_id},
        campaign,
        user_id=state["user_id"],
        request_id=state["request_id"],
    )
    steps.append(f"Campaign scheduled: {campaign.get('campaign_id')} starting {start}")

    outcome = record_campaign_outcome(
        campaign_id=campaign.get("campaign_id", "unknown"),
        segment_id=segment_id,
        goal=goal,
        estimated_reach=estimated_reach,
        kpi_baseline=kpi,
    )
    steps.append("Outcome baseline recorded for post-campaign feedback")

    return {
        "segment": segment_id,
        "campaign": campaign,
        "kpi_baseline": kpi,
        "outcome": outcome,
    }


@node_trace("level4_strategic")
def level4_node(state: AgentState) -> dict:
    goal = state["original_request"]
    steps: list[str] = []

    # Step 1 — decompose goal
    sub_goals = _decompose(goal)
    steps.append(f"Goal decomposed into {len(sub_goals)} sub-tasks")
    log_audit_event(
        "level4_strategic",
        "decompose_goal",
        {"goal": goal},
        {"sub_goals": sub_goals},
        user_id=state["user_id"],
        request_id=state["request_id"],
    )

    # Step 2 — first campaign cycle
    cycle_result = _run_campaign_cycle(goal, state, steps)

    # Step 3 — self-reflection loop (G7 + G8)
    segment_id = cycle_result.get("segment", "all")
    reflection = reflect_and_replan(segment_id, goal)
    log_audit_event(
        "level4_strategic",
        "reflect_and_replan",
        {"segment_id": segment_id},
        reflection,
        user_id=state["user_id"],
        request_id=state["request_id"],
    )

    if reflection["should_replan"]:
        steps.append(f"⚠️ Self-reflection triggered re-plan: {reflection['reason']}")

        # Re-decompose with updated context
        refined_goal = f"{goal} [refined: focus on high-engagement low-risk customers]"
        sub_goals = _decompose(refined_goal)
        steps.append(f"Re-decomposed into {len(sub_goals)} refined sub-tasks")

        # Re-run campaign cycle with tighter segment filter
        cycle_result = _run_campaign_cycle(
            goal,
            state,
            steps,
            seg_filters={"segment": "vip"},  # tighter filter after reflection
        )
        steps.append("Re-plan cycle complete")

    result = {
        "sub_goals": sub_goals,
        "segment": cycle_result.get("segment"),
        "campaign": cycle_result.get("campaign"),
        "kpi_baseline": cycle_result.get("kpi_baseline"),
        "reflection": reflection,
    }
    if cycle_result.get("blocked"):
        result["blocked"] = cycle_result["blocked"]

    summary = "\n".join(f"✅ {s}" for s in steps)
    return {
        "routed_to": "level4_strategic",
        "result": result,
        "messages": [AIMessage(content=summary)],
        "tool_calls": [{"tool": "level4", "inputs": {"goal": goal}, "outputs": result}],
        "audit_trail": [
            {"node": "level4_strategic", "action": "completed", "steps": steps}
        ],
    }
