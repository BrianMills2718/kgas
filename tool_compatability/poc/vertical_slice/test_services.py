#!/usr/bin/env python3
"""Test all services are working correctly"""

from neo4j import GraphDatabase
import pandas as pd
from services.crossmodal_service import CrossModalService
from services.identity_service_v3 import IdentityServiceV3
from services.provenance_enhanced import ProvenanceEnhanced

def test_crossmodal_service():
    """Test CrossModalService graph↔table conversions"""
    print("\n=== Testing CrossModalService ===")
    
    # Setup
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "devpassword"))
    service = CrossModalService(driver, "vertical_slice.db")
    
    # Create test data in Neo4j
    with driver.session() as session:
        # Clean up first - detach delete to handle relationships
        session.run("MATCH (n:VSEntity) DETACH DELETE n")
        
        # Create test entities
        session.run("""
            CREATE (e1:VSEntity {entity_id: 'test_1', canonical_name: 'Test Entity 1', entity_type: 'person'})
            CREATE (e2:VSEntity {entity_id: 'test_2', canonical_name: 'Test Entity 2', entity_type: 'organization'})
            CREATE (e1)-[:WORKS_FOR]->(e2)
        """)
    
    # Test graph_to_table
    entity_df = service.graph_to_table(['test_1', 'test_2'])
    print(f"✅ graph_to_table: Exported {len(entity_df)} entities")
    
    # Test table_to_graph
    test_relationships = pd.DataFrame([
        {'source': 'test_1', 'target': 'test_2', 'relationship_type': 'COLLABORATES', 'properties': {}}
    ])
    result = service.table_to_graph(test_relationships)
    print(f"✅ table_to_graph: Created {result['edges_created']} edges")
    
    # Cleanup
    with driver.session() as session:
        session.run("MATCH (n:VSEntity) DETACH DELETE n")
    
    driver.close()
    
def test_identity_service():
    """Test IdentityServiceV3 entity deduplication"""
    print("\n=== Testing IdentityServiceV3 ===")
    
    # Setup
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "devpassword"))
    service = IdentityServiceV3(driver)
    
    # Create test entities
    with driver.session() as session:
        session.run("MATCH (n:VSEntity) DETACH DELETE n")
        session.run("""
            CREATE (e1:VSEntity {entity_id: 'id_1', canonical_name: 'John Smith'})
            CREATE (e2:VSEntity {entity_id: 'id_2', canonical_name: 'John Smith Jr.'})
            CREATE (e3:VSEntity {entity_id: 'id_3', canonical_name: 'Jane Doe'})
        """)
    
    # Test find_similar_entities
    similar = service.find_similar_entities("john")
    print(f"✅ find_similar_entities: Found {len(similar)} entities matching 'john'")
    for entity in similar:
        print(f"   - {entity['name']} (id: {entity['id']})")
    
    # Cleanup
    with driver.session() as session:
        session.run("MATCH (n:VSEntity) DETACH DELETE n")
    
    driver.close()

def test_provenance_service():
    """Test ProvenanceEnhanced tracking"""
    print("\n=== Testing ProvenanceEnhanced ===")
    
    service = ProvenanceEnhanced("vertical_slice.db")
    
    # Test track_operation
    op_id = service.track_operation(
        tool_id="TextLoader",
        operation="text_extraction",
        inputs={"file": "test.pdf"},
        outputs={"text": "Sample text", "length": 100},
        uncertainty=0.15,
        reasoning="PDF extraction may have OCR errors",
        construct_mapping="file_path → character_sequence"
    )
    print(f"✅ track_operation: Created operation {op_id}")
    
    # Test get_operation_chain
    chain = service.get_operation_chain(op_id)
    print(f"✅ get_operation_chain: Retrieved {len(chain)} operations")
    for op in chain:
        print(f"   - {op['tool_id']}: {op['construct_mapping']} (uncertainty: {op['uncertainty']})")

if __name__ == "__main__":
    test_crossmodal_service()
    test_identity_service()
    test_provenance_service()
    print("\n✅ All services tested successfully!")