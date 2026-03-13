# 🤖 Agentic AI System

**Autonomous Multi-Agent Architecture for Business Automation**

---

## 🧩 Agents

<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:24px;margin:24px 0;">

<div style="background:white;border-radius:12px;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,0.12);">
<div style="background:linear-gradient(135deg,#667eea,#764ba2);padding:20px;color:white;font-weight:600;font-size:1.1em;">🎯 Orchestrator Agent</div>
<div style="padding:20px;">
<strong>Dynamic Coordination & Routing</strong><br><br>
Analyzes requests and dynamically routes to specialized agents based on context, not fixed rules.<br><br>
✓ Context-Aware Routing &nbsp;✓ Multi-Agent Coordination<br>
✓ Parallel Task Execution &nbsp;✓ Dynamic Agent Selection<br>
✓ Memory-Informed Decisions &nbsp;✓ Workflow Decomposition<br>
✓ Real-Time Adaptation &nbsp;✓ Evaluation Integration
</div>
<div style="padding:12px 20px;background:#f9fafb;border-top:1px solid #e5e7eb;display:flex;justify-content:space-between;align-items:center;">
<span style="background:#d1fae5;color:#065f46;padding:3px 10px;border-radius:20px;font-size:0.8em;font-weight:600;">✅ Production Ready</span>
<span><a href="agents/orchestrator_agent.py">Code</a> | <a href="docs/agentic/developer/guide.md">Docs</a></span>
</div>
</div>

<div style="background:white;border-radius:12px;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,0.12);">
<div style="background:linear-gradient(135deg,#3b82f6,#2563eb);padding:20px;color:white;font-weight:600;font-size:1.1em;">🔍 Knowledge Agent</div>
<div style="padding:20px;">
<strong>Intelligent Information Retrieval</strong><br><br>
Retrieves customer data, policies, and history with memory-enhanced context awareness.<br><br>
✓ Customer Profile Retrieval &nbsp;✓ Identity Verification<br>
✓ Email & CRM Search &nbsp;✓ Policy Document RAG<br>
✓ Cross-Source Integration &nbsp;✓ Memory-Enhanced Context<br>
✓ Audit Trail Logging &nbsp;✓ MCP Tool Integration
</div>
<div style="padding:12px 20px;background:#f9fafb;border-top:1px solid #e5e7eb;display:flex;justify-content:space-between;align-items:center;">
<span style="background:#d1fae5;color:#065f46;padding:3px 10px;border-radius:20px;font-size:0.8em;font-weight:600;">✅ Production Ready</span>
<span><a href="agents/knowledge_agent.py">Code</a> | <a href="mcp_servers/customer_data_server.py">MCP Server</a></span>
</div>
</div>

<div style="background:white;border-radius:12px;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,0.12);">
<div style="background:linear-gradient(135deg,#10b981,#059669);padding:20px;color:white;font-weight:600;font-size:1.1em;">📊 Analytics Agent</div>
<div style="padding:20px;">
<strong>Advanced Data Intelligence</strong><br><br>
Performs analytics with observation recording and insight generation for continuous learning.<br><br>
✓ Customer Segmentation &nbsp;✓ SQL Analytics<br>
✓ Fraud Risk Analysis &nbsp;✓ Sentiment Analysis<br>
✓ Customer 360 View &nbsp;✓ Observation Recording<br>
✓ Insight Generation &nbsp;✓ Pattern Recognition
</div>
<div style="padding:12px 20px;background:#f9fafb;border-top:1px solid #e5e7eb;display:flex;justify-content:space-between;align-items:center;">
<span style="background:#d1fae5;color:#065f46;padding:3px 10px;border-radius:20px;font-size:0.8em;font-weight:600;">✅ Production Ready</span>
<span><a href="agents/analytics_agent.py">Code</a> | <a href="mcp_servers/analytics_server.py">MCP Server</a></span>
</div>
</div>

<div style="background:white;border-radius:12px;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,0.12);">
<div style="background:linear-gradient(135deg,#ec4899,#db2777);padding:20px;color:white;font-weight:600;font-size:1.1em;">🎁 Recommendation Agent</div>
<div style="padding:20px;">
<strong>Personalized Intelligence</strong><br><br>
Generates personalized recommendations using collaborative filtering and behavioral signals.<br><br>
<strong>9 Use Cases:</strong><br>
✓ UC1: User-Based Recommendations (Segment peer behaviour)<br>
✓ UC2: Collaborative Filtering (User-user cosine similarity)<br>
✓ UC3: Behaviour-Based Ranking (Clicks, views, purchases)<br>
✓ UC4: Hybrid Recommender (Weighted combination of all signals)<br>
✓ UC5: Cold Start Handling (Segment/popularity fallback)<br>
✓ UC6: Cross-User Segment (Batch recommendations for segment)<br>
✓ UC7: Recommendation Evaluation (Offline metrics + leakage detection)<br>
✓ UC8: Visualisation (Charts and summaries)<br>
✓ UC9: Orchestrator Routing (Dynamic intent classification)
</div>
<div style="padding:12px 20px;background:#f9fafb;border-top:1px solid #e5e7eb;display:flex;justify-content:space-between;align-items:center;">
<span style="background:#d1fae5;color:#065f46;padding:3px 10px;border-radius:20px;font-size:0.8em;font-weight:600;">✅ Production Ready</span>
<span><a href="agents/recommendation_agent.py">Code</a> | <a href="mcp_servers/recommendation_server.py">MCP Server</a> | <a href="notebooks/agentic/05_level5_recommendation.ipynb">Demo</a></span>
</div>
</div>

<div style="background:white;border-radius:12px;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,0.12);">
<div style="background:linear-gradient(135deg,#f59e0b,#d97706);padding:20px;color:white;font-weight:600;font-size:1.1em;">⚙️ Action Agent</div>
<div style="padding:20px;">
<strong>Autonomous Execution</strong><br><br>
Executes business actions with consent validation and identity verification.<br><br>
✓ Lead Scoring &nbsp;✓ Customer Enrichment<br>
✓ Next-Best-Action &nbsp;✓ Notification Delivery<br>
✓ Campaign Execution &nbsp;✓ Consent Validation<br>
✓ Identity Gating &nbsp;✓ Action Logging
</div>
<div style="padding:12px 20px;background:#f9fafb;border-top:1px solid #e5e7eb;display:flex;justify-content:space-between;align-items:center;">
<span style="background:#d1fae5;color:#065f46;padding:3px 10px;border-radius:20px;font-size:0.8em;font-weight:600;">✅ Production Ready</span>
<span><a href="agents/other_agents.py">Code</a> | <a href="mcp_servers/crm_server.py">MCP Server</a></span>
</div>
</div>

<div style="background:white;border-radius:12px;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,0.12);">
<div style="background:linear-gradient(135deg,#8b5cf6,#7c3aed);padding:20px;color:white;font-weight:600;font-size:1.1em;">🗺️ Workflow Agent</div>
<div style="padding:20px;">
<strong>Strategic Orchestration</strong><br><br>
Plans and executes complex multi-step workflows with dynamic coordination.<br><br>
✓ Campaign Planning &nbsp;✓ Multi-Agent Coordination<br>
✓ Workflow Decomposition &nbsp;✓ Scenario Simulation<br>
✓ A/B Testing &nbsp;✓ KPI Tracking<br>
✓ Dynamic Replanning &nbsp;✓ ROI Analysis
</div>
<div style="padding:12px 20px;background:#f9fafb;border-top:1px solid #e5e7eb;display:flex;justify-content:space-between;align-items:center;">
<span style="background:#d1fae5;color:#065f46;padding:3px 10px;border-radius:20px;font-size:0.8em;font-weight:600;">✅ Production Ready</span>
<span><a href="agents/other_agents.py">Code</a> | <a href="graphs/agent_workflow_graph.py">Graph</a></span>
</div>
</div>

<div style="background:white;border-radius:12px;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,0.12);">
<div style="background:linear-gradient(135deg,#06b6d4,#0891b2);padding:20px;color:white;font-weight:600;font-size:1.1em;">🔬 Evaluation Agent</div>
<div style="padding:20px;">
<strong>Quality Assurance & Learning</strong><br><br>
Evaluates responses and triggers replanning when quality thresholds aren't met.<br><br>
✓ Response Quality Assessment &nbsp;✓ Completeness Validation<br>
✓ Accuracy Verification &nbsp;✓ Replan Triggering<br>
✓ Observation Recording &nbsp;✓ Continuous Learning<br>
✓ Feedback Loops &nbsp;✓ Quality Metrics
</div>
<div style="padding:12px 20px;background:#f9fafb;border-top:1px solid #e5e7eb;display:flex;justify-content:space-between;align-items:center;">
<span style="background:#d1fae5;color:#065f46;padding:3px 10px;border-radius:20px;font-size:0.8em;font-weight:600;">✅ Production Ready</span>
<span><a href="agents/other_agents.py">Code</a> | <a href="graphs/agent_workflow_graph.py">Graph</a></span>
</div>
</div>

<div style="background:white;border-radius:12px;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,0.12);">
<div style="background:linear-gradient(135deg,#84cc16,#65a30d);padding:20px;color:white;font-weight:600;font-size:1.1em;">🧠 Memory Agent</div>
<div style="padding:20px;">
<strong>Context & Learning Management</strong><br><br>
Manages multi-layer memory for conversation, profiles, interactions, and observations.<br><br>
✓ Conversation Memory &nbsp;✓ Profile Memory<br>
✓ Interaction History &nbsp;✓ Observation Storage<br>
✓ Context Retrieval &nbsp;✓ Memory Synthesis<br>
✓ Pattern Learning &nbsp;✓ Long-Term Storage
</div>
<div style="padding:12px 20px;background:#f9fafb;border-top:1px solid #e5e7eb;display:flex;justify-content:space-between;align-items:center;">
<span style="background:#d1fae5;color:#065f46;padding:3px 10px;border-radius:20px;font-size:0.8em;font-weight:600;">✅ Production Ready</span>
<span><a href="agents/other_agents.py">Code</a> | <a href="memory/memory_manager.py">Memory Manager</a></span>
</div>
</div>

<div style="background:white;border-radius:12px;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,0.12);">
<div style="background:linear-gradient(135deg,#ef4444,#dc2626);padding:20px;color:white;font-weight:600;font-size:1.1em;">🛡️ Guardrails Agent</div>
<div style="padding:20px;">
<strong>Safety & Compliance</strong><br><br>
Ensures all outputs meet security, compliance, and quality standards.<br><br>
✓ PII Redaction &nbsp;✓ Content Filtering<br>
✓ Compliance Validation &nbsp;✓ Output Sanitization<br>
✓ Risk Assessment &nbsp;✓ Policy Enforcement<br>
✓ Audit Trail &nbsp;✓ Real-Time Monitoring
</div>
<div style="padding:12px 20px;background:#f9fafb;border-top:1px solid #e5e7eb;display:flex;justify-content:space-between;align-items:center;">
<span style="background:#d1fae5;color:#065f46;padding:3px 10px;border-radius:20px;font-size:0.8em;font-weight:600;">✅ Production Ready</span>
<span><a href="agents/other_agents.py">Code</a></span>
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
<strong>🤖 Autonomous Collaboration</strong><br>
Dynamic agent selection, parallel execution, intelligent coordination, and self-correction through evaluation loops.
</div>

<div style="padding:20px;background:#f9fafb;border-radius:8px;border-left:4px solid #667eea;">
<strong>📊 MCP Tool Servers</strong><br>
Standardized tool abstraction using Model Context Protocol for customer data, analytics, recommendations, CRM, and product catalog.
</div>

<div style="padding:20px;background:#f9fafb;border-radius:8px;border-left:4px solid #667eea;">
<strong>🧠 Multi-Layer Memory</strong><br>
Conversation memory, profile memory, interaction history, and observation storage for continuous learning.
</div>

<div style="padding:20px;background:#f9fafb;border-radius:8px;border-left:4px solid #667eea;">
<strong>🎯 Evaluation & Replanning</strong><br>
Automatic quality assessment with intelligent replanning when responses don't meet thresholds.
</div>

<div style="padding:20px;background:#f9fafb;border-radius:8px;border-left:4px solid #667eea;">
<strong>📈 Observability</strong><br>
Langfuse integration for tracing, monitoring, and debugging. Full audit trail for compliance.
</div>

</div>

---

## 📋 Agent Comparison

| Agent | Type | Primary Capabilities | Key Technology |
|-------|------|---------------------|----------------|
| **Orchestrator** | Coordination | Dynamic routing, multi-agent coordination, workflow decomposition | LangGraph, memory integration |
| **Knowledge** | Retrieval | Customer lookup, policy Q&A, cross-source search | MCP, RAG, vector search |
| **Analytics** | Intelligence | Segmentation, SQL analytics, sentiment analysis, insights | MCP, K-means, NLP |
| **Recommendation** | Personalization | Collaborative filtering, behavior ranking, cold start | MCP, hybrid recommender, memory |
| **Action** | Execution | Lead scoring, enrichment, notifications, campaigns | MCP, consent gating, identity verification |
| **Workflow** | Orchestration | Campaign planning, scenario simulation, A/B testing | Multi-agent coordination, KPI tracking |
| **Evaluation** | Quality | Response assessment, replanning, continuous learning | Quality metrics, feedback loops |
| **Memory** | Context | Multi-layer memory, pattern learning, context synthesis | Memory manager, observation storage |
| **Guardrails** | Safety | PII redaction, compliance validation, real-time monitoring | Content filtering, policy enforcement |

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

## 🔄 Architecture Flow

```
User Request
    ↓
Orchestrator Agent (Dynamic Routing)
    ↓
┌───────────────────────────────────┐
│   Specialized Agents (Parallel)   │
│   - Knowledge  - Analytics        │
│   - Recommendation  - Action      │
│   - Workflow                      │
└───────────────────────────────────┘
    ↓
MCP Tool Servers → Memory Layer
    ↓
Evaluation Agent → Replan if needed
    ↓
Response
```

---

## 📚 Additional Resources

- [Business Overview](docs/agentic/business/overview.md)
- [Developer Guide](docs/agentic/developer/guide.md)
- [Architecture Spec](specs/agentic/architecture.md)
- [Comparison Notebook](notebooks/agentic/comparison.ipynb)
- [Main README](README.md)

---

**Last Updated:** 2026-03-12 | **Version:** 1.0 | **Status:** Production Ready
