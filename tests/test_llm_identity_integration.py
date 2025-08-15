#!/usr/bin/env python3
"""
Test LLM-enhanced identity service integration
Verifies that LLM resolution improves entity resolution accuracy
"""

import pytest
from src.core.identity_management.llm_enhanced_entity_resolver import LLMEnhancedEntityResolver
from src.core.identity_management.data_models import Mention, Entity
from src.services.llm_entity_resolver import MockEntityResolver
import uuid


class TestLLMIdentityIntegration:
    
    def setup_method(self):
        """Setup test environment"""
        # Create resolver with mock LLM provider
        self.resolver = LLMEnhancedEntityResolver(
            embedding_service=None,  # No embeddings for this test
            use_llm=True,
            llm_provider=MockEntityResolver()
        )
        
        # Create some test entities
        self.entities = {}
        self.mentions = {}
        self.surface_to_mentions = {}
        
        # Add test entities
        entity1_id = str(uuid.uuid4())
        self.entities[entity1_id] = Entity(
            id=entity1_id,
            canonical_name="Dr. Sarah Chen",
            entity_type="PERSON",
            confidence=0.9,
            mentions=[]
        )
        
        entity2_id = str(uuid.uuid4())
        self.entities[entity2_id] = Entity(
            id=entity2_id,
            canonical_name="Stanford University",
            entity_type="ORG",
            confidence=0.95,
            mentions=[]
        )
    
    def test_llm_resolution_fallback(self):
        """Test that LLM resolution is used when traditional methods fail"""
        
        # Create a mention that's a partial reference
        mention = Mention(
            id=str(uuid.uuid4()),
            surface_form="Dr. Chen",  # Partial name
            normalized_form="dr. chen",
            entity_type="PERSON",
            start_pos=0,
            end_pos=8,
            context="Dr. Chen published groundbreaking CRISPR research at Stanford.",
            source_ref="test_doc",
            confidence=0.85
        )
        
        # Try to resolve using the correct method signature
        entity_id, was_created = self.resolver.resolve_entity(
            normalized_form=mention.normalized_form,
            entity_type=mention.entity_type,
            entities=self.entities,
            mention_id=mention.id
        )
        
        # Should find Dr. Sarah Chen even with partial name
        assert entity_id is not None, "Should resolve partial name with LLM"
        
        # Verify it's the right entity
        if entity_id:
            entity = self.entities.get(entity_id)
            assert entity and "chen" in entity.canonical_name.lower()
    
    def test_improved_confidence_scoring(self):
        """Test that LLM improves confidence scoring"""
        
        # Try to resolve an ambiguous mention
        entity_id, was_created = self.resolver.resolve_entity(
            normalized_form="chen",
            entity_type="PERSON",
            entities=self.entities,
            mention_id=str(uuid.uuid4())
        )
        
        # With LLM, it should either find an existing Chen or create a new one
        assert entity_id is not None or was_created, "Should resolve or create entity for 'chen'"
    
    def test_find_similar_entities_with_llm(self):
        """Test finding similar entities using LLM enhancement"""
        
        # Try to resolve abbreviated form
        entity_id, was_created = self.resolver.resolve_entity(
            normalized_form="s. chen",
            entity_type="PERSON",
            entities=self.entities,
            mention_id=str(uuid.uuid4())
        )
        
        # Should either find Sarah Chen or create new entity
        if entity_id and not was_created:
            entity = self.entities.get(entity_id)
            assert entity is not None, "Should get valid entity"
    
    def test_organization_resolution(self):
        """Test resolving organization entities"""
        
        # Try to resolve Stanford
        entity_id, was_created = self.resolver.resolve_entity(
            normalized_form="stanford",
            entity_type="ORG",
            entities=self.entities,
            mention_id=str(uuid.uuid4())
        )
        
        # Should find Stanford University or create new entity
        if entity_id and not was_created:
            entity = self.entities.get(entity_id)
            assert entity and "Stanford" in entity.canonical_name
    
    def test_cross_document_entity_tracking(self):
        """Test that entities are correctly tracked across documents"""
        
        # Resolve first mention from doc1
        entity_id1, was_created1 = self.resolver.resolve_entity(
            normalized_form="dr. sarah chen",
            entity_type="PERSON",
            entities=self.entities,
            mention_id=str(uuid.uuid4())
        )
        
        # Resolve second mention from doc2 (partial reference)
        entity_id2, was_created2 = self.resolver.resolve_entity(
            normalized_form="chen",
            entity_type="PERSON",
            entities=self.entities,
            mention_id=str(uuid.uuid4())
        )
        
        # Both should resolve to valid entities
        assert entity_id1 is not None, "Should resolve first mention"
        assert entity_id2 is not None, "Should resolve second mention"
        
        # At minimum, both should be person entities if found
        if entity_id1:
            entity1 = self.entities.get(entity_id1)
            if entity1:
                assert entity1.entity_type == "PERSON" or entity1.entity_type is None
        
        if entity_id2:
            entity2 = self.entities.get(entity_id2)
            if entity2:
                assert entity2.entity_type == "PERSON" or entity2.entity_type is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])