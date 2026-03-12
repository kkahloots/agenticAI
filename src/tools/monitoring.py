from __future__ import annotations

import json
import os
from datetime import datetime, timezone

_OUTCOMES_PATH = os.getenv("OUTCOMES_PATH", "data/campaign_outcomes.jsonl")
_KPI_STORE: dict[str, dict] = {}
_KPI_STORE_LOADED = False


def _ensure_kpi_store_loaded() -> None:
    global _KPI_STORE_LOADED
    if _KPI_STORE_LOADED:
        return
    _KPI_STORE_LOADED = True
    try:
        if not os.path.exists(_OUTCOMES_PATH):
            return
        with open(_OUTCOMES_PATH, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                seg = record.get("segment_id")
                if not seg:
                    continue
                prior = _KPI_STORE.get(seg, {"campaigns_run": 0, "avg_conversion_rate": 0.0, "avg_open_rate": 0.0})
                n = prior["campaigns_run"] + 1
                conv = record.get("conversion_rate", 0.0)
                open_r = record.get("open_rate", 0.0)
                _KPI_STORE[seg] = {
                    "campaigns_run": n,
                    "avg_conversion_rate": round((prior["avg_conversion_rate"] * (n - 1) + conv) / n, 4),
                    "avg_open_rate": round((prior["avg_open_rate"] * (n - 1) + open_r) / n, 4),
                    "last_updated": record.get("recorded_at"),
                }
    except Exception:
        pass


def get_kpi_report(segment_id: str) -> dict:
    _ensure_kpi_store_loaded()
    if segment_id in _KPI_STORE:
        kpi = _KPI_STORE[segment_id]
        return {
            "segment_id": segment_id,
            "campaigns_run": kpi.get("campaigns_run", 0),
            "avg_conversion_rate": kpi.get("avg_conversion_rate", 0.0),
            "avg_open_rate": kpi.get("avg_open_rate", 0.0),
            "last_updated": kpi.get("last_updated"),
            "summary": (
                f"{kpi.get('campaigns_run', 0)} campaigns | "
                f"conversion {kpi.get('avg_conversion_rate', 0.0):.1%} | "
                f"open rate {kpi.get('avg_open_rate', 0.0):.1%}"
            ),
        }
    return {
        "segment_id": segment_id,
        "campaigns_run": 0,
        "avg_conversion_rate": 0.0,
        "avg_open_rate": 0.0,
        "last_updated": None,
        "summary": "no prior data",
    }


def record_campaign_outcome(
    campaign_id: str,
    segment_id: str,
    goal: str,
    estimated_reach: int,
    kpi_baseline: dict,
    actual_conversions: int = 0,
    actual_opens: int = 0,
) -> dict:
    from src.core.config import load_config
    cfg = load_config()

    conversion_rate = actual_conversions / estimated_reach if estimated_reach > 0 else 0.0
    open_rate = actual_opens / estimated_reach if estimated_reach > 0 else 0.0

    prior = _KPI_STORE.get(segment_id, {"campaigns_run": 0, "avg_conversion_rate": 0.0, "avg_open_rate": 0.0})
    n = prior["campaigns_run"] + 1
    _KPI_STORE[segment_id] = {
        "campaigns_run": n,
        "avg_conversion_rate": round((prior["avg_conversion_rate"] * (n - 1) + conversion_rate) / n, 4),
        "avg_open_rate": round((prior["avg_open_rate"] * (n - 1) + open_rate) / n, 4),
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }

    baseline_conv = kpi_baseline.get("avg_conversion_rate", 0.0)
    deviation = abs(conversion_rate - baseline_conv)
    needs_reanalysis = deviation > cfg.kpi_deviation_threshold

    record = {
        "campaign_id": campaign_id,
        "segment_id": segment_id,
        "goal": goal,
        "estimated_reach": estimated_reach,
        "actual_conversions": actual_conversions,
        "actual_opens": actual_opens,
        "conversion_rate": conversion_rate,
        "open_rate": open_rate,
        "deviation_from_baseline": round(deviation, 4),
        "needs_reanalysis": needs_reanalysis,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        os.makedirs(os.path.dirname(_OUTCOMES_PATH) or ".", exist_ok=True)
        with open(_OUTCOMES_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except OSError:
        pass

    return {
        "status": "recorded",
        "needs_reanalysis": needs_reanalysis,
        "deviation": deviation,
    }


def check_kpi_deviation(segment_id: str, target_conversion_rate: float | None = None) -> dict:
    from src.core.config import load_config
    cfg = load_config()
    target = target_conversion_rate if target_conversion_rate is not None else cfg.target_conversion_rate
    kpi = get_kpi_report(segment_id)
    current = kpi["avg_conversion_rate"]
    deviation = abs(current - target)
    return {
        "segment_id": segment_id,
        "current_conversion_rate": current,
        "target_conversion_rate": target,
        "deviation": round(deviation, 4),
        "action_required": deviation > cfg.kpi_deviation_threshold,
    }


def reflect_and_replan(segment_id: str, goal: str) -> dict:
    """
    Self-reflection entry point for Level-4.

    Reads the latest KPI for the segment, checks deviation against target,
    and returns a directive:
      - action_required=False → proceed as planned
      - action_required=True  → re-segment with tighter filters and re-plan

    This implements Gap 7 (reads needs_reanalysis) and Gap 8 (calls check_kpi_deviation
    and returns an actionable re-plan directive).
    """
    from src.core.config import load_config
    cfg = load_config()

    deviation_report = check_kpi_deviation(segment_id)

    # Also scan recent outcomes for this segment
    pending_reanalysis = _has_pending_reanalysis(segment_id)

    should_replan = deviation_report["action_required"] or pending_reanalysis

    if should_replan:
        return {
            "should_replan": True,
            "reason": (
                f"KPI deviation {deviation_report['deviation']:.1%} exceeds "
                f"threshold {cfg.kpi_deviation_threshold:.1%}" if deviation_report["action_required"]
                else "Recent campaign outcome flagged needs_reanalysis"
            ),
            "recommended_action": "re-segment with stricter filters and re-decompose goal",
            "deviation_report": deviation_report,
        }

    return {
        "should_replan": False,
        "reason": "KPI within acceptable range",
        "deviation_report": deviation_report,
    }


def _has_pending_reanalysis(segment_id: str) -> bool:
    """Check the outcomes JSONL for any recent needs_reanalysis=True for this segment."""
    try:
        if not os.path.exists(_OUTCOMES_PATH):
            return False
        with open(_OUTCOMES_PATH, encoding="utf-8") as f:
            lines = f.readlines()
        # Check last 10 records only
        for line in reversed(lines[-10:]):
            record = json.loads(line.strip())
            if record.get("segment_id") == segment_id and record.get("needs_reanalysis"):
                return True
    except Exception:
        pass
    return False
