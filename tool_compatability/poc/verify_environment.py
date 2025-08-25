#!/usr/bin/env python3
"""Verify which services are available for testing"""

import os
import sys

def check_neo4j():
    """Check if Neo4j is accessible"""
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "devpassword")
        )
        driver.verify_connectivity()
        driver.close()
        return True, "Connected to Neo4j"
    except Exception as e:
        return False, str(e)

def check_gemini():
    """Check if Gemini API is accessible"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return False, "GEMINI_API_KEY not set"
    
    try:
        import litellm
        response = litellm.completion(
            model="gemini/gemini-2.0-flash-exp",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        return True, "Gemini API working"
    except Exception as e:
        return False, str(e)

def main():
    print("="*60)
    print("ENVIRONMENT VERIFICATION")
    print("="*60)
    
    neo4j_ok, neo4j_msg = check_neo4j()
    print(f"Neo4j:  {'✅' if neo4j_ok else '❌'} {neo4j_msg}")
    
    gemini_ok, gemini_msg = check_gemini()
    print(f"Gemini: {'✅' if gemini_ok else '❌'} {gemini_msg}")
    
    print("="*60)
    
    if neo4j_ok and gemini_ok:
        print("Status: READY for full testing")
        print("Next: Run test_full_chain.py")
    elif neo4j_ok or gemini_ok:
        print("Status: PARTIAL testing possible")
        print("Next: Test available components only")
    else:
        print("Status: BLOCKED - No services available")
        print("\nTo setup Neo4j:")
        print("  docker run -d --name neo4j -p 7687:7687 \\")
        print("    -e NEO4J_AUTH=neo4j/devpassword neo4j:latest")
        print("\nTo setup Gemini:")
        print("  1. Visit https://makersuite.google.com/app/apikey")
        print("  2. export GEMINI_API_KEY='your-key'")
    
    return 0 if (neo4j_ok and gemini_ok) else 1

if __name__ == "__main__":
    sys.exit(main())