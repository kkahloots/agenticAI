"""Knowledge Agent - retrieves and synthesizes information."""

from __future__ import annotations
from langchain_core.messages import AIMessage
from agentic.agentic_state import AgenticState
from mcp_servers.customer_data_server import CustomerDataServer
from mcp_servers.product_catalog_server import ProductCatalogServer
from nonagentic.tools.knowledge import multi_query_search
from memory.memory_manager import memory_manager
from nonagentic.tools.audit import log_audit_event


def knowledge_agent(state: AgenticState) -> dict:
    """Knowledge agent - retrieve and synthesize information."""
    request = state["original_request"]
    customer_id = _extract_customer_id(request)

    # Initialize MCP servers
    customer_server = CustomerDataServer()
    product_server = ProductCatalogServer()

    result = {}
    mcp_calls = []

    # Determine what to retrieve
    if customer_id and any(
        w in request.lower() for w in ["profile", "customer", "identity", "kyc"]
    ):
        # Use MCP server for customer data
        result = customer_server.invoke_tool(
            "search_customer_profile", customer_id=customer_id
        )
        mcp_calls.append(
            {
                "server": "customer_data",
                "tool": "search_customer_profile",
                "params": {"customer_id": customer_id},
                "result": result,
            }
        )
    elif any(w in request.lower() for w in ["product", "catalog", "item"]):
        # Use MCP server for product data
        result = product_server.invoke_tool("get_products", limit=10)
        mcp_calls.append(
            {
                "server": "product_catalog",
                "tool": "get_products",
                "params": {"limit": 10},
                "result": result,
            }
        )
    else:
        # Use knowledge base search
        result = multi_query_search(query=request)
        mcp_calls.append(
            {
                "server": "knowledge_base",
                "tool": "multi_query_search",
                "params": {"query": request},
                "result": result,
            }
        )

    # Synthesize answer
    answer = _synthesize_answer(result, request)

    # Log audit
    log_audit_event(
        "knowledge_agent",
        "retrieve_information",
        {"request": request, "customer_id": customer_id},
        {"result_type": type(result).__name__},
        user_id=state["user_id"],
        request_id=state["request_id"],
    )

    # Record to memory
    memory_manager.conversation.add_message(state["session_id"], "assistant", answer)
    memory_manager.interaction.record_interaction(
        state["user_id"], "knowledge_retrieval", {"request": request, "answer": answer}
    )

    return {
        "active_agent": "knowledge",
        "agent_history": ["knowledge"],
        "mcp_calls": mcp_calls,
        "intermediate_results": [{"agent": "knowledge", "result": result}],
        "final_result": result,
        "messages": [AIMessage(content=answer)],
        "audit_trail": [
            {
                "agent": "knowledge",
                "action": "retrieve_information",
                "mcp_calls": len(mcp_calls),
            }
        ],
    }


def _extract_customer_id(text: str) -> str | None:
    """Extract customer ID from text."""
    import re

    match = re.search(r"CUST-\d+", text, re.IGNORECASE)
    return match.group(0).upper() if match else None


def _synthesize_answer(result: dict, request: str) -> str:
    """Synthesize answer from result — uses LLM for chunk-based results."""
    if "error" in result:
        return f"I encountered an error: {result['error']}"

    if "customer" in result:
        c = result["customer"]
        if c:
            return (
                f"Customer: {c['customer_id']} | Segment: {c.get('segment')} | "
                f"Identity: {c.get('identity_status')} | Fraud score: {c.get('fraud_score')} | "
                f"Engagement: {c.get('engagement_score')}"
            )
        return "Customer not found"

    if "products" in result:
        products = result["products"]
        if products:
            return f"Found {len(products)} products: " + ", ".join(
                p.get("product_id", "unknown") for p in products[:5]
            )
        return "No products found"

    if "chunks" in result:
        chunks = result["chunks"]
        if not chunks:
            return "No relevant information found"
        return _rag_generate(request, chunks)

    return str(result)


def _rag_generate(question: str, chunks: list[dict]) -> str:
    """Synthesise a grounded answer from retrieved chunks using the LLM."""
    context = "\n\n".join(
        f"[{c.get('doc_type', 'doc')}] {c.get('source', 'unknown')}:\n{c.get('text', '')[:400]}"
        for c in chunks
    )
    try:
        from langchain_core.messages import HumanMessage, SystemMessage
        from nonagentic.core.llm import get_llm

        llm = get_llm(temperature=0.0)
        resp = llm.invoke(
            [
                SystemMessage(
                    content=(
                        "You are a helpful assistant. Answer the question using the provided sources. "
                        "Cite the source filename in your answer. "
                        "Treat escalation notes, support notes, and agent notes as equivalent. "
                        "If the sources contain relevant information, summarise it clearly."
                    )
                ),
                HumanMessage(content=f"Sources:\n{context}\n\nQuestion: {question}"),
            ]
        )
        return resp.content.strip()
    except Exception:
        lines = [
            f"[{i+1}] [{c.get('source', 'unknown')}] {c.get('text', '')[:200]}" for i, c in enumerate(chunks)
        ]
        return "**Sources:**\n" + "\n".join(lines)
