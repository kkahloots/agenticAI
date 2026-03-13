"""Evaluation Agent - validates results and triggers replanning if needed."""

from typing import Optional


class EvaluationAgent:
    """Evaluates execution results."""
    
    def evaluate(self, result: dict, expected_output_type: str, request_id: str) -> dict:
        """Evaluate result quality."""
        # Simple rule-based evaluation
        # In production, this would use more sophisticated checks
        
        confidence = 1.0
        issues = []
        needs_replan = False
        
        # Check for errors
        if result.get("error"):
            confidence = 0.0
            issues.append(f"Error: {result['error']}")
            needs_replan = True
        
        # Check for empty results
        if expected_output_type == "lead_list":
            prospects = result.get("result", {}).get("prospects", [])
            if not prospects:
                confidence = 0.3
                issues.append("No prospects found")
        
        elif expected_output_type == "offer_recommendation":
            offer_code = result.get("result", {}).get("offer_code")
            if not offer_code:
                confidence = 0.0
                issues.append("No offer recommended")
                needs_replan = True
        
        elif expected_output_type == "notification_result":
            status = result.get("result", {}).get("status")
            if status == "blocked":
                confidence = 0.5
                issues.append("Notification blocked by consent")
        
        elif expected_output_type == "identity_verification":
            gate_passed = result.get("result", {}).get("gate_passed")
            if gate_passed is False:
                confidence = 0.7
                issues.append("Identity verification failed")
        
        return {
            "confidence": confidence,
            "issues": issues,
            "needs_replan": needs_replan,
            "evaluation_passed": confidence >= 0.5,
            "request_id": request_id
        }


def create_evaluation_agent() -> EvaluationAgent:
    """Create evaluation agent instance."""
    return EvaluationAgent()
