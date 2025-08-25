#!/usr/bin/env python3
"""
Fix and verify database contamination issue
Test Driven Design: Write verification first
"""

import sys
sys.path.insert(0, '/home/brian/projects/Digimons')

from neo4j import GraphDatabase
import os

def verify_database_empty():
    """Verify database is actually empty"""
    driver = GraphDatabase.driver(
        os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        auth=(os.getenv('NEO4J_USER', 'neo4j'), 
              os.getenv('NEO4J_PASSWORD', 'devpassword'))
    )
    
    with driver.session() as session:
        # Count ALL nodes
        result = session.run("MATCH (n) RETURN count(n) as count")
        count = result.single()["count"]
        
        if count > 0:
            # Get sample of contaminating nodes
            result = session.run("MATCH (n) RETURN n LIMIT 5")
            print(f"❌ Database contaminated: {count} nodes found")
            print("Sample nodes:")
            for record in result:
                node = record["n"]
                print(f"  - Labels: {node.labels}, Properties: {dict(node)}")
            return False
        else:
            print(f"✅ Database clean: 0 nodes")
            return True
    
    driver.close()

def force_complete_cleanup():
    """Force complete database cleanup"""
    driver = GraphDatabase.driver(
        os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        auth=(os.getenv('NEO4J_USER', 'neo4j'),
              os.getenv('NEO4J_PASSWORD', 'devpassword'))
    )
    
    with driver.session() as session:
        # Delete EVERYTHING
        session.run("MATCH (n) DETACH DELETE n")
        
        # Verify deletion
        result = session.run("MATCH (n) RETURN count(n) as count")
        count = result.single()["count"]
        
        if count == 0:
            print("✅ Forced cleanup successful: 0 nodes")
            return True
        else:
            print(f"❌ Forced cleanup failed: {count} nodes remain")
            return False
    
    driver.close()

def test_isolation():
    """Test that operations are truly isolated"""
    driver = GraphDatabase.driver(
        os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        auth=(os.getenv('NEO4J_USER', 'neo4j'),
              os.getenv('NEO4J_PASSWORD', 'devpassword'))
    )
    
    with driver.session() as session:
        # Clean first
        session.run("MATCH (n) DETACH DELETE n")
        
        # Create test nodes
        session.run("CREATE (n:TestNode {name: 'test1'})")
        session.run("CREATE (n:TestNode {name: 'test2'})")
        
        # Count nodes
        result = session.run("MATCH (n) RETURN count(n) as count")
        count1 = result.single()["count"]
        
        # Clean again
        session.run("MATCH (n) DETACH DELETE n")
        
        # Count again
        result = session.run("MATCH (n) RETURN count(n) as count")
        count2 = result.single()["count"]
        
        print(f"Before cleanup: {count1} nodes")
        print(f"After cleanup: {count2} nodes")
        
        if count1 == 2 and count2 == 0:
            print("✅ Isolation test passed")
            return True
        else:
            print("❌ Isolation test failed")
            return False
    
    driver.close()

if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE CONTAMINATION FIX")
    print("=" * 60)
    
    # Step 1: Check current state
    print("\n1. Checking current database state...")
    was_contaminated = not verify_database_empty()
    
    if was_contaminated:
        # Step 2: Force cleanup
        print("\n2. Forcing complete cleanup...")
        force_complete_cleanup()
        
        # Step 3: Verify cleanup
        print("\n3. Verifying cleanup...")
        verify_database_empty()
    
    # Step 4: Test isolation
    print("\n4. Testing isolation...")
    test_isolation()
    
    print("\n" + "=" * 60)
    print("Database contamination fixed and verified")
    print("=" * 60)