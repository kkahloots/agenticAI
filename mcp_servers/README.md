# MCP Tool Servers

Model Context Protocol (MCP) servers expose tools and data to agents through a standardized interface.

## Overview

MCP servers provide a consistent abstraction layer for agent-tool interaction. Each server implements the MCP protocol and exposes tools that agents can invoke dynamically.

## Servers

### 1. Customer Data Server
**File**: `customer_server.py`

Provides customer profile and interaction data.

**Tools**:
- `search_customer_profile(customer_id)` - Get customer profile
- `get_customer_interactions(customer_id)` - Get interaction history
- `update_customer_profile(customer_id, data)` - Update profile
- `search_customers(filters)` - Search customers by criteria

**Usage**:
```python
from mcp_servers.customer_data_server import CustomerDataServer

server = CustomerDataServer()
profile = server.invoke_tool("search_customer_profile", customer_id="CUST-001")
```

### 2. Analytics Server
**File**: `analytics_server.py`

Performs data analysis and generates insights.

**Tools**:
- `run_sql_query(sql, max_rows)` - Execute SQL query
- `generate_segment(filters, algorithm)` - Create customer segments
- `analyze_metrics(metric_type, parameters)` - Analyze KPIs
- `get_fraud_score(customer_id)` - Calculate fraud risk

**Usage**:
```python
from mcp_servers.analytics_server import AnalyticsServer

server = AnalyticsServer()
result = server.invoke_tool("run_sql_query", sql="SELECT * FROM customers LIMIT 10")
```

### 3. Recommendation Server
**File**: `recommendation_server.py`

Generates personalized recommendations.

**Tools**:
- `recommend_products(customer_id, top_k)` - Get product recommendations
- `get_similar_customers(customer_id)` - Find similar customers
- `rank_recommendations(customer_id, products)` - Rank products
- `get_cold_start_recommendations(top_k)` - Popular items for new users

**Usage**:
```python
from mcp_servers.recommendation_server import RecommendationServer

server = RecommendationServer()
recs = server.invoke_tool("recommend_products", customer_id="CUST-001", top_k=10)
```

### 4. Product Catalog Server
**File**: `product_server.py`

Provides product information and catalog operations.

**Tools**:
- `get_products(limit, filters)` - Get product list
- `get_product_details(product_id)` - Get product info
- `search_products(query)` - Search products
- `get_product_categories()` - Get categories

**Usage**:
```python
from mcp_servers.product_catalog_server import ProductCatalogServer

server = ProductCatalogServer()
products = server.invoke_tool("get_products", limit=10)
```

### 5. CRM Server
**File**: `crm_server.py`

Manages CRM operations and workflows.

**Tools**:
- `create_case(customer_id, case_type, description)` - Create support case
- `send_notification(customer_id, message, channel)` - Send notification
- `log_interaction(customer_id, interaction_type, data)` - Log interaction
- `get_customer_cases(customer_id)` - Get customer cases

**Usage**:
```python
from mcp_servers.crm_server import CRMServer

server = CRMServer()
case = server.invoke_tool("create_case", customer_id="CUST-001", case_type="support")
```

### 6. Compliance Server
**File**: `compliance_server.py`

Ensures compliance and safety.

**Tools**:
- `check_compliance(data, policy)` - Check policy compliance
- `redact_pii(text)` - Redact sensitive data
- `validate_consent(customer_id, action)` - Validate consent
- `log_audit_event(event_type, data)` - Log audit event

**Usage**:
```python
from mcp_servers.compliance_server import ComplianceServer

server = ComplianceServer()
redacted = server.invoke_tool("redact_pii", text="Customer: John Doe, Email: john@example.com")
```

### 7. Notification Server
**File**: `notification_server.py`

Handles notification delivery.

**Tools**:
- `send_email(customer_id, subject, body)` - Send email
- `send_sms(customer_id, message)` - Send SMS
- `send_push(customer_id, message)` - Send push notification
- `get_notification_status(notification_id)` - Get status

**Usage**:
```python
from mcp_servers.notification_server import NotificationServer

server = NotificationServer()
result = server.invoke_tool("send_email", customer_id="CUST-001", subject="Hello", body="Message")
```

### 8. Feature Server
**File**: `feature_server.py`

Provides feature engineering and selection.

**Tools**:
- `build_features(customer_id, feature_set)` - Build features
- `select_features(features, target)` - Select important features
- `get_feature_importance(model)` - Get feature importance
- `transform_features(data, transformations)` - Transform features

**Usage**:
```python
from mcp_servers.feature_server import FeatureServer

server = FeatureServer()
features = server.invoke_tool("build_features", customer_id="CUST-001", feature_set="default")
```

### 9. LLM Reasoning Server
**File**: `llm_reasoning_server.py`

Provides LLM-based reasoning and analysis.

**Tools**:
- `reason_about(question, context)` - LLM reasoning
- `summarize(text, length)` - Summarize text
- `extract_entities(text)` - Extract entities
- `classify_text(text, categories)` - Classify text

**Usage**:
```python
from mcp_servers.llm_reasoning_server import LLMReasoningServer

server = LLMReasoningServer()
result = server.invoke_tool("reason_about", question="Why is this customer at risk?", context={})
```

## Protocol

All servers implement the MCP protocol:

```python
class MCPServer:
    def invoke_tool(self, tool_name: str, **kwargs) -> dict:
        """Invoke a tool with parameters."""
        pass
    
    def get_tools(self) -> list[dict]:
        """Get available tools."""
        pass
    
    def get_tool_schema(self, tool_name: str) -> dict:
        """Get tool input/output schema."""
        pass
```

## Integration with Agents

Agents discover and invoke tools dynamically:

```python
from agentic.registry.tool_registry import tool_registry

# Discover tools
tools = tool_registry.get_tools_for_agent("analytics")

# Invoke tool
result = tool_registry.invoke_tool("analytics", "run_sql_query", sql="SELECT * FROM customers")
```

## Error Handling

All servers handle errors gracefully:

```python
result = server.invoke_tool("some_tool", param="value")

if "error" in result:
    print(f"Error: {result['error']}")
else:
    print(f"Success: {result['data']}")
```

## Audit Trail

All tool invocations are logged:

```python
# Audit trail includes:
# - Tool name
# - Parameters
# - Result
# - Timestamp
# - User/Agent ID
# - Status (success/failure)
```

## Testing

Test MCP servers:

```bash
pytest tests/test_mcp_servers.py -v
```

## Documentation

- [Main README](../README.md) - Project overview
- [Agentic Architecture](./README.md) - System architecture
- [Developer Guide](../docs/agentic/developer/guide.md) - API details

---

**Status**: ✅ Production Ready | **Version**: 1.0
