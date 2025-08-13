"""
DAG Adapter for WorkflowAgent
Converts between WorkflowSchema and simple DAG format
"""

from typing import Dict, List, Any
from src.core.workflow_schema import WorkflowSchema, WorkflowStep
from src.agents.workflow_agent import WorkflowAgent

class WorkflowDAGAdapter:
    """Adapter to simplify workflow interaction"""
    
    def __init__(self, workflow_agent: WorkflowAgent):
        self.workflow_agent = workflow_agent
    
    def generate_dag_from_nl(self, natural_language: str) -> Dict[str, Any]:
        """Generate simple DAG from natural language"""
        
        # Use WorkflowAgent to generate workflow
        from src.core.workflow_schema import AgentRequest, AgentLayer
        
        request = AgentRequest(
            natural_language_description=natural_language,
            layer=AgentLayer.LAYER_1,  # Full automation
            available_documents=[]
        )
        
        response = self.workflow_agent.generate_workflow(request)
        
        if response.status == "success" and response.generated_workflow:
            # Convert WorkflowSchema to simple DAG
            return self._workflow_to_dag(response.generated_workflow)
        else:
            return {
                "status": "error",
                "error": response.error_message or "Failed to generate workflow"
            }
    
    def _workflow_to_dag(self, workflow: WorkflowSchema) -> Dict[str, Any]:
        """Convert WorkflowSchema to simple DAG format"""
        
        dag = {
            "dag_id": workflow.metadata.name.replace(" ", "_").lower(),
            "description": workflow.metadata.description,
            "steps": []
        }
        
        for step in workflow.steps:
            dag_step = {
                "step_id": step.step_id,
                "tool_id": step.tool_id or "unknown",
                "operation": step.name,
                "input_data": step.input_mapping,
                "parameters": step.tool_parameters,
                "depends_on": step.depends_on
            }
            dag["steps"].append(dag_step)
        
        return dag
    
    def execute_dag(self, dag: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a simple DAG"""
        
        # Convert DAG back to WorkflowSchema
        workflow = self._dag_to_workflow(dag)
        
        # Execute using WorkflowEngine
        result = self.workflow_agent.execute_workflow_from_yaml(
            workflow_to_yaml(workflow),
            inputs
        )
        
        return result
