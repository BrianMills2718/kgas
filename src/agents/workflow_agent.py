"""Workflow Agent - Intelligent Workflow Generation with Gemini 2.5 Flash

Implements the multi-layer agent interface for automatic workflow generation
from natural language descriptions using Gemini 2.5 Flash.
"""

import json
import yaml
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging

from src.core.workflow_schema import (
    WorkflowSchema, WorkflowStep, WorkflowStepType, WorkflowMetadata, 
    AgentRequest, AgentResponse, AgentLayer, WORKFLOW_TEMPLATES,
    workflow_to_yaml, validate_workflow
)
from src.core.workflow_engine import WorkflowEngine, WorkflowValidator
from src.core.tool_contract import get_tool_registry
from src.core.enhanced_api_client import EnhancedAPIClient


class WorkflowAgent:
    """Intelligent agent for workflow generation and management."""
    
    def __init__(self, api_client: Optional[EnhancedAPIClient] = None):
        """Initialize workflow agent.
        
        Args:
            api_client: Optional API client (creates one if not provided)
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialize API client for LLM calls - FAIL-FAST MODE
        if api_client:
            self.api_client = api_client
        else:
            try:
                from src.core.service_manager import get_service_manager
                service_manager = get_service_manager()
                self.api_client = getattr(service_manager, 'enhanced_api_client', None)
                if not self.api_client:
                    self._validate_api_client_required()
            except Exception as e:
                self.logger.error(f"Failed to initialize API client: {e}")
                self._validate_api_client_required()
        
        # Initialize workflow components
        self.workflow_engine = WorkflowEngine()
        self.workflow_validator = WorkflowValidator()
        
        # Initialize tool registry with real KGAS tools
        try:
            from ..core.tool_registry_loader import initialize_tool_registry
            registry_results = initialize_tool_registry()
            self.logger.info(f"Tool registry populated with {len(registry_results)} real KGAS tools: {list(registry_results.keys())[:5]}...")
        except Exception as e:
            self.logger.warning(f"Failed to populate tool registry: {e}. Continuing with empty registry.")
        
        self.tool_registry = get_tool_registry()
        
        # Available tools for workflow generation
        self.available_tools = self.tool_registry.list_tools()
        
        self.logger.info(f"WorkflowAgent initialized with {len(self.available_tools)} available tools")
    
    def _validate_api_client_required(self):
        """Fail-fast validation for required API client."""
        from src.core.error_taxonomy import ErrorCategory, ErrorSeverity
        
        error_msg = (
            "Enhanced API client required for WorkflowAgent. "
            "Fix: Initialize ServiceManager with proper API client configuration. "
            "Ensure OPENAI_API_KEY, GOOGLE_API_KEY, or ANTHROPIC_API_KEY is set."
        )
        
        # Create standardized error
        error = Exception(error_msg)
        error.category = ErrorCategory.SERVICE_UNAVAILABLE
        error.severity = ErrorSeverity.CRITICAL
        
        self.logger.critical(error_msg)
        raise error
    
    def generate_workflow(self, request: AgentRequest) -> AgentResponse:
        """Generate workflow from natural language description.
        
        Args:
            request: Agent request with natural language description
            
        Returns:
            Agent response with generated workflow
        """
        try:
            self.logger.info(f"Generating workflow for layer {request.layer}: {request.natural_language_description[:100]}...")
            
            # Build context for LLM
            context = self._build_llm_context(request)
            
            # Generate workflow using LLM
            if request.layer == AgentLayer.LAYER_1:
                return self._generate_layer_1_workflow(request, context)
            elif request.layer == AgentLayer.LAYER_2:
                return self._generate_layer_2_workflow(request, context)
            else:  # LAYER_3
                return self._generate_layer_3_workflow(request, context)
                
        except Exception as e:
            self.logger.error(f"Workflow generation failed: {e}")
            return AgentResponse(
                status="error",
                reasoning=f"Failed to generate workflow: {str(e)}",
                ready_to_execute=False,
                error_message=str(e)
            )
    
    def _generate_layer_1_workflow(self, request: AgentRequest, context: Dict[str, Any]) -> AgentResponse:
        """Generate workflow for Layer 1 (full automation)."""
        # Layer 1: Agent generates and executes workflows automatically
        
        workflow_prompt = self._create_workflow_generation_prompt(request, context, layer=1)
        
        try:
            # Call LLM to generate workflow
            llm_response = self.api_client.generate_text(
                prompt=workflow_prompt,
                model = self._get_default_model(),
                max_tokens=2048
            )
            
            if not llm_response.get("success"):
                raise Exception(f"LLM call failed: {llm_response.get('error')}")
            
            # Parse generated workflow
            generated_text = llm_response["content"]
            workflow_yaml = self._extract_yaml_from_response(generated_text)
            
            # Validate and create workflow
            workflow = self._parse_and_validate_workflow(workflow_yaml)
            
            if workflow:
                # Execute immediately for Layer 1
                execution = self.workflow_engine.execute_workflow(
                    workflow=workflow,
                    inputs={"available_documents": request.available_documents},
                    layer=AgentLayer.LAYER_1
                )
                
                return AgentResponse(
                    status="success",
                    generated_workflow=workflow,
                    workflow_yaml=workflow_yaml,
                    reasoning=f"Generated and executed workflow automatically. Execution status: {execution.status}",
                    ready_to_execute=True,
                    assumptions=[
                        "Workflow executed immediately",
                        "Used available tools for analysis",
                        "Generated standard document processing pipeline"
                    ]
                )
            else:
                raise Exception("Generated workflow failed validation")
                
        except Exception as e:
            return AgentResponse(
                status="error",
                reasoning=f"Layer 1 workflow generation failed: {str(e)}",
                ready_to_execute=False,
                error_message=str(e),
                suggestions=[
                    "Try Layer 2 for user review capabilities",
                    "Check that required tools are available",
                    "Verify input document formats are supported"
                ]
            )
    
    def _generate_layer_2_workflow(self, request: AgentRequest, context: Dict[str, Any]) -> AgentResponse:
        """Generate workflow for Layer 2 (user review)."""
        # Layer 2: Agent generates, user reviews/edits YAML, then executes
        
        workflow_prompt = self._create_workflow_generation_prompt(request, context, layer=2)
        
        try:
            # Call LLM to generate workflow
            llm_response = self.api_client.generate_text(
                prompt=workflow_prompt,
                model = self._get_default_model(),
                max_tokens=2048
            )
            
            if not llm_response.get("success"):
                raise Exception(f"LLM call failed: {llm_response.get('error')}")
            
            # Parse generated workflow
            generated_text = llm_response["content"]
            workflow_yaml = self._extract_yaml_from_response(generated_text)
            
            # Validate workflow
            workflow = self._parse_and_validate_workflow(workflow_yaml)
            
            if workflow:
                return AgentResponse(
                    status="requires_review",
                    generated_workflow=workflow,
                    workflow_yaml=workflow_yaml,
                    reasoning="Generated workflow ready for user review and modification",
                    ready_to_execute=False,  # Requires user approval
                    assumptions=[
                        "User will review and potentially modify workflow",
                        "Execution will happen after user approval",
                        "Generated workflow follows best practices"
                    ],
                    suggestions=[
                        "Review the generated YAML workflow",
                        "Modify tool parameters if needed",
                        "Add additional steps if required",
                        "Execute when ready"
                    ]
                )
            else:
                raise Exception("Generated workflow failed validation")
                
        except Exception as e:
            return AgentResponse(
                status="error",
                reasoning=f"Layer 2 workflow generation failed: {str(e)}",
                ready_to_execute=False,
                error_message=str(e),
                suggestions=[
                    "Try Layer 3 for manual YAML writing",
                    "Check available tools and their requirements",
                    "Verify input description is clear and specific"
                ]
            )
    
    def _generate_layer_3_workflow(self, request: AgentRequest, context: Dict[str, Any]) -> AgentResponse:
        """Generate workflow for Layer 3 (manual YAML)."""
        # Layer 3: User writes YAML directly, engine executes
        
        # For Layer 3, provide a template and guidance rather than generating
        template_name = self._suggest_template(request)
        template_workflow = None
        
        if template_name:
            from src.core.workflow_schema import get_workflow_template
            template_workflow = get_workflow_template(template_name)
        
        guidance_prompt = f"""
        For Layer 3 (manual YAML), here's guidance for creating a workflow:
        
        Task: {request.natural_language_description}
        Available Tools: {', '.join(self.available_tools)}
        
        Suggested Template: {template_name if template_name else 'custom'}
        
        Key considerations:
        1. Define clear step dependencies
        2. Map inputs/outputs between steps
        3. Include error handling
        4. Set appropriate timeouts
        
        Required YAML structure:
        - metadata: (name, description, version)
        - steps: (step_id, step_type, tool_id, etc.)
        - entry_point: (first step to execute)
        """
        
        return AgentResponse(
            status="success",
            generated_workflow=template_workflow,
            workflow_yaml=workflow_to_yaml(template_workflow) if template_workflow else "",
            reasoning="Layer 3 guidance provided for manual YAML creation",
            ready_to_execute=False,
            assumptions=[
                "User will write YAML workflow manually",
                "Template provided as starting point",
                "User has YAML editing capabilities"
            ],
            suggestions=[
                "Use the provided template as a starting point",
                "Refer to the workflow schema documentation",
                "Test with simple workflows first",
                "Validate YAML before execution"
            ]
        )
    
    def _create_workflow_generation_prompt(
        self, 
        request: AgentRequest, 
        context: Dict[str, Any], 
        layer: int
    ) -> str:
        """Create LLM prompt for workflow generation."""
        
        prompt = f"""
You are an expert workflow designer for the KGAS research analysis system. Generate a complete YAML workflow based on the user's requirements.

USER REQUEST:
{request.natural_language_description}

AVAILABLE TOOLS:
{self._format_available_tools()}

CONTEXT:
- Layer: {layer} ({AgentLayer.LAYER_1.value if layer == 1 else AgentLayer.LAYER_2.value if layer == 2 else AgentLayer.LAYER_3.value})
- Available Documents: {len(request.available_documents) if request.available_documents else 0} documents ({sum(len(doc) for doc in request.available_documents) if request.available_documents else 0} characters total)
- Target Outputs: {request.target_outputs}
- Constraints: {request.constraints}

WORKFLOW REQUIREMENTS:
1. Generate a complete YAML workflow that accomplishes the user's goal
2. Use only the available tools listed above
3. Include proper step dependencies and data flow
4. Add appropriate error handling and timeouts
5. Follow the exact YAML schema format shown below
6. IMPORTANT: Use document references (like "document_1", "carter_speech") NOT raw document content
7. Let the tools themselves handle document processing

YAML SCHEMA FORMAT:
```yaml
metadata:
  name: "Workflow Name"
  description: "What this workflow does"
  version: "1.0.0"
  required_tools: ["TOOL1", "TOOL2"]

configuration:
  execution_mode: "sequential"
  error_handling: "stop"
  max_retries: 3

inputs:
  document_paths: ["document_reference"]  # Use references, not raw content
  target_analysis: "string"

steps:
  - step_id: "step_1"
    step_type: "tool_execution"
    name: "Step Name"
    description: "What this step does"
    tool_id: "TOOL_ID"
    tool_parameters:
      param1: "value1"
    input_mapping:
      tool_input: "workflow_data.source"
    output_mapping:
      tool_output: "workflow_data.result"
    depends_on: []
    retry_count: 0
    continue_on_error: false

entry_point: "step_1"
```

GENERATE WORKFLOW:
Create a complete, valid YAML workflow that:
1. Processes the available documents
2. Achieves the user's stated goal
3. Uses appropriate tools in the correct sequence
4. Includes proper data flow between steps
5. Has meaningful step names and descriptions

Return ONLY the YAML workflow, no additional text or explanation.
"""
        
        return prompt
    
    def _format_available_tools(self) -> str:
        """Format available tools for the LLM prompt."""
        tool_descriptions = []
        
        for tool_id in self.available_tools:
            tool = self.tool_registry.get_tool(tool_id)
            if tool:
                tool_info = tool.get_tool_info()
                description = tool_info.get('description', 'No description available')
                tool_descriptions.append(f"- {tool_id}: {description}")
        
        return "\n".join(tool_descriptions)
    
    def _extract_yaml_from_response(self, response_text: str) -> str:
        """Extract YAML content from LLM response, handling reasoning format."""
        
        # First, check if this is a reasoning-enhanced response
        if "**ACTUAL RESPONSE:**" in response_text:
            # Extract content after "**ACTUAL RESPONSE:**"
            response_parts = response_text.split("**ACTUAL RESPONSE:**", 1)
            if len(response_parts) > 1:
                actual_response = response_parts[1].strip()
                # Now extract YAML from the actual response section
                return self._extract_yaml_from_text(actual_response)
        
        # Fall back to standard extraction
        return self._extract_yaml_from_text(response_text)
    
    def _extract_yaml_from_text(self, text: str) -> str:
        """Extract YAML from text content."""
        # Look for YAML code blocks
        lines = text.split('\n')
        yaml_lines = []
        in_yaml_block = False
        
        for line in lines:
            if line.strip() == '```yaml' or line.strip() == '```':
                if not in_yaml_block:
                    in_yaml_block = True
                else:
                    break
            elif in_yaml_block:
                yaml_lines.append(line)
        
        if yaml_lines:
            return '\n'.join(yaml_lines)
        
        # If no code block, assume entire text is YAML
        return text
    
    def _parse_and_validate_workflow(self, workflow_yaml: str) -> Optional[WorkflowSchema]:
        """Parse and validate workflow YAML."""
        try:
            # Parse YAML
            from src.core.workflow_schema import workflow_from_yaml
            workflow = workflow_from_yaml(workflow_yaml)
            
            # Validate workflow
            is_valid, errors = validate_workflow(workflow)
            if not is_valid:
                self.logger.error(f"Workflow validation failed: {errors}")
                return None
            
            # Check execution readiness
            is_executable, exec_errors = self.workflow_validator.validate_for_execution(workflow)
            if not is_executable:
                self.logger.warning(f"Workflow not immediately executable: {exec_errors}")
                # Still return workflow but mark as not ready
            
            # Validate tool pipeline compatibility
            from src.core.pipeline_validator import PipelineValidator
            pipeline_validator = PipelineValidator()
            
            # Extract tool sequence from workflow
            tool_sequence = []
            for step in workflow.steps:
                if step.tool_id:
                    tool_sequence.append(step.tool_id)
            
            if tool_sequence:
                is_compatible, compatibility_errors = pipeline_validator.validate_pipeline(tool_sequence)
                if not is_compatible:
                    self.logger.error(f"Pipeline compatibility validation failed:")
                    for error in compatibility_errors:
                        self.logger.error(f"  - {error}")
                    
                    # Get suggestions
                    suggestions = pipeline_validator.suggest_fixes(compatibility_errors)
                    if suggestions:
                        self.logger.info("Suggestions to fix pipeline:")
                        for suggestion in suggestions:
                            self.logger.info(f"  - {suggestion}")
                    
                    # Return None to prevent execution of incompatible pipeline
                    return None
            
            return workflow
            
        except Exception as e:
            self.logger.error(f"Failed to parse workflow YAML: {e}")
            return None
    
    def _suggest_template(self, request: AgentRequest) -> Optional[str]:
        """Suggest appropriate workflow template based on request."""
        description = request.natural_language_description.lower()
        
        if "pdf" in description or "document" in description:
            if "multiple" in description or "multi" in description:
                return "multi_document_fusion"
            else:
                return "pdf_analysis"
        
        return None
    
    def _get_default_model(self) -> str:
        """Get the default model for LLM operations.
        
        Returns:
            Model name to use (defaults to Gemini 2.5 Flash)
        """
        # Prefer Gemini 2.5 Flash for workflow generation
        default_models = [
            "gemini/gemini-2.5-flash",
            "gemini-2.5-flash", 
            "gpt-4",
            "gpt-3.5-turbo",
            "claude-3-haiku"
        ]
        
        # Check which models are available if api_client has the method
        if hasattr(self.api_client, 'available_models'):
            try:
                available = self.api_client.available_models()
                for model in default_models:
                    if model in available:
                        return model
            except:
                pass  # Fall through to default
        
        # Fallback to Gemini
        return "gemini/gemini-2.5-flash"
    
    def _build_llm_context(self, request: AgentRequest) -> Dict[str, Any]:
        """Build context information for LLM."""
        return {
            "available_tools": self.available_tools,
            "tool_count": len(self.available_tools),
            "templates_available": list(WORKFLOW_TEMPLATES.keys()),
            "execution_layer": request.layer.value,
            "timestamp": datetime.now().isoformat()
        }
    
    def execute_workflow_from_yaml(
        self, 
        workflow_yaml: str, 
        inputs: Dict[str, Any],
        layer: AgentLayer = AgentLayer.LAYER_3
    ) -> Dict[str, Any]:
        """Execute a workflow from YAML definition.
        
        Args:
            workflow_yaml: YAML workflow definition
            inputs: Input data for workflow
            layer: Execution layer
            
        Returns:
            Execution results
        """
        try:
            # Parse workflow
            from src.core.workflow_schema import workflow_from_yaml
            workflow = workflow_from_yaml(workflow_yaml)
            
            # Execute workflow
            execution = self.workflow_engine.execute_workflow(
                workflow=workflow,
                inputs=inputs,
                layer=layer
            )
            
            return {
                "status": "success",
                "execution_id": execution.workflow_id,
                "execution_status": execution.status.value,
                "completed_steps": execution.completed_steps,
                "total_steps": execution.total_steps,
                "execution_log": execution.execution_log,
                "final_outputs": execution.final_outputs,
                "error_message": execution.error_message
            }
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            return {
                "status": "error",
                "error_message": str(e)
            }
    
    def get_workflow_templates(self) -> List[Dict[str, Any]]:
        """Get available workflow templates."""
        templates = []
        for name, template_data in WORKFLOW_TEMPLATES.items():
            templates.append({
                "name": name,
                "description": template_data["metadata"]["description"],
                "required_tools": template_data["metadata"]["required_tools"],
                "step_count": len(template_data["steps"])
            })
        return templates
    
    def generate_workflow_dag(self, natural_language: str) -> Dict[str, Any]:
        """Generate DAG from natural language (simplified interface).
        
        Args:
            natural_language: Natural language description of task
            
        Returns:
            Dictionary with status and DAG
        """
        try:
            # Create agent request for Layer 2 (user review)
            request = AgentRequest(
                natural_language_description=natural_language,
                layer=AgentLayer.LAYER_2,
                available_documents=[]
            )
            
            # Generate workflow using existing method
            response = self.generate_workflow(request)
            
            if response.status in ["success", "requires_review"] and response.generated_workflow:
                # Convert WorkflowSchema to simple DAG format
                dag = {
                    "dag_id": response.generated_workflow.metadata.name.replace(" ", "_").lower(),
                    "description": response.generated_workflow.metadata.description,
                    "steps": []
                }
                
                # Convert each workflow step to DAG step
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
                
                return {
                    "status": "success",
                    "dag": dag,
                    "reasoning": response.reasoning,
                    "assumptions": response.assumptions
                }
            else:
                return {
                    "status": "error",
                    "error": response.error_message or "Failed to generate workflow"
                }
                
        except Exception as e:
            self.logger.error(f"DAG generation failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def execute_workflow_from_dag(self, dag: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow from simple DAG format.
        
        Args:
            dag: DAG dictionary with steps
            
        Returns:
            Execution results
        """
        try:
            # Import required classes
            from src.core.workflow_schema import (
                WorkflowSchema, WorkflowMetadata, WorkflowConfiguration,
                WorkflowStep, WorkflowStepType
            )
            from src.core.workflow_engine import ExecutionStatus
            
            # First, convert DAG steps to workflow steps
            workflow_steps = []
            for dag_step in dag.get("steps", []):
                # Handle input data properly - convert from DAG format to workflow format
                input_data = dag_step.get("input_data", {})
                
                # For file loading steps, ensure we have proper tool_parameters
                tool_parameters = dag_step.get("parameters", {}).copy()
                if dag_step.get("tool_id") in ["T01_PDF_LOADER", "T01"] and input_data:
                    # Move file_path from input_data to tool_parameters where T01 expects it
                    if "file_path" in input_data:
                        tool_parameters["file_path"] = input_data["file_path"]
                    # Also add to input_data for backward compatibility
                    tool_parameters.update(input_data)
                
                step = WorkflowStep(
                    step_id=dag_step["step_id"],
                    step_type=WorkflowStepType.TOOL_EXECUTION,
                    name=dag_step.get("operation", dag_step["step_id"]),
                    tool_id=dag_step.get("tool_id"),
                    tool_parameters=tool_parameters,
                    depends_on=dag_step.get("depends_on", []),
                    input_mapping=dag_step.get("input_data", {}),
                    output_mapping={}
                )
                workflow_steps.append(step)
            
            # Find entry point - the step with no dependencies
            entry_point = None
            if workflow_steps:
                # Find step(s) with no dependencies
                entry_candidates = [
                    step.step_id for step in workflow_steps 
                    if not step.depends_on or len(step.depends_on) == 0
                ]
                
                # Use the first step with no dependencies, or fallback to first step
                entry_point = entry_candidates[0] if entry_candidates else workflow_steps[0].step_id
            
            # Now create the WorkflowSchema with all required fields
            workflow = WorkflowSchema(
                metadata=WorkflowMetadata(
                    name=dag.get("dag_id", "generated_workflow"),
                    description=dag.get("description", "Generated from DAG"),
                    version="1.0.0"
                ),
                configuration=WorkflowConfiguration(),
                steps=workflow_steps,
                entry_point=entry_point or "step_1"  # Fallback if no steps
            )
            
            # Execute the workflow
            execution = self.workflow_engine.execute_workflow(
                workflow=workflow,
                inputs={},
                layer=AgentLayer.LAYER_1  # Execute immediately
            )
            
            return {
                "status": "success" if execution.status == ExecutionStatus.COMPLETED else "error",
                "data": execution.final_outputs if hasattr(execution, 'final_outputs') else {},
                "execution_id": execution.workflow_id,
                "completed_steps": execution.completed_steps,
                "total_steps": execution.total_steps,
                "execution_log": execution.execution_log if hasattr(execution, 'execution_log') else [],
                "error_message": execution.error_message if hasattr(execution, 'error_message') else None
            }
            
        except Exception as e:
            self.logger.error(f"DAG execution failed: {e}")
            return {
                "status": "error",
                "error_message": str(e)
            }
    
    def list_available_tools(self) -> List[str]:
        """List all available tools in the registry.
        
        Returns:
            List of tool IDs
        """
        return self.available_tools


# Factory function
def create_workflow_agent(api_client: Optional[EnhancedAPIClient] = None) -> WorkflowAgent:
    """Create and configure a workflow agent."""
    return WorkflowAgent(api_client=api_client)