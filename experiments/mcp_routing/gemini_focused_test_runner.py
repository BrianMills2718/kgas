#!/usr/bin/env python3
"""
Gemini-Focused MCP Tool Selection Testing Framework

Uses universal_llm_kit with structured output for reliable JSON parsing.
Focuses exclusively on Gemini-2.5-flash for KGAS MCP strategy decisions.
"""

import os
import json
import asyncio
import time
import statistics
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from pydantic import BaseModel, Field
import logging

# Import universal LLM kit for structured output
import sys
sys.path.append('/home/brian/projects/Digimons/universal_llm_kit')
from universal_llm import UniversalLLM

# Import existing framework components
from mock_tool_generator import MockToolGenerator
from run_with_env import load_env

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_env()

# Pydantic models for structured output
class ToolSelection(BaseModel):
    tool: str = Field(description="The exact tool name selected")
    reasoning: str = Field(description="Why this tool was selected")
    confidence: float = Field(description="Confidence in this selection (0-1)", ge=0, le=1)

class ToolSelectionResponse(BaseModel):
    selected_tools: List[ToolSelection] = Field(description="List of selected tools with reasoning")
    overall_strategy: str = Field(description="High-level approach to the task")
    selection_confidence: float = Field(description="Overall confidence in selection (0-1)", ge=0, le=1)
    alternatives_considered: List[str] = Field(description="Other tools considered but not selected")

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
class GeminiTestResult:
    """Gemini test result structure"""
    tool_count: int
    methodology: str
    scenario: str
    response_time_seconds: float
    selection_success: bool
    selected_tools: List[str]
    selection_reasoning: List[str]
    accuracy_metrics: Dict[str, float]
    confidence_score: float
    error: Optional[str] = None

class GeminiFocusedTestRunner:
    """Gemini-focused MCP tool selection testing with structured output"""
    
    def __init__(self):
        self.tool_generator = MockToolGenerator()
        self.test_scenarios = self._create_test_scenarios()
        self.llm = UniversalLLM()
        
        # Focus on key tool counts for KGAS decision
        self.tool_counts = [10, 25, 50, 100, 200, 500]
        self.methodologies = [
            "direct_exposure",
            "semantic_workflow", 
            "hierarchical_categories",
            "smart_filtering"
        ]
        
        # Results storage
        self.results = {
            "cognitive_load_tests": [],
            "methodology_comparison": [],
            "metadata": {
                "test_timestamp": time.time(),
                "model": "gemini-2.5-flash",
                "framework_version": "3.0_structured_output"
            }
        }
    
    def _create_test_scenarios(self) -> List[TestScenario]:
        """Create test scenarios focused on KGAS use cases"""
        return [
            TestScenario(
                name="simple_document_processing",
                task_description="Process a PDF document to extract basic entities and export results",
                optimal_tools=["load_document_pdf", "extract_entities_basic", "export_simple_json"],
                complexity_level="low",
                expected_tool_count=3,
                domain="document_processing"
            ),
            TestScenario(
                name="academic_analysis_complex",
                task_description="Analyze academic research paper: extract methodologies, datasets, performance metrics, create knowledge graph with relationships",
                optimal_tools=[
                    "load_document_pdf", 
                    "extract_keywords",  # Better than generic NER for technical terms
                    "analyze_relationship_strength",  # Direct relationship analysis
                    "build_knowledge_graph",
                    "export_academic_summary"
                ],
                complexity_level="high", 
                expected_tool_count=5,
                domain="academic_research"
            ),
            TestScenario(
                name="multi_domain_processing",
                task_description="Process financial document with entity extraction, sentiment analysis, and create visualization dashboard",
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
            )
        ]
    
    async def test_gemini_with_structured_output(self, 
                                               tools: List[Dict[str, Any]], 
                                               scenario: TestScenario,
                                               methodology: str = "direct_exposure") -> GeminiTestResult:
        """Test Gemini with structured output for reliable JSON parsing"""
        
        # Create methodology-specific prompt
        prompt = self._create_structured_prompt(scenario, methodology)
        
        # Format tools for context
        tools_context = self._format_tools_context(tools, methodology, scenario)
        
        start_time = time.time()
        
        try:
            # Use structured output with universal LLM
            response_text = self.llm.structured_output(
                prompt=f"{prompt}\n\nAvailable tools:\n{json.dumps(tools_context, indent=2)}",
                schema=ToolSelectionResponse
            )
            
            # Parse the JSON response
            response = ToolSelectionResponse.model_validate_json(response_text)
            
            response_time = time.time() - start_time
            
            # Extract results from structured response
            selected_tools = [selection.tool for selection in response.selected_tools]
            selection_reasoning = [selection.reasoning for selection in response.selected_tools]
            confidence_score = response.selection_confidence
            
            # Calculate accuracy
            accuracy_metrics = self._calculate_accuracy_metrics(selected_tools, scenario.optimal_tools)
            
            return GeminiTestResult(
                tool_count=len(tools),
                methodology=methodology,
                scenario=scenario.name,
                response_time_seconds=response_time,
                selection_success=True,
                selected_tools=selected_tools,
                selection_reasoning=selection_reasoning,
                accuracy_metrics=accuracy_metrics,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Structured output test failed: {e}")
            
            return GeminiTestResult(
                tool_count=len(tools),
                methodology=methodology,
                scenario=scenario.name,
                response_time_seconds=response_time,
                selection_success=False,
                selected_tools=[],
                selection_reasoning=[],
                accuracy_metrics={"precision": 0.0, "recall": 0.0, "f1": 0.0},
                confidence_score=0.0,
                error=str(e)
            )
    
    def _create_structured_prompt(self, scenario: TestScenario, methodology: str) -> str:
        """Create prompt optimized for structured output"""
        
        methodology_instructions = {
            "direct_exposure": "All tools are presented equally. Select the most appropriate tools directly.",
            "semantic_workflow": "Tools are organized by workflow stage. Select tools that form a logical processing pipeline.",
            "hierarchical_categories": "Tools are organized by category. Choose from appropriate categories first, then specific tools.",
            "smart_filtering": "Only tools relevant to this specific task domain are shown."
        }
        
        instruction = methodology_instructions.get(methodology, "Select the most appropriate tools.")
        
        return f"""
You are an expert at selecting the optimal tools for knowledge graph analysis tasks.

TASK: {scenario.task_description}

DOMAIN: {scenario.domain}
COMPLEXITY: {scenario.complexity_level}
EXPECTED TOOLS NEEDED: ~{scenario.expected_tool_count}

METHODOLOGY: {instruction}

Your goal is to select the minimum viable set of tools that can complete this task effectively.

For each tool you select, provide:
1. The exact tool name (must match available tools exactly)
2. Clear reasoning for why this tool is essential
3. Your confidence level in this selection

Also provide:
- Overall strategy for approaching this task
- Alternative tools you considered but didn't select
- Your overall confidence in the complete selection

Focus on tools that actually exist and can work together to complete the task.
        """.strip()
    
    def _format_tools_context(self, tools: List[Dict[str, Any]], 
                            methodology: str, scenario: TestScenario) -> List[Dict[str, Any]]:
        """Format tools according to methodology"""
        
        if methodology == "semantic_workflow":
            # Group by workflow stage
            workflow_order = ["load", "extract", "process", "analyze", "build", "export"]
            organized_tools = []
            
            for stage in workflow_order:
                stage_tools = [t for t in tools if stage in t["name"].lower()]
                for tool in stage_tools[:5]:  # Limit per stage
                    tool["workflow_stage"] = stage
                    organized_tools.append(tool)
            
            return organized_tools[:20]  # Semantic workflow limit
        
        elif methodology == "hierarchical_categories":
            # Group by category
            categorized = {}
            for tool in tools:
                category = tool.get("category", "general")
                if category not in categorized:
                    categorized[category] = []
                categorized[category].append(tool)
            
            # Present with category structure
            hierarchical_tools = []
            for category, category_tools in categorized.items():
                for tool in category_tools[:8]:  # Limit per category
                    tool["category_group"] = category
                    hierarchical_tools.append(tool)
            
            return hierarchical_tools
        
        elif methodology == "smart_filtering":
            # Filter by domain relevance
            domain_keywords = {
                "document_processing": ["document", "pdf", "text", "extract", "load"],
                "academic_research": ["academic", "research", "citation", "methodology", "knowledge"],
                "cross_domain": ["financial", "sentiment", "visualization", "dashboard"]
            }
            
            keywords = domain_keywords.get(scenario.domain, [])
            filtered_tools = []
            
            for tool in tools:
                tool_text = f"{tool['name']} {tool['description']}".lower()
                if any(keyword in tool_text for keyword in keywords):
                    filtered_tools.append(tool)
            
            return filtered_tools[:30] if filtered_tools else tools[:30]
        
        else:  # direct_exposure
            return tools
    
    def _calculate_accuracy_metrics(self, selected_tools: List[str], optimal_tools: List[str]) -> Dict[str, float]:
        """Calculate precision, recall, F1 for tool selection accuracy"""
        
        if not selected_tools or not optimal_tools:
            return {"precision": 0.0, "recall": 0.0, "f1": 0.0, "exact_match": 0.0}
        
        selected_set = set(selected_tools)
        optimal_set = set(optimal_tools)
        
        true_positives = len(selected_set & optimal_set)
        precision = true_positives / len(selected_set) if selected_set else 0.0
        recall = true_positives / len(optimal_set) if optimal_set else 0.0
        
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        exact_match = 1.0 if selected_set == optimal_set else 0.0
        
        return {
            "precision": precision,
            "recall": recall, 
            "f1": f1,
            "exact_match": exact_match,
            "true_positives": true_positives,
            "selected_count": len(selected_tools),
            "optimal_count": len(optimal_tools)
        }
    
    async def run_cognitive_load_analysis(self) -> List[GeminiTestResult]:
        """Run cognitive load analysis across tool counts"""
        
        logger.info("🧠 Starting Gemini Cognitive Load Analysis")
        logger.info(f"Testing tool counts: {self.tool_counts}")
        
        cognitive_load_results = []
        
        # Use consistent scenario for cognitive load testing
        test_scenario = self.test_scenarios[1]  # academic_analysis_complex
        
        for tool_count in self.tool_counts:
            logger.info(f"Testing Gemini with {tool_count} tools...")
            
            # Generate consistent tool set
            tools = self.tool_generator.generate_tools(tool_count, seed=42)
            formatted_tools = self._format_tools_for_llm(tools)
            
            # Test with direct exposure methodology
            result = await self.test_gemini_with_structured_output(
                formatted_tools, test_scenario, "direct_exposure"
            )
            
            cognitive_load_results.append(result)
            
            if result.selection_success:
                logger.info(f"  ✅ {tool_count} tools: {result.response_time_seconds:.1f}s, "
                          f"F1: {result.accuracy_metrics['f1']:.2f}, "
                          f"confidence: {result.confidence_score:.2f}")
                logger.info(f"     Selected: {result.selected_tools}")
            else:
                logger.warning(f"  ❌ {tool_count} tools: Failed - {result.error}")
        
        self.results["cognitive_load_tests"] = [asdict(r) for r in cognitive_load_results]
        
        # Analysis
        successful_tests = [r for r in cognitive_load_results if r.selection_success]
        if successful_tests:
            avg_response_time = statistics.mean(r.response_time_seconds for r in successful_tests)
            avg_f1_score = statistics.mean(r.accuracy_metrics['f1'] for r in successful_tests)
            
            logger.info(f"📊 Cognitive Load Analysis Complete:")
            logger.info(f"   Successful tests: {len(successful_tests)}/{len(cognitive_load_results)}")
            logger.info(f"   Average response time: {avg_response_time:.1f}s")
            logger.info(f"   Average F1 score: {avg_f1_score:.2f}")
            logger.info(f"   Max tools tested: {max(self.tool_counts)} tools")
        
        return cognitive_load_results
    
    async def run_methodology_comparison(self, viable_tool_counts: List[int]) -> List[GeminiTestResult]:
        """Compare methodologies at viable tool counts"""
        
        logger.info("📊 Starting Methodology Comparison")
        logger.info(f"Testing methodologies: {self.methodologies}")
        logger.info(f"At tool counts: {viable_tool_counts}")
        
        methodology_results = []
        
        for methodology in self.methodologies:
            logger.info(f"Testing methodology: {methodology}")
            
            for tool_count in viable_tool_counts:
                for scenario in self.test_scenarios:
                    logger.info(f"  {methodology} | {tool_count} tools | {scenario.name}")
                    
                    # Generate tools
                    tools = self.tool_generator.generate_tools(tool_count, seed=42)
                    formatted_tools = self._format_tools_for_llm(tools)
                    
                    # Test methodology
                    result = await self.test_gemini_with_structured_output(
                        formatted_tools, scenario, methodology
                    )
                    
                    methodology_results.append(result)
                    
                    if result.selection_success:
                        logger.info(f"    ✅ {result.response_time_seconds:.1f}s, "
                                  f"F1: {result.accuracy_metrics['f1']:.2f}, "
                                  f"confidence: {result.confidence_score:.2f}")
                    else:
                        logger.warning(f"    ❌ Failed: {result.error}")
        
        self.results["methodology_comparison"] = [asdict(r) for r in methodology_results]
        
        return methodology_results
    
    def _format_tools_for_llm(self, tools: List[Any]) -> List[Dict[str, Any]]:
        """Format mock tools for LLM consumption"""
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
    
    def _analyze_results_for_kgas(self, 
                                cognitive_load_results: List[GeminiTestResult],
                                methodology_results: List[GeminiTestResult]) -> Dict[str, Any]:
        """Generate KGAS-specific recommendations"""
        
        logger.info("🎯 Analyzing Results for KGAS MCP Strategy")
        
        # Cognitive load analysis
        successful_cognitive = [r for r in cognitive_load_results if r.selection_success]
        
        if successful_cognitive:
            max_viable_tools = max(r.tool_count for r in successful_cognitive 
                                 if r.accuracy_metrics['f1'] > 0.3)  # Reasonable accuracy threshold
            
            avg_response_times = {}
            for result in successful_cognitive:
                avg_response_times[result.tool_count] = result.response_time_seconds
        else:
            max_viable_tools = 50  # Conservative fallback
            avg_response_times = {}
        
        # Methodology analysis
        methodology_performance = {}
        for methodology in self.methodologies:
            method_results = [r for r in methodology_results 
                            if r.methodology == methodology and r.selection_success]
            
            if method_results:
                avg_f1 = statistics.mean(r.accuracy_metrics['f1'] for r in method_results)
                avg_time = statistics.mean(r.response_time_seconds for r in method_results)
                avg_confidence = statistics.mean(r.confidence_score for r in method_results)
                
                methodology_performance[methodology] = {
                    "avg_f1_score": avg_f1,
                    "avg_response_time": avg_time,
                    "avg_confidence": avg_confidence,
                    "success_rate": len(method_results) / len([r for r in methodology_results if r.methodology == methodology])
                }
        
        # Best methodology
        best_methodology = max(methodology_performance.keys(), 
                             key=lambda m: methodology_performance[m]["avg_f1_score"]) if methodology_performance else "direct_exposure"
        
        # KGAS recommendations
        kgas_recommendations = {
            "cognitive_load_analysis": {
                "max_viable_tools": max_viable_tools,
                "kgas_121_tools_viable": max_viable_tools >= 121,
                "response_time_at_100_tools": avg_response_times.get(100, "not_tested"),
                "degradation_threshold": "no_degradation_detected" if max_viable_tools >= 500 else f"{max_viable_tools}_tools"
            },
            "methodology_recommendations": {
                "best_overall_methodology": best_methodology,
                "methodology_performance": methodology_performance,
                "recommended_for_kgas": best_methodology
            },
            "production_strategy": {
                "recommended_approach": f"{best_methodology} with up to {max_viable_tools} tools",
                "kgas_deployment_ready": max_viable_tools >= 121,
                "expected_response_time": f"{avg_response_times.get(100, 6):.1f}s for 100 tools",
                "confidence_level": "high" if max_viable_tools >= 200 else "medium"
            }
        }
        
        return kgas_recommendations
    
    async def run_comprehensive_gemini_analysis(self) -> Dict[str, Any]:
        """Run complete Gemini-focused analysis for KGAS"""
        
        logger.info("🚀 Starting Comprehensive Gemini Analysis for KGAS MCP Strategy")
        start_time = time.time()
        
        try:
            # Phase 1: Cognitive Load Analysis
            cognitive_load_results = await self.run_cognitive_load_analysis()
            
            # Determine viable tool counts (those with reasonable accuracy)
            viable_counts = [r.tool_count for r in cognitive_load_results 
                           if r.selection_success and r.accuracy_metrics['f1'] > 0.2]
            
            if not viable_counts:
                viable_counts = [10, 25, 50]  # Conservative fallback
            
            logger.info(f"Viable tool counts for methodology testing: {viable_counts}")
            
            # Phase 2: Methodology Comparison
            methodology_results = await self.run_methodology_comparison(viable_counts)
            
            # Phase 3: KGAS Analysis
            kgas_analysis = self._analyze_results_for_kgas(cognitive_load_results, methodology_results)
            
            total_time = time.time() - start_time
            
            # Compile final results
            final_results = {
                "test_summary": {
                    "model_tested": "gemini-2.5-flash",
                    "total_duration_seconds": total_time,
                    "cognitive_load_tests": len(cognitive_load_results),
                    "methodology_tests": len(methodology_results),
                    "success_rate": len([r for r in cognitive_load_results + methodology_results if r.selection_success]) / len(cognitive_load_results + methodology_results),
                    "completion_timestamp": time.time()
                },
                "cognitive_load_analysis": cognitive_load_results,
                "methodology_comparison": methodology_results,
                "kgas_recommendations": kgas_analysis,
                "raw_results": self.results
            }
            
            logger.info(f"🎉 Comprehensive Analysis Complete!")
            logger.info(f"Duration: {total_time/60:.1f} minutes")
            logger.info(f"KGAS 121-tool deployment: {'✅ VIABLE' if kgas_analysis['cognitive_load_analysis']['kgas_121_tools_viable'] else '⚠️ NEEDS REVIEW'}")
            logger.info(f"Recommended methodology: {kgas_analysis['methodology_recommendations']['best_overall_methodology']}")
            
            return final_results
            
        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            raise
    
    def save_results(self, results: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Save results to JSON file"""
        if not filename:
            timestamp = int(time.time())
            filename = f"gemini_focused_analysis_{timestamp}.json"
        
        filepath = Path(__file__).parent / filename
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"💾 Results saved to: {filepath}")
        return str(filepath)


async def main():
    """Run Gemini-focused analysis"""
    
    # Verify API access
    if not os.getenv("GOOGLE_API_KEY"):
        logger.error("Missing GOOGLE_API_KEY in environment")
        logger.info("Please ensure GOOGLE_API_KEY is set in .env file")
        return
    
    # Initialize and run analysis
    test_runner = GeminiFocusedTestRunner()
    
    try:
        results = await test_runner.run_comprehensive_gemini_analysis()
        
        # Save results
        results_file = test_runner.save_results(results)
        
        # Print executive summary
        print("\n" + "="*70)
        print("🎯 GEMINI-FOCUSED MCP ANALYSIS COMPLETE")
        print("="*70)
        
        summary = results["test_summary"]
        kgas_rec = results["kgas_recommendations"]
        
        print(f"Duration: {summary['total_duration_seconds']/60:.1f} minutes")
        print(f"Success rate: {summary['success_rate']:.1%}")
        print(f"Cognitive load tests: {summary['cognitive_load_tests']}")
        print(f"Methodology tests: {summary['methodology_tests']}")
        
        print(f"\n🚀 KGAS MCP STRATEGY RECOMMENDATIONS:")
        print(f"Max viable tools: {kgas_rec['cognitive_load_analysis']['max_viable_tools']}")
        print(f"121-tool deployment: {'✅ VIABLE' if kgas_rec['cognitive_load_analysis']['kgas_121_tools_viable'] else '⚠️ REVIEW NEEDED'}")
        print(f"Best methodology: {kgas_rec['methodology_recommendations']['best_overall_methodology']}")
        print(f"Production strategy: {kgas_rec['production_strategy']['recommended_approach']}")
        print(f"Confidence level: {kgas_rec['production_strategy']['confidence_level']}")
        
        print(f"\n📄 Full analysis: {results_file}")
        print("="*70)
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())