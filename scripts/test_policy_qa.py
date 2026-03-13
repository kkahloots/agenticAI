#!/usr/bin/env python3
"""
Comprehensive test of the Policy Q&A system.
Verifies that all three policy questions are answered correctly.
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "notebooks"))

from notebooks.nonagent.utils import ask, get_test_queries

def test_policy_qa():
    """Test all policy questions."""
    queries = get_test_queries()
    policy_questions = queries["policy_questions"]
    
    print("=" * 80)
    print("POLICY Q&A SYSTEM TEST")
    print("=" * 80)
    print()
    
    all_passed = True
    
    for i, question in enumerate(policy_questions, 1):
        print(f"📋 Question {i}: {question}")
        print("-" * 80)
        
        result = ask(question)
        
        # Check routing
        routed_to = result.get("routed_to", "unknown")
        intent = result.get("intent", "unknown")
        
        if routed_to != "level1_knowledge":
            print(f"❌ FAIL: Expected routing to level1_knowledge, got {routed_to}")
            all_passed = False
        else:
            print(f"✅ Routed to: {routed_to}")
        
        if intent != "informational":
            print(f"❌ FAIL: Expected intent 'informational', got {intent}")
            all_passed = False
        else:
            print(f"✅ Intent: {intent}")
        
        # Check answer
        messages = result.get("messages", [])
        if not messages:
            print(f"❌ FAIL: No answer returned")
            all_passed = False
        else:
            answer = messages[-1].content
            if not answer or answer.startswith("❌"):
                print(f"❌ FAIL: Invalid answer: {answer[:100]}")
                all_passed = False
            else:
                print(f"✅ Answer received ({len(answer)} chars)")
                print(f"   Preview: {answer[:150]}...")
        
        # Check chunks
        chunks = result.get("result", {}).get("chunks", []) or result.get("chunks", [])
        if not chunks:
            print(f"⚠️  WARNING: No chunks retrieved")
        else:
            print(f"✅ Chunks retrieved: {len(chunks)}")
            sources = list(set(c['source'] for c in chunks))
            print(f"   Sources: {', '.join(sources)}")
        
        print()
    
    print("=" * 80)
    if all_passed:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 80)
    
    return all_passed

if __name__ == "__main__":
    success = test_policy_qa()
    sys.exit(0 if success else 1)
