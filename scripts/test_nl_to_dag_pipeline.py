#!/usr/bin/env python3
"""
End-to-End Test: Natural Language → DAG → Execution Pipeline

This script demonstrates the complete automated pipeline:
1. User provides natural language request
2. WorkflowAgent generates DAG
3. System executes DAG with real tools
4. Results are returned to user

This is the functionality requested: "a user could just put in the natural 
language request and all this would happen"
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import logging
from typing import Dict, Any
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_natural_language_to_dag():
    """Test the natural language → DAG generation capability."""
    print("\n" + "="*70)
    print("🧪 TEST 1: Natural Language → DAG Generation")
    print("="*70)
    
    try:
        from src.agents.workflow_agent import WorkflowAgent
        from src.core.service_manager import ServiceManager
        from src.core.enhanced_api_client import EnhancedAPIClient
        
        # Initialize the API client explicitly
        api_client = EnhancedAPIClient()
        
        # Initialize the workflow agent with API client
        agent = WorkflowAgent(api_client=api_client)
        
        # Natural language request (what the user types)
        user_request = """
        Analyze the Carter Center document to understand relationships between 
        organizations and people. Extract entities, build a knowledge graph, 
        calculate influence scores using PageRank, and export the results 
        to a table format.
        """
        
        print(f"\n📝 User Request: {user_request.strip()}")
        print("\n🤖 Generating DAG from natural language...")
        
        # Generate DAG from natural language
        dag_result = agent.generate_workflow_dag(user_request)
        
        if dag_result["status"] == "success":
            dag = dag_result["dag"]
            print(f"\n✅ DAG Generated Successfully!")
            print(f"   DAG ID: {dag['dag_id']}")
            print(f"   Description: {dag['description']}")
            print(f"   Steps: {len(dag['steps'])}")
            
            # Display the generated DAG
            print("\n📊 Generated DAG Structure:")
            for i, step in enumerate(dag["steps"], 1):
                deps = f" (depends on: {', '.join(step['depends_on'])})" if step.get('depends_on') else ""
                print(f"   {i}. {step['step_id']}: {step['tool_id']}{deps}")
            
            # Show reasoning if available
            if dag_result.get("reasoning"):
                print(f"\n💭 Agent Reasoning: {dag_result['reasoning']}")
            
            return dag
        else:
            print(f"\n❌ DAG Generation Failed: {dag_result.get('error', 'Unknown error')}")
            return None
            
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_dag_execution(dag: Dict[str, Any] = None):
    """Test the DAG → Execution capability."""
    print("\n" + "="*70)
    print("🧪 TEST 2: DAG → Execution")
    print("="*70)
    
    try:
        from src.agents.workflow_agent import WorkflowAgent
        from src.core.service_manager import ServiceManager
        from src.core.enhanced_api_client import EnhancedAPIClient
        
        # If no DAG provided, create a simple test DAG
        if dag is None:
            print("\n📝 Using Test DAG (no LLM-generated DAG available)")
            dag = {
                "dag_id": "carter_analysis",
                "description": "Analyze Carter Center relationships",
                "steps": [
                    {
                        "step_id": "load_document",
                        "tool_id": "T01_PDF_LOADER",
                        "operation": "load",
                        "input_data": {
                            "file_path": "data/carter_center.pdf"
                        },
                        "parameters": {},
                        "depends_on": []
                    },
                    {
                        "step_id": "chunk_text",
                        "tool_id": "T15A_TEXT_CHUNKER",
                        "operation": "chunk",
                        "input_data": {
                            "text": "$load_document.text"
                        },
                        "parameters": {
                            "chunk_size": 512
                        },
                        "depends_on": ["load_document"]
                    },
                    {
                        "step_id": "extract_entities",
                        "tool_id": "T23C_ONTOLOGY_AWARE",
                        "operation": "extract",
                        "input_data": {
                            "chunks": "$chunk_text.chunks"
                        },
                        "parameters": {
                            "confidence_threshold": 0.7
                        },
                        "depends_on": ["chunk_text"]
                    },
                    {
                        "step_id": "build_graph",
                        "tool_id": "T31_ENTITY_BUILDER",
                        "operation": "build",
                        "input_data": {
                            "entities": "$extract_entities.entities"
                        },
                        "parameters": {},
                        "depends_on": ["extract_entities"]
                    },
                    {
                        "step_id": "calculate_pagerank",
                        "tool_id": "T68_PAGERANK",
                        "operation": "calculate",
                        "input_data": {
                            "graph_ref": "$build_graph.graph_ref"
                        },
                        "parameters": {},
                        "depends_on": ["build_graph"]
                    },
                    {
                        "step_id": "export_to_table",
                        "tool_id": "GRAPH_TABLE_EXPORTER",
                        "operation": "export",
                        "input_data": {
                            "graph_data": "$calculate_pagerank.graph_with_scores"
                        },
                        "parameters": {
                            "table_type": "node_attributes"
                        },
                        "depends_on": ["calculate_pagerank"]
                    }
                ]
            }
        
        print(f"\n📊 Executing DAG: {dag['dag_id']}")
        print(f"   Steps to execute: {len(dag['steps'])}")
        
        # Initialize workflow agent with API client
        api_client = EnhancedAPIClient()
        agent = WorkflowAgent(api_client=api_client)
        
        # Execute the DAG
        print("\n⚙️ Starting execution...")
        execution_result = agent.execute_workflow_from_dag(dag)
        
        if execution_result["status"] == "success":
            print(f"\n✅ Execution Completed Successfully!")
            print(f"   Execution ID: {execution_result.get('execution_id', 'N/A')}")
            print(f"   Completed Steps: {execution_result.get('completed_steps', 0)}/{execution_result.get('total_steps', 0)}")
            
            # Show execution log highlights
            if execution_result.get("execution_log"):
                print("\n📋 Execution Log Highlights:")
                for entry in execution_result["execution_log"][-5:]:  # Last 5 entries
                    print(f"   - {entry}")
            
            # Show final outputs
            if execution_result.get("data"):
                print("\n📦 Final Outputs:")
                output_keys = list(execution_result["data"].keys())[:5]  # First 5 keys
                for key in output_keys:
                    print(f"   - {key}: {type(execution_result['data'][key])}")
            
            return execution_result
        else:
            print(f"\n❌ Execution Failed: {execution_result.get('error_message', 'Unknown error')}")
            return None
            
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_full_pipeline():
    """Test the complete natural language → DAG → execution pipeline."""
    print("\n" + "="*70)
    print("🚀 FULL PIPELINE TEST: Natural Language → DAG → Execution")
    print("="*70)
    
    try:
        from src.agents.workflow_agent import WorkflowAgent
        from src.core.service_manager import ServiceManager
        from src.core.enhanced_api_client import EnhancedAPIClient
        
        # Initialize once
        print("\n🔧 Initializing System...")
        api_client = EnhancedAPIClient()
        agent = WorkflowAgent(api_client=api_client)
        
        # Check available tools
        available_tools = agent.list_available_tools()
        print(f"   Available tools: {len(available_tools)}")
        if available_tools:
            print(f"   Sample tools: {available_tools[:5]}")
        
        # Natural language request from user
        user_request = """
        I need to analyze relationships in the Carter Center documentation.
        Please extract all entities and relationships, identify key influencers
        using network analysis, and provide the results in both graph and 
        table formats for further analysis.
        """
        
        print(f"\n👤 User Request:")
        print(f"   '{user_request.strip()}'")
        
        # Step 1: Generate DAG from natural language
        print("\n📝 Step 1: Generating DAG from natural language...")
        dag_result = agent.generate_workflow_dag(user_request)
        
        if dag_result["status"] != "success":
            print(f"   ❌ DAG generation failed: {dag_result.get('error')}")
            return False
        
        dag = dag_result["dag"]
        print(f"   ✅ DAG generated: {dag['dag_id']}")
        print(f"   Steps: {[step['tool_id'] for step in dag['steps']]}")
        
        # Step 2: Execute the generated DAG
        print("\n⚙️ Step 2: Executing the generated DAG...")
        execution_result = agent.execute_workflow_from_dag(dag)
        
        if execution_result["status"] != "success":
            print(f"   ❌ Execution failed: {execution_result.get('error_message')}")
            return False
        
        print(f"   ✅ Execution completed successfully!")
        print(f"   Completed: {execution_result.get('completed_steps')}/{execution_result.get('total_steps')} steps")
        
        # Step 3: Display results
        print("\n📊 Step 3: Results Summary")
        if execution_result.get("data"):
            for key, value in list(execution_result["data"].items())[:3]:
                if isinstance(value, (list, dict)):
                    print(f"   - {key}: {type(value).__name__} with {len(value)} items")
                else:
                    print(f"   - {key}: {value}")
        
        print("\n🎉 FULL PIPELINE TEST COMPLETED SUCCESSFULLY!")
        print("   ✅ Natural language understood")
        print("   ✅ DAG automatically generated")
        print("   ✅ Workflow executed with real tools")
        print("   ✅ Results produced")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Pipeline Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("🔬 NATURAL LANGUAGE → DAG → EXECUTION PIPELINE TEST")
    print("="*80)
    print("\nThis test demonstrates that a user can input a natural language request")
    print("and the system will automatically:")
    print("  1. Generate a DAG of tool operations")
    print("  2. Execute the DAG with real tools")
    print("  3. Return the results")
    
    # Test 1: Natural Language → DAG
    dag = test_natural_language_to_dag()
    
    # Test 2: DAG → Execution  
    if dag:
        execution_result = test_dag_execution(dag)
    else:
        print("\n⚠️ Skipping execution test (no DAG generated)")
        # Try with a predefined DAG
        execution_result = test_dag_execution()
    
    # Test 3: Full Pipeline
    print("\n" + "="*80)
    full_success = test_full_pipeline()
    
    # Final Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    if full_success:
        print("\n✅ SUCCESS: The natural language → DAG → execution pipeline is working!")
        print("\nThe system successfully:")
        print("  • Accepted natural language input")
        print("  • Generated an appropriate DAG")
        print("  • Executed the workflow")
        print("  • Produced results")
        print("\n🎯 This proves the system can go from user request to results automatically!")
    else:
        print("\n⚠️ PARTIAL SUCCESS: Some components are working but not the full pipeline")
        print("\nTroubleshooting:")
        print("  • Check if LLM API keys are configured")
        print("  • Verify all required tools are registered")
        print("  • Ensure Neo4j is running for graph operations")
        print("  • Check service manager initialization")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    main()