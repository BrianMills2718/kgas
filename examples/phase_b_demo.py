#!/usr/bin/env python3
"""
Phase B Dynamic Execution Demonstration

Interactive demonstration of Phase B dynamic execution and intelligent orchestration.
Shows the complete pipeline from complex questions to optimized parallel execution.
"""

import asyncio
import sys
import time
from pathlib import Path
from typing import Dict, List, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Phase B components
from src.nlp.advanced_intent_classifier import AdvancedIntentClassifier, QuestionIntent
from src.nlp.question_complexity_analyzer import QuestionComplexityAnalyzer, ComplexityLevel
from src.nlp.context_extractor import ContextExtractor
from src.nlp.tool_chain_generator import ToolChainGenerator
from src.execution.dag_builder import DynamicDAGBuilder
from src.execution.execution_planner import DynamicExecutionPlanner, ExecutionStrategy
from src.execution.parallel_executor import ParallelExecutor
from src.performance.execution_optimizer import ExecutionOptimizer, OptimizationStrategy
from src.performance.resource_manager_enhanced import EnhancedResourceManager


class PhaseBDemo:
    """Interactive Phase B demonstration"""
    
    def __init__(self):
        """Initialize Phase B components"""
        print("🚀 Initializing Phase B Dynamic Execution System...")
        
        # Phase B.1 - Advanced Question Analysis
        self.intent_classifier = AdvancedIntentClassifier()
        self.complexity_analyzer = QuestionComplexityAnalyzer()
        self.context_extractor = ContextExtractor()
        self.tool_chain_generator = ToolChainGenerator()
        
        # Phase B.2 - Dynamic DAG Building & Planning
        self.dag_builder = DynamicDAGBuilder()
        self.execution_planner = DynamicExecutionPlanner()
        
        # Phase B.5 - Performance Optimization
        self.parallel_executor = ParallelExecutor()
        self.execution_optimizer = ExecutionOptimizer()
        self.resource_manager = EnhancedResourceManager()
        
        print("✅ Phase B system initialized!")
        print()
    
    async def demonstrate_simple_question(self):
        """Demonstrate simple question processing"""
        
        print("="*60)
        print("📋 DEMONSTRATION 1: Simple Question Processing")
        print("="*60)
        
        question = "What entities are mentioned in the document?"
        print(f"Question: {question}")
        print()
        
        # Step 1: Question Analysis
        print("🔍 Step 1: Advanced Question Analysis")
        intent_result = self.intent_classifier.classify(question)
        complexity_result = self.complexity_analyzer.analyze_complexity(question)
        context_result = self.context_extractor.extract_context(question)
        
        print(f"   Intent: {intent_result.primary_intent.value}")
        print(f"   Confidence: {intent_result.confidence:.2f}")
        print(f"   Complexity: {complexity_result.level.value}")
        print(f"   Estimated Tools: {complexity_result.estimated_tools}")
        print(f"   Multi-step Required: {intent_result.requires_multi_step}")
        print()
        
        # Step 2: Tool Chain Generation
        print("🔧 Step 2: Dynamic Tool Chain Generation")
        tool_chain = self.tool_chain_generator.generate_tool_chain(
            intent_result, complexity_result, context_result
        )
        
        print(f"   Required Tools: {tool_chain.required_tools}")
        print(f"   Execution Strategy: {tool_chain.execution_strategy}")
        print(f"   Estimated Time: {tool_chain.estimated_execution_time:.1f}s")
        print()
        
        # Step 3: Execution Planning
        print("📊 Step 3: Dynamic Execution Planning")
        execution_plan = self.execution_planner.create_execution_plan(
            tool_chain.required_tools,
            intent_result.primary_intent,
            complexity_result.level,
            context_result,
            ExecutionStrategy.ADAPTIVE
        )
        
        print(f"   Execution Steps: {len(execution_plan.steps)}")
        print(f"   Parallelization Ratio: {execution_plan.parallelization_ratio:.1%}")
        print(f"   Total Estimated Time: {execution_plan.total_estimated_time:.1f}s")
        print(f"   Plan Confidence: {execution_plan.confidence:.2f}")
        print()
        
        # Step 4: Performance Optimization
        print("⚡ Step 4: Performance Optimization")
        optimization_result = await self.execution_optimizer.optimize_execution_plan(execution_plan)
        
        print(f"   Optimization Strategy: {optimization_result.optimized_plan.strategy.value}")
        print(f"   Performance Improvement: {optimization_result.performance_improvement:.1%}")
        print(f"   Applied Optimizations: {optimization_result.applied_optimizations}")
        print()
        
        # Step 5: Parallel Execution
        print("🚀 Step 5: Optimized Parallel Execution")
        start_time = time.time()
        execution_result = await self.parallel_executor.execute_parallel_plan(optimization_result.optimized_plan)
        actual_time = time.time() - start_time
        
        print(f"   Execution Time: {actual_time:.2f}s")
        print(f"   Successful Steps: {execution_result.successful_steps}/{execution_result.total_steps}")
        print(f"   Speedup Factor: {execution_result.speedup_factor:.2f}x")
        print(f"   Parallel Efficiency: {execution_result.parallel_efficiency:.1%}")
        print(f"   Time Saved: {execution_result.performance_metrics.get('time_saved', 0):.2f}s")
        print()
        
        return execution_result.speedup_factor
    
    async def demonstrate_complex_question(self):
        """Demonstrate complex multi-part question processing"""
        
        print("="*60)
        print("🧠 DEMONSTRATION 2: Complex Multi-Part Question")
        print("="*60)
        
        question = "What are the main themes and how do they relate to key entities over time?"
        print(f"Question: {question}")
        print()
        
        # Step 1: Advanced Analysis
        print("🔍 Step 1: Advanced Question Analysis")
        intent_result = self.intent_classifier.classify(question)
        complexity_result = self.complexity_analyzer.analyze_complexity(question)
        context_result = self.context_extractor.extract_context(question)
        
        print(f"   Primary Intent: {intent_result.primary_intent.value}")
        print(f"   Secondary Intents: {[intent.value for intent in intent_result.secondary_intents]}")
        print(f"   Complexity: {complexity_result.level.value}")
        print(f"   Complexity Factors: {complexity_result.complexity_factors}")
        print(f"   Multi-step Required: {intent_result.requires_multi_step}")
        print()
        
        # Step 2: Context Analysis
        print("🌐 Step 2: Context Extraction")
        has_temporal = hasattr(context_result, 'temporal_context') and context_result.temporal_context
        has_entities = hasattr(context_result, 'entity_context') and context_result.entity_context
        print(f"   Temporal Context: {'Yes' if has_temporal else 'No'}")
        print(f"   Entity Context: {'Yes' if has_entities else 'No'}")
        print(f"   Requires Theme Analysis: Yes")
        print()
        
        # Step 3: Advanced Tool Chain
        print("🔧 Step 3: Advanced Tool Chain Generation")
        tool_chain = self.tool_chain_generator.generate_tool_chain(
            intent_result, complexity_result, context_result
        )
        
        print(f"   Required Tools: {tool_chain.required_tools}")
        print(f"   Tools Count: {len(tool_chain.required_tools)}")
        print(f"   Execution Strategy: {tool_chain.execution_strategy}")
        print()
        
        # Step 4: Dynamic DAG Construction
        print("📊 Step 4: Dynamic DAG Construction")
        dag = self.dag_builder.build_execution_dag(
            tool_chain.required_tools,
            intent_result.primary_intent,
            {"temporal": has_temporal, "entities": has_entities, "themes": True}
        )
        
        print(f"   DAG Nodes: {len(dag.nodes)}")
        print(f"   DAG Edges: {len(dag.edges)}")
        print(f"   Entry Points: {dag.entry_points}")
        print(f"   Exit Points: {dag.exit_points}")
        print()
        
        # Step 5: Adaptive Planning
        print("🎯 Step 5: Adaptive Execution Planning")
        execution_plan = self.execution_planner.create_execution_plan(
            tool_chain.required_tools,
            intent_result.primary_intent,
            complexity_result.level,
            context_result,
            ExecutionStrategy.ADAPTIVE
        )
        
        parallel_steps = execution_plan.get_parallel_steps()
        print(f"   Total Steps: {len(execution_plan.steps)}")
        print(f"   Parallel Steps: {len(parallel_steps)}")
        print(f"   Parallelization Ratio: {execution_plan.parallelization_ratio:.1%}")
        print(f"   Adaptive Features: {execution_plan.adaptive_features}")
        print()
        
        # Step 6: Multi-Strategy Optimization
        print("⚡ Step 6: Multi-Strategy Optimization")
        
        # Try different optimization strategies
        strategies = [
            OptimizationStrategy.THROUGHPUT_MAXIMIZATION,
            OptimizationStrategy.LATENCY_MINIMIZATION,
            OptimizationStrategy.BALANCED_PERFORMANCE
        ]
        
        best_strategy = None
        best_improvement = -1.0
        
        for strategy in strategies:
            optimizer = ExecutionOptimizer()
            optimizer.config.strategy = strategy
            
            opt_result = await optimizer.optimize_execution_plan(execution_plan)
            improvement = opt_result.performance_improvement
            
            print(f"   {strategy.value}: {improvement:.1%} improvement")
            
            if improvement > best_improvement:
                best_improvement = improvement
                best_strategy = strategy
        
        print(f"   Best Strategy: {best_strategy.value} ({best_improvement:.1%})")
        print()
        
        # Step 7: Optimized Execution
        print("🚀 Step 7: Optimized Parallel Execution")
        
        # Use best strategy
        final_optimizer = ExecutionOptimizer()
        final_optimizer.config.strategy = best_strategy
        final_optimization = await final_optimizer.optimize_execution_plan(execution_plan)
        
        start_time = time.time()
        execution_result = await self.parallel_executor.execute_parallel_plan(final_optimization.optimized_plan)
        actual_time = time.time() - start_time
        
        print(f"   Execution Time: {actual_time:.2f}s")
        print(f"   Sequential Estimate: {execution_result.performance_metrics.get('sequential_time_estimate', 0):.2f}s")
        print(f"   Speedup Factor: {execution_result.speedup_factor:.2f}x")
        print(f"   Parallel Efficiency: {execution_result.parallel_efficiency:.1%}")
        print(f"   Successful Steps: {execution_result.successful_steps}/{execution_result.total_steps}")
        print(f"   Parallel Groups: {execution_result.performance_metrics.get('parallel_groups', 0)}")
        print(f"   Time Saved: {execution_result.performance_metrics.get('time_saved', 0):.2f}s")
        print()
        
        return execution_result.speedup_factor
    
    async def demonstrate_performance_comparison(self):
        """Demonstrate performance comparison across question types"""
        
        print("="*60)
        print("📊 DEMONSTRATION 3: Performance Comparison")
        print("="*60)
        
        test_questions = [
            ("What is this document about?", "Simple"),
            ("How do entities relate to each other?", "Moderate"),
            ("What are the temporal patterns in entity relationships and network centrality?", "Complex")
        ]
        
        results = []
        
        for question, difficulty in test_questions:
            print(f"🔍 Processing {difficulty} Question:")
            print(f"   \"{question}\"")
            
            # Quick pipeline execution
            start_time = time.time()
            
            intent_result = self.intent_classifier.classify(question)
            complexity_result = self.complexity_analyzer.analyze_complexity(question)
            context_result = self.context_extractor.extract_context(question)
            
            tool_chain = self.tool_chain_generator.generate_tool_chain(
                intent_result, complexity_result, context_result
            )
            
            execution_plan = self.execution_planner.create_execution_plan(
                tool_chain.required_tools,
                intent_result.primary_intent,
                complexity_result.level,
                context_result
            )
            
            optimization_result = await self.execution_optimizer.optimize_execution_plan(execution_plan)
            execution_result = await self.parallel_executor.execute_parallel_plan(optimization_result.optimized_plan)
            
            pipeline_time = time.time() - start_time
            
            results.append({
                'difficulty': difficulty,
                'pipeline_time': pipeline_time,
                'tools_used': len(tool_chain.required_tools),
                'speedup': execution_result.speedup_factor,
                'efficiency': execution_result.parallel_efficiency
            })
            
            print(f"   Pipeline Time: {pipeline_time:.2f}s")
            print(f"   Tools Used: {len(tool_chain.required_tools)}")
            print(f"   Speedup: {execution_result.speedup_factor:.2f}x")
            print(f"   Efficiency: {execution_result.parallel_efficiency:.1%}")
            print()
        
        # Summary
        print("📈 Performance Summary:")
        total_speedup = sum(r['speedup'] for r in results)
        avg_speedup = total_speedup / len(results)
        max_speedup = max(r['speedup'] for r in results)
        
        print(f"   Average Speedup: {avg_speedup:.2f}x")
        print(f"   Maximum Speedup: {max_speedup:.2f}x")
        print(f"   Performance Improvement: {(max_speedup - 1.0) * 100:.1f}%")
        
        # Phase B requirement check
        if max_speedup >= 1.5:
            print("   🎉 PHASE B REQUIREMENT MET: >50% improvement achieved!")
        else:
            print(f"   ⚠️  Current improvement: {(max_speedup - 1.0) * 100:.1f}% (target: >50%)")
        
        print()
        return results
    
    async def demonstrate_resource_monitoring(self):
        """Demonstrate resource monitoring capabilities"""
        
        print("="*60)
        print("🖥️  DEMONSTRATION 4: Resource Monitoring")
        print("="*60)
        
        # Get initial system status
        initial_status = self.resource_manager.get_system_status()
        
        print("💻 System Status:")
        print(f"   CPU Usage: {initial_status['cpu_percent']:.1f}%")
        print(f"   Memory Usage: {initial_status['memory_percent']:.1f}%")
        print(f"   Active Allocations: {initial_status['active_allocations']}")
        print()
        
        # Resource allocation demonstration
        print("🔧 Resource Allocation Demo:")
        from src.performance.resource_manager_enhanced import ResourceRequest, ResourceType
        
        request = ResourceRequest(
            requester_id="demo_process",
            resource_type=ResourceType.CPU,
            amount=30.0,
            priority=7
        )
        
        allocation = await self.resource_manager.request_resource(request)
        
        if allocation:
            print(f"   ✅ Allocated {allocation.allocated_amount} {allocation.resource_type.value}")
            print(f"   Allocation ID: {allocation.allocation_id}")
            
            # Show updated status
            updated_status = self.resource_manager.get_system_status()
            print(f"   Active Allocations: {updated_status['active_allocations']}")
            
            # Release resource
            success = self.resource_manager.release_resource(allocation.allocation_id)
            print(f"   Released: {'✅ Success' if success else '❌ Failed'}")
        else:
            print("   ❌ Resource allocation failed")
        
        print()
        
        # Performance metrics
        print("📊 Performance Metrics:")
        perf_metrics = self.parallel_executor.get_performance_metrics()
        
        print(f"   Total Executions: {perf_metrics['total_executions']}")
        print(f"   Parallel Executions: {perf_metrics['parallel_executions']}")
        print(f"   Average Speedup: {perf_metrics['average_speedup']:.2f}x")
        print(f"   Best Speedup: {perf_metrics['best_speedup']:.2f}x")
        print(f"   Total Time Saved: {perf_metrics['total_time_saved']:.2f}s")
        print()
    
    async def run_full_demonstration(self):
        """Run complete Phase B demonstration"""
        
        print("🎯 PHASE B DYNAMIC EXECUTION DEMONSTRATION")
        print("🚀 Advanced Question Analysis → Dynamic Orchestration → Optimized Parallel Execution")
        print()
        
        try:
            # Run demonstrations
            speedup1 = await self.demonstrate_simple_question()
            speedup2 = await self.demonstrate_complex_question()
            comparison_results = await self.demonstrate_performance_comparison()
            await self.demonstrate_resource_monitoring()
            
            # Final summary
            print("="*60)
            print("🎉 PHASE B DEMONSTRATION COMPLETE")
            print("="*60)
            
            all_speedups = [speedup1, speedup2] + [r['speedup'] for r in comparison_results]
            max_speedup = max(all_speedups)
            
            print("✅ Phase B Capabilities Demonstrated:")
            print("   • Advanced Intent Classification (15 intent types)")
            print("   • Dynamic Question Complexity Analysis")
            print("   • Context-Aware Tool Chain Generation") 
            print("   • Dynamic DAG Construction & Execution Planning")
            print("   • Multi-Strategy Performance Optimization")
            print("   • Parallel Execution with Resource Management")
            print()
            
            print("📊 Performance Results:")
            print(f"   Maximum Speedup Achieved: {max_speedup:.2f}x")
            print(f"   Performance Improvement: {(max_speedup - 1.0) * 100:.1f}%")
            
            if max_speedup >= 1.5:
                print("   🎉 PHASE B SUCCESS: >50% performance improvement achieved!")
            else:
                print("   📈 Performance improvement demonstrated, targeting >50%")
            
            print()
            print("🚀 Phase B Dynamic Execution System is operational!")
            
        except Exception as e:
            print(f"❌ Demonstration failed: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Cleanup
            self.resource_manager.shutdown()


async def main():
    """Main demonstration function"""
    
    demo = PhaseBDemo()
    await demo.run_full_demonstration()


if __name__ == "__main__":
    asyncio.run(main())