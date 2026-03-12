"""
Centralised runtime configuration.

All thresholds that were previously hardcoded are now read from environment
variables so they can be tuned per deployment without code changes.

Usage:
    from src.config import cfg
    if estimated_reach > cfg.campaign_reach_threshold: ...
"""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    # Approval thresholds
    bulk_notification_threshold: int   # send_notification: require approval if recipients > this
    campaign_reach_threshold: int      # schedule_campaign: require approval if reach > this
    risk_score_threshold: float        # level3: require approval if customer fraud_score > this
    payment_delay_threshold: float     # level3: require approval if return_risk > this

    # KPI / self-reflection
    kpi_deviation_threshold: float     # level4: re-plan if KPI deviates > this fraction
    target_conversion_rate: float      # level4: default target conversion rate for campaigns

    # SQL safety
    sql_max_rows: int                  # level2: max rows returned by run_sql_query

    # LLM guardrails
    guardrail_enabled: bool            # whether ConstitutionalChain guardrail is active


def _int(key: str, default: int) -> int:
    return int(os.getenv(key, str(default)))


def _float(key: str, default: float) -> float:
    return float(os.getenv(key, str(default)))


def _bool(key: str, default: bool) -> bool:
    val = os.getenv(key, str(default)).lower()
    return val in ("1", "true", "yes")


def load_config() -> Config:
    return Config(
        bulk_notification_threshold=_int("APPROVAL_BULK_THRESHOLD", 100),
        campaign_reach_threshold=_int("APPROVAL_CAMPAIGN_REACH_THRESHOLD", 1000),
        risk_score_threshold=_float("APPROVAL_RISK_SCORE_THRESHOLD", 0.8),
        payment_delay_threshold=_float("APPROVAL_PAYMENT_DELAY_THRESHOLD", 0.8),
        kpi_deviation_threshold=_float("KPI_DEVIATION_THRESHOLD", 0.10),
        target_conversion_rate=_float("TARGET_CONVERSION_RATE", 0.05),
        sql_max_rows=_int("SQL_MAX_ROWS", 10_000),
        guardrail_enabled=_bool("GUARDRAIL_ENABLED", True),
    )


# Module-level singleton — re-read on each import so tests can monkeypatch env vars
cfg = load_config()
