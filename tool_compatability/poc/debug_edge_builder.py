#!/usr/bin/env python3
"""Debug what t34_edge_builder outputs"""

import sys
from dotenv import load_dotenv
load_dotenv('/home/brian/projects/Digimons/.env')

sys.path.append('/home/brian/projects/Digimons')
sys.path.append('/home/brian/projects/Digimons/tool_compatability/poc/vertical_slice')

from archive.archived.legacy_tools_2025_07_23.t34_edge_builder import EdgeBuilder
from adapters.universal_adapter import UniversalAdapter

print("=== Debugging t34_edge_builder Output ===\n")

# Create edge builder
edge_builder = EdgeBuilder()
adapted_edge = UniversalAdapter(edge_builder, "t34_edge_builder")

# Test input (simulating gemini extractor output)
test_input = {
    'entities': [
        {'text': 'Brian Chhun', 'type': 'PERSON', 'confidence': 0.95},
        {'text': 'KGAS', 'type': 'SYSTEM', 'confidence': 0.9}
    ],
    'source_text': 'Brian Chhun works on KGAS',
    'entity_count': 2
}

print("Input data:")
print(f"  Type: {type(test_input)}")
print(f"  Keys: {test_input.keys()}")
print(f"  Has entities: {'entities' in test_input}")

try:
    # Call edge builder
    result = adapted_edge.process(test_input)
    print("\nOutput from adapted t34_edge_builder:")
    print(f"  Success: {result.get('success')}")
    print(f"  Result keys: {result.keys()}")
    
    output_data = result.get('data')
    print(f"  Data type: {type(output_data)}")
    if isinstance(output_data, dict):
        print(f"  Data keys: {output_data.keys()}")
        print(f"  Has entities: {'entities' in output_data}")
        print(f"  Sample data: {str(output_data)[:200]}")
    else:
        print(f"  Data content: {str(output_data)[:200]}")
        
except Exception as e:
    print(f"\n❌ Edge builder failed: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Analysis ===")
print("t34_edge_builder likely writes directly to Neo4j and doesn't return entity data")
print("This breaks the pipeline - it can't pass data to the next tool")