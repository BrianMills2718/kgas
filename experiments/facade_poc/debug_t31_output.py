#!/usr/bin/env python3
"""Debug T31 output format"""

import sys
import os
sys.path.insert(0, '/home/brian/projects/Digimons')

from src.core.service_manager import ServiceManager
from src.core.tool_contract import ToolRequest
from src.tools.phase1.t31_entity_builder_unified import T31EntityBuilderUnified

# Setup
service_manager = ServiceManager()
t31 = T31EntityBuilderUnified(service_manager)

# Create test mentions
test_mentions = [
    {
        "text": "Apple Inc.",
        "entity_type": "ORGANIZATION",
        "confidence": 0.95,
        "start": 0,
        "end": 10
    },
    {
        "text": "Tim Cook",
        "entity_type": "PERSON",
        "confidence": 0.90,
        "start": 20,
        "end": 28
    }
]

# Execute T31
print("Testing T31 with mentions:")
for m in test_mentions:
    print(f"  - {m['text']} ({m['entity_type']})")

request = ToolRequest(input_data={"mentions": test_mentions})
result = t31.execute(request)

print(f"\nT31 Status: {result.status}")
if result.status == "success":
    entities = result.data.get("entities", [])
    print(f"Entities created: {len(entities)}")
    
    for i, entity in enumerate(entities):
        print(f"\nEntity {i}:")
        for key, value in entity.items():
            print(f"  {key}: {value}")
else:
    print(f"Error: {result.error_message}")