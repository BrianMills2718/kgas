#!/usr/bin/env python3
"""Test that Identity Service properly fails without Neo4j and works with it"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, '/home/brian/projects/Digimons')

def test_identity_service_requires_neo4j():
    """Test that identity service fails properly without Neo4j"""
    # Remove Neo4j - should FAIL FAST
    os.environ.pop('NEO4J_URI', None)
    
    from src.core.service_manager import ServiceManager
    sm = ServiceManager()
    
    # MUST raise clear exception when Neo4j not available
    try:
        identity = sm.get_identity_service()
        print("❌ Should have raised exception without Neo4j")
        return False
    except RuntimeError as e:
        if "Neo4j" in str(e):
            print("✅ Correctly fails without Neo4j")
            return True
        else:
            print(f"❌ Wrong error: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error type: {type(e).__name__}: {e}")
        return False

def test_identity_service_with_neo4j():
    """Test that identity service works with Neo4j"""
    # With Neo4j configured
    os.environ['NEO4J_URI'] = 'bolt://localhost:7687'
    os.environ['NEO4J_USER'] = 'neo4j'
    os.environ['NEO4J_PASSWORD'] = 'devpassword'  # Verified working password
    
    # Force reload to pick up new environment variables
    import importlib
    from src.core import service_manager
    importlib.reload(service_manager)
    from src.core.service_manager import ServiceManager
    
    sm = ServiceManager()
    
    try:
        # Should work with Neo4j
        identity = sm.get_identity_service()
        assert identity is not None
        
        # MUST implement required methods
        mention = identity.create_mention(
            surface_form="Test",
            start_pos=0,
            end_pos=4,
            source_ref="test",
            entity_type="TEST",
            confidence=1.0
        )
        
        # Handle wrapped response format
        assert isinstance(mention, dict)
        if 'success' in mention and 'data' in mention:
            # Wrapped format
            assert mention['success'] == True
            mention_data = mention['data']
            assert "mention_id" in mention_data
        else:
            # Direct dict format
            assert "mention_id" in mention
        
        # Test find_or_create_entity if it exists
        if hasattr(identity, 'find_or_create_entity'):
            entity = identity.find_or_create_entity(
                mention_text="Test",
                entity_type="TEST",
                confidence=1.0
            )
            
            assert isinstance(entity, dict)
            # Handle wrapped response format
            if 'success' in entity and 'data' in entity:
                # Wrapped format
                assert entity['success'] == True
                entity_data = entity['data']
                assert "entity_id" in entity_data
            else:
                # Direct dict format
                assert "entity_id" in entity
        
        print("✅ Identity service works with Neo4j")
        return True
        
    except Exception as e:
        print(f"❌ Failed with Neo4j: {e}")
        return False

def main():
    """Run all tests and generate evidence"""
    results = {
        "timestamp": datetime.now().isoformat(),
        "test_name": "identity_service_requirements",
        "tests": []
    }
    
    # Test 1: Fails without Neo4j
    test1_passed = test_identity_service_requires_neo4j()
    results["tests"].append({
        "name": "fails_without_neo4j",
        "passed": test1_passed,
        "description": "Identity service should fail-fast without Neo4j"
    })
    
    # Test 2: Works with Neo4j
    test2_passed = test_identity_service_with_neo4j()
    results["tests"].append({
        "name": "works_with_neo4j",
        "passed": test2_passed,
        "description": "Identity service should work with Neo4j"
    })
    
    # Overall result
    results["status"] = "success" if all(t["passed"] for t in results["tests"]) else "failure"
    
    # Save evidence
    os.makedirs('evidence', exist_ok=True)
    with open('evidence/identity_requirements.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    if results["status"] == "success":
        print("\n✅ All identity service tests passed")
    else:
        print("\n❌ Some identity service tests failed")
    
    return results["status"] == "success"

if __name__ == "__main__":
    exit(0 if main() else 1)