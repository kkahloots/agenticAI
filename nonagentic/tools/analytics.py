from __future__ import annotations

import json
import os
import re
from typing import Optional

_DB_URL = os.getenv("DATABASE_URL", "sqlite:///data/customers.db")
_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        from sqlalchemy import create_engine

        _engine = create_engine(_DB_URL, connect_args={"check_same_thread": False})
    return _engine


def _is_safe(sql: str) -> bool:
    forbidden = re.compile(
        r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|EXEC|EXECUTE)\b",
        re.IGNORECASE,
    )
    return not forbidden.search(sql)


def run_sql_query(
    sql: str, params: Optional[dict] = None, max_rows: int = 10_000
) -> dict:
    if not _is_safe(sql):
        return {"error": "unsafe_query", "rows": [], "row_count": 0, "truncated": False}
    try:
        from sqlalchemy import text

        engine = _get_engine()
        with engine.connect() as conn:
            result = conn.execute(text(sql), params or {})
            rows = [dict(r._mapping) for r in result]
        truncated = len(rows) > max_rows
        return {
            "rows": rows[:max_rows],
            "row_count": len(rows[:max_rows]),
            "truncated": truncated,
        }
    except Exception as exc:
        return {"error": str(exc), "rows": [], "row_count": 0, "truncated": False}


def generate_segment(
    filters: Optional[dict] = None,
    algorithm: str = "rules",
    n_clusters: int = 3,
) -> dict:
    from nonagentic.tools.customer import _load_customers

    customers = _load_customers()
    if filters:
        for k, v in filters.items():
            customers = [c for c in customers if c.get(k) == v]

    if len(customers) < 10:
        return {"warning": "insufficient_data", "segments": _rule_segment(customers)}

    if algorithm == "kmeans":
        try:
            return _kmeans_segment(customers, n_clusters)
        except Exception:
            pass  # fallback to rules

    return {"segments": _rule_segment(customers)}


def _rule_segment(customers: list[dict]) -> list[dict]:
    buckets: dict[str, list] = {}
    for c in customers:
        label = c.get("segment", "unknown")
        buckets.setdefault(label, []).append(c["customer_id"])

    return [
        {
            "label": label,
            "customer_ids": ids,
            "size": len(ids),
            "avg_risk_score": _avg(
                [c.get("fraud_score", 0) for c in customers if c["customer_id"] in ids]
            ),
            "avg_engagement_score": _avg(
                [
                    c.get("engagement_score", 0)
                    for c in customers
                    if c["customer_id"] in ids
                ]
            ),
        }
        for label, ids in buckets.items()
    ]


def _kmeans_segment(customers: list[dict], n_clusters: int) -> dict:
    from sklearn.cluster import KMeans
    import numpy as np

    features = [
        [c.get("fraud_score", 0.5), c.get("engagement_score", 0.5)] for c in customers
    ]
    X = np.array(features)
    km = KMeans(
        n_clusters=min(n_clusters, len(customers)), random_state=42, n_init="auto"
    )
    labels = km.fit_predict(X)

    buckets: dict[int, list] = {}
    for c, lbl in zip(customers, labels):
        buckets.setdefault(int(lbl), []).append(c["customer_id"])

    segments = [
        {
            "label": f"cluster_{lbl}",
            "customer_ids": ids,
            "size": len(ids),
            "avg_risk_score": float(km.cluster_centers_[lbl][0]),
            "avg_engagement_score": float(km.cluster_centers_[lbl][1]),
        }
        for lbl, ids in buckets.items()
    ]
    return {"segments": segments}


def _avg(values: list) -> float:
    return round(sum(values) / len(values), 3) if values else 0.0
