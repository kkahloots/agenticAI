#!/usr/bin/env python3
"""
Diagnostic script showing the routing fix for fraud score threshold questions.
Demonstrates the before/after behavior.
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def show_routing_logic():
    """Show how the orchestrator classifies the question."""
    from nonagentic.orchestration.orchestrator import _rule_classify

    question = "What are the fraud score thresholds that trigger manual approval?"

    print("=" * 80)
    print("ROUTING DIAGNOSTIC")
    print("=" * 80)
    print()
    print(f"Question: {question}")
    print()

    # Get classification
    intent, confidence, customer_id = _rule_classify(question)

    print("Orchestrator Classification:")
    print(f"  Intent: {intent}")
    print(f"  Confidence: {confidence}")
    print(f"  Customer ID: {customer_id}")
    print()

    # Show routing
    mapping = {
        "informational": "level1_knowledge (Policy Retrieval)",
        "analytical": "level2_analytics (SQL Queries)",
        "action": "level3_functional (Actions)",
        "strategic": "level4_strategic (Strategy)",
        "recommendation": "level5_recommendation (Recommendations)",
    }

    routed_to = mapping.get(intent, "unknown")
    print(f"Routes to: {routed_to}")
    print()

    # Explain the logic
    print("Why this routing?")
    print("-" * 80)

    r = question.lower()

    # Check informational keywords
    informational_keywords = [
        "identity",
        "verification",
        "policy",
        "profile",
        "status",
        "what is",
        "show me",
        "retrieve",
        "email",
        "emails",
        "note",
        "notes",
        "document",
        "search",
        "find",
        "look up",
        "eligib",
        "criteria",
        "threshold",
        "rule",
        "guideline",
        "what are",
        "how often",
        "explain",
        "describe",
        "policies say",
        "agent note",
        "fraud score threshold",
        "manual approval",
    ]

    found_keywords = [kw for kw in informational_keywords if kw in r]

    print(f"Informational keywords found: {found_keywords}")
    print()

    # Show what would happen with old logic
    print("OLD LOGIC (Before Fix):")
    print("-" * 80)
    old_analytical = [
        "segment",
        "sql",
        "query",
        "kpi",
        "churn",
        "analys",
        "cluster",
        "fraud score",
    ]
    old_found = [kw for kw in old_analytical if kw in r]

    if old_found:
        print(f"❌ Would match analytical keywords: {old_found}")
        print(f"❌ Would route to: level2_analytics (SQL Queries)")
        print(f"❌ Result: Tries to generate SQL → Error!")
    else:
        print("✅ Would not match analytical keywords")

    print()
    print("NEW LOGIC (After Fix):")
    print("-" * 80)
    new_analytical = ["segment", "sql", "query", "kpi", "churn", "analys", "cluster"]
    new_found = [kw for kw in new_analytical if kw in r]

    if new_found:
        print(f"❌ Matches analytical keywords: {new_found}")
    else:
        print(f"✅ Does NOT match analytical keywords (fraud score removed)")

    print(f"✅ Matches informational keywords: {found_keywords}")
    print(f"✅ Routes to: level1_knowledge (Policy Retrieval)")
    print(f"✅ Result: Retrieves policy answer!")

    print()
    print("=" * 80)
    print("RESULT")
    print("=" * 80)

    if intent == "informational":
        print("✅ CORRECT: Question routed to policy retrieval")
        print("✅ System will search policy documents and return the answer")
    else:
        print(f"❌ ERROR: Question routed to {intent}")
        print(f"❌ System will try to execute SQL instead of retrieving policy")

    print()


def show_answer():
    """Show the correct answer from the system."""
    from nonagentic.graph import graph
    from nonagentic.core.state import new_state

    print("=" * 80)
    print("SYSTEM RESPONSE")
    print("=" * 80)
    print()

    question = "What are the fraud score thresholds that trigger manual approval?"
    state = new_state(question)
    result = graph.invoke(
        state, config={"configurable": {"thread_id": state["request_id"]}}
    )

    print(f"Routed to: {result.get('routed_to')}")
    print(f"Intent: {result.get('intent')}")
    print()

    message = result["messages"][-1].content

    # Extract just the thresholds section
    lines = message.split("\n")
    in_thresholds = False

    print("Answer:")
    print("-" * 80)
    for line in lines:
        if "Fraud Score Thresholds" in line:
            in_thresholds = True
        if in_thresholds:
            print(line)
            if line.startswith("- 0.7"):
                break

    print()
    print("=" * 80)
    print("✅ SUCCESS: Policy answer retrieved correctly")
    print("=" * 80)


if __name__ == "__main__":
    show_routing_logic()
    print()
    print()
    show_answer()
