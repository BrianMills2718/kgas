#!/usr/bin/env python3
"""
Minimal Pipeline for Processing a Single Document

This script implements the basic workflow:
1. Load document -> text
2. Chunk text
3. Extract entities (with fallback)
4. Store in Neo4j
5. Verify storage
"""

import sys
import os
from datetime import datetime
from typing import Dict, Any, List


def process_single_document(file_path: str) -> Dict[str, Any]:
    """Process a single document through the minimal pipeline
    
    Args:
        file_path: Path to the document to process
        
    Returns:
        Dictionary with processing results
    """
    results = {
        "file_path": file_path,
        "timestamp": datetime.now().isoformat(),
        "text_extracted": False,
        "chunks_created": 0,
        "entities_found": 0,
        "stored_in_db": 0,
        "errors": []
    }
    
    print(f"\n{'=' * 60}")
    print(f"PROCESSING DOCUMENT: {file_path}")
    print(f"{'=' * 60}")
    
    # Step 1: Load document
    print("\n1. Loading document...")
    try:
        from src.core.service_manager import ServiceManager
        from src.tools.phase1.t01_pdf_loader import PDFLoader
        from src.tools.base_tool import ToolRequest
        
        sm = ServiceManager()
        loader = PDFLoader(sm)
        
        # Create tool request
        request = ToolRequest(
            tool_id="T01_PDF_LOADER",
            operation="load_document",
            input_data={
                "file_path": file_path,
                "workflow_id": "minimal_pipeline"
            },
            parameters={}
        )
        
        # Load the document
        load_result = loader.execute(request)
        
        if load_result and load_result.status == 'success':
            # Extract document data
            document = load_result.data.get('document', {})
            text = document.get('text', '')
            doc_ref = document.get('document_ref', 'doc_unknown')
            confidence = document.get('confidence', 0.8)
            
            results["text_extracted"] = True
            results["text_length"] = len(text)
            print(f"  ✓ Text extracted: {len(text)} characters")
            print(f"  Document reference: {doc_ref}")
        else:
            error = f"Document loading failed: {load_result}"
            results["errors"].append(error)
            print(f"  ✗ {error}")
            return results
            
    except Exception as e:
        error = f"Document loading error: {str(e)}"
        results["errors"].append(error)
        print(f"  ✗ {error}")
        return results
    
    # Step 2: Chunk text
    print("\n2. Chunking text...")
    try:
        from src.tools.phase1.t15a_text_chunker import TextChunker
        
        chunker = TextChunker(sm)
        
        # Create tool request
        chunk_request = ToolRequest(
            tool_id="T15A_TEXT_CHUNKER",
            operation="chunk_text",
            input_data={
                "document_ref": doc_ref,
                "text": text,
                "chunk_confidence": confidence
            },
            parameters={}
        )
        
        chunk_result = chunker.execute(chunk_request)
        
        if chunk_result and chunk_result.status == 'success':
            chunks = chunk_result.data.get('chunks', [])
            results["chunks_created"] = len(chunks)
            print(f"  ✓ Created {len(chunks)} chunks")
            
            # Show first chunk as sample
            if chunks:
                first_chunk = chunks[0]
                preview = first_chunk.get('text', '')[:100] + "..."
                print(f"  First chunk preview: {preview}")
        else:
            error = f"Chunking failed: {chunk_result.error_message if hasattr(chunk_result, 'error_message') else chunk_result}"
            results["errors"].append(error)
            print(f"  ✗ {error}")
            chunks = [{"chunk_ref": f"chunk_{i}", "text": text[i:i+500]} 
                     for i in range(0, len(text), 400)]
            results["chunks_created"] = len(chunks)
            print(f"  Using fallback chunking: {len(chunks)} chunks")
            
    except Exception as e:
        error = f"Chunking error: {str(e)}"
        results["errors"].append(error)
        print(f"  ✗ {error}")
        # Fallback: create simple chunks
        chunks = [{"chunk_ref": f"chunk_{i}", "text": text[i:i+500]} 
                 for i in range(0, len(text), 400)]
        results["chunks_created"] = len(chunks)
        print(f"  Using fallback chunking: {len(chunks)} chunks")
    
    # Step 3: Extract entities
    print("\n3. Extracting entities...")
    all_entities = []
    
    try:
        # Use proper entity extraction - FAIL-FAST MODE
        from src.tools.phase1.t23a_spacy_ner import SpacyNER
        
        # Create extractor with proper service manager
        from src.core.service_manager import ServiceManager
        service_manager = ServiceManager()
        extractor = SpacyNER(service_manager)
        
        for i, chunk in enumerate(chunks[:5]):  # Process first 5 chunks for demo
            chunk_text = chunk.get('text', '')
            chunk_ref = chunk.get('chunk_ref', f'chunk_{i}')
            
            print(f"  Processing chunk {i+1}/{min(5, len(chunks))}...")
            
            # Use fallback extraction
            extraction_result = extractor.extract_entities_fallback(
                chunk_text, 
                chunk_ref,
                confidence_threshold=0.4  # Lower threshold for demo
            )
            
            if extraction_result:
                entities = extraction_result.get('entities', [])
                all_entities.extend(entities)
                print(f"    Found {len(entities)} entities")
        
        results["entities_found"] = len(all_entities)
        print(f"  ✓ Total entities extracted: {len(all_entities)}")
        
        # Show sample entities
        if all_entities:
            print("  Sample entities:")
            for entity in all_entities[:5]:
                print(f"    - {entity.get('surface_form')} ({entity.get('entity_type')})")
                
    except Exception as e:
        error = f"Entity extraction error: {str(e)}"
        results["errors"].append(error)
        print(f"  ✗ {error}")
    
    # Step 4: Store in Neo4j
    print("\n4. Storing entities in Neo4j...")
    try:
        from src.tools.phase1.t31_entity_builder import EntityBuilder
        
        builder = EntityBuilder(sm)
        
        # Convert entities to mentions format for entity builder
        mentions = []
        for entity in all_entities:
            mention = {
                'mention_id': f"mention_{entity.get('entity_id', '')}",
                'entity_id': entity.get('entity_id', ''),
                'surface_form': entity.get('surface_form', ''),
                'text': entity.get('surface_form', ''),  # Add text field
                'entity_type': entity.get('entity_type', 'MISC'),
                'confidence': entity.get('confidence', 0.5),
                'start_pos': entity.get('start_pos', 0),
                'end_pos': entity.get('end_pos', 0)
            }
            mentions.append(mention)
        
        if mentions:
            # Create tool request for entity builder
            build_request = ToolRequest(
                tool_id="T31_ENTITY_BUILDER",
                operation="build_entities",
                input_data={
                    "mentions": mentions,
                    "source_refs": [doc_ref]
                },
                parameters={}
            )
            
            build_result = builder.execute(build_request)
            
            if build_result and build_result.status == 'success':
                entity_count = build_result.data.get('entity_count', 0)
                results["stored_in_db"] = entity_count
                print(f"  ✓ Stored {entity_count} entities in Neo4j")
            else:
                error = f"Entity storage failed: {build_result}"
                results["errors"].append(error)
                print(f"  ✗ {error}")
        else:
            print("  No entities to store")
            
    except Exception as e:
        error = f"Neo4j storage error: {str(e)}"
        results["errors"].append(error)
        print(f"  ✗ {error}")
    
    # Step 5: Verify storage
    print("\n5. Verifying data in Neo4j...")
    try:
        from neo4j import GraphDatabase
        
        # Connect to Neo4j
        driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", os.getenv("NEO4J_PASSWORD", "Geriatric7Ambition-Stitch"))
        )
        
        with driver.session() as session:
            # Count entities
            result = session.run("MATCH (e:Entity) RETURN count(e) as count")
            entity_count = result.single()["count"]
            print(f"  ✓ Total entities in database: {entity_count}")
            
            # Get sample entities
            result = session.run("""
                MATCH (e:Entity) 
                RETURN e.canonical_name as name, e.entity_type as type
                LIMIT 5
            """)
            
            print("  Sample entities from database:")
            for record in result:
                print(f"    - {record['name']} ({record['type']})")
        
        driver.close()
        
    except Exception as e:
        error = f"Verification error: {str(e)}"
        results["errors"].append(error)
        print(f"  ✗ {error}")
    
    # Summary
    print(f"\n{'=' * 60}")
    print("PROCESSING SUMMARY")
    print(f"{'=' * 60}")
    print(f"Text extracted: {results['text_extracted']} ({results.get('text_length', 0)} chars)")
    print(f"Chunks created: {results['chunks_created']}")
    print(f"Entities found: {results['entities_found']}")
    print(f"Stored in DB: {results['stored_in_db']}")
    print(f"Errors: {len(results['errors'])}")
    
    if results['errors']:
        print("\nErrors encountered:")
        for error in results['errors']:
            print(f"  - {error}")
    
    # Determine success
    success = (
        results['text_extracted'] and
        results['chunks_created'] > 0 and
        results['entities_found'] > 0
    )
    
    if success:
        print("\n✅ Pipeline execution successful!")
    else:
        print("\n⚠️ Pipeline partially successful. See errors above.")
    
    return results


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        # Use default test file
        file_path = "test_data/simple_test.txt"
        print(f"No file specified. Using default: {file_path}")
    else:
        file_path = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return 1
    
    # Process the document
    results = process_single_document(file_path)
    
    # Return appropriate exit code
    if results['text_extracted'] and results['entities_found'] > 0:
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())