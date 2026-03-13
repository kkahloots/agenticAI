"""Content Model - wraps nonagentic content similarity scoring."""

from nonagentic.recommenders import get_content_scores, get_category_affinity


class ContentModel:
    """Category-based content similarity scoring."""

    def score(self, customer: dict, products: list) -> dict:
        content = get_content_scores(customer, products)
        affinity = get_category_affinity(content, products)
        return {
            "content_scores": content,
            "category_affinity": affinity,
            "model": "content",
        }
