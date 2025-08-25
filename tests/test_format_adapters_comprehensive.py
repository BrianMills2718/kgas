#!/usr/bin/env python3
"""Comprehensive test for format adapters - all functions"""

import sys
import json
from datetime import datetime

sys.path.insert(0, '/home/brian/projects/Digimons')

def test_all_format_adapter_functions():
    """Test all FormatAdapter functions comprehensively"""
    from src.core.format_adapters import FormatAdapter
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "test_name": "format_adapters_comprehensive",
        "functions_tested": [],
        "tests_passed": [],
        "tests_failed": []
    }
    
    print("=" * 60)
    print("Testing Format Adapters Comprehensively")
    print("=" * 60)
    
    # Test 1: t23c_to_t31
    print("\n1. Testing t23c_to_t31...")
    try:
        t23c_output = [
            {
                "entity_id": "e1",
                "canonical_name": "Apple Inc.",
                "entity_type": "ORG",
                "confidence": 0.9,
                "extra_field": "preserved"
            },
            {
                "entity_id": "e2",
                "canonical_name": "Tim Cook",
                "entity_type": "PERSON",
                "confidence": 0.85
            }
        ]
        
        t31_input = FormatAdapter.t23c_to_t31(t23c_output)
        
        assert len(t31_input) == 2
        assert t31_input[0]["text"] == "Apple Inc."
        assert t31_input[0]["entity_type"] == "ORG"
        assert t31_input[0]["confidence"] == 0.9
        assert t31_input[0]["t23c_entity_id"] == "e1"
        assert t31_input[0]["t23c_extra_field"] == "preserved"
        
        results["functions_tested"].append("t23c_to_t31")
        results["tests_passed"].append("t23c_to_t31 conversion")
        print("   ✅ t23c_to_t31 conversion passed")
    except Exception as e:
        results["tests_failed"].append(f"t23c_to_t31: {e}")
        print(f"   ❌ t23c_to_t31 failed: {e}")
    
    # Test 2: t31_to_t34
    print("\n2. Testing t31_to_t34...")
    try:
        t31_output = [
            {
                "entity_id": "org_001",
                "canonical_name": "Apple Inc.",
                "entity_type": "ORG"
                # Note: NO 'text' field
            },
            {
                "entity_id": "person_001",
                "text": "Tim Cook",  # Has text field
                "canonical_name": "Timothy D. Cook",
                "entity_type": "PERSON"
            }
        ]
        
        t34_input = FormatAdapter.t31_to_t34(t31_output)
        
        assert len(t34_input) == 2
        assert t34_input[0]["text"] == "Apple Inc."  # Added from canonical_name
        assert t34_input[1]["text"] == "Tim Cook"  # Preserved existing
        
        results["functions_tested"].append("t31_to_t34")
        results["tests_passed"].append("t31_to_t34 text field addition")
        print("   ✅ t31_to_t34 text field addition passed")
    except Exception as e:
        results["tests_failed"].append(f"t31_to_t34: {e}")
        print(f"   ❌ t31_to_t34 failed: {e}")
    
    # Test 3: normalize_relationship
    print("\n3. Testing normalize_relationship...")
    try:
        variations = [
            {"source": "Apple", "target": "Tim Cook", "type": "LED_BY"},
            {"subject": "Microsoft", "object": "Satya Nadella", "relationship_type": "CEO_OF"},
            {"source_entity": "Google", "target_entity": "Sundar Pichai", "relationship": "MANAGED_BY"},
            {"subject": "Amazon", "object": "Andy Jassy", "predicate": "HAS_CEO"}
        ]
        
        for i, rel in enumerate(variations):
            normalized = FormatAdapter.normalize_relationship(rel)
            assert "subject" in normalized
            assert "object" in normalized
            assert "relationship_type" in normalized
            assert "confidence" in normalized
            assert normalized["confidence"] == 0.5  # Default value
        
        results["functions_tested"].append("normalize_relationship")
        results["tests_passed"].append(f"normalize_relationship ({len(variations)} variations)")
        print(f"   ✅ normalize_relationship passed for {len(variations)} variations")
    except Exception as e:
        results["tests_failed"].append(f"normalize_relationship: {e}")
        print(f"   ❌ normalize_relationship failed: {e}")
    
    # Test 4: wrap_for_tool_request
    print("\n4. Testing wrap_for_tool_request...")
    try:
        data = {"entities": ["Apple", "Tim Cook"]}
        wrapped = FormatAdapter.wrap_for_tool_request(data, "process")
        
        assert wrapped["input_data"] == data
        assert wrapped["operation"] == "process"
        assert "parameters" in wrapped
        assert "validation_mode" in wrapped
        
        results["functions_tested"].append("wrap_for_tool_request")
        results["tests_passed"].append("wrap_for_tool_request")
        print("   ✅ wrap_for_tool_request passed")
    except Exception as e:
        results["tests_failed"].append(f"wrap_for_tool_request: {e}")
        print(f"   ❌ wrap_for_tool_request failed: {e}")
    
    # Test 5: unwrap_tool_response
    print("\n5. Testing unwrap_tool_response...")
    try:
        # Test wrapped format
        wrapped_response = {
            "success": True,
            "data": {"result": "processed"}
        }
        unwrapped = FormatAdapter.unwrap_tool_response(wrapped_response)
        assert unwrapped == {"result": "processed"}
        
        # Test direct format
        direct_response = {"result": "direct"}
        unwrapped = FormatAdapter.unwrap_tool_response(direct_response)
        assert unwrapped == {"result": "direct"}
        
        # Test error case
        error_response = {
            "success": False,
            "error": "Test error"
        }
        error_raised = False
        try:
            FormatAdapter.unwrap_tool_response(error_response)
        except RuntimeError as e:
            error_raised = True
            assert "Test error" in str(e)
        
        assert error_raised, "Should have raised RuntimeError for failed response"
        
        results["functions_tested"].append("unwrap_tool_response")
        results["tests_passed"].append("unwrap_tool_response (3 cases)")
        print("   ✅ unwrap_tool_response passed (wrapped, direct, error)")
    except Exception as e:
        results["tests_failed"].append(f"unwrap_tool_response: {e}")
        print(f"   ❌ unwrap_tool_response failed: {e}")
    
    # Test 6: convert_entity_mentions_to_t31
    print("\n6. Testing convert_entity_mentions_to_t31...")
    try:
        mentions = [
            {"surface_form": "Apple", "type": "ORG", "start_pos": 0, "end_pos": 5},
            {"text": "Tim Cook", "entity_type": "PERSON", "start": 10, "end": 18},
            {"canonical_name": "Microsoft", "entity_type": "ORG", "confidence": 0.95}
        ]
        
        t31_mentions = FormatAdapter.convert_entity_mentions_to_t31(mentions)
        
        assert len(t31_mentions) == 3
        assert t31_mentions[0]["text"] == "Apple"
        assert t31_mentions[1]["text"] == "Tim Cook"
        assert t31_mentions[2]["text"] == "Microsoft"
        assert all("entity_type" in m for m in t31_mentions)
        assert all("confidence" in m for m in t31_mentions)
        
        results["functions_tested"].append("convert_entity_mentions_to_t31")
        results["tests_passed"].append("convert_entity_mentions_to_t31")
        print("   ✅ convert_entity_mentions_to_t31 passed")
    except Exception as e:
        results["tests_failed"].append(f"convert_entity_mentions_to_t31: {e}")
        print(f"   ❌ convert_entity_mentions_to_t31 failed: {e}")
    
    # Test 7: convert_relationships_for_t34
    print("\n7. Testing convert_relationships_for_t34...")
    try:
        relationships = [
            {"source": "Apple", "target": "Tim Cook", "type": "LED_BY"},
            {"subject": "Microsoft", "object": "Satya Nadella", "relationship_type": "CEO_OF"}
        ]
        
        entity_map = {
            "Apple": "entity_apple",
            "Tim Cook": "entity_cook",
            "Microsoft": "entity_msft",
            "Satya Nadella": "entity_nadella"
        }
        
        t34_rels = FormatAdapter.convert_relationships_for_t34(relationships, entity_map)
        
        assert len(t34_rels) == 2
        
        # Check first relationship
        assert t34_rels[0]["subject"]["text"] == "Apple"
        assert t34_rels[0]["subject"]["entity_id"] == "entity_apple"
        assert t34_rels[0]["object"]["text"] == "Tim Cook"
        assert t34_rels[0]["object"]["entity_id"] == "entity_cook"
        assert t34_rels[0]["relationship_type"] == "LED_BY"
        
        # Check second relationship
        assert t34_rels[1]["subject"]["text"] == "Microsoft"
        assert t34_rels[1]["subject"]["entity_id"] == "entity_msft"
        assert t34_rels[1]["relationship_type"] == "CEO_OF"
        
        results["functions_tested"].append("convert_relationships_for_t34")
        results["tests_passed"].append("convert_relationships_for_t34")
        print("   ✅ convert_relationships_for_t34 passed")
    except Exception as e:
        results["tests_failed"].append(f"convert_relationships_for_t34: {e}")
        print(f"   ❌ convert_relationships_for_t34 failed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Functions tested: {len(results['functions_tested'])}")
    print(f"Tests passed: {len(results['tests_passed'])}")
    print(f"Tests failed: {len(results['tests_failed'])}")
    
    # Determine overall status
    results["status"] = "success" if len(results["tests_failed"]) == 0 else "failure"
    
    # Save evidence
    os.makedirs('evidence', exist_ok=True)
    with open('evidence/format_adapters_comprehensive.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    if results["status"] == "success":
        print("\n✅ ALL FORMAT ADAPTER TESTS PASSED")
        print("✅ Evidence saved to: evidence/format_adapters_comprehensive.json")
    else:
        print(f"\n❌ {len(results['tests_failed'])} TESTS FAILED")
        for failure in results["tests_failed"]:
            print(f"   - {failure}")
    
    return results["status"] == "success"

if __name__ == "__main__":
    import os
    success = test_all_format_adapter_functions()
    exit(0 if success else 1)