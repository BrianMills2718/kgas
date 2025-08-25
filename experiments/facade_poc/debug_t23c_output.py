#!/usr/bin/env python3
"""Debug T23C output format to see what it returns"""

import sys
sys.path.insert(0, '/home/brian/projects/Digimons')

from src.core.service_manager import ServiceManager
from src.core.tool_contract import ToolRequest
from src.tools.phase2.t23c_ontology_aware_extractor_unified import OntologyAwareExtractor

# Setup
service_manager = ServiceManager()
t23c = OntologyAwareExtractor(service_manager)

# Test text
test_text = "Apple Inc., led by CEO Tim Cook, is headquartered in Cupertino."

print("Testing T23C output format...")
request = ToolRequest(input_data={"text": test_text})
result = t23c.execute(request)

if result.status == "success":
    entities = result.data.get("entities", [])
    print(f"\nT23C returned {len(entities)} entities")
    
    if entities:
        print("\nFirst entity structure:")
        first_entity = entities[0]
        print(f"Type: {type(first_entity)}")
        if isinstance(first_entity, dict):
            print("Keys:", list(first_entity.keys()))
            for key, value in first_entity.items():
                print(f"  {key}: {value}")
else:
    print(f"Error: {result.error_message}")