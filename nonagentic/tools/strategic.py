from __future__ import annotations

import uuid
from datetime import datetime, timezone

from nonagentic.core.config import load_config

_CAMPAIGNS: dict[str, dict] = {}


def schedule_campaign(
    campaign_name: str,
    segment_id: str,
    steps: list[dict],
    start_date: str,
    estimated_reach: int = 0,
    approved: bool = False,
) -> dict:
    cfg = load_config()
    if estimated_reach > cfg.campaign_reach_threshold and not approved:
        return {
            "campaign_id": None,
            "status": "approval_required",
            "reason": (
                f"Reach {estimated_reach} exceeds threshold "
                f"{cfg.campaign_reach_threshold} — human approval needed"
            ),
        }

    campaign_id = f"CAMP-{uuid.uuid4().hex[:8].upper()}"
    _CAMPAIGNS[campaign_id] = {
        "campaign_name": campaign_name,
        "segment_id": segment_id,
        "steps": steps,
        "start_date": start_date,
        "estimated_reach": estimated_reach,
        "status": "scheduled",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return {
        "campaign_id": campaign_id,
        "scheduled_steps": len(steps),
        "estimated_reach": estimated_reach,
        "status": "scheduled",
    }


def simulate_revenue_impact(
    segment_size: int,
    conversion_rate: float,
    avg_order_value: float,
    campaign_cost: float = 0.0,
) -> dict:
    """Project revenue impact of a campaign on a segment."""
    projected_conversions = int(segment_size * conversion_rate)
    projected_revenue = round(projected_conversions * avg_order_value, 2)
    incremental_revenue = round(projected_revenue - campaign_cost, 2)
    roi_pct = round(
        (incremental_revenue / campaign_cost * 100) if campaign_cost > 0 else 0.0, 1
    )
    return {
        "segment_size": segment_size,
        "conversion_rate": conversion_rate,
        "avg_order_value": avg_order_value,
        "projected_conversions": projected_conversions,
        "projected_revenue": projected_revenue,
        "campaign_cost": campaign_cost,
        "incremental_revenue": incremental_revenue,
        "roi_pct": roi_pct,
    }


def run_scenario_simulation(goal: str, scenarios: list[dict]) -> list[dict]:
    """
    Compare strategy scenarios. Each scenario dict must have:
      name, segment_size, conversion_rate, avg_order_value, risk (low/medium/high).
    Returns scenarios enriched with projected_revenue and recommended flag.
    """
    results = []
    for s in scenarios:
        impact = simulate_revenue_impact(
            s["segment_size"],
            s["conversion_rate"],
            s["avg_order_value"],
            s.get("campaign_cost", 0.0),
        )
        results.append({**s, **impact})
    # Recommend highest incremental revenue with non-high risk
    safe = [r for r in results if r.get("risk") != "high"]
    best = max(safe or results, key=lambda x: x["incremental_revenue"])
    for r in results:
        r["recommended"] = r["name"] == best["name"]
    return results


def run_pilot_test(
    segment_ids: list[str],
    offer_code: str,
    pilot_pct: float = 0.2,
) -> dict:
    """
    Split a segment into pilot and control groups.
    Enforces compliance gate: pilot_pct must be <= 0.5.
    """
    compliance_passed = pilot_pct <= 0.5
    total = len(segment_ids)
    pilot_size = int(total * pilot_pct)
    control_size = total - pilot_size
    return {
        "offer_code": offer_code,
        "total": total,
        "pilot_pct": pilot_pct,
        "pilot_size": pilot_size,
        "control_size": control_size,
        "pilot_ids": segment_ids[:pilot_size],
        "control_ids": segment_ids[pilot_size:],
        "compliance_passed": compliance_passed,
        "compliance_notes": (
            "Pilot split ≤ 50% — compliance gate passed"
            if compliance_passed
            else "Pilot split > 50% — compliance gate FAILED; reduce pilot_pct"
        ),
    }


def prioritize_initiatives(initiatives: list[dict]) -> list[dict]:
    """
    Rank initiatives by ROI score = est_revenue / effort_weight.
    effort: low=1, medium=2, high=3.
    """
    effort_map = {"low": 1, "medium": 2, "high": 3}
    for init in initiatives:
        effort_w = effort_map.get(init.get("effort", "medium"), 2)
        init["roi_score"] = round(init.get("est_revenue", 0) / effort_w, 2)
    return sorted(initiatives, key=lambda x: x["roi_score"], reverse=True)
