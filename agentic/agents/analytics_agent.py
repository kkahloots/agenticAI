"""Analytics Agent - handles SQL generation, queries, and analytics."""

from typing import Optional
from agentic.mcp import analytics_server
from agentic.sql.sql_generator import create_sql_generator
from agentic.registry.tool_registry import get_registry
from agentic.memory.memory_manager import get_memory


class AnalyticsAgent:
    """Handles analytics and SQL generation."""
    
    def __init__(self):
        self.registry = get_registry()
        self.memory = get_memory()
        self.sql_generator = create_sql_generator()
    
    def execute(self, task: dict, request_id: str) -> dict:
        """Execute analytics task."""
        action = task.get("action", "")
        
        if "sql" in action.lower() or "query" in action.lower():
            return self._run_query(task, request_id)
        elif "segment" in action.lower():
            return self._generate_segment(task, request_id)
        elif "campaign" in action.lower() and ("performance" in action.lower() or "result" in action.lower()):
            return self._campaign_performance(task, request_id)
        elif "return" in action.lower() and "risk" in action.lower():
            return self._identify_return_risk(task, request_id)
        else:
            return {"error": "unknown_action", "action": action}
    
    def _run_query(self, task: dict, request_id: str) -> dict:
        """Run SQL query."""
        query = task.get("query")
        intent = task.get("intent", "")
        
        # If no query provided, generate from intent
        if not query and intent:
            sql_result = self.sql_generator.generate(intent, context=task.get("context"))
            if sql_result.get("error"):
                return {"error": "sql_generation_failed", "details": sql_result}
            query = sql_result["query"]
            self.memory.record_sql_generation(request_id, query, intent)
        
        if not query:
            return {"error": "missing_query"}
        
        # Validate query
        validation = self.sql_generator.validate(query)
        if not validation.get("valid"):
            return {"error": "invalid_query", "details": validation}
        
        result = analytics_server.run_sql_query(query, safe_mode=True)
        self.memory.record_tool_usage(request_id, "run_sql_query", {"query": query}, result)
        return result
    
    def _generate_segment(self, task: dict, request_id: str) -> dict:
        """Generate customer segment."""
        criteria = task.get("criteria", {})
        result = analytics_server.generate_segment(criteria)
        self.memory.record_tool_usage(request_id, "generate_segment", task, result)
        return result
    
    def _campaign_performance(self, task: dict, request_id: str) -> dict:
        """Get campaign performance summary."""
        result = analytics_server.campaign_performance_summary()
        self.memory.record_tool_usage(request_id, "campaign_performance_summary", task, result)
        return result
    
    def _identify_return_risk(self, task: dict, request_id: str) -> dict:
        """Identify high return risk customers."""
        threshold = task.get("threshold", 0.7)
        result = analytics_server.identify_high_return_risk(threshold=threshold)
        self.memory.record_tool_usage(request_id, "identify_high_return_risk", task, result)
        return result


def create_analytics_agent() -> AnalyticsAgent:
    """Create analytics agent instance."""
    return AnalyticsAgent()
