#!/usr/bin/env python3
"""Debug neo4j_graph_builder failure in complex pipeline"""

import sys
import os
from dotenv import load_dotenv
load_dotenv('/home/brian/projects/Digimons/.env')

sys.path.append('/home/brian/projects/Digimons')
sys.path.append('/home/brian/projects/Digimons/tool_compatability/poc/vertical_slice')

from src.tools.neo4j_graph_builder import Neo4jGraphBuilder
from src.tools.gemini_entity_extractor import GeminiEntityExtractor
from adapters.universal_adapter import UniversalAdapter

print("=== Debugging Neo4j Graph Builder Issue ===\n")

# Test 1: Direct neo4j_graph_builder with expected format
print("Test 1: Direct call with expected format")
builder = Neo4jGraphBuilder()
test_data = {
    'entities': [
        {'id': '1', 'name': 'Brian Chhun', 'type': 'PERSON'},
        {'id': '2', 'name': 'KGAS', 'type': 'SYSTEM'}
    ],
    'relationships': [
        {'source': '1', 'target': '2', 'type': 'DEVELOPS'}
    ]
}
result1 = builder.process(test_data)
print(f"  Direct call result: {result1}")
print(f"  Success: {result1.get('success')}\n")

# Test 2: Through UniversalAdapter with same data
print("Test 2: Through UniversalAdapter")
adapted_builder = UniversalAdapter(builder, "neo4j_graph_builder", "process")
try:
    result2 = adapted_builder.process(test_data)
    print(f"  Adapter result: {result2}")
    print(f"  Success: {result2.get('success')}\n")
except Exception as e:
    print(f"  ❌ Adapter failed: {e}\n")

# Test 3: Check what gemini_entity_extractor actually outputs
print("Test 3: Check gemini_entity_extractor output format")
extractor = GeminiEntityExtractor()
text = "Brian Chhun works on KGAS at Melbourne University"
extractor_result = extractor.process(text)
print(f"  Extractor output keys: {extractor_result.keys()}")
print(f"  Entities type: {type(extractor_result.get('entities'))}")
print(f"  Sample entity: {extractor_result.get('entities', [])[:1]}")
print(f"  Entity format matches expected? {bool(extractor_result.get('entities'))}\n")

# Test 4: Through adapter - what does it transform to?
print("Test 4: Gemini extractor through adapter")
adapted_extractor = UniversalAdapter(extractor, "gemini_entity_extractor", "process")
adapted_result = adapted_extractor.process(text)
print(f"  Adapted result keys: {adapted_result.keys()}")
print(f"  Data key type: {type(adapted_result.get('data'))}")
if isinstance(adapted_result.get('data'), dict):
    print(f"  Data contents keys: {adapted_result['data'].keys()}")
    print(f"  Entities in data? {'entities' in adapted_result['data']}")

# Test 5: What if we pass the adapted extractor result to builder?
print("\nTest 5: Pass adapted extractor output to neo4j_graph_builder")
if adapted_result.get('success'):
    # The adapter wraps the result in 'data' key
    extracted_data = adapted_result.get('data')
    print(f"  Passing data type: {type(extracted_data)}")
    print(f"  Data has entities key: {'entities' in extracted_data if isinstance(extracted_data, dict) else False}")
    
    try:
        # Try with the raw builder
        builder_result = builder.process(extracted_data)
        print(f"  ✅ Direct builder succeeded: {builder_result}")
    except Exception as e:
        print(f"  ❌ Direct builder failed: {e}")
    
    # Try with adapted builder
    try:
        adapted_builder_result = adapted_builder.process(extracted_data)
        print(f"  ✅ Adapted builder succeeded: {adapted_builder_result}")
    except Exception as e:
        print(f"  ❌ Adapted builder failed: {e}")

print("\n=== Analysis ===")
print("The issue is likely in how the UniversalAdapter transforms data between tools.")
print("The framework needs to extract the actual data from the 'data' wrapper.")