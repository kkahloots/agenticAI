# 📚 Level‑1 Knowledge Agent Proposal

**TL;DR**: This agent acts as a smart librarian. It retrieves information from documents, databases and APIs, then summarises it in plain language.

### What & Why (ELI5)

When you ask a question, this helper looks through all the available documents, customer data or policies and brings you the answer. It explains the answer concisely and can cite sources so you know where the information came from.

### Formula Rule

`IF request is a factual query OR requires document retrieval THEN use knowledge agent ELSE fallback to next rule.`

### Explanation

The knowledge agent serves simple queries and data lookup tasks. It uses Retrieval‑Augmented Generation (RAG) to search customer profiles, policy manuals or other knowledge bases. It then summarises the relevant information in a user‑friendly way.

### What Is NOT

- ❌ Not for multi‑step tasks that require planning or execution.
- ❌ Not for numerical analysis or pattern discovery.
- ❌ Does not modify data; it only reads and summarises.

### Edge Cases

- **No Data Found**: If the requested information doesn’t exist, return a polite message and suggest alternative queries.
- **Confidential Fields**: Mask sensitive information (e.g. personal identifiers) in the output.
- **Large Documents**: When documents are long, return a concise summary with links to detailed sections.

### Examples

✅ *“What documents do I need for corporate KYC in Estonia?”* → retrieves from KYC manual and summarises.

✅ *“Show me the last transaction date for customer CUST‑001.”* → pulls from the database and returns the date.

❌ *“Segment customers and generate SQL.”* → not a Level‑1 task.
