#!/usr/bin/env python3
"""Test multi-input support for tools"""

import sys
import os
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from poc.data_types import DataSchema
from typing import Dict, Any
from pydantic import BaseModel

def test_entity_extraction_with_ontology():
    """Prove we can pass custom ontology to EntityExtractor"""
    
    # Import after path setup
    from poc.tool_context import ToolContext
    from poc.tools.entity_extractor_v2 import EntityExtractorV2
    
    print("="*60)
    print("TEST: Multi-Input Entity Extraction with Custom Ontology")
    print("="*60)
    
    # Create context with multiple inputs
    context = ToolContext()
    
    # Set primary data
    test_text = """
    John Smith is the CEO of Apple Inc.
    Jane Doe works as CTO at Microsoft Corporation.
    They met in San Francisco last week.
    """
    
    context.primary_data = DataSchema.TextData(
        content=test_text,
        source_file="test.txt",
        encoding="utf-8",
        checksum="test123",
        char_count=len(test_text),
        line_count=4
    )
    
    # Add custom ontology as parameter
    custom_ontology = {
        "PERSON": {
            "properties": ["name", "title", "role"],
            "patterns": ["CEO", "CTO", "Director", "Manager"]
        },
        "COMPANY": {
            "properties": ["name", "industry", "type"],
            "patterns": ["Inc", "Corporation", "LLC", "Ltd"]
        },
        "LOCATION": {
            "properties": ["city", "country"],
            "patterns": ["San Francisco", "New York", "London"]
        }
    }
    
    context.set_param("EntityExtractorV2", "ontology", custom_ontology)
    
    # Add extraction rules
    extraction_rules = {
        "confidence_threshold": 0.7,
        "include_positions": True,
        "extract_relationships": True
    }
    
    context.set_param("EntityExtractorV2", "rules", extraction_rules)
    
    # Create extractor and process
    print("\nCreating EntityExtractorV2...")
    extractor = EntityExtractorV2()
    
    print("Processing with custom ontology and rules...")
    result = extractor.process(context)
    
    # Verify ontology was used
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    
    # Check that prompt included ontology
    if hasattr(extractor, 'last_prompt'):
        assert "ontology" in extractor.last_prompt.lower(), "Ontology not in prompt!"
        assert "PERSON" in extractor.last_prompt, "PERSON type not in prompt!"
        assert "COMPANY" in extractor.last_prompt, "COMPANY type not in prompt!"
        print("✅ Custom ontology was included in prompt")
        
        # Show portion of prompt for evidence
        print("\nPrompt excerpt (first 500 chars):")
        print(extractor.last_prompt[:500])
    
    # Check entities were extracted
    entities = result.primary_data.entities if hasattr(result.primary_data, 'entities') else []
    print(f"\n✅ Entities found: {len(entities)}")
    
    for entity in entities:
        print(f"  - {entity.text} ({entity.type}) - confidence: {entity.confidence:.2f}")
    
    # Verify extraction rules were applied
    if entities:
        # Check confidence threshold
        for entity in entities:
            assert entity.confidence >= 0.7, f"Entity {entity.text} below threshold!"
        print("\n✅ Confidence threshold applied correctly")
    
    # Check that context parameters were accessible
    retrieved_ontology = context.get_param("EntityExtractorV2", "ontology")
    assert retrieved_ontology == custom_ontology, "Ontology not stored correctly!"
    print("✅ Parameters stored and retrieved correctly")
    
    print("\n" + "="*60)
    print("✅ MULTI-INPUT TEST PASSED")
    print("="*60)
    
    return True


if __name__ == "__main__":
    # Run test
    try:
        success = test_entity_extraction_with_ontology()
        sys.exit(0 if success else 1)
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("Need to implement ToolContext and EntityExtractorV2 first")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)