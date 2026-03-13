# 🧩 Nonagent Pipeline System

**Traditional Pipeline-Based AI Architecture**

```
User Request → Orchestrator → Fixed Routing → Single Agent → Response
```

---

## 🏗️ Levels

<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:24px;margin:24px 0;">

<div style="background:white;border-radius:12px;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,0.12);">
<div style="background:linear-gradient(135deg,#3b82f6,#2563eb);padding:20px;color:white;font-weight:600;font-size:1.1em;">🔍 Level 1: Knowledge & Retrieval</div>
<div style="padding:20px;">
<strong>RAG-Based Document Retrieval Layer</strong><br><br>
Answers questions by retrieving relevant documents from a vector store and synthesizing answers using RAG.<br><br>
✓ Customer Profile Lookup &nbsp;✓ Identity Verification Status<br>
✓ Email Correspondence Search &nbsp;✓ CRM Agent Notes Search<br>
✓ Policy Document Search (RAG) &nbsp;✓ Cross-Source Search<br>
✓ Audit Trail Logging &nbsp;✓ Output Guardrails
</div>
<div style="padding:12px 20px;background:#f9fafb;border-top:1px solid #e5e7eb;display:flex;justify-content:space-between;align-items:center;">
<span style="background:#d1fae5;color:#065f46;padding:3px 10px;border-radius:20px;font-size:0.8em;font-weight:600;">✅ Production Ready</span>
<span><a href="notebooks/nonagentic/01_level1_knowledge_retrieval.ipynb">Notebook</a> | <a href="docs/nonagentic/level1-knowledge.md">Docs</a></span>
</div>
</div>

<div style="background:white;border-radius:12px;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,0.12);">
<div style="background:linear-gradient(135deg,#10b981,#059669);padding:20px;color:white;font-weight:600;font-size:1.1em;">📊 Level 2: Analytics & Insights</div>
<div style="padding:20px;">
<strong>Data Science Co-Pilot</strong><br><br>
Transforms natural language into actionable insights using SQL, ML, and NLP.<br><br>
✓ K-means Customer Segmentation &nbsp;✓ SQL Analytics & Queries<br>
✓ Fraud Risk Analysis &nbsp;✓ Sentiment Analysis<br>
✓ Text Summarization &nbsp;✓ Customer 360 View<br>
✓ Sales Analytics &nbsp;✓ Support Analytics
</div>
<div style="padding:12px 20px;background:#f9fafb;border-top:1px solid #e5e7eb;display:flex;justify-content:space-between;align-items:center;">
<span style="background:#d1fae5;color:#065f46;padding:3px 10px;border-radius:20px;font-size:0.8em;font-weight:600;">✅ Production Ready</span>
<span><a href="notebooks/nonagentic/02_level2_analytics.ipynb">Notebook</a> | <a href="docs/nonagentic/level2-analytics.md">Docs</a></span>
</div>
</div>

<div style="background:white;border-radius:12px;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,0.12);">
<div style="background:linear-gradient(135deg,#f59e0b,#d97706);padding:20px;color:white;font-weight:600;font-size:1.1em;">⚙️ Level 3: Functional Execution</div>
<div style="padding:20px;">
<strong>Lead Generation & Marketing</strong><br><br>
Executes business actions: lead scoring, enrichment, recommendations, notifications, and campaigns.<br><br>
✓ Lead Scoring &nbsp;✓ Customer Enrichment<br>
✓ Next-Best-Action (NBA) &nbsp;✓ Upsell Recommendations<br>
✓ User-Based Recommendations &nbsp;✓ Collaborative Filtering<br>
✓ Consent-Gated Notifications &nbsp;✓ Identity-Gated Actions
</div>
<div style="padding:12px 20px;background:#f9fafb;border-top:1px solid #e5e7eb;display:flex;justify-content:space-between;align-items:center;">
<span style="background:#d1fae5;color:#065f46;padding:3px 10px;border-radius:20px;font-size:0.8em;font-weight:600;">✅ Production Ready</span>
<span><a href="notebooks/nonagentic/03_level3_functional.ipynb">Notebook</a> | <a href="docs/nonagentic/level3-functional.md">Docs</a></span>
</div>
</div>

<div style="background:white;border-radius:12px;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,0.12);">
<div style="background:linear-gradient(135deg,#8b5cf6,#7c3aed);padding:20px;color:white;font-weight:600;font-size:1.1em;">🎯 Level 4: Strategic Orchestration</div>
<div style="padding:20px;">
<strong>Workflow Orchestration</strong><br><br>
Plans campaigns to achieve business outcomes and self-corrects when KPIs deviate.<br><br>
✓ Campaign Planning & Decomposition &nbsp;✓ Multi-Agent Orchestration<br>
✓ Revenue Impact Analysis &nbsp;✓ Scenario Simulation<br>
✓ Pilot Testing (A/B) &nbsp;✓ Roadmap Prioritization<br>
✓ Self-Reflection Loop &nbsp;✓ Governance Dashboard
</div>
<div style="padding:12px 20px;background:#f9fafb;border-top:1px solid #e5e7eb;display:flex;justify-content:space-between;align-items:center;">
<span style="background:#d1fae5;color:#065f46;padding:3px 10px;border-radius:20px;font-size:0.8em;font-weight:600;">✅ Production Ready</span>
<span><a href="notebooks/nonagentic/04_level4_strategic.ipynb">Notebook</a> | <a href="docs/nonagentic/level4-strategic.md">Docs</a></span>
</div>
</div>

<div style="background:white;border-radius:12px;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,0.12);">
<div style="background:linear-gradient(135deg,#ec4899,#db2777);padding:20px;color:white;font-weight:600;font-size:1.1em;">🎁 Level 5: Recommendation Intelligence</div>
<div style="padding:20px;">
<strong>Personalized Recommendations</strong><br><br>
Generates personalized product suggestions using collaborative filtering and behavior signals.<br><br>
✓ User-Based Recommendations &nbsp;✓ Collaborative Filtering<br>
✓ Behaviour-Based Ranking &nbsp;✓ Hybrid Recommender<br>
✓ Cold Start Handling &nbsp;✓ Cross-User Segment Recs<br>
✓ Offline Evaluation &nbsp;✓ Orchestrator Routing
</div>
<div style="padding:12px 20px;background:#f9fafb;border-top:1px solid #e5e7eb;display:flex;justify-content:space-between;align-items:center;">
<span style="background:#d1fae5;color:#065f46;padding:3px 10px;border-radius:20px;font-size:0.8em;font-weight:600;">✅ Production Ready</span>
<span><a href="notebooks/nonagentic/05_level5_recommendation.ipynb">Notebook</a> | <a href="docs/nonagentic/level5-recommendation.md">Docs</a></span>
</div>
</div>

</div>

---

## 🚀 Key Capabilities

<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:16px;margin:16px 0;">

<div style="padding:20px;background:#f9fafb;border-radius:8px;border-left:4px solid #667eea;">
<strong>🔐 Security & Compliance</strong><br>
Automatic PII redaction, immutable audit trails, consent validation, identity verification gating, and 7-year retention.
</div>

<div style="padding:20px;background:#f9fafb;border-radius:8px;border-left:4px solid #667eea;">
<strong>🤖 Multi-Agent Orchestration</strong><br>
Seamless coordination across all 5 levels. Level 4 decomposes goals and calls Levels 2, 3, and 5 as needed.
</div>

<div style="padding:20px;background:#f9fafb;border-radius:8px;border-left:4px solid #667eea;">
<strong>📊 Data Integration</strong><br>
Unified access to customer DB, emails, CRM notes, policies, sales, social media, and support tickets.
</div>

<div style="padding:20px;background:#f9fafb;border-radius:8px;border-left:4px solid #667eea;">
<strong>🎯 Business Outcomes</strong><br>
ROI projection, scenario simulation, A/B testing, KPI tracking, and self-correcting strategies.
</div>

<div style="padding:20px;background:#f9fafb;border-radius:8px;border-left:4px solid #667eea;">
<strong>🧠 AI/ML Stack</strong><br>
LLMs (Claude), vector search (Chroma/Pinecone), clustering (scikit-learn), NLP (RoBERTa, BART), and collaborative filtering.
</div>

<div style="padding:20px;background:#f9fafb;border-radius:8px;border-left:4px solid #667eea;">
<strong>📈 Observability</strong><br>
Langfuse integration for tracing, monitoring, and debugging. Full audit trail for compliance.
</div>

</div>

---

## 📋 Use Case Summary

| Level | Agent Type | Primary Use Cases | Key Technology |
|-------|-----------|-------------------|----------------|
| **Level 1** | Knowledge Retrieval | Customer lookup, email search, policy Q&A, audit trail | Vector search, RAG, MultiQueryRetriever |
| **Level 2** | Analytics & Insights | Segmentation, SQL analytics, sentiment analysis, Customer 360 | K-means, SQL, NLP, matplotlib |
| **Level 3** | Functional Execution | Lead scoring, enrichment, NBA, notifications, campaigns | Rule-based, collaborative filtering, consent gating |
| **Level 4** | Strategic Orchestration | Campaign planning, ROI projection, scenario simulation, self-correction | LLM decomposition, multi-agent coordination, KPI tracking |
| **Level 5** | Recommendation Intelligence | Personalized recommendations, cold start, offline evaluation | Collaborative filtering, behavior scoring, hybrid ranking |

---

## 🆚 Nonagent vs Agentic

| Feature | Nonagent Pipeline | Agentic System |
|---------|------------------|----------------|
| **Routing** | Fixed rules | Dynamic, context-aware |
| **Agents** | 5 levels (sequential) | 8 agents (collaborative) |
| **Tools** | Direct function calls | MCP protocol servers |
| **Memory** | Session only | Multi-layer (conversation, profile, interaction, observation) |
| **Evaluation** | None | Evaluation agent with replanning |
| **Autonomy** | Low | High |
| **Collaboration** | Sequential | Parallel & coordinated |

---

## 🔄 Pipeline Flow

```
User Request
    ↓
Orchestrator (Fixed Routing)
    ↓
┌─────────────────────────────┐
│   Level 1: Knowledge        │
│   Level 2: Analytics        │
│   Level 3: Functional       │
│   Level 4: Strategic        │
│   Level 5: Recommendation   │
└─────────────────────────────┘
    ↓
Response
```

---

## 🚀 Quick Start

```python
from nonagentic.core.state import new_state
from nonagentic.graph.graph import graph

state = new_state("What is the profile for CUST-001?")
config = {"configurable": {"thread_id": state["request_id"]}}
result = graph.invoke(state, config=config)

print(result["messages"][-1].content)
```

---

## 🧪 Testing

```bash
pytest tests/test_graph.py tests/test_orchestrator.py tests/test_agents.py -v
# Results: ✅ 121 tests passing
```

---

## 📁 Directory Structure

```
nonagentic/
├── agents/              # Level 1-5 agents
├── orchestration/       # Orchestrator & registry
├── graph/               # LangGraph pipeline
├── tools/               # Tool functions
└── core/                # Config, LLM, state
```

---

## 📚 Additional Resources

- [Business Overview](docs/nonagentic/business/overview.md)
- [Developer Guide](docs/nonagentic/developer/guide.md)
- [Architecture Spec](specs/nonagent/architecture.md)
- [Main README](README.md) — Compare with Agentic System

---

**Last Updated:** 2025-01-XX | **Version:** 1.0 | **Status:** Production Ready
