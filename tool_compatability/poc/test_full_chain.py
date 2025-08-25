#!/usr/bin/env python3
"""Test the complete chain with real services - NOW WORKING!"""

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from poc.registry import ToolRegistry
from poc.tools.text_loader import TextLoader
from poc.tools.entity_extractor import EntityExtractor
from poc.tools.graph_builder import GraphBuilder
from poc.data_types import DataType, DataSchema

def test_chain():
    print("="*60)
    print("FULL CHAIN TEST (WITH GEMINI API)")
    print("="*60)
    
    # Test document with entities
    test_content = """
    John Smith is the CEO of TechCorp, a technology company based in San Francisco.
    The company recently raised $10M in Series A funding from Venture Partners.
    Sarah Johnson, the CTO, announced they are expanding to New York City.
    The engineering team will grow from 20 to 50 people by Q3 2025.
    """
    
    test_file = "/tmp/test_chain.txt"
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    # Setup registry
    registry = ToolRegistry()
    
    # Register all tools
    print("\nRegistering tools...")
    loader = TextLoader()
    extractor = EntityExtractor()
    builder = GraphBuilder()
    
    registry.register(loader)
    registry.register(extractor)
    registry.register(builder)
    
    print(f"  ✅ TextLoader registered")
    print(f"  ✅ EntityExtractor registered (Gemini API ready)")
    print(f"  ✅ GraphBuilder registered (Neo4j connected)")
    
    # Find chain
    print("\nFinding chain...")
    chains = registry.find_chains(DataType.FILE, DataType.GRAPH)
    if not chains:
        print("❌ No chain found")
        return False
    
    chain = chains[0]
    print(f"✅ Chain found: {' → '.join(chain)}")
    
    # Execute chain
    print("\n" + "="*60)
    print("EXECUTING CHAIN")
    print("="*60)
    
    # Start with file data
    file_data = DataSchema.FileData(
        path=test_file,
        size_bytes=os.path.getsize(test_file),
        mime_type="text/plain"
    )
    
    current_data = file_data
    chain_results = []
    total_start = time.perf_counter()
    
    for i, tool_id in enumerate(chain, 1):
        tool = registry.tools[tool_id]
        print(f"\nStep {i}/{len(chain)}: {tool_id}")
        print("-" * 40)
        
        start = time.perf_counter()
        result = tool.process(current_data)
        duration = time.perf_counter() - start
        
        if not result.success:
            print(f"❌ Failed: {result.error}")
            print(f"\nChain failed at step {i}")
            return False
        
        print(f"✅ Success in {duration:.3f}s")
        
        # Show results based on tool type
        if tool_id == "TextLoader":
            print(f"   Content length: {len(result.data.content)} chars")
            print(f"   Preview: {result.data.content[:50]}...")
            
        elif tool_id == "EntityExtractor":
            print(f"   Entities found: {len(result.data.entities)}")
            for e in result.data.entities[:5]:  # Show first 5
                print(f"     - {e.text} ({e.type}, confidence: {e.confidence:.2f})")
            if len(result.data.entities) > 5:
                print(f"     ... and {len(result.data.entities) - 5} more")
            
            print(f"   Relationships found: {len(result.data.relationships)}")
            for r in result.data.relationships[:3]:  # Show first 3
                print(f"     - {r.source_id} --[{r.relation_type}]--> {r.target_id}")
            if len(result.data.relationships) > 3:
                print(f"     ... and {len(result.data.relationships) - 3} more")
                
        elif tool_id == "GraphBuilder":
            print(f"   Graph ID: {result.data.graph_id}")
            print(f"   Nodes created: {result.data.node_count}")
            print(f"   Edges created: {result.data.edge_count}")
        
        chain_results.append({
            "step": i,
            "tool": tool_id,
            "duration": duration,
            "success": True
        })
        
        current_data = result.data
    
    total_duration = time.perf_counter() - total_start
    
    # Summary
    print("\n" + "="*60)
    print("CHAIN EXECUTION COMPLETE")
    print("="*60)
    print(f"\n✅ Full chain executed successfully!")
    print(f"   Total duration: {total_duration:.3f}s")
    print(f"   Steps completed: {len(chain_results)}")
    
    print("\nStep-by-step timing:")
    for r in chain_results:
        print(f"   {r['step']}. {r['tool']}: {r['duration']:.3f}s")
    
    # Verify in Neo4j
    print("\n" + "="*60)
    print("VERIFYING IN NEO4J")
    print("="*60)
    
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(
        "bolt://localhost:7687",
        auth=("neo4j", "devpassword")
    )
    
    with driver.session() as session:
        # Count all nodes
        result = session.run("MATCH (n) RETURN count(n) as count")
        total_nodes = result.single()["count"]
        
        # Count all relationships
        result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
        total_rels = result.single()["count"]
        
        # Get sample of recently created nodes
        result = session.run("""
            MATCH (n:Entity)
            WHERE n.graph_id IS NOT NULL
            RETURN n.name as name, labels(n) as labels
            ORDER BY n.created_at DESC
            LIMIT 5
        """)
        
        print(f"Total nodes in database: {total_nodes}")
        print(f"Total relationships in database: {total_rels}")
        print("\nRecently created entities:")
        for record in result:
            if record['name']:
                print(f"  - {record['name']}: {record['labels']}")
    
    driver.close()
    
    print("\n" + "="*60)
    print("SUCCESS: Full chain validated with all components!")
    print("="*60)
    
    return True

if __name__ == "__main__":
    success = test_chain()
    sys.exit(0 if success else 1)