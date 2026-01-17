#!/usr/bin/env python3
"""
Agent Orchestrator - Integrates WorkflowAgent with Tool Framework
Enables dynamic tool chain creation and agentic evaluation
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from framework.clean_framework import CleanToolFramework, ToolCapabilities, DataType, ChainResult
from agents.vertical_slice_workflow_agent import VerticalSliceWorkflowAgent


@dataclass
class AgentRequest:
    """Request for agent-driven tool chain execution"""
    request: str  # Natural language request
    data: Any     # Input data
    data_type: str = "TEXT"  # Type of input data


@dataclass  
class AgentResponse:
    """Response from agent execution"""
    success: bool
    chain_used: List[str]
    goal_evaluation: Dict[str, Any]
    result: Optional[ChainResult] = None
    error: Optional[str] = None


class AgentOrchestrator:
    """Orchestrates agent-driven tool chain composition and execution"""
    
    def __init__(self, neo4j_uri: str, sqlite_path: str):
        """Initialize agent orchestrator with tool framework"""
        # Initialize core framework
        self.framework = CleanToolFramework(neo4j_uri, sqlite_path)
        
        # Initialize agent
        self.agent = VerticalSliceWorkflowAgent()
        
        # Track registered tools for agent awareness
        self.tool_registry_synced = False
    
    def register_tool(self, tool, capabilities: ToolCapabilities):
        """Register tool with both framework and agent"""
        # Register with framework
        self.framework.register_tool(tool, capabilities)
        
        # Register with agent for chain composition
        agent_capabilities = {
            "input_type": capabilities.input_type.value,
            "output_type": capabilities.output_type.value,
            "operations": [capabilities.transformation_type],
            "input_construct": capabilities.input_construct,
            "output_construct": capabilities.output_construct
        }
        self.agent.register_tool(capabilities.tool_id, agent_capabilities)
        
        print(f"✅ Registered with both framework and agent: {capabilities.tool_id}")
    
    def execute_agent_request(self, request: AgentRequest) -> AgentResponse:
        """Execute user request using agent-driven tool selection"""
        try:
            # Step 1: Agent evaluates goal
            goal_evaluation = self.agent.evaluate_goal(request.request)
            print(f"\n🎯 Goal Analysis: {goal_evaluation['goal_type']} (complexity: {goal_evaluation['complexity']})")
            print(f"Required capabilities: {goal_evaluation['required_capabilities']}")
            
            # Step 2: Agent composes tool chain
            chain = self.agent.compose_chain(request.request, request.data_type)
            print(f"🔗 Agent composed chain: {chain}")
            
            # Step 3: Validate chain exists in framework
            if not chain:
                return AgentResponse(
                    success=False,
                    chain_used=[],
                    goal_evaluation=goal_evaluation,
                    error="Agent could not compose a valid tool chain"
                )
            
            # Validate all tools are registered
            missing_tools = [tool for tool in chain if tool not in self.framework.tools]
            if missing_tools:
                return AgentResponse(
                    success=False,
                    chain_used=chain,
                    goal_evaluation=goal_evaluation,
                    error=f"Chain contains unregistered tools: {missing_tools}"
                )
            
            # Step 4: Convert input data to proper format for first tool
            formatted_data = self._format_input_data(request.data, request.data_type, chain)
            
            # Step 5: Execute chain using framework
            print(f"⚡ Executing chain: {' → '.join(chain)}")
            result = self.framework.execute_chain(chain, formatted_data)
            
            return AgentResponse(
                success=result.success,
                chain_used=chain,
                goal_evaluation=goal_evaluation,
                result=result,
                error=result.error if not result.success else None
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                chain_used=[],
                goal_evaluation={},
                error=f"Agent orchestration failed: {str(e)}"
            )
    
    def _format_input_data(self, data: Any, data_type: str, chain: List[str]) -> Any:
        """Format input data based on data type and first tool requirements"""
        if not chain:
            return data
        
        first_tool_id = chain[0]
        first_tool_cap = self.framework.capabilities.get(first_tool_id)
        
        if not first_tool_cap:
            return data
        
        # Handle TEXT input formatting
        if data_type.upper() == "TEXT" and first_tool_cap.input_type == DataType.TEXT:
            if isinstance(data, str):
                # Convert plain string to expected format for VectorTool
                return {"text": data}
        
        # Add more data type conversions as needed
        return data
    
    def get_available_chains(self, input_type: DataType = DataType.TEXT) -> Dict[str, List[str]]:
        """Get all possible chains starting from input type"""
        chains = {}
        
        # Find chains to all possible output types
        for output_type in DataType:
            if output_type != input_type:
                chain = self.framework.find_chain(input_type, output_type)
                if chain:
                    chains[f"{input_type.value}_to_{output_type.value}"] = chain
        
        return chains
    
    def demonstrate_capabilities(self, sample_request: str = "Analyze this text for key concepts") -> Dict[str, Any]:
        """Demonstrate agent capabilities with a sample request"""
        print(f"\n🔍 Demonstrating capabilities with request: '{sample_request}'")
        
        # Show goal evaluation
        goal_eval = self.agent.evaluate_goal(sample_request)
        print(f"Goal evaluation: {goal_eval}")
        
        # Show possible chains
        chains = self.get_available_chains()
        print(f"Available chains from TEXT: {list(chains.keys())}")
        
        # Show agent's chain selection
        agent_chain = self.agent.compose_chain(sample_request, "TEXT")
        print(f"Agent selected chain: {agent_chain}")
        
        return {
            "goal_evaluation": goal_eval,
            "available_chains": chains,
            "agent_selected_chain": agent_chain,
            "registered_tools": list(self.framework.tools.keys())
        }