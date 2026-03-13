# 🔧 Level‑1 Knowledge Agent Design

### Retrieval Flow

1. **Query Understanding**: Use an LLM to restate the user’s question and extract keywords and entities (e.g. customer ID, country).
2. **Document Search**: Perform a semantic search in the vector store using the extracted keywords. Employ MultiQueryRetriever to improve recall.
3. **Context Assembly**: Select the top chunks of information and assemble them into a prompt context.
4. **Answer Generation**: Use a summarisation chain to answer the question using the context, citing sources when available.
5. **Memory Update**: Store the user’s request and the response in short‑term memory for context in subsequent questions.

### Implementation Notes

- Utilise RAG pipelines with Pinecone or Chroma for vector storage.
- Integrate the AI capabilities described in the pdf (e.g. BERT for sentiment analysis and K‑means for clustering) only as retrieval helpers if needed; do not perform analytics here.

### Constraints

- Do not fetch more than 5 documents per query to avoid latency.
- Mask personally identifiable information (PII) according to compliance rules.
