#!/usr/bin/env python3
"""
Real Agent Validation Runner

Runs comprehensive validation testing with real AI agents to validate
MCP tool organization strategies and agent behavior patterns.
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import time

# Import our frameworks
from agent_validation_framework import (
    AgentValidationFramework, 
    AgentType, 
    MockAIAgent,
    ValidationStatus
)
from real_agents import create_real_agent
from mock_tool_generator import MockToolGenerator, ToolCategory
from test_framework import (
    SemanticWorkflowStrategy,
    DirectExposureStrategy,
    DynamicFilteringStrategy
)

logger = logging.getLogger(__name__)

class RealAgentValidationRunner:
    """Orchestrates comprehensive real agent validation testing"""
    
    def __init__(self):
        self.framework = AgentValidationFramework()
        self.available_agents = self._detect_available_agents()
        self.tool_generator = MockToolGenerator()
        self.results = {}
        
    def _detect_available_agents(self) -> Dict[AgentType, bool]:
        """Detect which real agents can be tested based on API keys"""
        availability = {}
        
        # Check API keys
        api_keys = {
            AgentType.GPT_4: os.getenv("OPENAI_API_KEY"),
            AgentType.GPT_4O_MINI: os.getenv("OPENAI_API_KEY"),
            AgentType.CLAUDE_SONNET: os.getenv("ANTHROPIC_API_KEY"),
            AgentType.CLAUDE_HAIKU: os.getenv("ANTHROPIC_API_KEY"),
            AgentType.GEMINI_FLASH: os.getenv("GOOGLE_API_KEY")
        }
        
        for agent_type, api_key in api_keys.items():
            availability[agent_type] = api_key is not None
            
        return availability
    
    async def setup_agents(self) -> Dict[str, str]:
        """Setup all available agents for testing"""
        setup_results = {}
        
        for agent_type, available in self.available_agents.items():
            if available:
                try:
                    # Test with real agent
                    real_agent = create_real_agent(agent_type)
                    self.framework.register_agent(real_agent)
                    setup_results[agent_type.value] = "✅ Real Agent"
                    logger.info(f"Registered real agent: {agent_type.value}")
                    
                except Exception as e:
                    # Fallback to mock agent
                    mock_agent = MockAIAgent(agent_type)
                    self.framework.register_agent(mock_agent)
                    setup_results[agent_type.value] = f"⚠️ Mock Agent (Real failed: {str(e)[:50]})"
                    logger.warning(f"Failed to create real agent {agent_type.value}, using mock: {e}")
                    
            else:
                # Use mock agent when API key not available
                mock_agent = MockAIAgent(agent_type)
                self.framework.register_agent(mock_agent)
                setup_results[agent_type.value] = "🔑 Mock Agent (No API Key)"
                logger.info(f"No API key for {agent_type.value}, using mock agent")
        
        return setup_results
    
    def generate_strategy_tools(self, strategy_name: str) -> List[Dict]:
        """Generate tools for different MCP organization strategies"""
        
        # Generate base set of 100 tools
        all_tools = self.tool_generator.generate_all_tools()
        
        # Convert to MCP tool format
        mcp_tools = []
        for tool in all_tools:
            mcp_tools.append({
                "name": tool.tool_id,
                "description": tool.description,
                "category": tool.category.value,
                "complexity": tool.complexity_score
            })
        
        # Apply strategy-specific filtering
        scenario_context = {
            "keywords": ["document", "extract", "analyze", "graph"],
            "complexity": "medium",
            "user_intent": "general_analysis"
        }
        
        if strategy_name == "semantic_workflow":
            strategy = SemanticWorkflowStrategy()
            organized_tools = strategy.organize_tools(all_tools, scenario_context)
            return [{"name": t.tool_id, "description": t.description} for t in organized_tools]
            
        elif strategy_name == "dynamic_filtering":
            strategy = DynamicFilteringStrategy()
            organized_tools = strategy.organize_tools(all_tools, scenario_context)
            return [{"name": t.tool_id, "description": t.description} for t in organized_tools[:10]]
            
        elif strategy_name == "direct_exposure":
            # Return all tools (testing the 40+ tool barrier)
            return mcp_tools
            
        else:
            # Default to semantic workflow
            strategy = SemanticWorkflowStrategy()
            organized_tools = strategy.organize_tools(all_tools, scenario_context)
            return [{"name": t.tool_id, "description": t.description} for t in organized_tools]
    
    async def run_strategy_comparison(self) -> Dict[str, Any]:
        """Compare agent performance across different MCP organization strategies"""
        
        strategies = ["semantic_workflow", "dynamic_filtering", "direct_exposure"]
        workflows = ["academic_paper_analysis", "simple_entity_extraction"]
        
        comparison_results = {}
        
        logger.info(f"Starting strategy comparison: {len(strategies)} strategies × {len(workflows)} workflows")
        
        for strategy_name in strategies:
            logger.info(f"Testing strategy: {strategy_name}")
            
            # Generate tools for this strategy
            strategy_tools = self.generate_strategy_tools(strategy_name)
            logger.info(f"Generated {len(strategy_tools)} tools for {strategy_name} strategy")
            
            strategy_results = {}
            
            for workflow_id in workflows:
                workflow_results = {}
                
                # Test each available agent
                for agent_type in self.available_agents.keys():
                    if agent_type not in self.framework.agents:
                        continue
                        
                    try:
                        logger.info(f"Testing {agent_type.value} on {workflow_id} with {strategy_name}")
                        
                        result = await self.framework.test_agent_workflow(
                            agent_type,
                            workflow_id,
                            strategy_tools
                        )
                        
                        # Update strategy name in result
                        result.strategy_name = strategy_name
                        
                        workflow_results[agent_type.value] = {
                            "success": result.success,
                            "overall_score": result.overall_score,
                            "tool_selection_accuracy": result.tool_selection_accuracy,
                            "parameter_accuracy": result.parameter_accuracy,
                            "execution_time_ms": result.execution_time_ms,
                            "tools_used": result.tools_used,
                            "errors": result.errors
                        }
                        
                    except Exception as e:
                        logger.error(f"Failed testing {agent_type.value} on {workflow_id}: {e}")
                        workflow_results[agent_type.value] = {
                            "error": str(e),
                            "success": False
                        }
                
                strategy_results[workflow_id] = workflow_results
            
            comparison_results[strategy_name] = strategy_results
        
        return comparison_results
    
    async def run_agent_behavior_analysis(self) -> Dict[str, Any]:
        """Deep analysis of individual agent behavior patterns"""
        
        behavior_results = {}
        
        # Use semantic workflow tools for consistent testing
        test_tools = self.generate_strategy_tools("semantic_workflow")
        
        for agent_type in self.available_agents.keys():
            if agent_type not in self.framework.agents:
                continue
                
            logger.info(f"Analyzing behavior patterns for {agent_type.value}")
            
            agent_behavior = {
                "consistency_tests": [],
                "parameter_patterns": {},
                "tool_preferences": {},
                "error_patterns": []
            }
            
            # Test consistency across multiple runs of same workflow
            for run in range(3):
                try:
                    result = await self.framework.test_agent_workflow(
                        agent_type,
                        "academic_paper_analysis",
                        test_tools
                    )
                    
                    agent_behavior["consistency_tests"].append({
                        "run": run + 1,
                        "tools_selected": result.tools_used,
                        "parameters": result.parameters_used,
                        "score": result.overall_score
                    })
                    
                except Exception as e:
                    agent_behavior["error_patterns"].append({
                        "run": run + 1,
                        "error": str(e)
                    })
            
            # Analyze decision logs if available
            agent_instance = self.framework.agents[agent_type]
            if hasattr(agent_instance, 'decision_log') and agent_instance.decision_log:
                recent_decisions = agent_instance.decision_log[-10:]  # Last 10 decisions
                
                # Extract tool preferences
                tool_choices = []
                for decision in recent_decisions:
                    if decision["decision_type"] == "tool_selection_result":
                        if isinstance(decision["decision"], list):
                            for tool_choice in decision["decision"]:
                                if isinstance(tool_choice, dict) and "tool" in tool_choice:
                                    tool_choices.append(tool_choice["tool"])
                
                # Count tool preferences
                from collections import Counter
                tool_counts = Counter(tool_choices)
                agent_behavior["tool_preferences"] = dict(tool_counts)
            
            behavior_results[agent_type.value] = agent_behavior
        
        return behavior_results
    
    def analyze_results(self, strategy_results: Dict, behavior_results: Dict) -> Dict[str, Any]:
        """Analyze and summarize all validation results"""
        
        analysis = {
            "strategy_performance": {},
            "agent_rankings": {},
            "key_findings": [],
            "recommendations": []
        }
        
        # Strategy performance analysis
        for strategy_name, strategy_data in strategy_results.items():
            strategy_scores = []
            strategy_success_rate = 0.0
            total_tests = 0
            successful_tests = 0
            
            for workflow_id, workflow_data in strategy_data.items():
                for agent_name, agent_result in workflow_data.items():
                    if not isinstance(agent_result, dict) or "error" in agent_result:
                        continue
                        
                    total_tests += 1
                    if agent_result.get("success", False):
                        successful_tests += 1
                        strategy_scores.append(agent_result.get("overall_score", 0.0))
            
            if strategy_scores:
                analysis["strategy_performance"][strategy_name] = {
                    "average_score": sum(strategy_scores) / len(strategy_scores),
                    "success_rate": successful_tests / total_tests if total_tests > 0 else 0.0,
                    "total_tests": total_tests,
                    "successful_tests": successful_tests
                }
        
        # Agent performance rankings
        agent_scores = {}
        for strategy_name, strategy_data in strategy_results.items():
            for workflow_id, workflow_data in strategy_data.items():
                for agent_name, agent_result in workflow_data.items():
                    if not isinstance(agent_result, dict) or "error" in agent_result:
                        continue
                        
                    if agent_name not in agent_scores:
                        agent_scores[agent_name] = []
                    
                    if agent_result.get("success", False):
                        agent_scores[agent_name].append(agent_result.get("overall_score", 0.0))
        
        # Calculate agent averages
        for agent_name, scores in agent_scores.items():
            if scores:
                analysis["agent_rankings"][agent_name] = {
                    "average_score": sum(scores) / len(scores),
                    "test_count": len(scores),
                    "consistency": max(scores) - min(scores) if len(scores) > 1 else 0.0
                }
        
        # Generate key findings
        if analysis["strategy_performance"]:
            best_strategy = max(analysis["strategy_performance"].items(), 
                              key=lambda x: x[1]["average_score"])
            analysis["key_findings"].append(
                f"Best performing strategy: {best_strategy[0]} "
                f"(avg score: {best_strategy[1]['average_score']:.2f})"
            )
        
        if analysis["agent_rankings"]:
            best_agent = max(analysis["agent_rankings"].items(),
                           key=lambda x: x[1]["average_score"])
            analysis["key_findings"].append(
                f"Best performing agent: {best_agent[0]} "
                f"(avg score: {best_agent[1]['average_score']:.2f})"
            )
        
        # Generate recommendations
        if "semantic_workflow" in analysis["strategy_performance"]:
            semantic_perf = analysis["strategy_performance"]["semantic_workflow"]
            if semantic_perf["average_score"] > 0.6:
                analysis["recommendations"].append(
                    "Semantic workflow strategy shows strong performance - recommended for production"
                )
            else:
                analysis["recommendations"].append(
                    "Semantic workflow strategy needs improvement before production deployment"
                )
        
        return analysis
    
    async def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run the complete validation suite"""
        
        logger.info("🚀 Starting Comprehensive Real Agent Validation")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        # Setup phase
        logger.info("Phase 1: Setting up agents...")
        setup_results = await self.setup_agents()
        
        for agent_name, status in setup_results.items():
            logger.info(f"  {agent_name}: {status}")
        
        # Strategy comparison phase
        logger.info("\nPhase 2: Strategy comparison testing...")
        strategy_results = await self.run_strategy_comparison()
        
        # Behavior analysis phase
        logger.info("\nPhase 3: Agent behavior analysis...")
        behavior_results = await self.run_agent_behavior_analysis()
        
        # Analysis phase
        logger.info("\nPhase 4: Results analysis...")
        analysis = self.analyze_results(strategy_results, behavior_results)
        
        total_time = time.time() - start_time
        
        # Compile final results
        final_results = {
            "validation_info": {
                "timestamp": datetime.now().isoformat(),
                "total_duration_seconds": total_time,
                "agents_tested": list(setup_results.keys()),
                "strategies_tested": list(strategy_results.keys())
            },
            "agent_setup": setup_results,
            "strategy_comparison": strategy_results,
            "behavior_analysis": behavior_results,
            "analysis": analysis,
            "framework_results": [result.__dict__ for result in self.framework.test_results]
        }
        
        logger.info(f"\n✅ Validation completed in {total_time:.1f} seconds")
        
        return final_results
    
    def save_results(self, results: Dict[str, Any], filename: Optional[str] = None):
        """Save validation results to file"""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"real_agent_validation_results_{timestamp}.json"
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        # Convert any non-serializable objects
        def json_serializer(obj):
            if hasattr(obj, '__dict__'):
                return obj.__dict__
            elif hasattr(obj, 'value'):  # For Enums
                return obj.value
            return str(obj)
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=json_serializer)
        
        logger.info(f"Results saved to: {filepath}")
        return filepath


async def main():
    """Main execution function"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Check if we're in test mode (no API keys required)
    test_mode = os.getenv("VALIDATION_TEST_MODE", "false").lower() == "true"
    
    if test_mode:
        logger.info("🧪 Running in TEST MODE - using mock agents only")
        os.environ.pop("OPENAI_API_KEY", None)
        os.environ.pop("ANTHROPIC_API_KEY", None)
        os.environ.pop("GOOGLE_API_KEY", None)
    
    # Create and run validation
    runner = RealAgentValidationRunner()
    
    # Show available agents
    logger.info("Available Agents:")
    for agent_type, available in runner.available_agents.items():
        status = "✅ API Key Found" if available else "❌ No API Key"
        logger.info(f"  {agent_type.value}: {status}")
    
    if not test_mode and not any(runner.available_agents.values()):
        logger.warning("\n⚠️  No API keys found. Set environment variables:")
        logger.warning("   export OPENAI_API_KEY='your-openai-key'")
        logger.warning("   export ANTHROPIC_API_KEY='your-anthropic-key'")
        logger.warning("   export GOOGLE_API_KEY='your-google-key'")
        logger.warning("\nOr run in test mode: export VALIDATION_TEST_MODE=true")
        return
    
    try:
        # Run comprehensive validation
        results = await runner.run_comprehensive_validation()
        
        # Save results
        filepath = runner.save_results(results)
        
        # Print summary
        logger.info("\n📊 VALIDATION SUMMARY")
        logger.info("=" * 30)
        
        analysis = results.get("analysis", {})
        
        if analysis.get("strategy_performance"):
            logger.info("\n🏆 Strategy Performance:")
            for strategy, perf in analysis["strategy_performance"].items():
                logger.info(f"  {strategy}: {perf['average_score']:.2f} avg score, "
                          f"{perf['success_rate']:.1%} success rate")
        
        if analysis.get("agent_rankings"):
            logger.info("\n🤖 Agent Performance:")
            sorted_agents = sorted(analysis["agent_rankings"].items(),
                                 key=lambda x: x[1]["average_score"], reverse=True)
            for agent, perf in sorted_agents:
                logger.info(f"  {agent}: {perf['average_score']:.2f} avg score")
        
        if analysis.get("key_findings"):
            logger.info("\n🔍 Key Findings:")
            for finding in analysis["key_findings"]:
                logger.info(f"  • {finding}")
        
        if analysis.get("recommendations"):
            logger.info("\n💡 Recommendations:")
            for rec in analysis["recommendations"]:
                logger.info(f"  • {rec}")
        
        logger.info(f"\n📄 Full results saved to: {filepath}")
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())