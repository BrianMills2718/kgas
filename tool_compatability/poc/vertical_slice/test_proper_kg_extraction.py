#!/usr/bin/env python3
"""Test proper knowledge graph extraction with entities AND relationships"""

import sys
import os
from dotenv import load_dotenv
load_dotenv('/home/brian/projects/Digimons/.env')

sys.path.append('/home/brian/projects/Digimons')
sys.path.append('/home/brian/projects/Digimons/tool_compatability/poc/vertical_slice')

from framework.clean_framework import CleanToolFramework, ToolCapabilities, DataType
from tools.text_loader_v3 import TextLoaderV3
from tools.knowledge_graph_extractor import KnowledgeGraphExtractor
from tools.graph_persister import GraphPersister

print("="*60)
print("PROPER KNOWLEDGE GRAPH EXTRACTION")
print("="*60)

# Initialize framework
framework = CleanToolFramework(
    neo4j_uri="bolt://localhost:7687",
    sqlite_path="vertical_slice.db"
)

# Clean Neo4j
with framework.neo4j.session() as session:
    session.run("MATCH (n:VSEntity) DETACH DELETE n")
    print("✅ Neo4j cleaned\n")

# Create tools
text_loader = TextLoaderV3()
kg_extractor = KnowledgeGraphExtractor()  # This extracts entities AND relationships
graph_persister = GraphPersister(framework.neo4j, framework.identity, framework.crossmodal)

# Register tools
framework.register_tool(text_loader, ToolCapabilities(
    tool_id="TextLoaderV3",
    input_type=DataType.FILE,
    output_type=DataType.TEXT,
    input_construct="file_path",
    output_construct="character_sequence",
    transformation_type="text_extraction"
))

framework.register_tool(kg_extractor, ToolCapabilities(
    tool_id="KnowledgeGraphExtractor",
    input_type=DataType.TEXT,
    output_type=DataType.KNOWLEDGE_GRAPH,
    input_construct="character_sequence",
    output_construct="knowledge_graph",
    transformation_type="knowledge_graph_extraction"
))

framework.register_tool(graph_persister, ToolCapabilities(
    tool_id="GraphPersister",
    input_type=DataType.KNOWLEDGE_GRAPH,
    output_type=DataType.NEO4J_GRAPH,
    input_construct="knowledge_graph",
    output_construct="persisted_graph",
    transformation_type="graph_persistence"
))

# Create test file with rich content
test_file = "research_paper.txt"
with open(test_file, 'w') as f:
    f.write("""
    The Knowledge Graph Augmentation System (KGAS) was developed by Brian Chhun 
    at the University of Melbourne to address uncertainty propagation in knowledge pipelines.
    
    Dr. Sarah Chen collaborated with Brian on the mathematical foundations, developing
    a physics-style error propagation model where confidence = ∏(1 - uᵢ).
    
    The system integrates with Neo4j for graph storage and utilizes SQLite for metrics.
    CrossModalService, developed by the KGAS team, enables conversions between graph 
    and tabular representations.
    
    The framework was tested on datasets from the Computer Science Department and
    showed promising results with combined uncertainties between 0.25 and 0.45.
    
    Brian presented the system at the AI Conference 2024 in Sydney, where it received
    positive feedback from researchers including Prof. John Smith from MIT.
    """)

print("📄 Input: research_paper.txt")
print("🔧 Pipeline: File → Text → Knowledge Graph → Neo4j\n")

# Execute pipeline
chain = framework.find_chain(DataType.FILE, DataType.NEO4J_GRAPH)
print(f"Chain found: {' → '.join(chain)}\n")

result = framework.execute_chain(chain, test_file)

if result.success:
    print("\n✅ Pipeline executed successfully!")
    print(f"Total uncertainty: {result.total_uncertainty:.3f}")
    print(f"Step uncertainties: {[f'{u:.3f}' for u in result.step_uncertainties]}")
    
    # Check what was extracted and stored
    with framework.neo4j.session() as session:
        # Count entities
        entity_result = session.run("MATCH (n:VSEntity) RETURN count(n) as count")
        entity_count = entity_result.single()['count']
        
        # Count relationships
        rel_result = session.run("MATCH ()-[r]->() WHERE type(r) STARTS WITH 'VS_' RETURN count(r) as count")
        rel_count = rel_result.single()['count']
        
        # Get sample entities
        sample_entities = session.run("""
            MATCH (n:VSEntity) 
            RETURN n.canonical_name as name, n.entity_type as type 
            LIMIT 5
        """)
        
        # Get sample relationships
        sample_rels = session.run("""
            MATCH (s:VSEntity)-[r]->(t:VSEntity)
            WHERE type(r) STARTS WITH 'VS_'
            RETURN s.canonical_name as source, type(r) as type, t.canonical_name as target
            LIMIT 5
        """)
        
        print(f"\n📊 Results in Neo4j:")
        print(f"  Entities: {entity_count}")
        print(f"  Relationships: {rel_count}")
        
        print(f"\n  Sample entities:")
        for record in sample_entities:
            print(f"    - {record['name']} ({record['type']})")
            
        print(f"\n  Sample relationships:")
        for record in sample_rels:
            print(f"    - {record['source']} --[{record['type']}]--> {record['target']}")
    
    print("\n🎯 This is the correct approach:")
    print("  1. Single tool extracts entities AND relationships together")
    print("  2. Maintains context for better relationship extraction")
    print("  3. More efficient (one LLM call instead of multiple)")
    print("  4. Entities and relationships are semantically connected")

# Clean up
os.remove(test_file)
framework.cleanup()

print("\n" + "="*60)
print("✅ DEMONSTRATION COMPLETE")
print("="*60)