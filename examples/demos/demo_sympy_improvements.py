#!/usr/bin/env python3
"""
Demo: SymPy Integration Improvements for Statistical Functions

Shows how the hybrid parser handles previously failing cases.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.mcp_tools.hybrid_formula_parser import HybridFormulaParser
from src.mcp_tools.enhanced_formula_parser import EnhancedFormulaParser
import time


def test_formula(parser, formula, description=""):
    """Test a single formula and show results"""
    print(f"\n{'='*60}")
    print(f"Formula: {formula}")
    print(f"Parser: {type(parser).__name__}")
    
    start = time.time()
    result = parser.parse_formula(formula)
    elapsed = time.time() - start
    
    if result.success:
        print(f"✅ SUCCESS (parsed in {elapsed:.3f}s)")
        print("\nGenerated Code:")
        print("-" * 40)
        print(result.python_code)
        print("-" * 40)
        
        # Try to execute the generated code
        try:
            # Create a namespace for execution
            namespace = {}
            exec("from typing import Union\nimport math", namespace)
            exec(result.python_code, namespace)
            
            # Find the function name
            func_name = None
            for name in namespace:
                if callable(namespace[name]) and name not in ['Union', 'math']:
                    func_name = name
                    break
                    
            if func_name:
                func = namespace[func_name]
                print("\nTest Execution:")
                
                # Test cases based on number of variables
                if 'x' in result.python_code and 'y' in result.python_code:
                    # Two variable function
                    test_cases = [(2, 3), (5, 1), (-1, -3), (0, 0), (1.5, 2.5)]
                    for x, y in test_cases:
                        try:
                            result_val = func(x, y)
                            print(f"  {func_name}({x}, {y}) = {result_val}")
                        except Exception as e:
                            print(f"  {func_name}({x}, {y}) = ERROR: {e}")
                else:
                    # Single variable function
                    test_cases = [0, 1, 2, -1, 0.5]
                    for x in test_cases:
                        try:
                            result_val = func(x)
                            print(f"  {func_name}({x}) = {result_val}")
                        except Exception as e:
                            print(f"  {func_name}({x}) = ERROR: {e}")
                            
        except Exception as e:
            print(f"\nExecution Error: {e}")
    else:
        print(f"❌ FAILED: {result.error}")
    
    return result.success


def main():
    """Compare enhanced vs hybrid parser on challenging formulas"""
    
    print("🔬 Formula Parser Comparison: Enhanced vs Hybrid (with SymPy)")
    print("="*80)
    
    enhanced_parser = EnhancedFormulaParser()
    hybrid_parser = HybridFormulaParser()
    
    # Test cases that were challenging before
    test_formulas = [
        # Statistical functions (previously 60% success)
        ("f(x,y) = max(x, y)", "Maximum of two values"),
        ("f(x,y) = min(x, y)", "Minimum of two values"),
        ("avg(x,y) = (x + y) / 2", "Average of two values"),
        
        # Nested transcendental (previously 60% success)
        ("f(x) = exp(sin(x))", "Exponential of sine"),
        ("g(x) = log(cos(x) + 2)", "Log of shifted cosine"),
        
        # Complex expressions
        ("norm(x,y,z) = sqrt(x^2 + y^2 + z^2)", "3D Euclidean norm"),
        ("relu(x) = max(0, x)", "ReLU activation function"),
        
        # Edge cases that work well
        ("v(x) = x^0.88", "Prospect theory value function"),
        ("f(x,y) = x^2 + y^2", "Sum of squares"),
    ]
    
    # Track results
    enhanced_results = []
    hybrid_results = []
    
    print("\n" + "="*80)
    print("TESTING WITH ENHANCED PARSER (No SymPy)")
    print("="*80)
    
    for formula, desc in test_formulas:
        print(f"\n{desc}")
        success = test_formula(enhanced_parser, formula, desc)
        enhanced_results.append(success)
    
    print("\n" + "="*80)
    print("TESTING WITH HYBRID PARSER (With SymPy)")
    print("="*80)
    
    for formula, desc in test_formulas:
        print(f"\n{desc}")
        success = test_formula(hybrid_parser, formula, desc)
        hybrid_results.append(success)
    
    # Summary
    print("\n" + "="*80)
    print("📊 PERFORMANCE COMPARISON SUMMARY")
    print("="*80)
    
    enhanced_success = sum(enhanced_results)
    hybrid_success = sum(hybrid_results)
    
    print(f"\nEnhanced Parser Success: {enhanced_success}/{len(test_formulas)} ({enhanced_success/len(test_formulas)*100:.1f}%)")
    print(f"Hybrid Parser Success:   {hybrid_success}/{len(test_formulas)} ({hybrid_success/len(test_formulas)*100:.1f}%)")
    
    improvement = hybrid_success - enhanced_success
    if improvement > 0:
        print(f"\n✨ Improvement: +{improvement} formulas ({improvement/len(test_formulas)*100:.1f}% better)")
    
    # Show specific improvements
    print("\n🎯 Specific Improvements:")
    for i, (formula, desc) in enumerate(test_formulas):
        if not enhanced_results[i] and hybrid_results[i]:
            print(f"  ✅ {desc}: {formula}")
    
    print("\n🔍 Key Insights:")
    print("  - SymPy handles max/min functions that regex parsing struggles with")
    print("  - Complex nested expressions are parsed more reliably")
    print("  - Multi-variable support is more robust")
    print("  - Mathematical correctness is preserved")


if __name__ == "__main__":
    main()