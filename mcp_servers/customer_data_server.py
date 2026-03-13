"""Customer Data MCP Server - exposes customer data tools to agents."""

from __future__ import annotations
from mcp_servers import MCPServer, MCPTool
from nonagentic.tools.customer import (
    search_customer_profile,
    get_identity_status,
    get_kyc_status,
)


class CustomerDataServer(MCPServer):
    """MCP server for customer data operations."""

    def __init__(self):
        super().__init__(
            server_id="customer_data",
            description="Customer profiles, identity verification, and KYC data",
        )
        self.initialize()

    def initialize(self) -> None:
        """Register customer data tools."""
        self.register_tool(
            MCPTool(
                name="search_customer_profile",
                description="Search and retrieve customer profile by ID",
                func=search_customer_profile,
                schema={"customer_id": "string"},
            )
        )

        self.register_tool(
            MCPTool(
                name="get_identity_status",
                description="Get customer identity verification status",
                func=get_identity_status,
                schema={"customer_id": "string"},
            )
        )

        self.register_tool(
            MCPTool(
                name="get_kyc_status",
                description="Get customer KYC status",
                func=get_kyc_status,
                schema={"customer_id": "string"},
            )
        )
