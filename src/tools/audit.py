from __future__ import annotations

import json
import os
import time
import uuid
from datetime import datetime, timezone


_AUDIT_PATH = os.getenv("AUDIT_LOG_PATH", "data/audit.jsonl")
_buffer: list[dict] = []


def log_audit_event(
    agent_id: str,
    action: str,
    inputs: dict,
    outputs: dict,
    user_id: str = "system",
    customer_id: str | None = None,
    request_id: str | None = None,
) -> dict:
    record = {
        "audit_id": str(uuid.uuid4()),
        "request_id": request_id,
        "user_id": user_id,
        "agent_id": agent_id,
        "action": action,
        "customer_id": customer_id,
        "inputs": _mask_pii(inputs),
        "outputs": _mask_pii(outputs),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    _flush(record)
    return {"audit_id": record["audit_id"], "status": "logged"}


def _mask_pii(data: dict) -> dict:
    pii_keys = {"full_name", "email", "phone"}
    return {k: "***" if k in pii_keys else v for k, v in data.items()}


def _flush(record: dict, retries: int = 10) -> None:
    _buffer.append(record)
    for attempt in range(retries):
        try:
            os.makedirs(os.path.dirname(_AUDIT_PATH) or ".", exist_ok=True)
            with open(_AUDIT_PATH, "a", encoding="utf-8") as f:
                for r in _buffer:
                    f.write(json.dumps(r) + "\n")
            _buffer.clear()
            return
        except OSError:
            time.sleep(0.2 * (2 ** attempt))
    # buffer retained for next flush attempt — never silently dropped
