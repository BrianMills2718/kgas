#!/usr/bin/env python3
"""
Test real tools with actual Neo4j database
Test Driven Design: Define expected behavior first
"""

import sys
import os
import json
from datetime import datetime
sys.path.insert(0, '/home/brian/projects/Digimons')

from neo4j import GraphDatabase
from src.core.service_manager import ServiceManager
from src.core.tool_contract import ToolRequest, ToolResult
from src.tools.phase2.t23c_ontology_aware_extractor_unified import OntologyAwareExtractor as T23COntologyAwareExtractor
from src.tools.phase1.t31_entity_builder_unified import T31EntityBuilderUnified
from src.tools.phase1.t34_edge_builder import EdgeBuilder as T34EdgeBuilder
from src.tools.phase1.t68_pagerank_unified import T68PageRankCalculatorUnified as T68PageRank

class Neo4jTestHelper:
    """Helper for Neo4j operations"""
    
    def __init__(self):
        self.driver = GraphDatabase.driver(
            os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
            auth=(os.getenv('NEO4J_USER', 'neo4j'),
                  os.getenv('NEO4J_PASSWORD', 'password'))  # Using docker-compose password
        )
    
    def cleanup_database(self):
        """Clean the database"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            result = session.run("MATCH (n) RETURN count(n) as count")
            count = result.single()["count"]
            return count == 0
    
    def count_nodes(self):
        """Count nodes in database"""
        with self.driver.session() as session:
            result = session.run("MATCH (n) RETURN count(n) as count")
            return result.single()["count"]
    
    def count_relationships(self):
        """Count relationships in database"""
        with self.driver.session() as session:
            result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            return result.single()["count"]
    
    def get_node_samples(self, limit=5):
        """Get sample nodes"""
        with self.driver.session() as session:
            result = session.run(f"MATCH (n) RETURN n LIMIT {limit}")
            nodes = []
            for record in result:
                node = record["n"]
                nodes.append({
                    "labels": list(node.labels),
                    "properties": dict(node)
                })
            return nodes
    
    def close(self):
        """Close driver"""
        self.driver.close()

def test_t31_entity_creation():
    """Test real T31 entity creation"""
    print("\n" + "=" * 60)
    print("TEST: T31 Entity Creation with Neo4j")
    print("=" * 60)
    
    # Setup
    neo4j = Neo4jTestHelper()
    service_manager = ServiceManager()
    t31 = T31EntityBuilderUnified(service_manager)
    
    # Clean database
    print("\n1. Cleaning database...")
    if neo4j.cleanup_database():
        print("✅ Database cleaned")
    else:
        print("❌ Database cleanup failed")
        return False
    
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
        },
        {
            "text": "Cupertino",
            "entity_type": "LOCATION",
            "confidence": 0.85,
            "start": 40,
            "end": 49
        }
    ]
    
    # Execute T31
    print("\n2. Creating entities with T31...")
    request = ToolRequest(input_data={"mentions": test_mentions})
    result = t31.execute(request)
    
    if result.status == "success":
        entities_created = len(result.data.get("entities", []))
        print(f"✅ T31 created {entities_created} entities")
        
        # Verify in database
        node_count = neo4j.count_nodes()
        print(f"   Database has {node_count} nodes")
        
        if node_count == entities_created:
            print("✅ Entity count matches database")
            
            # Show sample nodes
            samples = neo4j.get_node_samples(3)
            for sample in samples:
                print(f"   - {sample['labels']}: {sample['properties'].get('canonical_name', 'N/A')}")
            
            neo4j.close()
            return True
        else:
            print(f"❌ Mismatch: T31 created {entities_created} but database has {node_count}")
            neo4j.close()
            return False
    else:
        print(f"❌ T31 failed: {result.error_message}")
        neo4j.close()
        return False

def test_t34_edge_creation():
    """Test real T34 edge creation"""
    print("\n" + "=" * 60)
    print("TEST: T34 Edge Creation with Neo4j")
    print("=" * 60)
    
    # Setup
    neo4j = Neo4jTestHelper()
    service_manager = ServiceManager()
    t31 = T31EntityBuilderUnified(service_manager)
    t34 = T34EdgeBuilder(service_manager)
    
    # Clean and setup entities
    print("\n1. Setting up test entities...")
    neo4j.cleanup_database()
    
    # Create entities first
    test_mentions = [
        {"text": "Apple", "entity_type": "ORGANIZATION", "confidence": 0.95},
        {"text": "Tim Cook", "entity_type": "PERSON", "confidence": 0.90},
        {"text": "Microsoft", "entity_type": "ORGANIZATION", "confidence": 0.95}
    ]
    
    t31_request = ToolRequest(input_data={"mentions": test_mentions})
    t31_result = t31.execute(t31_request)
    
    if t31_result.status != "success":
        print(f"❌ Failed to create entities: {t31_result.error_message}")
        neo4j.close()
        return False
    
    entities = t31_result.data.get("entities", [])
    print(f"✅ Created {len(entities)} entities")
    
    # Create relationships (T34 expects entity objects with 'text' field)
    # Map entity text to entity objects and ensure 'text' field exists
    entity_map = {}
    for e in entities:
        name = e.get("canonical_name", e.get("text", ""))
        # Ensure entity has 'text' field for T34
        if "text" not in e:
            e["text"] = e.get("canonical_name", "")
        entity_map[name] = e
    
    test_relationships = [
        {
            "subject": entity_map.get("Apple", {"text": "Apple", "canonical_name": "Apple"}),
            "relationship_type": "LED_BY",
            "object": entity_map.get("Tim Cook", {"text": "Tim Cook", "canonical_name": "Tim Cook"}),
            "confidence": 0.9
        },
        {
            "subject": entity_map.get("Apple", {"text": "Apple", "canonical_name": "Apple"}),
            "relationship_type": "COMPETES_WITH",
            "object": entity_map.get("Microsoft", {"text": "Microsoft", "canonical_name": "Microsoft"}),
            "confidence": 0.85
        }
    ]
    
    print("\n2. Creating edges with T34...")
    t34_request = ToolRequest(input_data={
        "entities": entities,
        "relationships": test_relationships
    })
    t34_result = t34.execute(t34_request)
    
    if t34_result.status == "success":
        edges_created = len(t34_result.data.get("edges", []))
        print(f"✅ T34 created {edges_created} edges")
        
        # Verify in database
        rel_count = neo4j.count_relationships()
        print(f"   Database has {rel_count} relationships")
        
        if rel_count == edges_created:
            print("✅ Edge count matches database")
            neo4j.close()
            return True
        else:
            print(f"❌ Mismatch: T34 created {edges_created} but database has {rel_count}")
            neo4j.close()
            return False
    else:
        print(f"❌ T34 failed: {t34_result.error_message}")
        neo4j.close()
        return False

def test_t68_pagerank():
    """Test real T68 PageRank computation"""
    print("\n" + "=" * 60)
    print("TEST: T68 PageRank with Neo4j")
    print("=" * 60)
    
    # Setup
    neo4j = Neo4jTestHelper()
    service_manager = ServiceManager()
    t68 = T68PageRank(service_manager)
    
    # Check if we have nodes
    node_count = neo4j.count_nodes()
    if node_count == 0:
        print("❌ No nodes in database to compute PageRank")
        neo4j.close()
        return False
    
    print(f"\n1. Computing PageRank for {node_count} nodes...")
    
    # Execute T68
    t68_request = ToolRequest(input_data={})
    t68_result = t68.execute(t68_request)
    
    if t68_result.status == "success":
        nodes_processed = t68_result.data.get("nodes_processed", 0)
        print(f"✅ T68 processed {nodes_processed} nodes")
        
        # Check if PageRank scores were added
        with neo4j.driver.session() as session:
            result = session.run(
                "MATCH (n) WHERE n.pagerank_score IS NOT NULL "
                "RETURN count(n) as count"
            )
            scored_count = result.single()["count"]
            
            if scored_count > 0:
                print(f"✅ {scored_count} nodes have PageRank scores")
                
                # Show top nodes by PageRank
                result = session.run(
                    "MATCH (n) WHERE n.pagerank_score IS NOT NULL "
                    "RETURN n.canonical_name as name, n.pagerank_score as score "
                    "ORDER BY score DESC LIMIT 3"
                )
                print("\n   Top nodes by PageRank:")
                for record in result:
                    print(f"   - {record['name']}: {record['score']:.4f}")
                
                neo4j.close()
                return True
            else:
                print("❌ No nodes have PageRank scores")
                neo4j.close()
                return False
    else:
        print(f"❌ T68 failed: {t68_result.error_message}")
        neo4j.close()
        return False

def test_complete_pipeline():
    """Test complete pipeline with all real tools"""
    print("\n" + "=" * 60)
    print("TEST: Complete Pipeline with All Real Tools")
    print("=" * 60)
    
    # Setup
    neo4j = Neo4jTestHelper()
    service_manager = ServiceManager()
    
    # Initialize all tools
    t23c = T23COntologyAwareExtractor(service_manager)
    t31 = T31EntityBuilderUnified(service_manager)
    t34 = T34EdgeBuilder(service_manager)
    t68 = T68PageRank(service_manager)
    
    # Clean database
    print("\n1. Cleaning database...")
    neo4j.cleanup_database()
    initial_count = neo4j.count_nodes()
    print(f"✅ Database clean: {initial_count} nodes")
    
    # Test text
    test_text = """
    Apple Inc., led by CEO Tim Cook, is headquartered in Cupertino.
    Microsoft was founded by Bill Gates and Paul Allen in 1975.
    Google competes with Microsoft and Apple in cloud services.
    """
    
    # Step 1: Extract entities with T23C
    print("\n2. Extracting entities with T23C...")
    t23c_request = ToolRequest(input_data={
        "text": test_text,
        "source_ref": "test_document"
    })
    t23c_result = t23c.execute(t23c_request)
    
    if t23c_result.status != "success":
        print(f"❌ T23C failed: {t23c_result.error_message}")
        neo4j.close()
        return False
    
    # Get entities from T23C output and convert to T31 mention format
    t23c_entities = t23c_result.data.get("entities", [])
    mentions = []
    for entity in t23c_entities:
        # Convert T23C entity format to T31 mention format
        mention = {
            "text": entity.get("canonical_name", ""),
            "entity_type": entity.get("entity_type", "UNKNOWN"),
            "confidence": entity.get("confidence", 0.5),
            "start": 0,  # T23C doesn't provide position info
            "end": len(entity.get("canonical_name", ""))
        }
        mentions.append(mention)
    print(f"✅ T23C extracted {len(mentions)} entities")
    
    # Step 2: Create entities with T31
    print("\n3. Creating entities with T31...")
    t31_request = ToolRequest(input_data={"mentions": mentions})
    t31_result = t31.execute(t31_request)
    
    if t31_result.status != "success":
        print(f"❌ T31 failed: {t31_result.error_message}")
        neo4j.close()
        return False
    
    entities = t31_result.data.get("entities", [])
    entity_count = len(entities)
    print(f"✅ T31 created {entity_count} entities")
    
    # Step 3: Extract and create relationships
    print("\n4. Extracting relationships...")
    # Map entity text to entity objects for T34 and ensure 'text' field exists
    entity_map = {}
    for e in entities:
        name = e.get("canonical_name", e.get("text", ""))
        # Ensure entity has 'text' field for T34
        if "text" not in e:
            e["text"] = e.get("canonical_name", "")
        entity_map[name] = e
    
    # Simple relationship extraction (since T27 might not be available)
    relationships = []
    
    if "led by" in test_text and "Apple Inc." in entity_map and "Tim Cook" in entity_map:
        relationships.append({
            "subject": entity_map["Apple Inc."],
            "relationship_type": "LED_BY",
            "object": entity_map["Tim Cook"],
            "confidence": 0.9
        })
    
    if "founded by" in test_text and "Microsoft" in entity_map:
        if "Bill Gates" in entity_map:
            relationships.append({
                "subject": entity_map["Microsoft"],
                "relationship_type": "FOUNDED_BY",
                "object": entity_map["Bill Gates"],
                "confidence": 0.9
            })
        if "Paul Allen" in entity_map:
            relationships.append({
                "subject": entity_map["Microsoft"],
                "relationship_type": "FOUNDED_BY",
                "object": entity_map["Paul Allen"],
                "confidence": 0.9
            })
    
    if "competes with" in test_text and "Google" in entity_map:
        if "Microsoft" in entity_map:
            relationships.append({
                "subject": entity_map["Google"],
                "relationship_type": "COMPETES_WITH",
                "object": entity_map["Microsoft"],
                "confidence": 0.85
            })
        if "Apple" in entity_map:
            relationships.append({
                "subject": entity_map["Google"],
                "relationship_type": "COMPETES_WITH",
                "object": entity_map.get("Apple", entity_map.get("Apple Inc.", {})),
                "confidence": 0.85
            })
    
    print(f"   Found {len(relationships)} relationships")
    
    # Step 4: Create edges with T34
    print("\n5. Creating edges with T34...")
    t34_request = ToolRequest(input_data={
        "entities": entities,
        "relationships": relationships
    })
    t34_result = t34.execute(t34_request)
    
    if t34_result.status != "success":
        print(f"❌ T34 failed: {t34_result.error_message}")
        neo4j.close()
        return False
    
    edges = t34_result.data.get("edges", [])
    print(f"✅ T34 created {len(edges)} edges")
    
    # Step 5: Compute PageRank with T68
    print("\n6. Computing PageRank with T68...")
    t68_request = ToolRequest(input_data={})
    t68_result = t68.execute(t68_request)
    
    if t68_result.status != "success":
        print(f"❌ T68 failed: {t68_result.error_message}")
        neo4j.close()
        return False
    
    nodes_processed = t68_result.data.get("nodes_processed", 0)
    print(f"✅ T68 processed {nodes_processed} nodes")
    
    # Final verification
    print("\n7. Final verification...")
    final_node_count = neo4j.count_nodes()
    final_rel_count = neo4j.count_relationships()
    
    print(f"   Final database state:")
    print(f"   - Nodes: {final_node_count}")
    print(f"   - Relationships: {final_rel_count}")
    
    # Check for contamination
    if nodes_processed == entity_count:
        print(f"✅ No contamination: PageRank nodes ({nodes_processed}) == entities ({entity_count})")
    else:
        print(f"❌ Contamination detected: PageRank nodes ({nodes_processed}) != entities ({entity_count})")
    
    # Generate evidence
    evidence = {
        "timestamp": datetime.now().isoformat(),
        "pipeline": "complete",
        "tools_used": ["T23C", "T31", "T34", "T68"],
        "results": {
            "t23c_entities": len(mentions),
            "t31_entities": entity_count,
            "t34_edges": len(edges),
            "t68_nodes": nodes_processed,
            "final_nodes": final_node_count,
            "final_relationships": final_rel_count,
            "no_contamination": nodes_processed == entity_count
        }
    }
    
    evidence_file = f"experiments/facade_poc/evidence/complete_pipeline_neo4j_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs(os.path.dirname(evidence_file), exist_ok=True)
    with open(evidence_file, 'w') as f:
        json.dump(evidence, f, indent=2)
    print(f"\n✅ Evidence saved to: {evidence_file}")
    
    neo4j.close()
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("REAL TOOLS WITH NEO4J TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("T31 Entity Creation", test_t31_entity_creation),
        ("T34 Edge Creation", test_t34_edge_creation),
        ("T68 PageRank", test_t68_pagerank),
        ("Complete Pipeline", test_complete_pipeline)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED! Real tools pipeline working with Neo4j!")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")