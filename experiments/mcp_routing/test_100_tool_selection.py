#!/usr/bin/env python3
"""
CRITICAL TEST: Can Gemini-2.5-flash actually select correctly from 100+ tools?

This test directly validates our MCP organization strategy by testing:
1. Direct exposure (100+ tools) vs. Semantic workflow (5-15 tools)
2. Tool selection accuracy with large tool sets
3. Cognitive load impact on selection quality
4. Response time and success rate differences
"""

import os
import json
import asyncio
import time
import logging
from pathlib import Path
from typing import List, Dict, Any
import random

# Import our frameworks
from mock_tool_generator import MockToolGenerator
from real_agents import create_real_agent, AgentType

logger = logging.getLogger(__name__)

# Load environment variables
def load_env():
    env_path = Path("/home/brian/projects/Digimons/.env")
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env()

class ToolSelectionTest:
    """Test tool selection accuracy with different tool set sizes"""
    
    def __init__(self):
        self.tool_generator = MockToolGenerator()
        self.all_tools = self.tool_generator.generate_all_tools()
        self.results = {}
        
        # Define test scenarios
        self.test_scenarios = [
            {
                "name": "academic_paper_processing",
                "description": "Process an academic machine learning paper to extract methodologies, datasets, and performance metrics",
                "optimal_tools": [
                    "load_document_comprehensive_pdf",
                    "extract_entities_spacy_advanced", 
                    "build_knowledge_graph_academic",
                    "analyze_methodology_patterns",
                    "export_academic_summary"
                ],
                "context": {
                    "document_type": "academic_paper",
                    "domain": "machine_learning",
                    "complexity": "high",
                    "expected_outputs": ["methodologies", "datasets", "metrics", "relationships"]
                }
            },
            {
                "name": "simple_document_analysis", 
                "description": "Extract basic entities and relationships from a business document",
                "optimal_tools": [
                    "load_document_basic_text",
                    "extract_entities_spacy_basic",
                    "export_simple_json"
                ],
                "context": {
                    "document_type": "business_document", 
                    "domain": "general",
                    "complexity": "low",
                    "expected_outputs": ["people", "organizations", "locations"]
                }
            }
        ]
    
    def create_tool_sets(self) -> Dict[str, List[Dict]]:
        """Create different tool sets for testing"""
        
        # Convert tools to simple format for agents
        all_tools_simple = []
        for tool in self.all_tools:
            all_tools_simple.append({
                "name": tool.tool_id,
                "description": tool.description,
                "category": tool.category.value,
                "complexity": tool.complexity_score
            })
        
        # Create different exposure strategies
        tool_sets = {
            "direct_exposure_100": all_tools_simple,  # All 100+ tools
            "direct_exposure_50": all_tools_simple[:50],  # 50 tools
            "direct_exposure_25": all_tools_simple[:25],  # 25 tools
            "semantic_workflow": [
                {"name": "load_document_comprehensive", "description": "Load and parse documents with full metadata extraction"},
                {"name": "load_document_basic", "description": "Basic document loading without metadata"},
                {"name": "extract_knowledge_adaptive", "description": "Intelligently extract entities and relationships"},
                {"name": "analyze_graph_insights", "description": "Analyze knowledge graph for patterns and insights"},
                {"name": "export_results_comprehensive", "description": "Export results in multiple formats"},
                {"name": "query_knowledge_intelligent", "description": "Query knowledge graph with natural language"},
                {"name": "build_knowledge_graph", "description": "Build structured knowledge graph from entities"}
            ]
        }
        
        # Shuffle tools to avoid order bias
        for key in ["direct_exposure_100", "direct_exposure_50", "direct_exposure_25"]:
            random.shuffle(tool_sets[key])
        
        return tool_sets
    
    async def test_agent_with_toolset(self, agent_type: AgentType, toolset_name: str, 
                                    tools: List[Dict], scenario: Dict) -> Dict[str, Any]:
        """Test agent tool selection with specific toolset"""
        
        print(f"\n🧪 Testing {agent_type.value} with {toolset_name} ({len(tools)} tools)")
        print(f"   Scenario: {scenario['name']}")
        
        try:
            agent = create_real_agent(agent_type)
            
            start_time = time.time()
            
            # Test tool selection
            selected_tools = await agent.select_tools_for_workflow(
                scenario["description"],
                tools,
                scenario["context"]
            )
            
            selection_time = time.time() - start_time
            
            # Analyze results
            result = {
                "agent": agent_type.value,
                "toolset": toolset_name,
                "toolset_size": len(tools),
                "scenario": scenario["name"],
                "selection_time_seconds": selection_time,
                "tools_selected": len(selected_tools) if selected_tools else 0,
                "selected_tools": [tool.get("tool", tool.get("name", "unknown")) for tool in selected_tools] if selected_tools else [],
                "selection_success": selected_tools is not None and len(selected_tools) > 0,
                "optimal_tools": scenario["optimal_tools"],
                "accuracy_metrics": self._calculate_accuracy(selected_tools, scenario["optimal_tools"]) if selected_tools else {}
            }
            
            # Check for optimal tool matches
            if selected_tools:
                selected_names = [tool.get("tool", tool.get("name", "")) for tool in selected_tools]
                optimal_matches = len(set(selected_names) & set(scenario["optimal_tools"]))
                result["optimal_matches"] = optimal_matches
                result["optimal_match_rate"] = optimal_matches / len(scenario["optimal_tools"])
            else:
                result["optimal_matches"] = 0
                result["optimal_match_rate"] = 0.0
            
            print(f"   ✅ Completed in {selection_time:.1f}s")
            print(f"   🛠️  Selected {len(selected_tools) if selected_tools else 0} tools")
            if selected_tools and len(selected_tools) > 0:
                print(f"   🎯 Tools: {[tool.get('tool', tool.get('name', 'unknown'))[:30] for tool in selected_tools[:3]]}")
            
            return result
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return {
                "agent": agent_type.value,
                "toolset": toolset_name,
                "toolset_size": len(tools),
                "scenario": scenario["name"],
                "error": str(e),
                "selection_success": False
            }
    
    def _calculate_accuracy(self, selected_tools: List[Dict], optimal_tools: List[str]) -> Dict[str, float]:
        """Calculate tool selection accuracy metrics"""
        if not selected_tools:
            return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
        
        selected_names = set(tool.get("tool", tool.get("name", "")) for tool in selected_tools)
        optimal_names = set(optimal_tools)
        
        # Calculate precision, recall, F1
        true_positives = len(selected_names & optimal_names)
        precision = true_positives / len(selected_names) if selected_names else 0.0
        recall = true_positives / len(optimal_names) if optimal_names else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return {
            "precision": precision,
            "recall": recall, 
            "f1": f1,
            "true_positives": true_positives
        }
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive 100-tool selection test"""
        
        print("🚀 CRITICAL TEST: 100-Tool Selection Validation")
        print("=" * 60)
        print(f"Testing with {len(self.all_tools)} generated tools")
        print(f"Scenarios: {len(self.test_scenarios)}")
        
        # Create tool sets
        tool_sets = self.create_tool_sets()
        
        print(f"\nTool sets prepared:")
        for name, tools in tool_sets.items():
            print(f"  {name}: {len(tools)} tools")
        
        # Run tests
        all_results = []
        
        for scenario in self.test_scenarios:
            print(f"\n📋 SCENARIO: {scenario['name'].upper()}")
            print(f"   Description: {scenario['description']}")
            print(f"   Optimal tools: {len(scenario['optimal_tools'])}")
            
            for toolset_name, tools in tool_sets.items():
                # Test with Gemini-2.5-flash (primary agent)
                result = await self.test_agent_with_toolset(
                    AgentType.GEMINI_FLASH,
                    toolset_name, 
                    tools,
                    scenario
                )
                all_results.append(result)
        
        # Analyze results
        analysis = self._analyze_results(all_results)
        
        return {
            "test_info": {
                "timestamp": time.time(),
                "total_tools_generated": len(self.all_tools),
                "scenarios_tested": len(self.test_scenarios),
                "toolsets_tested": list(tool_sets.keys())
            },
            "results": all_results,
            "analysis": analysis
        }
    
    def _analyze_results(self, results: List[Dict]) -> Dict[str, Any]:
        """Analyze test results to answer key questions"""
        
        analysis = {
            "toolset_performance": {},
            "cognitive_load_impact": {},
            "key_findings": [],
            "recommendations": []
        }
        
        # Group results by toolset
        by_toolset = {}
        for result in results:
            toolset = result["toolset"]
            if toolset not in by_toolset:
                by_toolset[toolset] = []
            by_toolset[toolset].append(result)
        
        # Analyze each toolset
        for toolset_name, toolset_results in by_toolset.items():
            successful_tests = [r for r in toolset_results if r.get("selection_success", False)]
            
            if successful_tests:
                avg_time = sum(r["selection_time_seconds"] for r in successful_tests) / len(successful_tests)
                avg_tools_selected = sum(r["tools_selected"] for r in successful_tests) / len(successful_tests)
                avg_accuracy = sum(r.get("optimal_match_rate", 0) for r in successful_tests) / len(successful_tests)
                
                analysis["toolset_performance"][toolset_name] = {
                    "toolset_size": toolset_results[0]["toolset_size"],
                    "success_rate": len(successful_tests) / len(toolset_results),
                    "avg_selection_time": avg_time,
                    "avg_tools_selected": avg_tools_selected,
                    "avg_accuracy": avg_accuracy,
                    "total_tests": len(toolset_results)
                }
        
        # Cognitive load analysis
        if "direct_exposure_100" in analysis["toolset_performance"] and "semantic_workflow" in analysis["toolset_performance"]:
            large_set = analysis["toolset_performance"]["direct_exposure_100"]
            small_set = analysis["toolset_performance"]["semantic_workflow"]
            
            analysis["cognitive_load_impact"] = {
                "time_increase_factor": large_set["avg_selection_time"] / small_set["avg_selection_time"],
                "accuracy_difference": large_set["avg_accuracy"] - small_set["avg_accuracy"],
                "success_rate_difference": large_set["success_rate"] - small_set["success_rate"]
            }
        
        # Generate findings
        if analysis["toolset_performance"]:
            best_toolset = max(analysis["toolset_performance"].items(), 
                             key=lambda x: x[1]["avg_accuracy"])
            analysis["key_findings"].append(
                f"Best performing toolset: {best_toolset[0]} (accuracy: {best_toolset[1]['avg_accuracy']:.2f})"
            )
            
            fastest_toolset = min(analysis["toolset_performance"].items(),
                                key=lambda x: x[1]["avg_selection_time"])
            analysis["key_findings"].append(
                f"Fastest selection: {fastest_toolset[0]} ({fastest_toolset[1]['avg_selection_time']:.1f}s)"
            )
        
        return analysis


async def main():
    """Run the critical 100-tool selection test"""
    
    logging.basicConfig(level=logging.INFO)
    
    print("🎯 CRITICAL VALIDATION: Can AI agents handle 100+ tools effectively?")
    print("This test directly validates our MCP organization strategy hypothesis.")
    
    # Check if we have Gemini API access
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY required for this test")
        print("This test requires real Gemini-2.5-flash to validate tool selection at scale")
        return
    
    # Run the test
    tester = ToolSelectionTest()
    results = await tester.run_comprehensive_test()
    
    # Save detailed results
    timestamp = int(time.time())
    results_file = f"100_tool_selection_test_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    # Print summary
    print(f"\n📊 TEST RESULTS SUMMARY")
    print("=" * 40)
    
    analysis = results["analysis"]
    
    if analysis["toolset_performance"]:
        print("\n🏆 Toolset Performance:")
        for name, perf in analysis["toolset_performance"].items():
            print(f"  {name}:")
            print(f"    Tools: {perf['toolset_size']}")
            print(f"    Success Rate: {perf['success_rate']:.1%}")
            print(f"    Avg Time: {perf['avg_selection_time']:.1f}s")
            print(f"    Avg Accuracy: {perf['avg_accuracy']:.2f}")
    
    if analysis["cognitive_load_impact"]:
        print(f"\n🧠 Cognitive Load Impact:")
        impact = analysis["cognitive_load_impact"] 
        print(f"  Time increase (100 vs 7 tools): {impact['time_increase_factor']:.1f}x")
        print(f"  Accuracy difference: {impact['accuracy_difference']:.2f}")
        print(f"  Success rate difference: {impact['success_rate_difference']:.2f}")
    
    if analysis["key_findings"]:
        print(f"\n🔍 Key Findings:")
        for finding in analysis["key_findings"]:
            print(f"  • {finding}")
    
    print(f"\n📄 Detailed results saved to: {results_file}")
    
    # Answer the core question
    semantic_perf = analysis["toolset_performance"].get("semantic_workflow", {})
    direct_100_perf = analysis["toolset_performance"].get("direct_exposure_100", {})
    
    if semantic_perf and direct_100_perf:
        if semantic_perf["avg_accuracy"] > direct_100_perf["avg_accuracy"]:
            print(f"\n✅ VALIDATION RESULT: Semantic workflow outperforms direct 100-tool exposure")
            print(f"   Accuracy: {semantic_perf['avg_accuracy']:.2f} vs {direct_100_perf['avg_accuracy']:.2f}")
        else:
            print(f"\n⚠️ VALIDATION RESULT: Direct exposure performs better than expected")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())