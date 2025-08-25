#!/usr/bin/env python3
"""
Agent Validation Framework

Tests real AI agents (GPT-4, Claude, Gemini) to validate their tool selection
accuracy and usage patterns with different MCP organization strategies.
"""

import json
import time
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class ValidationStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    PARTIAL = "partial"
    ERROR = "error"


class AgentType(Enum):
    GPT_4 = "gpt-4"
    CLAUDE_SONNET = "claude-3-5-sonnet-20241022"
    GEMINI_FLASH = "gemini-2.5-flash"
    GPT_4O_MINI = "gpt-4o-mini"
    CLAUDE_HAIKU = "claude-3-haiku-20240307"


@dataclass
class ReferenceWorkflow:
    """Ground truth workflow for validation"""
    workflow_id: str
    name: str
    description: str
    scenario_type: str
    input_context: Dict[str, Any]
    optimal_sequence: List[Dict[str, Any]]
    expected_outputs: Dict[str, Any]
    common_mistakes: List[str] = field(default_factory=list)
    difficulty_level: str = "medium"  # easy, medium, hard
    
    def validate_tool_sequence(self, agent_sequence: List[str]) -> Dict[str, Any]:
        """Validate agent's tool sequence against optimal"""
        optimal_tools = [step["tool"] for step in self.optimal_sequence]
        
        # Calculate sequence similarity
        sequence_match = self._calculate_sequence_similarity(agent_sequence, optimal_tools)
        
        # Check for common mistakes
        mistakes_made = [mistake for mistake in self.common_mistakes 
                        if self._check_mistake_in_sequence(mistake, agent_sequence)]
        
        return {
            "sequence_similarity": sequence_match,
            "optimal_sequence": optimal_tools,
            "agent_sequence": agent_sequence,
            "mistakes_made": mistakes_made,
            "is_optimal": sequence_match > 0.8,
            "improvement_suggestions": self._suggest_improvements(agent_sequence, optimal_tools)
        }
    
    def _calculate_sequence_similarity(self, agent_seq: List[str], optimal_seq: List[str]) -> float:
        """Calculate similarity between two tool sequences"""
        if not agent_seq or not optimal_seq:
            return 0.0
        
        # Simple longest common subsequence similarity
        from difflib import SequenceMatcher
        matcher = SequenceMatcher(None, agent_seq, optimal_seq)
        return matcher.ratio()
    
    def _check_mistake_in_sequence(self, mistake: str, sequence: List[str]) -> bool:
        """Check if a common mistake appears in the sequence"""
        # Simple keyword matching - could be more sophisticated
        return any(mistake.lower() in tool.lower() for tool in sequence)
    
    def _suggest_improvements(self, agent_seq: List[str], optimal_seq: List[str]) -> List[str]:
        """Suggest improvements for agent sequence"""
        suggestions = []
        
        # Check for missing optimal tools
        missing_tools = set(optimal_seq) - set(agent_seq)
        if missing_tools:
            suggestions.append(f"Consider using these optimal tools: {', '.join(missing_tools)}")
        
        # Check for suboptimal ordering
        if len(agent_seq) == len(optimal_seq) and agent_seq != optimal_seq:
            suggestions.append("Tool sequence could be reordered for better efficiency")
        
        return suggestions


@dataclass
class ParameterValidation:
    """Validation for tool parameter usage"""
    tool_name: str
    context: Dict[str, Any]
    expected_parameters: Dict[str, Any]
    agent_parameters: Dict[str, Any]
    
    def validate(self) -> Dict[str, Any]:
        """Validate agent parameter choices"""
        validation_score = 0.0
        issues = []
        suggestions = []
        
        # Check if all required parameters are present
        missing_params = set(self.expected_parameters.keys()) - set(self.agent_parameters.keys())
        if missing_params:
            issues.append(f"Missing parameters: {', '.join(missing_params)}")
        else:
            validation_score += 0.3
        
        # Check parameter value appropriateness
        for param, expected_value in self.expected_parameters.items():
            if param in self.agent_parameters:
                agent_value = self.agent_parameters[param]
                if self._is_parameter_appropriate(param, agent_value, expected_value):
                    validation_score += 0.7 / len(self.expected_parameters)
                else:
                    issues.append(f"Suboptimal {param}: got {agent_value}, expected {expected_value}")
                    suggestions.append(f"For {self.context.get('scenario_type', 'this scenario')}, "
                                     f"{param} should be {expected_value}")
        
        return {
            "validation_score": min(1.0, validation_score),
            "issues": issues,
            "suggestions": suggestions,
            "is_valid": validation_score > 0.7
        }
    
    def _is_parameter_appropriate(self, param: str, agent_value: Any, expected_value: Any) -> bool:
        """Check if agent parameter value is appropriate"""
        if expected_value == agent_value:
            return True
        
        # Handle flexible parameter matching
        if isinstance(expected_value, list) and agent_value in expected_value:
            return True
        
        # Handle range matching for numeric parameters
        if isinstance(expected_value, dict) and "range" in expected_value:
            min_val, max_val = expected_value["range"]
            return min_val <= agent_value <= max_val
        
        return False


@dataclass
class AgentTestResult:
    """Results from testing a single agent"""
    agent_type: AgentType
    workflow_id: str
    strategy_name: str
    success: bool
    execution_time_ms: float
    tools_used: List[str]
    parameters_used: List[Dict[str, Any]]
    tool_selection_accuracy: float
    parameter_accuracy: float
    overall_score: float
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    agent_reasoning: Optional[str] = None
    validation_details: Dict[str, Any] = field(default_factory=dict)


class AIAgent(ABC):
    """Abstract base class for AI agents"""
    
    def __init__(self, agent_type: AgentType, api_key: Optional[str] = None):
        self.agent_type = agent_type
        self.api_key = api_key
        self.available_tools = []
        self.decision_log = []
    
    @abstractmethod
    async def select_tools_for_workflow(self, workflow_description: str, 
                                      available_tools: List[Dict], 
                                      context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Select and configure tools for a given workflow"""
        pass
    
    @abstractmethod  
    async def execute_workflow(self, workflow: ReferenceWorkflow, 
                             tools: List[Dict]) -> Dict[str, Any]:
        """Execute a workflow using selected tools"""
        pass
    
    def set_available_tools(self, tools: List[Dict]):
        """Set the tools available to this agent"""
        self.available_tools = tools
    
    def log_decision(self, decision_type: str, context: Dict, decision: Any):
        """Log agent decision for analysis"""
        self.decision_log.append({
            "timestamp": datetime.now(),
            "decision_type": decision_type,
            "context": context,
            "decision": decision
        })


class MockAIAgent(AIAgent):
    """Mock implementation for testing the framework"""
    
    async def select_tools_for_workflow(self, workflow_description: str,
                                      available_tools: List[Dict],
                                      context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Simple mock tool selection"""
        # Log the decision process
        self.log_decision("tool_selection", {
            "workflow_description": workflow_description,
            "available_tools_count": len(available_tools),
            "context": context
        }, "mock_selection")
        
        # Simple heuristic selection
        selected_tools = []
        
        # Always start with document loading if needed
        if "document" in workflow_description.lower():
            doc_tools = [t for t in available_tools if "load" in t["name"].lower()]
            if doc_tools:
                selected_tools.append({
                    "tool": doc_tools[0]["name"],
                    "parameters": {"extract_metadata": True}
                })
        
        # Add entity extraction for analysis tasks
        if "extract" in workflow_description.lower() or "analyz" in workflow_description.lower():
            extract_tools = [t for t in available_tools if "extract" in t["name"].lower()]
            if extract_tools:
                selected_tools.append({
                    "tool": extract_tools[0]["name"],
                    "parameters": {"method": "hybrid", "ontology_mode": "mixed"}
                })
        
        # Add graph building for relationship tasks
        if "graph" in workflow_description.lower() or "relationship" in workflow_description.lower():
            graph_tools = [t for t in available_tools if "graph" in t["name"].lower()]
            if graph_tools:
                selected_tools.append({
                    "tool": graph_tools[0]["name"],
                    "parameters": {"include_analytics": True}
                })
        
        return selected_tools
    
    async def execute_workflow(self, workflow: ReferenceWorkflow, 
                             tools: List[Dict]) -> Dict[str, Any]:
        """Mock workflow execution"""
        start_time = time.time()
        
        # Simulate execution
        await asyncio.sleep(0.1)  # Simulate processing time
        
        execution_time = (time.time() - start_time) * 1000
        
        # Extract tool names and parameters
        tools_used = [tool["tool"] for tool in tools]
        parameters_used = [tool["parameters"] for tool in tools]
        
        # Simulate success with some realistic failure rate
        import random
        success = random.random() > 0.1  # 90% success rate
        
        return {
            "success": success,
            "execution_time_ms": execution_time,
            "tools_used": tools_used,
            "parameters_used": parameters_used,
            "results": {"mock_results": True},
            "errors": [] if success else ["Mock execution error"],
            "reasoning": "Mock agent reasoning process"
        }


class ReferenceWorkflowLibrary:
    """Library of reference workflows for validation"""
    
    def __init__(self):
        self.workflows = {}
        self._initialize_reference_workflows()
    
    def _initialize_reference_workflows(self):
        """Initialize standard reference workflows"""
        
        # Academic Paper Analysis
        self.workflows["academic_paper_analysis"] = ReferenceWorkflow(
            workflow_id="academic_paper_analysis",
            name="Academic Paper Analysis",
            description="Analyze research paper for key methodological contributions",
            scenario_type="academic_research",
            input_context={
                "document_type": "academic_paper",
                "domain": "machine_learning",
                "complexity": "high",
                "expected_entities": ["methods", "algorithms", "datasets", "metrics"]
            },
            optimal_sequence=[
                {
                    "tool": "load_document_comprehensive",
                    "parameters": {"extract_metadata": True, "quality_check": True},
                    "rationale": "Academic papers need metadata and quality checking"
                },
                {
                    "tool": "extract_knowledge_graph", 
                    "parameters": {"method": "hybrid", "ontology_mode": "mixed"},
                    "rationale": "Hybrid approach best for academic content complexity"
                },
                {
                    "tool": "analyze_graph_insights",
                    "parameters": {"focus": "contributions", "depth": "comprehensive"},
                    "rationale": "Focus on identifying novel contributions"
                }
            ],
            expected_outputs={
                "entities_min": 20,
                "relationships_min": 15,
                "key_contributions": 3,
                "quality_threshold": 0.85
            },
            common_mistakes=[
                "Using basic extraction instead of hybrid",
                "Missing metadata extraction",
                "Insufficient analysis depth",
                "Wrong ontology mode for academic content"
            ],
            difficulty_level="hard"
        )
        
        # Multi-Document Comparison
        self.workflows["multi_document_comparison"] = ReferenceWorkflow(
            workflow_id="multi_document_comparison",
            name="Multi-Document Comparison",
            description="Compare key concepts and relationships across multiple documents",
            scenario_type="comparative_analysis",
            input_context={
                "document_count": 3,
                "comparison_focus": "methodological_differences",
                "complexity": "medium"
            },
            optimal_sequence=[
                {
                    "tool": "load_document_batch",
                    "parameters": {"batch_processing": True, "maintain_provenance": True},
                    "rationale": "Batch processing maintains document relationships"
                },
                {
                    "tool": "extract_knowledge_graph",
                    "parameters": {"method": "llm", "ontology_mode": "closed"},
                    "rationale": "Closed ontology ensures consistent comparison categories"
                },
                {
                    "tool": "compare_knowledge_graphs",
                    "parameters": {"comparison_type": "structural", "highlight_differences": True},
                    "rationale": "Structural comparison identifies methodological differences"
                }
            ],
            expected_outputs={
                "documents_processed": 3,
                "common_concepts": 10,
                "unique_concepts_per_doc": 5,
                "difference_categories": 3
            },
            common_mistakes=[
                "Processing documents separately instead of batch",
                "Using open ontology for comparison",
                "Missing difference highlighting"
            ],
            difficulty_level="medium"
        )
        
        # Simple Entity Extraction
        self.workflows["simple_entity_extraction"] = ReferenceWorkflow(
            workflow_id="simple_entity_extraction",
            name="Simple Entity Extraction",
            description="Extract basic entities from a single document",
            scenario_type="basic_extraction",
            input_context={
                "document_type": "business_report",
                "complexity": "low",
                "focus": "organizations_and_people"
            },
            optimal_sequence=[
                {
                    "tool": "load_document_basic",
                    "parameters": {"extract_metadata": False},
                    "rationale": "Simple loading sufficient for basic extraction"
                },
                {
                    "tool": "extract_knowledge_graph",
                    "parameters": {"method": "spacy", "ontology_mode": "closed"},
                    "rationale": "SpaCy sufficient for simple entity recognition"
                }
            ],
            expected_outputs={
                "entities_min": 10,
                "entity_types": 3,
                "quality_threshold": 0.75
            },
            common_mistakes=[
                "Over-engineering with LLM methods",
                "Using open ontology unnecessarily"
            ],
            difficulty_level="easy"
        )
    
    def get_workflow(self, workflow_id: str) -> Optional[ReferenceWorkflow]:
        """Get a reference workflow by ID"""
        return self.workflows.get(workflow_id)
    
    def get_all_workflows(self) -> List[ReferenceWorkflow]:
        """Get all reference workflows"""
        return list(self.workflows.values())
    
    def get_workflows_by_difficulty(self, difficulty: str) -> List[ReferenceWorkflow]:
        """Get workflows by difficulty level"""
        return [w for w in self.workflows.values() if w.difficulty_level == difficulty]


class AgentValidationFramework:
    """Main framework for validating agent tool selection and usage"""
    
    def __init__(self):
        self.workflow_library = ReferenceWorkflowLibrary()
        self.agents = {}
        self.test_results = []
        
    def register_agent(self, agent: AIAgent):
        """Register an AI agent for testing"""
        self.agents[agent.agent_type] = agent
        logger.info(f"Registered agent: {agent.agent_type.value}")
    
    async def test_agent_workflow(self, agent_type: AgentType, workflow_id: str,
                                strategy_tools: List[Dict]) -> AgentTestResult:
        """Test a single agent on a single workflow"""
        
        if agent_type not in self.agents:
            raise ValueError(f"Agent {agent_type.value} not registered")
        
        workflow = self.workflow_library.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        agent = self.agents[agent_type]
        agent.set_available_tools(strategy_tools)
        
        logger.info(f"Testing {agent_type.value} on {workflow_id}")
        
        start_time = time.time()
        
        try:
            # Agent selects tools
            selected_tools = await agent.select_tools_for_workflow(
                workflow.description,
                strategy_tools,
                workflow.input_context
            )
            
            # Agent executes workflow
            execution_result = await agent.execute_workflow(workflow, selected_tools)
            
            total_time = (time.time() - start_time) * 1000
            
            # Validate tool selection - handle different tool formats
            tool_names = []
            for tool in selected_tools:
                if isinstance(tool, dict):
                    if "tool" in tool:
                        tool_names.append(tool["tool"])
                    elif "name" in tool:
                        tool_names.append(tool["name"])
                    else:
                        # Log the unexpected format for debugging
                        logger.warning(f"Unexpected tool format: {tool}")
                        tool_names.append(str(tool))
                else:
                    tool_names.append(str(tool))
            
            tool_validation = workflow.validate_tool_sequence(tool_names)
            
            # Validate parameters
            parameter_validations = []
            for i, tool_call in enumerate(selected_tools):
                if i < len(workflow.optimal_sequence) and isinstance(tool_call, dict):
                    expected_params = workflow.optimal_sequence[i]["parameters"]
                    
                    # Get tool name safely
                    tool_name = tool_call.get("tool") or tool_call.get("name", "unknown")
                    
                    param_validation = ParameterValidation(
                        tool_name=tool_name,
                        context=workflow.input_context,
                        expected_parameters=expected_params,
                        agent_parameters=tool_call.get("parameters", {})
                    )
                    parameter_validations.append(param_validation.validate())
            
            # Calculate scores
            tool_accuracy = tool_validation["sequence_similarity"]
            param_accuracy = (sum(pv["validation_score"] for pv in parameter_validations) / 
                            len(parameter_validations)) if parameter_validations else 0.0
            
            overall_score = (tool_accuracy * 0.6 + param_accuracy * 0.4)
            
            result = AgentTestResult(
                agent_type=agent_type,
                workflow_id=workflow_id,
                strategy_name="test_strategy",  # Would be set by caller
                success=execution_result["success"],
                execution_time_ms=total_time,
                tools_used=execution_result["tools_used"],
                parameters_used=execution_result["parameters_used"],
                tool_selection_accuracy=tool_accuracy,
                parameter_accuracy=param_accuracy,
                overall_score=overall_score,
                errors=execution_result.get("errors", []),
                agent_reasoning=execution_result.get("reasoning"),
                validation_details={
                    "tool_validation": tool_validation,
                    "parameter_validations": parameter_validations
                }
            )
            
            self.test_results.append(result)
            
            logger.info(f"Test completed: {agent_type.value} scored {overall_score:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Test failed for {agent_type.value} on {workflow_id}: {e}")
            
            error_result = AgentTestResult(
                agent_type=agent_type,
                workflow_id=workflow_id,
                strategy_name="test_strategy",
                success=False,
                execution_time_ms=time.time() - start_time,
                tools_used=[],
                parameters_used=[],
                tool_selection_accuracy=0.0,
                parameter_accuracy=0.0,
                overall_score=0.0,
                errors=[str(e)]
            )
            
            self.test_results.append(error_result)
            return error_result
    
    async def run_comprehensive_validation(self, test_matrix: Dict[str, List]) -> Dict[str, Any]:
        """Run comprehensive validation across agents, strategies, and workflows"""
        
        results = {}
        total_tests = len(test_matrix["agents"]) * len(test_matrix["workflows"])
        completed_tests = 0
        
        logger.info(f"Starting comprehensive validation: {total_tests} total tests")
        
        for agent_type_str in test_matrix["agents"]:
            agent_type = AgentType(agent_type_str)
            
            for workflow_id in test_matrix["workflows"]:
                test_key = f"{agent_type.value}_{workflow_id}"
                
                try:
                    # For now, use mock tools - would be replaced with actual strategy tools
                    mock_tools = [
                        {"name": "load_document_comprehensive", "description": "Load document with metadata"},
                        {"name": "extract_knowledge_graph", "description": "Extract entities and relationships"},
                        {"name": "analyze_graph_insights", "description": "Analyze graph for insights"},
                        {"name": "compare_knowledge_graphs", "description": "Compare multiple graphs"}
                    ]
                    
                    result = await self.test_agent_workflow(agent_type, workflow_id, mock_tools)
                    results[test_key] = result
                    
                    completed_tests += 1
                    logger.info(f"Progress: {completed_tests}/{total_tests} tests completed")
                    
                except Exception as e:
                    logger.error(f"Failed test {test_key}: {e}")
                    results[test_key] = {"error": str(e)}
        
        # Analyze results
        analysis = self._analyze_comprehensive_results(results)
        
        return {
            "test_results": results,
            "analysis": analysis,
            "summary": {
                "total_tests": total_tests,
                "successful_tests": len([r for r in results.values() if isinstance(r, AgentTestResult) and r.success]),
                "average_score": analysis.get("overall_average_score", 0.0)
            }
        }
    
    def _analyze_comprehensive_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze comprehensive test results"""
        
        # Filter successful results
        successful_results = [r for r in results.values() 
                            if isinstance(r, AgentTestResult) and r.success]
        
        if not successful_results:
            return {"error": "No successful test results to analyze"}
        
        # Agent performance analysis
        agent_scores = {}
        for result in successful_results:
            agent = result.agent_type.value
            if agent not in agent_scores:
                agent_scores[agent] = []
            agent_scores[agent].append(result.overall_score)
        
        agent_averages = {agent: sum(scores) / len(scores) 
                         for agent, scores in agent_scores.items()}
        
        # Workflow difficulty analysis
        workflow_scores = {}
        for result in successful_results:
            workflow = result.workflow_id
            if workflow not in workflow_scores:
                workflow_scores[workflow] = []
            workflow_scores[workflow].append(result.overall_score)
        
        workflow_averages = {workflow: sum(scores) / len(scores)
                           for workflow, scores in workflow_scores.items()}
        
        return {
            "agent_performance_ranking": sorted(agent_averages.items(), 
                                              key=lambda x: x[1], reverse=True),
            "workflow_difficulty_ranking": sorted(workflow_averages.items(),
                                                key=lambda x: x[1]),
            "overall_average_score": sum(r.overall_score for r in successful_results) / len(successful_results),
            "tool_selection_accuracy": sum(r.tool_selection_accuracy for r in successful_results) / len(successful_results),
            "parameter_accuracy": sum(r.parameter_accuracy for r in successful_results) / len(successful_results)
        }
    
    def save_results(self, filepath: str):
        """Save validation results to file"""
        results_data = {
            "validation_run_info": {
                "timestamp": datetime.now().isoformat(),
                "total_tests": len(self.test_results),
                "framework_version": "1.0"
            },
            "test_results": [asdict(result) for result in self.test_results],
            "workflows_tested": list(self.workflow_library.workflows.keys()),
            "agents_tested": list(self.agents.keys())
        }
        
        with open(filepath, 'w') as f:
            json.dump(results_data, f, indent=2, default=str)
        
        logger.info(f"Results saved to {filepath}")


# Example usage and testing
async def main():
    """Example usage of the validation framework"""
    
    # Initialize framework
    framework = AgentValidationFramework()
    
    # Register mock agents for testing
    mock_gpt4 = MockAIAgent(AgentType.GPT_4)
    mock_claude = MockAIAgent(AgentType.CLAUDE_SONNET)
    
    framework.register_agent(mock_gpt4)
    framework.register_agent(mock_claude)
    
    # Run a single test
    logger.info("Running single agent test...")
    
    mock_tools = [
        {"name": "load_document_comprehensive", "description": "Load document with metadata"},
        {"name": "extract_knowledge_graph", "description": "Extract entities and relationships"},
        {"name": "analyze_graph_insights", "description": "Analyze graph for insights"}
    ]
    
    result = await framework.test_agent_workflow(
        AgentType.GPT_4, 
        "academic_paper_analysis",
        mock_tools
    )
    
    print(f"Test Result:")
    print(f"  Success: {result.success}")
    print(f"  Overall Score: {result.overall_score:.2f}")
    print(f"  Tool Selection Accuracy: {result.tool_selection_accuracy:.2f}")
    print(f"  Parameter Accuracy: {result.parameter_accuracy:.2f}")
    print(f"  Tools Used: {result.tools_used}")
    
    # Run comprehensive validation
    logger.info("Running comprehensive validation...")
    
    test_matrix = {
        "agents": ["gpt-4", "claude-3-5-sonnet-20241022"],
        "workflows": ["academic_paper_analysis", "simple_entity_extraction"]
    }
    
    comprehensive_results = await framework.run_comprehensive_validation(test_matrix)
    
    print(f"\nComprehensive Results Summary:")
    print(f"  Total Tests: {comprehensive_results['summary']['total_tests']}")
    print(f"  Successful Tests: {comprehensive_results['summary']['successful_tests']}")
    print(f"  Average Score: {comprehensive_results['summary']['average_score']:.2f}")
    
    # Save results
    framework.save_results("validation_results.json")
    
    return framework


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())