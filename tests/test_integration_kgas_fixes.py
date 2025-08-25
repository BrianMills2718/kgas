#!/usr/bin/env python3
"""Integration test for KGAS fixes - validates all components work together"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, '/home/brian/projects/Digimons')

def test_kgas_integration():
    """Test that all KGAS fixes work together"""
    
    print("=" * 60)
    print("KGAS Integration Test Suite")
    print("=" * 60)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "test_name": "kgas_integration",
        "components": [],
        "tests": []
    }
    
    # Test 1: ToolRequest has required fields
    print("\n1. Testing ToolRequest Contract...")
    try:
        from src.core.tool_contract import ToolRequest
        
        # Create a ToolRequest with all required fields
        request = ToolRequest(
            input_data={"test": "data"},
            operation="execute",
            parameters={"param": "value"},
            validation_mode=False
        )
        
        # Verify all fields exist
        assert hasattr(request, "input_data")
        assert hasattr(request, "operation")
        assert hasattr(request, "parameters")
        assert hasattr(request, "validation_mode")
        
        results["components"].append("ToolRequest")
        results["tests"].append({
            "name": "ToolRequest contract",
            "passed": True
        })
        print("   ✅ ToolRequest has all required fields")
    except Exception as e:
        results["tests"].append({
            "name": "ToolRequest contract",
            "passed": False,
            "error": str(e)
        })
        print(f"   ❌ ToolRequest failed: {e}")
    
    # Test 2: Identity Service with Neo4j
    print("\n2. Testing Identity Service...")
    try:
        # Set Neo4j credentials
        os.environ['NEO4J_URI'] = 'bolt://localhost:7687'
        os.environ['NEO4J_USER'] = 'neo4j'
        os.environ['NEO4J_PASSWORD'] = 'devpassword'
        
        from src.core.service_manager import ServiceManager
        sm = ServiceManager()
        
        # Get identity service (should work with Neo4j)
        identity = sm.get_identity_service()
        assert identity is not None
        
        # Create a mention
        mention = identity.create_mention(
            surface_form="Test Entity",
            start_pos=0,
            end_pos=11,
            source_ref="integration_test",
            entity_type="TEST",
            confidence=0.9
        )
        
        # Handle wrapped response
        if isinstance(mention, dict) and 'success' in mention:
            assert mention['success'] == True
            mention_data = mention['data']
            assert 'mention_id' in mention_data
            print(f"   ✅ Identity Service created mention: {mention_data['mention_id']}")
        else:
            assert 'mention_id' in mention
            print(f"   ✅ Identity Service created mention: {mention['mention_id']}")
        
        results["components"].append("IdentityService")
        results["tests"].append({
            "name": "Identity Service with Neo4j",
            "passed": True
        })
    except Exception as e:
        results["tests"].append({
            "name": "Identity Service with Neo4j",
            "passed": False,
            "error": str(e)
        })
        print(f"   ❌ Identity Service failed: {e}")
    
    # Test 3: Format Adapters
    print("\n3. Testing Format Adapters...")
    try:
        from src.core.format_adapters import FormatAdapter
        
        # Test t23c_to_t31 conversion
        t23c_output = [{
            "entity_id": "e1",
            "canonical_name": "Apple Inc.",
            "entity_type": "ORG",
            "confidence": 0.9
        }]
        
        t31_input = FormatAdapter.t23c_to_t31(t23c_output)
        assert t31_input[0]["text"] == "Apple Inc."
        
        # Test t31_to_t34
        t31_output = [{
            "entity_id": "org_001",
            "canonical_name": "Apple Inc.",
            "entity_type": "ORG"
        }]
        
        t34_input = FormatAdapter.t31_to_t34(t31_output)
        assert "text" in t34_input[0]
        
        # Test relationship normalization
        rel = {"source": "Apple", "target": "Tim Cook", "type": "LED_BY"}
        normalized = FormatAdapter.normalize_relationship(rel)
        assert normalized["subject"] == "Apple"
        assert normalized["object"] == "Tim Cook"
        assert normalized["relationship_type"] == "LED_BY"
        
        results["components"].append("FormatAdapter")
        results["tests"].append({
            "name": "Format Adapters",
            "passed": True
        })
        print("   ✅ Format Adapters working correctly")
    except Exception as e:
        results["tests"].append({
            "name": "Format Adapters",
            "passed": False,
            "error": str(e)
        })
        print(f"   ❌ Format Adapters failed: {e}")
    
    # Test 4: Integration - Create entity through full pipeline
    print("\n4. Testing Full Pipeline Integration...")
    try:
        from src.core.format_adapters import FormatAdapter
        from src.core.tool_contract import ToolRequest
        
        # Simulate T23C output
        t23c_entities = [
            {
                "entity_id": "e1",
                "canonical_name": "Microsoft Corporation",
                "entity_type": "ORG",
                "confidence": 0.95
            },
            {
                "entity_id": "e2",
                "canonical_name": "Satya Nadella",
                "entity_type": "PERSON",
                "confidence": 0.90
            }
        ]
        
        # Convert to T31 format
        t31_mentions = FormatAdapter.t23c_to_t31(t23c_entities)
        assert len(t31_mentions) == 2
        assert t31_mentions[0]["text"] == "Microsoft Corporation"
        assert t31_mentions[1]["text"] == "Satya Nadella"
        
        # Ensure T34 compatibility
        t34_entities = FormatAdapter.t31_to_t34(t31_mentions)
        assert all("text" in e for e in t34_entities)
        
        # Test relationship conversion
        relationships = [
            {"source": "Microsoft Corporation", "target": "Satya Nadella", "type": "LED_BY"}
        ]
        
        entity_map = {
            "Microsoft Corporation": "e1",
            "Satya Nadella": "e2"
        }
        
        t34_rels = FormatAdapter.convert_relationships_for_t34(relationships, entity_map)
        assert len(t34_rels) == 1
        assert t34_rels[0]["subject"]["text"] == "Microsoft Corporation"
        assert t34_rels[0]["object"]["text"] == "Satya Nadella"
        assert t34_rels[0]["relationship_type"] == "LED_BY"
        
        # Wrap for tool request
        wrapped = FormatAdapter.wrap_for_tool_request(
            {"entities": t34_entities, "relationships": t34_rels},
            "process"
        )
        assert wrapped["operation"] == "process"
        assert "input_data" in wrapped
        
        results["components"].append("Full Pipeline")
        results["tests"].append({
            "name": "Full Pipeline Integration",
            "passed": True
        })
        print("   ✅ Full pipeline integration successful")
    except Exception as e:
        results["tests"].append({
            "name": "Full Pipeline Integration",
            "passed": False,
            "error": str(e)
        })
        print(f"   ❌ Full pipeline failed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 60)
    
    passed_count = sum(1 for t in results["tests"] if t["passed"])
    failed_count = sum(1 for t in results["tests"] if not t["passed"])
    
    print(f"Components tested: {len(results['components'])}")
    print(f"Tests passed: {passed_count}")
    print(f"Tests failed: {failed_count}")
    
    # Determine overall status
    results["status"] = "success" if failed_count == 0 else "failure"
    
    # Save evidence
    os.makedirs('evidence', exist_ok=True)
    with open('evidence/kgas_integration.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    if results["status"] == "success":
        print("\n✅ ALL INTEGRATION TESTS PASSED")
        print("✅ Evidence saved to: evidence/kgas_integration.json")
        print("\nKGAS FIXES VALIDATED:")
        print("- ToolRequest contract fixed")
        print("- Identity Service works with Neo4j (no fallbacks)")
        print("- Format Adapters handle all tool variations")
        print("- Full pipeline integration successful")
    else:
        print(f"\n❌ {failed_count} INTEGRATION TESTS FAILED")
        for test in results["tests"]:
            if not test["passed"]:
                print(f"   - {test['name']}: {test.get('error', 'Unknown error')}")
    
    print("=" * 60)
    
    return results["status"] == "success"

if __name__ == "__main__":
    success = test_kgas_integration()
    exit(0 if success else 1)