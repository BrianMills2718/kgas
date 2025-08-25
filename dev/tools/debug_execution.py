#!/usr/bin/env python3
"""
Debug the execution failures
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.theory_to_code import IntegratedTheorySystem
import json

# Initialize system
system = IntegratedTheorySystem()

# Load theory
schema_path = "config/schemas/prospect_theory_schema.json"
system.load_and_compile_theory(schema_path)

# Get the generated module code
module_code = system.generated_theories['prospect_theory']['module_code']
print("Generated Module Code:")
print("=" * 60)
print(module_code)
print("=" * 60)

# Test direct execution
from src.theory_to_code.simple_executor import SimpleExecutor

executor = SimpleExecutor()

# Test a simple function call
print("\nTesting direct execution:")
result = executor.execute_module_function(
    module_code,
    'value_function',
    {'x': 100, 'reference_point': 0}
)

print(f"Success: {result.success}")
if result.error:
    print(f"Error: {result.error}")