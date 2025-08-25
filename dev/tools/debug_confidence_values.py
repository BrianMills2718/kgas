#!/usr/bin/env python3
"""
Debug actual confidence values during filtering
"""

import sys
sys.path.insert(0, '/home/brian/projects/Digimons')

# Let me modify the NER tool to add debug logging
def patch_ner_for_debugging():
    """Add debug logging to the NER tool"""
    
    # Read the current file
    with open('/home/brian/projects/Digimons/src/tools/phase1/t23a_spacy_ner_unified.py', 'r') as f:
        content = f.read()
    
    # Find the confidence filtering line and add logging before it
    old_line = "if entity_confidence < confidence_threshold:"
    new_lines = """print(f"DEBUG: Entity '{ent.text}' - calculated_confidence={entity_confidence:.3f}, threshold={confidence_threshold:.3f}")
                    if entity_confidence < confidence_threshold:
                        print(f"DEBUG: FILTERED OUT '{ent.text}' - {entity_confidence:.3f} < {confidence_threshold:.3f}")"""
    
    # Replace the line
    modified_content = content.replace(
        "                    # Apply adaptive confidence threshold\n                    if entity_confidence < confidence_threshold:",
        f"                    # Apply adaptive confidence threshold\n                    {new_lines}"
    )
    
    # Write back
    with open('/home/brian/projects/Digimons/src/tools/phase1/t23a_spacy_ner_unified.py', 'w') as f:
        f.write(modified_content)
    
    print("Added debug logging to NER tool")

if __name__ == "__main__":
    patch_ner_for_debugging()
    
    # Now run a test
    print("Running test with debug logging...")
    
    from src.core.service_manager import get_service_manager
    from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
    from src.tools.base_tool import ToolRequest
    
    # Test with known problematic case
    test_text = "John Smith works at Apple Inc. in San Francisco."
    
    service_manager = get_service_manager()
    entity_extractor = T23ASpacyNERUnified(
        service_manager=service_manager,
        memory_config={"db_path": None},
        reasoning_config={"enable_reasoning": False}
    )
    
    # Test with 0.5 threshold (the failing case)
    request = ToolRequest(
        tool_id="T23A",
        operation="extract_entities", 
        input_data={
            "text": test_text,
            "chunk_ref": "storage://chunk/debug_test",
            "chunk_confidence": 1.0
        },
        parameters={
            "confidence_threshold": 0.5,  # This was failing before
            "schema": None,
            "reasoning_guidance": None,
            "context_metadata": {}
        }
    )
    
    print(f"\nTesting with confidence_threshold=0.5:")
    result = entity_extractor.execute(request)
    
    entities = result.data.get('entities', []) if result.status == "success" else []
    print(f"Result: {len(entities)} entities extracted")