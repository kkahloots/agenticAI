"""Customer 360 view - unified data from CRM, sales, social, and support."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

_SALES_DATA = None
_SOCIAL_DATA = None
_SUPPORT_DATA = None


def _load_json_data(filepath: str) -> list[dict]:
    """Load JSON data file."""
    path = Path(filepath)
    if not path.exists():
        return []
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return []


def _get_sales_data() -> list[dict]:
    """Lazy load sales transactions."""
    global _SALES_DATA
    if _SALES_DATA is None:
        _SALES_DATA = _load_json_data("data/sales_transactions.json")
    return _SALES_DATA


def _get_social_data() -> list[dict]:
    """Lazy load social media data."""
    global _SOCIAL_DATA
    if _SOCIAL_DATA is None:
        _SOCIAL_DATA = _load_json_data("data/social_media.json")
    return _SOCIAL_DATA


def _get_support_data() -> list[dict]:
    """Lazy load support tickets."""
    global _SUPPORT_DATA
    if _SUPPORT_DATA is None:
        _SUPPORT_DATA = _load_json_data("data/support_tickets.json")
    return _SUPPORT_DATA


def get_customer_360(customer_id: str) -> dict:
    """
    Get unified 360-degree view of a customer.

    Returns:
        dict with keys: customer_profile, sales, social, support, summary
    """
    from nonagentic.tools.customer import search_customer_profile

    # Get base customer profile
    profile_result = search_customer_profile(customer_id=customer_id)
    profile = profile_result.get("customer")

    if not profile:
        return {"error": "customer_not_found", "customer_id": customer_id}

    # Get sales transactions
    sales = [s for s in _get_sales_data() if s.get("customer_id") == customer_id]

    # Get social media activity (sample - not linked to customer_id in data)
    all_social = _get_social_data()
    social = all_social[:5] if all_social else []

    # Get support tickets
    support = [t for t in _get_support_data() if t.get("customer_id") == customer_id]

    # Calculate summary metrics
    total_sales = sum(
        s.get("total_amount", 0) for s in sales if s.get("status") == "completed"
    )
    avg_transaction = total_sales / len(sales) if sales else 0

    sentiment_counts = {}
    for post in social:
        sent = post.get("sentiment", "neutral")
        sentiment_counts[sent] = sentiment_counts.get(sent, 0) + 1

    open_tickets = len(
        [t for t in support if t.get("status") in ["open", "in_progress"]]
    )

    return {
        "customer_id": customer_id,
        "customer_profile": profile,
        "sales": {
            "transactions": sales,
            "total_count": len(sales),
            "total_amount": round(total_sales, 2),
            "avg_transaction": round(avg_transaction, 2),
            "channels": (
                list(set(s.get("channel", "unknown") for s in sales)) if sales else []
            ),
        },
        "social": {
            "posts": social,
            "total_count": len(social),
            "sentiment_breakdown": sentiment_counts,
            "platforms": (
                list(set(s.get("platform", "unknown") for s in social))
                if social
                else []
            ),
        },
        "support": {
            "tickets": support,
            "total_count": len(support),
            "open_tickets": open_tickets,
            "ticket_types": (
                list(set(t.get("type", "unknown") for t in support)) if support else []
            ),
        },
        "summary": {
            "total_sales_value": round(total_sales, 2),
            "transaction_count": len(sales),
            "social_engagement": len(social),
            "support_tickets": len(support),
            "open_issues": open_tickets,
            "overall_sentiment": (
                max(sentiment_counts.items(), key=lambda x: x[1])[0]
                if sentiment_counts
                else "neutral"
            ),
        },
    }


def get_sales_analytics(filters: Optional[dict] = None) -> dict:
    """
    Get sales analytics with optional filters.

    Filters: customer_id, product, channel, date_from, date_to
    """
    sales = _get_sales_data()

    if filters:
        if "customer_id" in filters:
            sales = [s for s in sales if s.get("customer_id") == filters["customer_id"]]
        if "product" in filters:
            sales = [s for s in sales if s.get("product") == filters["product"]]
        if "channel" in filters:
            sales = [s for s in sales if s.get("channel") == filters["channel"]]

    # Calculate metrics
    total_revenue = sum(
        s.get("total_amount", 0) for s in sales if s.get("status") == "completed"
    )

    by_product = {}
    for s in sales:
        if s.get("status") == "completed":
            prod = s.get("product_category", "unknown")
            by_product[prod] = by_product.get(prod, 0) + s.get("total_amount", 0)

    by_channel = {}
    for s in sales:
        ch = s.get("channel", "unknown")
        by_channel[ch] = by_channel.get(ch, 0) + 1

    return {
        "total_transactions": len(sales),
        "total_revenue": round(total_revenue, 2),
        "avg_transaction_value": round(total_revenue / len(sales), 2) if sales else 0,
        "by_product": {k: round(v, 2) for k, v in by_product.items()},
        "by_channel": by_channel,
        "top_product": (
            max(by_product.items(), key=lambda x: x[1])[0] if by_product else None
        ),
    }


def get_sentiment_analytics(filters: Optional[dict] = None) -> dict:
    """
    Get sentiment analytics from social media.

    Filters: platform, sentiment
    """
    social = _get_social_data()

    if filters:
        if "platform" in filters:
            social = [s for s in social if s.get("platform") == filters["platform"]]
        if "sentiment" in filters:
            social = [s for s in social if s.get("sentiment") == filters["sentiment"]]

    # Calculate metrics
    sentiment_counts = {}
    for post in social:
        sent = post.get("sentiment", "neutral")
        sentiment_counts[sent] = sentiment_counts.get(sent, 0) + 1

    total = len(social)
    sentiment_percentages = (
        {k: round(v / total * 100, 1) for k, v in sentiment_counts.items()}
        if total > 0
        else {}
    )

    return {
        "total_posts": total,
        "sentiment_counts": sentiment_counts,
        "sentiment_percentages": sentiment_percentages,
        "positive_ratio": sentiment_percentages.get("positive", 0),
        "negative_ratio": sentiment_percentages.get("negative", 0),
        "sample_posts": social[:5],
    }


def get_support_analytics(filters: Optional[dict] = None) -> dict:
    """
    Get support ticket analytics.

    Filters: customer_id, type, priority, status
    """
    tickets = _get_support_data()

    if filters:
        if "customer_id" in filters:
            tickets = [
                t for t in tickets if t.get("customer_id") == filters["customer_id"]
            ]
        if "type" in filters:
            tickets = [t for t in tickets if t.get("type") == filters["type"]]
        if "priority" in filters:
            tickets = [t for t in tickets if t.get("priority") == filters["priority"]]
        if "status" in filters:
            tickets = [t for t in tickets if t.get("status") == filters["status"]]

    # Calculate metrics
    by_type = {}
    for t in tickets:
        typ = t.get("type", "unknown")
        by_type[typ] = by_type.get(typ, 0) + 1

    by_status = {}
    for t in tickets:
        stat = t.get("status", "unknown")
        by_status[stat] = by_status.get(stat, 0) + 1

    resolved_times = [
        t.get("resolution_time_hours", 0)
        for t in tickets
        if t.get("resolution_time_hours")
    ]
    avg_resolution = sum(resolved_times) / len(resolved_times) if resolved_times else 0

    return {
        "total_tickets": len(tickets),
        "by_type": by_type,
        "by_status": by_status,
        "open_tickets": by_status.get("open", 0) + by_status.get("in_progress", 0),
        "avg_resolution_hours": round(avg_resolution, 1),
        "high_priority": len([t for t in tickets if t.get("priority") == "high"]),
    }
