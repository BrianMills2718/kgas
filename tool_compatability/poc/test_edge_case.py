#!/usr/bin/env python3
"""Test edge case that might be causing failure"""

import sys
from dotenv import load_dotenv
load_dotenv('/home/brian/projects/Digimons/.env')

sys.path.append('/home/brian/projects/Digimons')
sys.path.append('/home/brian/projects/Digimons/tool_compatability/poc/vertical_slice')

from src.tools.neo4j_graph_builder import Neo4jGraphBuilder
from adapters.universal_adapter import UniversalAdapter

builder = Neo4jGraphBuilder()
adapted = UniversalAdapter(builder, "neo4j_graph_builder", "process")

# Test different input formats that might occur in pipeline
test_cases = [
    # Case 1: Empty entities
    {'entities': [], 'source_text': 'test'},
    
    # Case 2: None entities
    {'entities': None},
    
    # Case 3: Missing entities key
    {'source_text': 'test'},
    
    # Case 4: Wrapped in another dict (double wrapping)
    {'data': {'entities': [{'text': 'Test', 'type': 'PERSON'}]}},
]

for i, test_input in enumerate(test_cases, 1):
    print(f"\nTest case {i}: {str(test_input)[:50]}...")
    
    # Direct call
    direct_result = builder.process(test_input)
    print(f"  Direct: success={direct_result.get('success')}, nodes={direct_result.get('nodes_created', 0)}")
    
    # Through adapter
    try:
        adapted_result = adapted.process(test_input)
        print(f"  Adapted: success={adapted_result.get('success')}")
    except Exception as e:
        print(f"  Adapted failed: {e.__class__.__name__}")
        
        # This is the issue - when builder returns success=False,
        # the adapter tries to assess uncertainty for a failed operation