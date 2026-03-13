"""Recommendation Execution Graph - multi-agent workflow for Level 5 recommendations.

Flow:
  orchestrator → planner → recommendation_strategy_agent → recommendation_agent
              → analytics_agent → compliance_agent → evaluation_agent
"""

from typing import Optional


class RecommendationExecutionGraph:
    """Executes multi-agent recommendation workflows.

    Nodes:
        orchestrator
        planner
        recommendation_strategy_agent
        recommendation_agent
        analytics_agent
        compliance_agent
        evaluation_agent
    """

    # UC → agent path mapping
    UC_PATHS = {
        "user_based_recommendations":       ["recommendation_agent", "evaluation_agent"],
        "collaborative_filtering":          ["recommendation_agent", "evaluation_agent"],
        "behaviour_based_ranking":          ["recommendation_strategy_agent", "recommendation_agent", "evaluation_agent"],
        "hybrid_recommender":               ["recommendation_strategy_agent", "recommendation_agent", "evaluation_agent"],
        "cold_start_handling":              ["recommendation_agent", "evaluation_agent"],
        "cross_user_segment_recommendations": ["analytics_agent", "recommendation_agent", "evaluation_agent"],
        "recommendation_evaluation":        ["analytics_agent", "evaluation_agent"],
        "recommendation_visualisation":     ["analytics_agent", "recommendation_agent", "evaluation_agent"],
        "orchestrator_routing":             ["recommendation_strategy_agent", "evaluation_agent"],
    }

    def get_path(self, intent: str) -> list[str]:
        """Return the agent execution path for a given intent."""
        return self.UC_PATHS.get(intent, ["recommendation_agent", "evaluation_agent"])

    def execute(self, intent: str, agents: dict, tasks: list[dict],
                request_id: str) -> dict:
        """Execute the graph for a given intent.

        Args:
            intent: UC intent string
            agents: dict of agent_name → agent instance
            tasks: list of task dicts (one per subtask)
            request_id: unique request identifier

        Returns:
            dict with results, agent_path, and final_result
        """
        path = self.get_path(intent)
        results = []

        for i, agent_name in enumerate(path):
            agent = agents.get(agent_name)
            if agent is None:
                results.append({"error": f"agent_not_found: {agent_name}"})
                continue

            task = tasks[i] if i < len(tasks) else {}

            if agent_name == "evaluation_agent":
                result = agent.evaluate(
                    results[-1] if results else {},
                    "recommendation_list",
                    request_id,
                )
            else:
                result = agent.execute(task, request_id)

            results.append(result)

        return {
            "agent_path": path,
            "results": results,
            "final_result": results[-1] if results else {},
        }


def create_recommendation_graph() -> RecommendationExecutionGraph:
    """Create recommendation execution graph instance."""
    return RecommendationExecutionGraph()
