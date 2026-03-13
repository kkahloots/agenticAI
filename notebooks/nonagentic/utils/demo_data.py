"""
Demo data utilities for consistent test data across notebooks.
Provides standardized customer selections and test queries.
"""

def get_demo_customers():
    """Get consistent demo customer selections for different use cases."""
    return {
        # Level 1 use cases
        "profile_demo": "CUST-005",  # Good mix of data
        "identity_verification_mix": [
            # Verified customers (9 customers = 60%)
            "CUST-001", "CUST-004", "CUST-006", "CUST-007", "CUST-008", 
            "CUST-009", "CUST-011", "CUST-012", "CUST-015",
            # Unverified customers (4 customers = 27%)
            "CUST-005", "CUST-013", "CUST-014", "CUST-023",
            # Pending customers (2 customers = 13%)
            "CUST-002", "CUST-003"
        ],
        
        # Level 2 use cases
        "analytics_sample": ["CUST-001", "CUST-004", "CUST-007", "CUST-015", "CUST-025"],
        "customer_360_demo": "CUST-001",
        
        # Level 3 use cases
        "lead_scoring_sample": ["CUST-001", "CUST-004", "CUST-006", "CUST-007", "CUST-008"],
        "nba_test_customers": ["CUST-001", "CUST-004", "CUST-006", "CUST-007", "CUST-008"],
        "consent_demo": "CUST-001",  # Has marketing consent=true
        "identity_gate_demo": "CUST-005",  # Has identity_status=unverified
        "upselling_demo": ["CUST-001", "CUST-004", "CUST-007", "CUST-015", "CUST-025"],
        "recommendations_demo": "CUST-001",
        "collaborative_demo": "CUST-007",
    }


def get_test_queries():
    """Get standardized test queries for different notebook sections."""
    return {
        # Level 1 queries
        "email_search": "Show me emails about identity verification reminders sent to customers",
        "notes_escalations": "Show me agent notes about customer escalations and complaints",
        "notes_retention": "Show me agent notes about customer retention and loyalty bonuses",
        "policy_questions": [
            "What is the identity verification renewal policy? How often must customers renew?",
            "What are the fraud score thresholds that trigger manual approval?",
            "What are the eligibility criteria for the Premium Membership promotion?"
        ],
        "cross_source": "What do our policies say about return risk and churn prevention workflows?",
        
        # Level 2 queries - SQL patterns
        "top_customers_sql": '''
        SELECT customer_id, full_name, segment, lifetime_value, fraud_score, engagement_score
        FROM customers
        WHERE lifetime_value > 10000
        ORDER BY lifetime_value DESC
        LIMIT 10
        ''',
        "high_fraud_risk_sql": '''
        SELECT segment, COUNT(*) as count, AVG(fraud_score) as avg_fraud, AVG(engagement_score) as avg_engagement
        FROM customers
        WHERE fraud_score > 0.7
        GROUP BY segment
        ORDER BY count DESC
        ''',
        
        # Level 3 queries - functional patterns
        "bulk_campaign_offer": "PROMO-PREMIUM-MEMBERSHIP",
        "bulk_campaign_segment": "dormant_vip",
    }


def get_high_return_risk_customers():
    """Get customers with high return risk (>0.7) and verified/pending identity for intervention demos."""
    return [
        "CUST-011", "CUST-013", "CUST-021", "CUST-032", "CUST-033",
        "CUST-034", "CUST-041", "CUST-043", "CUST-049", "CUST-052"
    ]


