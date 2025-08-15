#!/usr/bin/env python3
"""
Test Linear Pipeline (T01 → T15A → T23A → T27 → T31 → T34 → T68 → T49)
This tests the complete standalone pipeline without service dependencies
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "src" / "tools"))

# Import all standalone tools
from phase1.t01_pdf_loader_standalone import T01PDFLoaderStandalone
from phase1.t15a_text_chunker_standalone import T15ATextChunkerStandalone
from phase1.t23a_spacy_ner_standalone import T23ASpacyNERStandalone
from phase1.t27_relationship_extractor_standalone import T27RelationshipExtractorStandalone
from phase1.t31_entity_builder_standalone import T31EntityBuilderStandalone
from phase1.t34_edge_builder_standalone import T34EdgeBuilderStandalone
from phase1.t68_pagerank_standalone import T68PageRankStandalone
from phase1.t49_multihop_query_standalone import T49MultiHopQueryStandalone

from base_tool_fixed import ToolRequest
import json
import time


def test_linear_pipeline():
    """Test the complete linear pipeline with real document"""
    
    print("=" * 80)
    print("TESTING LINEAR PIPELINE: PDF → PageRank → Answer")
    print("=" * 80)
    
    # Initialize all tools
    print("\n📦 Initializing tools...")
    t01_loader = T01PDFLoaderStandalone()
    t15a_chunker = T15ATextChunkerStandalone()
    t23a_ner = T23ASpacyNERStandalone()
    t27_rel_extractor = T27RelationshipExtractorStandalone()
    t31_entity_builder = T31EntityBuilderStandalone()
    t34_edge_builder = T34EdgeBuilderStandalone()
    t68_pagerank = T68PageRankStandalone()
    t49_query = T49MultiHopQueryStandalone()
    
    print("✅ All tools initialized in standalone mode")
    
    # Test file path
    test_file = "/home/brian/projects/Digimons/experiments/lit_review/data/test_texts/carter_anapolis.txt"
    
    # Step 1: Load document
    print(f"\n📄 Step 1: Loading document: {Path(test_file).name}")
    start_time = time.time()
    
    load_request = ToolRequest(
        tool_id="T01",
        operation="load",
        input_data={"file_path": test_file}
    )
    
    load_result = t01_loader.execute(load_request)
    if load_result.status != "success":
        print(f"❌ Loading failed: {load_result.error_message}")
        return False
    
    document = load_result.data["document"]
    print(f"✅ Loaded document: {document['text_length']} characters")
    print(f"   Confidence: {document['confidence']:.2f}")
    
    # Step 2: Chunk text
    print(f"\n📝 Step 2: Chunking text...")
    chunk_request = ToolRequest(
        tool_id="T15A",
        operation="chunk",
        input_data={
            "text": document["text"],
            "document_id": document["document_id"],
            "chunk_size": 100,  # Smaller chunks for testing
            "overlap_size": 20
        }
    )
    
    chunk_result = t15a_chunker.execute(chunk_request)
    if chunk_result.status != "success":
        print(f"❌ Chunking failed: {chunk_result.error_message}")
        return False
    
    chunks = chunk_result.data["chunks"]
    print(f"✅ Created {len(chunks)} chunks")
    
    # Step 3: Extract entities from all chunks
    print(f"\n🔍 Step 3: Extracting entities...")
    all_entities = []
    
    for i, chunk in enumerate(chunks[:5]):  # Process first 5 chunks for speed
        ner_request = ToolRequest(
            tool_id="T23A",
            operation="extract",
            input_data={
                "text": chunk["text"],
                "chunk_ref": chunk["chunk_id"],
                "confidence_threshold": 0.5
            }
        )
        
        ner_result = t23a_ner.execute(ner_request)
        if ner_result.status == "success":
            all_entities.extend(ner_result.data["entities"])
    
    print(f"✅ Extracted {len(all_entities)} entities")
    if all_entities:
        entity_types = {}
        for e in all_entities:
            t = e["entity_type"]
            entity_types[t] = entity_types.get(t, 0) + 1
        print(f"   Types: {entity_types}")
    
    # Step 4: Extract relationships
    print(f"\n🔗 Step 4: Extracting relationships...")
    all_relationships = []
    
    for i, chunk in enumerate(chunks[:5]):  # Process first 5 chunks
        # Get entities for this chunk
        chunk_entities = [e for e in all_entities if e.get("chunk_ref") == chunk["chunk_id"] or i < len(all_entities) // len(chunks[:5])]
        
        if len(chunk_entities) >= 2:
            rel_request = ToolRequest(
                tool_id="T27",
                operation="extract",
                input_data={
                    "text": chunk["text"],
                    "entities": chunk_entities[:10],  # Limit entities per chunk
                    "chunk_ref": chunk["chunk_id"],
                    "confidence_threshold": 0.5
                }
            )
            
            rel_result = t27_rel_extractor.execute(rel_request)
            if rel_result.status == "success":
                all_relationships.extend(rel_result.data["relationships"])
    
    print(f"✅ Extracted {len(all_relationships)} relationships")
    if all_relationships:
        rel_types = {}
        for r in all_relationships:
            t = r["relationship_type"]
            rel_types[t] = rel_types.get(t, 0) + 1
        print(f"   Types: {rel_types}")
    
    # Step 5: Build entities
    print(f"\n🏗️ Step 5: Building graph entities...")
    entity_request = ToolRequest(
        tool_id="T31",
        operation="build",
        input_data={
            "entities": all_entities,
            "source_refs": [document["document_id"]],
            "merge_strategy": "type_aware"
        }
    )
    
    entity_result = t31_entity_builder.execute(entity_request)
    if entity_result.status != "success":
        print(f"❌ Entity building failed: {entity_result.error_message}")
        return False
    
    built_entities = entity_result.data["entities"]
    print(f"✅ Built {len(built_entities)} unique entities (merged {entity_result.data['merged_count']})")
    
    # Step 6: Build edges
    print(f"\n🌉 Step 6: Building graph edges...")
    edge_request = ToolRequest(
        tool_id="T34",
        operation="build",
        input_data={
            "relationships": all_relationships,
            "entities": built_entities,
            "source_refs": [document["document_id"]]
        }
    )
    
    edge_result = t34_edge_builder.execute(edge_request)
    if edge_result.status != "success":
        print(f"❌ Edge building failed: {edge_result.error_message}")
        return False
    
    built_edges = edge_result.data["edges"]
    print(f"✅ Built {len(built_edges)} edges")
    
    # Step 7: Calculate PageRank
    print(f"\n📊 Step 7: Calculating PageRank...")
    pagerank_request = ToolRequest(
        tool_id="T68",
        operation="calculate",
        input_data={
            "entities": built_entities,
            "edges": built_edges,
            "damping_factor": 0.85,
            "max_iterations": 100
        }
    )
    
    pagerank_result = t68_pagerank.execute(pagerank_request)
    if pagerank_result.status != "success":
        print(f"❌ PageRank calculation failed: {pagerank_result.error_message}")
        return False
    
    pagerank_scores = pagerank_result.data["pagerank_scores"]
    top_entities = pagerank_result.data["top_entities"]
    
    print(f"✅ Calculated PageRank for {len(pagerank_scores)} entities")
    print(f"   Top 5 entities by PageRank:")
    for i, entity in enumerate(top_entities[:5]):
        print(f"     {i+1}. {entity['canonical_name']}: {entity['pagerank_score']:.4f}")
    
    # Step 8: Answer queries
    print(f"\n❓ Step 8: Answering queries...")
    
    # Sample queries about the Carter speech
    test_queries = [
        "Who is Carter?",
        "What is the Naval Academy?",
        "Where is Annapolis?",
        "What did Carter discuss?"
    ]
    
    for query_text in test_queries:
        print(f"\n   Query: {query_text}")
        
        query_request = ToolRequest(
            tool_id="T49",
            operation="query",
            input_data={
                "query": query_text,
                "entities": built_entities,
                "edges": built_edges,
                "pagerank_scores": pagerank_scores,
                "max_hops": 2,
                "result_limit": 5
            }
        )
        
        query_result = t49_query.execute(query_request)
        if query_result.status == "success":
            print(f"   Answer: {query_result.data['answer']}")
        else:
            print(f"   ❌ Query failed: {query_result.error_message}")
    
    # Calculate total time
    total_time = time.time() - start_time
    
    print(f"\n" + "=" * 80)
    print(f"✅ LINEAR PIPELINE TEST COMPLETE")
    print(f"   Total execution time: {total_time:.2f} seconds")
    print(f"   Document: {document['text_length']} characters")
    print(f"   Chunks: {len(chunks)}")
    print(f"   Entities: {len(all_entities)} → {len(built_entities)} unique")
    print(f"   Relationships: {len(all_relationships)} → {len(built_edges)} edges")
    print(f"   Top entity: {top_entities[0]['canonical_name'] if top_entities else 'None'}")
    print("=" * 80)
    
    return True


if __name__ == "__main__":
    success = test_linear_pipeline()
    sys.exit(0 if success else 1)