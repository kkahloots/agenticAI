"""SQL Generator for dynamic query generation with safety checks."""

import re
from typing import Optional


class SQLGenerator:
    """Generate safe SQL queries from natural language."""
    
    ALLOWED_TABLES = {
        "customers", "campaigns", "campaign_results",
        "customer_interactions", "offers", "notifications", "cases"
    }
    
    FORBIDDEN_KEYWORDS = [
        "INSERT", "UPDATE", "DELETE", "DROP", "ALTER",
        "TRUNCATE", "CREATE", "GRANT", "REVOKE"
    ]
    
    def generate(self, intent: str, context: Optional[dict] = None) -> dict:
        """Generate SQL from natural language intent."""
        intent_lower = intent.lower()
        
        # Check for forbidden operations
        for keyword in self.FORBIDDEN_KEYWORDS:
            if keyword.lower() in intent_lower:
                return {
                    "error": "forbidden_operation",
                    "keyword": keyword,
                    "query": None
                }
        
        # Pattern matching for common queries
        if "dormant" in intent_lower and "vip" in intent_lower:
            return self._generate_dormant_vip_query(context)
        
        if "return" in intent_lower and "risk" in intent_lower:
            return self._generate_return_risk_query(context)
        
        if "campaign" in intent_lower and ("performance" in intent_lower or "result" in intent_lower):
            return self._generate_campaign_performance_query(context)
        
        if "segment" in intent_lower or "customer" in intent_lower:
            return self._generate_customer_segment_query(intent, context)
        
        return {
            "error": "intent_not_recognized",
            "query": None,
            "suggestion": "Try more specific criteria"
        }
    
    def _generate_dormant_vip_query(self, context: Optional[dict]) -> dict:
        """Generate query for dormant VIP customers."""
        query = """
SELECT customer_id, segment, engagement_score, lifetime_value
FROM customers
WHERE segment = 'dormant_vip'
ORDER BY lifetime_value DESC
LIMIT 50
        """.strip()
        
        return {
            "query": query,
            "intent": "dormant_vip_targeting",
            "tables": ["customers"],
            "safe": True
        }
    
    def _generate_return_risk_query(self, context: Optional[dict]) -> dict:
        """Generate query for high return risk customers."""
        threshold = context.get("threshold", 0.7) if context else 0.7
        
        query = f"""
SELECT customer_id, return_risk, identity_status
FROM customers
WHERE return_risk > {threshold}
  AND identity_status IN ('verified', 'pending')
  AND marketing_consent = 1
ORDER BY return_risk DESC
        """.strip()
        
        return {
            "query": query,
            "intent": "return_risk_identification",
            "tables": ["customers"],
            "safe": True
        }
    
    def _generate_campaign_performance_query(self, context: Optional[dict]) -> dict:
        """Generate query for campaign performance."""
        query = """
SELECT offer_code, COUNT(*) AS sends, AVG(conversion_rate) AS avg_conversion
FROM campaign_results
GROUP BY offer_code
ORDER BY avg_conversion DESC
        """.strip()
        
        return {
            "query": query,
            "intent": "campaign_performance_summary",
            "tables": ["campaign_results"],
            "safe": True
        }
    
    def _generate_customer_segment_query(self, intent: str, context: Optional[dict]) -> dict:
        """Generate query for customer segmentation."""
        conditions = []
        
        # Extract conditions from intent
        if "vip" in intent.lower():
            conditions.append("segment = 'vip'")
        if "verified" in intent.lower():
            conditions.append("identity_status = 'verified'")
        if "consent" in intent.lower():
            conditions.append("marketing_consent = 1")
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        query = f"""
SELECT customer_id, full_name, segment, engagement_score
FROM customers
WHERE {where_clause}
ORDER BY engagement_score DESC
LIMIT 100
        """.strip()
        
        return {
            "query": query,
            "intent": "customer_segmentation",
            "tables": ["customers"],
            "safe": True
        }
    
    def validate(self, query: str) -> dict:
        """Validate SQL query for safety."""
        query_upper = query.upper()
        
        # Check for forbidden keywords
        for keyword in self.FORBIDDEN_KEYWORDS:
            if keyword in query_upper:
                return {
                    "valid": False,
                    "error": "forbidden_keyword",
                    "keyword": keyword
                }
        
        # Check for allowed tables only
        for table in re.findall(r'FROM\s+(\w+)', query_upper):
            if table.lower() not in self.ALLOWED_TABLES:
                return {
                    "valid": False,
                    "error": "forbidden_table",
                    "table": table
                }
        
        # Must be SELECT only
        if not query_upper.strip().startswith("SELECT"):
            return {
                "valid": False,
                "error": "must_be_select"
            }
        
        return {"valid": True}


def create_sql_generator() -> SQLGenerator:
    """Create SQL generator instance."""
    return SQLGenerator()


def generate_sql(intent: str, context: Optional[dict] = None) -> dict:
    """Generate SQL from natural language intent (convenience function)."""
    generator = SQLGenerator()
    return generator.generate(intent, context)
