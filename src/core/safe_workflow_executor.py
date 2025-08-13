"""
Safe Workflow Execution Framework

Executes KGAS workflows with real tools, comprehensive error handling, 
and fail-fast behavior. NO MOCKS OR FALLBACKS.
"""

import json
import time
import yaml
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from .tool_contract import get_tool_registry, ToolRequest, ToolResult
from .tool_id_mapper import get_tool_id_mapper, ToolMappingError

logger = logging.getLogger(__name__)

@dataclass
class ExecutionContext:
    """Context for workflow execution"""
    workflow_id: str
    execution_id: str
    start_time: datetime
    user_request: str
    tool_registry: Any
    tool_mapper: Any
    intermediate_results: Dict[str, Any] = field(default_factory=dict)
    execution_log: List[Dict[str, Any]] = field(default_factory=list)

@dataclass 
class ExecutionResult:
    """Result of workflow execution"""
    status: str  # "success", "error", "validation_failed"
    execution_id: str
    total_execution_time: float
    steps_completed: int
    steps_failed: int
    final_output: Any
    execution_log: List[Dict[str, Any]]
    error_details: Optional[str] = None

class SafeWorkflowExecutor:
    """Execute workflows safely with real tools and comprehensive error handling"""
    
    def __init__(self):
        self.tool_registry = get_tool_registry()
        self.tool_mapper = get_tool_id_mapper()
        self.execution_count = 0
        
        # Fail fast if core dependencies missing
        if len(self.tool_registry.list_tools()) == 0:
            raise WorkflowExecutionError("No tools registered in tool registry")
        
        logger.info(f"SafeWorkflowExecutor initialized with {len(self.tool_registry.list_tools())} tools")
    
    def execute_workflow_from_yaml(self, workflow_yaml: str, user_request: str) -> ExecutionResult:
        """Execute workflow from YAML with comprehensive validation and error handling"""
        
        execution_id = f"exec_{int(time.time())}_{self.execution_count}"
        self.execution_count += 1
        start_time = datetime.now()
        
        # Create execution context
        context = ExecutionContext(
            workflow_id="workflow_from_yaml",
            execution_id=execution_id,
            start_time=start_time,
            user_request=user_request,
            tool_registry=self.tool_registry,
            tool_mapper=self.tool_mapper
        )
        
        try:
            # Phase 1: Parse and validate YAML
            workflow_data = self._parse_workflow_yaml(workflow_yaml, context)
            
            # Phase 2: Validate tool availability 
            tool_mappings = self._validate_workflow_tools(workflow_data, context)
            
            # Phase 3: Execute workflow steps
            final_output = self._execute_workflow_steps(workflow_data, tool_mappings, context)
            
            # Calculate execution metrics
            total_time = (datetime.now() - start_time).total_seconds()
            
            return ExecutionResult(
                status="success",
                execution_id=execution_id,
                total_execution_time=total_time,
                steps_completed=len([log for log in context.execution_log if log.get("status") == "success"]),
                steps_failed=len([log for log in context.execution_log if log.get("status") == "error"]),
                final_output=final_output,
                execution_log=context.execution_log
            )
            
        except WorkflowValidationError as e:
            logger.error(f"Workflow validation failed: {e}")
            return self._create_error_result(context, "validation_failed", str(e))
            
        except ToolMappingError as e:
            logger.error(f"Tool mapping failed: {e}")
            return self._create_error_result(context, "validation_failed", str(e))
            
        except WorkflowExecutionError as e:
            logger.error(f"Workflow execution failed: {e}")
            return self._create_error_result(context, "error", str(e))
            
        except Exception as e:
            logger.error(f"Unexpected error in workflow execution: {e}", exc_info=True)
            return self._create_error_result(context, "error", f"Unexpected error: {str(e)}")
    
    def _parse_workflow_yaml(self, workflow_yaml: str, context: ExecutionContext) -> Dict[str, Any]:
        """Parse and validate YAML structure"""
        context.execution_log.append({
            "step": "yaml_parsing",
            "timestamp": datetime.now().isoformat(),
            "status": "started"
        })
        
        try:
            workflow_data = yaml.safe_load(workflow_yaml)
            
            # Validate required sections
            required_sections = ["metadata", "steps"]
            for section in required_sections:
                if section not in workflow_data:
                    raise WorkflowValidationError(f"Missing required section: {section}")
            
            # Validate steps structure
            if not isinstance(workflow_data["steps"], list) or len(workflow_data["steps"]) == 0:
                raise WorkflowValidationError("Workflow must have at least one step")
            
            context.execution_log.append({
                "step": "yaml_parsing",
                "timestamp": datetime.now().isoformat(),
                "status": "success",
                "steps_parsed": len(workflow_data["steps"])
            })
            
            return workflow_data
            
        except yaml.YAMLError as e:
            raise WorkflowValidationError(f"Invalid YAML format: {str(e)}")
    
    def _validate_workflow_tools(self, workflow_data: Dict[str, Any], context: ExecutionContext) -> Dict[str, str]:
        """Validate all tools in workflow exist in registry"""
        context.execution_log.append({
            "step": "tool_validation", 
            "timestamp": datetime.now().isoformat(),
            "status": "started"
        })
        
        # Extract all tool IDs from workflow steps
        workflow_tools = []
        for step in workflow_data["steps"]:
            if "tool_id" in step:
                workflow_tools.append(step["tool_id"])
        
        if not workflow_tools:
            raise WorkflowValidationError("No tools found in workflow steps")
        
        try:
            # Map workflow tools to registry IDs - FAIL FAST if any unmapped
            tool_mappings = self.tool_mapper.validate_workflow_tools(workflow_tools)
            
            # Verify all mapped tools exist in registry
            missing_tools = []
            for workflow_tool, registry_id in tool_mappings.items():
                if not self.tool_registry.get_tool(registry_id):
                    missing_tools.append(f"{workflow_tool} -> {registry_id}")
            
            if missing_tools:
                raise WorkflowValidationError(f"Tools mapped but not found in registry: {missing_tools}")
            
            context.execution_log.append({
                "step": "tool_validation",
                "timestamp": datetime.now().isoformat(), 
                "status": "success",
                "tools_validated": len(tool_mappings),
                "mappings": tool_mappings
            })
            
            return tool_mappings
            
        except ToolMappingError as e:
            context.execution_log.append({
                "step": "tool_validation",
                "timestamp": datetime.now().isoformat(),
                "status": "error", 
                "error": str(e)
            })
            raise
    
    def _execute_workflow_steps(self, workflow_data: Dict[str, Any], tool_mappings: Dict[str, str], context: ExecutionContext) -> Any:
        """Execute workflow steps sequentially with real tools"""
        
        steps = workflow_data["steps"]
        final_output = None
        
        for i, step in enumerate(steps):
            step_id = step.get("step_id", f"step_{i}")
            workflow_tool_id = step.get("tool_id", "")
            
            context.execution_log.append({
                "step": f"execute_{step_id}",
                "timestamp": datetime.now().isoformat(),
                "status": "started",
                "tool_id": workflow_tool_id
            })
            
            try:
                # Map to registry tool ID
                registry_tool_id = tool_mappings.get(workflow_tool_id)
                if not registry_tool_id:
                    raise WorkflowExecutionError(f"No mapping found for tool: {workflow_tool_id}")
                
                # Get tool instance from registry
                tool = self.tool_registry.get_tool(registry_tool_id)
                if not tool:
                    raise WorkflowExecutionError(f"Tool not found in registry: {registry_tool_id}")
                
                # Prepare tool input data
                input_data = self._prepare_tool_input_data(step, context)
                
                # Create tool request
                tool_request = ToolRequest(
                    input_data=input_data,
                    options=step.get("parameters", {}),
                    workflow_id=context.execution_id,
                    request_id=f"{context.execution_id}_{step_id}"
                )
                
                # Execute tool - NO FALLBACKS
                step_start_time = time.time()
                result = tool.execute(tool_request)
                execution_time = time.time() - step_start_time
                
                # Validate tool result
                if not isinstance(result, ToolResult):
                    raise WorkflowExecutionError(f"Tool {registry_tool_id} returned invalid result type")
                
                if result.status == "error":
                    raise WorkflowExecutionError(
                        f"Tool {registry_tool_id} failed: {result.error_details or 'Unknown error'}"
                    )
                
                # Store intermediate result for next steps
                context.intermediate_results[step_id] = result.data
                final_output = result.data  # Last step output becomes final output
                
                context.execution_log.append({
                    "step": f"execute_{step_id}",
                    "timestamp": datetime.now().isoformat(),
                    "status": "success",
                    "tool_id": workflow_tool_id,
                    "registry_tool_id": registry_tool_id,
                    "execution_time": execution_time,
                    "output_keys": list(result.data.keys()) if isinstance(result.data, dict) else ["result"]
                })
                
            except Exception as e:
                context.execution_log.append({
                    "step": f"execute_{step_id}",
                    "timestamp": datetime.now().isoformat(),
                    "status": "error",
                    "tool_id": workflow_tool_id,
                    "error": str(e)
                })
                
                # FAIL FAST - don't continue with failed steps
                raise WorkflowExecutionError(f"Step {step_id} failed: {str(e)}")
        
        return final_output
    
    def _prepare_tool_input_data(self, step: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """Prepare input data for tool execution"""
        
        # Start with step inputs
        input_data = step.get("inputs", {}).copy()
        
        # Resolve dependencies from previous steps
        depends_on = step.get("depends_on", [])
        for dependency in depends_on:
            if dependency in context.intermediate_results:
                # Add dependency output to current input
                dep_result = context.intermediate_results[dependency]
                input_data.update(dep_result if isinstance(dep_result, dict) else {"dependency_result": dep_result})
            else:
                raise WorkflowExecutionError(f"Dependency {dependency} not found in intermediate results")
        
        return input_data
    
    def _create_error_result(self, context: ExecutionContext, status: str, error_details: str) -> ExecutionResult:
        """Create error result with context information"""
        total_time = (datetime.now() - context.start_time).total_seconds()
        
        return ExecutionResult(
            status=status,
            execution_id=context.execution_id,
            total_execution_time=total_time,
            steps_completed=len([log for log in context.execution_log if log.get("status") == "success"]),
            steps_failed=len([log for log in context.execution_log if log.get("status") == "error"]),
            final_output=None,
            execution_log=context.execution_log,
            error_details=error_details
        )


class WorkflowValidationError(Exception):
    """Raised when workflow validation fails"""
    pass

class WorkflowExecutionError(Exception):
    """Raised when workflow execution fails"""
    pass