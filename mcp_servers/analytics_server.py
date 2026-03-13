"""Analytics MCP Server - exposes analytics and segmentation tools."""

from __future__ import annotations
from mcp_servers import MCPServer, MCPTool
from nonagentic.tools.analytics import run_sql_query, generate_segment


class AnalyticsServer(MCPServer):
    """MCP server for analytics operations."""

    def __init__(self):
        super().__init__(
            server_id="analytics",
            description="SQL queries, segmentation, and analytics",
        )
        self.initialize()

    def initialize(self) -> None:
        """Register analytics tools."""
        self.register_tool(
            MCPTool(
                name="run_sql_query",
                description="Execute SQL query on customer database",
                func=run_sql_query,
                schema={"sql": "string", "max_rows": "integer"},
            )
        )

        self.register_tool(
            MCPTool(
                name="generate_segment",
                description="Generate customer segments using rules or ML",
                func=generate_segment,
                schema={"filters": "object", "algorithm": "string"},
            )
        )
