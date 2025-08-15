#!/usr/bin/env python3
"""
Simplified pipeline test - Direct approach
"""

import sys
import os

def test_simple_pipeline():
    """Test the simplest possible pipeline"""
    
    print("=" * 60)
    print("SIMPLE PIPELINE TEST")
    print("=" * 60)
    
    # Step 1: Read PDF
    print("\n1. Loading PDF...")
    try:
        import PyPDF2
        pdf_path = "test_data/simple_test.pdf"
        
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
        
        print(f"   ✓ Loaded {len(text)} characters")
        print(f"   Sample: {text[:100]}...")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Step 2: Extract entities with SpaCy
    print("\n2. Extracting entities with SpaCy...")
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text[:1000])  # Process first 1000 chars
        
        entities = []
        for ent in doc.ents:
            entities.append({
                'text': ent.text,
                'type': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char
            })
        
        print(f"   ✓ Found {len(entities)} entities")
        print("   Sample entities:")
        for ent in entities[:5]:
            print(f"     - {ent['text']} ({ent['type']})")
            
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Step 3: Store in Neo4j
    print("\n3. Storing in Neo4j...")
    try:
        from neo4j import GraphDatabase
        import os
        
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        username = os.getenv("NEO4J_USERNAME", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        
        driver = GraphDatabase.driver(uri, auth=(username, password))
        
        with driver.session() as session:
            # Clear existing test data
            session.run("MATCH (n:TestEntity) DELETE n")
            
            # Store entities
            stored = 0
            for entity in entities[:10]:  # Store first 10
                result = session.run(
                    """
                    CREATE (e:TestEntity {
                        name: $name,
                        type: $type,
                        source: 'simple_pipeline_test'
                    })
                    RETURN e
                    """,
                    name=entity['text'],
                    type=entity['type']
                )
                if result.single():
                    stored += 1
            
            print(f"   ✓ Stored {stored} entities")
            
            # Verify
            result = session.run("MATCH (n:TestEntity) RETURN count(n) as count")
            count = result.single()["count"]
            print(f"   ✓ Verified: {count} TestEntity nodes in database")
            
        driver.close()
        
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Step 4: Query back
    print("\n4. Querying entities...")
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        
        with driver.session() as session:
            result = session.run(
                """
                MATCH (e:TestEntity)
                RETURN e.name as name, e.type as type
                LIMIT 5
                """
            )
            
            print("   Retrieved entities:")
            for record in result:
                print(f"     - {record['name']} ({record['type']})")
        
        driver.close()
        print("   ✓ Query successful")
        
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_simple_pipeline()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ SIMPLE PIPELINE TEST PASSED")
        print("The basic components are working:")
        print("  1. PDF loading: ✓")
        print("  2. Entity extraction: ✓")
        print("  3. Neo4j storage: ✓")
        print("  4. Query retrieval: ✓")
    else:
        print("✗ SIMPLE PIPELINE TEST FAILED")
    print("=" * 60)
    
    sys.exit(0 if success else 1)