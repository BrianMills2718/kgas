#!/usr/bin/env python3
"""
Test PageRank tool with Neo4j password fix
"""

import sys
import os
sys.path.append('/home/brian/projects/Digimons')

from dotenv import load_dotenv
load_dotenv()

from src.tools.phase1.t68_pagerank_unified import T68PageRankCalculatorUnified
from src.core.service_manager import ServiceManager
from src.tools.base_tool import ToolRequest

def test_pagerank_neo4j_connection():
    """Test PageRank tool can now connect to Neo4j without password"""
    print("Testing PageRank with Neo4j password fix...")
    
    try:
        # Create service manager
        service_manager = ServiceManager()
        
        # Create PageRank tool
        pagerank_tool = T68PageRankCalculatorUnified(service_manager)
        
        # Check if Neo4j connection was established
        if pagerank_tool.driver:
            print("✅ Neo4j connection established successfully")
            
            # Test connection with simple query
            with pagerank_tool.driver.session() as session:
                result = session.run("RETURN 1 as test")
                test_value = result.single()["test"]
                if test_value == 1:
                    print("✅ Neo4j connection tested - query successful")
                else:
                    print("❌ Neo4j query failed")
                    return False
        else:
            print("❌ Neo4j connection failed")
            return False
        
        # Create test request
        request = ToolRequest(
            tool_id="T68",
            operation="calculate_pagerank",
            input_data={"graph_ref": "neo4j://graph/main"},
            parameters={"result_limit": 10}
        )
        
        # Execute PageRank
        print("Executing PageRank calculation...")
        result = pagerank_tool.execute(request)
        
        if result.status == "success":
            print(f"✅ PageRank execution successful")
            print(f"   - Entity count: {result.data.get('entity_count', 0)}")
            print(f"   - Node count: {result.data.get('node_count', 0)}")
            print(f"   - Execution time: {result.execution_time:.3f}s")
            
            # Show top entities if any
            top_entities = result.data.get('top_entities', [])
            if top_entities:
                print(f"   - Top 3 entities:")
                for i, entity in enumerate(top_entities[:3], 1):
                    print(f"     {i}. {entity.get('canonical_name', 'Unknown')} (score: {entity.get('pagerank_score', 0):.6f})")
            else:
                print(f"   - Reason: {result.data.get('reason', 'No entities found')}")
            
            return True
        else:
            print(f"❌ PageRank execution failed: {result.error_message}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        if 'pagerank_tool' in locals():
            pagerank_tool.cleanup()

if __name__ == "__main__":
    success = test_pagerank_neo4j_connection()
    print(f"\nTest result: {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)