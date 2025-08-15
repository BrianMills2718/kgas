#!/usr/bin/env python3
"""
Integration tests for T302 Theory Extraction Tool
Tests full theory extraction + KGAS integration pipeline
"""

import pytest
import os
from src.tools.phase3.t302_theory_extraction_kgas import T302TheoryExtractionKGAS
from src.core.tool_contract import ToolRequest
from src.core.service_manager import ServiceManager

class TestT302TheoryExtraction:
    
    def setup_method(self):
        """Setup test environment"""
        # Skip if no Gemini API key
        if not os.getenv("GEMINI_API_KEY"):
            pytest.skip("GEMINI_API_KEY required for theory extraction tests")
        
        self.service_manager = ServiceManager()
        self.tool = T302TheoryExtractionKGAS(self.service_manager)
    
    def test_theory_extraction_basic(self):
        """Test basic theory extraction functionality"""
        
        # Sample academic text
        test_text = """
        Cognitive mapping theory proposes that individuals construct mental representations
        of their environment through direct experience and social learning. These cognitive
        maps consist of concepts linked by causal relationships, with beliefs represented
        as nodes and causal connections as directed edges. The theory suggests that
        decision-making processes rely on traversing these cognitive networks to identify
        relevant information and potential outcomes.
        """
        
        request = ToolRequest(
            input_data={"text": test_text}
        )
        
        # Execute theory extraction
        result = self.tool.execute(request)
        
        # Verify successful execution
        assert result.status == "success"
        assert result.data is not None
        
        # Verify KGAS entities created
        entities = result.data["kgas_entities"]
        assert len(entities) > 0
        
        # Check entity structure
        sample_entity = entities[0]
        assert "entity_id" in sample_entity
        assert "canonical_name" in sample_entity
        assert "entity_type" in sample_entity
        assert sample_entity["entity_type"] == "THEORETICAL_CONSTRUCT"
        
        # Verify KGAS relationships created
        relationships = result.data["kgas_relationships"]
        assert len(relationships) > 0
        
        # Check relationship structure
        sample_rel = relationships[0]
        assert "relationship_id" in sample_rel
        assert "relationship_type" in sample_rel
        assert sample_rel["relationship_type"] in ["THEORETICAL_RELATIONSHIP", "THEORETICAL_ACTION"]
        
        # Verify theory schema included
        theory_schema = result.data["theory_schema"]
        assert "title" in theory_schema
        assert "model_type" in theory_schema
        
        print(f"✅ Theory extraction successful:")
        print(f"   Entities: {len(entities)}")
        print(f"   Relationships: {len(relationships)}")
        print(f"   Theory type: {result.data['extraction_metadata']['theory_type']}")
    
    def test_theory_extraction_quality(self):
        """Test theory extraction meets quality thresholds"""
        
        # Use longer, more complex academic text
        with open("/home/brian/projects/Digimons/experiments/lit_review/data/test_texts/texts/grusch_testimony.txt", "r") as f:
            test_text = f.read()[:5000]  # First 5000 chars
        
        request = ToolRequest(
            input_data={"text": test_text}
        )
        
        result = self.tool.execute(request)
        
        # Verify quality metrics
        assert result.status == "success"
        metadata = result.data["extraction_metadata"]
        
        # Should extract meaningful number of terms
        assert metadata["total_vocabulary_terms"] >= 10
        assert metadata["classified_terms"] >= 5
        
        # Extraction quality should be reasonable
        assert metadata["extraction_quality"] >= 0.3  # At least 30% classification rate
        
        # Confidence should reflect quality
        assert result.confidence.value >= 0.5
        
        print(f"✅ Theory extraction quality verified:")
        print(f"   Vocabulary terms: {metadata['total_vocabulary_terms']}")
        print(f"   Classified terms: {metadata['classified_terms']}")
        print(f"   Quality score: {metadata['extraction_quality']:.2f}")
        print(f"   Confidence: {result.confidence.value:.2f}")

    def test_theory_compatibility(self):
        """Test theory compatibility method"""
        compatibility = self.tool.get_theory_compatibility()
        assert isinstance(compatibility, list)
        assert "all_theories" in compatibility
        assert "academic_theories" in compatibility

    def test_input_validation(self):
        """Test input validation"""
        # Test valid input
        valid_result = self.tool.validate_input({"text": "This is a test text with enough content."})
        assert valid_result.is_valid
        
        # Test invalid input - missing text
        invalid_result = self.tool.validate_input({})
        assert not invalid_result.is_valid
        assert "Missing required field: text" in invalid_result.errors
        
        # Test invalid input - wrong type
        invalid_result2 = self.tool.validate_input({"text": 123})
        assert not invalid_result2.is_valid
        assert "text must be a string" in invalid_result2.errors

if __name__ == "__main__":
    pytest.main([__file__, "-v"])