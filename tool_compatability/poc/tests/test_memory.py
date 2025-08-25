#!/usr/bin/env python3
"""
Memory Limit Testing - Find the breaking points

Tests memory usage under various conditions to determine:
- Maximum document size that can be processed
- Memory overhead of the framework
- Memory leaks in tool chains
"""

import os
import sys
import psutil
import tracemalloc
import json
import tempfile
from pathlib import Path
from typing import Dict, Any, List
import time

# Add poc to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from poc.registry import ToolRegistry
from poc.tools.text_loader import TextLoader, TextLoaderConfig
from poc.tools.entity_extractor import EntityExtractor, EntityExtractorConfig
from poc.tools.graph_builder import GraphBuilder, GraphBuilderConfig
from poc.data_types import DataType, DataSchema


class MemoryProfiler:
    """Profiles memory usage during tool execution"""
    
    def __init__(self):
        self.process = psutil.Process()
        self.baseline_memory = 0
        self.peak_memory = 0
        self.measurements = []
    
    def start(self):
        """Start memory profiling"""
        tracemalloc.start()
        self.baseline_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        self.peak_memory = self.baseline_memory
        self.measurements = []
    
    def measure(self, label: str):
        """Take a memory measurement"""
        current = self.process.memory_info().rss / 1024 / 1024  # MB
        self.peak_memory = max(self.peak_memory, current)
        self.measurements.append({
            "label": label,
            "memory_mb": current,
            "delta_mb": current - self.baseline_memory
        })
    
    def stop(self) -> Dict[str, Any]:
        """Stop profiling and return results"""
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        return {
            "baseline_mb": self.baseline_memory,
            "peak_mb": self.peak_memory,
            "current_mb": self.process.memory_info().rss / 1024 / 1024,
            "traced_current_mb": current / 1024 / 1024,
            "traced_peak_mb": peak / 1024 / 1024,
            "measurements": self.measurements
        }


def create_large_document(size_mb: float) -> str:
    """Create a document of specific size"""
    # Each entity description is ~100 bytes
    bytes_per_entity = 100
    num_entities = int((size_mb * 1024 * 1024) / bytes_per_entity)
    
    lines = [
        "Large Document for Memory Testing",
        f"This document contains {num_entities} entities to test memory limits.",
        ""
    ]
    
    # Generate entities
    for i in range(num_entities):
        if i % 10 == 0:
            lines.append(f"\nSection {i//10}: Group of related entities\n")
        
        lines.append(f"Entity_{i:06d} is a test entity located in TestLocation_{i%100} "
                    f"and works with Partner_{(i+1):06d} on Project_{i%50}.")
    
    content = "\n".join(lines)
    actual_size = len(content.encode()) / 1024 / 1024
    print(f"  Created document: {actual_size:.2f}MB ({num_entities} entities)")
    return content


def test_document_size_limits():
    """Test maximum document size that can be processed"""
    print("\n" + "="*80)
    print("TEST 1: Document Size Limits")
    print("="*80)
    
    sizes_mb = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0]
    results = []
    
    # Initialize tools with real services
    try:
        registry = ToolRegistry()
        
        # TextLoader with size limits
        text_loader = TextLoader(TextLoaderConfig(max_size_mb=50.0))
        registry.register(text_loader)
        
        # EntityExtractor - requires GEMINI_API_KEY
        if not os.getenv("GEMINI_API_KEY"):
            print("  ⚠️  Skipping - GEMINI_API_KEY not set")
            print("  Set GEMINI_API_KEY to test with real LLM")
            return
        
        entity_extractor = EntityExtractor()
        registry.register(entity_extractor)
        
        # GraphBuilder - requires Neo4j
        try:
            graph_builder = GraphBuilder()
            registry.register(graph_builder)
        except Exception as e:
            print(f"  ⚠️  Skipping - Neo4j not available: {e}")
            print("  Start Neo4j to test with real graph database")
            return
        
    except Exception as e:
        print(f"  ✗ Failed to initialize tools: {e}")
        return
    
    for size_mb in sizes_mb:
        print(f"\nTesting {size_mb}MB document:")
        
        profiler = MemoryProfiler()
        profiler.start()
        
        try:
            # Create test document
            profiler.measure("before_create")
            content = create_large_document(size_mb)
            profiler.measure("after_create")
            
            # Save to file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(content)
                file_path = f.name
            profiler.measure("after_save")
            
            # Process through chain
            file_data = DataSchema.FileData(
                path=file_path,
                size_bytes=os.path.getsize(file_path),
                mime_type="text/plain"
            )
            
            # Find chain
            chains = registry.find_chains(DataType.FILE, DataType.GRAPH)
            if not chains:
                print("  ✗ No chain found")
                continue
            
            chain = chains[0]
            print(f"  Chain: {' → '.join(chain)}")
            
            # Execute chain
            start_time = time.time()
            current_data = file_data
            
            for tool_id in chain:
                tool = registry.tools[tool_id]
                profiler.measure(f"before_{tool_id}")
                
                result = tool.process(current_data)
                if not result.success:
                    raise RuntimeError(f"Tool {tool_id} failed: {result.error}")
                
                current_data = result.data
                profiler.measure(f"after_{tool_id}")
            
            duration = time.time() - start_time
            
            # Get memory stats
            stats = profiler.stop()
            
            # Record results
            result = {
                "size_mb": size_mb,
                "success": True,
                "duration": duration,
                "memory_used_mb": stats["peak_mb"] - stats["baseline_mb"],
                "peak_memory_mb": stats["peak_mb"]
            }
            results.append(result)
            
            print(f"  ✓ Success in {duration:.2f}s")
            print(f"  Memory used: {result['memory_used_mb']:.1f}MB")
            print(f"  Peak memory: {result['peak_memory_mb']:.1f}MB")
            
            # Cleanup
            os.unlink(file_path)
            
        except Exception as e:
            stats = profiler.stop()
            result = {
                "size_mb": size_mb,
                "success": False,
                "error": str(e),
                "memory_used_mb": stats["peak_mb"] - stats["baseline_mb"],
                "peak_memory_mb": stats["peak_mb"]
            }
            results.append(result)
            
            print(f"  ✗ Failed: {e}")
            print(f"  Memory at failure: {result['peak_memory_mb']:.1f}MB")
            
            # This is our limit
            print(f"\n  LIMIT FOUND: Failed at {size_mb}MB")
            break
    
    # Summary
    print("\n" + "-"*80)
    print("Summary:")
    print("-"*80)
    
    successful = [r for r in results if r["success"]]
    if successful:
        max_size = max(r["size_mb"] for r in successful)
        print(f"✓ Maximum successful size: {max_size}MB")
        
        # Memory efficiency
        for r in successful:
            efficiency = r["memory_used_mb"] / r["size_mb"]
            print(f"  {r['size_mb']}MB: {efficiency:.1f}x memory overhead")
    
    failed = [r for r in results if not r["success"]]
    if failed:
        min_fail = min(r["size_mb"] for r in failed)
        print(f"✗ Minimum failure size: {min_fail}MB")
    
    return results


def test_memory_leak():
    """Test for memory leaks in repeated operations"""
    print("\n" + "="*80)
    print("TEST 2: Memory Leak Detection")
    print("="*80)
    
    # Create small test document
    content = """
    Memory leak test document.
    John Smith works at TechCorp in San Francisco.
    The company develops AI products.
    """
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(content)
        file_path = f.name
    
    try:
        # Initialize tools
        registry = ToolRegistry()
        registry.register(TextLoader())
        
        # Check if we can use real services
        use_real = False
        if os.getenv("GEMINI_API_KEY"):
            try:
                registry.register(EntityExtractor())
                registry.register(GraphBuilder())
                use_real = True
            except:
                pass
        
        if not use_real:
            print("  ⚠️  Using TextLoader only (no API keys)")
        
        # Memory measurements
        measurements = []
        iterations = 50
        
        print(f"Running {iterations} iterations...")
        
        for i in range(iterations):
            if i % 10 == 0:
                # Measure memory
                memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
                measurements.append(memory_mb)
                print(f"  Iteration {i}: {memory_mb:.1f}MB")
            
            # Process document
            file_data = DataSchema.FileData(
                path=file_path,
                size_bytes=os.path.getsize(file_path),
                mime_type="text/plain"
            )
            
            # Execute available chain
            if use_real:
                chains = registry.find_chains(DataType.FILE, DataType.GRAPH)
            else:
                chains = registry.find_chains(DataType.FILE, DataType.TEXT)
            
            if chains:
                chain = chains[0]
                current_data = file_data
                
                for tool_id in chain:
                    tool = registry.tools[tool_id]
                    result = tool.process(current_data)
                    if result.success:
                        current_data = result.data
        
        # Check for leak
        print("\nMemory Analysis:")
        print(f"  Start: {measurements[0]:.1f}MB")
        print(f"  End:   {measurements[-1]:.1f}MB")
        print(f"  Delta: {measurements[-1] - measurements[0]:.1f}MB")
        
        # Calculate leak rate
        if len(measurements) > 2:
            # Simple linear regression
            x = list(range(len(measurements)))
            y = measurements
            n = len(x)
            
            x_mean = sum(x) / n
            y_mean = sum(y) / n
            
            numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
            denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
            
            if denominator > 0:
                slope = numerator / denominator
                leak_per_10 = slope * 10
                
                print(f"  Leak rate: {leak_per_10:.3f}MB per 10 iterations")
                
                if abs(leak_per_10) < 0.1:
                    print("  ✓ No significant memory leak detected")
                else:
                    print(f"  ⚠️  Potential memory leak: {leak_per_10:.3f}MB/10 iterations")
    
    finally:
        os.unlink(file_path)


def test_concurrent_processing():
    """Test memory usage with concurrent processing"""
    print("\n" + "="*80)
    print("TEST 3: Concurrent Processing Memory")
    print("="*80)
    
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    # Create test documents
    num_docs = 10
    docs = []
    
    for i in range(num_docs):
        content = f"Document {i}: Entity_{i} works at Company_{i} in Location_{i}."
        with tempfile.NamedTemporaryFile(mode='w', suffix=f'_{i}.txt', delete=False) as f:
            f.write(content)
            docs.append(f.name)
    
    try:
        # Initialize registry
        registry = ToolRegistry()
        registry.register(TextLoader())
        
        # Baseline memory
        baseline_mb = psutil.Process().memory_info().rss / 1024 / 1024
        print(f"Baseline memory: {baseline_mb:.1f}MB")
        
        def process_document(file_path):
            """Process a single document"""
            file_data = DataSchema.FileData(
                path=file_path,
                size_bytes=os.path.getsize(file_path),
                mime_type="text/plain"
            )
            
            chains = registry.find_chains(DataType.FILE, DataType.TEXT)
            if chains:
                chain = chains[0]
                current_data = file_data
                
                for tool_id in chain:
                    tool = registry.tools[tool_id]
                    result = tool.process(current_data)
                    if result.success:
                        current_data = result.data
                
                return True
            return False
        
        # Test different thread counts
        for num_threads in [1, 2, 4, 8]:
            print(f"\nTesting with {num_threads} threads:")
            
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = [executor.submit(process_document, doc) for doc in docs]
                
                # Monitor memory while processing
                peak_memory = start_memory
                
                for future in as_completed(futures):
                    current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                    peak_memory = max(peak_memory, current_memory)
                    future.result()
            
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            print(f"  Start:  {start_memory:.1f}MB")
            print(f"  Peak:   {peak_memory:.1f}MB")
            print(f"  End:    {end_memory:.1f}MB")
            print(f"  Delta:  {peak_memory - start_memory:.1f}MB")
            
            overhead_per_thread = (peak_memory - start_memory) / num_threads
            print(f"  Per thread: {overhead_per_thread:.1f}MB")
    
    finally:
        # Cleanup
        for doc in docs:
            os.unlink(doc)


def main():
    """Run all memory tests"""
    print("\n" + "="*80)
    print("MEMORY LIMIT TESTING")
    print("="*80)
    
    # Store results
    all_results = {}
    
    # Test 1: Document size limits
    size_results = test_document_size_limits()
    all_results["size_limits"] = size_results
    
    # Test 2: Memory leak detection
    test_memory_leak()
    
    # Test 3: Concurrent processing
    test_concurrent_processing()
    
    # Save results
    results_file = "/tmp/poc_memory_test_results.json"
    with open(results_file, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    
    print("\n" + "="*80)
    print("MEMORY TESTING COMPLETE")
    print("="*80)
    print(f"Results saved to: {results_file}")
    
    # Final summary
    if size_results:
        successful = [r for r in size_results if r.get("success")]
        if successful:
            max_size = max(r["size_mb"] for r in successful)
            print(f"\n✓ Maximum document size: {max_size}MB")
            
            # Check against requirement
            if max_size >= 10.0:
                print("✓ Meets 10MB requirement")
            elif max_size >= 5.0:
                print("⚠️  Below 10MB target but acceptable (5MB+)")
            else:
                print("✗ Fails requirement (needs 5MB minimum)")


if __name__ == "__main__":
    main()