"""Behaviour Model - wraps nonagentic behaviour and content scoring."""

from nonagentic.recommenders import get_behaviour_scores, get_content_scores, get_category_affinity


class BehaviourModel:
    """Behaviour + content signal scoring."""

    def score(self, customer: dict, products: list) -> dict:
        behav = get_behaviour_scores(customer, products)
        content = get_content_scores(customer, products)
        affinity = get_category_affinity(behav, products)
        return {
            "behaviour_scores": behav,
            "content_scores": content,
            "category_affinity": affinity,
            "model": "behaviour",
        }
