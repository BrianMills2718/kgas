#!/usr/bin/env python3
"""
Performance Baseline Test - Measure adapter overhead
"""

import sys
import time
from pathlib import Path
sys.path.append('/home/brian/projects/Digimons')

from src.core.adapter_factory import UniversalAdapterFactory
from src.tools.simple_text_loader import SimpleTextLoader

def measure_direct_execution(iterations=100):
    """Measure direct tool execution time"""
    tool = SimpleTextLoader()
    
    # Create test file
    test_file = Path("/home/brian/projects/Digimons/test_data/sample.txt")
    if not test_file.exists():
        test_file.parent.mkdir(exist_ok=True)
        test_file.write_text("Test content for performance measurement.")
    
    # Warm up
    for _ in range(10):
        tool.process(str(test_file))
    
    # Measure
    start = time.perf_counter()
    for _ in range(iterations):
        result = tool.process(str(test_file))
    end = time.perf_counter()
    
    return (end - start) / iterations

def measure_adapted_execution(iterations=100):
    """Measure execution through adapter"""
    factory = UniversalAdapterFactory()
    tool = SimpleTextLoader()
    adapted = factory.wrap(tool)
    
    # Create test file
    test_file = Path("/home/brian/projects/Digimons/test_data/sample.txt")
    if not test_file.exists():
        test_file.parent.mkdir(exist_ok=True)
        test_file.write_text("Test content for performance measurement.")
    
    # Warm up
    for _ in range(10):
        adapted.process(str(test_file))
    
    # Measure
    start = time.perf_counter()
    for _ in range(iterations):
        result = adapted.process(str(test_file))
    end = time.perf_counter()
    
    return (end - start) / iterations

def main():
    print("="*60)
    print("PERFORMANCE BASELINE TEST")
    print("="*60)
    
    iterations = 1000
    print(f"\nMeasuring with {iterations} iterations...")
    
    # Measure direct
    print("\n1. Direct Execution:")
    direct_time = measure_direct_execution(iterations)
    print(f"   Average time: {direct_time*1000:.4f}ms")
    print(f"   Operations/sec: {1/direct_time:.0f}")
    
    # Measure adapted
    print("\n2. Adapted Execution:")
    adapted_time = measure_adapted_execution(iterations)
    print(f"   Average time: {adapted_time*1000:.4f}ms")
    print(f"   Operations/sec: {1/adapted_time:.0f}")
    
    # Calculate overhead
    overhead_time = adapted_time - direct_time
    overhead_percent = (overhead_time / direct_time) * 100
    
    print("\n3. Overhead Analysis:")
    print(f"   Additional time: {overhead_time*1000:.4f}ms")
    print(f"   Overhead: {overhead_percent:.1f}%")
    
    # Success criteria
    print("\n4. Success Criteria:")
    if overhead_percent < 20:
        print(f"   ✅ PASS: {overhead_percent:.1f}% < 20% (acceptable)")
    else:
        print(f"   ❌ FAIL: {overhead_percent:.1f}% >= 20% (too high)")
    
    # Framework vs adapter-only test
    print("\n5. Component Breakdown:")
    
    # Just wrapping overhead
    start = time.perf_counter()
    factory = UniversalAdapterFactory()
    for _ in range(1000):
        factory.wrap(SimpleTextLoader())
    wrap_time = (time.perf_counter() - start) / 1000
    
    print(f"   Wrapping overhead: {wrap_time*1000:.4f}ms per wrap")
    print(f"   Execution overhead: {overhead_time*1000:.4f}ms per call")
    print(f"   Ratio: {overhead_time/wrap_time:.1f}x execution vs wrapping")
    
    print("\n" + "="*60)
    print("PERFORMANCE TEST COMPLETE")
    print("="*60)
    
    return overhead_percent < 20

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)