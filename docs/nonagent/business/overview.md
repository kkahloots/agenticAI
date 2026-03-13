# 🧩 Agentic AI System – Business Overview

### Purpose

This multi‑agent system helps your organisation move from simple information retrieval to autonomous business growth. It leverages agentic AI to manage customer data, extract insights and execute campaigns with minimal human intervention.

### Key Benefits

- **Efficiency Gains**: Automating repetitive tasks frees employees to focus on strategy. AI agents replace manual processes — KYC lookups, segmentation queries, and campaign scheduling — letting staff work on higher-value activities.
- **Better Decisions**: Predictive models identify late-paying customers and high-value segments, enabling proactive collections and targeted offers.
- **Unified Customer View**: By integrating the customer database, communication logs, CRM notes, and policy documents, the system delivers a single view of the customer and improves satisfaction.

### System Levels

1. **Knowledge Assistant (Level 1)**: Answers questions, retrieves customer profiles, checks KYC status, searches emails, CRM notes, and policy documents.
   - **Demo**: `notebooks/level1_knowledge_agent.ipynb`
   - **Status**: ✅ Fully implemented

2. **Analytics & Pattern Discovery (Level 2)**: Performs data segmentation using K-means clustering, runs SQL queries, analyzes sentiment from social media, summarizes text, and generates visualizations.
   - **Demo**: `notebooks/nonagent/02_level2_analytics.ipynb`
   - **Status**: ✅ Fully implemented
   - **Features**:
     - K-means customer segmentation (scikit-learn)
     - Text-to-SQL query generation (LangChain)
     - Sentiment analysis (RoBERTa)
     - Text summarization (BART)
     - Customer 360 view (CRM + Sales + Social + Support)
     - Automated chart generation (matplotlib)

3. **Functional Agent (Level 3)**: Executes lead generation, customer enrichment, next-best-action recommendations, consent-gated notifications, identity-gated actions, bulk campaign targeting, and payment risk interventions.
   - **Demo**: `notebooks/level3_functional_agent.ipynb`
   - **Status**: ✅ Fully implemented
   - **Features**:
     - Lead scoring — multi-factor prospect ranking (engagement, fraud_score, lifetime_value, recency)
     - Customer enrichment — credit bureau, business registry, location API simulation
     - Next-Best-Action (NBA) recommendation — cross-sell rules + segment scoring
     - **Upsell recommendations** — higher-tier products based on purchase categories
     - **User-based recommendations** — segment peer behavior analysis
     - **Collaborative filtering** — cross-customer similarity recommendations
     - Consent-gated notifications (email/SMS/push)
     - Identity gate — blocks actions on expired identity verification, opens remediation case
     - Bulk campaign targeting — segment-level execution plan with approval gates
     - Payment risk intervention — identifies and contacts at-risk customers

4. **Strategic Agent (Level 4)**: Plans campaigns to achieve business outcomes, such as increasing card adoption or reducing churn, and self-corrects when KPIs deviate.
   - **Demo**: `notebooks/level4_strategic_agent.ipynb`
   - **Status**: ✅ Fully implemented

5. **Recommendation Intelligence Agent (Level 5)**: Generates personalised product recommendations using collaborative filtering, behaviour signals, content similarity, and popularity — with cold-start handling and offline evaluation.
   - **Demo**: `notebooks/level5_recommendation_agent.ipynb`
   - **Status**: ✅ Fully implemented
   - **Features**:
     - Collaborative filtering — user-user cosine similarity
     - Behaviour-based ranking — recency-weighted clicks, views, purchases
     - Content similarity — category overlap matching
     - Hybrid ranking — weighted formula (0.4 + 0.3 + 0.2 + 0.1)
     - Cold start handling — segment-level and global popular item fallback
     - Cross-user segment recommendations — aggregate recs for a full segment
     - Offline evaluation — precision@K, recall@K, MAP, NDCG
     - Orchestrator routing — natural language → recommendation intent
   - **Features**:
     - Goal decomposition — LLM breaks high-level objectives into 2-4 sub-tasks
     - Multi-agent orchestration — coordinates Level 2 segmentation + Level 3 campaign scheduling
     - Revenue impact analysis — projects conversions, revenue, and ROI from campaign parameters
     - Scenario simulation — compares strategy options and recommends highest-ROI non-high-risk path
     - Pilot testing — A/B split with compliance gate (pilot ≤ 50% enforced)
     - Roadmap prioritization — ranks initiatives by ROI score (revenue / effort weight)
     - Self-reflection loop — KPI deviation above threshold triggers automatic goal re-decomposition
     - Governance dashboard — immutable audit trail + Langfuse observability metrics

### Safeguards

- Human approval is required for high-risk or high-reach decisions (> 100 customers or > 1,000 campaign reach).
- Sensitive data (e.g. personal identifiers) is automatically redacted from outputs by the guardrail layer.
- The system complies with identity verification requirements and respects customer consent preferences unconditionally.
- Every action is logged to an immutable audit trail — retained for 7 years.

### Return on Investment

Implementing agentic AI delivers measurable results across the organisation:

- **Analyst time saved**: Automating KYC lookups and segmentation queries frees an estimated 2–4 hours/day per team.
- **Revenue uplift**: Personalised upsell campaigns driven by Level-3 targeting typically improve conversion rates by 15–25% vs. batch campaigns.
- **Risk reduction**: Proactive payment-delay detection reduces collections cost by intervening 30+ days earlier.
- **Compliance**: Automated identity verification expiry tracking eliminates manual monitoring and reduces regulatory exposure.

### Next Steps

Review the detailed specifications to understand how each agent functions. The system is designed to scale: start with Level 1 and Level 2 to gain quick insights, then add Levels 3 and 4 for end-to-end automation.

**Interactive Demos**:
- **Level 1**: `notebooks/level1_knowledge_agent.ipynb` - Knowledge retrieval and search
- **Level 2**: `notebooks/nonagent/02_level2_analytics.ipynb` - Analytics, ML, and NLP
- **Level 3**: `notebooks/level3_functional_agent.ipynb` - Lead generation and targeted marketing
- **Level 4**: `notebooks/level4_strategic_agent.ipynb` - Strategic orchestration and business outcomes
- **Level 5**: `notebooks/level5_recommendation_agent.ipynb` - Personalised product recommendations

**Quick Tests**:
```bash
python test_level2.py  # Test Level 2 analytics features
```
