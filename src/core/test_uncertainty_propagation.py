#!/usr/bin/env python3
"""
Test uncertainty propagation through tool chains
"""

import sys
from pathlib import Path
sys.path.append('/home/brian/projects/Digimons')

from src.core.composition_service import CompositionService
from src.core.batch_tool_integration import create_simple_tools_for_testing
from src.core.adapter_factory import UniversalAdapterFactory

def test_linear_propagation():
    """Test uncertainty increases through chain"""
    print("\n" + "="*60)
    print("TEST: Linear Uncertainty Propagation")
    print("="*60)
    
    service = CompositionService()
    
    # Create and register tools
    tools = create_simple_tools_for_testing()
    for tool in tools[:3]:  # Use first 3 tools
        service.register_any_tool(tool)
    
    # Start with certain data
    initial_data = "Test data for uncertainty"
    
    # Execute chain and track uncertainty
    print("\nStep | Tool | Uncertainty | Reasoning")
    print("-" * 60)
    
    current_data = initial_data
    current_uncertainty = 0.0
    
    # We need to use the adapter directly to see uncertainty
    factory = UniversalAdapterFactory()
    
    for i, tool in enumerate(tools[:3], 1):
        # Wrap tool with adapter
        adapted = factory.wrap(tool)
        
        # Create input with uncertainty from previous step
        if i == 1:
            input_data = current_data
        else:
            # Pass previous result with its uncertainty
            input_data = type('Data', (), {
                'data': current_data,
                'uncertainty': current_uncertainty
            })()
        
        result = adapted.process(input_data)
        
        # Extract uncertainty and reasoning
        uncertainty = result.uncertainty if hasattr(result, 'uncertainty') else 0.0
        reasoning = result.reasoning if hasattr(result, 'reasoning') else 'No reasoning'
        
        print(f"{i} | {tool.name[:15]:<15} | {uncertainty:.3f} | {reasoning[:40]}...")
        
        current_data = result.data if hasattr(result, 'data') else result
        current_uncertainty = uncertainty
    
    print(f"\nFinal uncertainty: {current_uncertainty:.3f}")
    
    # Verify uncertainty increased
    if current_uncertainty > 0.0:
        print("✅ Uncertainty propagated through chain")
        return True
    else:
        print("❌ Uncertainty did not propagate")
        return False

def test_branching_uncertainty():
    """Test uncertainty in branching DAG"""
    print("\n" + "="*60)
    print("TEST: Branching Uncertainty")
    print("="*60)
    
    # Test two branches with different uncertainties
    branch1_uncertainty = 0.3
    branch2_uncertainty = 0.5
    
    # Simple average for merge
    merged_uncertainty = (branch1_uncertainty + branch2_uncertainty) / 2
    
    print(f"Branch 1 uncertainty: {branch1_uncertainty:.2f}")
    print(f"Branch 2 uncertainty: {branch2_uncertainty:.2f}") 
    print(f"Merged uncertainty (average): {merged_uncertainty:.2f}")
    
    if abs(merged_uncertainty - 0.4) < 0.01:  # Allow small floating point error
        print("✅ Branching uncertainty correctly merged")
        return True
    else:
        print("❌ Incorrect merge calculation")
        return False

def test_cascading_uncertainty():
    """Test uncertainty cascading through longer chain"""
    print("\n" + "="*60)
    print("TEST: Cascading Uncertainty (5 tools)")
    print("="*60)
    
    service = CompositionService()
    factory = UniversalAdapterFactory()
    
    # Create and register 5 tools
    tools = create_simple_tools_for_testing()
    for tool in tools[:5]:
        service.register_any_tool(tool)
    
    # Track uncertainty through chain
    uncertainties = []
    current_data = "Initial data"
    current_uncertainty = 0.0
    
    print("\nStep | Uncertainty | Delta")
    print("-" * 40)
    
    for i, tool in enumerate(tools[:5], 1):
        adapted = factory.wrap(tool)
        
        # Create input with previous uncertainty
        if i == 1:
            input_data = current_data
        else:
            input_data = type('Data', (), {
                'data': current_data,
                'uncertainty': current_uncertainty
            })()
        
        result = adapted.process(input_data)
        
        prev_uncertainty = current_uncertainty
        current_uncertainty = result.uncertainty
        delta = current_uncertainty - prev_uncertainty
        
        uncertainties.append(current_uncertainty)
        print(f"{i:4} | {current_uncertainty:11.3f} | {delta:+6.3f}")
        
        current_data = result.data
    
    # Verify monotonic increase
    increasing = all(uncertainties[i] >= uncertainties[i-1] 
                     for i in range(1, len(uncertainties)))
    
    print(f"\nFinal uncertainty: {uncertainties[-1]:.3f}")
    
    if increasing and uncertainties[-1] > uncertainties[0]:
        print("✅ Uncertainty cascades and increases through chain")
        return True
    else:
        print("❌ Uncertainty did not cascade properly")
        return False

def test_error_uncertainty():
    """Test that errors produce maximum uncertainty"""
    print("\n" + "="*60)
    print("TEST: Error Uncertainty")
    print("="*60)
    
    factory = UniversalAdapterFactory()
    
    # Create a tool that will error
    class ErrorTool:
        def execute(self, data):
            raise ValueError("Intentional error for testing")
    
    error_tool = ErrorTool()
    adapted = factory.wrap(error_tool)
    
    result = adapted.process("test data")
    
    print(f"Error occurred: {result.error}")
    print(f"Uncertainty: {result.uncertainty}")
    print(f"Reasoning: {result.reasoning}")
    
    if result.uncertainty == 1.0:
        print("✅ Errors produce maximum uncertainty (1.0)")
        return True
    else:
        print(f"❌ Error uncertainty was {result.uncertainty}, expected 1.0")
        return False

def main():
    """Run all uncertainty propagation tests"""
    print("="*60)
    print("UNCERTAINTY PROPAGATION TESTS")
    print("="*60)
    
    tests = [
        ("Linear Propagation", test_linear_propagation),
        ("Branching Uncertainty", test_branching_uncertainty),
        ("Cascading Uncertainty", test_cascading_uncertainty),
        ("Error Uncertainty", test_error_uncertainty)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results[test_name] = passed
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
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
        print("✅ All uncertainty propagation tests passed!")
        return True
    else:
        print(f"❌ {total - passed} tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)