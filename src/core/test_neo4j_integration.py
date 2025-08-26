#!/usr/bin/env python3
"""
Test Neo4j Graph Builder Integration
REAL DATABASE TEST - No mocks
"""

import sys
import os
from pathlib import Path
sys.path.append('/home/brian/projects/Digimons')

# Set Neo4j environment
os.environ['NEO4J_PASSWORD'] = 'devpassword'
os.environ['NEO4J_URI'] = 'bolt://localhost:7687'
os.environ['NEO4J_USER'] = 'neo4j'

from src.core.composition_service import CompositionService
from src.core.adapter_factory import UniversalAdapterFactory
from src.tools.neo4j_graph_builder import Neo4jGraphBuilder
from neo4j import GraphDatabase

def verify_neo4j_nodes():
    """Verify nodes were actually created in Neo4j"""
    driver = GraphDatabase.driver(
        'bolt://localhost:7687',
        auth=('neo4j', 'devpassword')
    )
    
    with driver.session() as session:
        # Count framework nodes
        result = session.run("""
            MATCH (n:Entity {created_by: 'framework_poc'})
            RETURN count(n) as count, collect(n.name) as names
        """)
        record = result.single()
        count = record['count']
        names = record['names']
        
    driver.close()
    return count, names

def test_neo4j_integration():
    """Test Neo4jGraphBuilder through composition service"""
    
    print("="*60)
    print("NEO4J GRAPH BUILDER INTEGRATION TEST")
    print("="*60)
    
    # 1. Create composition service
    service = CompositionService()
    service.adapter_factory = UniversalAdapterFactory()
    print("✅ CompositionService created")
    
    try:
        # 2. Create Neo4j graph builder
        builder = Neo4jGraphBuilder()
        print("✅ Neo4jGraphBuilder instantiated (connected to Neo4j)")
    except RuntimeError as e:
        print(f"❌ Failed to create builder: {e}")
        return False
    
    # 3. Register it
    print("\n1. Registering Neo4jGraphBuilder...")
    success = service.register_any_tool(builder)
    
    if success:
        print("   ✅ Neo4jGraphBuilder registered successfully")
    else:
        print("   ❌ Registration failed")
        return False
    
    # 4. Get initial node count
    initial_count, _ = verify_neo4j_nodes()
    print(f"\n2. Initial Neo4j state:")
    print(f"   Framework nodes before: {initial_count}")
    
    # 5. Test with real entities
    print("\n3. Creating graph from entities...")
    
    # Sample entities (as would come from Gemini)
    test_entities = {
        'entities': [
            {'text': 'Apple Inc.', 'type': 'ORGANIZATION', 'confidence': 0.95},
            {'text': 'Tim Cook', 'type': 'PERSON', 'confidence': 0.98},
            {'text': 'Cupertino', 'type': 'LOCATION', 'confidence': 0.9},
            {'text': 'Microsoft', 'type': 'ORGANIZATION', 'confidence': 0.93},
            {'text': 'Satya Nadella', 'type': 'PERSON', 'confidence': 0.96}
        ]
    }
    
    print(f"   Input: {len(test_entities['entities'])} entities")
    
    try:
        # Call Neo4j builder directly
        result = builder.process(test_entities)
        
        print("\n4. REAL Neo4j Write Results:")
        print(f"   Success: {result['success']}")
        print(f"   Nodes created: {result['nodes_created']}")
        print(f"   Relationships created: {result['relationships_created']}")
        print(f"   Total framework nodes: {result['total_framework_nodes']}")
        print(f"   Neo4j URI: {result['neo4j_uri']}")
        print(f"   Created by: {result['created_by']}")
        
        if result['success']:
            print("\n   ✅ Neo4j graph successfully created")
        else:
            print(f"\n   ❌ Graph creation failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"\n   ❌ Neo4j operation failed: {e}")
        return False
    
    # 6. Verify with actual Neo4j query
    print("\n5. Verification with Cypher Query:")
    
    final_count, node_names = verify_neo4j_nodes()
    nodes_added = final_count - initial_count
    
    print(f"   Framework nodes after: {final_count}")
    print(f"   Nodes added: {nodes_added}")
    
    if node_names and nodes_added > 0:
        print(f"\n   Nodes in Neo4j:")
        for name in node_names[-5:]:  # Show last 5
            print(f"      - {name}")
        print("\n   ✅ Verified: Nodes exist in Neo4j database")
    else:
        print("\n   ❌ No nodes found in Neo4j")
    
    # 7. Check framework integration
    print("\n6. Framework Integration Check:")
    
    if "Neo4jGraphBuilder" in service.framework.tools:
        print("   ✅ Neo4jGraphBuilder in framework registry")
        
        adapted_tool = service.framework.tools.get("Neo4jGraphBuilder")
        if adapted_tool:
            caps = adapted_tool.get_capabilities()
            print(f"   Input Type: {caps.input_type}")
            print(f"   Output Type: {caps.output_type}")
    
    # 8. Cleanup
    builder.cleanup()
    print("\n7. Cleanup:")
    print("   ✅ Neo4j connection closed")
    
    print("\n" + "="*60)
    print("NEO4J INTEGRATION TEST COMPLETE")
    print("="*60)
    
    return nodes_added > 0

if __name__ == "__main__":
    success = test_neo4j_integration()
    sys.exit(0 if success else 1)