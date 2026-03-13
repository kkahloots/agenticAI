#!/usr/bin/env python3
"""
Initialize RAG system by ingesting policy documents into ChromaDB.
Run this once after setup to populate the vector store.
"""
import sys
import os
from pathlib import Path

# Setup paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

from dotenv import load_dotenv

load_dotenv()

from nonagentic.tools.loader import load_file
from nonagentic.tools.knowledge import ingest_documents


def init_rag():
    """Ingest all policy documents into ChromaDB."""
    docs_folder = project_root / "data" / "docs" / "policies"

    if not docs_folder.exists():
        print(f"❌ Policies folder not found: {docs_folder}")
        return False

    policy_files = list(docs_folder.glob("*.md"))
    if not policy_files:
        print(f"❌ No policy files found in {docs_folder}")
        return False

    print(f"📚 Ingesting {len(policy_files)} policy documents...")
    total_chunks = 0

    for policy_file in sorted(policy_files):
        chunks = load_file(policy_file)
        if chunks:
            ingest_documents(chunks)
            total_chunks += len(chunks)
            print(f"  ✅ {policy_file.name}: {len(chunks)} chunk(s)")
        else:
            print(f"  ⚠️  {policy_file.name}: no content")

    print(f"\n✅ RAG initialized: {total_chunks} chunks ingested")
    return True


if __name__ == "__main__":
    success = init_rag()
    sys.exit(0 if success else 1)
