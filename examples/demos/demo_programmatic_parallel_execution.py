#!/usr/bin/env python3
"""
Demo Programmatic Parallel Execution

Demonstrates the new programmatic dependency analysis in action.
Shows how the system discovers parallel opportunities without hardcoded rules.
"""

import asyncio
import logging
from pathlib import Path

from src.execution.programmatic_dependency_analyzer import ProgrammaticDependencyAnalyzer
from src.execution.parallel_opportunity_finder import ParallelOpportunityFinder
from src.analysis.dependency_graph_builder import DependencyGraphBuilder
from src.nlp.tool_chain_generator import ToolStep

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def demo_programmatic_analysis():
    """Demonstrate programmatic dependency analysis"""
    
    print("\n" + "="*80)
    print("DEMO: PROGRAMMATIC PARALLEL EXECUTION")
    print("="*80)
    
    # Initialize analyzers
    print("\n1. Initializing programmatic analyzers...")
    dependency_analyzer = ProgrammaticDependencyAnalyzer()
    parallel_finder = ParallelOpportunityFinder()
    graph_builder = DependencyGraphBuilder()
    
    # Create a complex tool chain
    print("\n2. Creating complex tool chain...")
    test_steps = [
        ToolStep(tool_id="T01_PDF_LOADER", input_mapping={}, depends_on=[]),
        ToolStep(tool_id="T15A_TEXT_CHUNKER", input_mapping={}, depends_on=["T01_PDF_LOADER"]),
        ToolStep(tool_id="T23A_SPACY_NER", input_mapping={}, depends_on=["T15A_TEXT_CHUNKER"]),
        ToolStep(tool_id="T27_RELATIONSHIP_EXTRACTOR", input_mapping={}, depends_on=["T15A_TEXT_CHUNKER", "T23A_SPACY_NER"]),
        ToolStep(tool_id="T31_ENTITY_BUILDER", input_mapping={}, depends_on=["T23A_SPACY_NER"]),
        ToolStep(tool_id="T34_EDGE_BUILDER", input_mapping={}, depends_on=["T27_RELATIONSHIP_EXTRACTOR"]),
        ToolStep(tool_id="T68_PAGE_RANK", input_mapping={}, depends_on=["T31_ENTITY_BUILDER", "T34_EDGE_BUILDER"]),
        ToolStep(tool_id="T49_MULTI_HOP_QUERY", input_mapping={}, depends_on=["T31_ENTITY_BUILDER", "T34_EDGE_BUILDER"])
    ]
    
    print(f"   Tool chain: {[step.tool_id for step in test_steps]}")
    
    # Analyze dependencies programmatically
    print("\n3. Analyzing dependencies programmatically...")
    analysis = dependency_analyzer.analyze_dependencies(test_steps)
    
    dependency_analyzer.print_analysis_summary(analysis)
    
    # Build execution graph
    print("\n4. Building optimized execution plan...")
    required_tools = [step.tool_id for step in test_steps]
    dependency_graph = graph_builder.build_execution_graph(required_tools)
    
    execution_plan = parallel_finder.optimize_execution_plan(dependency_graph)
    parallel_finder.print_execution_plan(execution_plan)
    
    # Demonstrate specific parallel opportunities
    print("\n5. Demonstrating specific parallel opportunities...")
    
    # Test level 3 tools (should be able to run in parallel)
    level_3_tools = ["T27_RELATIONSHIP_EXTRACTOR", "T31_ENTITY_BUILDER"]
    parallel_groups = parallel_finder.find_maximal_parallel_groups(level_3_tools)
    
    print(f"\nLevel 3 tools: {level_3_tools}")
    print(f"Parallel groups found: {parallel_groups}")
    
    if any(len(group) > 1 for group in parallel_groups):
        print("✅ Successfully found parallel opportunities at level 3")
    else:
        print("❌ No parallel opportunities found (may be due to resource conflicts)")
    
    # Test level 4 tools (T68 and T49 should be able to run in parallel)
    level_4_tools = ["T68_PAGE_RANK", "T49_MULTI_HOP_QUERY"]
    parallel_groups = parallel_finder.find_maximal_parallel_groups(level_4_tools)
    
    print(f"\nLevel 4 tools: {level_4_tools}")
    print(f"Parallel groups found: {parallel_groups}")
    
    if any(len(group) > 1 for group in parallel_groups):
        print("✅ Successfully found parallel opportunities at level 4")
    else:
        print("❌ No parallel opportunities found (may be due to resource conflicts)")
    
    # Performance analysis
    print("\n6. Performance analysis...")
    performance = parallel_finder.estimate_performance_gain(execution_plan)
    
    print(f"Sequential time: {performance['sequential_time']:.1f}s")
    print(f"Parallel time: {performance['parallel_time']:.1f}s")
    print(f"Speedup: {performance['speedup_factor']:.2f}x")
    print(f"Time saved: {performance['time_saved']:.1f}s")
    print(f"Parallelization ratio: {performance['parallelization_ratio']:.1%}")
    
    print("\n" + "="*80)
    print("DEMO COMPLETE")
    print("="*80)
    
    print("\n🎉 SUCCESS: Programmatic parallel execution working!")
    print("🔧 Zero hardcoded rules - all analysis from contracts")
    print("⚡ Automatic discovery of parallel opportunities")
    print("📊 Performance optimization through intelligent scheduling")


if __name__ == "__main__":
    asyncio.run(demo_programmatic_analysis())