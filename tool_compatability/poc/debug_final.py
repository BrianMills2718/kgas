#!/usr/bin/env python3
"""Final debug - why neo4j_graph_builder fails with gemini output"""

import sys
from dotenv import load_dotenv
load_dotenv('/home/brian/projects/Digimons/.env')

sys.path.append('/home/brian/projects/Digimons')

from src.tools.neo4j_graph_builder import Neo4jGraphBuilder
from src.tools.gemini_entity_extractor import GeminiEntityExtractor

print("=== Final Debug ===\n")

# Get real gemini output
extractor = GeminiEntityExtractor()
text = "Brian Chhun and Sarah Chen work on KGAS at Melbourne University"
gemini_output = extractor.process(text)

print("Gemini output:")
print(f"  Keys: {gemini_output.keys()}")
print(f"  Entities: {gemini_output.get('entities')}")
print(f"  Entity format: {gemini_output.get('entities')[0] if gemini_output.get('entities') else 'No entities'}")

# Try passing directly to neo4j_graph_builder
builder = Neo4jGraphBuilder()
print("\nPassing to neo4j_graph_builder...")

try:
    result = builder.process(gemini_output)
    print(f"✅ Success: {result.get('success')}")
    print(f"   Nodes created: {result.get('nodes_created')}")
    print(f"   Result: {result}")
except Exception as e:
    print(f"❌ Failed: {e}")

# Check what format neo4j_graph_builder expects
print("\n=== Expected Format ===")
print("neo4j_graph_builder expects entities with these fields:")
print("  - id or entity_id")
print("  - name or canonical_name") 
print("  - type or entity_type")

print("\n=== Actual Format ===")
print("gemini_entity_extractor provides:")
print("  - text (the entity text)")
print("  - type (entity type)")
print("  - confidence (confidence score)")

print("\n=== Solution ===")
print("Need to transform gemini output to match neo4j_graph_builder expectations")
print("Or modify neo4j_graph_builder to accept gemini format")