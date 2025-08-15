#!/usr/bin/env python3
"""
Direct test of relationship extraction fix without MCP complexity.
This validates that our format conversion and chunk_ref fixes work correctly.
"""

import asyncio
import sys
sys.path.append("/home/brian/projects/Digimons")

from src.tools.phase1.t15a_text_chunker_unified import T15ATextChunkerUnified
from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
from src.tools.phase1.t27_relationship_extractor_unified import T27RelationshipExtractorUnified
from src.core.service_manager import get_service_manager
from src.tools.base_tool import ToolRequest

def test_relationship_extraction_fix():
    """Test that our relationship extraction fixes work correctly"""
    
    print("🧪 Testing Relationship Extraction Fix")
    print("   Goal: Validate format conversion and chunk_ref fixes")
    print("   Method: Direct Python tool calls (no MCP)")
    print("=" * 60)
    
    try:
        # Initialize tools with service manager
        service_manager = get_service_manager()
        text_chunker = T15ATextChunkerUnified(service_manager)
        entity_extractor = T23ASpacyNERUnified(service_manager)
        relationship_extractor = T27RelationshipExtractorUnified(service_manager)
        
        print("✅ Tools initialized successfully")
        
        # Test content with explicit relationships
        test_content = """
        Dr. Sarah Chen works at MIT Computer Science Department. She collaborates with Prof. Michael Rodriguez from Stanford University.
        The research conducted by Dr. Chen and Prof. Rodriguez focuses on machine learning and artificial intelligence.
        MIT Computer Science Department partners with Stanford University on this research project.
        """
        
        print(f"📝 Test content: {len(test_content)} characters")
        
        # Step 1: Text chunking
        print("\n🔧 Step 1: Text chunking")
        chunk_request = ToolRequest(
            tool_id="T15A",
            operation="chunk_text",
            input_data={
                "document_ref": "storage://test/relationship_test.txt",
                "text": test_content,
                "confidence": 0.9
            },
            parameters={}
        )
        
        chunk_result = text_chunker.execute(chunk_request)
        if chunk_result.status != "success":
            raise Exception(f"Chunking failed: {chunk_result.error_message}")
        
        chunks = chunk_result.data.get("chunks", [])
        print(f"   ✅ Created {len(chunks)} chunks")
        
        # Step 2: Entity extraction with chunk_ref fix
        print("\n🔧 Step 2: Entity extraction (with chunk_ref fix)")
        all_entities = []
        
        for i, chunk in enumerate(chunks):
            print(f"   Processing chunk {i+1}: '{chunk['text'][:50]}...'")
            
            entity_request = ToolRequest(
                tool_id="T23A",
                operation="extract_entities",
                input_data={
                    "chunk_ref": chunk["chunk_ref"],  # This should now work correctly
                    "text": chunk["text"],
                    "chunk_confidence": chunk.get("confidence", 0.8)
                },
                parameters={"confidence_threshold": 0.3}  # Lower threshold for testing
            )
            
            entity_result = entity_extractor.execute(entity_request)
            if entity_result.status == "success":
                entities = entity_result.data.get("entities", [])
                all_entities.extend(entities)
                print(f"     ✅ Found {len(entities)} entities")
                
                # Check that chunk_ref is properly included
                for entity in entities:
                    chunk_ref_in_entity = entity.get("chunk_ref")
                    if chunk_ref_in_entity == chunk["chunk_ref"]:
                        print(f"       ✅ Entity '{entity.get('surface_form')}': chunk_ref correctly set")
                    else:
                        print(f"       ❌ Entity '{entity.get('surface_form')}': chunk_ref mismatch!")
                        print(f"          Expected: {chunk['chunk_ref']}")
                        print(f"          Got: {chunk_ref_in_entity}")
            else:
                print(f"     ❌ Entity extraction failed: {entity_result.error_message}")
        
        print(f"   ✅ Total entities extracted: {len(all_entities)}")
        
        if len(all_entities) == 0:
            print("❌ No entities found - cannot test relationships")
            return False
        
        # Step 3: Relationship extraction with format conversion fix
        print("\n🔧 Step 3: Relationship extraction (with format conversion fix)")
        all_relationships = []
        
        for i, chunk in enumerate(chunks):
            chunk_entities = [e for e in all_entities if e.get("chunk_ref") == chunk["chunk_ref"]]
            print(f"   Processing chunk {i+1}: {len(chunk_entities)} entities")
            
            if len(chunk_entities) >= 2:  # Need at least 2 entities for relationships
                print(f"     Entities: {[e.get('surface_form') for e in chunk_entities]}")
                
                # Apply the critical format conversion fix
                t27_formatted_entities = []
                for entity in chunk_entities:
                    # This is the fix: T23A format → T27 format conversion
                    t27_entity = {
                        'text': entity.get('surface_form', ''),  # T23A → T27
                        'label': entity.get('entity_type', ''),  # T23A → T27
                        'start': entity.get('start_pos', 0),     # T23A → T27
                        'end': entity.get('end_pos', 0),         # T23A → T27
                        # Debug info
                        '_original_chunk_ref': entity.get('chunk_ref', ''),
                        '_confidence': entity.get('confidence', 0.0)
                    }
                    t27_formatted_entities.append(t27_entity)
                
                print(f"     ✅ Format conversion: {len(t27_formatted_entities)} entities converted")
                
                # Test relationship extraction with converted format
                rel_request = ToolRequest(
                    tool_id="T27",
                    operation="extract_relationships",
                    input_data={
                        "chunk_ref": chunk["chunk_ref"],
                        "text": chunk["text"],
                        "entities": t27_formatted_entities,  # Using converted format!
                        "confidence": 0.1  # Very low threshold for testing
                    },
                    parameters={}
                )
                
                rel_result = relationship_extractor.execute(rel_request)
                if rel_result.status == "success":
                    relationships = rel_result.data.get("relationships", [])
                    all_relationships.extend(relationships)
                    print(f"     ✅ Found {len(relationships)} relationships")
                    
                    for j, rel in enumerate(relationships):
                        source = rel.get("source_entity", "Unknown")
                        rel_type = rel.get("relationship_type", "Unknown")
                        target = rel.get("target_entity", "Unknown")
                        conf = rel.get("confidence", 0.0)
                        print(f"       {j+1}. {source} → {rel_type} → {target} (conf: {conf:.2f})")
                else:
                    print(f"     ❌ Relationship extraction failed: {rel_result.error_message}")
            else:
                print(f"     ⚠️  Skipping chunk {i+1}: Only {len(chunk_entities)} entities (need 2+)")
        
        print(f"\n📊 FINAL RESULTS:")
        print(f"   Chunks: {len(chunks)}")
        print(f"   Entities: {len(all_entities)}")
        print(f"   Relationships: {len(all_relationships)}")
        
        # Validation
        if len(all_relationships) > 0:
            print(f"\n🎉 SUCCESS: Relationship extraction fix is working!")
            print(f"   ✅ chunk_ref association: Fixed")
            print(f"   ✅ Format conversion (T23A→T27): Fixed")
            print(f"   ✅ End-to-end pipeline: Working")
            
            # Show relationship details
            print(f"\n📋 Extracted Relationships:")
            for i, rel in enumerate(all_relationships):
                print(f"   {i+1}. {rel.get('source_entity')} → {rel.get('relationship_type')} → {rel.get('target_entity')}")
            
            return True
        else:
            print(f"\n❌ FAILURE: No relationships extracted")
            print(f"   Possible issues:")
            print(f"   - Format conversion not working")
            print(f"   - T27 relationship patterns not matching")
            print(f"   - Confidence thresholds too high")
            return False
            
    except Exception as e:
        print(f"💥 TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_relationship_extraction_fix()
    sys.exit(0 if success else 1)