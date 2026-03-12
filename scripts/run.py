#!/usr/bin/env python3
"""
Run the agentic graph with one example request per intent type.
Usage:
    PYTHONPATH=. python scripts/run.py
"""
import json
from dotenv import load_dotenv
load_dotenv()

from src.graph import graph
from src.core.state import new_state

REQUESTS = [
    ("informational", "What is the KYC status of customer CUST-001?"),
    ("analytical",    "Show me a segment breakdown of high-risk customers"),
    ("action",        "Send a retention offer to customer CUST-042"),
    ("strategic",     "Increase product adoption among low-engagement customers this quarter"),
]

for intent, request in REQUESTS:
    print(f"\n{'='*60}")
    print(f"[{intent.upper()}] {request}")
    print("="*60)

    state = new_state(request, user_id="analyst@bank.com")
    result = graph.invoke(
        state,
        config={"configurable": {"thread_id": state["request_id"]}},
    )

    print(f"Routed to : {result.get('routed_to', 'unknown')}")
    print(f"Confidence: {result.get('confidence', 0):.2f}")
    print(f"Result    : {json.dumps(result.get('result'), indent=2, default=str)}")
    print(f"Audit trail ({len(result.get('audit_trail', []))} events)")
