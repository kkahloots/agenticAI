"""Recommendation MCP Server - exposes recommendation engine tools."""

from __future__ import annotations
from mcp_servers import MCPServer, MCPTool
from nonagentic.tools.recommender import recommend
from nonagentic.tools.functional import recommend_offer


class RecommendationServer(MCPServer):
    """MCP server for recommendation operations."""

    def __init__(self):
        super().__init__(
            server_id="recommendation",
            description="Product recommendations and offer suggestions",
        )
        self.initialize()

    def initialize(self) -> None:
        """Register recommendation tools."""
        self.register_tool(
            MCPTool(
                name="recommend_products",
                description="Generate personalized product recommendations",
                func=recommend,
                schema={"customer_id": "string", "top_k": "integer"},
            )
        )

        self.register_tool(
            MCPTool(
                name="recommend_offer",
                description="Recommend next best offer for customer",
                func=recommend_offer,
                schema={"customer_id": "string"},
            )
        )
