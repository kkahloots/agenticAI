from __future__ import annotations

import os
from typing import Optional

_CHROMA_DIR = os.getenv("CHROMA_PERSIST_DIR", "data/chroma")
_client = None

_DOC_TYPE_TO_COLLECTION = {
    "policy":  "policy_docs",
    "email":   "emails",
    "note":    "notes",
    "general": "policy_docs",
}

_COLLECTION_TO_DOC_TYPE = {v: k for k, v in _DOC_TYPE_TO_COLLECTION.items()}


def _get_collection(name: str = "policy_docs"):
    global _client
    try:
        import chromadb
        if _client is None:
            _client = chromadb.PersistentClient(path=_CHROMA_DIR)
        return _client.get_or_create_collection(name)
    except Exception:
        return None


def search_policy_docs(query: str, doc_type: Optional[str] = None, top_k: int = 5) -> dict:
    """Single-query vector search across the appropriate collection."""
    col_name = _DOC_TYPE_TO_COLLECTION.get(doc_type or "policy", "policy_docs")
    collection = _get_collection(col_name)
    if collection is None:
        return {"chunks": [], "message": "Policy store unavailable"}
    try:
        results = collection.query(query_texts=[query], n_results=min(top_k, 5))
        chunks = [
            {"text": doc, "source": meta.get("source", "unknown"),
             "doc_type": meta.get("doc_type", doc_type or "policy"), "score": dist}
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            )
        ]
        return {"chunks": chunks}
    except Exception as exc:
        return {"chunks": [], "message": str(exc)}


def multi_query_search(query: str, doc_type: Optional[str] = None, top_k: int = 5) -> dict:
    """
    MultiQueryRetriever — generates query variants via LLM, deduplicates,
    searches across all relevant collections, returns merged top-k chunks.
    """
    queries = _expand_queries(query)
    # Determine which collections to search
    if doc_type:
        collections_to_search = [_DOC_TYPE_TO_COLLECTION.get(doc_type, "policy_docs")]
    else:
        collections_to_search = ["policy_docs", "emails", "notes"]

    seen: set[str] = set()
    merged: list[dict] = []

    for col_name in collections_to_search:
        for q in queries:
            for chunk in search_policy_docs(q, doc_type=_COLLECTION_TO_DOC_TYPE.get(col_name), top_k=top_k).get("chunks", []):
                key = f"{chunk['source']}::{chunk['text'][:80]}"
                if key not in seen:
                    seen.add(key)
                    merged.append(chunk)

    merged.sort(key=lambda c: c.get("score", 1.0))
    top = merged[:top_k]
    if not top:
        return {"chunks": [], "message": "No documents found."}
    return {"chunks": top, "query_variants": queries}


def _expand_queries(query: str) -> list[str]:
    """Generate query variants via the active LLM provider; fall back to rewrites."""
    try:
        from langchain_core.messages import HumanMessage, SystemMessage
        from src.core.llm import get_llm
        llm = get_llm(temperature=0.3)
        resp = llm.invoke([
            SystemMessage(content=(
                "Generate 3 different search queries to retrieve documents relevant to the user question. "
                "Return one query per line, no numbering, no explanation."
            )),
            HumanMessage(content=query),
        ])
        variants = [l.strip() for l in resp.content.strip().splitlines() if l.strip()]
        return ([query] + variants)[:4]
    except Exception:
        return [query, f"policy about {query}", f"rules and guidelines for {query}"]


def ingest_documents(docs: list[dict]) -> None:
    """Ingest [{ id, text, source, doc_type }] into the appropriate collection per doc_type."""
    # Group by target collection
    groups: dict[str, list[dict]] = {}
    for d in docs:
        col = _DOC_TYPE_TO_COLLECTION.get(d.get("doc_type", "general"), "policy_docs")
        groups.setdefault(col, []).append(d)

    for col_name, group in groups.items():
        collection = _get_collection(col_name)
        if collection is None:
            continue
        collection.upsert(
            ids=[d["id"] for d in group],
            documents=[d["text"] for d in group],
            metadatas=[{"source": d["source"], "doc_type": d.get("doc_type", "general")} for d in group],
        )
