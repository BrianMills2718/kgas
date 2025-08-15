#!/usr/bin/env python3
"""Test DAG generation to see the structure"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from src.core.enhanced_api_client import EnhancedAPIClient
from src.agents.workflow_agent import WorkflowAgent

def test_dag_structure():
    """Test DAG generation and inspect structure"""
    
    client = EnhancedAPIClient()
    agent = WorkflowAgent(api_client=client)
    
    # Generate a simple DAG
    dag_result = agent.generate_workflow_dag(
        "Extract entities from a PDF document and calculate their importance"
    )
    
    if dag_result["status"] == "success":
        dag = dag_result["dag"]
        
        print("DAG Structure:")
        print(json.dumps(dag, indent=2))
        
        print("\n\nSteps Analysis:")
        for step in dag["steps"]:
            print(f"Step: {step['step_id']}")
            print(f"  Tool: {step.get('tool_id', 'MISSING')}")
            print(f"  Depends on: {step.get('depends_on', [])}")
            print()
        
        # Check for entry point candidates
        entry_candidates = [
            step["step_id"] for step in dag["steps"]
            if not step.get("depends_on") or len(step.get("depends_on", [])) == 0
        ]
        print(f"Entry point candidates: {entry_candidates}")
        
        return dag
    else:
        print(f"DAG generation failed: {dag_result.get('error')}")
        return None

if __name__ == "__main__":
    dag = test_dag_structure()