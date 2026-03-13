"""Level 3 Functional Agent helpers - minimal wrappers for notebook cells."""

import json
import sys
from pathlib import Path

# Get project root - notebooks/nonagent/utils/level3_helpers.py -> agenticAI (4 parents)
_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()


def _ensure_src_path():
    """Ensure src module can be imported."""
    project_root = str(_PROJECT_ROOT)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)


from .visualization import (
    display_lead_scoring_results,
    display_customer_enrichment,
    display_nba_recommendations,
    display_consent_notification,
    display_blocked_example,
    display_kyc_gate,
    display_campaign_execution_plan,
    display_return_risk_intervention,
    display_campaign_results_dashboard,
    display_title,
    display_side_by_side,
    display_violations_list,
    display_status_banner,
)
from .display_helpers import display_metrics


def run_lead_scoring(offer_code: str, top_n: int = 10):
    """UC1: Lead Scoring - identify top prospects."""
    _ensure_src_path()
    from nonagentic.tools.leads import score_leads

    result = score_leads(offer_code, top_n=top_n)
    display_lead_scoring_results(result)


def run_customer_enrichment(customer_id: str):
    """UC2: Customer Enrichment - multi-source data."""
    _ensure_src_path()
    from nonagentic.tools.leads import enrich_customer

    enriched = enrich_customer(customer_id)
    display_customer_enrichment(enriched, customer_id)


def run_nba_recommendations(customer_ids: list):
    """UC3: NBA Recommendation - ranked offer scoring."""
    _ensure_src_path()
    from nonagentic.tools.functional import recommend_offer
    from nonagentic.tools.customer import search_customer_profile

    display_nba_recommendations(customer_ids, recommend_offer, search_customer_profile)


def run_consent_notification(customer_id: str, blocked_id: str):
    """UC4: Consent-Gated Notification - send offer with consent check."""
    _ensure_src_path()
    from nonagentic.tools.functional import (
        recommend_offer,
        draft_email,
        send_notification,
    )

    offer = recommend_offer(customer_id)
    draft = draft_email(
        customer_id, "T-PROMO-01", variables={"offer_name": offer["offer_name"]}
    )
    send_result = send_notification(
        customer_id, "email", {"subject": draft["subject"], "body": draft["body"]}
    )

    display_consent_notification(customer_id, send_result, draft)

    blocked_result = send_notification(
        blocked_id, "email", {"subject": "Test", "body": "Test"}
    )
    display_blocked_example(blocked_id, blocked_result)


def run_identity_gate(customer_id: str):
    """UC5: Identity Gate - block action on unverified identity."""
    _ensure_src_path()
    from nonagentic.tools.customer import get_kyc_status
    from nonagentic.tools.functional import create_case

    kyc = get_kyc_status(customer_id)

    case = None
    if kyc.get("kyc_status") in ("unverified", "expired"):
        case = create_case(
            customer_id,
            "identity_reverification",
            "Identity unverified — re-verification required before action",
            priority="high",
        )

    display_kyc_gate(customer_id, kyc, case)


def run_bulk_campaign(offer_code: str, segment: str, top_n: int = 50):
    """UC6: Bulk Campaign Targeting - segment-level execution plan."""
    _ensure_src_path()
    from nonagentic.tools.leads import bulk_recommend

    plan = bulk_recommend(offer_code, segment=segment, top_n=top_n)
    display_campaign_execution_plan(plan, offer_code, segment)


def run_return_risk_intervention():
    """UC7: Return Risk Intervention - identify and contact high-return-risk customers."""
    _ensure_src_path()
    from nonagentic.tools.functional import send_notification

    customers = json.loads(Path(_PROJECT_ROOT / "data" / "customers.json").read_text())

    at_risk = [
        c
        for c in customers
        if c.get("return_risk", 0) > 0.7
        and c.get("identity_status") in ("verified", "pending")
        and c.get("consent_flags", {}).get("marketing", False)
    ]
    at_risk.sort(key=lambda x: x["return_risk"], reverse=True)

    display_return_risk_intervention(at_risk, send_notification)


def run_campaign_dashboard():
    """UC8: Campaign Results Dashboard - analyse past campaign performance."""
    campaign_results = json.loads(
        Path(_PROJECT_ROOT / "data" / "campaign_results.json").read_text()
    )
    display_campaign_results_dashboard(campaign_results)


def run_guardrails_demo():
    """UC9: Guardrails - PII redaction and policy enforcement."""
    import os

    _ensure_src_path()
    from nonagentic.core.guardrails import guardrail_check

    os.environ["GUARDRAIL_ENABLED"] = "true"

    test_output = "Customer email is john.doe@example.com and phone is 555-123-4567. We recommend buying shares."
    result = guardrail_check(test_output, request_id="demo-001")

    display_title("Guardrail Check", emoji="🛡️")

    display_side_by_side(
        "❌ Original",
        test_output,
        "✅ Sanitized",
        result.revised_text,
        left_color="#fee2e2",
        left_text_color="#dc2626",
        right_color="#dcfce7",
        right_text_color="#16a34a",
    )

    display_violations_list(result.violations)

    display_metrics(
        {
            "Guardrail Passed": "✅ Yes" if result.passed else "❌ No",
            "Violations Found": len(result.violations),
            "Action Taken": "Redacted PII & forbidden phrases",
        }
    )

    os.environ["GUARDRAIL_ENABLED"] = "false"
    display_status_banner(
        "✅ Guardrails disabled for remaining demos", status="success"
    )
