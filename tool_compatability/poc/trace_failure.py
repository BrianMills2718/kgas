#!/usr/bin/env python3
"""Trace the exact failure point"""

import sys
from dotenv import load_dotenv
load_dotenv('/home/brian/projects/Digimons/.env')

sys.path.append('/home/brian/projects/Digimons')
sys.path.append('/home/brian/projects/Digimons/tool_compatability/poc/vertical_slice')

from src.tools.gemini_entity_extractor import GeminiEntityExtractor
from src.tools.neo4j_graph_builder import Neo4jGraphBuilder
from adapters.universal_adapter import UniversalAdapter

# Simulate the pipeline
extractor = GeminiEntityExtractor()
builder = Neo4jGraphBuilder()

# Step 1: Extract entities
text = "Brian Chhun works on KGAS"
extractor_result = extractor.process(text)
print("Extractor output entities:", extractor_result.get('entities'))

# Step 2: Wrap with adapter (simulating framework)
adapted_extractor = UniversalAdapter(extractor, "gemini_entity_extractor", "process")
adapted_result = adapted_extractor.process(text)
print("\nAdapted extractor output:")
print("  Success:", adapted_result['success'])
print("  Data has entities:", 'entities' in adapted_result.get('data', {}))

# Step 3: Pass to builder through adapter
adapted_builder = UniversalAdapter(builder, "neo4j_graph_builder", "process")

# This is what the framework would pass - the 'data' from previous step
input_to_builder = adapted_result.get('data')
print("\nInput to builder:")
print("  Type:", type(input_to_builder))
print("  Has entities:", 'entities' in input_to_builder if isinstance(input_to_builder, dict) else False)

try:
    builder_result = adapted_builder.process(input_to_builder)
    print("\n✅ Builder succeeded:")
    print("  Result:", builder_result)
except Exception as e:
    print(f"\n❌ Builder failed: {e}")
    
    # Try direct call to understand
    print("\nTrying direct builder call...")
    direct_result = builder.process(input_to_builder)
    print("  Direct result:", direct_result)
    print("  Success field:", direct_result.get('success'))
    
    if not direct_result.get('success'):
        print("\nThe issue: builder returns success=False for some reason")
        print("This causes UniversalAdapter._assess_uncertainty to fail")
        print("Because it tries to assess uncertainty for a failed operation")