"""Agent Orchestration System - KGAS Interface Migration & Agent Orchestration Phase

This system leverages the validated tool registry to create intelligent agents that can 
automatically select and execute appropriate tools for complex tasks.

Implements agent creation, tool selection logic, workflow orchestration, and error recovery
as specified in CLAUDE.md Interface Migration & Agent Orchestration Phase.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from src.core.tool_registry_auto import ToolAutoRegistry, auto_register_all_tools
from src.core.tool_contract import get_tool_registry
from src.tools.base_tool import BaseTool, ToolRequest, ToolResult, ToolStatus
from src.core.service_manager import ServiceManager

logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Types of agents supported by the orchestration system."""
    DOCUMENT_PROCESSING = "document_processing"
    QUERY_PROCESSING = "query_processing"
    CROSS_MODAL_ANALYSIS = "cross_modal_analysis"
    VALIDATION = "validation"


class AgentStatus(Enum):
    """Agent operational status."""
    INITIALIZING = "initializing"
    READY = "ready"
    WORKING = "working"
    ERROR = "error"
    COMPLETED = "completed"


@dataclass
class AgentCapability:
    """Defines what an agent can do."""
    capability_id: str
    name: str
    description: str
    required_tools: List[str]
    optional_tools: List[str] = field(default_factory=list)
    input_types: List[str] = field(default_factory=list)
    output_types: List[str] = field(default_factory=list)


@dataclass
class WorkflowStep:
    """Single step in a workflow execution."""
    step_id: str
    tool_id: str
    operation: str
    input_data: Any
    parameters: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class WorkflowSpec:
    """Specification for a complete workflow."""
    workflow_id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    parallel_execution: bool = False
    error_handling: str = "stop_on_error"  # "stop_on_error", "continue_on_error", "retry_on_error"


@dataclass
class WorkflowResult:
    """Result of workflow execution."""
    workflow_id: str
    status: str  # "success", "partial_success", "error"
    results: Dict[str, Any]
    step_results: Dict[str, ToolResult]
    execution_time: float
    error_details: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


class Agent:
    """Individual agent with tool access and specific capabilities."""
    
    def __init__(self, agent_id: str, agent_type: AgentType, capabilities: List[AgentCapability],
                 tool_registry, service_manager: ServiceManager):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.tool_registry = tool_registry
        self.service_manager = service_manager
        self.status = AgentStatus.INITIALIZING
        self.available_tools = {}
        self.execution_history = []
        
        # Initialize tools for this agent
        self._initialize_tools()
        
        self.status = AgentStatus.READY
        logger.info(f"Agent {agent_id} ({agent_type.value}) initialized with {len(self.available_tools)} tools")
    
    def _initialize_tools(self):
        """Initialize tools required by this agent's capabilities."""
        required_tools = set()
        optional_tools = set()
        
        for capability in self.capabilities:
            required_tools.update(capability.required_tools)
            optional_tools.update(capability.optional_tools)
        
        all_tool_ids = self.tool_registry.list_tools()
        
        # Load required tools
        for tool_id in required_tools:
            if tool_id in all_tool_ids:
                tool = self.tool_registry.get_tool(tool_id)
                if tool:
                    self.available_tools[tool_id] = tool
                    logger.debug(f"Agent {self.agent_id} loaded required tool: {tool_id}")
                else:
                    logger.error(f"Agent {self.agent_id} failed to load required tool: {tool_id}")
            else:
                logger.warning(f"Agent {self.agent_id} missing required tool: {tool_id}")
        
        # Load optional tools
        for tool_id in optional_tools:
            if tool_id in all_tool_ids:
                tool = self.tool_registry.get_tool(tool_id)
                if tool:
                    self.available_tools[tool_id] = tool
                    logger.debug(f"Agent {self.agent_id} loaded optional tool: {tool_id}")
    
    def can_handle_task(self, task_type: str, required_tools: List[str] = None) -> bool:
        """Check if agent can handle a specific task type."""
        # Check if agent has capability for this task type
        for capability in self.capabilities:
            if task_type in capability.input_types or task_type == capability.capability_id:
                # Check if agent has required tools
                if required_tools:
                    missing_tools = [tool for tool in required_tools if tool not in self.available_tools]
                    if missing_tools:
                        logger.debug(f"Agent {self.agent_id} missing tools for task {task_type}: {missing_tools}")
                        return False
                return True
        return False
    
    def execute_tool(self, tool_id: str, request: ToolRequest) -> ToolResult:
        """Execute a specific tool."""
        if tool_id not in self.available_tools:
            return ToolResult(
                tool_id=tool_id,
                status="error",
                error_code="TOOL_NOT_AVAILABLE",
                error_message=f"Tool {tool_id} not available to agent {self.agent_id}"
            )
        
        tool = self.available_tools[tool_id]
        self.status = AgentStatus.WORKING
        
        try:
            result = tool.execute(request)
            self.execution_history.append({
                "timestamp": datetime.now().isoformat(),
                "tool_id": tool_id,
                "operation": request.operation,
                "status": result.status
            })
            return result
        
        except Exception as e:
            logger.error(f"Agent {self.agent_id} tool execution failed: {e}")
            return ToolResult(
                tool_id=tool_id,
                status="error",
                error_code="TOOL_EXECUTION_FAILED",
                error_message=str(e)
            )
        finally:
            self.status = AgentStatus.READY
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status and statistics."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "status": self.status.value,
            "capabilities": [cap.capability_id for cap in self.capabilities],
            "available_tools": list(self.available_tools.keys()),
            "execution_count": len(self.execution_history),
            "last_execution": self.execution_history[-1] if self.execution_history else None
        }


class AgentOrchestrator:
    """Manages multiple agents and tool allocation for complex workflows."""
    
    def __init__(self, service_manager: ServiceManager = None):
        """Initialize agent orchestrator with tool registry."""
        if service_manager is None:
            service_manager = ServiceManager()
        
        self.service_manager = service_manager
        
        # Initialize tool registry and auto-register tools
        logger.info("Initializing agent orchestrator with tool auto-registration")
        self.auto_registry = ToolAutoRegistry()
        registration_result = self.auto_registry.auto_register_all_tools()
        
        self.tool_registry = get_tool_registry()
        self.available_tools = self.tool_registry.list_tools()
        
        logger.info(f"AgentOrchestrator initialized with {len(self.available_tools)} tools")
        logger.info(f"Registration result: {len(registration_result.registered_tools)} registered, "
                   f"{len(registration_result.failed_tools)} failed")
        
        # Initialize agent capabilities
        self.agent_capabilities = self._define_agent_capabilities()
        
        # Active agents
        self.agents: Dict[str, Agent] = {}
        
        # Workflow engine
        self.workflow_engine = WorkflowEngine(self)
    
    def _define_agent_capabilities(self) -> Dict[AgentType, List[AgentCapability]]:
        """Define capabilities for each agent type."""
        return {
            AgentType.DOCUMENT_PROCESSING: [
                AgentCapability(
                    capability_id="pdf_to_entities",
                    name="PDF to Entities Pipeline",
                    description="Extract entities from PDF documents",
                    required_tools=["T01_PDF_LOADER", "T15A_TEXT_CHUNKER", "T23A_SPACY_NER"],
                    optional_tools=["T23C_ONTOLOGY_AWARE_EXTRACTOR"],
                    input_types=["pdf", "document"],
                    output_types=["entities", "mentions"]
                ),
                AgentCapability(
                    capability_id="entity_to_graph",
                    name="Entity to Graph Pipeline",
                    description="Build knowledge graph from entities",
                    required_tools=["T27_RELATIONSHIP_EXTRACTOR", "T31_ENTITY_BUILDER", "T34_EDGE_BUILDER"],
                    optional_tools=["T68_PAGERANK"],
                    input_types=["entities", "relationships"],
                    output_types=["graph", "knowledge_graph"]
                )
            ],
            
            AgentType.QUERY_PROCESSING: [
                AgentCapability(
                    capability_id="multihop_query",
                    name="Multi-hop Graph Query",
                    description="Answer questions using graph traversal",
                    required_tools=["T49_MULTIHOP_QUERY"],
                    optional_tools=["T68_PAGERANK"],
                    input_types=["query", "question"],
                    output_types=["answer", "results"]
                )
            ],
            
            AgentType.CROSS_MODAL_ANALYSIS: [
                AgentCapability(
                    capability_id="graph_to_table",
                    name="Graph to Table Conversion",
                    description="Convert graph data to tabular format",
                    required_tools=["GRAPH_TABLE_EXPORTER"],
                    input_types=["graph", "neo4j_data"],
                    output_types=["table", "dataframe"]
                ),
                AgentCapability(
                    capability_id="multi_format_export",
                    name="Multi-format Data Export",
                    description="Export data to various formats",
                    required_tools=["MULTI_FORMAT_EXPORTER"],
                    input_types=["data", "results"],
                    output_types=["json", "csv", "xml", "yaml"]
                )
            ],
            
            AgentType.VALIDATION: [
                AgentCapability(
                    capability_id="contract_validation",
                    name="Tool Contract Validation",
                    description="Validate tool contracts and interfaces",
                    required_tools=[],  # Uses orchestrator's validation methods
                    input_types=["tool_contract", "tool_spec"],
                    output_types=["validation_result"]
                )
            ]
        }
    
    def create_agent(self, agent_spec: Dict[str, Any]) -> Agent:
        """Create agent with specified capabilities."""
        agent_id = agent_spec.get("agent_id", f"agent_{len(self.agents) + 1}")
        agent_type_str = agent_spec.get("agent_type", "document_processing")
        
        try:
            agent_type = AgentType(agent_type_str)
        except ValueError:
            raise ValueError(f"Invalid agent type: {agent_type_str}")
        
        # Get capabilities for this agent type
        capabilities = self.agent_capabilities.get(agent_type, [])
        
        # Filter capabilities if specific ones requested
        if "capabilities" in agent_spec:
            requested_caps = agent_spec["capabilities"]
            capabilities = [cap for cap in capabilities if cap.capability_id in requested_caps]
        
        # Create agent
        agent = Agent(
            agent_id=agent_id,
            agent_type=agent_type,
            capabilities=capabilities,
            tool_registry=self.tool_registry,
            service_manager=self.service_manager
        )
        
        self.agents[agent_id] = agent
        logger.info(f"Created agent {agent_id} with {len(capabilities)} capabilities")
        
        return agent
    
    def get_agent_for_task(self, task_type: str, required_tools: List[str] = None) -> Optional[Agent]:
        """Find best agent for a specific task."""
        best_agent = None
        best_score = 0
        
        for agent in self.agents.values():
            if agent.can_handle_task(task_type, required_tools):
                # Score based on capability match and tool availability
                score = len([cap for cap in agent.capabilities if task_type in cap.input_types])
                if required_tools:
                    score += len([tool for tool in required_tools if tool in agent.available_tools])
                
                if score > best_score:
                    best_agent = agent
                    best_score = score
        
        return best_agent
    
    def execute_workflow(self, workflow_spec: WorkflowSpec) -> WorkflowResult:
        """Execute multi-tool workflow using appropriate agents."""
        return self.workflow_engine.execute_workflow(workflow_spec)
    
    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get orchestrator status and statistics."""
        return {
            "available_tools": len(self.available_tools),
            "active_agents": len(self.agents),
            "agent_types": list(set(agent.agent_type.value for agent in self.agents.values())),
            "total_capabilities": sum(len(agent.capabilities) for agent in self.agents.values()),
            "agents": [agent.get_status() for agent in self.agents.values()]
        }


class WorkflowEngine:
    """Executes complex multi-tool workflows with dependency management."""
    
    def __init__(self, orchestrator: AgentOrchestrator):
        self.orchestrator = orchestrator
        self.logger = logging.getLogger(f"{__name__}.WorkflowEngine")
    
    def execute_workflow(self, workflow_spec: WorkflowSpec) -> WorkflowResult:
        """Execute workflow with dependency resolution and error handling."""
        start_time = datetime.now()
        self.logger.info(f"Starting workflow execution: {workflow_spec.workflow_id}")
        
        # Initialize result tracking
        results = {}
        step_results = {}
        warnings = []
        
        try:
            if workflow_spec.parallel_execution:
                # Execute steps in parallel where possible
                results, step_results, warnings = self._execute_parallel_workflow(workflow_spec)
            else:
                # Execute steps sequentially with dependency checking
                results, step_results, warnings = self._execute_sequential_workflow(workflow_spec)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Determine overall status
            failed_steps = [step_id for step_id, result in step_results.items() if result.status == "error"]
            if failed_steps:
                if len(failed_steps) == len(workflow_spec.steps):
                    status = "error"
                    error_details = f"All workflow steps failed: {failed_steps}"
                else:
                    status = "partial_success"
                    error_details = f"Some workflow steps failed: {failed_steps}"
                    warnings.append(f"Workflow completed with {len(failed_steps)} failed steps")
            else:
                status = "success"
                error_details = None
            
            return WorkflowResult(
                workflow_id=workflow_spec.workflow_id,
                status=status,
                results=results,
                step_results=step_results,
                execution_time=execution_time,
                error_details=error_details,
                warnings=warnings
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Workflow {workflow_spec.workflow_id} failed: {e}")
            
            return WorkflowResult(
                workflow_id=workflow_spec.workflow_id,
                status="error",
                results=results,
                step_results=step_results,
                execution_time=execution_time,
                error_details=str(e),
                warnings=warnings
            )
    
    def _execute_sequential_workflow(self, workflow_spec: WorkflowSpec) -> tuple:
        """Execute workflow steps sequentially."""
        results = {}
        step_results = {}
        warnings = []
        
        # Build dependency graph
        dependency_order = self._resolve_dependencies(workflow_spec.steps)
        
        for step in dependency_order:
            step_id = step.step_id
            self.logger.info(f"Executing workflow step: {step_id}")
            
            try:
                # Check dependencies
                if not self._check_dependencies(step, step_results):
                    error_msg = f"Dependencies not met for step {step_id}"
                    self.logger.error(error_msg)
                    step_results[step_id] = ToolResult(
                        tool_id=step.tool_id,
                        status="error",
                        error_code="DEPENDENCIES_NOT_MET",
                        error_message=error_msg
                    )
                    continue
                
                # Execute step with retry logic
                result = self._execute_step_with_retry(step, results)
                step_results[step_id] = result
                
                if result.status == "success":
                    results[step_id] = result.data
                    self.logger.info(f"Step {step_id} completed successfully")
                else:
                    self.logger.error(f"Step {step_id} failed: {result.error_message}")
                    if workflow_spec.error_handling == "stop_on_error":
                        break
                    elif workflow_spec.error_handling == "continue_on_error":
                        warnings.append(f"Step {step_id} failed but workflow continued")
                        continue
                
            except Exception as e:
                self.logger.error(f"Step {step_id} execution failed: {e}")
                step_results[step_id] = ToolResult(
                    tool_id=step.tool_id,
                    status="error",
                    error_code="STEP_EXECUTION_FAILED",
                    error_message=str(e)
                )
                if workflow_spec.error_handling == "stop_on_error":
                    break
        
        return results, step_results, warnings
    
    def _execute_parallel_workflow(self, workflow_spec: WorkflowSpec) -> tuple:
        """Execute workflow steps in parallel where dependencies allow."""
        # For now, implement as sequential - parallel execution would require asyncio
        self.logger.info("Parallel execution not yet implemented, falling back to sequential")
        return self._execute_sequential_workflow(workflow_spec)
    
    def _resolve_dependencies(self, steps: List[WorkflowStep]) -> List[WorkflowStep]:
        """Resolve step dependencies and return execution order."""
        # Topological sort of dependencies
        step_map = {step.step_id: step for step in steps}
        visited = set()
        result = []
        
        def visit(step_id: str):
            if step_id in visited:
                return
            visited.add(step_id)
            
            step = step_map.get(step_id)
            if step:
                # Visit dependencies first
                for dep_id in step.depends_on:
                    if dep_id in step_map:
                        visit(dep_id)
                result.append(step)
        
        for step in steps:
            visit(step.step_id)
        
        return result
    
    def _check_dependencies(self, step: WorkflowStep, completed_steps: Dict[str, ToolResult]) -> bool:
        """Check if step dependencies are satisfied."""
        for dep_id in step.depends_on:
            if dep_id not in completed_steps:
                return False
            if completed_steps[dep_id].status != "success":
                return False
        return True
    
    def _execute_step_with_retry(self, step: WorkflowStep, workflow_results: Dict[str, Any]) -> ToolResult:
        """Execute a workflow step with retry logic."""
        for attempt in range(step.max_retries + 1):
            try:
                # Find appropriate agent for this step
                agent = self.orchestrator.get_agent_for_task(step.operation, [step.tool_id])
                if not agent:
                    return ToolResult(
                        tool_id=step.tool_id,
                        status="error",
                        error_code="NO_SUITABLE_AGENT",
                        error_message=f"No agent available for tool {step.tool_id}"
                    )
                
                # Prepare tool request
                # Resolve input data from workflow results if needed
                input_data = self._resolve_input_data(step.input_data, workflow_results)
                
                request = ToolRequest(
                    tool_id=step.tool_id,
                    operation=step.operation,
                    input_data=input_data,
                    parameters=step.parameters
                )
                
                # Execute through agent
                result = agent.execute_tool(step.tool_id, request)
                
                if result.status == "success" or attempt == step.max_retries:
                    if attempt > 0:
                        self.logger.info(f"Step {step.step_id} succeeded on attempt {attempt + 1}")
                    return result
                else:
                    self.logger.warning(f"Step {step.step_id} failed on attempt {attempt + 1}, retrying...")
                    step.retry_count += 1
                    
            except Exception as e:
                if attempt == step.max_retries:
                    return ToolResult(
                        tool_id=step.tool_id,
                        status="error",
                        error_code="STEP_EXECUTION_FAILED",
                        error_message=f"Step failed after {step.max_retries + 1} attempts: {str(e)}"
                    )
                else:
                    self.logger.warning(f"Step {step.step_id} attempt {attempt + 1} failed: {e}")
        
        return ToolResult(
            tool_id=step.tool_id,
            status="error",
            error_code="MAX_RETRIES_EXCEEDED",
            error_message=f"Step failed after {step.max_retries + 1} attempts"
        )
    
    def _resolve_input_data(self, input_data: Any, workflow_results: Dict[str, Any]) -> Any:
        """Resolve input data references from previous workflow results."""
        if isinstance(input_data, str) and input_data.startswith("$"):
            # Reference to previous step result
            step_ref = input_data[1:]  # Remove $
            return workflow_results.get(step_ref, input_data)
        elif isinstance(input_data, dict):
            # Recursively resolve dictionary values
            resolved = {}
            for key, value in input_data.items():
                resolved[key] = self._resolve_input_data(value, workflow_results)
            return resolved
        elif isinstance(input_data, list):
            # Recursively resolve list items
            return [self._resolve_input_data(item, workflow_results) for item in input_data]
        else:
            return input_data


def create_document_processing_agent(orchestrator: AgentOrchestrator) -> Agent:
    """Create a document processing agent with full PDF to graph capabilities."""
    agent_spec = {
        "agent_id": "doc_processor_001",
        "agent_type": "document_processing",
        "capabilities": ["pdf_to_entities", "entity_to_graph"]
    }
    return orchestrator.create_agent(agent_spec)


def create_query_processing_agent(orchestrator: AgentOrchestrator) -> Agent:
    """Create a query processing agent with multi-hop query capabilities."""
    agent_spec = {
        "agent_id": "query_processor_001",
        "agent_type": "query_processing",
        "capabilities": ["multihop_query"]
    }
    return orchestrator.create_agent(agent_spec)


def create_cross_modal_agent(orchestrator: AgentOrchestrator) -> Agent:
    """Create a cross-modal analysis agent with format conversion capabilities."""
    agent_spec = {
        "agent_id": "cross_modal_001",
        "agent_type": "cross_modal_analysis",
        "capabilities": ["graph_to_table", "multi_format_export"]
    }
    return orchestrator.create_agent(agent_spec)


if __name__ == "__main__":
    # Test the agent orchestration system
    logging.basicConfig(level=logging.INFO)
    
    print("KGAS Agent Orchestration System")
    print("=" * 40)
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator()
    status = orchestrator.get_orchestrator_status()
    
    print(f"Orchestrator initialized with {status['available_tools']} tools")
    
    # Create test agents
    doc_agent = create_document_processing_agent(orchestrator)
    query_agent = create_query_processing_agent(orchestrator)
    cross_modal_agent = create_cross_modal_agent(orchestrator)
    
    print(f"Created {len(orchestrator.agents)} agents:")
    for agent_id, agent in orchestrator.agents.items():
        agent_status = agent.get_status()
        print(f"  - {agent_id}: {agent_status['status']} with {len(agent_status['available_tools'])} tools")
    
    # Show orchestrator final status
    final_status = orchestrator.get_orchestrator_status()
    print(f"\nOrchestrator Status:")
    print(f"  - Active agents: {final_status['active_agents']}")
    print(f"  - Total capabilities: {final_status['total_capabilities']}")
    print(f"  - Agent types: {final_status['agent_types']}")