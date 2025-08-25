#!/usr/bin/env python3
"""
Test entity extraction with confidence threshold = 0
"""

import sys
sys.path.insert(0, '/home/brian/projects/Digimons')

from src.core.service_manager import get_service_manager
from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
from src.tools.base_tool import ToolRequest

def debug_zero_confidence():
    """Debug with confidence threshold = 0"""
    
    print("=== Testing with confidence_threshold = 0 ===")
    
    test_text = """John Smith is the CEO of TechCorp Corporation, a leading technology company based in San Francisco, California. 

The company was founded in 2010 and has grown rapidly under John's leadership. TechCorp specializes in artificial intelligence and machine learning solutions for enterprise clients.

Mary Johnson, the CTO of TechCorp, leads the engineering team responsible for developing innovative AI products."""
    
    print(f"Test text: {len(test_text)} characters")
    
    # Initialize service manager
    service_manager = get_service_manager()
    
    # Create entity extractor 
    entity_extractor = T23ASpacyNERUnified(
        service_manager=service_manager,
        memory_config={"db_path": None},
        reasoning_config={"enable_reasoning": False}
    )
    
    # Test with confidence_threshold = 0
    request = ToolRequest(
        tool_id="T23A",
        operation="extract_entities", 
        input_data={
            "text": test_text,
            "chunk_ref": "storage://chunk/zero_test",
            "chunk_confidence": 1.0  # Maximum chunk confidence
        },
        parameters={
            "confidence_threshold": 0.0,  # ZERO threshold - should allow everything
            "schema": None,
            "reasoning_guidance": None,
            "context_metadata": {}
        }
    )
    
    print("Executing with confidence_threshold = 0.0...")
    result = entity_extractor.execute(request)
    
    print(f"Result status: {result.status}")
    
    if result.status == "success":
        entities = result.data.get('entities', [])
        print(f"Extracted {len(entities)} entities with confidence_threshold = 0:")
        for entity in entities:
            print(f"  - {entity.get('surface_form')} ({entity.get('entity_type')}) confidence: {entity.get('confidence', 0):.3f}")
    else:
        print(f"Failed: {result.error_message}")
    
    # Compare with direct spaCy
    print(f"\n=== Direct spaCy comparison ===")
    import spacy
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(test_text)
    print(f"spaCy found {len(doc.ents)} entities directly:")
    for ent in doc.ents:
        print(f"  - {ent.text} ({ent.label_})")

if __name__ == "__main__":
    debug_zero_confidence()