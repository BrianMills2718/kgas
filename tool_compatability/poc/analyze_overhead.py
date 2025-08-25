#!/usr/bin/env python3
"""Analyze where the overhead really comes from"""

import time
import statistics
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from poc.tools.text_loader import TextLoader
from poc.data_types import DataSchema

def measure_overhead():
    # Create a test file
    test_content = 'This is test content for benchmarking'
    test_file = '/tmp/bench_test.txt'
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    print("="*60)
    print("OVERHEAD ANALYSIS")
    print("="*60)
    
    # 1. Measure direct file read
    print("\n1. Direct file read (no framework):")
    times_direct = []
    for _ in range(1000):
        start = time.perf_counter()
        with open(test_file, 'r') as f:
            content = f.read()
        times_direct.append(time.perf_counter() - start)
    
    direct_ms = statistics.mean(times_direct) * 1000
    print(f"   Average: {direct_ms:.4f}ms")
    
    # 2. Measure Pydantic validation only
    print("\n2. Pydantic validation overhead:")
    
    # Time creating FileData object
    times_filedata = []
    for _ in range(1000):
        start = time.perf_counter()
        file_data = DataSchema.FileData(
            path=test_file,
            size_bytes=os.path.getsize(test_file),
            mime_type='text/plain'
        )
        times_filedata.append(time.perf_counter() - start)
    
    filedata_ms = statistics.mean(times_filedata) * 1000
    print(f"   FileData creation: {filedata_ms:.4f}ms")
    
    # 3. Measure framework file read
    print("\n3. Framework file read (TextLoader):")
    loader = TextLoader()
    
    # Pre-create FileData to separate concerns
    file_data = DataSchema.FileData(
        path=test_file,
        size_bytes=os.path.getsize(test_file),
        mime_type='text/plain'
    )
    
    times_framework = []
    for _ in range(1000):
        start = time.perf_counter()
        result = loader.process(file_data)
        content = result.data.content if result.success else None
        times_framework.append(time.perf_counter() - start)
    
    framework_ms = statistics.mean(times_framework) * 1000
    print(f"   Average: {framework_ms:.4f}ms")
    
    # 4. Break down the overhead
    print("\n4. Overhead breakdown:")
    print(f"   Direct read:           {direct_ms:.4f}ms")
    print(f"   Pydantic FileData:    +{filedata_ms:.4f}ms")
    print(f"   Framework processing: +{framework_ms - direct_ms - filedata_ms:.4f}ms")
    print(f"   Total framework:       {framework_ms:.4f}ms")
    
    overhead_percent = ((framework_ms - direct_ms) / direct_ms * 100)
    print(f"\n   Total overhead: {overhead_percent:.1f}%")
    
    # 5. Measure individual Pydantic operations
    print("\n5. Pydantic operations (microseconds):")
    
    # Simple dict vs Pydantic Entity
    entity_dict = {'id': 'e1', 'text': 'John', 'type': 'PERSON', 'confidence': 0.9}
    
    # Dict access
    times_dict = []
    for _ in range(10000):
        start = time.perf_counter()
        _ = entity_dict['id']
        times_dict.append(time.perf_counter() - start)
    
    # Pydantic creation
    times_pydantic = []
    for _ in range(10000):
        start = time.perf_counter()
        entity = DataSchema.Entity(**entity_dict)
        times_pydantic.append(time.perf_counter() - start)
    
    dict_us = statistics.mean(times_dict) * 1_000_000
    pydantic_us = statistics.mean(times_pydantic) * 1_000_000
    
    print(f"   Dict access:         {dict_us:.3f}μs")
    print(f"   Pydantic Entity:     {pydantic_us:.3f}μs")
    print(f"   Overhead:            {((pydantic_us - dict_us) / dict_us * 100):.0f}%")
    
    print("\n" + "="*60)
    print("CONCLUSION")
    print("="*60)
    
    if overhead_percent > 100:
        print(f"⚠️  Framework adds {overhead_percent:.0f}% overhead to file operations")
        print("   This is primarily from:")
        print(f"   - Pydantic validation: ~{filedata_ms:.3f}ms per operation")
        print(f"   - Framework wrapper: ~{framework_ms - direct_ms - filedata_ms:.3f}ms")
    else:
        print(f"✅ Framework overhead is reasonable: {overhead_percent:.0f}%")
    
    # The key insight
    print("\n📊 KEY INSIGHT:")
    print(f"   For a {direct_ms:.4f}ms operation:")
    print(f"   - Adding Pydantic validation: +{filedata_ms:.4f}ms")
    print(f"   - Total time with framework: {framework_ms:.4f}ms")
    print(f"   - Overhead percentage: {overhead_percent:.0f}%")
    print("\n   Note: For very fast operations (microseconds), ")
    print("   even small absolute overhead appears large in percentage.")

if __name__ == "__main__":
    measure_overhead()