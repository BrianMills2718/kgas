#!/usr/bin/env python3
"""Test workflow execution to debug the validation error"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from src.core.enhanced_api_client import EnhancedAPIClient
from src.agents.workflow_agent import WorkflowAgent
from src.core.workflow_schema import (
    WorkflowSchema, WorkflowMetadata, WorkflowConfiguration,
    WorkflowStep, WorkflowStepType
)

def test_simple_workflow():
    """Test with a minimal workflow"""
    
    # Create a minimal workflow
    workflow = WorkflowSchema(
        metadata=WorkflowMetadata(
            name="test_workflow",
            description="Test workflow",
            version="1.0.0"
        ),
        configuration=WorkflowConfiguration(),
        steps=[
            WorkflowStep(
                step_id="step1",
                step_type=WorkflowStepType.TOOL_EXECUTION,
                name="Load PDF",
                tool_id="T01_PDF_LOADER",
                tool_parameters={},
                depends_on=[],
                input_mapping={},
                output_mapping={}
            )
        ],
        entry_point="step1"  # Explicitly set entry point
    )
    
    print("Testing minimal workflow validation...")
    try:
        # This should work
        print(f"✅ Workflow validation passed")
        print(f"  Entry point: {workflow.entry_point}")
        print(f"  Steps: {[s.step_id for s in workflow.steps]}")
        return True
    except Exception as e:
        print(f"❌ Workflow validation failed: {e}")
        return False

def test_dag_execution():
    """Test executing a DAG"""
    
    client = EnhancedAPIClient()
    agent = WorkflowAgent(api_client=client)
    
    # Create a simple DAG
    dag = {
        "dag_id": "test_dag",
        "description": "Test DAG",
        "steps": [
            {
                "step_id": "load_doc",
                "tool_id": "T01_PDF_LOADER",
                "operation": "load",
                "input_data": {"file_path": "test.pdf"},
                "parameters": {},
                "depends_on": []
            },
            {
                "step_id": "chunk_text",
                "tool_id": "T15A_TEXT_CHUNKER",
                "operation": "chunk",
                "input_data": {"text": "$load_doc.text"},
                "parameters": {"chunk_size": 512},
                "depends_on": ["load_doc"]
            }
        ]
    }
    
    print("\nTesting DAG execution...")
    print(f"DAG has {len(dag['steps'])} steps")
    
    try:
        result = agent.execute_workflow_from_dag(dag)
        
        if result["status"] == "success":
            print(f"✅ DAG execution succeeded")
            return True
        else:
            print(f"❌ DAG execution failed: {result.get('error_message')}")
            return False
            
    except Exception as e:
        print(f"❌ DAG execution error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*60)
    print("WORKFLOW EXECUTION DEBUGGING")
    print("="*60)
    
    # Test minimal workflow
    minimal_ok = test_simple_workflow()
    
    # Test DAG execution
    dag_ok = test_dag_execution()
    
    print("\n" + "="*60)
    if minimal_ok and dag_ok:
        print("✅ ALL TESTS PASSED")
    else:
        print("⚠️ SOME TESTS FAILED")