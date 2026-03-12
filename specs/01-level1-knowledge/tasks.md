# 📝 Level‑1 Knowledge Agent Tasks

1. **Set Up Vector Store**: Ingest the customer documents, policy manuals and FAQs into a vector database with metadata fields (e.g. source, date).
2. **Implement MultiQueryRetriever**: Generate multiple search queries from the user’s question to improve result diversity.
3. **Create Summarisation Chain**: Build a chain using an LLM to summarise retrieved chunks with citations.
4. **Develop Answer Formatter**: Include citation markers in the response so users can verify the source.
5. **Add Safeguards**: Ensure sensitive fields such as KYC documents are not exposed directly.
