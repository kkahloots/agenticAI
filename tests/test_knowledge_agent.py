"""Tests for knowledge agent."""

import pytest
from unittest.mock import MagicMock, patch
from langchain_core.messages import AIMessage
from agentic.agentic_state import new_agentic_state
from agentic.knowledge_agent import (
    knowledge_agent,
    _extract_customer_id,
    _synthesize_answer,
    _rag_generate,
)


class TestExtractCustomerId:
    """Test customer ID extraction from text."""

    def test_extract_cust_format(self):
        """Test extracting CUST-XXX format."""
        customer_id = _extract_customer_id("Show me CUST-001")
        assert customer_id == "CUST-001"

    def test_extract_case_insensitive(self):
        """Test extraction is case insensitive."""
        customer_id = _extract_customer_id("Show me cust-001")
        assert customer_id == "CUST-001"

    def test_extract_multiple_returns_first(self):
        """Test that multiple IDs returns first."""
        customer_id = _extract_customer_id("Compare CUST-001 and CUST-002")
        assert customer_id == "CUST-001"

    def test_extract_returns_none_if_not_found(self):
        """Test returns None if not found."""
        customer_id = _extract_customer_id("Show me customer profile")
        assert customer_id is None


class TestSynthesizeAnswer:
    """Test answer synthesis."""

    def test_synthesize_error_result(self):
        """Test synthesizing error result."""
        result = {"error": "Customer not found"}
        answer = _synthesize_answer(result, "test")
        assert "error" in answer.lower()

    def test_synthesize_customer_result(self):
        """Test synthesizing customer result."""
        result = {
            "customer": {
                "customer_id": "CUST-001",
                "segment": "VIP",
                "identity_status": "verified",
                "fraud_score": 0.1,
                "engagement_score": 0.9,
            }
        }
        answer = _synthesize_answer(result, "test")
        assert "CUST-001" in answer
        assert "VIP" in answer

    def test_synthesize_empty_customer(self):
        """Test synthesizing empty customer."""
        result = {"customer": None}
        answer = _synthesize_answer(result, "test")
        assert "not found" in answer.lower()

    def test_synthesize_products_result(self):
        """Test synthesizing products result."""
        result = {
            "products": [
                {"product_id": "PROD-001"},
                {"product_id": "PROD-002"},
            ]
        }
        answer = _synthesize_answer(result, "test")
        assert "2 products" in answer

    def test_synthesize_empty_products(self):
        """Test synthesizing empty products."""
        result = {"products": []}
        answer = _synthesize_answer(result, "test")
        assert "No products" in answer

    def test_synthesize_chunks_result(self):
        """Test synthesizing chunks result."""
        result = {
            "chunks": [
                {"doc_type": "policy", "source": "file1.txt", "text": "Policy content"}
            ]
        }
        answer = _synthesize_answer(result, "test")
        assert answer is not None

    def test_synthesize_empty_chunks(self):
        """Test synthesizing empty chunks."""
        result = {"chunks": []}
        answer = _synthesize_answer(result, "test")
        assert "No relevant information" in answer

    def test_synthesize_unknown_result(self):
        """Test synthesizing unknown result format."""
        result = {"unknown_key": "value"}
        answer = _synthesize_answer(result, "test")
        assert answer is not None


class TestRagGenerate:
    """Test RAG answer generation."""

    def test_rag_generate_with_chunks(self):
        """Test RAG generation with chunks."""
        chunks = [
            {"doc_type": "policy", "source": "file1.txt", "text": "Policy content here"}
        ]
        answer = _rag_generate("What is the policy?", chunks)
        assert answer is not None
        assert len(answer) > 0

    def test_rag_generate_multiple_chunks(self):
        """Test RAG generation with multiple chunks."""
        chunks = [
            {"doc_type": "policy", "source": "file1.txt", "text": "Policy 1"},
            {"doc_type": "note", "source": "file2.txt", "text": "Note 1"},
        ]
        answer = _rag_generate("What is the policy?", chunks)
        assert answer is not None

    def test_rag_generate_truncates_long_text(self):
        """Test that RAG generation truncates long text."""
        long_text = "x" * 1000
        chunks = [
            {"doc_type": "policy", "source": "file1.txt", "text": long_text}
        ]
        answer = _rag_generate("What is this?", chunks)
        assert len(answer) < len(long_text)

    def test_rag_generate_handles_missing_fields(self):
        """Test RAG generation with missing fields."""
        chunks = [
            {"text": "Content without doc_type or source"}
        ]
        answer = _rag_generate("What is this?", chunks)
        assert answer is not None


class TestKnowledgeAgent:
    """Test knowledge agent."""

    def test_knowledge_agent_returns_dict(self):
        """Test that knowledge agent returns dict."""
        state = new_agentic_state("Show me CUST-001", user_id="user1")
        state["intent"] = "knowledge"
        state["confidence"] = 0.9
        
        result = knowledge_agent(state)
        assert isinstance(result, dict)

    def test_knowledge_agent_sets_active_agent(self):
        """Test that knowledge agent sets active_agent."""
        state = new_agentic_state("Show me CUST-001", user_id="user1")
        state["intent"] = "knowledge"
        state["confidence"] = 0.9
        
        result = knowledge_agent(state)
        assert result["active_agent"] == "knowledge"

    def test_knowledge_agent_has_messages(self):
        """Test that knowledge agent returns messages."""
        state = new_agentic_state("Show me CUST-001", user_id="user1")
        state["intent"] = "knowledge"
        state["confidence"] = 0.9
        
        result = knowledge_agent(state)
        assert "messages" in result
        assert len(result["messages"]) > 0

    def test_knowledge_agent_has_audit_trail(self):
        """Test that knowledge agent has audit trail."""
        state = new_agentic_state("Show me CUST-001", user_id="user1")
        state["intent"] = "knowledge"
        state["confidence"] = 0.9
        
        result = knowledge_agent(state)
        assert "audit_trail" in result
        assert len(result["audit_trail"]) > 0

    def test_knowledge_agent_has_mcp_calls(self):
        """Test that knowledge agent records MCP calls."""
        state = new_agentic_state("Show me CUST-001", user_id="user1")
        state["intent"] = "knowledge"
        state["confidence"] = 0.9
        
        result = knowledge_agent(state)
        assert "mcp_calls" in result

    def test_knowledge_agent_has_intermediate_results(self):
        """Test that knowledge agent has intermediate results."""
        state = new_agentic_state("Show me CUST-001", user_id="user1")
        state["intent"] = "knowledge"
        state["confidence"] = 0.9
        
        result = knowledge_agent(state)
        assert "intermediate_results" in result

    def test_knowledge_agent_has_final_result(self):
        """Test that knowledge agent has final result."""
        state = new_agentic_state("Show me CUST-001", user_id="user1")
        state["intent"] = "knowledge"
        state["confidence"] = 0.9
        
        result = knowledge_agent(state)
        assert "final_result" in result

    def test_knowledge_agent_has_agent_history(self):
        """Test that knowledge agent updates agent history."""
        state = new_agentic_state("Show me CUST-001", user_id="user1")
        state["intent"] = "knowledge"
        state["confidence"] = 0.9
        
        result = knowledge_agent(state)
        assert "agent_history" in result
        assert "knowledge" in result["agent_history"]

    def test_knowledge_agent_with_product_query(self):
        """Test knowledge agent with product query."""
        state = new_agentic_state("Show me products", user_id="user1")
        state["intent"] = "knowledge"
        state["confidence"] = 0.9
        
        result = knowledge_agent(state)
        assert result["active_agent"] == "knowledge"

    def test_knowledge_agent_with_generic_query(self):
        """Test knowledge agent with generic query."""
        state = new_agentic_state("What is the policy?", user_id="user1")
        state["intent"] = "knowledge"
        state["confidence"] = 0.9
        
        result = knowledge_agent(state)
        assert result["active_agent"] == "knowledge"
