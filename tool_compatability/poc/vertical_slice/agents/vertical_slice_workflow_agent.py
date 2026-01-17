"""Vertical Slice Workflow Agent - Simplified Agent for Dynamic Tool Chain Creation

Adapted from src/agents/workflow_agent.py for use in vertical slice proof-of-concept.
Removes production dependencies while maintaining core functionality.
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

class RealEnhancedAPIClient:
    """Real LLM API client - no mocks, no fallbacks, fail-fast only"""
    def __init__(self):
        self.openai_available = bool(os.getenv('OPENAI_API_KEY'))
        if not self.openai_available:
            raise RuntimeError("OPENAI_API_KEY environment variable not set - LLM intelligence required")
    
    def chat_completion(self, messages, model="gpt-4o-mini"):
        """Make real LLM API call with no fallbacks - fail fast on any error"""
        try:
            import litellm
            response = litellm.completion(
                model=model,
                messages=messages,
                #max_tokens=1000,
                temperature=0.1  # Low temperature for consistent results
            )
            return response
        except Exception as e:
            # Fail fast - no fallbacks allowed
            raise RuntimeError(f"LLM API call failed: {e}. No fallbacks allowed per coding philosophy.")


class VerticalSliceWorkflowAgent:
    """Simplified workflow agent for vertical slice dynamic tool chain creation."""
    
    def __init__(self, api_client: Optional[RealEnhancedAPIClient] = None):
        """Initialize workflow agent.
        
        Args:
            api_client: Optional API client (creates one if not provided)
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialize API client for LLM calls - no fallbacks allowed
        self.api_client = api_client or RealEnhancedAPIClient()
        
        # No workflow engine needed - agent handles composition directly
        
        # Tool capabilities registry (will be populated by integration)
        self.available_tools = {}
        
    def register_tool(self, tool_name: str, tool_capabilities: Dict[str, Any]):
        """Register a tool with its capabilities for chain composition.
        
        Args:
            tool_name: Name of the tool
            tool_capabilities: Dict with input_type, output_type, operations
        """
        self.available_tools[tool_name] = tool_capabilities
        self.logger.debug(f"Registered tool {tool_name} with capabilities: {tool_capabilities}")
    
    def compose_chain(self, request: str, data_type: str = "TEXT") -> List[str]:
        """Compose a tool chain based on natural language request and data type using LLM intelligence.
        
        Args:
            request: Natural language description of what user wants to do
            data_type: Type of input data (TEXT, CSV, JSON, etc.)
            
        Returns:
            List of tool names in execution order
        """
        if not self.api_client.openai_available:
            raise RuntimeError("OPENAI_API_KEY not configured - LLM intelligence required, no fallbacks allowed")
        
        chain = self._llm_intelligent_composition(request, data_type)
        self.logger.info(f"Composed chain for '{request}': {chain}")
        return chain
    
    
    def _llm_intelligent_composition(self, request: str, data_type: str) -> List[str]:
        """Use LLM for intelligent tool chain composition from scratch."""
        
        available_tools_desc = []
        for tool_name, capabilities in self.available_tools.items():
            desc = f"- {tool_name}: {capabilities.get('input_type', 'unknown')} → {capabilities.get('output_type', 'unknown')}"
            if capabilities.get('operations'):
                desc += f" (operations: {', '.join(capabilities['operations'])})"
            available_tools_desc.append(desc)
        
        prompt = f"""
You are an expert at composing tool chains for data processing workflows.

User request: "{request}"
Input data type: {data_type}

Available tools:
{chr(10).join(available_tools_desc)}

Your task:
1. Understand what the user wants to accomplish
2. Design an optimal tool chain that transforms the input data through the necessary steps
3. Each tool's output must be compatible with the next tool's input
4. Choose the shortest effective chain that accomplishes the goal

Rules:
- Chain must start with a tool that accepts {data_type} input
- Each subsequent tool must accept the previous tool's output type
- Choose tools that directly serve the user's stated goal
- Avoid unnecessary steps

Examples:
- For "generate embeddings": Just VectorTool (text → vector)
- For "analyze and store": VectorTool → TableTool (text → vector → table)
- For "create knowledge graph": VectorTool → GraphTool (text → vector → graph) OR VectorTool → TableTool → GraphTool (text → vector → table → graph)

Respond with JSON only:
{{
    "chain": ["Tool1", "Tool2", ...],
    "reasoning": "explanation of why this chain was chosen"
}}
"""

        try:
            messages = [
                {"role": "system", "content": "You are an expert tool chain composer. Analyze the request carefully and respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.api_client.chat_completion(messages)
            llm_response = response["choices"][0]["message"]["content"]
            
            # Extract JSON from response
            if "{" in llm_response and "}" in llm_response:
                start = llm_response.find("{")
                end = llm_response.rfind("}") + 1
                json_str = llm_response[start:end]
                
                chain_data = json.loads(json_str)
                chain = chain_data.get("chain", [])
                
                # Validate that all tools exist and chain is valid
                valid_chain = [tool for tool in chain if tool in self.available_tools]
                
                if valid_chain and len(valid_chain) == len(chain):
                    self.logger.info(f"LLM composed chain: {chain} (reasoning: {chain_data.get('reasoning', 'none')})")
                    return valid_chain
                else:
                    raise RuntimeError(f"LLM chain contained invalid tools: {chain}. Available tools: {list(self.available_tools.keys())}")
                    
        except Exception as e:
            self.logger.error(f"LLM chain composition failed: {e}")
            raise RuntimeError(f"LLM chain composition failed and no fallbacks allowed: {e}")
    
    def _llm_enhanced_composition(self, request: str, data_type: str, initial_chain: List[str]) -> List[str]:
        """Use LLM to enhance or validate the tool chain composition."""
        try:
            prompt = self._create_chain_composition_prompt(request, data_type, initial_chain)
            
            messages = [
                {"role": "system", "content": "You are a tool chain composition expert. Respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.api_client.chat_completion(messages)
            
            # Parse LLM response
            llm_response = response["choices"][0]["message"]["content"]
            
            # Try to extract JSON from response
            if "{" in llm_response and "}" in llm_response:
                start = llm_response.find("{")
                end = llm_response.rfind("}") + 1
                json_str = llm_response[start:end]
                
                workflow_data = json.loads(json_str)
                
                if "workflow" in workflow_data and "steps" in workflow_data["workflow"]:
                    steps = workflow_data["workflow"]["steps"]
                    enhanced_chain = [step.get("tool", "") for step in steps if step.get("tool")]
                    
                    # Validate that all tools are available
                    valid_chain = [tool for tool in enhanced_chain if tool in self.available_tools]
                    
                    if valid_chain:
                        return valid_chain
            
            # If LLM enhancement fails, return initial chain
            return initial_chain
            
        except Exception as e:
            self.logger.warning(f"LLM enhancement failed: {e}, using rule-based chain")
            return initial_chain
    
    def _create_chain_composition_prompt(self, request: str, data_type: str, initial_chain: List[str]) -> str:
        """Create prompt for LLM chain composition."""
        available_tools_desc = []
        for tool_name, capabilities in self.available_tools.items():
            desc = f"- {tool_name}: {capabilities.get('input_type', 'unknown')} → {capabilities.get('output_type', 'unknown')}"
            if capabilities.get('operations'):
                desc += f" (operations: {', '.join(capabilities['operations'])})"
            available_tools_desc.append(desc)
        
        prompt = f"""
Task: Create a tool chain to accomplish this request: "{request}"

Input data type: {data_type}
Initial suggested chain: {initial_chain}

Available tools:
{chr(10).join(available_tools_desc)}

Requirements:
1. Chain should start with a tool that can process {data_type} input
2. Each tool's output should match the next tool's input type
3. Chain should accomplish the user's request efficiently
4. Prefer shorter chains when possible

Respond with JSON in this exact format:
{{
    "workflow": {{
        "name": "Tool Chain for Request",
        "steps": [
            {{"tool": "ToolName1", "operation": "operation_name"}},
            {{"tool": "ToolName2", "operation": "operation_name"}}
        ]
    }}
}}
"""
        return prompt
    
    
    def evaluate_goal(self, request: str) -> Dict[str, Any]:
        """Evaluate user goal and determine requirements using LLM intelligence.
        
        Args:
            request: Natural language request
            
        Returns:
            Dict with goal analysis
        """
        if not self.api_client.openai_available:
            raise RuntimeError("OPENAI_API_KEY not configured - LLM intelligence required, no fallbacks allowed")
        
        return self._llm_goal_evaluation(request)
    
    def _llm_goal_evaluation(self, request: str) -> Dict[str, Any]:
        """Use LLM to intelligently evaluate user goals and requirements."""
        
        available_tools_desc = []
        for tool_name, capabilities in self.available_tools.items():
            desc = f"- {tool_name}: {capabilities.get('input_type', 'unknown')} → {capabilities.get('output_type', 'unknown')}"
            if capabilities.get('operations'):
                desc += f" (operations: {', '.join(capabilities['operations'])})"
            available_tools_desc.append(desc)
        
        prompt = f"""
Analyze this user request and determine the processing requirements:
"{request}"

Available tools and capabilities:
{chr(10).join(available_tools_desc)}

Please analyze:
1. What is the main goal/intent behind this request?
2. What level of complexity does this require (low/medium/high)?
3. What specific capabilities are needed to fulfill this request?
4. How many processing steps would this likely require?

Consider:
- Simple tasks (like basic embedding) are low complexity
- Analysis tasks that require multiple steps are medium complexity  
- Complex tasks requiring graph construction, relationships, or multi-stage processing are high complexity

Respond with JSON only:
{{
    "goal_type": "embedding|data_analysis|knowledge_extraction|visualization|storage|general_processing",
    "complexity": "low|medium|high",
    "required_capabilities": ["capability1", "capability2", ...],
    "estimated_tools_needed": number,
    "reasoning": "explanation of why this analysis was chosen"
}}
"""

        try:
            messages = [
                {"role": "system", "content": "You are an expert at analyzing data processing requirements. Respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.api_client.chat_completion(messages)
            llm_response = response["choices"][0]["message"]["content"]
            
            # Extract JSON from response
            if "{" in llm_response and "}" in llm_response:
                start = llm_response.find("{")
                end = llm_response.rfind("}") + 1
                json_str = llm_response[start:end]
                
                goal_analysis = json.loads(json_str)
                goal_analysis["request"] = request
                return goal_analysis
            
        except Exception as e:
            self.logger.error(f"LLM goal evaluation failed: {e}")
            raise RuntimeError(f"LLM goal evaluation failed and no fallbacks allowed: {e}")
    
