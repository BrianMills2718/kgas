#!/usr/bin/env python3
"""
Performance Benchmark and Memory Profiling for KGAS System.

Tests the actual performance characteristics of the orchestration system
to identify real bottlenecks and memory usage patterns.
"""

import asyncio
import time
import psutil
import logging
import sys
import os
import tracemalloc
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
import tempfile
import yaml

sys.path.insert(0, 'src')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Container for performance measurement data."""
    test_name: str
    execution_time: float
    memory_peak_mb: float
    memory_delta_mb: float
    cpu_percent: float
    task_throughput: float
    errors: List[str]
    memory_trace: Dict[str, Any]

class PerformanceBenchmark:
    """Comprehensive performance and memory profiling for KGAS."""
    
    def __init__(self):
        self.process = psutil.Process()
        self.results: List[PerformanceMetrics] = []
        
    async def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """Run comprehensive performance and memory benchmarks."""
        logger.info("🚀 Starting comprehensive performance and memory benchmark")
        
        # Enable memory tracing
        tracemalloc.start()
        
        try:
            # Benchmark different scenarios
            await self._benchmark_resource_pool_performance()
            await self._benchmark_reasoning_agent_performance()
            await self._benchmark_orchestrator_initialization()
            await self._benchmark_memory_patterns()
            
            # Generate summary report
            return self._generate_performance_report()
            
        finally:
            tracemalloc.stop()
    
    async def _benchmark_resource_pool_performance(self):
        """Benchmark ResourcePool allocation/deallocation performance."""
        logger.info("📊 Benchmarking ResourcePool performance...")
        
        from orchestration.parallel_orchestrator import ResourcePool
        
        # Start monitoring
        tracemalloc.start()
        start_memory = self.process.memory_info().rss / 1024 / 1024
        start_time = time.time()
        cpu_start = self.process.cpu_percent()
        
        errors = []
        operations_completed = 0
        
        try:
            # Create resource pool
            pool = ResourcePool(
                max_concurrent_agents=10,
                max_memory_mb=4096,
                max_reasoning_threads=5
            )
            
            # Stress test allocation/deallocation
            for iteration in range(1000):
                requirements = {
                    "agents": 1 + (iteration % 3),
                    "memory_mb": 256 + (iteration % 512),
                    "reasoning_threads": iteration % 2
                }
                
                # Allocate
                if pool.allocate(requirements):
                    operations_completed += 1
                    # Immediate release
                    pool.release(requirements)
                else:
                    # Reset pool if it gets full
                    pool = ResourcePool(
                        max_concurrent_agents=10,
                        max_memory_mb=4096,
                        max_reasoning_threads=5
                    )
                
                # Memory check every 100 iterations
                if iteration % 100 == 0:
                    current_memory = self.process.memory_info().rss / 1024 / 1024
                    if current_memory - start_memory > 500:  # 500MB growth
                        errors.append(f"Excessive memory growth at iteration {iteration}: {current_memory - start_memory:.1f}MB")
        
        except Exception as e:
            errors.append(f"ResourcePool benchmark error: {str(e)}")
        
        # Calculate metrics
        end_time = time.time()
        end_memory = self.process.memory_info().rss / 1024 / 1024
        cpu_end = self.process.cpu_percent()
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        self.results.append(PerformanceMetrics(
            test_name="ResourcePool Stress Test",
            execution_time=end_time - start_time,
            memory_peak_mb=peak / 1024 / 1024,
            memory_delta_mb=end_memory - start_memory,
            cpu_percent=cpu_end - cpu_start,
            task_throughput=operations_completed / (end_time - start_time),
            errors=errors,
            memory_trace={"current_mb": current / 1024 / 1024, "peak_mb": peak / 1024 / 1024}
        ))
        
        logger.info(f"✅ ResourcePool: {operations_completed} ops in {end_time - start_time:.2f}s ({operations_completed/(end_time - start_time):.1f} ops/sec)")
    
    async def _benchmark_reasoning_agent_performance(self):
        """Benchmark ReasoningAgent task validation performance."""
        logger.info("📊 Benchmarking ReasoningAgent performance...")
        
        from orchestration.reasoning_agent import ReasoningAgent
        from orchestration.base import Task, TaskPriority
        
        tracemalloc.start()
        start_memory = self.process.memory_info().rss / 1024 / 1024
        start_time = time.time()
        
        errors = []
        validations_completed = 0
        
        try:
            # Create reasoning agent
            agent = ReasoningAgent(
                agent_id="benchmark_agent",
                reasoning_config={
                    "enable_reasoning": True,
                    "reasoning_threshold": 0.5,
                    "max_reasoning_time": 1.0
                }
            )
            
            # Create variety of tasks for validation
            task_templates = [
                {"task_type": "analysis", "params_size": 5},
                {"task_type": "document_processing", "params_size": 10},
                {"task_type": "graph_building", "params_size": 20},
                {"task_type": "insight_generation", "params_size": 50}
            ]
            
            # Stress test task validation
            for iteration in range(5000):
                template = task_templates[iteration % len(task_templates)]
                
                # Create task with varying complexity
                parameters = {f"param_{i}": f"value_{i}_{iteration}" for i in range(template["params_size"])}
                
                task = Task(
                    task_id=f"benchmark_task_{iteration}",
                    task_type=template["task_type"],
                    parameters=parameters,
                    priority=TaskPriority.MEDIUM
                )
                
                # Validate task (this tests our improvements)
                if agent._validate_task(task):
                    validations_completed += 1
                
                # Test invalid tasks occasionally
                if iteration % 100 == 0:
                    invalid_task = Task(task_id="", task_type="", parameters={}, priority=TaskPriority.LOW)
                    agent._validate_task(invalid_task)  # Should return False
        
        except Exception as e:
            errors.append(f"ReasoningAgent benchmark error: {str(e)}")
        
        # Calculate metrics
        end_time = time.time()
        end_memory = self.process.memory_info().rss / 1024 / 1024
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        self.results.append(PerformanceMetrics(
            test_name="ReasoningAgent Task Validation",
            execution_time=end_time - start_time,
            memory_peak_mb=peak / 1024 / 1024,
            memory_delta_mb=end_memory - start_memory,
            cpu_percent=0,  # Not measuring CPU for this test
            task_throughput=validations_completed / (end_time - start_time),
            errors=errors,
            memory_trace={"current_mb": current / 1024 / 1024, "peak_mb": peak / 1024 / 1024}
        ))
        
        logger.info(f"✅ ReasoningAgent: {validations_completed} validations in {end_time - start_time:.2f}s ({validations_completed/(end_time - start_time):.1f} validations/sec)")
    
    async def _benchmark_orchestrator_initialization(self):
        """Benchmark orchestrator initialization and cleanup performance."""
        logger.info("📊 Benchmarking ParallelOrchestrator initialization...")
        
        from orchestration.parallel_orchestrator import ParallelOrchestrator
        
        tracemalloc.start()
        start_memory = self.process.memory_info().rss / 1024 / 1024
        start_time = time.time()
        
        errors = []
        initializations_completed = 0
        
        # Create temporary config
        temp_dir = tempfile.mkdtemp()
        config_path = os.path.join(temp_dir, "benchmark_config.yaml")
        
        config = {
            "parallel": {
                "execution_mode": "parallel",
                "max_parallel_tasks": 5,
                "batch_size": 3,
                "resources": {
                    "max_concurrent_agents": 5,
                    "max_memory_mb": 1024,
                    "max_reasoning_threads": 2
                }
            }
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(config, f)
        
        try:
            # Stress test initialization/cleanup cycles
            for iteration in range(50):  # Fewer iterations for heavy operations
                try:
                    orchestrator = ParallelOrchestrator(config_path)
                    
                    # Test initialization
                    success = await orchestrator.initialize()
                    if success:
                        initializations_completed += 1
                        # Test status retrieval
                        status = orchestrator.get_status()
                        # Test cleanup
                        await orchestrator.cleanup()
                    
                except Exception as e:
                    errors.append(f"Iteration {iteration}: {str(e)}")
        
        except Exception as e:
            errors.append(f"Orchestrator benchmark error: {str(e)}")
        
        # Calculate metrics
        end_time = time.time()
        end_memory = self.process.memory_info().rss / 1024 / 1024
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        self.results.append(PerformanceMetrics(
            test_name="ParallelOrchestrator Init/Cleanup",
            execution_time=end_time - start_time,
            memory_peak_mb=peak / 1024 / 1024,
            memory_delta_mb=end_memory - start_memory,
            cpu_percent=0,
            task_throughput=initializations_completed / (end_time - start_time),
            errors=errors,
            memory_trace={"current_mb": current / 1024 / 1024, "peak_mb": peak / 1024 / 1024}
        ))
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        logger.info(f"✅ Orchestrator: {initializations_completed} init/cleanup cycles in {end_time - start_time:.2f}s")
    
    async def _benchmark_memory_patterns(self):
        """Analyze memory usage patterns and potential leaks."""
        logger.info("📊 Analyzing memory usage patterns...")
        
        tracemalloc.start()
        start_memory = self.process.memory_info().rss / 1024 / 1024
        start_time = time.time()
        
        memory_samples = []
        errors = []
        
        try:
            # Sample memory usage during various operations
            for phase in range(10):
                phase_start_memory = self.process.memory_info().rss / 1024 / 1024
                
                # Simulate typical workload
                from orchestration.parallel_orchestrator import ResourcePool
                from orchestration.reasoning_agent import ReasoningAgent
                from orchestration.base import Task, TaskPriority
                
                # Create and use components
                pools = []
                agents = []
                tasks = []
                
                for i in range(20):
                    # Create resource pools
                    pool = ResourcePool(max_concurrent_agents=5, max_memory_mb=1024, max_reasoning_threads=2)
                    pools.append(pool)
                    
                    # Create agents
                    agent = ReasoningAgent(agent_id=f"agent_{i}", reasoning_config={"enable_reasoning": True})
                    agents.append(agent)
                    
                    # Create tasks
                    task = Task(
                        task_id=f"task_{i}",
                        task_type="analysis",
                        parameters={"data": f"benchmark_data_{i}" * 100},  # Some data
                        priority=TaskPriority.MEDIUM
                    )
                    tasks.append(task)
                
                phase_end_memory = self.process.memory_info().rss / 1024 / 1024
                
                memory_samples.append({
                    "phase": phase,
                    "start_memory_mb": phase_start_memory,
                    "end_memory_mb": phase_end_memory,
                    "delta_mb": phase_end_memory - phase_start_memory,
                    "objects_created": len(pools) + len(agents) + len(tasks)
                })
                
                # Force garbage collection periodically
                import gc
                if phase % 3 == 0:
                    gc.collect()
                
                # Clear references
                del pools, agents, tasks
        
        except Exception as e:
            errors.append(f"Memory pattern analysis error: {str(e)}")
        
        # Calculate metrics
        end_time = time.time()
        end_memory = self.process.memory_info().rss / 1024 / 1024
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        self.results.append(PerformanceMetrics(
            test_name="Memory Usage Patterns",
            execution_time=end_time - start_time,
            memory_peak_mb=peak / 1024 / 1024,
            memory_delta_mb=end_memory - start_memory,
            cpu_percent=0,
            task_throughput=len(memory_samples) / (end_time - start_time),
            errors=errors,
            memory_trace={
                "current_mb": current / 1024 / 1024,
                "peak_mb": peak / 1024 / 1024,
                "samples": memory_samples
            }
        ))
        
        logger.info(f"✅ Memory patterns: {len(memory_samples)} phases analyzed")
    
    def _generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance analysis report."""
        logger.info("📋 Generating performance analysis report...")
        
        # System information
        system_info = {
            "cpu_count": psutil.cpu_count(),
            "memory_total_mb": psutil.virtual_memory().total / 1024 / 1024,
            "memory_available_mb": psutil.virtual_memory().available / 1024 / 1024,
            "python_version": sys.version,
            "platform": sys.platform
        }
        
        # Analyze results
        performance_summary = {
            "system_info": system_info,
            "benchmark_timestamp": datetime.now().isoformat(),
            "total_tests": len(self.results),
            "test_results": []
        }
        
        total_errors = 0
        peak_memory_usage = 0
        
        for result in self.results:
            total_errors += len(result.errors)
            peak_memory_usage = max(peak_memory_usage, result.memory_peak_mb)
            
            test_summary = {
                "test_name": result.test_name,
                "execution_time_seconds": round(result.execution_time, 3),
                "memory_peak_mb": round(result.memory_peak_mb, 2),
                "memory_delta_mb": round(result.memory_delta_mb, 2),
                "throughput": round(result.task_throughput, 1),
                "error_count": len(result.errors),
                "errors": result.errors[:5],  # First 5 errors only
                "performance_rating": self._rate_performance(result)
            }
            
            performance_summary["test_results"].append(test_summary)
        
        # Overall assessment
        performance_summary["overall_assessment"] = {
            "total_errors": total_errors,
            "peak_memory_usage_mb": round(peak_memory_usage, 2),
            "memory_efficiency": self._assess_memory_efficiency(),
            "performance_bottlenecks": self._identify_bottlenecks(),
            "recommendations": self._generate_recommendations()
        }
        
        return performance_summary
    
    def _rate_performance(self, result: PerformanceMetrics) -> str:
        """Rate performance of individual test."""
        # Simple heuristic-based rating
        if len(result.errors) > 0:
            return "POOR"
        elif result.memory_delta_mb > 100:  # >100MB growth
            return "POOR"
        elif result.task_throughput < 10:  # <10 ops/sec
            return "FAIR"
        elif result.task_throughput > 100:  # >100 ops/sec
            return "EXCELLENT"
        else:
            return "GOOD"
    
    def _assess_memory_efficiency(self) -> str:
        """Assess overall memory efficiency."""
        total_memory_growth = sum(r.memory_delta_mb for r in self.results)
        peak_usage = max(r.memory_peak_mb for r in self.results)
        
        if total_memory_growth > 500 or peak_usage > 1000:
            return "POOR - Excessive memory usage detected"
        elif total_memory_growth > 200 or peak_usage > 500:
            return "FAIR - Moderate memory usage"
        else:
            return "GOOD - Efficient memory usage"
    
    def _identify_bottlenecks(self) -> List[str]:
        """Identify performance bottlenecks."""
        bottlenecks = []
        
        for result in self.results:
            if result.task_throughput < 50 and "Init/Cleanup" not in result.test_name:
                bottlenecks.append(f"{result.test_name}: Low throughput ({result.task_throughput:.1f} ops/sec)")
            
            if result.memory_delta_mb > 100:
                bottlenecks.append(f"{result.test_name}: High memory growth ({result.memory_delta_mb:.1f}MB)")
            
            if result.execution_time > 10:
                bottlenecks.append(f"{result.test_name}: Slow execution ({result.execution_time:.1f}s)")
            
            if len(result.errors) > 5:
                bottlenecks.append(f"{result.test_name}: High error rate ({len(result.errors)} errors)")
        
        return bottlenecks
    
    def _generate_recommendations(self) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []
        
        # Analyze patterns
        memory_issues = any(r.memory_delta_mb > 100 for r in self.results)
        throughput_issues = any(r.task_throughput < 50 for r in self.results if "Init/Cleanup" not in r.test_name)
        error_issues = any(len(r.errors) > 0 for r in self.results)
        
        if memory_issues:
            recommendations.append("Consider implementing object pooling for frequently created/destroyed components")
            recommendations.append("Review ResourcePool and ReasoningAgent for potential memory leaks")
            recommendations.append("Add memory monitoring to production deployment")
        
        if throughput_issues:
            recommendations.append("Profile task validation logic for optimization opportunities")
            recommendations.append("Consider caching validation results for similar tasks")
            recommendations.append("Evaluate async/await usage for potential improvements")
        
        if error_issues:
            recommendations.append("Review error handling and add more graceful degradation")
            recommendations.append("Add input validation at component boundaries")
            recommendations.append("Implement circuit breaker pattern for failing operations")
        
        if not memory_issues and not throughput_issues and not error_issues:
            recommendations.append("Performance is good - focus on production monitoring and gradual optimization")
            recommendations.append("Consider load testing with realistic workloads")
            recommendations.append("Monitor performance under concurrent usage")
        
        return recommendations

async def main():
    """Run comprehensive performance benchmark."""
    logger.info("🚀 Starting KGAS Performance and Memory Benchmark")
    
    benchmark = PerformanceBenchmark()
    
    try:
        # Run benchmark
        report = await benchmark.run_comprehensive_benchmark()
        
        # Save report
        report_file = f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        import json
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        logger.info("📊 PERFORMANCE BENCHMARK COMPLETE")
        logger.info(f"📄 Full report saved to: {report_file}")
        
        print("\n" + "="*60)
        print("PERFORMANCE BENCHMARK SUMMARY")
        print("="*60)
        
        for test_result in report["test_results"]:
            print(f"\n{test_result['test_name']}:")
            print(f"  Performance: {test_result['performance_rating']}")
            print(f"  Execution Time: {test_result['execution_time_seconds']}s")
            print(f"  Memory Peak: {test_result['memory_peak_mb']}MB")
            print(f"  Throughput: {test_result['throughput']} ops/sec")
            if test_result['error_count'] > 0:
                print(f"  Errors: {test_result['error_count']}")
        
        print(f"\nOVERALL ASSESSMENT:")
        assessment = report["overall_assessment"]
        print(f"  Memory Efficiency: {assessment['memory_efficiency']}")
        print(f"  Peak Memory Usage: {assessment['peak_memory_usage_mb']}MB")
        print(f"  Total Errors: {assessment['total_errors']}")
        
        if assessment['performance_bottlenecks']:
            print(f"\nBOTTLENECKS IDENTIFIED:")
            for bottleneck in assessment['performance_bottlenecks']:
                print(f"  - {bottleneck}")
        
        print(f"\nRECOMMENDATIONS:")
        for rec in assessment['recommendations']:
            print(f"  - {rec}")
        
        return report
        
    except Exception as e:
        logger.error(f"Benchmark failed: {e}")
        raise

if __name__ == "__main__":
    report = asyncio.run(main())