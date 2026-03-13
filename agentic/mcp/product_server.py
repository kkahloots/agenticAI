"""Product MCP Server - wraps product catalog tools."""

from typing import Optional
from nonagentic.tools.recommender import _load_products


def get_product_catalog(category: Optional[str] = None) -> dict:
    """Get product catalog, optionally filtered by category."""
    products = _load_products()
    if category:
        products = [p for p in products if p.get("category") == category]
    return {
        "result": products,
        "tool_name": "get_product_catalog",
        "execution_status": "success",
        "audit": {"category": category, "count": len(products)},
    }


def get_product_metadata(product_id: str) -> dict:
    """Get metadata for a specific product."""
    products = _load_products()
    prod_map = {p["product_id"]: p for p in products}
    product = prod_map.get(product_id)
    return {
        "result": product,
        "tool_name": "get_product_metadata",
        "execution_status": "success" if product else "not_found",
        "audit": {"product_id": product_id},
    }


def get_product_categories() -> dict:
    """Get all unique product categories."""
    products = _load_products()
    categories = sorted(set(p.get("category", "unknown") for p in products))
    return {
        "result": categories,
        "tool_name": "get_product_categories",
        "execution_status": "success",
        "audit": {"count": len(categories)},
    }
