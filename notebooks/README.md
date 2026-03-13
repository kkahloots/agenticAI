# Notebooks

This directory contains Jupyter notebooks demonstrating both the nonagent pipeline and agentic AI systems.

## Structure

```
notebooks/
├── nonagent/              # Original pipeline-based system
│   ├── level1_knowledge_agent.ipynb
│   ├── level2_analytics_agent.ipynb
│   ├── level3_functional_agent.ipynb
│   ├── level4_strategic_agent.ipynb
│   ├── level5_recommendation_agent.ipynb
│   ├── utils/            # Helper utilities
│   └── data/             # Sample data
│
├── agentic/              # New agentic AI system
│   └── comparison.ipynb  # Side-by-side comparison
│
├── utils/                # Shared utilities
└── data/                 # Shared data
```

## Quick Start

### Nonagent Notebooks

```bash
cd notebooks/nonagent
jupyter notebook
```

Demonstrates the original 5-level pipeline architecture.

### Agentic Notebooks

```bash
cd notebooks/agentic
jupyter notebook
```

Demonstrates the new agentic AI system with comparison to nonagent.

## Comparison

The `agentic/comparison.ipynb` notebook provides a comprehensive side-by-side comparison:
- Same requests executed by both systems
- Output comparison
- Performance metrics
- Architecture differences

## Dependencies

Install Jupyter and dependencies:

```bash
pip install jupyter ipywidgets matplotlib
```

All notebooks require the main project dependencies from `requirements.txt`.

## Use Cases Covered

### Nonagent Notebooks
1. **Level 1 (Knowledge)**: Customer profiles, KYC status, policy retrieval
2. **Level 2 (Analytics)**: Segmentation, SQL queries, KPIs
3. **Level 3 (Functional)**: Offers, notifications, case creation
4. **Level 4 (Strategic)**: Campaign planning, goal decomposition
5. **Level 5 (Recommendation)**: Product recommendations, collaborative filtering

### Agentic Notebooks
1. **Comparison**: All use cases compared between systems
2. **Future**: Specialized notebooks for each agent type

## Key Differences

| Aspect | Nonagent | Agentic |
|--------|----------|---------|
| **Notebooks** | 5 (one per level) | 1 comparison + future specialized |
| **Architecture** | Pipeline | Collaborative agents |
| **Routing** | Fixed | Dynamic |
| **Memory** | None | 4 types |
| **Evaluation** | None | Continuous |

## Contributing

To add new notebooks:
1. Place nonagent notebooks in `nonagent/`
2. Place agentic notebooks in `agentic/`
3. Update this README
4. Ensure notebooks run end-to-end
