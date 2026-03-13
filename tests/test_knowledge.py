import pytest
from unittest.mock import MagicMock, patch
from nonagentic.tools.knowledge import (
    search_policy_docs,
    multi_query_search,
    _expand_queries,
)


def test_search_policy_docs_no_collection():
    with patch("src.tools.knowledge._get_collection", return_value=None):
        result = search_policy_docs("test query")
        assert result["chunks"] == []
        assert "unavailable" in result["message"]


def test_search_policy_docs_success():
    mock_collection = MagicMock()
    mock_collection.query.return_value = {
        "documents": [["doc1", "doc2"]],
        "metadatas": [
            [
                {"source": "s1", "doc_type": "policy"},
                {"source": "s2", "doc_type": "policy"},
            ]
        ],
        "distances": [[0.1, 0.2]],
    }
    with patch("src.tools.knowledge._get_collection", return_value=mock_collection):
        result = search_policy_docs("test query", doc_type="policy", top_k=2)
        assert len(result["chunks"]) == 2
        assert result["chunks"][0]["text"] == "doc1"
        assert result["chunks"][0]["score"] == 0.1


def test_multi_query_search_no_results():
    with patch("src.tools.knowledge._get_collection", return_value=None):
        result = multi_query_search("test query")
        assert result["chunks"] == []


def test_expand_queries_llm_failure():
    with patch("src.core.llm.get_llm", side_effect=Exception("LLM error")):
        queries = _expand_queries("test query")
        assert "test query" in queries
        assert len(queries) == 3
