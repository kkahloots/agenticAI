import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture(autouse=True)
def no_llm(request, monkeypatch):
    """
    Prevent any real LLM calls during tests.
    Skipped for tests marked with @pytest.mark.real_llm_factory so that
    test_llm_factory.py can inspect the actual objects returned by get_llm().
    """
    if request.node.get_closest_marker("real_llm_factory"):
        return
    mock_llm = MagicMock()
    mock_llm.return_value.invoke.side_effect = Exception("LLM disabled in tests")
    monkeypatch.setattr("langchain_openai.ChatOpenAI", mock_llm)
