#!/usr/bin/env python3
"""Test that the API client fix works"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.enhanced_api_client import EnhancedAPIClient
from src.agents.workflow_agent import WorkflowAgent

def test_api_client():
    """Test that generate_text method works"""
    print("Testing API client generate_text method...")
    
    client = EnhancedAPIClient()
    
    # Test the new generate_text method
    result = client.generate_text(
        prompt="What is 2+2? Answer with just the number.",
        max_tokens=10
    )
    
    print(f"API Client Test Result: {result}")
    
    if result.get("success"):
        print(f"✅ generate_text works! Response: {result.get('content', '')[:100]}")
        return True
    else:
        print(f"❌ generate_text failed: {result.get('error')}")
        return False

def test_workflow_agent():
    """Test that WorkflowAgent can now generate DAGs"""
    print("\nTesting WorkflowAgent with fixed API...")
    
    try:
        from src.agents.workflow_agent import WorkflowAgent, AgentRequest, AgentLayer
        
        client = EnhancedAPIClient()
        agent = WorkflowAgent(api_client=client)
        
        # Test that _get_default_model works
        default_model = agent._get_default_model()
        print(f"Default model: {default_model}")
        
        # Test simple DAG generation
        dag_result = agent.generate_workflow_dag("Extract entities from a document")
        
        if dag_result["status"] == "success":
            print(f"✅ WorkflowAgent can generate DAGs!")
            print(f"   Generated {len(dag_result['dag']['steps'])} steps")
            return True
        else:
            print(f"❌ DAG generation failed: {dag_result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ WorkflowAgent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*60)
    print("API CLIENT FIX VALIDATION")
    print("="*60)
    
    # Test API client
    api_success = test_api_client()
    
    # Test workflow agent
    workflow_success = test_workflow_agent()
    
    print("\n" + "="*60)
    if api_success and workflow_success:
        print("✅ ALL TESTS PASSED - API FIX SUCCESSFUL!")
    else:
        print("⚠️ SOME TESTS FAILED - NEEDS MORE FIXES")
    print("="*60)