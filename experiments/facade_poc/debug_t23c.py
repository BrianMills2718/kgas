#!/usr/bin/env python3
"""Debug why T23C returns 0 entities"""

import sys
sys.path.insert(0, '/home/brian/projects/Digimons')

from src.core.service_manager import ServiceManager
from src.core.tool_contract import ToolRequest
from src.tools.phase2.t23c_ontology_aware_extractor_unified import OntologyAwareExtractor

# Setup
service_manager = ServiceManager()
t23c = OntologyAwareExtractor(service_manager)

# Test text
test_text = """
Apple Inc., led by CEO Tim Cook, is headquartered in Cupertino.
Microsoft was founded by Bill Gates and Paul Allen in 1975.
Google competes with Microsoft and Apple in cloud services.
"""

print("Testing T23C with text:")
print(test_text)
print("-" * 60)

# Try different input formats
test_cases = [
    {
        "name": "Basic text only",
        "input_data": {"text": test_text}
    },
    {
        "name": "With source_ref",
        "input_data": {"text": test_text, "source_ref": "test_doc"}
    },
    {
        "name": "With confidence threshold",
        "input_data": {"text": test_text, "confidence_threshold": 0.5}
    }
]

for test_case in test_cases:
    print(f"\nTest: {test_case['name']}")
    request = ToolRequest(input_data=test_case["input_data"])
    
    try:
        result = t23c.execute(request)
        print(f"Status: {result.status}")
        
        if result.status == "success":
            data = result.data
            print(f"Data keys: {list(data.keys())}")
            
            # Check different possible output formats
            entities = data.get("entities", [])
            mentions = data.get("mentions", [])
            extracted_entities = data.get("extracted_entities", [])
            
            print(f"  entities: {len(entities)}")
            print(f"  mentions: {len(mentions)}")
            print(f"  extracted_entities: {len(extracted_entities)}")
            
            # Show first few items from each
            if entities:
                print(f"  First entity: {entities[0]}")
            if mentions:
                print(f"  First mention: {mentions[0]}")
            if extracted_entities:
                print(f"  First extracted: {extracted_entities[0]}")
        else:
            print(f"Error: {result.error_message}")
    except Exception as e:
        print(f"Exception: {e}")