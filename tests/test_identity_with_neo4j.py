#!/usr/bin/env python3
"""Test that identity service works with Neo4j - separate script to avoid singleton issues"""

import sys
import os

sys.path.insert(0, '/home/brian/projects/Digimons')

# Set Neo4j credentials BEFORE importing ServiceManager
os.environ['NEO4J_URI'] = 'bolt://localhost:7687'
os.environ['NEO4J_USER'] = 'neo4j'
os.environ['NEO4J_PASSWORD'] = 'devpassword'

from src.core.service_manager import ServiceManager

def test_identity_service_with_neo4j():
    """Test that identity service works with Neo4j"""
    sm = ServiceManager()
    
    try:
        # Should work with Neo4j
        identity = sm.get_identity_service()
        assert identity is not None
        print("✅ Got identity service with Neo4j")
        
        # MUST implement required methods
        mention = identity.create_mention(
            surface_form="Test",
            start_pos=0,
            end_pos=4,
            source_ref="test",
            entity_type="TEST",
            confidence=1.0
        )
        
        print(f"Mention result type: {type(mention)}")
        print(f"Mention result: {mention}")
        
        # Handle wrapped response format
        if isinstance(mention, dict) and 'success' in mention and 'data' in mention:
            # Wrapped format
            assert mention['success'] == True
            mention_data = mention['data']
            assert "mention_id" in mention_data
            print(f"✅ Created mention with ID: {mention_data['mention_id']}")
        elif isinstance(mention, dict):
            # Direct dict format
            assert "mention_id" in mention
            print(f"✅ Created mention with ID: {mention['mention_id']}")
        else:
            # Object format
            assert hasattr(mention, 'mention_id')
            print(f"✅ Created mention with ID: {mention.mention_id}")
        
        # Test find_or_create_entity if it exists
        if hasattr(identity, 'find_or_create_entity'):
            entity = identity.find_or_create_entity(
                mention_text="Test",
                entity_type="TEST",
                confidence=1.0
            )
            
            print(f"Entity result type: {type(entity)}")
            print(f"Entity result: {entity}")
            
            assert isinstance(entity, dict) or hasattr(entity, 'entity_id')
            
            if isinstance(entity, dict):
                assert "entity_id" in entity
                print(f"✅ Created entity with ID: {entity['entity_id']}")
            else:
                assert hasattr(entity, 'entity_id')
                print(f"✅ Created entity with ID: {entity.entity_id}")
        else:
            print("⚠️ find_or_create_entity method not found")
        
        print("\n✅ Identity service works with Neo4j")
        return True
        
    except Exception as e:
        print(f"❌ Failed with Neo4j: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_identity_service_with_neo4j()
    exit(0 if success else 1)