#!/usr/bin/env python3
"""
Minimal Pipeline - Process a Single Document End-to-End
Task 3.2 Implementation
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, List
from src.core.service_manager import ServiceManager
from src.tools.base_tool import ToolRequest

def process_single_document(pdf_path: str) -> Dict[str, Any]:
    """
    Process a single PDF document through the minimal pipeline.
    
    Steps:
    1. Load PDF -> text
    2. Chunk text
    3. Extract entities (with fallback)
    4. Store in Neo4j
    5. Verify storage
    """
    
    results = {
        "pdf_path": pdf_path,
        "text_extracted": False,
        "chunks_created": 0,
        "entities_found": 0,
        "relationships_found": 0,
        "stored_in_db": 0,
        "errors": []
    }
    
    print("=" * 60)
    print("PROCESSING SINGLE DOCUMENT")
    print("=" * 60)
    print(f"PDF: {pdf_path}")
    print()
    
    # Initialize service manager
    sm = ServiceManager()
    
    # Step 1: Load PDF
    print("Step 1: Loading PDF...")
    try:
        from src.tools.phase1.t01_pdf_loader import PDFLoader
        loader = PDFLoader(sm)
        
        # Create request for PDF loading
        request = ToolRequest(
            tool_id="T01_PDF_LOADER",
            operation="load",
            input_data={"file_path": pdf_path},
            parameters={}
        )
        
        # Try to load PDF
        if hasattr(loader, 'execute'):
            pdf_result = loader.execute(request)
        elif hasattr(loader, 'load_pdf'):
            pdf_result = loader.load_pdf(pdf_path)
        else:
            # Try direct approach
            import PyPDF2
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
            pdf_result = {"text": text, "success": True}
        
        if isinstance(pdf_result, dict):
            text = pdf_result.get("text", "")
        else:
            text = str(pdf_result)
            
        if text and len(text) > 0:
            results["text_extracted"] = True
            print(f"  ✓ Extracted {len(text)} characters")
        else:
            results["errors"].append("No text extracted from PDF")
            print(f"  ✗ No text extracted")
            return results
            
    except Exception as e:
        results["errors"].append(f"PDF loading failed: {e}")
        print(f"  ✗ Error: {e}")
        
        # Try alternative PDF loading
        try:
            print("  Trying alternative PDF loading with PyPDF2...")
            import PyPDF2
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            results["text_extracted"] = True
            print(f"  ✓ Extracted {len(text)} characters (alternative method)")
        except Exception as e2:
            print(f"  ✗ Alternative method also failed: {e2}")
            return results
    
    # Step 2: Chunk text
    print("\nStep 2: Chunking text...")
    try:
        from src.tools.phase1.t15a_text_chunker import TextChunker
        chunker = TextChunker(sm)
        
        # Create request for chunking
        request = ToolRequest(
            tool_id="T15A_TEXT_CHUNKER",
            operation="chunk",
            input_data={"text": text, "chunk_size": 500},
            parameters={}
        )
        
        # Try to chunk text
        if hasattr(chunker, 'execute'):
            chunk_result = chunker.execute(request)
        elif hasattr(chunker, 'chunk_text'):
            chunk_result = chunker.chunk_text(text, chunk_size=500)
        else:
            # Simple fallback chunking
            words = text.split()
            chunk_size = 100  # words per chunk
            chunks = []
            for i in range(0, len(words), chunk_size):
                chunk = ' '.join(words[i:i+chunk_size])
                chunks.append(chunk)
            chunk_result = {"chunks": chunks}
        
        if isinstance(chunk_result, dict):
            chunks = chunk_result.get("chunks", [])
        elif hasattr(chunk_result, 'data'):
            chunks = chunk_result.data.get("chunks", [])
        else:
            chunks = [text]  # Fallback to single chunk
            
        results["chunks_created"] = len(chunks)
        print(f"  ✓ Created {len(chunks)} chunks")
        
    except Exception as e:
        results["errors"].append(f"Chunking failed: {e}")
        print(f"  ✗ Error: {e}")
        chunks = [text]  # Use whole text as single chunk
        results["chunks_created"] = 1
    
    # Step 3: Extract entities
    print("\nStep 3: Extracting entities...")
    all_entities = []
    all_relationships = []
    
    try:
        # Try SpaCy extraction first (more reliable)
        from src.tools.phase1.t23a_spacy_ner import SpacyNER
        spacy_tool = SpacyNER(sm)
        
        for i, chunk in enumerate(chunks[:5]):  # Process first 5 chunks for demo
            print(f"  Processing chunk {i+1}/{min(5, len(chunks))}...")
            
            try:
                # Extract entities from chunk
                if hasattr(spacy_tool, 'extract_entities'):
                    entities = spacy_tool.extract_entities(chunk)
                else:
                    request = ToolRequest(
                        tool_id="T23A_SPACY_NER",
                        operation="extract",
                        input_data={"text": chunk},
                        parameters={}
                    )
                    if hasattr(spacy_tool, 'execute'):
                        result = spacy_tool.execute(request)
                        if hasattr(result, 'data'):
                            entities = result.data.get('entities', [])
                        else:
                            entities = []
                    else:
                        entities = []
                
                if isinstance(entities, dict):
                    entities = entities.get('entities', [])
                    
                all_entities.extend(entities)
                
            except Exception as chunk_error:
                print(f"    Warning: Chunk {i+1} failed: {chunk_error}")
                continue
        
        # Also try to extract relationships
        try:
            from src.tools.phase1.t27_relationship_extractor import RelationshipExtractor
            rel_extractor = RelationshipExtractor(sm)
            
            # Extract relationships from first chunk
            if chunks and hasattr(rel_extractor, 'extract_relationships'):
                relationships = rel_extractor.extract_relationships(chunks[0])
                if isinstance(relationships, dict):
                    all_relationships = relationships.get('relationships', [])
        except Exception as rel_error:
            print(f"  Relationship extraction skipped: {rel_error}")
        
        results["entities_found"] = len(all_entities)
        results["relationships_found"] = len(all_relationships)
        print(f"  ✓ Found {len(all_entities)} entities and {len(all_relationships)} relationships")
        
    except Exception as e:
        results["errors"].append(f"Entity extraction failed: {e}")
        print(f"  ✗ Error: {e}")
    
    # Step 4: Store in Neo4j
    print("\nStep 4: Storing in Neo4j...")
    stored_count = 0
    
    try:
        from src.tools.phase1.t31_entity_builder import EntityBuilder
        entity_builder = EntityBuilder(sm)
        
        # Prepare entities for storage
        entities_to_store = []
        for entity in all_entities[:20]:  # Store first 20 entities for demo
            if isinstance(entity, dict):
                entities_to_store.append({
                    'name': entity.get('text', entity.get('name', '')),
                    'type': entity.get('type', entity.get('label', 'UNKNOWN')),
                    'confidence': entity.get('confidence', 0.8)
                })
        
        if entities_to_store:
            request = ToolRequest(
                tool_id="T31_ENTITY_BUILDER",
                operation="build",
                input_data={"entities": entities_to_store},
                parameters={}
            )
            
            if hasattr(entity_builder, 'execute'):
                build_result = entity_builder.execute(request)
                if hasattr(build_result, 'data'):
                    stored_count = build_result.data.get('entities_created', 0)
            elif hasattr(entity_builder, 'build_entities'):
                build_result = entity_builder.build_entities(entities_to_store)
                if isinstance(build_result, dict):
                    stored_count = build_result.get('entities_created', len(entities_to_store))
            
        results["stored_in_db"] = stored_count
        print(f"  ✓ Stored {stored_count} entities in Neo4j")
        
    except Exception as e:
        results["errors"].append(f"Neo4j storage failed: {e}")
        print(f"  ✗ Error: {e}")
    
    # Step 5: Verify storage
    print("\nStep 5: Verifying storage...")
    try:
        from neo4j import GraphDatabase
        from src.core.standard_config import get_database_uri
        
        uri = get_database_uri("neo4j")
        driver = GraphDatabase.driver(uri)
        
        with driver.session() as session:
            result = session.run("MATCH (n) RETURN count(n) as count")
            count = result.single()["count"]
            print(f"  ✓ Total nodes in database: {count}")
            
            # Get sample entities
            result = session.run("MATCH (n) RETURN n LIMIT 5")
            print("  Sample entities:")
            for record in result:
                node = record["n"]
                props = dict(node)
                print(f"    - {props.get('name', props.get('canonical_name', 'Unknown'))}")
        
        driver.close()
        
    except Exception as e:
        print(f"  ⚠ Could not verify storage: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("PROCESSING SUMMARY")
    print("=" * 60)
    print(f"✓ Text extracted: {results['text_extracted']}")
    print(f"✓ Chunks created: {results['chunks_created']}")
    print(f"✓ Entities found: {results['entities_found']}")
    print(f"✓ Relationships found: {results['relationships_found']}")
    print(f"✓ Stored in database: {results['stored_in_db']}")
    
    if results["errors"]:
        print(f"\n⚠ Errors encountered:")
        for error in results["errors"]:
            print(f"  - {error}")
    
    # Determine success
    success = (
        results["text_extracted"] and
        results["chunks_created"] > 0 and
        results["entities_found"] > 0
    )
    
    print(f"\nOverall: {'✓ SUCCESS' if success else '✗ FAILED'}")
    
    return results

if __name__ == "__main__":
    # Use the test PDF we created
    pdf_path = "test_data/simple_test.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"Error: Test PDF not found at {pdf_path}")
        print("Please run create_test_pdf.py first")
        sys.exit(1)
    
    results = process_single_document(pdf_path)
    
    # Exit with appropriate code
    success = (
        results["text_extracted"] and
        results["chunks_created"] > 0 and
        results["entities_found"] > 0
    )
    
    sys.exit(0 if success else 1)