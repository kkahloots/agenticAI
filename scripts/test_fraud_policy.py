#!/usr/bin/env python3
"""
Test policy search to verify RAG is working and display fraud score thresholds.
"""
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

from dotenv import load_dotenv

load_dotenv()

from nonagentic.tools.knowledge import search_policy_docs


def test_fraud_policy():
    """Search for fraud score thresholds."""
    query = "What are the fraud score thresholds that trigger manual approval?"

    print(f"🔍 Query: {query}\n")
    result = search_policy_docs(query, doc_type="policy", top_k=5)

    if not result.get("chunks"):
        print("❌ No results found")
        return False

    print(f"✅ Found {len(result['chunks'])} result(s):\n")
    for i, chunk in enumerate(result["chunks"], 1):
        print(f"📄 Result {i} (source: {chunk['source']}, score: {chunk['score']:.3f})")
        print(f"   {chunk['text']}\n")

    return True


if __name__ == "__main__":
    success = test_fraud_policy()
    sys.exit(0 if success else 1)
