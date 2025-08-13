"""
Reasoning Enhanced Workflow Agent

Extends the standard WorkflowAgent with comprehensive reasoning capture capabilities.
Integrates with the Enhanced Reasoning System to provide complete decision traces
for workflow generation, tool selection, and execution decisions.

NO MOCKS - Production-ready implementation with full reasoning capture.
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
import logging

from .workflow_agent import WorkflowAgent
from ..core.enhanced_reasoning_llm_client import EnhancedReasoningLLMClient, create_enhanced_reasoning_llm_client
from ..core.reasoning_trace import (
    ReasoningTrace, ReasoningStep, DecisionLevel, ReasoningType,
    create_workflow_planning_step, create_tool_selection_step, create_error_handling_step
)
from ..core.reasoning_trace_store import ReasoningTraceStore, create_reasoning_trace_store
from ..core.workflow_schema import AgentRequest, AgentResponse, AgentLayer


class ReasoningEnhancedWorkflowAgent(WorkflowAgent):
    """Workflow agent with comprehensive reasoning capture"""
    
    def __init__(
        self, 
        api_client=None,
        reasoning_store: Optional[ReasoningTraceStore] = None,
        capture_reasoning: bool = True
    ):
        """Initialize reasoning-enhanced workflow agent
        
        Args:
            api_client: Base API client (will be wrapped with reasoning capabilities)
            reasoning_store: Store for reasoning traces
            capture_reasoning: Whether to capture reasoning traces
        """
        # Initialize base WorkflowAgent (but don't call super().__init__ yet)
        self.logger = logging.getLogger(__name__)
        
        # Initialize reasoning components first
        if reasoning_store:
            self.reasoning_store = reasoning_store
        else:
            self.reasoning_store = create_reasoning_trace_store()
        
        self.capture_reasoning = capture_reasoning
        
        # Create enhanced reasoning LLM client
        self.reasoning_llm_client = create_enhanced_reasoning_llm_client(
            base_client=api_client,
            reasoning_store=self.reasoning_store,
            capture_reasoning=capture_reasoning
        )
        
        # Now initialize parent class with our enhanced client
        super().__init__(api_client=self.reasoning_llm_client.base_client)
        
        # Override the api_client with our reasoning-enhanced client
        self.api_client = self.reasoning_llm_client
        
        # Current reasoning context
        self.current_trace_id: Optional[str] = None
        self.current_operation_id: Optional[str] = None
        
        self.logger.info(f"ReasoningEnhancedWorkflowAgent initialized (capture_reasoning={capture_reasoning})")
    
    def generate_workflow(self, request: AgentRequest) -> AgentResponse:
        """Generate workflow with comprehensive reasoning capture
        
        Args:
            request: Agent request with natural language description
            
        Returns:
            Agent response with generated workflow and reasoning trace
        """
        start_time = datetime.now()
        
        # Start reasoning trace
        if self.capture_reasoning:
            self.current_trace_id = self.api_client.start_reasoning_trace(
                operation_type="workflow_generation",
                operation_id=f"workflow_{int(time.time())}",
                session_id=getattr(request, 'session_id', None),
                initial_context={
                    "natural_language_description": request.natural_language_description,
                    "layer": request.layer.value,
                    "available_documents": request.available_documents,
                    "target_outputs": request.target_outputs,
                    "constraints": request.constraints
                }
            )
        
        try:
            self.logger.info(f"Generating workflow for layer {request.layer}: {request.natural_language_description[:100]}...")
            
            # Capture initial workflow planning decision
            self._capture_workflow_planning_decision(request)
            
            # Build context for LLM
            context = self._build_llm_context(request)
            
            # Capture context building decision
            self._capture_context_building_step(request, context)
            
            # Generate workflow using LLM with reasoning
            if request.layer == AgentLayer.LAYER_1:
                response = self._generate_layer_1_workflow_with_reasoning(request, context)
            elif request.layer == AgentLayer.LAYER_2:
                response = self._generate_layer_2_workflow_with_reasoning(request, context)
            else:  # LAYER_3
                response = self._generate_layer_3_workflow_with_reasoning(request, context)
            
            # Calculate execution time
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Complete reasoning trace
            if self.capture_reasoning:
                self.api_client.complete_reasoning_trace(
                    success=(response.status != "error"),
                    final_outputs={
                        "status": response.status,
                        "workflow_generated": response.generated_workflow is not None,
                        "ready_to_execute": response.ready_to_execute,
                        "execution_time_ms": execution_time
                    },
                    error_message=response.error_message if response.status == "error" else None
                )
            
            # Add reasoning trace ID to response
            if hasattr(response, '__dict__'):
                response.__dict__['reasoning_trace_id'] = self.current_trace_id
            
            return response
                
        except Exception as e:
            self.logger.error(f"Workflow generation failed: {e}")
            
            # Capture error in reasoning trace
            self._capture_generation_error(str(e))
            
            # Complete trace with error
            if self.capture_reasoning:
                execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
                self.api_client.complete_reasoning_trace(
                    success=False,
                    final_outputs={"execution_time_ms": execution_time},
                    error_message=str(e)
                )
            
            error_response = AgentResponse(
                status="error",
                reasoning=f"Workflow generation failed: {str(e)}",
                ready_to_execute=False,
                error_message=str(e)
            )
            
            # Add reasoning trace ID
            if hasattr(error_response, '__dict__'):
                error_response.__dict__['reasoning_trace_id'] = self.current_trace_id
            
            return error_response
    
    def _generate_layer_1_workflow_with_reasoning(
        self, 
        request: AgentRequest, 
        context: Dict[str, Any]
    ) -> AgentResponse:
        """Generate Layer 1 workflow with reasoning capture"""
        
        # Capture layer selection reasoning
        self._capture_layer_selection_step(request, 1, "Full automation layer selected")
        
        # Create workflow generation prompt
        workflow_prompt = self._create_workflow_generation_prompt(request, context, layer=1)
        
        try:
            # Call LLM with reasoning capture
            llm_response = self.api_client.generate_text_with_reasoning(
                prompt=workflow_prompt,
                model=self._get_default_model(),
                max_tokens=2048,
                decision_point="Generate Layer 1 workflow YAML",
                reasoning_context={
                    "layer": 1,
                    "automation_level": "full",
                    "user_review": False,
                    "immediate_execution": True
                }
            )
            
            if not llm_response.get("success"):
                raise Exception(f"LLM call failed: {llm_response.get('error')}")
            
            # Parse generated workflow
            generated_text = llm_response["content"]
            workflow_yaml = self._extract_yaml_from_response(generated_text)
            
            # Capture YAML extraction decision
            self._capture_yaml_extraction_step(generated_text, workflow_yaml)
            
            # Validate and create workflow
            workflow = self._parse_and_validate_workflow_with_reasoning(workflow_yaml)
            
            if workflow:
                # Capture execution decision
                self._capture_execution_decision(workflow, True, "Layer 1 immediate execution")
                
                # Execute immediately for Layer 1
                execution = self.workflow_engine.execute_workflow(
                    workflow=workflow,
                    inputs={"available_documents": request.available_documents},
                    layer=AgentLayer.LAYER_1
                )
                
                # Capture execution results
                self._capture_execution_results(execution)
                
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
            return self._handle_generation_error(e, "Layer 1 workflow generation failed")
    
    def _generate_layer_2_workflow_with_reasoning(
        self,
        request: AgentRequest,
        context: Dict[str, Any]
    ) -> AgentResponse:
        """Generate Layer 2 workflow with reasoning capture"""
        
        # Capture layer selection reasoning
        self._capture_layer_selection_step(request, 2, "User review layer selected")
        
        workflow_prompt = self._create_workflow_generation_prompt(request, context, layer=2)
        
        try:
            # Call LLM with reasoning capture
            llm_response = self.api_client.generate_text_with_reasoning(
                prompt=workflow_prompt,
                model=self._get_default_model(),
                max_tokens=2048,
                decision_point="Generate Layer 2 workflow YAML for user review",
                reasoning_context={
                    "layer": 2,
                    "automation_level": "assisted",
                    "user_review": True,
                    "immediate_execution": False
                }
            )
            
            if not llm_response.get("success"):
                raise Exception(f"LLM call failed: {llm_response.get('error')}")
            
            # Parse generated workflow
            generated_text = llm_response["content"]
            workflow_yaml = self._extract_yaml_from_response(generated_text)
            
            # Capture YAML extraction decision
            self._capture_yaml_extraction_step(generated_text, workflow_yaml)
            
            # Validate workflow
            workflow = self._parse_and_validate_workflow_with_reasoning(workflow_yaml)
            
            if workflow:
                # Capture user review decision
                self._capture_execution_decision(workflow, False, "Layer 2 requires user review")
                
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
            return self._handle_generation_error(e, "Layer 2 workflow generation failed")
    
    def _generate_layer_3_workflow_with_reasoning(
        self,
        request: AgentRequest,
        context: Dict[str, Any]
    ) -> AgentResponse:
        """Generate Layer 3 workflow with reasoning capture"""
        
        # Capture layer selection reasoning
        self._capture_layer_selection_step(request, 3, "Manual YAML layer selected")
        
        # For Layer 3, provide template and guidance
        template_name = self._suggest_template(request)
        
        # Capture template suggestion decision
        self._capture_template_suggestion_step(request, template_name)
        
        template_workflow = None
        if template_name:
            from ..core.workflow_schema import get_workflow_template
            template_workflow = get_workflow_template(template_name)
        
        # Capture manual workflow decision
        self._capture_manual_workflow_decision(request, template_name, template_workflow)
        
        return AgentResponse(
            status="success",
            generated_workflow=template_workflow,
            workflow_yaml=self._workflow_to_yaml(template_workflow) if template_workflow else "",
            reasoning="Layer 3 guidance provided for manual YAML creation",
            ready_to_execute=False,
            assumptions=[
                "User will write YAML workflow manually",
                "Template provided as starting point",
                "User has YAML editing capabilities"
            ],
            suggestions=[
                "Use the provided template as starting point",
                "Refer to workflow schema documentation",
                "Test with simple workflows first",
                "Validate YAML before execution"
            ]
        )
    
    def _capture_workflow_planning_decision(self, request: AgentRequest) -> None:
        """Capture initial workflow planning decision"""
        if not self.capture_reasoning or not self.api_client.current_trace:
            return
        
        step = create_workflow_planning_step(
            decision_point="Analyze workflow generation request",
            context={
                "natural_language_description": request.natural_language_description,
                "available_documents": request.available_documents,
                "target_outputs": request.target_outputs,
                "constraints": request.constraints,
                "layer": request.layer.value
            },
            workflow_generated={
                "planning_stage": "initial_analysis",
                "layer_requested": request.layer.value
            },
            reasoning_text=(
                f"Analyzing workflow generation request for {request.layer.value}. "
                f"Task: {request.natural_language_description[:200]}... "
                f"Available documents: {len(request.available_documents) if request.available_documents else 0}. "
                f"Need to determine appropriate workflow structure and tool sequence."
            ),
            confidence=0.9
        )
        
        self.api_client.current_trace.add_step(step)
        self.api_client.set_current_step(step)
    
    def _capture_context_building_step(self, request: AgentRequest, context: Dict[str, Any]) -> None:
        """Capture context building decision"""
        if not self.capture_reasoning or not self.api_client.current_trace:
            return
        
        step = ReasoningStep(
            decision_level=DecisionLevel.AGENT,
            reasoning_type=ReasoningType.WORKFLOW_PLANNING,
            decision_point="Build LLM context for workflow generation",
            context={
                "available_tools_count": len(self.available_tools),
                "templates_available": len(context.get("templates_available", [])),
                "execution_layer": request.layer.value
            },
            decision_made={
                "context_built": True,
                "available_tools": len(self.available_tools),
                "context_size": len(str(context))
            },
            reasoning_text=(
                f"Built comprehensive context for LLM including {len(self.available_tools)} available tools, "
                f"workflow templates, and execution layer configuration. Context includes tool registry "
                f"information and layer-specific parameters for {request.layer.value}."
            ),
            confidence_score=0.85
        )
        
        self.api_client.current_trace.add_step(step, self.api_client.current_step.step_id)
    
    def _capture_layer_selection_step(self, request: AgentRequest, layer: int, reasoning: str) -> None:
        """Capture layer selection decision"""
        if not self.capture_reasoning or not self.api_client.current_trace:
            return
        
        step = ReasoningStep(
            decision_level=DecisionLevel.AGENT,
            reasoning_type=ReasoningType.WORKFLOW_PLANNING,
            decision_point=f"Execute Layer {layer} workflow generation",
            context={
                "requested_layer": request.layer.value,
                "layer_capabilities": {
                    1: "Full automation with immediate execution",
                    2: "Generated workflow with user review",
                    3: "Manual YAML with template guidance"
                }
            },
            decision_made={
                "selected_layer": layer,
                "automation_level": ["none", "full", "assisted", "manual"][layer],
                "user_review_required": layer == 2,
                "immediate_execution": layer == 1
            },
            reasoning_text=reasoning,
            confidence_score=0.95
        )
        
        self.api_client.current_trace.add_step(step, self.api_client.current_step.step_id)
        self.api_client.set_current_step(step)
    
    def _capture_yaml_extraction_step(self, generated_text: str, workflow_yaml: str) -> None:
        """Capture YAML extraction decision"""
        if not self.capture_reasoning or not self.api_client.current_trace:
            return
        
        extraction_success = len(workflow_yaml.strip()) > 0
        
        step = ReasoningStep(
            decision_level=DecisionLevel.SYSTEM,
            reasoning_type=ReasoningType.WORKFLOW_PLANNING,
            decision_point="Extract YAML workflow from LLM response",
            context={
                "response_length": len(generated_text),
                "yaml_markers_present": "```yaml" in generated_text.lower(),
                "code_blocks_present": "```" in generated_text
            },
            decision_made={
                "extraction_success": extraction_success,
                "yaml_length": len(workflow_yaml),
                "method_used": "regex_extraction" if "```yaml" in generated_text.lower() else "full_response"
            },
            reasoning_text=(
                f"Extracted YAML workflow from LLM response. "
                f"Response length: {len(generated_text)} chars, "
                f"Extracted YAML length: {len(workflow_yaml)} chars. "
                f"{'Successfully' if extraction_success else 'Failed to'} extract structured YAML."
            ),
            confidence_score=0.9 if extraction_success else 0.3
        )
        
        self.api_client.current_trace.add_step(step, self.api_client.current_step.step_id)
    
    def _parse_and_validate_workflow_with_reasoning(self, workflow_yaml: str):
        """Parse and validate workflow with reasoning capture"""
        
        # Capture validation decision
        if self.capture_reasoning and self.api_client.current_trace:
            step = ReasoningStep(
                decision_level=DecisionLevel.SYSTEM,
                reasoning_type=ReasoningType.VALIDATION,
                decision_point="Parse and validate workflow YAML",
                context={
                    "yaml_length": len(workflow_yaml),
                    "yaml_not_empty": len(workflow_yaml.strip()) > 0
                },
                reasoning_text="Parsing YAML workflow and validating structure, tool compatibility, and execution readiness"
            )
            self.api_client.current_trace.add_step(step, self.api_client.current_step.step_id)
        
        # Use parent method
        result = self._parse_and_validate_workflow(workflow_yaml)
        
        # Update validation step with results
        if self.capture_reasoning and self.api_client.current_trace:
            step.decision_made = {
                "parsing_success": result is not None,
                "workflow_valid": result is not None
            }
            step.confidence_score = 0.9 if result else 0.1
            step.error_occurred = result is None
            if result is None:
                step.error_message = "Workflow parsing or validation failed"
        
        return result
    
    def _capture_execution_decision(self, workflow, should_execute: bool, reasoning: str) -> None:
        """Capture workflow execution decision"""
        if not self.capture_reasoning or not self.api_client.current_trace:
            return
        
        step = ReasoningStep(
            decision_level=DecisionLevel.AGENT,
            reasoning_type=ReasoningType.WORKFLOW_PLANNING,
            decision_point="Decide whether to execute workflow immediately",
            context={
                "workflow_steps": len(workflow.steps) if workflow else 0,
                "workflow_valid": workflow is not None,
                "layer_execution_policy": "immediate" if should_execute else "deferred"
            },
            decision_made={
                "execute_immediately": should_execute,
                "requires_user_review": not should_execute,
                "workflow_ready": workflow is not None
            },
            reasoning_text=reasoning,
            confidence_score=0.95
        )
        
        self.api_client.current_trace.add_step(step, self.api_client.current_step.step_id)
    
    def _capture_execution_results(self, execution) -> None:
        """Capture workflow execution results"""
        if not self.capture_reasoning or not self.api_client.current_trace:
            return
        
        step = ReasoningStep(
            decision_level=DecisionLevel.SYSTEM,
            reasoning_type=ReasoningType.WORKFLOW_PLANNING,
            decision_point="Workflow execution completed",
            context={
                "execution_attempted": True
            },
            decision_made={
                "execution_status": execution.status.value if hasattr(execution, 'status') else "unknown",
                "completed_steps": getattr(execution, 'completed_steps', 0),
                "total_steps": getattr(execution, 'total_steps', 0)
            },
            reasoning_text=f"Workflow execution completed with status: {getattr(execution, 'status', 'unknown')}",
            confidence_score=0.9
        )
        
        self.api_client.current_trace.add_step(step, self.api_client.current_step.step_id)
    
    def _capture_template_suggestion_step(self, request: AgentRequest, template_name: Optional[str]) -> None:
        """Capture template suggestion decision"""
        if not self.capture_reasoning or not self.api_client.current_trace:
            return
        
        step = create_tool_selection_step(
            decision_point="Suggest workflow template for Layer 3",
            available_tools=["pdf_analysis", "multi_document_fusion", "custom"],
            selected_tool=template_name or "custom",
            reasoning_text=(
                f"Analyzed request description '{request.natural_language_description[:100]}...' "
                f"to suggest appropriate template. "
                f"{'Selected template: ' + template_name if template_name else 'No specific template matched, using custom approach'}."
            ),
            confidence=0.8 if template_name else 0.6
        )
        
        self.api_client.current_trace.add_step(step, self.api_client.current_step.step_id)
    
    def _capture_manual_workflow_decision(self, request: AgentRequest, template_name: Optional[str], template_workflow) -> None:
        """Capture manual workflow creation decision"""
        if not self.capture_reasoning or not self.api_client.current_trace:
            return
        
        step = ReasoningStep(
            decision_level=DecisionLevel.AGENT,
            reasoning_type=ReasoningType.WORKFLOW_PLANNING,
            decision_point="Provide manual workflow guidance",
            context={
                "template_suggested": template_name,
                "template_available": template_workflow is not None,
                "user_expertise_assumed": "advanced"
            },
            decision_made={
                "guidance_provided": True,
                "template_provided": template_workflow is not None,
                "manual_creation_required": True
            },
            reasoning_text=(
                f"Layer 3 selected requires manual YAML creation. "
                f"{'Provided template: ' + str(template_name) if template_name else 'No template provided'}. "
                f"User will have full control over workflow structure and parameters."
            ),
            confidence_score=0.9
        )
        
        self.api_client.current_trace.add_step(step, self.api_client.current_step.step_id)
    
    def _capture_generation_error(self, error_message: str) -> None:
        """Capture workflow generation error"""
        if not self.capture_reasoning or not self.api_client.current_trace:
            return
        
        step = create_error_handling_step(
            decision_point="Handle workflow generation error",
            error_context={
                "error_message": error_message,
                "stage": "workflow_generation"
            },
            fallback_decision={
                "return_error_response": True,
                "provide_suggestions": True
            },
            reasoning_text=f"Workflow generation failed with error: {error_message}. Returning structured error response with recovery suggestions.",
            confidence=0.7
        )
        
        self.api_client.current_trace.add_step(step, self.api_client.current_step.step_id)
    
    def _handle_generation_error(self, error: Exception, context: str) -> AgentResponse:
        """Handle generation error with reasoning capture"""
        error_msg = str(error)
        self.logger.error(f"{context}: {error_msg}")
        
        # Capture error
        self._capture_generation_error(error_msg)
        
        return AgentResponse(
            status="error",
            reasoning=f"{context}: {error_msg}",
            ready_to_execute=False,
            error_message=error_msg,
            suggestions=[
                "Try a different layer for different automation level",
                "Check that required tools are available",
                "Verify input description is clear and specific",
                "Check API client configuration"
            ]
        )
    
    def _workflow_to_yaml(self, workflow) -> str:
        """Convert workflow to YAML (helper method)"""
        if workflow:
            from ..core.workflow_schema import workflow_to_yaml
            return workflow_to_yaml(workflow)
        return ""
    
    def _get_default_model(self) -> str:
        """Get default model for LLM calls"""
        return "gemini_flash"  # Use configured Gemini model
    
    def get_reasoning_trace(self, trace_id: str) -> Optional[ReasoningTrace]:
        """Get a specific reasoning trace
        
        Args:
            trace_id: Trace identifier
            
        Returns:
            ReasoningTrace if found
        """
        if self.reasoning_store:
            return self.reasoning_store.get_trace(trace_id)
        return None
    
    def get_recent_traces(self, limit: int = 10) -> List[ReasoningTrace]:
        """Get recent reasoning traces
        
        Args: 
            limit: Maximum number of traces to return
            
        Returns:
            List of recent ReasoningTrace objects
        """
        if self.reasoning_store:
            return self.reasoning_store.query_traces(limit=limit)
        return []
    
    def get_reasoning_statistics(self) -> Dict[str, Any]:
        """Get reasoning capture statistics
        
        Returns:
            Dictionary with reasoning statistics
        """
        if self.reasoning_store:
            return self.reasoning_store.get_statistics()
        return {}


# Factory function
def create_reasoning_enhanced_workflow_agent(
    api_client=None,
    reasoning_store: Optional[ReasoningTraceStore] = None,
    capture_reasoning: bool = True
) -> ReasoningEnhancedWorkflowAgent:
    """Create reasoning-enhanced workflow agent
    
    Args:
        api_client: Base API client
        reasoning_store: Reasoning trace store
        capture_reasoning: Whether to capture reasoning
        
    Returns:
        ReasoningEnhancedWorkflowAgent instance
    """
    return ReasoningEnhancedWorkflowAgent(
        api_client=api_client,
        reasoning_store=reasoning_store,
        capture_reasoning=capture_reasoning
    )