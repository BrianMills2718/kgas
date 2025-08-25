#!/usr/bin/env python3
"""
Performance Benchmarking - Compare framework overhead vs direct calls

This benchmark measures:
1. Framework overhead vs direct function calls
2. Chain execution performance
3. Validation overhead
4. Registry lookup costs
"""

import os
import sys
import time
import json
import tempfile
import statistics
from pathlib import Path
from typing import Dict, Any, List, Tuple
import hashlib

# Add poc to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from poc.registry import ToolRegistry
from poc.tools.text_loader import TextLoader, TextLoaderConfig
from poc.tools.entity_extractor import EntityExtractor, EntityExtractorConfig
from poc.tools.graph_builder import GraphBuilder, GraphBuilderConfig
from poc.data_types import DataType, DataSchema


class PerformanceBenchmark:
    """Benchmark framework performance"""
    
    def __init__(self, iterations: int = 100):
        self.iterations = iterations
        self.results = {}
    
    def time_function(self, func, *args, **kwargs) -> Tuple[Any, float]:
        """Time a function execution"""
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start
        return result, duration
    
    def benchmark_direct_calls(self, test_file: str) -> Dict[str, Any]:
        """Benchmark direct function calls without framework"""
        print("\n" + "="*80)
        print("BENCHMARK 1: Direct Function Calls (No Framework)")
        print("="*80)
        
        times = []
        
        for i in range(self.iterations):
            if i % 20 == 0:
                print(f"  Iteration {i}/{self.iterations}")
            
            start_total = time.perf_counter()
            
            # Direct file read
            with open(test_file, 'r') as f:
                content = f.read()
            
            # Direct checksum
            checksum = hashlib.sha256(content.encode()).hexdigest()
            
            # Direct entity extraction (simulate)
            # In real scenario, would call Gemini directly
            entities = [
                {"id": f"e{i}", "text": f"Entity_{i}", "type": "PERSON", "confidence": 0.9}
                for i in range(3)
            ]
            
            # Direct graph building (simulate)
            # In real scenario, would call Neo4j directly
            graph_id = f"graph_{checksum[:12]}"
            node_count = len(entities)
            edge_count = 0
            
            total_time = time.perf_counter() - start_total
            times.append(total_time)
        
        # Calculate statistics
        mean_time = statistics.mean(times)
        median_time = statistics.median(times)
        stdev_time = statistics.stdev(times) if len(times) > 1 else 0
        
        results = {
            "method": "direct",
            "iterations": self.iterations,
            "mean_ms": mean_time * 1000,
            "median_ms": median_time * 1000,
            "stdev_ms": stdev_time * 1000,
            "min_ms": min(times) * 1000,
            "max_ms": max(times) * 1000
        }
        
        print(f"\nResults:")
        print(f"  Mean:   {results['mean_ms']:.3f}ms")
        print(f"  Median: {results['median_ms']:.3f}ms")
        print(f"  StdDev: {results['stdev_ms']:.3f}ms")
        print(f"  Min:    {results['min_ms']:.3f}ms")
        print(f"  Max:    {results['max_ms']:.3f}ms")
        
        return results
    
    def benchmark_framework_calls(self, test_file: str) -> Dict[str, Any]:
        """Benchmark calls through the framework"""
        print("\n" + "="*80)
        print("BENCHMARK 2: Framework Calls (With Validation & Metrics)")
        print("="*80)
        
        # Initialize framework
        registry = ToolRegistry()
        text_loader = TextLoader()
        registry.register(text_loader)
        
        # Check if we have real services
        has_gemini = os.getenv("GEMINI_API_KEY") is not None
        has_neo4j = False
        
        if has_gemini:
            try:
                entity_extractor = EntityExtractor()
                registry.register(entity_extractor)
                
                graph_builder = GraphBuilder()
                registry.register(graph_builder)
                has_neo4j = True
            except:
                pass
        
        if has_gemini and has_neo4j:
            print("  Using: TextLoader → EntityExtractor → GraphBuilder")
            target_type = DataType.GRAPH
        elif has_gemini:
            print("  Using: TextLoader → EntityExtractor")
            target_type = DataType.ENTITIES
        else:
            print("  Using: TextLoader only")
            target_type = DataType.TEXT
        
        times = []
        
        for i in range(self.iterations):
            if i % 20 == 0:
                print(f"  Iteration {i}/{self.iterations}")
            
            start_total = time.perf_counter()
            
            # Create file data
            file_data = DataSchema.FileData(
                path=test_file,
                size_bytes=os.path.getsize(test_file),
                mime_type="text/plain"
            )
            
            # Find chain
            chains = registry.find_chains(DataType.FILE, target_type)
            if not chains:
                raise RuntimeError("No chain found")
            
            chain = chains[0]
            
            # Execute chain through framework
            current_data = file_data
            for tool_id in chain:
                tool = registry.tools[tool_id]
                result = tool.process(current_data)
                if not result.success:
                    raise RuntimeError(f"Tool {tool_id} failed: {result.error}")
                current_data = result.data
            
            total_time = time.perf_counter() - start_total
            times.append(total_time)
        
        # Calculate statistics
        mean_time = statistics.mean(times)
        median_time = statistics.median(times)
        stdev_time = statistics.stdev(times) if len(times) > 1 else 0
        
        results = {
            "method": "framework",
            "chain": " → ".join(chain),
            "iterations": self.iterations,
            "mean_ms": mean_time * 1000,
            "median_ms": median_time * 1000,
            "stdev_ms": stdev_time * 1000,
            "min_ms": min(times) * 1000,
            "max_ms": max(times) * 1000
        }
        
        print(f"\nResults:")
        print(f"  Mean:   {results['mean_ms']:.3f}ms")
        print(f"  Median: {results['median_ms']:.3f}ms")
        print(f"  StdDev: {results['stdev_ms']:.3f}ms")
        print(f"  Min:    {results['min_ms']:.3f}ms")
        print(f"  Max:    {results['max_ms']:.3f}ms")
        
        return results
    
    def benchmark_validation_overhead(self) -> Dict[str, Any]:
        """Benchmark Pydantic validation overhead"""
        print("\n" + "="*80)
        print("BENCHMARK 3: Validation Overhead")
        print("="*80)
        
        # Test data
        entity_data = {
            "id": "e1",
            "text": "John Smith",
            "type": "PERSON",
            "confidence": 0.95,
            "metadata": {"context": "CEO"}
        }
        
        # Benchmark dict access (no validation)
        times_dict = []
        for _ in range(10000):
            start = time.perf_counter()
            _ = entity_data["id"]
            _ = entity_data["text"]
            _ = entity_data["type"]
            _ = entity_data["confidence"]
            times_dict.append(time.perf_counter() - start)
        
        # Benchmark Pydantic validation
        times_pydantic = []
        for _ in range(10000):
            start = time.perf_counter()
            entity = DataSchema.Entity(**entity_data)
            _ = entity.id
            _ = entity.text
            _ = entity.type
            _ = entity.confidence
            times_pydantic.append(time.perf_counter() - start)
        
        mean_dict = statistics.mean(times_dict) * 1_000_000  # Convert to microseconds
        mean_pydantic = statistics.mean(times_pydantic) * 1_000_000
        overhead = ((mean_pydantic - mean_dict) / mean_dict) * 100
        
        results = {
            "dict_access_us": mean_dict,
            "pydantic_validation_us": mean_pydantic,
            "overhead_percent": overhead
        }
        
        print(f"\nResults (10,000 iterations):")
        print(f"  Dict access:        {results['dict_access_us']:.3f}μs")
        print(f"  Pydantic validation: {results['pydantic_validation_us']:.3f}μs")
        print(f"  Overhead:           {results['overhead_percent']:.1f}%")
        
        return results
    
    def benchmark_registry_operations(self) -> Dict[str, Any]:
        """Benchmark registry operations"""
        print("\n" + "="*80)
        print("BENCHMARK 4: Registry Operations")
        print("="*80)
        
        # Create registry with multiple tools
        registry = ToolRegistry()
        
        # Add multiple tools
        for i in range(10):
            tool = TextLoader()
            # Each tool gets unique ID automatically
            registry.register(tool)
        
        # Benchmark tool lookup
        tool_ids = list(registry.tools.keys())
        times_lookup = []
        
        for _ in range(10000):
            for tool_id in tool_ids:
                start = time.perf_counter()
                _ = registry.tools[tool_id]
                times_lookup.append(time.perf_counter() - start)
        
        # Benchmark chain discovery
        times_chain = []
        
        for _ in range(1000):
            start = time.perf_counter()
            _ = registry.find_chains(DataType.FILE, DataType.TEXT)
            times_chain.append(time.perf_counter() - start)
        
        # Benchmark compatibility checking
        times_compat = []
        
        # Add some tools with different types for compatibility testing
        entity_tool = EntityExtractor() if os.getenv("GEMINI_API_KEY") else None
        if entity_tool:
            registry.register(entity_tool)
        
        # Now check compatibility between different tool types
        text_tool_id = tool_ids[0] if tool_ids else None
        
        if text_tool_id and entity_tool:
            for _ in range(10000):
                start = time.perf_counter()
                _ = registry.can_connect(text_tool_id, entity_tool.tool_id)
                times_compat.append(time.perf_counter() - start)
        else:
            # Fallback: just check self-compatibility
            for _ in range(10000):
                if tool_ids:
                    start = time.perf_counter()
                    _ = registry.can_connect(tool_ids[0], tool_ids[0])
                    times_compat.append(time.perf_counter() - start)
        
        results = {
            "tool_lookup_us": statistics.mean(times_lookup) * 1_000_000 if times_lookup else 0,
            "chain_discovery_us": statistics.mean(times_chain) * 1_000_000 if times_chain else 0,
            "compatibility_check_us": statistics.mean(times_compat) * 1_000_000 if times_compat else 0
        }
        
        print(f"\nResults:")
        print(f"  Tool lookup:         {results['tool_lookup_us']:.3f}μs")
        print(f"  Chain discovery:     {results['chain_discovery_us']:.3f}μs")
        print(f"  Compatibility check: {results['compatibility_check_us']:.3f}μs")
        
        return results
    
    def calculate_overhead(self, direct_results: Dict, framework_results: Dict) -> Dict[str, Any]:
        """Calculate framework overhead"""
        print("\n" + "="*80)
        print("OVERHEAD ANALYSIS")
        print("="*80)
        
        overhead_mean = ((framework_results['mean_ms'] - direct_results['mean_ms']) 
                        / direct_results['mean_ms']) * 100
        overhead_median = ((framework_results['median_ms'] - direct_results['median_ms']) 
                          / direct_results['median_ms']) * 100
        
        results = {
            "direct_mean_ms": direct_results['mean_ms'],
            "framework_mean_ms": framework_results['mean_ms'],
            "overhead_mean_percent": overhead_mean,
            "overhead_median_percent": overhead_median,
            "absolute_overhead_ms": framework_results['mean_ms'] - direct_results['mean_ms']
        }
        
        print(f"\nFramework Overhead:")
        print(f"  Mean overhead:     {results['overhead_mean_percent']:.1f}%")
        print(f"  Median overhead:   {results['overhead_median_percent']:.1f}%")
        print(f"  Absolute overhead: {results['absolute_overhead_ms']:.3f}ms")
        
        # Determine if overhead is acceptable
        if overhead_mean < 20:
            print(f"\n✓ PASS: Overhead {overhead_mean:.1f}% is below 20% threshold")
        elif overhead_mean < 50:
            print(f"\n⚠️  WARNING: Overhead {overhead_mean:.1f}% is between 20-50%")
        else:
            print(f"\n✗ FAIL: Overhead {overhead_mean:.1f}% exceeds 50% threshold")
        
        return results


def main():
    """Run performance benchmarks"""
    print("\n" + "="*80)
    print("PERFORMANCE BENCHMARKING")
    print("="*80)
    
    # Create test file
    test_content = """
    Performance test document.
    John Smith is the CEO of TechCorp, located in San Francisco.
    The company develops AI products and has partnerships with BigData Inc.
    Alice Johnson, CTO, leads the engineering team of 50 developers.
    """
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_content)
        test_file = f.name
    
    try:
        # Initialize benchmark
        benchmark = PerformanceBenchmark(iterations=100)
        
        # Run benchmarks
        all_results = {}
        
        # 1. Direct calls
        direct_results = benchmark.benchmark_direct_calls(test_file)
        all_results['direct'] = direct_results
        
        # 2. Framework calls
        framework_results = benchmark.benchmark_framework_calls(test_file)
        all_results['framework'] = framework_results
        
        # 3. Validation overhead
        validation_results = benchmark.benchmark_validation_overhead()
        all_results['validation'] = validation_results
        
        # 4. Registry operations
        registry_results = benchmark.benchmark_registry_operations()
        all_results['registry'] = registry_results
        
        # 5. Calculate overhead
        overhead_results = benchmark.calculate_overhead(direct_results, framework_results)
        all_results['overhead'] = overhead_results
        
        # Save results
        results_file = "/tmp/poc_benchmark_results.json"
        with open(results_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        print("\n" + "="*80)
        print("BENCHMARKING COMPLETE")
        print("="*80)
        print(f"Results saved to: {results_file}")
        
        # Final summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        
        print("\nKey Metrics:")
        print(f"  Direct call:       {direct_results['mean_ms']:.3f}ms")
        print(f"  Framework call:    {framework_results['mean_ms']:.3f}ms")
        print(f"  Framework overhead: {overhead_results['overhead_mean_percent']:.1f}%")
        print(f"  Validation overhead: {validation_results['overhead_percent']:.1f}%")
        
        print("\nMicro-benchmarks:")
        print(f"  Tool lookup:       {registry_results['tool_lookup_us']:.1f}μs")
        print(f"  Chain discovery:   {registry_results['chain_discovery_us']:.1f}μs")
        print(f"  Compatibility:     {registry_results['compatibility_check_us']:.1f}μs")
        
        # Success criteria
        print("\n" + "="*80)
        print("SUCCESS CRITERIA")
        print("="*80)
        
        criteria = [
            ("Framework overhead < 20%", overhead_results['overhead_mean_percent'] < 20),
            ("Tool lookup < 10μs", registry_results['tool_lookup_us'] < 10),
            ("Chain discovery < 1000μs", registry_results['chain_discovery_us'] < 1000),
        ]
        
        all_pass = True
        for criterion, passed in criteria:
            if passed:
                print(f"  ✓ {criterion}")
            else:
                print(f"  ✗ {criterion}")
                all_pass = False
        
        if all_pass:
            print("\n✓ ALL PERFORMANCE CRITERIA MET")
        else:
            print("\n⚠️  Some performance criteria not met")
            
    finally:
        # Cleanup
        os.unlink(test_file)


if __name__ == "__main__":
    main()