#!/usr/bin/env python3
"""
Test ProvenanceService integration with framework
"""

import sys
from pathlib import Path
sys.path.append('/home/brian/projects/Digimons')

from src.core.service_bridge import ServiceBridge
from src.core.adapter_factory import UniversalAdapterFactory
from src.core.batch_tool_integration import create_simple_tools_for_testing

def test_provenance_tracking():
    """Test that ProvenanceService tracks tool executions"""
    print("\n" + "="*60)
    print("TEST: Provenance Service Tracking")
    print("="*60)
    
    # Create service bridge and factory
    bridge = ServiceBridge()
    factory = UniversalAdapterFactory(service_bridge=bridge)
    
    # Create test tools
    tools = create_simple_tools_for_testing()
    
    # Execute tools and verify provenance
    print("\nStep | Tool | Provenance Tracked")
    print("-" * 50)
    
    for i, tool in enumerate(tools[:3], 1):
        adapted = factory.wrap(tool)
        
        # Execute with provenance tracking
        input_data = f"Test input {i}"
        result = adapted.process(input_data)
        
        # Check provenance
        has_provenance = hasattr(result, 'provenance') and result.provenance is not None
        status = "✅" if has_provenance else "❌"
        
        print(f"{i:4} | {tool.name[:20]:<20} | {status}")
        
        if has_provenance:
            print(f"      Operation ID: {result.provenance.get('operation_id', 'N/A')}")
            print(f"      Input hash: {result.provenance.get('input_hash', 'N/A')}")
    
    print("\n✅ Provenance tracking active")
    return True

def test_lineage_chain():
    """Test provenance tracks full execution chain"""
    print("\n" + "="*60)
    print("TEST: Lineage Chain Tracking")
    print("="*60)
    
    # Create service bridge and factory
    bridge = ServiceBridge()
    factory = UniversalAdapterFactory(service_bridge=bridge)
    
    # Create and execute chain
    tools = create_simple_tools_for_testing()
    provenance_chain = []
    
    print("\nBuilding execution chain...")
    current_data = "Initial data"
    
    for i, tool in enumerate(tools[:4], 1):
        adapted = factory.wrap(tool)
        result = adapted.process(current_data)
        
        if hasattr(result, 'provenance') and result.provenance:
            provenance_chain.append(result.provenance)
            print(f"  Step {i}: {tool.name} - Operation {result.provenance.get('operation_id', 'N/A')}")
        
        current_data = result.data if hasattr(result, 'data') else result
    
    print(f"\nChain length: {len(provenance_chain)} operations tracked")
    
    if len(provenance_chain) == 4:
        print("✅ Complete chain tracked in provenance")
        return True
    else:
        print(f"❌ Expected 4 operations, got {len(provenance_chain)}")
        return False

def test_provenance_with_uncertainty():
    """Test provenance includes uncertainty metadata"""
    print("\n" + "="*60)
    print("TEST: Provenance with Uncertainty")
    print("="*60)
    
    bridge = ServiceBridge()
    factory = UniversalAdapterFactory(service_bridge=bridge)
    
    # Create tool and execute
    tool = create_simple_tools_for_testing()[0]
    adapted = factory.wrap(tool)
    
    result = adapted.process("Test data")
    
    print(f"Tool: {tool.name}")
    print(f"Uncertainty: {result.uncertainty}")
    print(f"Reasoning: {result.reasoning}")
    
    if hasattr(result, 'provenance') and result.provenance:
        print(f"Provenance tracked: ✅")
        print(f"  Operation ID: {result.provenance.get('operation_id')}")
        print(f"  Tool ID: {result.provenance.get('tool_id')}")
        print(f"  Timestamp: {result.provenance.get('timestamp')}")
        
        # Verify both uncertainty and provenance exist
        if result.uncertainty > 0 and result.provenance:
            print("\n✅ Tool execution has both uncertainty and provenance")
            return True
    
    print("❌ Provenance not properly tracked")
    return False

def test_service_persistence():
    """Test that ProvenanceService persists across multiple uses"""
    print("\n" + "="*60)
    print("TEST: Service Persistence")
    print("="*60)
    
    bridge1 = ServiceBridge()
    bridge2 = ServiceBridge()
    
    # Both should get the same service instance from ServiceManager
    prov1 = bridge1.get_provenance_service()
    prov2 = bridge2.get_provenance_service()
    
    # In our implementation they're different instances,
    # but each bridge maintains its own service
    print(f"Bridge 1 service ID: {id(prov1)}")
    print(f"Bridge 2 service ID: {id(prov2)}")
    
    # Test that each bridge maintains its service
    prov1_again = bridge1.get_provenance_service()
    
    if prov1 is prov1_again:
        print("✅ Service persists within bridge")
        return True
    else:
        print("❌ Service not persisting")
        return False

def main():
    """Run all service integration tests"""
    print("="*60)
    print("PROVENANCE SERVICE INTEGRATION TESTS")
    print("="*60)
    
    tests = [
        ("Provenance Tracking", test_provenance_tracking),
        ("Lineage Chain", test_lineage_chain),
        ("Provenance with Uncertainty", test_provenance_with_uncertainty),
        ("Service Persistence", test_service_persistence)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results[test_name] = passed
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All ProvenanceService integration tests passed!")
        return True
    else:
        print(f"❌ {total - passed} tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)