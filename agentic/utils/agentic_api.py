"""Agentic API - simple interface for executing use cases."""

from typing import Optional
from agentic.orchestrator.orchestrator_agent import create_orchestrator


class AgenticAPI:
    """Simple API for agentic execution."""

    def __init__(self):
        self.orchestrator = create_orchestrator()

    # ── Level 3 methods (existing) ────────────────────────────────────────────

    def execute_uc1_lead_scoring(self, offer_code: str, top_n: int = 10,
                                  segment: Optional[str] = None, mode: str = "deterministic") -> dict:
        """UC1 (L3): Lead Scoring."""
        return self.orchestrator.execute(
            f"Score leads for {offer_code}",
            {"offer_code": offer_code, "top_n": top_n, "segment": segment},
            mode=mode,
        )

    def execute_uc2_enrichment(self, customer_id: str, mode: str = "deterministic") -> dict:
        """UC2 (L3): Customer Enrichment."""
        return self.orchestrator.execute(
            f"Enrich customer {customer_id}",
            {"customer_id": customer_id},
            mode=mode,
        )

    def execute_uc3_nba(self, customer_id: str, mode: str = "deterministic") -> dict:
        """UC3 (L3): Next-Best-Action Recommendation."""
        return self.orchestrator.execute(
            f"Recommend next-best-action for {customer_id}",
            {"customer_id": customer_id},
            mode=mode,
        )

    def execute_uc4_notification(self, customer_id: str, mode: str = "deterministic") -> dict:
        """UC4 (L3): Consent-Gated Notification."""
        return self.orchestrator.execute(
            f"Send notification to {customer_id}",
            {"customer_id": customer_id, "channel": "email"},
            mode=mode,
        )

    def execute_uc5_identity_gate(self, customer_id: str, mode: str = "deterministic") -> dict:
        """UC5 (L3): Identity Gate."""
        return self.orchestrator.execute(
            f"Check identity for {customer_id}",
            {"customer_id": customer_id},
            mode=mode,
        )

    def execute_uc6_bulk_campaign(self, offer_code: str, segment: Optional[str] = None,
                                   top_n: int = 50, mode: str = "deterministic") -> dict:
        """UC6 (L3): Bulk Campaign Targeting."""
        return self.orchestrator.execute(
            f"Generate bulk campaign targeting for {offer_code}",
            {"offer_code": offer_code, "segment": segment, "top_n": top_n},
            mode=mode,
        )

    def execute_uc7_return_risk(self, threshold: float = 0.7, mode: str = "deterministic") -> dict:
        """UC7 (L3): Return Risk Intervention."""
        return self.orchestrator.execute(
            "Identify and intervene with high return risk customers",
            {"threshold": threshold},
            mode=mode,
        )

    def execute_uc8_campaign_dashboard(self, mode: str = "deterministic") -> dict:
        """UC8 (L3): Campaign Results Dashboard."""
        return self.orchestrator.execute(
            "Show campaign performance dashboard",
            {},
            mode=mode,
        )

    def execute_uc9_guardrails(self, text: str, mode: str = "deterministic") -> dict:
        """UC9 (L3): Guardrails."""
        return self.orchestrator.execute(
            "Apply guardrails and redact PII",
            {"text": text},
            mode=mode,
        )

    # ── Level 5 methods (new) ─────────────────────────────────────────────────

    def execute_rec_uc1_user_based(self, customer_id: str, segment: str,
                                    top_k: int = 10, mode: str = "deterministic") -> dict:
        """Rec-UC1: User-Based Recommendations."""
        return self.orchestrator.execute(
            f"User-based segment recommendations for {customer_id}",
            {"customer_id": customer_id, "segment": segment, "top_k": top_k},
            mode=mode,
        )

    def execute_rec_uc2_collaborative(self, customer_id: str,
                                       top_k: int = 10, mode: str = "deterministic") -> dict:
        """Rec-UC2: Collaborative Filtering."""
        return self.orchestrator.execute(
            f"Collaborative filtering recommendations for {customer_id}",
            {"customer_id": customer_id, "top_k": top_k},
            mode=mode,
        )

    def execute_rec_uc3_behaviour(self, customer_id: str,
                                   top_k: int = 10, mode: str = "deterministic") -> dict:
        """Rec-UC3: Behaviour-Based Ranking."""
        return self.orchestrator.execute(
            f"Behaviour-based ranking for {customer_id}",
            {"customer_id": customer_id, "top_k": top_k},
            mode=mode,
        )

    def execute_rec_uc4_hybrid(self, customer_id: str,
                                top_k: int = 10, mode: str = "deterministic") -> dict:
        """Rec-UC4: Hybrid Recommender."""
        return self.orchestrator.execute(
            f"Hybrid recommendations for {customer_id}",
            {"customer_id": customer_id, "top_k": top_k},
            mode=mode,
        )

    def execute_rec_uc5_cold_start(self, customer_id: str, segment: str,
                                    top_k: int = 10, mode: str = "deterministic") -> dict:
        """Rec-UC5: Cold Start Handling."""
        return self.orchestrator.execute(
            f"Cold start recommendations for {customer_id}",
            {"customer_id": customer_id, "segment": segment, "top_k": top_k},
            mode=mode,
        )

    def execute_rec_uc6_cross_segment(self, segment: str, top_k: int = 10,
                                       sample_size: int = 15, mode: str = "deterministic") -> dict:
        """Rec-UC6: Cross-User Segment Recommendations."""
        return self.orchestrator.execute(
            f"Cross-user segment batch recommendations for {segment}",
            {"segment": segment, "top_k": top_k, "sample_size": sample_size},
            mode=mode,
        )

    def execute_rec_uc7_evaluation(self, sample_users: int = 40,
                                    k: int = 10, mode: str = "deterministic") -> dict:
        """Rec-UC7: Recommendation Evaluation."""
        return self.orchestrator.execute(
            "Evaluate recommendation metrics",
            {"sample_users": sample_users, "k": k},
            mode=mode,
        )

    def execute_rec_uc8_visualisation(self, customer_id: str = "CUST-001",
                                       mode: str = "deterministic") -> dict:
        """Rec-UC8: Visualisation."""
        return self.orchestrator.execute(
            f"Visualise recommendation engine for {customer_id}",
            {"customer_id": customer_id},
            mode=mode,
        )

    def execute_rec_uc9_routing(self, request: str, mode: str = "deterministic") -> dict:
        """Rec-UC9: Orchestrator Routing."""
        return self.orchestrator.execute(
            f"Routing test: {request}",
            {"routing_test": True, "original_request": request},
            mode=mode,
        )


def create_api() -> AgenticAPI:
    """Create API instance."""
    return AgenticAPI()
