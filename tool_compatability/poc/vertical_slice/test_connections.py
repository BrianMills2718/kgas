#!/usr/bin/env python3
"""Test database connections before building services"""

def test_neo4j_connection():
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "devpassword"))
    driver.verify_connectivity()
    print("✅ Neo4j connected")
    
    # Test VS namespace
    with driver.session() as session:
        session.run("CREATE (n:VSEntity {test: true})")
        result = session.run("MATCH (n:VSEntity) RETURN count(n) as count")
        print(f"✅ VS namespace working: {result.single()['count']} nodes")
        session.run("MATCH (n:VSEntity {test: true}) DELETE n")  # Cleanup
    driver.close()

def test_sqlite_connection():
    import sqlite3
    conn = sqlite3.connect("vertical_slice.db")
    conn.execute("CREATE TABLE IF NOT EXISTS vs_metrics (id TEXT PRIMARY KEY)")
    print("✅ SQLite connected")
    conn.close()

if __name__ == "__main__":
    test_neo4j_connection()
    test_sqlite_connection()
    print("✅ All connections verified")