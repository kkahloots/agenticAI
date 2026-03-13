# 🔍 Level 1 — Knowledge & Retrieval Agent

**TL;DR**: The knowledge agent answers questions by retrieving relevant documents from a vector store and synthesizing answers using RAG (Retrieval-Augmented Generation). It understands context, extracts entities, and cites sources.

---

## Business Use Cases

### 1. Document Search & Synthesis
A user asks a question about policies, procedures, or historical information. The agent searches the vector store, retrieves the most relevant documents, and synthesizes a clear answer with citations.

**Trigger**: Any question requiring document retrieval.

**Output**: Synthesized answer with cited sources and relevance scores.

**Technology**: Semantic search using vector embeddings (Chroma/Pinecone) + LLM synthesis.

---

### 2. Entity Extraction & Context
The agent extracts key entities from the user's question (e.g., customer ID, country, product type) to improve search precision and context assembly.

**Trigger**: Automatic on every query.

**Output**: Structured entities used to refine document retrieval.

---

### 3. Multi-Query Retrieval
For complex questions, the agent generates multiple reformulations of the user's query to improve recall. Instead of searching once, it searches multiple ways and combines results.

**Trigger**: Automatic on every query.

**Output**: Higher recall by searching from multiple angles.

**Technology**: MultiQueryRetriever pattern.

---

### 4. Memory Integration
The agent stores user requests and responses in short-term memory, allowing follow-up questions to reference previous context without re-explaining.

**Trigger**: Automatic after each response.

**Output**: Conversation context available for subsequent queries.

---

### 5. PII Masking
Before returning results, the agent masks personally identifiable information (email addresses, phone numbers, names) according to compliance rules.

**Trigger**: Automatic on every response.

**Output**: Sanitized response with PII redacted.

---

## Key Features

### Semantic Search
Instead of keyword matching, the agent understands meaning. So "renewal reminder" will match documents about "identity verification expiry notice" even if the exact words differ.

### Multi-Query Retrieval
For complex questions, the agent generates multiple reformulations to improve recall. This ensures better coverage of relevant documents.

### Retrieval-Augmented Generation (RAG)
The agent:
1. Searches the vector store for relevant sections
2. Passes those sections to the LLM
3. Returns a synthesised, cited answer — not just a raw document dump

### Entity Extraction
Automatically extracts key entities (customer ID, country, product type, etc.) from user questions to improve search precision.

### Automatic PII Masking
Every response is checked for:
- **Email addresses** — automatically redacted
- **Phone numbers** — automatically redacted
- **Names** — automatically masked

---

## How It Works

```
Your question
     │
     ▼
Query Understanding: Extract keywords and entities
     │
     ▼
Multi-Query Retrieval: Generate multiple reformulations
     │
     ▼
Semantic Search: Find top documents from vector store
     │
     ▼
Context Assembly: Select and organize retrieved chunks
     │
     ▼
Answer Generation: LLM synthesizes answer with citations
     │
     ▼
PII Masking: Redact sensitive information
     │
     ▼
Memory Update: Store request and response for context
     │
     ▼
Answer returned
```

---

## Architecture

```
Level 1 Agent (src/agents/level1.py)
│
├── Query Understanding
│   ├── Restate user question
│   ├── Extract keywords
│   └── Extract entities (customer ID, country, etc.)
│
├── Multi-Query Retrieval
│   ├── Generate multiple reformulations
│   └── Improve recall from multiple angles
│
├── Semantic Search
│   ├── Vector embedding (Chroma/Pinecone)
│   ├── Similarity ranking
│   └── Top-K document selection
│
├── Context Assembly
│   ├── Select relevant chunks
│   └── Organize for LLM input
│
├── Answer Synthesis
│   ├── LLM generation with context
│   ├── Citation tracking
│   └── Source attribution
│
├── PII Masking
│   ├── Email redaction
│   ├── Phone number redaction
│   └── Name masking
│
└── Memory Integration
    ├── Store requests
    ├── Store responses
    └── Maintain conversation context
```

---

## Configuration

### Environment Variables

```bash
# Vector Store
VECTOR_STORE=chroma              # or pinecone
CHROMA_COLLECTION=documents

# LLM
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key_here

# Retrieval
MAX_DOCUMENTS_PER_QUERY=5        # Avoid latency
RETRIEVAL_TIMEOUT=30             # seconds

# PII Masking
PII_MASKING_ENABLED=true
MASK_EMAILS=true
MASK_PHONE_NUMBERS=true
MASK_NAMES=true
```

### Adding New Documents

1. Place documents in `data/docs/` (markdown, PDF, text)
2. Run the ingestion script:
   ```bash
   python scripts/ingest_folder.py data/docs/
   ```
3. Documents are immediately searchable via semantic search

---

## Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Query understanding | ~100ms | Entity extraction |
| Multi-query generation | ~200ms | Generate reformulations |
| Semantic search (1000 docs) | ~500ms | Vector similarity |
| Context assembly | ~100ms | Select top chunks |
| Answer synthesis | ~2-3s | LLM generation |
| PII masking | ~50ms | Regex patterns |
| **Total** | **~3-4s** | End-to-end |

---

## Constraints

- Do not fetch more than 5 documents per query to avoid latency
- Mask personally identifiable information (PII) according to compliance rules
- Use MultiQueryRetriever to improve recall on complex questions
- Integrate AI capabilities (sentiment analysis, clustering) only as retrieval helpers if needed

---

## Troubleshooting

### "No documents found"
**Cause**: Documents not ingested or search term too specific.

**Solution**: Run `python scripts/ingest_folder.py data/docs/` to ingest documents.

### "PII masking too aggressive"
**Cause**: Masking legitimate content.

**Solution**: Adjust patterns in `src/core/guardrails.py` or set `PII_MASKING_ENABLED=false` for testing.

### "Slow response times"
**Cause**: Too many documents being retrieved or LLM latency.

**Solution**: Reduce `MAX_DOCUMENTS_PER_QUERY` or use a faster LLM model.

### "Poor answer quality"
**Cause**: Irrelevant documents retrieved or insufficient context.

**Solution**: Improve document quality, add more relevant documents, or adjust retrieval parameters.

---

## API Reference

### Document Search

```python
from nonagentic.tools.knowledge import search_documents

results = search_documents("What is the fraud policy?", top_k=5)
# Returns: [{source, relevance, content}, ...]
```

### Multi-Query Search

```python
from nonagentic.tools.knowledge import multi_query_search

results = multi_query_search("How do we handle disputes?", top_k=5)
# Returns: [{source, relevance, content}, ...]
```

### Answer Synthesis (RAG)

```python
from nonagentic.tools.knowledge import synthesize_answer

answer = synthesize_answer("What is the identity verification policy?")
# Returns: {answer, sources, citations}
```

### Entity Extraction

```python
from nonagentic.tools.knowledge import extract_entities

entities = extract_entities("Show me fraud policies for high-value transactions in Europe")
# Returns: {keywords: [...], entities: {country: "Europe", transaction_type: "high-value"}}
```

---

## Key Differences from Nonagent Pipeline

| Aspect | Level 1 | Other Levels |
|--------|---------|-------------|
| **Purpose** | Read-only retrieval | Action-oriented |
| **Data Access** | Vector store search | SQL queries, APIs |
| **Output** | Synthesized answers | Structured data, actions |
| **Latency** | 3-4 seconds | Variable |
| **Autonomy** | None (retrieval only) | High (can execute actions) |

---

## Next Steps

Level 1 is the **read-only** retrieval layer. When you need to *act* on what you find:

- **Level 2** — run SQL analytics, segment customers, generate charts
- **Level 3** — send notifications, create cases, recommend offers
- **Level 4** — run full campaigns, track KPIs, self-correct strategy
