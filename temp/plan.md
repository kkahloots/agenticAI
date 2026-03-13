# Plan: Refactor notebooks/agentic/05_level5_recommendation.ipynb

## Goal
Transform the nonagentic Level 5 recommendation notebook into a full agentic notebook
with two versions (A=deterministic, B=dynamic) for each of the 9 use cases.

## Architecture Understanding
- Nonagentic source: `nonagentic/recommenders/` + `nonagentic/tools/recommender.py`
- Existing agentic infra: `agentic/` (orchestrator, planner, agents, mcp, memory, registry, sql, utils)
- Existing agentic display: `agentic/utils/agentic_display.py` (show_agentic_result, show_agent_plan, etc.)
- Existing agentic API: `agentic/utils/agentic_api.py` (needs new UC methods for recommendation)
- Pattern from: `notebooks/agentic/03_level3_functional.ipynb` (temp chunks show the pattern)

## What Needs to Be Created

### 1. New MCP servers (agentic/mcp/)
- `product_server.py` - wraps product catalog tools
- `feature_server.py` - wraps feature building
- `llm_reasoning_server.py` - LLM-based reasoning (with fallback)
- Update `recommendation_server.py` - add Level 5 recommendation tools

### 2. New agentic agents (agentic/agents/)
- `recommendation_strategy_agent.py` - selects strategy (collaborative/behaviour/hybrid/cold_start)
- `evaluation_agent.py` - already exists, may need updates

### 3. New models (agentic/models/)
- `hybrid_ranker.py` - wraps nonagentic hybrid recommend
- `collaborative_model.py` - wraps collaborative filtering
- `behaviour_model.py` - wraps behaviour scoring
- `content_model.py` - wraps content scoring

### 4. New features (agentic/features/)
- `feature_builder.py` - wraps feature extraction
- `feature_selector.py` - dynamic feature selection

### 5. Update agentic/utils/agentic_api.py
- Add UC1-UC9 recommendation methods

### 6. Update agentic/planner/planner_agent.py
- Add recommendation planning methods

### 7. Update agentic/utils/agentic_display.py
- Add show_model_choice, show_feature_selection

### 8. Create the notebook
- notebooks/agentic/05_level5_recommendation.ipynb
- 9 use cases × 2 versions (A=deterministic, B=dynamic)

## Use Case Mapping
- UC1: User-Based Recommendations → get_segment_recommendations
- UC2: Collaborative Filtering → get_similar_users + _collaborative_scores
- UC3: Behaviour-Based Ranking → get_behaviour_scores + get_content_scores
- UC4: Hybrid Recommender → recommend() full hybrid
- UC5: Cold Start Handling → get_cold_start_recommendations
- UC6: Cross-User Segment → get_segment_recommendations_batch
- UC7: Recommendation Evaluation → evaluate_batch + check_data_leakage
- UC8: Visualisation → plot_* functions
- UC9: Orchestrator Routing → orchestrator intent classification

## Steps
1. [x] Read existing code (done above)
2. [ ] Create plan.md (this file)
3. [ ] Create agentic/mcp/product_server.py
4. [ ] Create agentic/mcp/feature_server.py
5. [ ] Create agentic/mcp/llm_reasoning_server.py
6. [ ] Update agentic/mcp/recommendation_server.py (add Level 5 tools)
7. [ ] Create agentic/agents/recommendation_strategy_agent.py
8. [ ] Create agentic/models/ files
9. [ ] Create agentic/features/ files
10. [ ] Update agentic/planner/planner_agent.py (add recommendation plans)
11. [ ] Update agentic/utils/agentic_api.py (add recommendation UC methods)
12. [ ] Update agentic/utils/agentic_display.py (add show_model_choice, show_feature_selection)
13. [ ] Build notebook in chunks, then merge

## Checkpoints
- CP1: After creating MCP servers → verify imports work
- CP2: After creating agents/models/features → verify they work
- CP3: After updating planner + API → verify UC execution works
- CP4: After building notebook → verify it runs

## Current Status: STEP 3 - Creating MCP servers
