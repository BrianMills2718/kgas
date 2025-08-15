#!/usr/bin/env python3
"""
Simple Query Interface for Knowledge Graph

Provides basic keyword search in entities without complex multi-hop queries.
"""

import os
from typing import List, Dict, Any
from neo4j import GraphDatabase


def query_knowledge_graph(question: str, limit: int = 10) -> Dict[str, Any]:
    """Simple keyword search in entities
    
    Args:
        question: Query string
        limit: Maximum results to return
        
    Returns:
        Dictionary with query results
    """
    results = {
        "question": question,
        "entities": [],
        "count": 0,
        "success": False,
        "error": None
    }
    
    try:
        # Connect to Neo4j
        driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", os.getenv("NEO4J_PASSWORD", "Geriatric7Ambition-Stitch"))
        )
        
        with driver.session() as session:
            # Simple keyword search in entity names
            # Convert question to lowercase for case-insensitive search
            keywords = question.lower().split()
            
            # Build query to search for entities containing any keyword
            query = """
                MATCH (e:Entity)
                WHERE any(keyword IN $keywords WHERE toLower(e.canonical_name) CONTAINS keyword
                          OR toLower(e.entity_type) CONTAINS keyword)
                RETURN e.canonical_name as name, 
                       e.entity_type as type,
                       e.confidence as confidence
                ORDER BY e.confidence DESC
                LIMIT $limit
            """
            
            result = session.run(query, keywords=keywords, limit=limit)
            
            entities = []
            for record in result:
                entities.append({
                    "name": record["name"],
                    "type": record["type"],
                    "confidence": record["confidence"]
                })
            
            results["entities"] = entities
            results["count"] = len(entities)
            results["success"] = True
            
        driver.close()
        
    except Exception as e:
        results["error"] = str(e)
        results["success"] = False
    
    return results


def interactive_query():
    """Interactive query mode"""
    print("\n" + "=" * 60)
    print("SIMPLE KNOWLEDGE GRAPH QUERY INTERFACE")
    print("=" * 60)
    print("Type 'quit' to exit")
    print("Examples:")
    print("  - What companies are in the graph?")
    print("  - Show me people")
    print("  - Find Apple")
    print()
    
    while True:
        try:
            question = input("\nQuery> ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not question:
                continue
            
            # Execute query
            results = query_knowledge_graph(question)
            
            if results["success"]:
                if results["count"] > 0:
                    print(f"\nFound {results['count']} entities:")
                    for i, entity in enumerate(results["entities"], 1):
                        name = entity["name"] if entity["name"] else "[No name]"
                        print(f"  {i}. {name} ({entity['type']}) - confidence: {entity['confidence']:.2f}")
                else:
                    print("\nNo entities found matching your query.")
            else:
                print(f"\nError: {results['error']}")
                
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")


def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) > 1:
        # Direct query mode
        question = " ".join(sys.argv[1:])
        results = query_knowledge_graph(question)
        
        if results["success"]:
            print(f"\nResults for: {question}")
            print("-" * 40)
            if results["count"] > 0:
                for entity in results["entities"]:
                    name = entity["name"] if entity["name"] else "[No name]"
                    print(f"• {name} ({entity['type']}) - confidence: {entity['confidence']:.2f}")
            else:
                print("No entities found.")
        else:
            print(f"Error: {results['error']}")
    else:
        # Interactive mode
        interactive_query()


if __name__ == "__main__":
    main()