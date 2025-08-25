#!/usr/bin/env python3
"""
Debug parameter mapping issues
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.theory_to_code.structured_extractor import ResolvedParameters

# Create test resolved parameters
params = ResolvedParameters(
    prospect_name="Test Prospect",
    outcomes=[100, -50],
    probabilities=[0.7, 0.3],
    reference_point=0
)

print("Resolved Parameters:")
print(params.dict())
print()

# Test the mapping logic from integrated_system
from src.theory_to_code.integrated_system import IntegratedTheorySystem

system = IntegratedTheorySystem()

# Test mapping for different function names
test_functions = [
    'value_function',
    'probability_weighting_function', 
    'prospect_evaluation'
]

for func_name in test_functions:
    print(f"\nMapping for {func_name}:")
    mapped = system._map_parameters_to_function(func_name, params)
    print(mapped)