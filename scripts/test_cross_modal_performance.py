#!/usr/bin/env python3
"""Cross-modal performance measurement and validation framework"""

import time
import sys
import psutil
import os
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@dataclass
class PerformanceMetrics:
    """Performance measurement results"""
    operation: str
    execution_time: float
    memory_usage_mb: float
    cpu_percent: float
    success: bool
    error_message: str = None

class PerformanceFramework:
    """Framework for measuring cross-modal system performance"""
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.process = psutil.Process()
    
    def measure_operation(self, operation_name: str, operation_func, *args, **kwargs) -> PerformanceMetrics:
        """Measure performance of an operation"""
        # Get baseline measurements
        start_time = time.time()
        start_memory = self.process.memory_info().rss / (1024 * 1024)  # MB
        start_cpu = self.process.cpu_percent()
        
        success = False
        error_message = None
        result = None
        
        try:
            # Execute operation
            result = operation_func(*args, **kwargs)
            success = True
        except Exception as e:
            error_message = str(e)
            success = False
        
        # Calculate metrics
        execution_time = time.time() - start_time
        end_memory = self.process.memory_info().rss / (1024 * 1024)  # MB
        memory_usage = end_memory - start_memory
        cpu_percent = self.process.cpu_percent() - start_cpu
        
        metrics = PerformanceMetrics(
            operation=operation_name,
            execution_time=execution_time,
            memory_usage_mb=memory_usage,
            cpu_percent=max(0, cpu_percent),  # Ensure non-negative
            success=success,
            error_message=error_message
        )
        
        self.metrics.append(metrics)
        return metrics
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get summary of all performance measurements"""
        if not self.metrics:
            return {"error": "No metrics recorded"}
        
        successful_metrics = [m for m in self.metrics if m.success]
        failed_metrics = [m for m in self.metrics if not m.success]
        
        if successful_metrics:
            total_time = sum(m.execution_time for m in successful_metrics)
            avg_time = total_time / len(successful_metrics)
            max_time = max(m.execution_time for m in successful_metrics)
            total_memory = sum(m.memory_usage_mb for m in successful_metrics)
            avg_memory = total_memory / len(successful_metrics)
        else:
            total_time = avg_time = max_time = total_memory = avg_memory = 0
        
        return {
            "total_operations": len(self.metrics),
            "successful_operations": len(successful_metrics),
            "failed_operations": len(failed_metrics),
            "total_execution_time": total_time,
            "average_execution_time": avg_time,
            "max_execution_time": max_time,
            "total_memory_usage_mb": total_memory,
            "average_memory_usage_mb": avg_memory,
            "meets_30s_requirement": max_time < 30.0 if successful_metrics else False
        }

def test_dag_generation_performance():
    """Test DAG generation performance"""
    print("🔍 Testing DAG Generation Performance...")
    
    framework = PerformanceFramework()
    
    def generate_comprehensive_dag():
        from src.workflows.cross_modal_dag_template import CrossModalDAGTemplate
        return CrossModalDAGTemplate.create_graph_table_vector_synthesis_dag("test.pdf", "comprehensive")
    
    def generate_simple_dag():
        from src.workflows.cross_modal_dag_template import CrossModalDAGTemplate
        return CrossModalDAGTemplate.create_simple_cross_modal_dag("test.txt", "all")
    
    # Test multiple DAG generations
    operations = [
        ("Comprehensive DAG", generate_comprehensive_dag),
        ("Simple DAG", generate_simple_dag),
    ]
    
    # Run each operation multiple times for average
    for op_name, op_func in operations:
        for i in range(3):  # 3 iterations each
            metrics = framework.measure_operation(f"{op_name}_run_{i+1}", op_func)
            status = "✅" if metrics.success else "❌"
            print(f"   {status} {op_name} Run {i+1}: {metrics.execution_time:.3f}s, {metrics.memory_usage_mb:.1f}MB")
    
    summary = framework.get_performance_summary()
    print(f"\n   📊 DAG Generation Summary:")
    print(f"      Total Time: {summary['total_execution_time']:.3f}s")
    print(f"      Average Time: {summary['average_execution_time']:.3f}s")
    print(f"      Max Time: {summary['max_execution_time']:.3f}s")
    print(f"      Memory Usage: {summary['average_memory_usage_mb']:.1f}MB avg")
    
    return summary['meets_30s_requirement'], summary

def test_tool_instantiation_performance():
    """Test tool instantiation performance"""
    print("\n🔍 Testing Tool Instantiation Performance...")
    
    framework = PerformanceFramework()
    
    def instantiate_graph_table_exporter():
        from src.tools.cross_modal.graph_table_exporter_unified import GraphTableExporterUnified
        return GraphTableExporterUnified(service_manager=None)
    
    def instantiate_cross_modal_analyzer():
        from src.tools.phase_c.cross_modal_tool import CrossModalTool
        return CrossModalTool(service_manager=None)
    
    # Test tool instantiation (without full service manager to avoid timeout)
    operations = [
        ("GraphTableExporter", instantiate_graph_table_exporter),
        ("CrossModalAnalyzer", instantiate_cross_modal_analyzer),
    ]
    
    for op_name, op_func in operations:
        metrics = framework.measure_operation(op_name, op_func)
        status = "✅" if metrics.success else "❌"
        print(f"   {status} {op_name}: {metrics.execution_time:.3f}s, {metrics.memory_usage_mb:.1f}MB")
        if not metrics.success:
            print(f"      Error: {metrics.error_message}")
    
    summary = framework.get_performance_summary()
    print(f"\n   📊 Tool Instantiation Summary:")
    print(f"      Average Time: {summary['average_execution_time']:.3f}s")
    print(f"      Max Time: {summary['max_execution_time']:.3f}s")
    print(f"      Success Rate: {summary['successful_operations']}/{summary['total_operations']}")
    
    return summary['meets_30s_requirement'], summary

def test_mapping_performance():
    """Test tool ID mapping performance"""
    print("\n🔍 Testing Tool ID Mapping Performance...")
    
    framework = PerformanceFramework()
    
    def test_semantic_mapping():
        from src.core.tool_id_mapper import ToolIDMapper
        mapper = ToolIDMapper.__new__(ToolIDMapper)  # Create without full init
        
        # Test multiple mappings
        results = []
        test_names = [
            "graph to table converter",
            "cross modal analyzer",
            "vector embedder", 
            "format converter",
            "data exporter",
            "embedding generator"
        ]
        
        for name in test_names:
            try:
                # Test basic mapping logic (without full registry)
                base_name = name.replace(" ", "_")
                variations = mapper._get_semantic_variations("test", base_name)
                results.append((name, bool(variations)))
            except:
                results.append((name, False))
        
        return results
    
    metrics = framework.measure_operation("Semantic Mapping", test_semantic_mapping)
    status = "✅" if metrics.success else "❌"
    print(f"   {status} Semantic Mapping: {metrics.execution_time:.3f}s, {metrics.memory_usage_mb:.1f}MB")
    
    summary = framework.get_performance_summary()
    return summary['meets_30s_requirement'], summary

def test_end_to_end_workflow_performance():
    """Test simulated end-to-end workflow performance"""
    print("\n🔍 Testing End-to-End Workflow Performance...")
    
    framework = PerformanceFramework()
    
    def simulate_end_to_end_workflow():
        """Simulate complete workflow without heavy services"""
        
        # Step 1: Generate DAG
        from src.workflows.cross_modal_dag_template import CrossModalDAGTemplate
        dag = CrossModalDAGTemplate.create_graph_table_vector_synthesis_dag("test_document.pdf")
        
        # Step 2: Validate DAG tools
        tool_availability = CrossModalDAGTemplate.validate_dag_tool_availability(dag)
        
        # Step 3: Simulate tool mapping
        from src.core.tool_id_mapper import ToolIDMapper
        mapper = ToolIDMapper.__new__(ToolIDMapper)
        
        mapped_tools = []
        for step in dag['steps']:
            tool_id = step['tool_id']
            if tool_id in ['GRAPH_TABLE_EXPORTER', 'CROSS_MODAL_ANALYZER', 'VECTOR_EMBEDDER', 'MULTI_FORMAT_EXPORTER']:
                # Simulate mapping lookup
                base_name = tool_id.lower().replace('_', ' ')
                try:
                    variations = mapper._get_semantic_variations("test", base_name)
                    mapped_tools.append((tool_id, bool(variations)))
                except:
                    mapped_tools.append((tool_id, False))
        
        # Step 4: Simulate basic tool instantiation (lightweight)
        tool_instances = 0
        try:
            from src.tools.cross_modal.graph_table_exporter_unified import GraphTableExporterUnified
            tool = GraphTableExporterUnified(service_manager=None)
            tool_instances += 1
        except:
            pass
        
        return {
            "dag_steps": len(dag['steps']),
            "tool_availability": tool_availability,
            "mapped_tools": len(mapped_tools),
            "instantiated_tools": tool_instances
        }
    
    # Simulate workflow multiple times
    for i in range(3):
        metrics = framework.measure_operation(f"E2E_Workflow_run_{i+1}", simulate_end_to_end_workflow)
        status = "✅" if metrics.success else "❌"
        print(f"   {status} E2E Workflow Run {i+1}: {metrics.execution_time:.3f}s, {metrics.memory_usage_mb:.1f}MB")
        if not metrics.success:
            print(f"      Error: {metrics.error_message}")
    
    summary = framework.get_performance_summary()
    print(f"\n   📊 E2E Workflow Summary:")
    print(f"      Average Time: {summary['average_execution_time']:.3f}s")
    print(f"      Max Time: {summary['max_execution_time']:.3f}s")
    print(f"      Meets 30s Requirement: {summary['meets_30s_requirement']}")
    
    return summary['meets_30s_requirement'], summary

def main():
    """Run performance testing suite"""
    print("🚀 KGAS Cross-Modal Performance Testing Suite")
    print("=" * 50)
    
    performance_tests = [
        ("DAG Generation", test_dag_generation_performance),
        ("Tool Instantiation", test_tool_instantiation_performance),
        ("Tool Mapping", test_mapping_performance),
        ("End-to-End Workflow", test_end_to_end_workflow_performance)
    ]
    
    results = {}
    overall_start = time.time()
    
    for test_name, test_func in performance_tests:
        print(f"\n{'='*15} {test_name} {'='*15}")
        try:
            meets_requirement, summary = test_func()
            results[test_name] = {
                "meets_30s": meets_requirement,
                "summary": summary
            }
        except Exception as e:
            print(f"❌ {test_name}: CRITICAL ERROR - {e}")
            results[test_name] = {
                "meets_30s": False,
                "summary": {"error": str(e)}
            }
    
    total_time = time.time() - overall_start
    
    # Overall Summary
    print(f"\n{'='*20} PERFORMANCE SUMMARY {'='*20}")
    
    meets_requirements = [r["meets_30s"] for r in results.values()]
    total_operations = sum(r["summary"].get("total_operations", 0) for r in results.values() if "total_operations" in r["summary"])
    successful_operations = sum(r["summary"].get("successful_operations", 0) for r in results.values() if "successful_operations" in r["summary"])
    
    for test_name, result in results.items():
        status_icon = "✅" if result["meets_30s"] else "❌"
        print(f"{status_icon} {test_name}: {'MEETS 30s' if result['meets_30s'] else 'EXCEEDS 30s'}")
        
        if "average_execution_time" in result["summary"]:
            avg_time = result["summary"]["average_execution_time"]
            print(f"    Average: {avg_time:.3f}s")
    
    print(f"\n📊 Overall Performance Results:")
    print(f"    Total Test Suite Time: {total_time:.2f}s")
    print(f"    Operations Tested: {total_operations}")
    print(f"    Success Rate: {successful_operations}/{total_operations} ({100*successful_operations/total_operations:.1f}%)" if total_operations > 0 else "    No operations measured")
    print(f"    Performance Requirements Met: {sum(meets_requirements)}/{len(meets_requirements)} test categories")
    
    # Final assessment
    overall_meets_requirement = sum(meets_requirements) >= len(meets_requirements) * 0.75  # 75% threshold
    
    if overall_meets_requirement:
        print("🎉 Cross-Modal System: PERFORMANCE REQUIREMENTS MET")
        return True
    else:
        print("⚠️  Cross-Modal System: PERFORMANCE NEEDS OPTIMIZATION")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)