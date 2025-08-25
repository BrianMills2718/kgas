#!/usr/bin/env python3
"""Test format adapters for tool compatibility - TDD approach"""

import sys
import json
from datetime import datetime

sys.path.insert(0, '/home/brian/projects/Digimons')

def test_format_conversions():
    from src.core.format_adapters import FormatAdapter
    
    # Test T23C to T31
    t23c_output = [{
        "entity_id": "e1",
        "canonical_name": "Apple Inc.",
        "entity_type": "ORG",
        "confidence": 0.9
    }]
    
    t31_input = FormatAdapter.t23c_to_t31(t23c_output)
    assert t31_input[0]["text"] == "Apple Inc."
    assert "canonical_name" not in t31_input[0] or t31_input[0]["text"] == t31_input[0].get("canonical_name")
    
    # Test T31 to T34
    t31_output = [{
        "entity_id": "org_001",
        "canonical_name": "Apple Inc.",
        "entity_type": "ORG"
        # Note: NO 'text' field
    }]
    
    t34_input = FormatAdapter.t31_to_t34(t31_output)
    assert "text" in t34_input[0]
    assert t34_input[0]["text"] == "Apple Inc."
    
    # Test relationship normalization
    rel_variations = [
        {"source": "Apple", "target": "Tim Cook", "type": "LED_BY"},
        {"subject": "Apple", "object": "Tim Cook", "relationship_type": "LED_BY"},
        {"source_entity": "Apple", "target_entity": "Tim Cook", "relationship": "LED_BY"},
        {"subject": "Apple", "object": "Tim Cook", "predicate": "LED_BY"}
    ]
    
    for rel in rel_variations:
        normalized = FormatAdapter.normalize_relationship(rel)
        assert normalized["subject"] == "Apple"
        assert normalized["object"] == "Tim Cook"
        assert normalized["relationship_type"] == "LED_BY"
        assert "confidence" in normalized
    
    # Generate evidence
    evidence = {
        "timestamp": datetime.now().isoformat(),
        "test_name": "format_adapters",
        "conversions": [
            {
                "type": "t23c_to_t31",
                "input_fields": list(t23c_output[0].keys()),
                "output_fields": list(t31_input[0].keys()),
                "text_field_present": "text" in t31_input[0]
            },
            {
                "type": "t31_to_t34",
                "input_has_text": "text" in t31_output[0],
                "output_has_text": "text" in t34_input[0],
                "text_added": True
            },
            {
                "type": "relationship_normalization",
                "variations_tested": len(rel_variations),
                "all_normalized": True
            }
        ],
        "status": "success"
    }
    
    with open('evidence/format_adapters.json', 'w') as f:
        json.dump(evidence, f, indent=2)
    
    print("✅ Format adapters verified")
    return True

if __name__ == "__main__":
    success = test_format_conversions()
    exit(0 if success else 1)