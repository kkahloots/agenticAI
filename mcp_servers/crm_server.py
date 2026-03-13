"""CRM MCP Server - exposes CRM and action tools."""

from __future__ import annotations
from mcp_servers import MCPServer, MCPTool
from nonagentic.tools.functional import draft_email, send_notification, create_case
from nonagentic.tools.strategic import schedule_campaign


class CRMServer(MCPServer):
    """MCP server for CRM operations."""

    def __init__(self):
        super().__init__(
            server_id="crm", description="CRM operations, notifications, and campaigns"
        )
        self.initialize()

    def initialize(self) -> None:
        """Register CRM tools."""
        self.register_tool(
            MCPTool(
                name="draft_email",
                description="Draft email from template",
                func=draft_email,
                schema={
                    "customer_id": "string",
                    "template_id": "string",
                    "variables": "object",
                },
            )
        )

        self.register_tool(
            MCPTool(
                name="send_notification",
                description="Send notification to customer",
                func=send_notification,
                schema={
                    "customer_id": "string",
                    "channel": "string",
                    "payload": "object",
                },
            )
        )

        self.register_tool(
            MCPTool(
                name="create_case",
                description="Create support case",
                func=create_case,
                schema={
                    "customer_id": "string",
                    "case_type": "string",
                    "description": "string",
                },
            )
        )

        self.register_tool(
            MCPTool(
                name="schedule_campaign",
                description="Schedule marketing campaign",
                func=schedule_campaign,
                schema={
                    "campaign_name": "string",
                    "segment_id": "string",
                    "steps": "array",
                },
            )
        )
