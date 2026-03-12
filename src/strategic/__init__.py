"""Static data definitions for Level 4 strategic agent demos."""


def get_uc4_scenarios():
    return [
        {"name": "Broad Email Blast",  "segment": "all",      "segment_size": 200, "conversion_rate": 0.04, "avg_order_value": 149.99, "campaign_cost": 800.0, "risk": "medium"},
        {"name": "VIP Targeted Offer", "segment": "vip",      "segment_size": 45,  "conversion_rate": 0.18, "avg_order_value": 199.99, "campaign_cost": 300.0, "risk": "low"},
        {"name": "At-Risk Win-Back",   "segment": "at_risk",  "segment_size": 80,  "conversion_rate": 0.12, "avg_order_value": 99.99,  "campaign_cost": 400.0, "risk": "high"},
    ]


def get_uc6_initiatives():
    return [
        {"name": "Premium Membership Drive",  "est_revenue": 12000, "effort": "low",    "timeline": "Q1"},
        {"name": "Win-Back Dormant VIPs",      "est_revenue": 8500,  "effort": "medium", "timeline": "Q1"},
        {"name": "Cross-Sell Electronics",     "est_revenue": 22000, "effort": "high",   "timeline": "Q2"},
        {"name": "Churn Reduction Program",    "est_revenue": 15000, "effort": "medium", "timeline": "Q2"},
        {"name": "NPS Improvement Campaign",   "est_revenue": 5000,  "effort": "low",    "timeline": "Q3"},
        {"name": "New Customer Onboarding",    "est_revenue": 9000,  "effort": "medium", "timeline": "Q3"},
    ]
