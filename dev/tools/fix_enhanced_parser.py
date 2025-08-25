#!/usr/bin/env python3
"""
Fix Enhanced Parser Issues

Based on comprehensive testing, fix the core issues in enhanced parser
rather than adding SymPy complexity.
"""

import re

def test_exp_conversion():
    """Test what's going wrong with exp() conversion"""
    
    test_cases = [
        "exp(x)",
        "exp(x) - 1", 
        "exp(sin(x))",
        "log(exp(x))",
        "x * exp(-x^2)"
    ]
    
    supported_functions = {
        'log': 'math.log',
        'ln': 'math.log', 
        'log10': 'math.log10',
        'sqrt': 'math.sqrt',
        'exp': 'math.exp',
        'sin': 'math.sin',
        'cos': 'math.cos',
        'tan': 'math.tan',
    }
    
    for expr in test_cases:
        print(f"\nOriginal: {expr}")
        
        # Current conversion logic
        python_expr = expr.strip()
        
        # Power notation first
        python_expr = re.sub(r'(\w+)\^([^,\s)]+)', r'(\1)**(\2)', python_expr)
        print(f"After power: {python_expr}")
        
        # Mathematical functions
        for math_func, python_func in supported_functions.items():
            pattern = rf'\b{math_func}\('
            python_expr = re.sub(pattern, f'{python_func}(', python_expr)
        print(f"After functions: {python_expr}")
        
        # Test if it's valid Python
        try:
            # Replace variables for testing
            test_expr = python_expr.replace('x', '1.0')
            test_code = f"import math; result = {test_expr}"
            exec(test_code)
            print("✅ Valid Python")
        except Exception as e:
            print(f"❌ Error: {e}")


def find_problematic_patterns():
    """Find what patterns are causing issues"""
    
    # Test specific failing cases from comprehensive test
    failing_cases = [
        "f(x) = exp(x)",
        "f(x) = exp(x) - 1", 
        "f(x) = log(exp(x))",
        "f(x) = x * exp(-x^2)"
    ]
    
    for case in failing_cases:
        print(f"\n=== Testing: {case} ===")
        
        # Extract expression part
        if '=' in case:
            left, right = case.split('=', 1)
            expr = right.strip()
        else:
            expr = case
            
        print(f"Expression: {expr}")
        
        # Apply transformations step by step
        python_expr = expr
        
        # Step 1: Power notation
        python_expr = re.sub(r'(\w+)\^([^,\s)]+)', r'(\1)**(\2)', python_expr)
        print(f"Step 1 (power): {python_expr}")
        
        # Step 2: exp function
        python_expr = re.sub(r'\bexp\(', 'math.exp(', python_expr)
        print(f"Step 2 (exp): {python_expr}")
        
        # Step 3: Other functions if present
        python_expr = re.sub(r'\blog\(', 'math.log(', python_expr)
        print(f"Step 3 (log): {python_expr}")
        
        # Test execution
        try:
            test_expr = python_expr.replace('x', '1.0')
            test_code = f"import math; result = {test_expr}"
            print(f"Test code: {test_code}")
            exec(test_code)
            print("✅ Success")
        except Exception as e:
            print(f"❌ Failed: {e}")
            
            # Debug further
            print("Debugging character by character:")
            for i, char in enumerate(test_expr):
                print(f"{i}: '{char}' (ord {ord(char)})")


if __name__ == "__main__":
    print("🔍 DEBUGGING ENHANCED PARSER ISSUES")
    print("="*50)
    
    test_exp_conversion()
    
    print("\n" + "="*50)
    find_problematic_patterns()