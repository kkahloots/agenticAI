import pytest
from nonagentic.tools.customer import search_customer_profile, get_kyc_status
from nonagentic.tools.functional import send_notification, create_case, recommend_offer
from nonagentic.tools.analytics import run_sql_query, generate_segment
from nonagentic.tools.strategic import schedule_campaign
from nonagentic.tools.audit import log_audit_event
from nonagentic.tools.approval import request_human_approval, set_auto_approve


# ── customer ──────────────────────────────────────────────────────────────────


def test_search_customer_by_id():
    result = search_customer_profile(customer_id="CUST-001")
    assert result["customer"] is not None
    assert result["customer"]["customer_id"] == "CUST-001"
    assert result["match_confidence"] == 1.0


def test_search_customer_not_found():
    result = search_customer_profile(customer_id="CUST-999")
    assert result["customer"] is None
    assert result["match_confidence"] == 0.0


def test_get_kyc_status_returns_fields():
    result = get_kyc_status("CUST-001")
    assert "kyc_status" in result
    assert result["kyc_status"] in ("verified", "unverified", "pending")


def test_get_kyc_status_unknown_customer():
    result = get_kyc_status("CUST-999")
    assert result.get("error") == "customer_not_found"


# ── consent gate ──────────────────────────────────────────────────────────────


def test_send_notification_blocked_when_no_marketing_consent(monkeypatch):
    """Patch customer data to force marketing=False."""
    from nonagentic.tools import customer as cmod

    fake = {
        "customer_id": "CUST-TEST",
        "consent_flags": {
            "marketing": False,
            "email": True,
            "sms": True,
            "data_sharing": True,
        },
    }
    monkeypatch.setattr(cmod, "_find", lambda *a, **kw: fake)
    result = send_notification("CUST-TEST", "email", {"body": "hi"})
    assert result["status"] == "blocked"
    assert "consent" in result["reason"]


def test_send_notification_blocked_no_sms_consent(monkeypatch):
    from nonagentic.tools import customer as cmod

    fake = {
        "customer_id": "CUST-TEST",
        "consent_flags": {
            "marketing": True,
            "email": True,
            "sms": False,
            "data_sharing": True,
        },
    }
    monkeypatch.setattr(cmod, "_find", lambda *a, **kw: fake)
    result = send_notification("CUST-TEST", "sms", {"body": "hi"})
    assert result["status"] == "blocked"


def test_send_notification_dry_run():
    result = send_notification("CUST-001", "email", {"body": "test"}, dry_run=True)
    # dry_run should not block on consent (consent check still runs) but status = queued
    assert result["status"] in ("queued", "blocked", "sent")


# ── case creation ─────────────────────────────────────────────────────────────


def test_create_case_returns_case_id():
    result = create_case("CUST-002", "general", "Test case")
    assert result["case_id"].startswith("CASE-")
    assert result["status"] == "open"


def test_create_case_deduplicates():
    first = create_case("CUST-003", "kyc_remediation", "KYC expired")
    second = create_case("CUST-003", "kyc_remediation", "KYC expired again")
    assert first["case_id"] == second["case_id"]
    assert second.get("duplicate") is True


# ── analytics ─────────────────────────────────────────────────────────────────


def test_run_sql_query_rejects_unsafe():
    result = run_sql_query("DROP TABLE customers")
    assert result["error"] == "unsafe_query"


def test_run_sql_query_rejects_insert():
    result = run_sql_query("INSERT INTO customers VALUES (1)")
    assert result["error"] == "unsafe_query"


def test_generate_segment_returns_segments():
    result = generate_segment(algorithm="rules")
    assert "segments" in result
    assert len(result["segments"]) > 0
    seg = result["segments"][0]
    assert "label" in seg and "size" in seg


def test_generate_segment_insufficient_data():
    result = generate_segment(
        filters={"kyc_status": "nonexistent_status"}, algorithm="rules"
    )
    assert "warning" in result or "segments" in result


# ── strategic ─────────────────────────────────────────────────────────────────


def test_schedule_campaign_requires_approval_for_large_reach():
    result = schedule_campaign(
        campaign_name="Big Campaign",
        segment_id="high-value",
        steps=[{"channel": "email", "template_id": "T-UPSELL-01", "delay_days": 0}],
        start_date="2025-08-01",
        estimated_reach=1500,
        approved=False,
    )
    assert result["status"] == "approval_required"
    assert result["campaign_id"] is None


def test_schedule_campaign_succeeds_when_approved():
    result = schedule_campaign(
        campaign_name="Small Campaign",
        segment_id="new",
        steps=[
            {"channel": "sms", "template_id": "T-PAYMENT-REMINDER", "delay_days": 0}
        ],
        start_date="2025-08-01",
        estimated_reach=50,
        approved=True,
    )
    assert result["campaign_id"] is not None
    assert result["status"] == "scheduled"


# ── audit ─────────────────────────────────────────────────────────────────────


def test_log_audit_event_returns_logged(tmp_path, monkeypatch):
    monkeypatch.setenv("AUDIT_LOG_PATH", str(tmp_path / "audit.jsonl"))
    import importlib, nonagentic.tools.audit as amod

    importlib.reload(amod)
    result = amod.log_audit_event(
        "test_agent", "test_action", {"key": "val"}, {"out": 1}
    )
    assert result["status"] == "logged"
    assert "audit_id" in result


def test_audit_masks_pii(tmp_path, monkeypatch):
    import json

    monkeypatch.setenv("AUDIT_LOG_PATH", str(tmp_path / "audit.jsonl"))
    import importlib, nonagentic.tools.audit as amod

    importlib.reload(amod)
    amod.log_audit_event(
        "agent", "action", {"email": "real@email.com", "safe": "ok"}, {}
    )
    lines = (tmp_path / "audit.jsonl").read_text().strip().splitlines()
    record = json.loads(lines[-1])
    assert record["inputs"]["email"] == "***"
    assert record["inputs"]["safe"] == "ok"


# ── approval ──────────────────────────────────────────────────────────────────


def test_approval_auto_approves_in_dev():
    set_auto_approve(True)
    result = request_human_approval("wf-1", "Test action", "low")
    assert result["approved"] is True


def test_approval_rejects_when_disabled():
    set_auto_approve(False)
    result = request_human_approval("wf-2", "Risky action", "high")
    assert result["approved"] is False
    set_auto_approve(True)  # restore
