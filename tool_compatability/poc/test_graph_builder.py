#!/usr/bin/env python3
"""Test GraphBuilder with Neo4j"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from poc.tools.graph_builder import GraphBuilder
from poc.data_types import DataSchema

def test_graph_builder():
    print("="*60)
    print("GRAPH BUILDER TEST")
    print("="*60)
    
    # Create test entities
    import hashlib
    from datetime import datetime
    import uuid
    
    # Use unique IDs to avoid conflicts
    test_id = str(uuid.uuid4())[:8]
    
    entities_data = DataSchema.EntitiesData(
        entities=[
            DataSchema.Entity(
                id=f"e1_{test_id}",
                text="John Smith",
                type="PERSON",
                confidence=0.95,
                metadata={"role": "CEO"}
            ),
            DataSchema.Entity(
                id=f"e2_{test_id}",
                text="TechCorp",
                type="ORG",
                confidence=0.90,
                metadata={"industry": "Technology"}
            ),
            DataSchema.Entity(
                id=f"e3_{test_id}",
                text="San Francisco",
                type="LOCATION",
                confidence=0.88,
                metadata={"country": "USA"}
            ),
        ],
        relationships=[
            DataSchema.Relationship(
                source_id=f"e1_{test_id}",
                target_id=f"e2_{test_id}",
                relation_type="WORKS_FOR",
                confidence=0.92,
                metadata={"position": "CEO"}
            ),
            DataSchema.Relationship(
                source_id=f"e2_{test_id}",
                target_id=f"e3_{test_id}",
                relation_type="LOCATED_IN",
                confidence=0.85,
                metadata={"headquarters": True}
            ),
        ],
        source_checksum=hashlib.md5(b"test content").hexdigest(),
        extraction_model="manual",
        extraction_timestamp=datetime.now().isoformat()
    )
    
    # Test GraphBuilder
    builder = GraphBuilder()
    print(f"\nTool: {builder.tool_id}")
    print(f"Input: {builder.input_type}")
    print(f"Output: {builder.output_type}")
    
    print("\nProcessing entities...")
    result = builder.process(entities_data)
    
    if result.success:
        print(f"✅ Success!")
        print(f"  Graph ID: {result.data.graph_id}")
        print(f"  Nodes: {result.data.node_count}")
        print(f"  Edges: {result.data.edge_count}")
        print(f"  Metadata: {result.data.metadata}")
        
        # Query the graph to verify
        print("\nVerifying in Neo4j...")
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "devpassword")
        )
        
        with driver.session() as session:
            # Count nodes
            node_result = session.run("MATCH (n) RETURN count(n) as count")
            node_count = node_result.single()["count"]
            print(f"  Actual nodes in Neo4j: {node_count}")
            
            # Count relationships
            rel_result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            rel_count = rel_result.single()["count"]
            print(f"  Actual relationships in Neo4j: {rel_count}")
            
            # Show some nodes
            nodes_result = session.run("MATCH (n) RETURN n.name as name, labels(n) as labels LIMIT 5")
            print("\n  Sample nodes:")
            for record in nodes_result:
                print(f"    - {record['name']}: {record['labels']}")
        
        driver.close()
        return True
    else:
        print(f"❌ Failed: {result.error}")
        return False

if __name__ == "__main__":
    success = test_graph_builder()
    sys.exit(0 if success else 1)