"""Base class for MCP (Model Context Protocol) servers."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Callable


class MCPTool:
    """Represents a tool exposed by an MCP server."""
    def __init__(self, name: str, description: str, func: Callable, schema: dict | None = None):
        self.name = name
        self.description = description
        self.func = func
        self.schema = schema or {}

    def invoke(self, **kwargs) -> Any:
        return self.func(**kwargs)


class MCPServer(ABC):
    """Base class for MCP servers that expose tools to agents."""
    
    def __init__(self, server_id: str, description: str):
        self.server_id = server_id
        self.description = description
        self._tools: dict[str, MCPTool] = {}
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the server and register tools."""
        pass
    
    def register_tool(self, tool: MCPTool) -> None:
        """Register a tool with this server."""
        self._tools[tool.name] = tool
    
    def get_tool(self, name: str) -> MCPTool | None:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def list_tools(self) -> list[MCPTool]:
        """List all available tools."""
        return list(self._tools.values())
    
    def invoke_tool(self, tool_name: str, **kwargs) -> Any:
        """Invoke a tool by name."""
        tool = self.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool {tool_name} not found in server {self.server_id}")
        return tool.invoke(**kwargs)
