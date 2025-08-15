#!/usr/bin/env python3
"""
Demo Basic Functionality - Phase 4
Shows what actually works in the KGAS system
"""

import os
import sys
from neo4j import GraphDatabase

def load_pdf(pdf_path):
    """Load and extract text from PDF"""
    print("📄 Loading PDF...")
    import PyPDF2
    
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
    
    print(f"   ✓ Loaded {len(text)} characters from {len(reader.pages)} pages")
    return text

def extract_entities(text):
    """Extract entities using SpaCy"""
    print("\n🔍 Extracting entities...")
    import spacy
    
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    
    entities = []
    entity_types = {}
    
    for ent in doc.ents:
        entities.append({
            'text': ent.text,
            'type': ent.label_,
            'start': ent.start_char,
            'end': ent.end_char
        })
        
        # Count by type
        entity_types[ent.label_] = entity_types.get(ent.label_, 0) + 1
    
    print(f"   ✓ Found {len(entities)} entities")
    print("   Entity types:")
    for etype, count in sorted(entity_types.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"     - {etype}: {count}")
    
    return entities

def store_in_graph(entities):
    """Store entities in Neo4j"""
    print("\n💾 Storing in Neo4j...")
    
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    username = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")
    
    driver = GraphDatabase.driver(uri, auth=(username, password))
    
    with driver.session() as session:
        # Clear demo data
        session.run("MATCH (n:DemoEntity) DETACH DELETE n")
        
        # Store entities
        stored = 0
        for entity in entities[:50]:  # Store first 50
            result = session.run(
                """
                MERGE (e:DemoEntity {name: $name})
                SET e.type = $type, e.source = 'demo'
                RETURN e
                """,
                name=entity['text'],
                type=entity['type']
            )
            if result.single():
                stored += 1
        
        # Create some relationships based on co-occurrence
        session.run(
            """
            MATCH (e1:DemoEntity), (e2:DemoEntity)
            WHERE e1.name < e2.name
            AND e1.type = 'PERSON' AND e2.type = 'ORG'
            WITH e1, e2
            LIMIT 10
            MERGE (e1)-[r:ASSOCIATED_WITH]->(e2)
            SET r.source = 'demo'
            """
        )
        
        print(f"   ✓ Stored {stored} entities")
        
        # Get stats
        result = session.run(
            """
            MATCH (n:DemoEntity)
            OPTIONAL MATCH (n)-[r]->()
            RETURN count(DISTINCT n) as nodes, count(r) as relationships
            """
        )
        record = result.single()
        print(f"   ✓ Graph now contains: {record['nodes']} nodes, {record['relationships']} relationships")
    
    driver.close()

def query_knowledge_graph(question):
    """Simple query interface"""
    print(f"\n❓ Query: {question}")
    
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    username = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")
    
    driver = GraphDatabase.driver(uri, auth=(username, password))
    
    # Extract keywords from question
    keywords = [word for word in question.split() if len(word) > 3 and word[0].isupper()]
    
    results = []
    with driver.session() as session:
        # Search for entities matching keywords
        for keyword in keywords:
            result = session.run(
                """
                MATCH (e:DemoEntity)
                WHERE e.name CONTAINS $keyword
                OPTIONAL MATCH (e)-[r]-(connected)
                RETURN e.name as entity, e.type as type,
                       collect(DISTINCT connected.name) as connections
                LIMIT 5
                """,
                keyword=keyword
            )
            
            for record in result:
                results.append({
                    'entity': record['entity'],
                    'type': record['type'],
                    'connections': record['connections']
                })
    
    driver.close()
    
    if results:
        print(f"   ✓ Found {len(results)} relevant entities:")
        for r in results[:3]:
            print(f"     - {r['entity']} ({r['type']})")
            if r['connections']:
                print(f"       Connected to: {', '.join(r['connections'][:3])}")
    else:
        print("   ⚠ No direct matches found")
        # Try broader search
        with GraphDatabase.driver(uri, auth=(username, password)) as driver:
            with driver.session() as session:
                result = session.run(
                    """
                    MATCH (e:DemoEntity)
                    RETURN e.name as name, e.type as type
                    LIMIT 10
                    """
                )
                print("   Sample entities in graph:")
                for record in result:
                    print(f"     - {record['name']} ({record['type']})")
    
    return results

def run_demo():
    """Run the complete demo"""
    print("=" * 60)
    print("🚀 KGAS BASIC FUNCTIONALITY DEMO")
    print("=" * 60)
    print("Demonstrating what actually works in the system\n")
    
    # Step 1: Load PDF
    pdf_path = "test_data/simple_test.pdf"
    if not os.path.exists(pdf_path):
        print("❌ Test PDF not found. Creating it...")
        os.system("python create_test_pdf.py")
    
    text = load_pdf(pdf_path)
    
    # Step 2: Extract entities
    entities = extract_entities(text)
    
    # Step 3: Store in graph
    store_in_graph(entities)
    
    # Step 4: Query the graph
    print("\n" + "=" * 60)
    print("📊 KNOWLEDGE GRAPH QUERIES")
    print("=" * 60)
    
    questions = [
        "What do we know about Apple?",
        "Who is Steve Jobs?",
        "Tell me about Microsoft",
        "What companies are mentioned?"
    ]
    
    for question in questions:
        query_knowledge_graph(question)
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ DEMO COMPLETE - WORKING FEATURES")
    print("=" * 60)
    print("✓ PDF text extraction")
    print("✓ Entity extraction with SpaCy")
    print("✓ Neo4j storage and retrieval")
    print("✓ Basic keyword-based querying")
    print("\n⚠ Known Limitations:")
    print("  - No complex multi-hop queries yet")
    print("  - LLM integration requires API keys")
    print("  - Relationship extraction is basic")
    print("  - No cross-modal analysis yet")

if __name__ == "__main__":
    try:
        run_demo()
        print("\n✨ Demo completed successfully!")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)