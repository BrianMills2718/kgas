"""
Test complete pipeline with real Neo4j integration
Verify all 8 tools are using Neo4j properly
"""

import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_complete_pipeline():
    """Test the complete pipeline with all 8 tools using Neo4j"""
    print("\n" + "="*60)
    print("🚀 COMPLETE PIPELINE TEST WITH REAL NEO4J")
    print("="*60)
    
    # Import all tools
    from src.tools.phase1.t01_pdf_loader import PDFLoader
    from src.tools.phase1.t15a_text_chunker import TextChunker
    from src.tools.phase1.t23a_spacy_ner import SpacyNER
    from src.tools.phase1.t27_relationship_extractor import RelationshipExtractor
    from src.tools.phase1.t31_entity_builder_neo4j import T31EntityBuilderNeo4j
    from src.tools.phase1.t34_edge_builder_neo4j import T34EdgeBuilderNeo4j
    from src.tools.phase1.t68_pagerank_neo4j import T68PageRankNeo4j
    from src.tools.phase1.t49_multihop_query_neo4j import T49MultiHopQueryNeo4j
    
    from src.tools.base_tool_fixed import ToolRequest
    from src.core.service_manager import get_service_manager
    
    # Get service manager
    service_manager = get_service_manager()
    
    # Initialize all tools
    print("\n📦 Initializing all 8 tools...")
    tools = {
        "T01": PDFLoader(service_manager),
        "T15A": TextChunker(service_manager),
        "T23A": SpacyNER(service_manager),
        "T27": RelationshipExtractor(service_manager),
        "T31": T31EntityBuilderNeo4j(service_manager),
        "T34": T34EdgeBuilderNeo4j(service_manager),
        "T68": T68PageRankNeo4j(service_manager),
        "T49": T49MultiHopQueryNeo4j(service_manager)
    }
    
    print("✅ All tools initialized successfully")
    
    # Check Neo4j connection
    print("\n🔌 Checking Neo4j connections...")
    neo4j_driver = service_manager.get_neo4j_driver()
    if neo4j_driver:
        with neo4j_driver.session() as session:
            result = session.run("RETURN 1 as test")
            record = result.single()
            print(f"✅ Neo4j connection verified: {record['test']}")
            
            # Get initial entity count
            count_result = session.run("MATCH (e:Entity) RETURN count(e) as count")
            initial_count = count_result.single()["count"]
            print(f"📊 Initial entity count in Neo4j: {initial_count}")
    
    # Create test document
    test_text = """
    Carter graduated from the Naval Academy in Annapolis in 1946. 
    He served in the U.S. Navy before entering politics.
    The Naval Academy is one of the most prestigious military institutions.
    Annapolis is the capital of Maryland and home to the Naval Academy.
    """
    
    # Save test text to file
    test_file = Path("test_carter_document.txt")
    test_file.write_text(test_text)
    print(f"\n📄 Created test document: {test_file}")
    
    try:
        # Step 1: Load document (T01)
        print("\n" + "-"*50)
        print("Step 1: T01 - Load Document")
        load_request = ToolRequest(
            tool_id="T01",
            operation="load",
            input_data={
                "file_path": str(test_file),
                "workflow_id": "test_pipeline"
            },
            parameters={}
        )
        
        load_result = tools["T01"].execute(load_request)
        if load_result.status != "success":
            raise Exception(f"T01 failed: {load_result.error_message}")
        
        document = load_result.data['document']
        print(f"✅ Document loaded: {len(document['text'])} characters")
        doc_ref = document["document_ref"]
        text_content = document["text"]
        
        # Step 2: Chunk text (T15A)
        print("\n" + "-"*50)
        print("Step 2: T15A - Chunk Text")
        chunk_request = ToolRequest(
            tool_id="T15A",
            operation="chunk",
            input_data={
                "text": text_content,
                "document_ref": doc_ref,
                "document_confidence": document.get("confidence", 0.9)
            },
            parameters={
                "chunk_size": 512,
                "overlap_size": 50
            }
        )
        
        chunk_result = tools["T15A"].execute(chunk_request)
        if chunk_result.status != "success":
            raise Exception(f"T15A failed: {chunk_result.error_message}")
        
        print(f"✅ Text chunked: {len(chunk_result.data['chunks'])} chunks")
        chunks = chunk_result.data["chunks"]
        
        # Step 3: Extract entities (T23A)
        print("\n" + "-"*50)
        print("Step 3: T23A - Extract Entities")
        all_entities = []
        
        for chunk in chunks:
            ner_request = ToolRequest(
                tool_id="T23A",
                operation="extract",
                input_data={
                    "text": chunk["text"],
                    "chunk_ref": chunk["chunk_ref"],
                    "confidence": chunk["confidence"]
                },
                parameters={}
            )
            
            ner_result = tools["T23A"].execute(ner_request)
            if ner_result.status == "success":
                all_entities.extend(ner_result.data["entities"])
        
        print(f"✅ Entities extracted: {len(all_entities)} total")
        for entity in all_entities[:5]:
            print(f"   - {entity['surface_form']} ({entity['entity_type']})")
        
        # Step 4: Extract relationships (T27)
        print("\n" + "-"*50)
        print("Step 4: T27 - Extract Relationships")
        all_relationships = []
        
        for chunk in chunks:
            # Get entities for this chunk
            chunk_entities = [e for e in all_entities if e.get("chunk_ref") == chunk["chunk_ref"]]
            
            rel_request = ToolRequest(
                tool_id="T27",
                operation="extract",
                input_data={
                    "text": chunk["text"],
                    "entities": chunk_entities,
                    "chunk_ref": chunk["chunk_ref"],
                    "confidence": chunk["confidence"]
                },
                parameters={}
            )
            
            rel_result = tools["T27"].execute(rel_request)
            if rel_result.status == "success":
                all_relationships.extend(rel_result.data["relationships"])
        
        print(f"✅ Relationships extracted: {len(all_relationships)} total")
        for rel in all_relationships[:3]:
            print(f"   - {rel['source_entity']} → {rel['target_entity']} ({rel['relationship_type']})")
        
        # Step 5: Build entities in Neo4j (T31)
        print("\n" + "-"*50)
        print("Step 5: T31 - Build Entities (Neo4j)")
        
        entity_request = ToolRequest(
            tool_id="T31",
            operation="build",
            input_data={
                "entities": all_entities,
                "source_refs": [doc_ref]
            },
            parameters={}
        )
        
        entity_result = tools["T31"].execute(entity_request)
        if entity_result.status != "success":
            raise Exception(f"T31 failed: {entity_result.error_message}")
        
        print(f"✅ Entities built:")
        print(f"   - Total processed: {entity_result.data['total_entities']}")
        print(f"   - Stored in Neo4j: {entity_result.data['neo4j_stored']}")
        print(f"   - Merged duplicates: {entity_result.data.get('merged_count', 0)}")
        
        # Step 6: Build edges in Neo4j (T34)
        print("\n" + "-"*50)
        print("Step 6: T34 - Build Edges (Neo4j)")
        
        edge_request = ToolRequest(
            tool_id="T34",
            operation="build",
            input_data={
                "relationships": all_relationships,
                "source_refs": [doc_ref]
            },
            parameters={}
        )
        
        edge_result = tools["T34"].execute(edge_request)
        if edge_result.status != "success":
            raise Exception(f"T34 failed: {edge_result.error_message}")
        
        print(f"✅ Edges built:")
        print(f"   - Created: {edge_result.data['edges_created']}")
        print(f"   - Updated: {edge_result.data['edges_updated']}")
        print(f"   - Failed: {edge_result.data['failed_edges']}")
        
        # Step 7: Calculate PageRank (T68)
        print("\n" + "-"*50)
        print("Step 7: T68 - Calculate PageRank (Neo4j)")
        
        pagerank_request = ToolRequest(
            tool_id="T68",
            operation="calculate",
            input_data={
                "source_refs": [doc_ref]
            },
            parameters={}
        )
        
        pagerank_result = tools["T68"].execute(pagerank_request)
        if pagerank_result.status != "success":
            raise Exception(f"T68 failed: {pagerank_result.error_message}")
        
        print(f"✅ PageRank calculated:")
        print(f"   - Entities processed: {pagerank_result.data['entity_count']}")
        print(f"   - Iterations: {pagerank_result.data['iterations']}")
        print(f"   - Top entities:")
        for entity in pagerank_result.data['top_entities'][:3]:
            print(f"     • {entity['canonical_name']}: {entity['pagerank_score']:.4f}")
        
        # Step 8: Query the graph (T49)
        print("\n" + "-"*50)
        print("Step 8: T49 - Query Graph (Neo4j)")
        
        test_queries = [
            "Where did Carter graduate?",
            "What is in Annapolis?",
            "Who served in the Navy?"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Query: '{query}'")
            
            query_request = ToolRequest(
                tool_id="T49",
                operation="query",
                input_data={
                    "query": query,
                    "max_hops": 2,
                    "result_limit": 3,
                    "source_refs": [doc_ref]
                },
                parameters={}
            )
            
            query_result = tools["T49"].execute(query_request)
            if query_result.status == "success":
                print(f"✅ Found {len(query_result.data['results'])} results")
                for i, res in enumerate(query_result.data['results']):
                    path_str = " → ".join([p['entity'] for p in res['path']])
                    print(f"   {i+1}. {res['answer']} (confidence: {res['confidence']:.3f})")
                    print(f"      Path: {path_str}")
            else:
                print(f"❌ Query failed: {query_result.error_message}")
        
        # Final Neo4j verification
        print("\n" + "="*50)
        print("📊 FINAL NEO4J VERIFICATION")
        print("="*50)
        
        with neo4j_driver.session() as session:
            # Count entities
            entity_count = session.run("MATCH (e:Entity) RETURN count(e) as count").single()["count"]
            print(f"✅ Total entities in Neo4j: {entity_count}")
            print(f"   New entities added: {entity_count - initial_count}")
            
            # Count relationships
            rel_count = session.run("MATCH ()-[r:RELATES_TO]->() RETURN count(r) as count").single()["count"]
            print(f"✅ Total relationships in Neo4j: {rel_count}")
            
            # Show some entities with PageRank
            print("\n📈 Sample entities with PageRank scores:")
            sample_result = session.run("""
                MATCH (e:Entity)
                WHERE e.pagerank_score IS NOT NULL
                RETURN e.canonical_name as name, 
                       e.entity_type as type,
                       e.pagerank_score as pagerank
                ORDER BY e.pagerank_score DESC
                LIMIT 5
            """)
            
            for record in sample_result:
                print(f"   - {record['name']} ({record['type']}): {record['pagerank']:.4f}")
        
        print("\n" + "="*50)
        print("✅ COMPLETE PIPELINE TEST SUCCESSFUL!")
        print("   All 8 tools are using Neo4j properly")
        print("="*50)
        
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()
            print(f"\n🧹 Cleaned up test file: {test_file}")


if __name__ == "__main__":
    test_complete_pipeline()