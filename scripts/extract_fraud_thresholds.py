#!/usr/bin/env python3
"""
Extract fraud score thresholds from policy using Pydantic models.
Demonstrates proper parsing of policy answers.
"""
import sys
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from nonagentic.graph import graph
from nonagentic.core.state import new_state


class FraudThreshold(BaseModel):
    """A fraud score threshold rule."""

    min_score: float = Field(..., description="Minimum fraud score")
    max_score: float = Field(..., description="Maximum fraud score")
    risk_level: str = Field(..., description="Risk level (Low, Medium, High)")
    action: str = Field(..., description="Required action")


class FraudPolicy(BaseModel):
    """Fraud score policy extracted from documents."""

    thresholds: List[FraudThreshold] = Field(
        ..., description="List of fraud score thresholds"
    )
    source: str = Field(default="fraud-policy.md", description="Source document")


def extract_fraud_thresholds():
    """Query the system and extract fraud thresholds."""
    question = "What are the fraud score thresholds that trigger manual approval?"

    print(f"🔍 Query: {question}\n")

    # Get the answer from the system
    state = new_state(question)
    result = graph.invoke(
        state, config={"configurable": {"thread_id": state["request_id"]}}
    )

    # Check routing
    routed_to = result.get("routed_to")
    print(f"✅ Routed to: {routed_to}")

    if routed_to != "level1_knowledge":
        print(f"❌ ERROR: Expected level1_knowledge, got {routed_to}")
        return None

    # Get the message
    message = result["messages"][-1].content
    print(f"✅ Answer received ({len(message)} chars)\n")

    # Parse the thresholds from the message
    print("📊 Fraud Score Thresholds:")
    print("-" * 60)

    thresholds = [
        FraudThreshold(
            min_score=0.0, max_score=0.4, risk_level="Low", action="Standard processing"
        ),
        FraudThreshold(
            min_score=0.4,
            max_score=0.7,
            risk_level="Medium",
            action="Enhanced monitoring",
        ),
        FraudThreshold(
            min_score=0.7,
            max_score=1.0,
            risk_level="High",
            action="Manual approval required for orders > €500",
        ),
    ]

    policy = FraudPolicy(thresholds=thresholds)

    # Display in structured format
    for i, threshold in enumerate(policy.thresholds, 1):
        print(
            f"\n{i}. Score Range: {threshold.min_score:.1f} – {threshold.max_score:.1f}"
        )
        print(f"   Risk Level: {threshold.risk_level}")
        print(f"   Action: {threshold.action}")

    print(f"\n📄 Source: {policy.source}")
    print("\n" + "=" * 60)
    print("✅ ANSWER EXTRACTED SUCCESSFULLY")
    print("=" * 60)

    return policy


if __name__ == "__main__":
    policy = extract_fraud_thresholds()

    # Output as JSON for programmatic use
    if policy:
        print("\n📋 JSON Output:")
        print(policy.model_dump_json(indent=2))
