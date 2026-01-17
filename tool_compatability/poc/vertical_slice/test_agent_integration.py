#!/usr/bin/env python3
"""Test Agent Integration - Verify agent-driven tool chain creation works"""

import sys
sys.path.append('/home/brian/projects/Digimons')
sys.path.append('/home/brian/projects/Digimons/tool_compatability/poc/vertical_slice')

from framework.agent_orchestrator import AgentOrchestrator, AgentRequest
from framework.clean_framework import ToolCapabilities, DataType
from services.vector_service import VectorService  
from services.table_service import TableService
from tools.vector_tool import VectorTool
from tools.table_tool import TableTool

def test_agent_integration():
    """Test that agent can compose and execute tool chains dynamically"""
    print("🧪 Testing Agent Integration")
    print("=" * 50)
    
    # Initialize agent orchestrator
    orchestrator = AgentOrchestrator(
        neo4j_uri='bolt://localhost:7687',
        sqlite_path='vertical_slice.db'
    )
    
    # Create services
    vector_service = VectorService()
    table_service = TableService()
    
    # Register tools with agent orchestrator
    print("\n📝 Registering tools...")
    
    orchestrator.register_tool(
        VectorTool(vector_service),
        ToolCapabilities(
            tool_id="VectorTool",
            input_type=DataType.TEXT,
            output_type=DataType.VECTOR,
            input_construct="text",
            output_construct="embedding",
            transformation_type="embedding"
        )
    )
    
    orchestrator.register_tool(
        TableTool(table_service),
        ToolCapabilities(
            tool_id="TableTool", 
            input_type=DataType.VECTOR,
            output_type=DataType.TABLE,
            input_construct="embedding",
            output_construct="stored",
            transformation_type="persistence"
        )
    )
    
    # Demonstrate agent capabilities
    print("\n🎯 Demonstrating Agent Capabilities...")
    capabilities = orchestrator.demonstrate_capabilities("Extract key concepts from this document and store them")
    
    # Test different types of requests
    test_requests = [
        ("Extract entities from this document", "This is a test document about artificial intelligence and machine learning."),
        ("Create embeddings for similarity search", "Sample text for embedding generation."),
        ("Analyze and store this text data", "Text data that needs to be processed and stored.")
    ]
    
    print("\n🚀 Testing Dynamic Chain Execution...")
    for request_text, sample_data in test_requests:
        print(f"\n--- Testing: '{request_text}' ---")
        
        request = AgentRequest(
            request=request_text,
            data=sample_data,
            data_type="TEXT"
        )
        
        response = orchestrator.execute_agent_request(request)
        
        if response.success:
            print(f"✅ SUCCESS")
            print(f"   Chain used: {' → '.join(response.chain_used)}")
            print(f"   Goal type: {response.goal_evaluation.get('goal_type', 'unknown')}")
            print(f"   Steps executed: {len(response.result.step_uncertainties) if response.result else 0}")
            if response.result and response.result.success:
                print(f"   Final uncertainty: {response.result.total_uncertainty:.3f}")
        else:
            print(f"❌ FAILED: {response.error}")
    
    print(f"\n🏁 Agent Integration Test Complete!")
    return True

if __name__ == "__main__":
    test_agent_integration()