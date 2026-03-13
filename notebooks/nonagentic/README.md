# Nonagent Pipeline Notebooks

These notebooks demonstrate the original pipeline-based system with 5 levels of agents.

## Notebooks

2. **01_level1_knowledge_retrieval.ipynb** - Knowledge retrieval and information synthesis
3. **02_level2_analytics.ipynb** - Data analysis and segmentation
3. **level3_functional_agent.ipynb** - Action execution and workflows
4. **level4_strategic_agent.ipynb** - Strategic planning and campaigns
5. **level5_recommendation_agent.ipynb** - Product recommendations

## Running the Notebooks

```bash
cd notebooks/nonagent
jupyter notebook
```

## Dependencies

- All notebooks use utilities from `utils/` directory
- Data files are in `data/` directory
- Requires the nonagent system in `src/`

## Architecture

These notebooks demonstrate the **nonagent pipeline** architecture:
- Fixed routing based on intent classification
- Sequential execution through levels
- Direct function calls to tools
- No memory layer (except LangGraph checkpointer)
- No evaluation or replanning

For comparison with the agentic system, see `../agentic/comparison.ipynb`
