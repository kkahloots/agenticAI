"""Orchestrator Agent - routes requests and coordinates agents."""

import uuid
from typing import Optional
from agentic.planner.planner_agent import create_planner
from agentic.agents.functional_agent import create_functional_agent
from agentic.agents.recommendation_agent import create_recommendation_agent
from agentic.agents.recommendation_strategy_agent import create_recommendation_strategy_agent
from agentic.agents.analytics_agent import create_analytics_agent
from agentic.agents.compliance_agent import create_compliance_agent
from agentic.agents.evaluation_agent import create_evaluation_agent
from agentic.graphs.recommendation_execution_graph import create_recommendation_graph
from agentic.memory.memory_manager import get_memory


class OrchestratorAgent:
    """Orchestrates agent execution."""

    def __init__(self):
        self.planner = create_planner()
        self.functional_agent = create_functional_agent()
        self.recommendation_agent = create_recommendation_agent()
        self.recommendation_strategy_agent = create_recommendation_strategy_agent()
        self.analytics_agent = create_analytics_agent()
        self.compliance_agent = create_compliance_agent()
        self.evaluation_agent = create_evaluation_agent()
        self.rec_graph = create_recommendation_graph()
        self.memory = get_memory()

    def execute(self, request: str, context: Optional[dict] = None,
                mode: str = "deterministic") -> dict:
        """Execute request with specified mode."""
        request_id = str(uuid.uuid4())

        if mode == "deterministic":
            return self._execute_deterministic(request, context, request_id)
        return self._execute_dynamic(request, context, request_id)

    # ── Deterministic ─────────────────────────────────────────────────────────

    def _execute_deterministic(self, request: str, context: Optional[dict],
                                request_id: str) -> dict:
        """Execute with fixed tool paths (baseline)."""
        plan = self.planner.plan(request, context)
        self.memory.record_plan(request_id, plan)

        results = []
        for subtask in plan["subtasks"]:
            agent = self._get_agent(subtask["agent"])
            task = {"action": subtask["action"], **(context or {})}
            results.append(agent.execute(task, request_id))

        final_result = results[-1] if results else {}
        evaluation = self.evaluation_agent.evaluate(
            final_result, plan["expected_output_type"], request_id
        )

        return {
            "request_id": request_id,
            "mode": "deterministic",
            "plan": plan,
            "results": results,
            "final_result": final_result,
            "evaluation": evaluation,
            "agent_path": [s["agent"] for s in plan["subtasks"]],
            "memory_entries": len(self.memory.get_request_history(request_id)),
        }

    # ── Dynamic ───────────────────────────────────────────────────────────────

    def _execute_dynamic(self, request: str, context: Optional[dict],
                          request_id: str) -> dict:
        """Execute with dynamic tool discovery, graph routing, and planning."""
        plan = self.planner.plan(request, context)
        self.memory.record_plan(request_id, plan)

        intent = plan.get("intent", "")

        # Build agent dict for graph
        agents = {
            "orchestrator":                    self.functional_agent,
            "functional_agent":                self.functional_agent,
            "recommendation_agent":            self.recommendation_agent,
            "recommendation_strategy_agent":   self.recommendation_strategy_agent,
            "analytics_agent":                 self.analytics_agent,
            "compliance_agent":                self.compliance_agent,
            "evaluation_agent":                self.evaluation_agent,
        }

        # Build task list from subtasks
        tasks = [
            {"action": s["action"], "candidate_tools": s.get("candidate_tools", []),
             **(context or {})}
            for s in plan["subtasks"]
        ]

        # Execute via graph
        graph_result = self.rec_graph.execute(intent, agents, tasks, request_id)

        # Record observations
        for agent_name in graph_result["agent_path"]:
            self.memory.record_observation(request_id, f"Completed step via {agent_name}")

        final_result = graph_result["final_result"]
        evaluation = self.evaluation_agent.evaluate(
            final_result, plan["expected_output_type"], request_id
        )

        if evaluation.get("needs_replan"):
            self.memory.record_observation(request_id, "Replanning triggered due to low confidence")

        return {
            "request_id": request_id,
            "mode": "dynamic",
            "plan": plan,
            "results": graph_result["results"],
            "final_result": final_result,
            "evaluation": evaluation,
            "agent_path": graph_result["agent_path"],
            "memory_entries": len(self.memory.get_request_history(request_id)),
            "tool_selections": [s.get("candidate_tools", []) for s in plan["subtasks"]],
        }

    def _get_agent(self, agent_name: str):
        """Get agent by name."""
        return {
            "functional_agent":              self.functional_agent,
            "recommendation_agent":          self.recommendation_agent,
            "recommendation_strategy_agent": self.recommendation_strategy_agent,
            "analytics_agent":               self.analytics_agent,
            "compliance_agent":              self.compliance_agent,
            "evaluation_agent":              self.evaluation_agent,
            # orchestrator routes to functional_agent as fallback
            "orchestrator":                  self.functional_agent,
        }.get(agent_name, self.functional_agent)


def create_orchestrator() -> OrchestratorAgent:
    """Create orchestrator instance."""
    return OrchestratorAgent()
