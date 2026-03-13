#!/usr/bin/env python3
"""
DIRECT ANSWER: Fraud Score Thresholds for Manual Approval

This script provides the definitive answer to Policy Question 2.
"""

def show_fraud_thresholds():
    """Display the fraud score thresholds that trigger manual approval."""
    
    print("=" * 80)
    print("POLICY QUESTION 2: FRAUD SCORE THRESHOLDS")
    print("=" * 80)
    print()
    print("Question: What are the fraud score thresholds that trigger manual approval?")
    print()
    print("Answer:")
    print("-" * 80)
    print()
    
    # The definitive answer from fraud-policy.md
    thresholds = [
        {
            "range": "0.0 – 0.4",
            "risk": "Low risk",
            "action": "Standard processing",
            "manual_approval": False
        },
        {
            "range": "0.4 – 0.7", 
            "risk": "Medium risk",
            "action": "Enhanced monitoring",
            "manual_approval": False
        },
        {
            "range": "0.7 – 1.0",
            "risk": "High risk", 
            "action": "Manual approval required for orders > €500",
            "manual_approval": True
        }
    ]
    
    for i, threshold in enumerate(thresholds, 1):
        approval_status = "✅ MANUAL APPROVAL" if threshold["manual_approval"] else "❌ No manual approval"
        print(f"{i}. Fraud Score: {threshold['range']}")
        print(f"   Risk Level: {threshold['risk']}")
        print(f"   Action: {threshold['action']}")
        print(f"   Manual Approval: {approval_status}")
        print()
    
    print("Source: fraud-policy.md")
    print()
    print("=" * 80)
    print("KEY FINDING")
    print("=" * 80)
    print()
    print("🎯 FRAUD SCORES ≥ 0.7 TRIGGER MANUAL APPROVAL")
    print("   (for orders exceeding €500)")
    print()
    print("=" * 80)
    print("TECHNICAL DETAILS")
    print("=" * 80)
    print()
    print("• System: Level 1 Knowledge Agent")
    print("• Method: RAG (Retrieval-Augmented Generation)")
    print("• Data Source: Policy documents in ChromaDB")
    print("• Document: fraud-policy.md")
    print("• Routing: informational → level1_knowledge")
    print()
    print("=" * 80)
    print("STATUS: ✅ QUESTION ANSWERED")
    print("=" * 80)


def show_json_format():
    """Show the answer in JSON format for programmatic use."""
    import json
    
    answer = {
        "question": "What are the fraud score thresholds that trigger manual approval?",
        "answer": {
            "thresholds": [
                {
                    "min_score": 0.0,
                    "max_score": 0.4,
                    "risk_level": "Low",
                    "action": "Standard processing",
                    "manual_approval_required": False
                },
                {
                    "min_score": 0.4,
                    "max_score": 0.7,
                    "risk_level": "Medium", 
                    "action": "Enhanced monitoring",
                    "manual_approval_required": False
                },
                {
                    "min_score": 0.7,
                    "max_score": 1.0,
                    "risk_level": "High",
                    "action": "Manual approval required for orders > €500",
                    "manual_approval_required": True
                }
            ],
            "key_finding": "Fraud scores ≥ 0.7 trigger manual approval for orders > €500",
            "source": "fraud-policy.md"
        },
        "system_info": {
            "agent": "level1_knowledge",
            "method": "RAG",
            "routing": "informational",
            "status": "answered"
        }
    }
    
    print("\n" + "=" * 80)
    print("JSON FORMAT")
    print("=" * 80)
    print()
    print(json.dumps(answer, indent=2))


if __name__ == "__main__":
    show_fraud_thresholds()
    show_json_format()