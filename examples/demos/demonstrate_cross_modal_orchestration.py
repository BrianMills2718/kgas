#!/usr/bin/env python3
"""
Demonstrate Cross-Modal Analysis Orchestration System

This script demonstrates the complete cross-modal analysis orchestration system
including intelligent mode selection, format conversion, validation, and workflow optimization.
"""

import asyncio
import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, List

# Import the cross-modal orchestration components
from src.analytics.mode_selection_service import (
    ModeSelectionService, DataContext, AnalysisMode, create_data_context
)
from src.analytics.cross_modal_converter import (
    CrossModalConverter, DataFormat, ConversionResult
)
from src.analytics.cross_modal_validator import (
    CrossModalValidator, ValidationLevel, ValidationReport
)
from src.analytics.cross_modal_orchestrator import (
    CrossModalOrchestrator, WorkflowOptimizationLevel
)


def create_sample_graph_data() -> Dict[str, Any]:
    """Create sample graph data for demonstration"""
    
    return {
        "nodes": [
            {"id": "person_1", "label": "Alice", "type": "person", "properties": {"age": 30, "city": "New York"}},
            {"id": "person_2", "label": "Bob", "type": "person", "properties": {"age": 25, "city": "San Francisco"}},
            {"id": "person_3", "label": "Charlie", "type": "person", "properties": {"age": 35, "city": "Boston"}},
            {"id": "company_1", "label": "TechCorp", "type": "company", "properties": {"industry": "technology", "size": 1000}},
            {"id": "company_2", "label": "DataInc", "type": "company", "properties": {"industry": "data", "size": 500}},
            {"id": "project_1", "label": "AI Research", "type": "project", "properties": {"budget": 100000, "duration": 12}},
            {"id": "project_2", "label": "Data Pipeline", "type": "project", "properties": {"budget": 50000, "duration": 6}}
        ],
        "edges": [
            {"source": "person_1", "target": "company_1", "type": "works_for", "weight": 1.0, "properties": {"role": "engineer", "years": 5}},
            {"source": "person_2", "target": "company_1", "type": "works_for", "weight": 1.0, "properties": {"role": "manager", "years": 3}},
            {"source": "person_3", "target": "company_2", "type": "works_for", "weight": 1.0, "properties": {"role": "scientist", "years": 7}},
            {"source": "person_1", "target": "project_1", "type": "contributes_to", "weight": 0.8, "properties": {"contribution": "lead"}},
            {"source": "person_2", "target": "project_1", "type": "contributes_to", "weight": 0.6, "properties": {"contribution": "support"}},
            {"source": "person_3", "target": "project_2", "type": "contributes_to", "weight": 1.0, "properties": {"contribution": "lead"}},
            {"source": "company_1", "target": "project_1", "type": "funds", "weight": 1.0, "properties": {"amount": 80000}},
            {"source": "company_2", "target": "project_2", "type": "funds", "weight": 1.0, "properties": {"amount": 50000}}
        ]
    }


def create_sample_table_data() -> pd.DataFrame:
    """Create sample table data for demonstration"""
    
    data = {
        "person_id": ["p1", "p2", "p3", "p4", "p5"],
        "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
        "age": [30, 25, 35, 28, 32],
        "city": ["New York", "San Francisco", "Boston", "Seattle", "Austin"],
        "profession": ["Engineer", "Manager", "Scientist", "Designer", "Analyst"],
        "company": ["TechCorp", "TechCorp", "DataInc", "DesignCo", "AnalyticsPro"],
        "salary": [85000, 95000, 90000, 75000, 80000],
        "years_experience": [5, 8, 10, 3, 6]
    }
    
    return pd.DataFrame(data)


def create_sample_vector_data() -> np.ndarray:
    """Create sample vector data for demonstration"""
    
    # Simulate embeddings for documents or entities
    np.random.seed(42)  # For reproducible results
    return np.random.rand(10, 384)  # 10 entities with 384-dimensional embeddings


def print_section_header(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_subsection_header(title: str):
    """Print a formatted subsection header"""
    print(f"\n{'-'*40}")
    print(f"  {title}")
    print(f"{'-'*40}")


async def demonstrate_mode_selection():
    """Demonstrate intelligent mode selection"""
    
    print_section_header("INTELLIGENT MODE SELECTION")
    
    # Initialize mode selection service
    mode_selector = ModeSelectionService()
    await mode_selector.initialize({})
    
    # Test different research questions and data contexts
    test_cases = [
        {
            "question": "What are the key relationships between people and companies in our network?",
            "context": create_data_context(
                data_size=1000,
                data_types=["entities", "relationships", "graph"],
                entity_count=100,
                relationship_count=200,
                has_temporal_data=False,
                has_spatial_data=False,
                has_hierarchical_structure=True
            )
        },
        {
            "question": "What are the statistical patterns in employee salaries across different cities?",
            "context": create_data_context(
                data_size=500,
                data_types=["structured", "numeric", "categorical"],
                entity_count=500,
                relationship_count=0,
                has_temporal_data=False,
                has_spatial_data=True,
                has_hierarchical_structure=False
            )
        },
        {
            "question": "Which documents are most similar to each other based on semantic content?",
            "context": create_data_context(
                data_size=10000,
                data_types=["embeddings", "text", "semantic"],
                entity_count=1000,
                relationship_count=0,
                has_temporal_data=False,
                has_spatial_data=False,
                has_hierarchical_structure=False
            )
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print_subsection_header(f"Test Case {i}")
        print(f"Research Question: {test_case['question']}")
        print(f"Data Context: {test_case['context'].data_size} records, "
              f"{test_case['context'].entity_count} entities, "
              f"{', '.join(test_case['context'].data_types)}")
        
        # Select optimal mode
        selection_result = await mode_selector.select_optimal_mode(
            test_case["question"],
            test_case["context"]
        )
        
        print(f"\nSelected Mode: {selection_result.primary_mode.value}")
        print(f"Confidence: {selection_result.confidence:.3f} ({selection_result.confidence_level.value})")
        print(f"Secondary Modes: {[mode.value for mode in selection_result.secondary_modes]}")
        print(f"Fallback Used: {selection_result.fallback_used}")
        print(f"Reasoning: {selection_result.reasoning[:200]}...")
        print(f"Workflow Steps: {len(selection_result.workflow_steps)} steps")
        
        # Show estimated performance
        performance = selection_result.estimated_performance
        print(f"Estimated Time: {performance.get('estimated_execution_time', 0):.1f}s")
        print(f"Memory Requirements: {performance.get('memory_requirements', 'Unknown')}")


async def demonstrate_cross_modal_conversion():
    """Demonstrate cross-modal format conversion"""
    
    print_section_header("CROSS-MODAL FORMAT CONVERSION")
    
    # Initialize converter
    converter = CrossModalConverter()
    await converter.initialize({})
    
    # Test conversions between different formats
    conversions = [
        {
            "name": "Graph to Table",
            "data": create_sample_graph_data(),
            "source": DataFormat.GRAPH,
            "target": DataFormat.TABLE,
            "params": {"table_type": "edges"}
        },
        {
            "name": "Table to Graph",
            "data": create_sample_table_data(),
            "source": DataFormat.TABLE,
            "target": DataFormat.GRAPH,
            "params": {"source_column": "person_id", "target_column": "company", "type_column": "profession"}
        },
        {
            "name": "Graph to Vector",
            "data": create_sample_graph_data(),
            "source": DataFormat.GRAPH,
            "target": DataFormat.VECTOR,
            "params": {"method": "graph_features"}
        }
    ]
    
    for conversion in conversions:
        print_subsection_header(conversion["name"])
        print(f"Converting {conversion['source'].value} -> {conversion['target'].value}")
        
        try:
            # Perform conversion
            result = await converter.convert_data(
                conversion["data"],
                conversion["source"],
                conversion["target"],
                preserve_semantics=True,
                **conversion["params"]
            )
            
            print(f"Conversion Status: {'SUCCESS' if result.validation_passed else 'FAILED'}")
            print(f"Preservation Score: {result.preservation_score:.3f}")
            print(f"Semantic Integrity: {result.semantic_integrity}")
            print(f"Processing Time: {result.conversion_metadata.processing_time:.3f}s")
            print(f"Data Size: {result.conversion_metadata.data_size_before} -> {result.conversion_metadata.data_size_after}")
            
            if result.warnings:
                print(f"Warnings: {'; '.join(result.warnings)}")
            
            # Show sample of converted data
            converted_data = result.data
            if isinstance(converted_data, pd.DataFrame):
                print(f"Converted DataFrame shape: {converted_data.shape}")
                print("Sample rows:")
                print(converted_data.head(3).to_string())
            elif isinstance(converted_data, np.ndarray):
                print(f"Converted array shape: {converted_data.shape}")
                print(f"Sample values: {converted_data.flatten()[:10]}")
            elif isinstance(converted_data, dict):
                print(f"Converted graph: {len(converted_data.get('nodes', []))} nodes, {len(converted_data.get('edges', []))} edges")
                
        except Exception as e:
            print(f"Conversion FAILED: {e}")


async def demonstrate_validation_framework():
    """Demonstrate comprehensive validation framework"""
    
    print_section_header("VALIDATION FRAMEWORK")
    
    # Initialize validator
    validator = CrossModalValidator()
    await validator.initialize({})
    
    # Test validation scenarios
    validation_tests = [
        {
            "name": "Basic Graph-Table Conversion Validation",
            "data": create_sample_graph_data(),
            "source": DataFormat.GRAPH,
            "target": DataFormat.TABLE,
            "level": ValidationLevel.BASIC
        },
        {
            "name": "Comprehensive Table-Graph Validation",
            "data": create_sample_table_data(),
            "source": DataFormat.TABLE,
            "target": DataFormat.GRAPH,
            "level": ValidationLevel.COMPREHENSIVE
        },
        {
            "name": "Round-trip Integrity Validation",
            "data": create_sample_graph_data(),
            "formats": [DataFormat.GRAPH, DataFormat.TABLE, DataFormat.GRAPH],
            "level": ValidationLevel.STANDARD
        }
    ]
    
    for i, test in enumerate(validation_tests, 1):
        print_subsection_header(f"Validation Test {i}: {test['name']}")
        
        try:
            if "formats" in test:
                # Round-trip validation
                report = await validator.validate_round_trip_integrity(
                    test["data"],
                    test["formats"],
                    test["level"]
                )
            else:
                # Single conversion validation
                report = await validator.validate_cross_modal_conversion(
                    test["data"],
                    test["source"],
                    test["target"],
                    test["level"]
                )
            
            print(f"Validation Result: {'PASSED' if report.overall_passed else 'FAILED'}")
            print(f"Overall Score: {report.overall_score:.3f}")
            print(f"Tests Run: {report.total_tests} (Passed: {report.passed_tests}, Failed: {report.failed_tests})")
            print(f"Execution Time: {report.execution_time:.3f}s")
            print(f"Validation Level: {report.validation_level.value}")
            
            # Show test results summary
            if report.test_results:
                print("\nTest Results Summary:")
                for test_result in report.test_results[:3]:  # Show first 3 tests
                    status = "PASS" if test_result.passed else "FAIL"
                    print(f"  - {test_result.test_name}: {status} (Score: {test_result.score:.3f})")
            
            # Show recommendations
            if report.recommendations:
                print(f"\nRecommendations:")
                for rec in report.recommendations[:3]:  # Show first 3 recommendations
                    print(f"  - {rec}")
            
            # Show performance metrics
            if report.performance_metrics:
                print(f"\nPerformance: Avg test time {report.performance_metrics.get('average_test_time', 0):.3f}s")
                
        except Exception as e:
            print(f"Validation FAILED: {e}")


async def demonstrate_full_orchestration():
    """Demonstrate complete cross-modal analysis orchestration"""
    
    print_section_header("COMPLETE CROSS-MODAL ORCHESTRATION")
    
    # Initialize orchestrator
    orchestrator = CrossModalOrchestrator()
    await orchestrator.initialize({})
    
    # Test orchestration scenarios
    orchestration_tests = [
        {
            "name": "Network Analysis Workflow",
            "question": "What are the most important relationships and influence patterns in our professional network?",
            "data": create_sample_graph_data(),
            "source_format": DataFormat.GRAPH,
            "preferred_modes": [AnalysisMode.GRAPH_ANALYSIS, AnalysisMode.HYBRID_GRAPH_TABLE],
            "validation_level": ValidationLevel.STANDARD,
            "optimization_level": WorkflowOptimizationLevel.STANDARD
        },
        {
            "name": "Statistical Analysis Workflow",
            "question": "What are the key demographic and professional patterns in our employee dataset?",
            "data": create_sample_table_data(),
            "source_format": DataFormat.TABLE,
            "preferred_modes": [AnalysisMode.TABLE_ANALYSIS, AnalysisMode.HYBRID_TABLE_VECTOR],
            "validation_level": ValidationLevel.COMPREHENSIVE,
            "optimization_level": WorkflowOptimizationLevel.AGGRESSIVE
        }
    ]
    
    for i, test in enumerate(orchestration_tests, 1):
        print_subsection_header(f"Orchestration Test {i}: {test['name']}")
        print(f"Research Question: {test['question']}")
        print(f"Data Format: {test['source_format'].value}")
        print(f"Preferred Modes: {[mode.value for mode in test['preferred_modes']]}")
        print(f"Validation Level: {test['validation_level'].value}")
        print(f"Optimization Level: {test['optimization_level'].value}")
        
        try:
            # Run orchestrated analysis
            result = await orchestrator.orchestrate_analysis(
                research_question=test["question"],
                data=test["data"],
                source_format=test["source_format"],
                preferred_modes=test["preferred_modes"],
                validation_level=test["validation_level"],
                optimization_level=test["optimization_level"]
            )
            
            print(f"\nOrchestration Result: {'SUCCESS' if result.success else 'FAILED'}")
            print(f"Execution Time: {result.execution_time:.3f}s")
            print(f"Workflow Efficiency: {result.workflow_efficiency:.3f}")
            print(f"Workflow ID: {result.workflow_id}")
            
            # Show analysis metadata
            analysis_meta = result.analysis_metadata
            mode_selection = analysis_meta.get("mode_selection", {})
            print(f"\nSelected Analysis Mode: {mode_selection.get('primary_mode', 'Unknown')}")
            print(f"Mode Selection Confidence: {mode_selection.get('confidence', 0):.3f}")
            print(f"Fallback Used: {mode_selection.get('fallback_used', False)}")
            
            # Show workflow optimization
            workflow_opt = analysis_meta.get("workflow_optimization", {})
            print(f"\nWorkflow Optimization:")
            print(f"  - Level: {workflow_opt.get('optimization_level', 'Unknown')}")
            print(f"  - Changes Applied: {len(workflow_opt.get('changes_made', []))}")
            print(f"  - Optimizations: {', '.join(workflow_opt.get('changes_made', []))}")
            
            # Show performance metrics
            perf_metrics = result.performance_metrics
            print(f"\nPerformance Metrics:")
            print(f"  - Steps Completed: {perf_metrics.get('steps_completed', 0)}/{perf_metrics.get('total_steps', 0)}")
            print(f"  - Completion Rate: {perf_metrics.get('completion_rate', 0):.3f}")
            print(f"  - Time Accuracy: {perf_metrics.get('time_accuracy', 0):.3f}")
            
            # Show validation results
            if result.validation_report:
                val_report = result.validation_report
                print(f"\nValidation Results:")
                print(f"  - Overall Score: {val_report.overall_score:.3f}")
                print(f"  - Tests Passed: {val_report.passed_tests}/{val_report.total_tests}")
                print(f"  - Validation Status: {'PASSED' if val_report.overall_passed else 'FAILED'}")
            
            # Show recommendations
            if result.recommendations:
                print(f"\nRecommendations:")
                for rec in result.recommendations[:3]:
                    print(f"  - {rec}")
            
            # Show primary result info
            if result.primary_result is not None:
                if isinstance(result.primary_result, pd.DataFrame):
                    print(f"\nPrimary Result: DataFrame with shape {result.primary_result.shape}")
                elif isinstance(result.primary_result, dict):
                    print(f"Primary Result: Graph with {len(result.primary_result.get('nodes', []))} nodes")
                elif isinstance(result.primary_result, np.ndarray):
                    print(f"Primary Result: Array with shape {result.primary_result.shape}")
                else:
                    print(f"Primary Result: {type(result.primary_result).__name__}")
            
            print(f"\nSecondary Results: {len(result.secondary_results)} additional analyses")
                
        except Exception as e:
            print(f"Orchestration FAILED: {e}")


async def demonstrate_performance_comparison():
    """Demonstrate performance comparison across different configurations"""
    
    print_section_header("PERFORMANCE COMPARISON")
    
    # Initialize orchestrator
    orchestrator = CrossModalOrchestrator()
    await orchestrator.initialize({})
    
    # Test data
    test_data = create_sample_graph_data()
    research_question = "Analyze the network structure and identify key patterns"
    
    # Different optimization levels
    optimization_levels = [
        WorkflowOptimizationLevel.BASIC,
        WorkflowOptimizationLevel.STANDARD,
        WorkflowOptimizationLevel.AGGRESSIVE
    ]
    
    results = []
    
    for opt_level in optimization_levels:
        print_subsection_header(f"Testing {opt_level.value.title()} Optimization")
        
        try:
            # Run analysis with this optimization level
            result = await orchestrator.orchestrate_analysis(
                research_question=research_question,
                data=test_data,
                source_format=DataFormat.GRAPH,
                validation_level=ValidationLevel.BASIC,  # Use basic for speed
                optimization_level=opt_level
            )
            
            results.append({
                "optimization_level": opt_level.value,
                "execution_time": result.execution_time,
                "workflow_efficiency": result.workflow_efficiency,
                "success": result.success,
                "steps_completed": result.performance_metrics.get("steps_completed", 0),
                "total_steps": result.performance_metrics.get("total_steps", 0)
            })
            
            print(f"Execution Time: {result.execution_time:.3f}s")
            print(f"Workflow Efficiency: {result.workflow_efficiency:.3f}")
            print(f"Success: {result.success}")
            
        except Exception as e:
            print(f"Test FAILED: {e}")
            results.append({
                "optimization_level": opt_level.value,
                "execution_time": float('inf'),
                "workflow_efficiency": 0.0,
                "success": False,
                "steps_completed": 0,
                "total_steps": 0
            })
    
    # Show comparison summary
    print_subsection_header("Performance Comparison Summary")
    
    if results:
        print(f"{'Optimization Level':<20} {'Time (s)':<10} {'Efficiency':<12} {'Success':<10}")
        print(f"{'-'*20} {'-'*10} {'-'*12} {'-'*10}")
        
        for result in results:
            time_str = f"{result['execution_time']:.3f}" if result['execution_time'] != float('inf') else "FAILED"
            print(f"{result['optimization_level']:<20} {time_str:<10} {result['workflow_efficiency']:<12.3f} {result['success']:<10}")
        
        # Find best performing configuration
        successful_results = [r for r in results if r['success']]
        if successful_results:
            best_result = min(successful_results, key=lambda x: x['execution_time'])
            print(f"\nBest Configuration: {best_result['optimization_level']} optimization")
            print(f"  - Time: {best_result['execution_time']:.3f}s")
            print(f"  - Efficiency: {best_result['workflow_efficiency']:.3f}")


async def main():
    """Main demonstration function"""
    
    print("🚀 Cross-Modal Analysis Orchestration System Demonstration")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Run all demonstrations
        await demonstrate_mode_selection()
        await demonstrate_cross_modal_conversion()
        await demonstrate_validation_framework()
        await demonstrate_full_orchestration()
        await demonstrate_performance_comparison()
        
        print_section_header("DEMONSTRATION COMPLETE")
        print("✅ All demonstrations completed successfully!")
        print("\nKey Features Demonstrated:")
        print("  ✓ Intelligent LLM-driven mode selection with fallback rules")
        print("  ✓ Comprehensive cross-modal format conversion (graph ↔ table ↔ vector)")
        print("  ✓ Multi-level validation framework with integrity testing")
        print("  ✓ Intelligent workflow orchestration with optimization")
        print("  ✓ Performance monitoring and efficiency tracking")
        print("  ✓ Comprehensive error handling and recovery")
        
        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"\n❌ Demonstration failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(main())