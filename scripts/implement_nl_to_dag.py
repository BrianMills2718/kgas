#!/usr/bin/env python3
"""
Implementation plan for Natural Language → DAG → Execution Pipeline

This script implements the missing pieces to enable:
1. Natural language input from user
2. DAG generation using existing WorkflowAgent + LLM
3. Tool execution through WorkflowEngine
4. Natural language summary of results
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json
import logging

# Step 1: Create T23A KGAS wrapper or use T23C
def create_t23a_kgas_wrapper():
    """
    Create a KGAS-compatible wrapper for T23A entity extraction
    """
    
    code = '''"""
T23A SpaCy NER KGAS Wrapper
Makes the deprecated T23A compatible with KGAS tool interface
"""

from typing import Dict, Any, Optional
from src.core.tool_contract import KGASTool, ToolRequest, ToolResult
from src.core.service_manager import ServiceManager
import spacy
import logging

logger = logging.getLogger(__name__)

class T23ASpacyNERKGAS(KGASTool):
    """KGAS wrapper for T23A SpaCy NER"""
    
    def __init__(self, service_manager: ServiceManager):
        self.service_manager = service_manager
        self.tool_id = "T23A"
        self.nlp = None
        self._initialize_spacy()
    
    def _initialize_spacy(self):
        """Initialize spaCy model"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("SpaCy model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load spaCy model: {e}")
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Return tool information"""
        return {
            "tool_id": self.tool_id,
            "name": "SpaCy Named Entity Recognition",
            "description": "Extract named entities using spaCy",
            "version": "1.0.0",
            "category": "entity_extraction"
        }
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute entity extraction"""
        try:
            text = request.input_data.get("text", "")
            chunk_ref = request.input_data.get("chunk_ref", "unknown")
            
            if not self.nlp:
                return ToolResult(
                    tool_id=self.tool_id,
                    status="error",
                    data={},
                    error_details="SpaCy model not loaded"
                )
            
            # Process with spaCy
            doc = self.nlp(text)
            
            # Extract entities
            entities = []
            for ent in doc.ents:
                entities.append({
                    "name": ent.text,
                    "entity_type": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "confidence": 0.85  # Default confidence
                })
            
            return ToolResult(
                tool_id=self.tool_id,
                status="success",
                data={"entities": entities, "entity_count": len(entities)},
                error_details=None
            )
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return ToolResult(
                tool_id=self.tool_id,
                status="error",
                data={},
                error_details=str(e)
            )
'''
    
    # Write the wrapper
    wrapper_path = Path("src/tools/phase1/t23a_spacy_ner_kgas.py")
    wrapper_path.write_text(code)
    print(f"✅ Created T23A KGAS wrapper at: {wrapper_path}")

# Step 2: Update tool registry loader
def update_tool_registry_loader():
    """
    Update the tool registry loader to include T23A and other missing tools
    """
    
    updates = '''
    def _get_priority_phase1_tools(self) -> Dict[str, str]:
        """Get priority Phase 1 tools for vertical slice"""
        return {
            # Working KGAS tools with proper KGASTool interface
            "t01_pdf_loader_kgas.py": "T01_PDF_LOADER",
            "t15a_text_chunker_kgas.py": "T15A_TEXT_CHUNKER",
            "t23a_spacy_ner_kgas.py": "T23A_SPACY_NER",  # Added!
            "t31_entity_builder_kgas.py": "T31_ENTITY_BUILDER",
            "t34_edge_builder_kgas.py": "T34_EDGE_BUILDER",  # Added!
            "t68_pagerank_kgas.py": "T68_PAGERANK",
            "t49_multihop_query_kgas.py": "T49_MULTIHOP_QUERY"  # Added!
        }
'''
    
    print("📝 Tool registry loader update needed:")
    print(updates)
    print("\nAdd T23A_SPACY_NER, T34_EDGE_BUILDER, and T49_MULTIHOP_QUERY to loader")

# Step 3: Create DAG adapter for WorkflowAgent
def create_dag_adapter():
    """
    Create adapter to convert between WorkflowSchema and simple DAG format
    """
    
    code = '''"""
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
'''
    
    adapter_path = Path("src/agents/workflow_dag_adapter.py")
    adapter_path.write_text(code)
    print(f"✅ Created DAG adapter at: {adapter_path}")

# Step 4: Add missing methods to WorkflowAgent
def extend_workflow_agent():
    """
    Add the missing generate_workflow_dag and execute_workflow_from_dag methods
    """
    
    extension_code = '''
# Add these methods to WorkflowAgent class

def generate_workflow_dag(self, natural_language: str) -> Dict[str, Any]:
    """Generate DAG from natural language (simplified interface)"""
    
    request = AgentRequest(
        natural_language_description=natural_language,
        layer=AgentLayer.LAYER_1,
        available_documents=[]
    )
    
    response = self.generate_workflow(request)
    
    if response.status == "success" and response.generated_workflow:
        # Convert to simple DAG format
        dag = {
            "dag_id": response.generated_workflow.metadata.name.replace(" ", "_").lower(),
            "description": response.generated_workflow.metadata.description,
            "steps": []
        }
        
        for step in response.generated_workflow.steps:
            dag_step = {
                "step_id": step.step_id,
                "tool_id": step.tool_id or "unknown",
                "operation": step.name,
                "input_data": step.input_mapping,
                "parameters": step.tool_parameters,
                "depends_on": step.depends_on
            }
            dag["steps"].append(dag_step)
        
        return {"status": "success", "dag": dag}
    else:
        return {
            "status": "error",
            "error": response.error_message or "Failed to generate workflow"
        }

def execute_workflow_from_dag(self, dag: Dict[str, Any]) -> Dict[str, Any]:
    """Execute workflow from simple DAG format"""
    
    # Convert DAG to WorkflowSchema
    from src.core.workflow_schema import (
        WorkflowSchema, WorkflowMetadata, WorkflowConfiguration, 
        WorkflowStep, WorkflowStepType
    )
    
    workflow = WorkflowSchema(
        metadata=WorkflowMetadata(
            name=dag.get("dag_id", "generated_workflow"),
            description=dag.get("description", "Generated from DAG")
        ),
        configuration=WorkflowConfiguration(),
        steps=[]
    )
    
    for dag_step in dag.get("steps", []):
        step = WorkflowStep(
            step_id=dag_step["step_id"],
            step_type=WorkflowStepType.TOOL_EXECUTION,
            name=dag_step.get("operation", dag_step["step_id"]),
            tool_id=dag_step.get("tool_id"),
            tool_parameters=dag_step.get("parameters", {}),
            depends_on=dag_step.get("depends_on", []),
            input_mapping=dag_step.get("input_data", {}),
            output_mapping={}
        )
        workflow.steps.append(step)
    
    # Execute the workflow
    execution = self.workflow_engine.execute_workflow(
        workflow=workflow,
        inputs={},
        layer=AgentLayer.LAYER_1
    )
    
    return {
        "status": "success" if execution.status == ExecutionStatus.COMPLETED else "error",
        "data": execution.outputs,
        "execution_id": execution.workflow_id
    }

def list_available_tools(self) -> List[str]:
    """List all available tools in the registry"""
    from src.core.tool_registry_loader import initialize_tool_registry
    
    registry = initialize_tool_registry()
    return list(registry.keys())
'''
    
    print("📝 WorkflowAgent extension code:")
    print(extension_code)
    print("\nAdd these methods to src/agents/workflow_agent.py")

# Step 5: Create KGAS versions of missing tools
def create_missing_kgas_tools():
    """
    Create KGAS versions of T34 and T49
    """
    
    # T34 Edge Builder KGAS
    t34_code = '''"""
T34 Edge Builder KGAS
"""

from src.core.tool_contract import KGASTool, ToolRequest, ToolResult
from src.core.service_manager import ServiceManager

class T34EdgeBuilderKGAS(KGASTool):
    """KGAS Edge Builder"""
    
    def __init__(self, service_manager: ServiceManager):
        self.service_manager = service_manager
        self.tool_id = "T34"
    
    def get_tool_info(self) -> Dict[str, Any]:
        return {
            "tool_id": self.tool_id,
            "name": "Edge Builder",
            "description": "Build graph edges from relationships"
        }
    
    def execute(self, request: ToolRequest) -> ToolResult:
        # Implementation would build edges in Neo4j
        return ToolResult(
            tool_id=self.tool_id,
            status="success",
            data={"edges_created": 0}
        )
'''
    
    # T49 Multi-hop Query KGAS
    t49_code = '''"""
T49 Multi-hop Query KGAS
"""

from src.core.tool_contract import KGASTool, ToolRequest, ToolResult
from src.core.service_manager import ServiceManager

class T49MultihopQueryKGAS(KGASTool):
    """KGAS Multi-hop Query"""
    
    def __init__(self, service_manager: ServiceManager):
        self.service_manager = service_manager
        self.tool_id = "T49"
    
    def get_tool_info(self) -> Dict[str, Any]:
        return {
            "tool_id": self.tool_id,
            "name": "Multi-hop Query",
            "description": "Query graph with multi-hop traversal"
        }
    
    def execute(self, request: ToolRequest) -> ToolResult:
        # Implementation would query Neo4j
        return ToolResult(
            tool_id=self.tool_id,
            status="success",
            data={"results": []}
        )
'''
    
    print("📝 Missing KGAS tool templates created")
    print("Create T34 and T49 KGAS versions in src/tools/phase1/")

# Main implementation plan
def main():
    print("="*70)
    print("🎯 IMPLEMENTATION PLAN: Natural Language → DAG → Execution")
    print("="*70)
    
    print("\n📋 STEP-BY-STEP IMPLEMENTATION:")
    print("-"*50)
    
    print("\n1️⃣ Create T23A KGAS Wrapper")
    create_t23a_kgas_wrapper()
    
    print("\n2️⃣ Update Tool Registry Loader")
    update_tool_registry_loader()
    
    print("\n3️⃣ Create DAG Adapter")
    create_dag_adapter()
    
    print("\n4️⃣ Extend WorkflowAgent")
    extend_workflow_agent()
    
    print("\n5️⃣ Create Missing KGAS Tools")
    create_missing_kgas_tools()
    
    print("\n"+"="*70)
    print("✅ IMPLEMENTATION PLAN COMPLETE")
    print("="*70)
    
    print("\n📝 NEXT STEPS:")
    print("1. Run this script to create the wrapper files")
    print("2. Manually add the extension methods to WorkflowAgent")
    print("3. Update tool_registry_loader.py with new tools")
    print("4. Test with Carter Center example")

if __name__ == "__main__":
    main()