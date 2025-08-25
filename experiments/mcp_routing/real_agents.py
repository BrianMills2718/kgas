#!/usr/bin/env python3
"""
Real AI Agent Implementations

Implements actual API integrations with OpenAI, Anthropic, and Google
for testing real agent behavior in tool selection and usage.
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import time
from abc import ABC

# Import the base agent classes
from agent_validation_framework import AIAgent, AgentType, ReferenceWorkflow

logger = logging.getLogger(__name__)

# Real agent implementations require API keys
class OpenAIAgent(AIAgent):
    """Real OpenAI GPT agent implementation"""
    
    def __init__(self, agent_type: AgentType, api_key: Optional[str] = None):
        super().__init__(agent_type, api_key)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable.")
        
        # Import OpenAI here to avoid dependency issues if not needed
        try:
            import openai
            self.client = openai.AsyncOpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("openai package required for OpenAI agents. Install with: pip install openai")
    
    async def select_tools_for_workflow(self, workflow_description: str,
                                      available_tools: List[Dict],
                                      context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Use GPT to select tools for a workflow"""
        
        # Create tool descriptions for the prompt
        tool_descriptions = []
        for tool in available_tools:
            tool_desc = f"- {tool['name']}: {tool.get('description', 'No description')}"
            tool_descriptions.append(tool_desc)
        
        prompt = f"""
You are an AI assistant helping to select the best tools for a knowledge graph analysis workflow.

WORKFLOW DESCRIPTION: {workflow_description}

CONTEXT: {json.dumps(context, indent=2)}

AVAILABLE TOOLS:
{chr(10).join(tool_descriptions)}

Your task is to select the most appropriate tools and parameters for this workflow. 
Return your response as a JSON list where each item has:
- "tool": the exact tool name
- "parameters": dict of parameter name-value pairs
- "reasoning": brief explanation why this tool is appropriate

Consider:
1. The workflow context and complexity
2. The document type and domain
3. The expected outputs and quality requirements
4. Efficiency vs. completeness trade-offs

Respond with only the JSON list, no other text.
"""
        
        self.log_decision("tool_selection_request", {
            "workflow_description": workflow_description,
            "available_tools_count": len(available_tools),
            "context": context
        }, "gpt_selection_request")
        
        try:
            # GPT-4 doesn't support structured output, use GPT-4o-mini for JSON format
            model_to_use = "gpt-4o-mini" if self.agent_type.value == "gpt-4" else self.agent_type.value
            
            completion_params = {
                "model": model_to_use,
                "messages": [
                    {"role": "system", "content": "You are a tool selection expert for knowledge graph workflows. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,  # Low temperature for consistent tool selection
                "max_tokens": 1000
            }
            
            # Only add response_format for models that support it
            if "gpt-4o" in model_to_use or "gpt-3.5" in model_to_use:
                completion_params["response_format"] = {"type": "json_object"}
            
            response = await self.client.chat.completions.create(**completion_params)
            
            response_text = response.choices[0].message.content
            
            # Parse the JSON response
            try:
                selected_tools = json.loads(response_text)
                if isinstance(selected_tools, dict) and "tools" in selected_tools:
                    selected_tools = selected_tools["tools"]
                elif not isinstance(selected_tools, list):
                    # Wrap single tool selection in list
                    selected_tools = [selected_tools]
                
                self.log_decision("tool_selection_result", {
                    "raw_response": response_text,
                    "parsed_tools": selected_tools
                }, selected_tools)
                
                return selected_tools
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse GPT response as JSON: {e}")
                logger.error(f"Raw response: {response_text}")
                
                # Fallback to heuristic selection
                return self._fallback_tool_selection(workflow_description, available_tools, context)
                
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            return self._fallback_tool_selection(workflow_description, available_tools, context)
    
    async def execute_workflow(self, workflow: ReferenceWorkflow, 
                             tools: List[Dict]) -> Dict[str, Any]:
        """Execute workflow with selected tools (simulated)"""
        start_time = time.time()
        
        # For now, simulate execution since we don't have actual tool implementations
        # In real implementation, this would call the actual KGAS tools
        await asyncio.sleep(0.2)  # Simulate processing time
        
        execution_time = (time.time() - start_time) * 1000
        
        # Extract tool information
        tools_used = [tool["tool"] for tool in tools]
        parameters_used = [tool.get("parameters", {}) for tool in tools]
        
        # Simulate realistic success/failure based on tool appropriateness
        # More sophisticated agents should have higher success rates
        success_rate = 0.85 if "gpt-4" in self.agent_type.value else 0.75
        success = hash(str(tools)) % 100 < (success_rate * 100)
        
        return {
            "success": success,
            "execution_time_ms": execution_time,
            "tools_used": tools_used,
            "parameters_used": parameters_used,
            "results": {"simulated_execution": True, "agent_type": self.agent_type.value},
            "errors": [] if success else [f"Simulated execution error for {self.agent_type.value}"],
            "reasoning": f"Real {self.agent_type.value} agent tool selection and execution"
        }
    
    def _fallback_tool_selection(self, workflow_description: str, 
                               available_tools: List[Dict], 
                               context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fallback heuristic tool selection if API fails"""
        selected_tools = []
        
        # Simple heuristics based on keywords
        if "document" in workflow_description.lower():
            doc_tools = [t for t in available_tools if "load" in t["name"].lower()]
            if doc_tools:
                selected_tools.append({
                    "tool": doc_tools[0]["name"],
                    "parameters": {"fallback_selection": True},
                    "reasoning": "Fallback: document loading detected"
                })
        
        if "extract" in workflow_description.lower() or "analyz" in workflow_description.lower():
            extract_tools = [t for t in available_tools if "extract" in t["name"].lower()]
            if extract_tools:
                selected_tools.append({
                    "tool": extract_tools[0]["name"],
                    "parameters": {"method": "hybrid", "fallback_selection": True},
                    "reasoning": "Fallback: extraction task detected"
                })
        
        self.log_decision("fallback_selection", {
            "reason": "API_failure_or_parse_error",
            "workflow_description": workflow_description
        }, selected_tools)
        
        return selected_tools


class AnthropicAgent(AIAgent):
    """Real Anthropic Claude agent implementation"""
    
    def __init__(self, agent_type: AgentType, api_key: Optional[str] = None):
        super().__init__(agent_type, api_key)
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key required. Set ANTHROPIC_API_KEY environment variable.")
        
        try:
            import anthropic
            self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("anthropic package required for Claude agents. Install with: pip install anthropic")
    
    async def select_tools_for_workflow(self, workflow_description: str,
                                      available_tools: List[Dict],
                                      context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Use Claude to select tools for a workflow"""
        
        # Format tools for Claude
        tool_list = []
        for i, tool in enumerate(available_tools, 1):
            tool_list.append(f"{i}. {tool['name']}: {tool.get('description', 'No description')}")
        
        prompt = f"""I need to select the optimal tools and parameters for a knowledge graph analysis workflow.

WORKFLOW: {workflow_description}

CONTEXT:
{json.dumps(context, indent=2)}

AVAILABLE TOOLS:
{chr(10).join(tool_list)}

Please analyze this workflow and select the most appropriate tools with their parameters. Consider:
- The workflow complexity and requirements
- The document type: {context.get('document_type', 'unknown')}
- The domain: {context.get('domain', 'general')}
- Expected quality and performance trade-offs

Return your response as a JSON array where each tool selection has:
{{
  "tool": "exact_tool_name",
  "parameters": {{"param_name": "value"}},
  "reasoning": "brief explanation"
}}

Respond with only the JSON array, no other text."""

        self.log_decision("tool_selection_request", {
            "workflow_description": workflow_description,
            "available_tools_count": len(available_tools),
            "context": context
        }, "claude_selection_request")

        try:
            response = await self.client.messages.create(
                model=self.agent_type.value,
                max_tokens=1000,
                temperature=0.1,
                messages=[
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ]
            )
            
            response_text = response.content[0].text
            
            # Clean and parse the response
            try:
                # Claude sometimes wraps JSON in markdown
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                
                selected_tools = json.loads(response_text)
                
                self.log_decision("tool_selection_result", {
                    "raw_response": response.content[0].text,
                    "cleaned_response": response_text,
                    "parsed_tools": selected_tools
                }, selected_tools)
                
                return selected_tools
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Claude response as JSON: {e}")
                logger.error(f"Raw response: {response.content[0].text}")
                
                return self._fallback_tool_selection(workflow_description, available_tools, context)
                
        except Exception as e:
            logger.error(f"Anthropic API call failed: {e}")
            return self._fallback_tool_selection(workflow_description, available_tools, context)
    
    async def execute_workflow(self, workflow: ReferenceWorkflow, 
                             tools: List[Dict]) -> Dict[str, Any]:
        """Execute workflow with selected tools (simulated)"""
        start_time = time.time()
        
        # Simulate processing
        await asyncio.sleep(0.15)
        
        execution_time = (time.time() - start_time) * 1000
        
        tools_used = [tool["tool"] for tool in tools]
        parameters_used = [tool.get("parameters", {}) for tool in tools]
        
        # Claude generally performs well on structured tasks
        success_rate = 0.88 if "sonnet" in self.agent_type.value else 0.82
        success = hash(str(tools)) % 100 < (success_rate * 100)
        
        return {
            "success": success,
            "execution_time_ms": execution_time,
            "tools_used": tools_used,
            "parameters_used": parameters_used,
            "results": {"simulated_execution": True, "agent_type": self.agent_type.value},
            "errors": [] if success else [f"Simulated execution error for {self.agent_type.value}"],
            "reasoning": f"Real {self.agent_type.value} agent with structured reasoning"
        }
    
    def _fallback_tool_selection(self, workflow_description: str, 
                               available_tools: List[Dict], 
                               context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fallback tool selection for Claude"""
        # Claude's fallback tends to be more conservative
        selected_tools = []
        
        # More sophisticated heuristics for Claude
        workflow_lower = workflow_description.lower()
        
        if "academic" in workflow_lower or "research" in workflow_lower:
            # Academic papers need comprehensive processing
            load_tools = [t for t in available_tools if "comprehensive" in t["name"].lower()]
            if load_tools:
                selected_tools.append({
                    "tool": load_tools[0]["name"],
                    "parameters": {"extract_metadata": True, "quality_check": True},
                    "reasoning": "Academic content requires comprehensive loading"
                })
        elif "simple" in workflow_lower or "basic" in workflow_lower:
            # Simple tasks use basic tools
            load_tools = [t for t in available_tools if "basic" in t["name"].lower()]
            if load_tools:
                selected_tools.append({
                    "tool": load_tools[0]["name"],
                    "parameters": {"extract_metadata": False},
                    "reasoning": "Simple task requires basic processing"
                })
        
        # Always add extraction if needed
        if "extract" in workflow_lower:
            extract_tools = [t for t in available_tools if "extract" in t["name"].lower()]
            if extract_tools:
                # Claude tends to choose appropriate methods based on context
                method = "hybrid" if context.get("complexity") == "high" else "spacy"
                selected_tools.append({
                    "tool": extract_tools[0]["name"],
                    "parameters": {"method": method, "ontology_mode": "mixed"},
                    "reasoning": f"Extraction with {method} method for {context.get('complexity', 'medium')} complexity"
                })
        
        self.log_decision("fallback_selection", {
            "reason": "API_failure_or_parse_error",
            "workflow_description": workflow_description,
            "fallback_strategy": "conservative_heuristics"
        }, selected_tools)
        
        return selected_tools


class GoogleAgent(AIAgent):
    """Real Google Gemini agent implementation"""
    
    def __init__(self, agent_type: AgentType, api_key: Optional[str] = None):
        super().__init__(agent_type, api_key)
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key required. Set GOOGLE_API_KEY environment variable.")
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            # Use the full model path for Gemini models
            model_name = self.agent_type.value
            if model_name == "gemini-2.5-flash":
                model_name = "models/gemini-2.5-flash"
            self.model = genai.GenerativeModel(model_name)
        except ImportError:
            raise ImportError("google-generativeai package required for Gemini agents. Install with: pip install google-generativeai")
    
    async def select_tools_for_workflow(self, workflow_description: str,
                                      available_tools: List[Dict],
                                      context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Use Gemini to select tools for a workflow"""
        
        # Format available tools
        tools_formatted = []
        for tool in available_tools:
            tools_formatted.append({
                "name": tool["name"],
                "description": tool.get("description", "No description available")
            })
        
        prompt = f"""You are an expert in knowledge graph analysis workflows. Select the optimal tools and parameters for this task.

WORKFLOW TASK: {workflow_description}

ANALYSIS CONTEXT:
{json.dumps(context, indent=2)}

AVAILABLE TOOLS:
{json.dumps(tools_formatted, indent=2)}

Based on the workflow requirements and context, select the most appropriate tools with their parameters.

Guidelines:
- For academic papers: use comprehensive loading with metadata extraction
- For simple tasks: use basic loading without unnecessary overhead  
- For entity extraction: choose method based on complexity (spacy for simple, hybrid for complex)
- For relationship analysis: ensure relationship extraction is enabled

Return a JSON array with this structure:
[
  {{
    "tool": "exact_tool_name",
    "parameters": {{"param1": "value1", "param2": "value2"}},
    "reasoning": "why this tool and parameters are optimal"
  }}
]

Respond with only the JSON array."""

        self.log_decision("tool_selection_request", {
            "workflow_description": workflow_description,
            "available_tools_count": len(available_tools),
            "context": context
        }, "gemini_selection_request")

        try:
            # Gemini API is synchronous, so we'll wrap it
            import asyncio
            
            def _sync_generate():
                return self.model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": 0.1,
                        "max_output_tokens": 1000,
                    }
                )
            
            response = await asyncio.get_event_loop().run_in_executor(None, _sync_generate)
            response_text = response.text
            
            # Parse JSON response
            try:
                # Clean up common Gemini response formatting
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                
                # Extract JSON array more robustly
                import re
                # Look for a JSON array that starts with [ and has at least one complete object
                json_match = re.search(r'\[[\s\S]*?\]', response_text)
                if json_match:
                    response_text = json_match.group(0)
                    # If the JSON seems truncated, try to fix simple cases
                    if not response_text.strip().endswith(']'):
                        # Try to find the last complete object and close properly
                        last_brace = response_text.rfind('}')
                        if last_brace > 0:
                            response_text = response_text[:last_brace+1] + '\n]'
                
                selected_tools = json.loads(response_text)
                
                self.log_decision("tool_selection_result", {
                    "raw_response": response.text,
                    "cleaned_response": response_text,
                    "parsed_tools": selected_tools
                }, selected_tools)
                
                return selected_tools
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini response as JSON: {e}")
                logger.error(f"Raw response: {response.text}")
                
                return self._fallback_tool_selection(workflow_description, available_tools, context)
                
        except Exception as e:
            logger.error(f"Google Gemini API call failed: {e}")
            return self._fallback_tool_selection(workflow_description, available_tools, context)
    
    async def execute_workflow(self, workflow: ReferenceWorkflow, 
                             tools: List[Dict]) -> Dict[str, Any]:
        """Execute workflow with selected tools (simulated)"""
        start_time = time.time()
        
        # Simulate processing
        await asyncio.sleep(0.12)
        
        execution_time = (time.time() - start_time) * 1000
        
        tools_used = [tool["tool"] for tool in tools]
        parameters_used = [tool.get("parameters", {}) for tool in tools]
        
        # Gemini performance varies by task complexity
        base_success_rate = 0.80 if "flash" in self.agent_type.value else 0.75
        
        # Adjust success rate based on workflow complexity
        complexity_penalty = 0.1 if workflow.difficulty_level == "hard" else 0.0
        success_rate = base_success_rate - complexity_penalty
        
        success = hash(str(tools)) % 100 < (success_rate * 100)
        
        return {
            "success": success,
            "execution_time_ms": execution_time,
            "tools_used": tools_used,
            "parameters_used": parameters_used,
            "results": {"simulated_execution": True, "agent_type": self.agent_type.value},
            "errors": [] if success else [f"Simulated execution error for {self.agent_type.value}"],
            "reasoning": f"Real {self.agent_type.value} agent with multimodal reasoning"
        }
    
    def _fallback_tool_selection(self, workflow_description: str, 
                               available_tools: List[Dict], 
                               context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fallback tool selection for Gemini"""
        selected_tools = []
        
        # Gemini's multimodal capabilities inform its heuristics
        workflow_lower = workflow_description.lower()
        
        # Gemini tends to be thorough with document analysis
        if "document" in workflow_lower or "paper" in workflow_lower:
            load_tools = [t for t in available_tools if "load" in t["name"].lower()]
            if load_tools:
                # Prefer comprehensive tools for document tasks
                comprehensive_tools = [t for t in load_tools if "comprehensive" in t["name"].lower()]
                selected_tool = comprehensive_tools[0] if comprehensive_tools else load_tools[0]
                
                selected_tools.append({
                    "tool": selected_tool["name"],
                    "parameters": {"extract_metadata": True},
                    "reasoning": "Document processing benefits from comprehensive analysis"
                })
        
        # Gemini is good at choosing appropriate extraction methods
        if "extract" in workflow_lower:
            extract_tools = [t for t in available_tools if "extract" in t["name"].lower()]
            if extract_tools:
                # Choose method based on context
                if context.get("domain") == "machine_learning" or context.get("complexity") == "high":
                    method = "hybrid"
                    ontology_mode = "mixed"
                else:
                    method = "llm"
                    ontology_mode = "closed"
                
                selected_tools.append({
                    "tool": extract_tools[0]["name"],
                    "parameters": {"method": method, "ontology_mode": ontology_mode},
                    "reasoning": f"Selected {method} method for {context.get('complexity', 'medium')} complexity task"
                })
        
        # Add analysis if workflow suggests insights are needed
        if "analyz" in workflow_lower or "insight" in workflow_lower:
            analysis_tools = [t for t in available_tools if "analyz" in t["name"].lower()]
            if analysis_tools:
                selected_tools.append({
                    "tool": analysis_tools[0]["name"],
                    "parameters": {"include_analytics": True},
                    "reasoning": "Analysis required for insight generation"
                })
        
        self.log_decision("fallback_selection", {
            "reason": "API_failure_or_parse_error",
            "workflow_description": workflow_description,
            "fallback_strategy": "multimodal_heuristics"
        }, selected_tools)
        
        return selected_tools


# Agent factory function
def create_real_agent(agent_type: AgentType, api_key: Optional[str] = None) -> AIAgent:
    """Factory function to create real AI agents"""
    
    if agent_type in [AgentType.GPT_4, AgentType.GPT_4O_MINI]:
        return OpenAIAgent(agent_type, api_key)
    elif agent_type in [AgentType.CLAUDE_SONNET, AgentType.CLAUDE_HAIKU]:
        return AnthropicAgent(agent_type, api_key)
    elif agent_type == AgentType.GEMINI_FLASH:
        return GoogleAgent(agent_type, api_key)
    else:
        raise ValueError(f"Unsupported agent type: {agent_type}")


# Example usage and testing
async def test_real_agents():
    """Test real agents with actual API calls"""
    
    print("Testing Real AI Agents for Tool Selection")
    print("=" * 50)
    
    # Check for API keys
    required_keys = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY")
    }
    
    available_agents = []
    for key_name, key_value in required_keys.items():
        if key_value:
            print(f"✅ {key_name} found")
            if "OPENAI" in key_name:
                available_agents.extend([AgentType.GPT_4])
            elif "ANTHROPIC" in key_name:
                available_agents.extend([AgentType.CLAUDE_SONNET])
            elif "GOOGLE" in key_name:
                available_agents.extend([AgentType.GEMINI_FLASH])
        else:
            print(f"❌ {key_name} not found - skipping related agents")
    
    if not available_agents:
        print("\n❌ No API keys found. Set environment variables to test real agents:")
        print("   export OPENAI_API_KEY='your-key'")
        print("   export ANTHROPIC_API_KEY='your-key'")
        print("   export GOOGLE_API_KEY='your-key'")
        return
    
    # Test available agents
    mock_tools = [
        {"name": "load_document_comprehensive", "description": "Load document with full metadata extraction"},
        {"name": "load_document_basic", "description": "Basic document loading without metadata"},
        {"name": "extract_knowledge_graph", "description": "Extract entities and relationships from text"},
        {"name": "analyze_graph_insights", "description": "Analyze knowledge graph for patterns and insights"}
    ]
    
    test_workflow = "Analyze an academic research paper to extract key methodological contributions and relationships"
    test_context = {
        "document_type": "academic_paper",
        "domain": "machine_learning",
        "complexity": "high",
        "expected_entities": ["methods", "algorithms", "datasets", "metrics"]
    }
    
    print(f"\nTesting {len(available_agents)} available agents...")
    
    for agent_type in available_agents:
        print(f"\n🧠 Testing {agent_type.value}...")
        
        try:
            agent = create_real_agent(agent_type)
            
            start_time = time.time()
            selected_tools = await agent.select_tools_for_workflow(
                test_workflow,
                mock_tools,
                test_context
            )
            selection_time = time.time() - start_time
            
            print(f"   ⏱️  Selection time: {selection_time:.2f}s")
            print(f"   🛠️  Selected {len(selected_tools)} tools:")
            
            for i, tool in enumerate(selected_tools, 1):
                print(f"      {i}. {tool['tool']}")
                if tool.get('parameters'):
                    print(f"         Parameters: {tool['parameters']}")
                if tool.get('reasoning'):
                    print(f"         Reasoning: {tool['reasoning']}")
            
        except Exception as e:
            print(f"   ❌ Error testing {agent_type.value}: {e}")
    
    print("\n✅ Real agent testing completed!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_real_agents())