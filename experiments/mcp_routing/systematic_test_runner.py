#!/usr/bin/env python3
"""
Systematic MCP Tool Selection Testing Framework

Implements comprehensive testing of:
1. Cognitive load thresholds for different models
2. Methodology effectiveness comparison 
3. Cross-model validation for production recommendations

Uses mock tools for controlled, systematic testing.
"""

import os
import json
import asyncio
import time
import statistics
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, asdict
import logging

# Import existing framework components
from mock_tool_generator import MockToolGenerator, ToolCategory
from real_agents import create_real_agent, AgentType
from run_with_env import load_env

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_env()

@dataclass
class TestScenario:
    """Standardized test scenario for consistent testing"""
    name: str
    task_description: str
    optimal_tools: List[str]
    complexity_level: str
    expected_tool_count: int
    domain: str

@dataclass 
class TestResult:
    """Individual test result structure"""
    model: str
    tool_count: int
    methodology: str
    scenario: str
    response_time_seconds: float
    selection_success: bool
    selected_tools: List[str]
    accuracy_metrics: Dict[str, float]
    token_usage: Optional[int] = None
    error: Optional[str] = None

@dataclass
class CognitiveLoadResult:
    """Cognitive load test result"""
    model: str
    tool_count: int
    response_time: float
    accuracy: float
    degradation_detected: bool
    baseline_comparison: float

@dataclass
class MethodologyResult:
    """Methodology comparison result"""
    methodology: str
    model: str
    tool_count: int
    scenario: str
    accuracy: float
    response_time: float
    user_experience_score: float

class SystematicTestRunner:
    """Orchestrates comprehensive MCP tool selection testing"""
    
    def __init__(self):
        self.tool_generator = MockToolGenerator()
        self.test_scenarios = self._create_test_scenarios()
        self.models = [
            AgentType.GEMINI_FLASH,
            AgentType.GPT_4,
            AgentType.CLAUDE_SONNET,
            AgentType.GPT_4O_MINI
        ]
        self.tool_counts = [10, 25, 50, 100, 200, 500]
        self.methodologies = [
            "direct_exposure",
            "semantic_workflow", 
            "hierarchical_categories",
            "smart_filtering",
            "adaptive_loading"
        ]
        
        # Results storage
        self.results = {
            "cognitive_load": [],
            "methodology_comparison": [],
            "cross_model_validation": [],
            "metadata": {
                "test_timestamp": time.time(),
                "framework_version": "2.0",
                "total_tests_planned": 0
            }
        }
    
    def _create_test_scenarios(self) -> List[TestScenario]:
        """Create standardized test scenarios"""
        return [
            TestScenario(
                name="simple_document_task",
                task_description="Extract key information from a simple business document",
                optimal_tools=["load_document_pdf", "extract_entities_basic", "export_simple_json"],
                complexity_level="low",
                expected_tool_count=3,
                domain="document_processing"
            ),
            TestScenario(
                name="complex_analysis_task", 
                task_description="Analyze academic research paper with methodology extraction and knowledge graph creation",
                optimal_tools=[
                    "load_document_pdf", 
                    "extract_entities_advanced", 
                    "extract_keywords",
                    "build_knowledge_graph",
                    "analyze_relationships",
                    "export_academic_summary"
                ],
                complexity_level="high",
                expected_tool_count=6,
                domain="academic_analysis"
            ),
            TestScenario(
                name="multi_domain_task",
                task_description="Process financial document with entity extraction, sentiment analysis, and visualization",
                optimal_tools=[
                    "load_document_pdf",
                    "extract_entities_financial", 
                    "analyze_sentiment",
                    "create_visualization",
                    "export_dashboard"
                ],
                complexity_level="medium",
                expected_tool_count=5,
                domain="cross_domain"
            ),
            TestScenario(
                name="academic_processing",
                task_description="Complete academic paper processing with citation analysis and research insights",
                optimal_tools=[
                    "load_document_comprehensive",
                    "extract_citations", 
                    "extract_methodology",
                    "build_knowledge_graph_academic",
                    "analyze_research_impact",
                    "generate_insights",
                    "export_research_summary"
                ],
                complexity_level="very_high", 
                expected_tool_count=7,
                domain="academic_research"
            )
        ]
    
    async def run_phase1_cognitive_load_testing(self) -> List[CognitiveLoadResult]:
        """Phase 1: Map cognitive load degradation thresholds"""
        
        logger.info("🧠 Starting Phase 1: Cognitive Load Testing")
        logger.info(f"Testing {len(self.models)} models with {len(self.tool_counts)} tool counts")
        
        cognitive_load_results = []
        baseline_times = {}
        
        # Use standard scenario for cognitive load testing
        standard_scenario = self.test_scenarios[0]  # simple_document_task
        
        for model in self.models:
            logger.info(f"Testing cognitive load for {model.value}")
            model_results = []
            
            try:
                agent = create_real_agent(model)
                
                for tool_count in self.tool_counts:
                    logger.info(f"  Testing with {tool_count} tools...")
                    
                    # Generate consistent tool set
                    tools = self.tool_generator.generate_tools(tool_count, seed=42)
                    tool_list = self._format_tools_for_agent(tools)
                    
                    # Measure performance
                    start_time = time.time()
                    try:
                        selection_result = await agent.select_tools_for_workflow(
                            self._create_tool_selection_prompt(standard_scenario),
                            tool_list,
                            {"task_complexity": standard_scenario.complexity_level}
                        )
                        response_time = time.time() - start_time
                        selection_success = True
                    except Exception as e:
                        response_time = time.time() - start_time
                        selection_success = False
                        logger.warning(f"    Selection failed for {tool_count} tools: {e}")
                        selection_result = []
                    
                    # Calculate accuracy
                    selected_tools = self._extract_tool_names(selection_result)
                    accuracy = self._calculate_accuracy(selected_tools, standard_scenario.optimal_tools)
                    
                    # Establish baseline (10 tools)
                    if tool_count == 10:
                        baseline_times[model.value] = response_time
                    
                    # Detect degradation
                    baseline_time = baseline_times.get(model.value, response_time)
                    degradation_detected = response_time > baseline_time * 1.5
                    baseline_comparison = response_time / baseline_time if baseline_time > 0 else 1.0
                    
                    result = CognitiveLoadResult(
                        model=model.value,
                        tool_count=tool_count,
                        response_time=response_time,
                        accuracy=accuracy,
                        degradation_detected=degradation_detected,
                        baseline_comparison=baseline_comparison
                    )
                    
                    cognitive_load_results.append(result)
                    model_results.append(result)
                    
                    logger.info(f"    Result: {response_time:.1f}s, accuracy: {accuracy:.2f}, degradation: {degradation_detected}")
                
                # Find degradation threshold for this model
                threshold = self._find_degradation_threshold(model_results)
                logger.info(f"  {model.value} degradation threshold: {threshold} tools")
                
            except Exception as e:
                logger.error(f"Failed to test {model.value}: {e}")
                continue
        
        self.results["cognitive_load"] = [asdict(r) for r in cognitive_load_results]
        
        logger.info(f"✅ Phase 1 Complete: {len(cognitive_load_results)} cognitive load tests")
        return cognitive_load_results
    
    async def run_phase2_methodology_comparison(self, cognitive_load_results: List[CognitiveLoadResult]) -> List[MethodologyResult]:
        """Phase 2: Compare methodology effectiveness"""
        
        logger.info("📊 Starting Phase 2: Methodology Comparison")
        
        # Determine viable tool counts from cognitive load results
        viable_tool_counts = self._get_viable_tool_counts(cognitive_load_results)
        logger.info(f"Using viable tool counts: {viable_tool_counts}")
        
        methodology_results = []
        
        for methodology in self.methodologies:
            logger.info(f"Testing methodology: {methodology}")
            
            for model in self.models:
                try:
                    agent = create_real_agent(model)
                    
                    for tool_count in viable_tool_counts:
                        for scenario in self.test_scenarios:
                            logger.info(f"  {model.value} | {tool_count} tools | {scenario.name}")
                            
                            # Generate and organize tools according to methodology
                            base_tools = self.tool_generator.generate_tools(tool_count, seed=42)
                            organized_tools = self._apply_methodology(base_tools, methodology, scenario)
                            
                            # Test methodology performance  
                            start_time = time.time()
                            try:
                                selection_result = await agent.select_tools_for_workflow(
                                    self._create_methodology_prompt(scenario, methodology),
                                    organized_tools,
                                    {"methodology": methodology, "task_complexity": scenario.complexity_level}
                                )
                                response_time = time.time() - start_time
                                
                                # Calculate metrics
                                selected_tools = self._extract_tool_names(selection_result)
                                accuracy = self._calculate_accuracy(selected_tools, scenario.optimal_tools)
                                ux_score = self._calculate_ux_score(methodology, response_time, accuracy)
                                
                                result = MethodologyResult(
                                    methodology=methodology,
                                    model=model.value,
                                    tool_count=tool_count,
                                    scenario=scenario.name,
                                    accuracy=accuracy,
                                    response_time=response_time,
                                    user_experience_score=ux_score
                                )
                                
                                methodology_results.append(result)
                                logger.info(f"    Result: {response_time:.1f}s, accuracy: {accuracy:.2f}, UX: {ux_score:.2f}")
                                
                            except Exception as e:
                                logger.warning(f"    Failed: {e}")
                                continue
                                
                except Exception as e:
                    logger.error(f"Failed to test {model.value} with {methodology}: {e}")
                    continue
        
        self.results["methodology_comparison"] = [asdict(r) for r in methodology_results]
        
        logger.info(f"✅ Phase 2 Complete: {len(methodology_results)} methodology tests")
        return methodology_results
    
    async def run_phase3_cross_model_validation(self, 
                                              cognitive_load_results: List[CognitiveLoadResult],
                                              methodology_results: List[MethodologyResult]) -> Dict[str, Any]:
        """Phase 3: Cross-model validation and production recommendations"""
        
        logger.info("🔬 Starting Phase 3: Cross-Model Validation")
        
        # Identify optimal configurations from previous phases
        optimal_configs = self._identify_optimal_configurations(cognitive_load_results, methodology_results)
        
        validation_results = []
        
        for config in optimal_configs:
            logger.info(f"Validating config: {config}")
            
            for model in self.models:
                try:
                    agent = create_real_agent(model)
                    
                    # Comprehensive validation across all scenarios
                    config_scores = []
                    
                    for scenario in self.test_scenarios:
                        # Generate tools using optimal configuration
                        tools = self.tool_generator.generate_tools(config["tool_count"], seed=42)
                        organized_tools = self._apply_methodology(tools, config["methodology"], scenario)
                        
                        # Test performance
                        start_time = time.time()
                        try:
                            selection_result = await agent.select_tools_for_workflow(
                                self._create_validation_prompt(scenario, config),
                                organized_tools,
                                {"validation_mode": True}
                            )
                            response_time = time.time() - start_time
                            
                            selected_tools = self._extract_tool_names(selection_result)
                            accuracy = self._calculate_accuracy(selected_tools, scenario.optimal_tools)
                            
                            scenario_score = self._calculate_overall_score(accuracy, response_time)
                            config_scores.append(scenario_score)
                            
                        except Exception as e:
                            logger.warning(f"Validation failed for {scenario.name}: {e}")
                            config_scores.append(0.0)
                    
                    overall_score = statistics.mean(config_scores) if config_scores else 0.0
                    production_ready = overall_score > 0.7  # 70% threshold
                    
                    validation_result = {
                        "model": model.value,
                        "configuration": config,
                        "overall_score": overall_score,
                        "scenario_scores": config_scores,
                        "production_ready": production_ready,
                        "recommended_use_case": self._determine_use_case(config, overall_score)
                    }
                    
                    validation_results.append(validation_result)
                    logger.info(f"  {model.value}: score {overall_score:.2f}, ready: {production_ready}")
                    
                except Exception as e:
                    logger.error(f"Validation failed for {model.value}: {e}")
                    continue
        
        # Generate production recommendations
        production_recommendations = self._generate_production_recommendations(validation_results)
        
        self.results["cross_model_validation"] = validation_results
        self.results["production_recommendations"] = production_recommendations
        
        logger.info("✅ Phase 3 Complete: Cross-model validation finished")
        return {"validation_results": validation_results, "recommendations": production_recommendations}
    
    def _format_tools_for_agent(self, tools: List[Any]) -> List[Dict[str, Any]]:
        """Format mock tools for agent consumption"""
        formatted_tools = []
        for tool in tools:
            formatted_tools.append({
                "name": tool.tool_id,
                "description": tool.description,
                "category": tool.category.value,
                "inputs": tool.input_types,
                "outputs": tool.output_types,
                "complexity": tool.complexity_score
            })
        return formatted_tools
    
    def _create_tool_selection_prompt(self, scenario: TestScenario) -> str:
        """Create standardized tool selection prompt"""
        return f"""
You are selecting tools for this task: {scenario.task_description}

Domain: {scenario.domain}
Complexity: {scenario.complexity_level}
Expected tools needed: ~{scenario.expected_tool_count}

Select the most appropriate tools and return as JSON:
{{
    "selected_tools": [
        {{"tool": "tool_name", "reasoning": "why this tool"}}
    ],
    "overall_strategy": "your approach"
}}
        """.strip()
    
    def _create_methodology_prompt(self, scenario: TestScenario, methodology: str) -> str:
        """Create methodology-specific prompt"""
        methodology_instructions = {
            "direct_exposure": "All tools are presented equally. Choose the best ones directly.",
            "semantic_workflow": "Tools are organized by workflow stage. Choose tools that form a logical workflow.",
            "hierarchical_categories": "Tools are organized by category. Choose from appropriate categories first.",
            "smart_filtering": "Only relevant tools for this task context are shown.",
            "adaptive_loading": "Tools are presented based on task complexity and requirements."
        }
        
        instruction = methodology_instructions.get(methodology, "Select appropriate tools.")
        
        return f"""
{instruction}

Task: {scenario.task_description}
Domain: {scenario.domain}
Complexity: {scenario.complexity_level}

Return JSON with selected tools and reasoning.
        """.strip()
    
    def _create_validation_prompt(self, scenario: TestScenario, config: Dict[str, Any]) -> str:
        """Create validation-specific prompt"""
        return f"""
VALIDATION MODE: Select tools using the optimal strategy identified in testing.

Task: {scenario.task_description}
Methodology: {config["methodology"]}
Tool Count: {config["tool_count"]}

This is a validation run - select tools as efficiently and accurately as possible.
Return JSON with selected tools.
        """.strip()
    
    def _extract_tool_names(self, selection_result: Any) -> List[str]:
        """Extract tool names from agent selection result"""
        tool_names = []
        
        if isinstance(selection_result, list):
            for item in selection_result:
                if isinstance(item, dict):
                    # Try different possible keys
                    for key in ["tool", "name", "tool_name"]:
                        if key in item:
                            tool_names.append(item[key])
                            break
                elif isinstance(item, str):
                    tool_names.append(item)
        
        return tool_names
    
    def _calculate_accuracy(self, selected_tools: List[str], optimal_tools: List[str]) -> float:
        """Calculate selection accuracy using precision/recall"""
        if not selected_tools or not optimal_tools:
            return 0.0
        
        selected_set = set(selected_tools)
        optimal_set = set(optimal_tools)
        
        true_positives = len(selected_set & optimal_set)
        precision = true_positives / len(selected_set) if selected_set else 0.0
        recall = true_positives / len(optimal_set) if optimal_set else 0.0
        
        # F1 score as primary accuracy metric
        if precision + recall == 0:
            return 0.0
        
        f1_score = 2 * (precision * recall) / (precision + recall)
        return f1_score
    
    def _calculate_ux_score(self, methodology: str, response_time: float, accuracy: float) -> float:
        """Calculate user experience score combining speed and accuracy"""
        # Normalize response time (assume 10s is baseline, 1s is excellent)
        time_score = max(0, 1 - (response_time - 1) / 9)  # 1-10s range normalized
        
        # Weight accuracy higher than speed for UX
        ux_score = (accuracy * 0.7) + (time_score * 0.3)
        return min(1.0, max(0.0, ux_score))
    
    def _calculate_overall_score(self, accuracy: float, response_time: float) -> float:
        """Calculate overall performance score"""
        # Penalize very slow responses
        time_penalty = max(0, (response_time - 5) / 10)  # Penalty starts at 5s
        time_score = max(0, 1 - time_penalty)
        
        # Combine accuracy and speed
        overall_score = (accuracy * 0.8) + (time_score * 0.2)
        return min(1.0, max(0.0, overall_score))
    
    def _find_degradation_threshold(self, model_results: List[CognitiveLoadResult]) -> int:
        """Find tool count where performance degrades significantly"""
        for result in model_results:
            if result.degradation_detected:
                return result.tool_count
        
        # If no degradation detected, return highest tested count
        return max(r.tool_count for r in model_results) if model_results else 500
    
    def _get_viable_tool_counts(self, cognitive_load_results: List[CognitiveLoadResult]) -> List[int]:
        """Get tool counts that don't cause significant degradation"""
        viable_counts = set()
        
        for result in cognitive_load_results:
            if not result.degradation_detected and result.accuracy > 0.3:
                viable_counts.add(result.tool_count)
        
        # Ensure we have some counts to test
        if not viable_counts:
            viable_counts = {10, 25, 50}
        
        return sorted(list(viable_counts))
    
    def _apply_methodology(self, tools: List[Any], methodology: str, scenario: TestScenario) -> List[Dict[str, Any]]:
        """Apply methodology-specific tool organization"""
        base_tools = self._format_tools_for_agent(tools)
        
        if methodology == "semantic_workflow":
            # Return subset of workflow-oriented tools
            workflow_tools = [t for t in base_tools if any(keyword in t["name"].lower() 
                            for keyword in ["load", "extract", "build", "analyze", "export"])]
            return workflow_tools[:15]  # Limit to 15 tools
        
        elif methodology == "hierarchical_categories":
            # Group by category and present hierarchically
            categorized = {}
            for tool in base_tools:
                category = tool.get("category", "general")
                if category not in categorized:
                    categorized[category] = []
                categorized[category].append(tool)
            
            # Flatten with category information
            hierarchical_tools = []
            for category, category_tools in categorized.items():
                for tool in category_tools:
                    tool["category_group"] = category
                    hierarchical_tools.append(tool)
            
            return hierarchical_tools
        
        elif methodology == "smart_filtering":
            # Filter based on scenario domain and complexity
            relevant_keywords = {
                "document_processing": ["document", "pdf", "text", "extract"],
                "academic_analysis": ["academic", "research", "citation", "methodology"],
                "cross_domain": ["financial", "sentiment", "visualization"],
                "academic_research": ["research", "citation", "impact", "analysis"]
            }
            
            domain_keywords = relevant_keywords.get(scenario.domain, [])
            filtered_tools = [t for t in base_tools if any(keyword in t["description"].lower() 
                            for keyword in domain_keywords)]
            
            return filtered_tools if filtered_tools else base_tools[:25]
        
        elif methodology == "adaptive_loading":
            # Adapt tool count based on task complexity
            complexity_limits = {
                "low": 15,
                "medium": 30, 
                "high": 50,
                "very_high": 75
            }
            
            limit = complexity_limits.get(scenario.complexity_level, 25)
            return base_tools[:limit]
        
        else:  # direct_exposure
            return base_tools
    
    def _identify_optimal_configurations(self, 
                                       cognitive_load_results: List[CognitiveLoadResult],
                                       methodology_results: List[MethodologyResult]) -> List[Dict[str, Any]]:
        """Identify optimal configurations from test results"""
        
        # Find best performing combinations
        optimal_configs = []
        
        # Group methodology results by configuration
        config_groups = {}
        for result in methodology_results:
            config_key = f"{result.methodology}_{result.tool_count}"
            if config_key not in config_groups:
                config_groups[config_key] = []
            config_groups[config_key].append(result)
        
        # Find top performing configurations
        for config_key, results in config_groups.items():
            if not results:
                continue
                
            avg_accuracy = statistics.mean(r.accuracy for r in results)
            avg_response_time = statistics.mean(r.response_time for r in results)
            avg_ux_score = statistics.mean(r.user_experience_score for r in results)
            
            if avg_accuracy > 0.6 and avg_ux_score > 0.6:  # Reasonable thresholds
                methodology, tool_count = config_key.split("_")
                optimal_configs.append({
                    "methodology": methodology,
                    "tool_count": int(tool_count),
                    "avg_accuracy": avg_accuracy,
                    "avg_response_time": avg_response_time,
                    "avg_ux_score": avg_ux_score
                })
        
        # Sort by UX score and return top configs
        optimal_configs.sort(key=lambda x: x["avg_ux_score"], reverse=True)
        return optimal_configs[:5]  # Top 5 configurations
    
    def _determine_use_case(self, config: Dict[str, Any], overall_score: float) -> str:
        """Determine recommended use case for configuration"""
        if overall_score > 0.8:
            return "production_recommended"
        elif overall_score > 0.6:
            return "production_viable_with_monitoring"
        elif overall_score > 0.4:
            return "development_testing_only"
        else:
            return "not_recommended"
    
    def _generate_production_recommendations(self, validation_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate final production recommendations"""
        
        # Find best overall configuration
        production_ready = [r for r in validation_results if r["production_ready"]]
        production_ready.sort(key=lambda x: x["overall_score"], reverse=True)
        
        recommendations = {
            "primary_recommendation": None,
            "alternative_options": [],
            "model_specific_guidance": {},
            "deployment_strategy": "",
            "risk_assessment": {},
            "scaling_roadmap": {}
        }
        
        if production_ready:
            best = production_ready[0]
            recommendations["primary_recommendation"] = {
                "model": best["model"],
                "configuration": best["configuration"], 
                "confidence_score": best["overall_score"],
                "reasoning": f"Best overall performance with {best['overall_score']:.1%} success rate"
            }
            
            recommendations["alternative_options"] = production_ready[1:3]  # Top alternatives
        
        # Model-specific guidance
        model_performance = {}
        for result in validation_results:
            model = result["model"]
            if model not in model_performance:
                model_performance[model] = []
            model_performance[model].append(result["overall_score"])
        
        for model, scores in model_performance.items():
            avg_score = statistics.mean(scores)
            recommendations["model_specific_guidance"][model] = {
                "average_performance": avg_score,
                "recommendation": "recommended" if avg_score > 0.7 else "viable" if avg_score > 0.5 else "not_recommended"
            }
        
        # KGAS-specific scaling recommendations
        if recommendations["primary_recommendation"]:
            primary_tool_count = recommendations["primary_recommendation"]["configuration"]["tool_count"]
            
            if primary_tool_count >= 100:
                recommendations["scaling_roadmap"]["kgas_121_tools"] = "viable_with_primary_config"
            elif primary_tool_count >= 50:
                recommendations["scaling_roadmap"]["kgas_121_tools"] = "viable_with_methodology_optimization"
            else:
                recommendations["scaling_roadmap"]["kgas_121_tools"] = "requires_advanced_methodology"
        
        return recommendations
    
    async def run_comprehensive_test_suite(self) -> Dict[str, Any]:
        """Run complete systematic testing suite"""
        
        logger.info("🚀 Starting Comprehensive MCP Tool Selection Testing")
        logger.info(f"Models: {[m.value for m in self.models]}")
        logger.info(f"Tool counts: {self.tool_counts}")
        logger.info(f"Methodologies: {self.methodologies}")
        logger.info(f"Scenarios: {[s.name for s in self.test_scenarios]}")
        
        start_time = time.time()
        
        try:
            # Phase 1: Cognitive Load Testing
            cognitive_load_results = await self.run_phase1_cognitive_load_testing()
            
            # Phase 2: Methodology Comparison 
            methodology_results = await self.run_phase2_methodology_comparison(cognitive_load_results)
            
            # Phase 3: Cross-Model Validation
            validation_results = await self.run_phase3_cross_model_validation(
                cognitive_load_results, methodology_results
            )
            
            total_time = time.time() - start_time
            
            # Compile final results
            final_results = {
                "test_summary": {
                    "total_duration_seconds": total_time,
                    "total_tests_completed": len(cognitive_load_results) + len(methodology_results) + len(validation_results["validation_results"]),
                    "success_rate": self._calculate_success_rate(),
                    "completion_timestamp": time.time()
                },
                "cognitive_load_analysis": cognitive_load_results,
                "methodology_comparison": methodology_results,
                "cross_model_validation": validation_results["validation_results"],
                "production_recommendations": validation_results["recommendations"],
                "raw_results": self.results
            }
            
            logger.info(f"🎉 Testing Complete! Duration: {total_time/60:.1f} minutes")
            logger.info(f"Total tests: {final_results['test_summary']['total_tests_completed']}")
            
            return final_results
            
        except Exception as e:
            logger.error(f"❌ Testing failed: {e}")
            raise
    
    def _calculate_success_rate(self) -> float:
        """Calculate overall test success rate"""
        total_tests = 0
        successful_tests = 0
        
        for result in self.results["cognitive_load"]:
            total_tests += 1
            if not result.get("error"):
                successful_tests += 1
        
        for result in self.results["methodology_comparison"]:
            total_tests += 1 
            if result.get("accuracy", 0) > 0:
                successful_tests += 1
        
        return successful_tests / total_tests if total_tests > 0 else 0.0
    
    def save_results(self, results: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Save results to JSON file"""
        if not filename:
            timestamp = int(time.time())
            filename = f"systematic_test_results_{timestamp}.json"
        
        filepath = Path(__file__).parent / filename
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"💾 Results saved to: {filepath}")
        return str(filepath)


async def main():
    """Run systematic testing"""
    
    # Verify API access
    required_keys = ["GOOGLE_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    
    if missing_keys:
        logger.error(f"Missing API keys: {missing_keys}")
        logger.info("Please ensure all API keys are set in .env file")
        return
    
    # Initialize and run tests
    test_runner = SystematicTestRunner()
    
    try:
        results = await test_runner.run_comprehensive_test_suite()
        
        # Save results
        results_file = test_runner.save_results(results)
        
        # Print summary
        print("\n" + "="*60)
        print("🎯 SYSTEMATIC TESTING COMPLETE")
        print("="*60)
        
        summary = results["test_summary"]
        print(f"Duration: {summary['total_duration_seconds']/60:.1f} minutes")
        print(f"Total tests: {summary['total_tests_completed']}")
        print(f"Success rate: {summary['success_rate']:.1%}")
        
        recommendations = results["production_recommendations"]
        if recommendations.get("primary_recommendation"):
            primary = recommendations["primary_recommendation"]
            print(f"\n🏆 PRIMARY RECOMMENDATION:")
            print(f"Model: {primary['model']}")
            print(f"Methodology: {primary['configuration']['methodology']}")
            print(f"Tool count: {primary['configuration']['tool_count']}")
            print(f"Confidence: {primary['confidence_score']:.1%}")
        
        print(f"\n📄 Full results: {results_file}")
        print("="*60)
        
    except Exception as e:
        logger.error(f"Testing failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())