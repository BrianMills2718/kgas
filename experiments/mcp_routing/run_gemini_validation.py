#!/usr/bin/env python3
"""
Gemini-Focused Agent Validation

Runs validation testing with Gemini-2.5-flash as the primary agent,
with fallbacks to available agents and mock agents as needed.
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
    MockAIAgent
)
from real_agents import create_real_agent
from run_real_agent_validation import RealAgentValidationRunner

logger = logging.getLogger(__name__)

class GeminiValidationRunner(RealAgentValidationRunner):
    """Specialized validation runner focusing on Gemini-2.5-flash"""
    
    def __init__(self):
        super().__init__()
        # Prioritize Gemini and available agents
        self.priority_agents = [
            AgentType.GEMINI_FLASH,    # Primary target
            AgentType.GPT_4,           # Backup if available
            AgentType.GPT_4O_MINI,     # Cost-effective backup  
            AgentType.CLAUDE_SONNET,   # If available
            AgentType.CLAUDE_HAIKU     # Fast backup
        ]
    
    async def setup_priority_agents(self) -> Dict[str, str]:
        """Setup agents in priority order, using real agents where possible"""
        setup_results = {}
        
        for agent_type in self.priority_agents:
            available = self.available_agents.get(agent_type, False)
            
            if available:
                try:
                    # Try to create real agent
                    real_agent = create_real_agent(agent_type)
                    self.framework.register_agent(real_agent)
                    setup_results[agent_type.value] = "✅ Real Agent"
                    logger.info(f"Successfully registered real agent: {agent_type.value}")
                    
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
    
    async def run_focused_gemini_test(self) -> Dict[str, Any]:
        """Run focused testing with Gemini as primary agent"""
        
        logger.info("🔍 Running Focused Gemini Validation Test")
        logger.info("=" * 50)
        
        # Test just semantic workflow strategy (our recommendation)
        strategy_name = "semantic_workflow"
        workflows = ["academic_paper_analysis", "simple_entity_extraction"]
        
        # Generate tools for semantic workflow
        strategy_tools = self.generate_strategy_tools(strategy_name)
        logger.info(f"Generated {len(strategy_tools)} tools for {strategy_name} strategy")
        
        # Test primary agents only
        test_agents = [AgentType.GEMINI_FLASH, AgentType.GPT_4, AgentType.GPT_4O_MINI]
        available_test_agents = [agent for agent in test_agents if agent in self.framework.agents]
        
        results = {}
        
        for workflow_id in workflows:
            workflow_results = {}
            
            for agent_type in available_test_agents:
                try:
                    logger.info(f"Testing {agent_type.value} on {workflow_id}")
                    
                    result = await self.framework.test_agent_workflow(
                        agent_type,
                        workflow_id,
                        strategy_tools
                    )
                    
                    workflow_results[agent_type.value] = {
                        "success": result.success,
                        "overall_score": result.overall_score,
                        "tool_selection_accuracy": result.tool_selection_accuracy,
                        "parameter_accuracy": result.parameter_accuracy,
                        "execution_time_ms": result.execution_time_ms,
                        "tools_used": result.tools_used,
                        "parameters_used": result.parameters_used,
                        "agent_reasoning": result.agent_reasoning,
                        "errors": result.errors
                    }
                    
                    logger.info(f"✅ {agent_type.value}: Score {result.overall_score:.2f}, "
                              f"Success: {result.success}")
                    
                except Exception as e:
                    logger.error(f"❌ Failed testing {agent_type.value} on {workflow_id}: {e}")
                    workflow_results[agent_type.value] = {
                        "error": str(e),
                        "success": False
                    }
            
            results[workflow_id] = workflow_results
        
        return results
    
    def analyze_gemini_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze results with focus on Gemini performance"""
        
        analysis = {
            "gemini_performance": {},
            "comparative_analysis": {},
            "strategy_validation": {},
            "recommendations": []
        }
        
        # Extract Gemini results
        gemini_scores = []
        gemini_details = {}
        
        for workflow_id, workflow_data in results.items():
            if "gemini-2.5-flash" in workflow_data:
                gemini_result = workflow_data["gemini-2.5-flash"]
                if not isinstance(gemini_result, dict) or "error" in gemini_result:
                    continue
                    
                gemini_scores.append(gemini_result.get("overall_score", 0.0))
                gemini_details[workflow_id] = {
                    "score": gemini_result.get("overall_score", 0.0),
                    "tool_accuracy": gemini_result.get("tool_selection_accuracy", 0.0),
                    "param_accuracy": gemini_result.get("parameter_accuracy", 0.0),
                    "tools_selected": gemini_result.get("tools_used", []),
                    "success": gemini_result.get("success", False)
                }
        
        if gemini_scores:
            analysis["gemini_performance"] = {
                "average_score": sum(gemini_scores) / len(gemini_scores),
                "best_score": max(gemini_scores),
                "worst_score": min(gemini_scores),
                "consistency": max(gemini_scores) - min(gemini_scores),
                "workflow_details": gemini_details,
                "total_tests": len(gemini_scores)
            }
        
        # Compare with other agents
        other_agents = {}
        for workflow_id, workflow_data in results.items():
            for agent_name, agent_result in workflow_data.items():
                if agent_name != "gemini-2.5-flash" and isinstance(agent_result, dict) and "error" not in agent_result:
                    if agent_name not in other_agents:
                        other_agents[agent_name] = []
                    other_agents[agent_name].append(agent_result.get("overall_score", 0.0))
        
        # Calculate comparative performance
        for agent_name, scores in other_agents.items():
            if scores:
                analysis["comparative_analysis"][agent_name] = {
                    "average_score": sum(scores) / len(scores),
                    "vs_gemini": (sum(scores) / len(scores)) - (sum(gemini_scores) / len(gemini_scores)) if gemini_scores else 0.0
                }
        
        # Strategy validation
        if gemini_scores:
            avg_score = sum(gemini_scores) / len(gemini_scores)
            analysis["strategy_validation"] = {
                "semantic_workflow_effectiveness": avg_score,
                "passes_threshold": avg_score > 0.5,  # 50% threshold for production readiness
                "tool_selection_quality": "good" if avg_score > 0.6 else "needs_improvement"
            }
        
        # Generate recommendations
        if analysis.get("gemini_performance", {}).get("average_score", 0) > 0.6:
            analysis["recommendations"].append(
                "✅ Gemini-2.5-flash shows strong performance with semantic workflow strategy"
            )
            analysis["recommendations"].append(
                "✅ Semantic workflow approach is validated for production use"
            )
        else:
            analysis["recommendations"].append(
                "⚠️ Gemini performance suggests semantic workflow needs refinement"
            )
        
        if analysis.get("strategy_validation", {}).get("passes_threshold", False):
            analysis["recommendations"].append(
                "✅ Ready to update ADR-031 from TENTATIVE to ACCEPTED"
            )
        else:
            analysis["recommendations"].append(
                "⚠️ Additional refinement needed before production deployment"
            )
        
        return analysis


async def main():
    """Main execution focusing on Gemini validation"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Check API key availability
    api_status = {}
    api_keys = {
        "GOOGLE_API_KEY": "Gemini-2.5-flash",
        "OPENAI_API_KEY": "GPT-4/GPT-4o-mini", 
        "ANTHROPIC_API_KEY": "Claude Sonnet/Haiku"
    }
    
    logger.info("🔑 API Key Status:")
    for key_name, models in api_keys.items():
        if os.getenv(key_name):
            logger.info(f"  ✅ {key_name}: {models}")
            api_status[key_name] = True
        else:
            logger.info(f"  ❌ {key_name}: {models} (will use mock)")
            api_status[key_name] = False
    
    if not api_status.get("GOOGLE_API_KEY", False):
        logger.warning("\n⚠️  GOOGLE_API_KEY not set. Gemini will use mock agent.")
        logger.warning("For real Gemini testing, set: export GOOGLE_API_KEY='your-google-api-key'")
    
    # Create and run focused validation
    runner = GeminiValidationRunner()
    
    try:
        start_time = time.time()
        
        # Setup agents with priority order
        logger.info("\n🤖 Setting up agents...")
        setup_results = await runner.setup_priority_agents()
        
        for agent_name, status in setup_results.items():
            logger.info(f"  {agent_name}: {status}")
        
        # Run focused Gemini test
        logger.info("\n🧪 Running focused validation test...")
        results = await runner.run_focused_gemini_test()
        
        # Analyze results
        logger.info("\n📊 Analyzing results...")
        analysis = runner.analyze_gemini_results(results)
        
        total_time = time.time() - start_time
        
        # Compile final results
        final_results = {
            "validation_info": {
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": total_time,
                "focus": "gemini-2.5-flash",
                "strategy_tested": "semantic_workflow"
            },
            "agent_setup": setup_results,
            "test_results": results,
            "analysis": analysis
        }
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"gemini_validation_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(final_results, f, indent=2, default=str)
        
        # Print summary
        logger.info(f"\n✅ Validation completed in {total_time:.1f} seconds")
        logger.info(f"📄 Results saved to: {filename}")
        
        logger.info("\n🎯 GEMINI VALIDATION SUMMARY")
        logger.info("=" * 40)
        
        gemini_perf = analysis.get("gemini_performance", {})
        if gemini_perf:
            logger.info(f"🤖 Gemini Average Score: {gemini_perf['average_score']:.2f}")
            logger.info(f"📈 Best Performance: {gemini_perf['best_score']:.2f}")
            logger.info(f"📉 Worst Performance: {gemini_perf['worst_score']:.2f}")
            logger.info(f"🎯 Consistency: {gemini_perf['consistency']:.2f} (lower is better)")
        
        if analysis.get("recommendations"):
            logger.info("\n💡 Key Recommendations:")
            for rec in analysis["recommendations"]:
                logger.info(f"  {rec}")
        
        # Strategy validation status
        strategy_val = analysis.get("strategy_validation", {})
        if strategy_val.get("passes_threshold", False):
            logger.info("\n✅ VALIDATION RESULT: Semantic workflow strategy VALIDATED for production")
            logger.info("📋 Next step: Update ADR-031 from TENTATIVE to ACCEPTED")
        else:
            logger.info("\n⚠️ VALIDATION RESULT: Strategy needs improvement before production")
        
        return final_results
        
    except Exception as e:
        logger.error(f"❌ Validation failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())