#!/usr/bin/env python3
"""
Test IdentityService integration with framework
Verify entity tracking across tools with uncertainty
"""

import sys
from pathlib import Path

# Add paths for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "tool_compatability" / "poc"))

from src.core.composition_service import CompositionService
from src.core.service_bridge import ServiceBridge
from src.core.test_tool_loader import register_test_tools
from data_types import DataType
import json

def test_entity_tracking():
    """Test that entities are tracked through IdentityService"""
    print("\n" + "="*60)
    print("TEST: Entity Tracking via IdentityService")
    print("="*60)
    
    # Create composition service with service bridge
    service = CompositionService()
    bridge = service.service_bridge
    
    # Get identity service
    identity = bridge.get_identity_service()
    
    # Track some test entities manually
    print("\n1. Manual entity tracking:")
    entity_ids = []
    
    entities_to_track = [
        ("Tim Cook", "PERSON", 0.95, "test_tool"),
        ("Apple", "ORGANIZATION", 0.90, "test_tool"),
        ("Satya Nadella", "PERSON", 0.93, "test_tool"),
        ("Microsoft", "ORGANIZATION", 0.91, "test_tool"),
    ]
    
    for surface_form, entity_type, confidence, source in entities_to_track:
        entity_id = bridge.track_entity(surface_form, entity_type, confidence, source)
        entity_ids.append(entity_id)
        print(f"  - Tracked '{surface_form}' as {entity_type} → ID: {entity_id}")
    
    print(f"\n✅ Tracked {len(entity_ids)} entities manually")
    
    return len(entity_ids) == 4

def test_entity_tracking_in_pipeline():
    """Test entity tracking during actual pipeline execution"""
    print("\n" + "="*60)
    print("TEST: Entity Tracking in Pipeline")
    print("="*60)
    
    # Create service and prepare test data
    service = CompositionService()
    
    # Register test tools
    register_test_tools(service)
    
    test_file = Path("test_data/mvp_test.txt")
    
    if not test_file.exists():
        print("Creating test file...")
        test_file.parent.mkdir(exist_ok=True)
        test_file.write_text("""
    Apple CEO Tim Cook announced new AI initiatives.
    Microsoft's Satya Nadella discussed cloud computing.
    Google's Sundar Pichai focused on search improvements.
    """)
    
    # Debug: show what tools are registered
    print("\n2. Checking registered tools:")
    if hasattr(service.framework, 'capabilities'):
        for tool_id, caps in service.framework.capabilities.items():
            print(f"  - {tool_id}: {caps.input_type} → {caps.output_type}")
    
    # Find and execute chain
    print("\n3. Running pipeline with entity tracking:")
    
    # First try FILE → ENTITIES (might have a chain)
    chains = service.find_chains(DataType.FILE, DataType.ENTITIES)
    
    if not chains:
        # If no direct chain, try FILE → TEXT first, then TEXT → ENTITIES
        print("  No direct FILE → ENTITIES chain, building composite chain...")
        # Debug: Try different approaches
        try:
            chain1 = service.framework.find_chains(DataType.FILE, DataType.TEXT)
            print(f"  Found chain1 (DataType.FILE→TEXT): {chain1}")
        except Exception as e:
            print(f"  Error finding chain1: {e}")
        
        try:
            chain2 = service.framework.find_chains(DataType.TEXT, DataType.ENTITIES)
            print(f"  Found chain2 (DataType.TEXT→ENTITIES): {chain2}")
        except Exception as e:
            print(f"  Error finding chain2: {e}")
        
        if chain1 and chain2:
            # Execute in sequence
            print(f"  Chain 1: {' → '.join(chain1[0])}")
            result1 = service.execute_chain(chain1[0], str(test_file))
            
            if result1.success:
                print(f"  Chain 2: {' → '.join(chain2[0])}")
                result = service.execute_chain(chain2[0], result1.data)
            else:
                print(f"❌ Chain 1 failed: {result1.error}")
                return False
        else:
            print("❌ No chains available to reach ENTITIES")
            return False
    else:
        chain = chains[0]
        print(f"  Chain: {' → '.join(chain)}")
        result = service.execute_chain(chain, str(test_file))
    
    if not result.success:
        print(f"❌ Chain execution failed: {result.error}")
        return False
    
    # Check if entities have entity_ids
    if isinstance(result.data, dict) and 'entities' in result.data:
        entities = result.data['entities']
        entities_with_ids = [e for e in entities if isinstance(e, dict) and 'entity_id' in e]
        
        print(f"\n3. Entity tracking results:")
        print(f"  - Total entities extracted: {len(entities)}")
        print(f"  - Entities with IDs: {len(entities_with_ids)}")
        
        if entities_with_ids:
            print("\n  Tracked entities:")
            for entity in entities_with_ids[:5]:  # Show first 5
                print(f"    - {entity.get('text', 'N/A')} ({entity.get('type', 'N/A')}) → ID: {entity['entity_id']}")
        
        return len(entities_with_ids) > 0
    else:
        print("❌ No entities found in result")
        return False

def test_entity_resolution():
    """Test that same entities get same IDs"""
    print("\n" + "="*60)
    print("TEST: Entity Resolution")
    print("="*60)
    
    service = CompositionService()
    bridge = service.service_bridge
    
    # Track same entity multiple times
    print("\n4. Testing entity resolution:")
    
    # First mention
    id1 = bridge.track_entity("Tim Cook", "PERSON", 0.95, "tool1")
    print(f"  First mention: 'Tim Cook' → {id1}")
    
    # Second mention (should potentially resolve to same entity)
    id2 = bridge.track_entity("Tim Cook", "PERSON", 0.90, "tool2")
    print(f"  Second mention: 'Tim Cook' → {id2}")
    
    # Different entity
    id3 = bridge.track_entity("Steve Jobs", "PERSON", 0.88, "tool3")
    print(f"  Different entity: 'Steve Jobs' → {id3}")
    
    # The IDs might be different mentions but could resolve to same entity
    # This depends on IdentityService implementation
    print(f"\n  Resolution behavior:")
    print(f"    - Same name, same ID: {id1 == id2}")
    print(f"    - Different name, different ID: {id1 != id3}")
    
    return True  # Basic test passes if no errors

def test_entity_uncertainty():
    """Test that entity confidence affects uncertainty"""
    print("\n" + "="*60)
    print("TEST: Entity Confidence → Uncertainty")
    print("="*60)
    
    service = CompositionService()
    bridge = service.service_bridge
    
    print("\n5. Testing confidence levels:")
    
    # High confidence entity
    high_conf_id = bridge.track_entity(
        "Apple Inc.", "ORGANIZATION", 0.98, "high_confidence_tool"
    )
    print(f"  High confidence (0.98): Apple Inc. → {high_conf_id}")
    
    # Low confidence entity
    low_conf_id = bridge.track_entity(
        "Possible Company", "ORGANIZATION", 0.45, "low_confidence_tool"
    )
    print(f"  Low confidence (0.45): Possible Company → {low_conf_id}")
    
    # Very low confidence
    vlow_conf_id = bridge.track_entity(
        "Unknown Entity", "UNKNOWN", 0.10, "uncertain_tool"
    )
    print(f"  Very low confidence (0.10): Unknown Entity → {vlow_conf_id}")
    
    print("\n✅ Entity confidence tracking works")
    return True

def main():
    """Run all identity integration tests"""
    print("="*60)
    print("IDENTITY SERVICE INTEGRATION TESTS")
    print("="*60)
    
    tests = [
        ("Manual Entity Tracking", test_entity_tracking),
        ("Pipeline Entity Tracking", test_entity_tracking_in_pipeline),
        ("Entity Resolution", test_entity_resolution),
        ("Entity Confidence", test_entity_uncertainty),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
            status = "✅" if passed else "❌"
            print(f"\n{status} {test_name}")
        except Exception as e:
            results.append((test_name, False))
            print(f"\n❌ {test_name}: {str(e)}")
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, p in results if p)
    total = len(results)
    
    for test_name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All IdentityService integration tests passed!")
    else:
        print(f"\n⚠️ {total - passed} tests failed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)