# MCP Servers Specification

## Overview

MCP (Model Context Protocol) servers provide a standardized abstraction layer between agents and underlying tools. All agents invoke tools exclusively through MCP servers — never via direct function calls.

## Base Architecture

### MCPTool
- **File**: `mcp_servers/__init__.py`
- Wraps a callable function with name, description, and schema
- Invoked via `tool.invoke(**kwargs)`

### MCPServer (Abstract Base)
- **File**: `mcp_servers/__init__.py`
- Registers and manages a collection of MCPTool instances
- Exposes `invoke_tool(tool_name, **kwargs)` to agents
- Raises `ValueError` if tool not found

```python
class MCPServer(ABC):
    server_id: str
    description: str
    _tools: dict[str, MCPTool]

    def register_tool(tool: MCPTool) -> None
    def invoke_tool(tool_name: str, **kwargs) -> Any
    def list_tools() -> list[MCPTool]
    def get_tool(name: str) -> MCPTool | None
```

---

## Server Catalogue

### 1. CustomerDataServer

| Property | Value |
|----------|-------|
| **File** | `mcp_servers/customer_data_server.py` |
| **server_id** | `customer_data` |
| **Description** | Customer profiles, identity verification, and KYC data |
| **Used by** | knowledge_agent, action_agent |

#### Tools

| Tool | Function | Schema | Returns |
|------|----------|--------|---------|
| `search_customer_profile` | `nonagentic.tools.customer.search_customer_profile` | `{customer_id: string}` | `{customer: {...}}` |
| `get_identity_status` | `nonagentic.tools.customer.get_identity_status` | `{customer_id: string}` | `{identity_status, verification_date, expiry_date}` |
| `get_kyc_status` | `nonagentic.tools.customer.get_kyc_status` | `{customer_id: string}` | `{kyc_status, documents_required}` |

#### Usage Example
```python
from mcp_servers.customer_data_server import CustomerDataServer

server = CustomerDataServer()
result = server.invoke_tool("search_customer_profile", customer_id="CUST-001")
# result: {"customer": {"customer_id": "CUST-001", "segment": "vip", ...}}
```

---

### 2. AnalyticsServer

| Property | Value |
|----------|-------|
| **File** | `mcp_servers/analytics_server.py` |
| **server_id** | `analytics` |
| **Description** | SQL queries, segmentation, and analytics |
| **Used by** | analytics_agent, evaluation_agent |

#### Tools

| Tool | Function | Schema | Returns |
|------|----------|--------|---------|
| `run_sql_query` | `nonagentic.tools.analytics.run_sql_query` | `{sql: string, max_rows: integer}` | `{rows: [...], columns: [...], row_count: int}` |
| `generate_segment` | `nonagentic.tools.analytics.generate_segment` | `{filters: object, algorithm: string}` | `{segment_id, customers: [...], count: int}` |

#### Usage Example
```python
from mcp_servers.analytics_server import AnalyticsServer

server = AnalyticsServer()
result = server.invoke_tool(
    "run_sql_query",
    sql="SELECT customer_id, segment FROM customers WHERE segment = 'vip'",
    max_rows=100
)
# result: {"rows": [...], "columns": ["customer_id", "segment"], "row_count": 42}
```

---

### 3. RecommendationServer

| Property | Value |
|----------|-------|
| **File** | `mcp_servers/recommendation_server.py` |
| **server_id** | `recommendation` |
| **Description** | Product recommendations and offer suggestions |
| **Used by** | recommendation_agent |

#### Tools

| Tool | Function | Schema | Returns |
|------|----------|--------|---------|
| `recommend_products` | `nonagentic.tools.recommender.recommend` | `{customer_id: string, top_k: integer}` | `{recommendations: [...], scores: [...]}` |
| `recommend_offer` | `nonagentic.tools.functional.recommend_offer` | `{customer_id: string}` | `{offer_id, offer_type, eligibility: bool}` |

#### Usage Example
```python
from mcp_servers.recommendation_server import RecommendationServer

server = RecommendationServer()
result = server.invoke_tool("recommend_products", customer_id="CUST-001", top_k=5)
# result: {"recommendations": [{"product_id": "PROD-010", "score": 0.92}, ...]}
```

---

### 4. CRMServer

| Property | Value |
|----------|-------|
| **File** | `mcp_servers/crm_server.py` |
| **server_id** | `crm` |
| **Description** | CRM operations, notifications, and campaigns |
| **Used by** | action_agent, workflow_agent |

#### Tools

| Tool | Function | Schema | Returns |
|------|----------|--------|---------|
| `draft_email` | `nonagentic.tools.functional.draft_email` | `{customer_id: string, template_id: string, variables: object}` | `{subject, body, recipient}` |
| `send_notification` | `nonagentic.tools.functional.send_notification` | `{customer_id: string, channel: string, payload: object}` | `{notification_id, status}` |
| `create_case` | `nonagentic.tools.functional.create_case` | `{customer_id: string, case_type: string, description: string}` | `{case_id, status, assigned_to}` |
| `schedule_campaign` | `nonagentic.tools.strategic.schedule_campaign` | `{campaign_name: string, segment_id: string, steps: array}` | `{campaign_id, scheduled_at, step_count}` |

#### Usage Example
```python
from mcp_servers.crm_server import CRMServer

server = CRMServer()
result = server.invoke_tool(
    "send_notification",
    customer_id="CUST-001",
    channel="email",
    payload={"subject": "Your offer", "body": "..."}
)
# result: {"notification_id": "NOTIF-001", "status": "sent"}
```

---

### 5. ProductCatalogServer

| Property | Value |
|----------|-------|
| **File** | `mcp_servers/product_catalog_server.py` |
| **server_id** | `product_catalog` |
| **Description** | Product catalog and inventory data |
| **Used by** | knowledge_agent, recommendation_agent |

#### Tools

| Tool | Function | Schema | Returns |
|------|----------|--------|---------|
| `get_products` | `product_catalog_server.get_products` | `{category: string, limit: integer}` | `{products: [...], count: int}` |
| `get_product_by_id` | `product_catalog_server.get_product_by_id` | `{product_id: string}` | `{product: {...}}` |

#### Data Source
- Reads from `data/products.json`
- Functions defined inline in the server file (not delegated to `nonagentic.tools`)

#### Usage Example
```python
from mcp_servers.product_catalog_server import ProductCatalogServer

server = ProductCatalogServer()
result = server.invoke_tool("get_products", category="electronics", limit=10)
# result: {"products": [...], "count": 10}
```

---

## MCP Call Trace Format

Every MCP invocation is recorded in `state["mcp_calls"]`:

```python
{
    "server": "customer_data",          # server_id
    "tool": "search_customer_profile",  # tool name
    "params": {"customer_id": "CUST-001"},  # kwargs passed
    "result": {...}                     # raw tool return value
}
```

This trace is surfaced in the notebook via `display_metrics` and `display_agentic_audit_trail`.

---

## Agent → Server Mapping

| Agent | MCP Servers Used |
|-------|-----------------|
| orchestrator | none (uses memory directly) |
| knowledge | `customer_data`, `product_catalog` |
| analytics | `analytics` |
| recommendation | `recommendation`, `customer_data` |
| workflow | `crm`, `analytics`, `customer_data` |
| action | `crm`, `customer_data` |
| evaluation | `analytics` |
| memory | none (uses memory_manager directly) |

---

## Error Handling

All servers raise `ValueError` for unknown tool names. Agents catch this and fall back gracefully:

```python
try:
    result = server.invoke_tool(tool_name, **params)
except ValueError as e:
    result = {"error": str(e)}
except Exception as e:
    result = {"error": f"Tool execution failed: {str(e)}"}
```

---

## Adding a New MCP Server

1. Create `mcp_servers/your_server.py`
2. Subclass `MCPServer`, set `server_id` and `description`
3. Implement `initialize()` — register tools via `self.register_tool(MCPTool(...))`
4. Register the server in the agent that will use it
5. Add the server to the agent's `mcp_servers` list in `agentic/agent_registry.py`

```python
from mcp_servers import MCPServer, MCPTool

class YourServer(MCPServer):
    def __init__(self):
        super().__init__(server_id="your_server", description="What it does")
        self.initialize()

    def initialize(self) -> None:
        self.register_tool(MCPTool(
            name="your_tool",
            description="What the tool does",
            func=your_function,
            schema={"param1": "string", "param2": "integer"}
        ))
```
