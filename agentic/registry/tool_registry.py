"""Tool Registry for dynamic tool discovery and execution."""

from typing import Any, Callable, Optional
from dataclasses import dataclass, field


@dataclass
class ToolMetadata:
    """Metadata for a registered tool."""
    tool_name: str
    category: str
    description: str
    input_schema: dict
    output_schema: dict
    risk_level: str = "low"           # low, medium, high
    requires_consent: bool = False
    requires_identity_check: bool = False
    supports_simulation: bool = False
    supports_batch: bool = False
    supports_cold_start: bool = False
    supports_explanations: bool = False
    model_type: str = ""              # collaborative, behaviour, content, hybrid, popularity, segment
    requires_sql: bool = False
    requires_llm: bool = False
    handler: Optional[Callable] = None


class ToolRegistry:
    """Registry for dynamic tool discovery and execution."""

    def __init__(self):
        self._tools: dict[str, ToolMetadata] = {}
        self._categories: dict[str, list[str]] = {}

    def register(self, metadata: ToolMetadata):
        """Register a tool."""
        self._tools[metadata.tool_name] = metadata
        if metadata.category not in self._categories:
            self._categories[metadata.category] = []
        self._categories[metadata.category].append(metadata.tool_name)

    def list_tools(self) -> list[str]:
        """List all registered tool names."""
        return list(self._tools.keys())

    def list_tools_by_category(self, category: str) -> list[str]:
        """List tools in a specific category."""
        return self._categories.get(category, [])

    def get_tool_metadata(self, tool_name: str) -> Optional[ToolMetadata]:
        """Get metadata for a tool."""
        return self._tools.get(tool_name)

    def find_tools_for_action(self, action_name: str) -> list[str]:
        """Find tools that match an action description."""
        matches = []
        action_lower = action_name.lower()
        for tool_name, meta in self._tools.items():
            if action_lower in tool_name.lower() or action_lower in meta.description.lower():
                matches.append(tool_name)
        return matches

    def find_tools_for_model_type(self, model_type: str) -> list[str]:
        """Find tools that use a specific model type."""
        return [
            name for name, meta in self._tools.items()
            if meta.model_type == model_type
        ]

    def execute_tool(self, tool_name: str, args: dict) -> dict:
        """Execute a tool with given arguments."""
        meta = self._tools.get(tool_name)
        if not meta:
            return {"error": "tool_not_found", "tool_name": tool_name}
        if not meta.handler:
            return {"error": "no_handler", "tool_name": tool_name}

        try:
            result = meta.handler(**args)
            return {
                "result": result,
                "tool_name": tool_name,
                "execution_status": "success",
                "audit": {"tool": tool_name, "args": args}
            }
        except Exception as e:
            return {
                "error": str(e),
                "tool_name": tool_name,
                "execution_status": "failed",
                "audit": {"tool": tool_name, "args": args}
            }


# Global registry instance
_registry = ToolRegistry()


def get_registry() -> ToolRegistry:
    """Get the global tool registry."""
    return _registry
