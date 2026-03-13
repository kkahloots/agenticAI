"""MCP module."""

from . import customer_server
from . import recommendation_server
from . import notification_server
from . import compliance_server
from . import analytics_server
from . import functional_server

__all__ = [
    "customer_server",
    "recommendation_server",
    "notification_server",
    "compliance_server",
    "analytics_server",
    "functional_server"
]
