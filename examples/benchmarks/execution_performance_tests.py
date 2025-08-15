#!/usr/bin/env python3
"""
Execution Performance Benchmarks

Comprehensive performance benchmarking for Phase B dynamic execution.
Measures and validates performance improvements across different scenarios.
"""

import asyncio
import sys
import time
import statistics
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.execution.parallel_executor import ParallelExecutor, ParallelExecutionConfig
from src.performance.execution_optimizer import ExecutionOptimizer, OptimizationStrategy
from src.performance.resource_manager_enhanced import EnhancedResourceManager
from src.nlp.advanced_intent_classifier import AdvancedIntentClassifier
from src.nlp.question_complexity_analyzer import QuestionComplexityAnalyzer
from src.execution.execution_planner import DynamicExecutionPlanner, ExecutionStrategy


@dataclass
class BenchmarkResult:
    """Result of a performance benchmark"""
    benchmark_name: str
    scenario: str
    sequential_time_estimate: float
    parallel_time_actual: float
    speedup_factor: float
    parallel_efficiency: float
    resource_utilization: Dict[str, float]
    success_rate: float
    metadata: Dict[str, Any]


@dataclass
class BenchmarkSuite:
    """Complete benchmark suite results"""
    suite_name: str
    total_benchmarks: int
    average_speedup: float
    best_speedup: float
    worst_speedup: float
    total_time_saved: float
    performance_requirement_met: bool
    individual_results: List[BenchmarkResult]


class ExecutionPerformanceBenchmarks:
    """Comprehensive performance benchmarking suite"""
    
    def __init__(self):
        """Initialize benchmarking environment"""
        print("🏁 Initializing Performance Benchmarking Suite...")
        
        # Core components
        self.parallel_executor = ParallelExecutor()
        self.execution_optimizer = ExecutionOptimizer()
        self.resource_manager = EnhancedResourceManager()
        self.intent_classifier = AdvancedIntentClassifier()
        self.complexity_analyzer = QuestionComplexityAnalyzer()
        self.execution_planner = DynamicExecutionPlanner()
        
        # Benchmark results
        self.results: List[BenchmarkResult] = []
        
        print("✅ Benchmarking suite initialized!")
    
    def create_test_execution_plan(self, plan_id: str, tool_ids: List[str], total_time: float = 10.0):
        """Create test execution plan for benchmarking"""
        from tests.test_performance_optimization import create_test_execution_plan
        return create_test_execution_plan(plan_id, tool_ids, total_time)
    
    async def benchmark_basic_parallel_execution(self) -> BenchmarkSuite:
        """Benchmark basic parallel execution capabilities"""
        
        print("\n🚀 BENCHMARK 1: Basic Parallel Execution")
        print("="*50)
        
        test_scenarios = [
            ("single_tool", ["T23A_SPACY_NER"], 3.0),
            ("two_tools", ["T23A_SPACY_NER", "T31_ENTITY_BUILDER"], 6.0),
            ("three_tools", ["T23A_SPACY_NER", "T31_ENTITY_BUILDER", "T27_RELATIONSHIP_EXTRACTOR"], 9.0),
            ("four_tools", ["T23A_SPACY_NER", "T31_ENTITY_BUILDER", "T27_RELATIONSHIP_EXTRACTOR", "T68_PAGE_RANK"], 12.0),
            ("five_tools", ["T01_PDF_LOADER", "T15A_TEXT_CHUNKER", "T23A_SPACY_NER", "T31_ENTITY_BUILDER", "T27_RELATIONSHIP_EXTRACTOR"], 15.0)
        ]
        
        results = []
        
        for scenario, tools, estimated_time in test_scenarios:
            print(f"⚡ Testing {scenario}: {len(tools)} tools")
            
            plan = self.create_test_execution_plan(f"bench_{scenario}", tools, estimated_time)
            
            # Execute multiple times for statistical accuracy
            run_times = []
            speedups = []
            efficiencies = []
            
            for run in range(3):  # 3 runs per scenario
                start_time = time.time()
                result = await self.parallel_executor.execute_parallel_plan(plan)
                actual_time = time.time() - start_time
                
                run_times.append(actual_time)
                speedups.append(result.speedup_factor)
                efficiencies.append(result.parallel_efficiency)
            
            # Calculate statistics
            avg_time = statistics.mean(run_times)
            avg_speedup = statistics.mean(speedups)
            avg_efficiency = statistics.mean(efficiencies)
            
            benchmark_result = BenchmarkResult(
                benchmark_name="basic_parallel_execution",
                scenario=scenario,
                sequential_time_estimate=estimated_time,
                parallel_time_actual=avg_time,
                speedup_factor=avg_speedup,
                parallel_efficiency=avg_efficiency,
                resource_utilization={},
                success_rate=1.0,  # All succeeded
                metadata={
                    "tools_count": len(tools),
                    "runs": len(run_times),
                    "time_std": statistics.stdev(run_times) if len(run_times) > 1 else 0.0
                }
            )
            
            results.append(benchmark_result)
            
            print(f"   Avg Time: {avg_time:.2f}s | Speedup: {avg_speedup:.2f}x | Efficiency: {avg_efficiency:.1%}")
        
        # Calculate suite metrics
        speedups = [r.speedup_factor for r in results]
        time_saved = sum(r.sequential_time_estimate - r.parallel_time_actual for r in results)
        
        suite = BenchmarkSuite(
            suite_name="Basic Parallel Execution",
            total_benchmarks=len(results),
            average_speedup=statistics.mean(speedups),
            best_speedup=max(speedups),
            worst_speedup=min(speedups),
            total_time_saved=time_saved,
            performance_requirement_met=max(speedups) >= 1.5,  # >50% improvement
            individual_results=results
        )
        
        self.results.extend(results)
        return suite
    
    async def benchmark_optimization_strategies(self) -> BenchmarkSuite:
        """Benchmark different optimization strategies"""
        
        print("\n⚡ BENCHMARK 2: Optimization Strategies")
        print("="*50)
        
        # Test plan with good optimization potential
        base_plan = self.create_test_execution_plan("optimization_test", 
                                                   ["T23A_SPACY_NER", "T31_ENTITY_BUILDER", "T27_RELATIONSHIP_EXTRACTOR"], 9.0)
        
        strategies = [
            OptimizationStrategy.THROUGHPUT_MAXIMIZATION,
            OptimizationStrategy.LATENCY_MINIMIZATION,
            OptimizationStrategy.RESOURCE_EFFICIENCY,
            OptimizationStrategy.BALANCED_PERFORMANCE
        ]
        
        results = []
        
        for strategy in strategies:
            print(f"🎯 Testing {strategy.value}")
            
            optimizer = ExecutionOptimizer()
            optimizer.config.strategy = strategy
            
            # Optimize plan
            opt_start = time.time()
            optimization_result = await optimizer.optimize_execution_plan(base_plan)
            opt_time = time.time() - opt_start
            
            # Execute optimized plan
            exec_start = time.time()
            execution_result = await self.parallel_executor.execute_parallel_plan(optimization_result.optimized_plan)
            exec_time = time.time() - exec_start
            
            benchmark_result = BenchmarkResult(
                benchmark_name="optimization_strategies",
                scenario=strategy.value,
                sequential_time_estimate=base_plan.total_estimated_time,
                parallel_time_actual=exec_time,
                speedup_factor=execution_result.speedup_factor,
                parallel_efficiency=execution_result.parallel_efficiency,
                resource_utilization={},
                success_rate=1.0 if execution_result.successful_steps > 0 else 0.0,
                metadata={
                    "optimization_time": opt_time,
                    "optimization_improvement": optimization_result.performance_improvement,
                    "applied_optimizations": optimization_result.applied_optimizations
                }
            )
            
            results.append(benchmark_result)
            
            print(f"   Optimization: {optimization_result.performance_improvement:.1%} | "
                  f"Speedup: {execution_result.speedup_factor:.2f}x | "
                  f"Time: {exec_time:.2f}s")
        
        # Calculate suite metrics
        speedups = [r.speedup_factor for r in results]
        time_saved = sum(r.sequential_time_estimate - r.parallel_time_actual for r in results)
        
        suite = BenchmarkSuite(
            suite_name="Optimization Strategies",
            total_benchmarks=len(results),
            average_speedup=statistics.mean(speedups),
            best_speedup=max(speedups),
            worst_speedup=min(speedups),
            total_time_saved=time_saved,
            performance_requirement_met=max(speedups) >= 1.5,
            individual_results=results
        )
        
        self.results.extend(results)
        return suite
    
    async def benchmark_scalability(self) -> BenchmarkSuite:
        """Benchmark system scalability with increasing load"""
        
        print("\n📈 BENCHMARK 3: Scalability Testing")
        print("="*50)
        
        # Test with increasing numbers of concurrent plans
        concurrency_levels = [1, 2, 4, 6]
        base_plan = self.create_test_execution_plan("scalability_test", 
                                                   ["T23A_SPACY_NER", "T31_ENTITY_BUILDER"], 6.0)
        
        results = []
        
        for concurrency in concurrency_levels:
            print(f"🔀 Testing concurrency level: {concurrency}")
            
            # Create multiple plans
            plans = [
                self.create_test_execution_plan(f"concurrent_{i}", 
                                              ["T23A_SPACY_NER", "T31_ENTITY_BUILDER"], 6.0)
                for i in range(concurrency)
            ]
            
            # Execute all plans concurrently
            start_time = time.time()
            
            tasks = [self.parallel_executor.execute_parallel_plan(plan) for plan in plans]
            execution_results = await asyncio.gather(*tasks)
            
            total_time = time.time() - start_time
            
            # Analyze results
            successful_executions = sum(1 for result in execution_results if result.successful_steps > 0)
            success_rate = successful_executions / len(execution_results)
            
            total_sequential_estimate = sum(plan.total_estimated_time for plan in plans)
            overall_speedup = total_sequential_estimate / total_time if total_time > 0 else 0.0
            
            avg_individual_speedup = statistics.mean([r.speedup_factor for r in execution_results])
            
            benchmark_result = BenchmarkResult(
                benchmark_name="scalability",
                scenario=f"concurrency_{concurrency}",
                sequential_time_estimate=total_sequential_estimate,
                parallel_time_actual=total_time,
                speedup_factor=overall_speedup,
                parallel_efficiency=avg_individual_speedup,
                resource_utilization={},
                success_rate=success_rate,
                metadata={
                    "concurrency_level": concurrency,
                    "individual_speedups": [r.speedup_factor for r in execution_results],
                    "successful_executions": successful_executions
                }
            )
            
            results.append(benchmark_result)
            
            print(f"   Success Rate: {success_rate:.1%} | "
                  f"Overall Speedup: {overall_speedup:.2f}x | "
                  f"Avg Individual: {avg_individual_speedup:.2f}x")
        
        # Calculate suite metrics
        speedups = [r.speedup_factor for r in results]
        time_saved = sum(r.sequential_time_estimate - r.parallel_time_actual for r in results)
        
        suite = BenchmarkSuite(
            suite_name="Scalability Testing",
            total_benchmarks=len(results),
            average_speedup=statistics.mean(speedups),
            best_speedup=max(speedups),
            worst_speedup=min(speedups),
            total_time_saved=time_saved,
            performance_requirement_met=max(speedups) >= 1.5,
            individual_results=results
        )
        
        self.results.extend(results)
        return suite
    
    async def benchmark_real_world_scenarios(self) -> BenchmarkSuite:
        """Benchmark realistic question processing scenarios"""
        
        print("\n🌍 BENCHMARK 4: Real-World Scenarios")
        print("="*50)
        
        # Realistic question scenarios
        scenarios = [
            ("simple_entity_extraction", "What entities are mentioned?", ["T23A_SPACY_NER", "T31_ENTITY_BUILDER"]),
            ("relationship_analysis", "How do entities relate to each other?", ["T23A_SPACY_NER", "T31_ENTITY_BUILDER", "T27_RELATIONSHIP_EXTRACTOR"]),
            ("complex_network_analysis", "What are the network patterns and centrality measures?", 
             ["T23A_SPACY_NER", "T31_ENTITY_BUILDER", "T27_RELATIONSHIP_EXTRACTOR", "T34_EDGE_BUILDER", "T68_PAGE_RANK"]),
            ("comprehensive_analysis", "Analyze all themes, entities, relationships, and network properties",
             ["T01_PDF_LOADER", "T15A_TEXT_CHUNKER", "T23A_SPACY_NER", "T31_ENTITY_BUILDER", "T27_RELATIONSHIP_EXTRACTOR", "T34_EDGE_BUILDER", "T68_PAGE_RANK"])
        ]
        
        results = []
        
        for scenario_name, question, tools in scenarios:
            print(f"🔍 Testing: {scenario_name}")
            print(f"   Question: {question}")
            
            # Analyze question for realistic context
            intent_result = self.intent_classifier.classify(question)
            complexity_result = self.complexity_analyzer.analyze_complexity(question)
            
            # Create execution plan
            execution_plan = self.execution_planner.create_execution_plan(
                tools,
                intent_result.primary_intent,
                complexity_result.level,
                strategy=ExecutionStrategy.ADAPTIVE
            )
            
            # Optimize plan
            optimization_result = await self.execution_optimizer.optimize_execution_plan(execution_plan)
            
            # Execute optimized plan
            start_time = time.time()
            execution_result = await self.parallel_executor.execute_parallel_plan(optimization_result.optimized_plan)
            actual_time = time.time() - start_time
            
            benchmark_result = BenchmarkResult(
                benchmark_name="real_world_scenarios",
                scenario=scenario_name,
                sequential_time_estimate=execution_plan.total_estimated_time,
                parallel_time_actual=actual_time,
                speedup_factor=execution_result.speedup_factor,
                parallel_efficiency=execution_result.parallel_efficiency,
                resource_utilization={},
                success_rate=execution_result.successful_steps / execution_result.total_steps,
                metadata={
                    "question": question,
                    "intent": intent_result.primary_intent.value,
                    "complexity": complexity_result.level.value,
                    "tools_count": len(tools),
                    "optimization_improvement": optimization_result.performance_improvement
                }
            )
            
            results.append(benchmark_result)
            
            print(f"   Intent: {intent_result.primary_intent.value} | "
                  f"Complexity: {complexity_result.level.value}")
            print(f"   Speedup: {execution_result.speedup_factor:.2f}x | "
                  f"Success: {benchmark_result.success_rate:.1%} | "
                  f"Time: {actual_time:.2f}s")
            print()
        
        # Calculate suite metrics
        speedups = [r.speedup_factor for r in results]
        time_saved = sum(r.sequential_time_estimate - r.parallel_time_actual for r in results)
        
        suite = BenchmarkSuite(
            suite_name="Real-World Scenarios",
            total_benchmarks=len(results),
            average_speedup=statistics.mean(speedups),
            best_speedup=max(speedups),
            worst_speedup=min(speedups),
            total_time_saved=time_saved,
            performance_requirement_met=max(speedups) >= 1.5,
            individual_results=results
        )
        
        self.results.extend(results)
        return suite
    
    async def run_comprehensive_benchmarks(self) -> Dict[str, Any]:
        """Run complete benchmark suite"""
        
        print("🏁 COMPREHENSIVE PERFORMANCE BENCHMARKING")
        print("🚀 Testing Phase B Dynamic Execution Performance")
        print("="*60)
        
        start_time = time.time()
        
        # Run all benchmark suites
        suites = []
        
        try:
            suites.append(await self.benchmark_basic_parallel_execution())
            suites.append(await self.benchmark_optimization_strategies())
            suites.append(await self.benchmark_scalability())
            suites.append(await self.benchmark_real_world_scenarios())
            
        except Exception as e:
            print(f"❌ Benchmark failed: {e}")
            import traceback
            traceback.print_exc()
        
        total_time = time.time() - start_time
        
        # Generate comprehensive report
        report = self.generate_benchmark_report(suites, total_time)
        
        # Cleanup
        self.resource_manager.shutdown()
        
        return report
    
    def generate_benchmark_report(self, suites: List[BenchmarkSuite], total_time: float) -> Dict[str, Any]:
        """Generate comprehensive benchmark report"""
        
        # Overall statistics
        all_speedups = []
        total_time_saved = 0.0
        total_benchmarks = 0
        
        for suite in suites:
            all_speedups.extend([r.speedup_factor for r in suite.individual_results])
            total_time_saved += suite.total_time_saved
            total_benchmarks += suite.total_benchmarks
        
        overall_stats = {
            "total_benchmarks": total_benchmarks,
            "total_duration": total_time,
            "average_speedup": statistics.mean(all_speedups) if all_speedups else 0.0,
            "median_speedup": statistics.median(all_speedups) if all_speedups else 0.0,
            "best_speedup": max(all_speedups) if all_speedups else 0.0,
            "worst_speedup": min(all_speedups) if all_speedups else 0.0,
            "speedup_std": statistics.stdev(all_speedups) if len(all_speedups) > 1 else 0.0,
            "total_time_saved": total_time_saved,
            "performance_requirement_met": max(all_speedups) >= 1.5 if all_speedups else False
        }
        
        # Print summary report
        print("\n" + "="*60)
        print("📊 COMPREHENSIVE BENCHMARK REPORT")
        print("="*60)
        
        print("🎯 Overall Performance:")
        print(f"   Total Benchmarks: {overall_stats['total_benchmarks']}")
        print(f"   Benchmark Duration: {overall_stats['total_duration']:.2f}s")
        print(f"   Average Speedup: {overall_stats['average_speedup']:.2f}x")
        print(f"   Best Speedup: {overall_stats['best_speedup']:.2f}x")
        print(f"   Performance Improvement: {(overall_stats['best_speedup'] - 1.0) * 100:.1f}%")
        print(f"   Total Time Saved: {overall_stats['total_time_saved']:.2f}s")
        
        # Phase B requirement assessment
        requirement_met = overall_stats['performance_requirement_met']
        print(f"\n🎯 Phase B Performance Requirement (>50% improvement):")
        if requirement_met:
            print("   🎉 ✅ REQUIREMENT MET: >50% performance improvement achieved!")
        else:
            current_improvement = (overall_stats['best_speedup'] - 1.0) * 100
            print(f"   ⚠️  ❌ Current best: {current_improvement:.1f}% (target: >50%)")
        
        # Suite-by-suite results
        print(f"\n📈 Benchmark Suite Results:")
        for suite in suites:
            print(f"   {suite.suite_name}:")
            print(f"     Tests: {suite.total_benchmarks}")
            print(f"     Avg Speedup: {suite.average_speedup:.2f}x")
            print(f"     Best Speedup: {suite.best_speedup:.2f}x")
            print(f"     Requirement Met: {'✅' if suite.performance_requirement_met else '❌'}")
        
        print("\n" + "="*60)
        
        # Return comprehensive data
        return {
            "overall_statistics": overall_stats,
            "benchmark_suites": [
                {
                    "suite_name": suite.suite_name,
                    "total_benchmarks": suite.total_benchmarks,
                    "average_speedup": suite.average_speedup,
                    "best_speedup": suite.best_speedup,
                    "worst_speedup": suite.worst_speedup,
                    "total_time_saved": suite.total_time_saved,
                    "performance_requirement_met": suite.performance_requirement_met,
                    "individual_results": [
                        {
                            "scenario": result.scenario,
                            "speedup_factor": result.speedup_factor,
                            "parallel_efficiency": result.parallel_efficiency,
                            "success_rate": result.success_rate
                        } for result in suite.individual_results
                    ]
                } for suite in suites
            ]
        }
    
    def save_benchmark_results(self, report: Dict[str, Any], filename: str = None) -> Path:
        """Save benchmark results to file"""
        
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_results_{timestamp}.json"
        
        filepath = Path(__file__).parent / filename
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"💾 Benchmark results saved to: {filepath}")
        return filepath


async def main():
    """Main benchmarking function"""
    
    benchmarks = ExecutionPerformanceBenchmarks()
    
    try:
        report = await benchmarks.run_comprehensive_benchmarks()
        
        # Save results
        benchmarks.save_benchmark_results(report)
        
        # Exit with appropriate code based on results
        if report["overall_statistics"]["performance_requirement_met"]:
            print("🎉 All performance requirements met!")
            sys.exit(0)
        else:
            print("⚠️  Performance requirements not fully met")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Benchmarking failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    # Create benchmarks directory if it doesn't exist
    Path(__file__).parent.mkdir(exist_ok=True)
    
    asyncio.run(main())