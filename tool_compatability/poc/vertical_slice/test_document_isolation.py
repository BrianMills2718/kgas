#!/usr/bin/env python3
"""Test that document isolation actually works"""

from neo4j import GraphDatabase
from tools.graph_persister_v2 import GraphPersisterV2

# Connect to Neo4j
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "devpassword"))
persister = GraphPersisterV2(driver)

# Clean slate
with driver.session() as session:
    session.run("MATCH (n:VSEntity) DETACH DELETE n")
    print("✅ Cleaned Neo4j")

# Document 1
doc1_kg = {
    'entities': [
        {'name': 'Brian Chhun', 'type': 'PERSON'},
        {'name': 'KGAS', 'type': 'SYSTEM'}
    ],
    'relationships': [
        {'source': 'Brian Chhun', 'target': 'KGAS', 'type': 'DEVELOPED'}
    ]
}

result1 = persister.process(doc1_kg, {'document_id': 'doc_001'})
print(f"\n📄 Document 1: Created {result1['entities_created']} entities")

# Document 2 with SAME entities (should be separate)
doc2_kg = {
    'entities': [
        {'name': 'Brian Chhun', 'type': 'PERSON'},  # Same name!
        {'name': 'University', 'type': 'ORGANIZATION'}
    ],
    'relationships': [
        {'source': 'Brian Chhun', 'target': 'University', 'type': 'STUDIES_AT'}
    ]
}

result2 = persister.process(doc2_kg, {'document_id': 'doc_002'})
print(f"📄 Document 2: Created {result2['entities_created']} entities")

# Check isolation
with driver.session() as session:
    # Count total Brian Chhun entities
    result = session.run("""
        MATCH (e:VSEntity {canonical_name: 'Brian Chhun'})
        RETURN count(e) as count, collect(e.document_id) as docs
    """).single()
    
    print(f"\n🔍 Total 'Brian Chhun' entities: {result['count']}")
    print(f"   From documents: {result['docs']}")
    
    # Get doc_001 graph
    doc1_graph = persister.get_document_graph('doc_001')
    print(f"\n📊 Doc_001 has {len(doc1_graph['entities'])} entities:")
    for e in doc1_graph['entities']:
        print(f"   - {e['name']}")
    
    # Get doc_002 graph  
    doc2_graph = persister.get_document_graph('doc_002')
    print(f"\n📊 Doc_002 has {len(doc2_graph['entities'])} entities:")
    for e in doc2_graph['entities']:
        print(f"   - {e['name']}")
    
    # Verify isolation
    if result['count'] == 2:
        print("\n✅ SUCCESS: Documents are properly isolated!")
        print("   Each document has its own 'Brian Chhun' entity")
    else:
        print("\n❌ FAILURE: Documents are not isolated")

# Cleanup
persister.cleanup_document('doc_001')
persister.cleanup_document('doc_002')
driver.close()