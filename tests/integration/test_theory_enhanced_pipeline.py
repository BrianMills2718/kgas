#!/usr/bin/env python3
"""
End-to-end test for theory-enhanced pipeline
Tests complete PDF → Theory → Graph → Answer workflow
"""

import pytest
import os
from pathlib import Path
from src.core.orchestration.pipeline_orchestrator import PipelineOrchestrator
from src.core.config_manager import get_config

class TestTheoryEnhancedPipeline:
    
    def setup_method(self):
        """Setup test environment"""
        # Skip if no API keys
        required_keys = ["GEMINI_API_KEY", "NEO4J_PASSWORD"]
        for key in required_keys:
            if not os.getenv(key):
                pytest.skip(f"{key} required for integration test")
        
        self.orchestrator = PipelineOrchestrator(config_manager=get_config())
        self.test_file = "/home/brian/projects/Digimons/experiments/lit_review/data/test_texts/texts/grusch_testimony.txt"
    
    def test_theory_enhanced_workflow_basic(self):
        """Test basic theory-enhanced workflow execution"""
        
        # Execute theory-enhanced workflow
        result = self.orchestrator.execute_theory_enhanced_workflow(self.test_file)
        
        # Verify successful execution
        assert result["status"] == "success"
        
        # Verify all workflow steps completed
        workflow_results = result["workflow_results"]
        expected_steps = [
            "pdf_loading", 
            "theory_extraction",
            "text_chunking", 
            "entity_building",
            "relationship_building",
            "pagerank"
        ]
        
        for step in expected_steps:
            assert step in workflow_results
            assert workflow_results[step].status == "success"
        
        # Verify theory metadata
        theory_metadata = result["theory_metadata"]
        assert theory_metadata["entities_created"] > 0
        assert theory_metadata["relationships_created"] > 0
        assert "theory_type" in theory_metadata
        
        print(f"✅ Theory-enhanced pipeline successful:")
        print(f"   Theory type: {theory_metadata['theory_type']}")
        print(f"   Entities created: {theory_metadata['entities_created']}")
        print(f"   Relationships created: {theory_metadata['relationships_created']}")

    def test_theory_enhanced_workflow_components(self):
        """Test individual components of theory-enhanced workflow"""
        
        # Test theory extraction tool access
        from src.core.tool_contract import ToolRequest
        
        # Create a simple text request
        request = ToolRequest(input_data={
            "text": "Cognitive mapping theory proposes mental representations."
        })
        
        # Test tool execution through orchestrator
        theory_tool = self.orchestrator._get_theory_extraction_tool()
        result = theory_tool.execute(request)
        
        assert result.status == "success"
        assert len(result.data["kgas_entities"]) > 0
        
        print(f"✅ Theory extraction component working:")
        print(f"   Entities extracted: {len(result.data['kgas_entities'])}")
        print(f"   Theory type: {result.data['extraction_metadata']['theory_type']}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])