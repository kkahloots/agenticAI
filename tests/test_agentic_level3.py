"""Tests for agentic Level 3 implementation."""

import pytest
from agentic.utils.agentic_api import create_api
from agentic.orchestrator.orchestrator_agent import create_orchestrator
from agentic.planner.planner_agent import create_planner
from agentic.registry.tool_registry import get_registry
from agentic.memory.memory_manager import get_memory
from agentic.sql.sql_generator import create_sql_generator


class TestAgenticInfrastructure:
    """Test core infrastructure components."""
    
    def test_api_creation(self):
        """Test API can be created."""
        api = create_api()
        assert api is not None
        assert hasattr(api, 'orchestrator')
    
    def test_orchestrator_creation(self):
        """Test orchestrator can be created."""
        orch = create_orchestrator()
        assert orch is not None
        assert hasattr(orch, 'planner')
        assert hasattr(orch, 'functional_agent')
    
    def test_planner_creation(self):
        """Test planner can be created."""
        planner = create_planner()
        assert planner is not None
    
    def test_registry_singleton(self):
        """Test registry is singleton."""
        reg1 = get_registry()
        reg2 = get_registry()
        assert reg1 is reg2
    
    def test_memory_singleton(self):
        """Test memory is singleton."""
        mem1 = get_memory()
        mem2 = get_memory()
        assert mem1 is mem2
    
    def test_sql_generator_creation(self):
        """Test SQL generator can be created."""
        gen = create_sql_generator()
        assert gen is not None


class TestPlanner:
    """Test planner agent."""
    
    def test_plan_lead_scoring(self):
        """Test planning for lead scoring."""
        planner = create_planner()
        plan = planner.plan("Score leads for premium membership")
        
        assert plan['intent'] == 'lead_scoring'
        assert len(plan['subtasks']) > 0
        assert 'recommendation_agent' in plan['selected_agents']
    
    def test_plan_enrichment(self):
        """Test planning for enrichment."""
        planner = create_planner()
        plan = planner.plan("Enrich customer CUST-001")
        
        assert plan['intent'] == 'customer_enrichment'
        assert 'functional_agent' in plan['selected_agents']
    
    def test_plan_nba(self):
        """Test planning for NBA."""
        planner = create_planner()
        plan = planner.plan("Recommend next-best-action for customer")
        
        assert plan['intent'] == 'nba_recommendation'
        assert 'recommendation_agent' in plan['selected_agents']
        assert 'compliance_agent' in plan['selected_agents']


class TestSQLGenerator:
    """Test SQL generator."""
    
    def test_generate_dormant_vip_query(self):
        """Test generating dormant VIP query."""
        gen = create_sql_generator()
        result = gen.generate("Find dormant VIP customers")
        
        assert result.get('query') is not None
        assert 'SELECT' in result['query']
        assert 'dormant_vip' in result['query']
        assert result['safe'] is True
    
    def test_generate_return_risk_query(self):
        """Test generating return risk query."""
        gen = create_sql_generator()
        result = gen.generate("Find high return risk customers")
        
        assert result.get('query') is not None
        assert 'return_risk' in result['query']
        assert result['safe'] is True
    
    def test_validate_safe_query(self):
        """Test validating safe query."""
        gen = create_sql_generator()
        result = gen.validate("SELECT * FROM customers WHERE segment = 'vip'")
        
        assert result['valid'] is True
    
    def test_validate_unsafe_query(self):
        """Test validating unsafe query."""
        gen = create_sql_generator()
        result = gen.validate("DELETE FROM customers WHERE id = 1")
        
        assert result['valid'] is False
        assert result['error'] == 'forbidden_keyword'


class TestMemory:
    """Test memory manager."""
    
    def test_record_plan(self):
        """Test recording plan."""
        memory = get_memory()
        memory.clear()
        
        plan = {"goal": "test", "subtasks": []}
        memory.record_plan("req-001", plan)
        
        history = memory.get_request_history("req-001")
        assert len(history) == 1
        assert history[0].entry_type == "plan"
    
    def test_record_tool_usage(self):
        """Test recording tool usage."""
        memory = get_memory()
        memory.clear()
        
        memory.record_tool_usage("req-001", "score_leads", {"offer": "test"}, {"result": "ok"})
        
        history = memory.get_request_history("req-001")
        assert len(history) == 1
        assert history[0].entry_type == "tool_usage"
    
    def test_record_sql_generation(self):
        """Test recording SQL generation."""
        memory = get_memory()
        memory.clear()
        
        memory.record_sql_generation("req-001", "SELECT * FROM customers", "test query")
        
        history = memory.get_request_history("req-001")
        assert len(history) == 1
        assert history[0].entry_type == "sql_generation"


class TestUseCases:
    """Test use case execution."""
    
    def test_uc1_deterministic(self):
        """Test UC1 lead scoring in deterministic mode."""
        api = create_api()
        result = api.execute_uc1_lead_scoring(
            offer_code="PROMO-PREMIUM-MEMBERSHIP",
            top_n=10,
            mode="deterministic"
        )
        
        assert result['mode'] == 'deterministic'
        assert 'plan' in result
        assert 'final_result' in result
        assert result['final_result']['execution_status'] == 'success'
    
    def test_uc1_dynamic(self):
        """Test UC1 lead scoring in dynamic mode."""
        api = create_api()
        result = api.execute_uc1_lead_scoring(
            offer_code="PROMO-PREMIUM-MEMBERSHIP",
            top_n=10,
            mode="dynamic"
        )
        
        assert result['mode'] == 'dynamic'
        assert 'tool_selections' in result
        assert result['memory_entries'] > 0
    
    def test_uc2_enrichment(self):
        """Test UC2 customer enrichment."""
        api = create_api()
        result = api.execute_uc2_enrichment(
            customer_id="CUST-001",
            mode="deterministic"
        )
        
        assert 'final_result' in result
        assert result['final_result']['execution_status'] in ['success', 'failed']
    
    def test_uc3_nba(self):
        """Test UC3 NBA recommendation."""
        api = create_api()
        result = api.execute_uc3_nba(
            customer_id="CUST-001",
            mode="deterministic"
        )
        
        assert 'final_result' in result
        assert len(result['agent_path']) > 0
    
    def test_output_parity(self):
        """Test output parity between modes."""
        api = create_api()
        
        result_det = api.execute_uc1_lead_scoring(
            offer_code="PROMO-PREMIUM-MEMBERSHIP",
            top_n=10,
            mode="deterministic"
        )
        
        result_dyn = api.execute_uc1_lead_scoring(
            offer_code="PROMO-PREMIUM-MEMBERSHIP",
            top_n=10,
            mode="dynamic"
        )
        
        # Both should return same number of prospects
        det_prospects = result_det['final_result']['result']['prospects']
        dyn_prospects = result_dyn['final_result']['result']['prospects']
        
        assert len(det_prospects) == len(dyn_prospects)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
