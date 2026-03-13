"""Product Catalog MCP Server - exposes product data tools."""
from __future__ import annotations
import json
from mcp_servers import MCPServer, MCPTool


def get_products(category: str | None = None, limit: int = 100) -> dict:
    """Get products from catalog."""
    try:
        with open("data/products.json") as f:
            products = json.load(f)
        if category:
            products = [p for p in products if p.get("category") == category]
        return {"products": products[:limit], "count": len(products)}
    except Exception as e:
        return {"error": str(e), "products": []}


def get_product_by_id(product_id: str) -> dict:
    """Get product by ID."""
    try:
        with open("data/products.json") as f:
            products = json.load(f)
        product = next((p for p in products if p.get("product_id") == product_id), None)
        return {"product": product} if product else {"error": "Product not found"}
    except Exception as e:
        return {"error": str(e)}


class ProductCatalogServer(MCPServer):
    """MCP server for product catalog operations."""
    
    def __init__(self):
        super().__init__(
            server_id="product_catalog",
            description="Product catalog and inventory data"
        )
        self.initialize()
    
    def initialize(self) -> None:
        """Register product catalog tools."""
        self.register_tool(MCPTool(
            name="get_products",
            description="Get products from catalog",
            func=get_products,
            schema={"category": "string", "limit": "integer"}
        ))
        
        self.register_tool(MCPTool(
            name="get_product_by_id",
            description="Get product details by ID",
            func=get_product_by_id,
            schema={"product_id": "string"}
        ))
