#!/usr/bin/env python3
"""Deep dive into overhead sources"""

import time
import statistics
import os
import sys
import psutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from poc.data_types import DataSchema

def profile_operations():
    print("="*60)
    print("OVERHEAD DEEP DIVE")
    print("="*60)
    
    # Test data
    test_file = '/tmp/test.txt'
    with open(test_file, 'w') as f:
        f.write("test content")
    
    process = psutil.Process()
    
    # 1. File read alone
    times = []
    for _ in range(1000):
        start = time.perf_counter()
        with open(test_file, 'r') as f:
            content = f.read()
        times.append(time.perf_counter() - start)
    file_read_ms = statistics.mean(times) * 1000
    print(f"\n1. Pure file read: {file_read_ms:.4f}ms")
    
    # 2. Memory measurement overhead
    times = []
    for _ in range(1000):
        start = time.perf_counter()
        memory_before = process.memory_info().rss / 1024 / 1024
        memory_after = process.memory_info().rss / 1024 / 1024
        memory_used = memory_after - memory_before
        times.append(time.perf_counter() - start)
    memory_overhead_ms = statistics.mean(times) * 1000
    print(f"2. Memory measurement (2x): {memory_overhead_ms:.4f}ms")
    
    # 3. Pydantic FileData creation
    times = []
    for _ in range(1000):
        start = time.perf_counter()
        file_data = DataSchema.FileData(
            path=test_file,
            size_bytes=os.path.getsize(test_file),
            mime_type='text/plain'
        )
        times.append(time.perf_counter() - start)
    pydantic_filedata_ms = statistics.mean(times) * 1000
    print(f"3. Pydantic FileData: {pydantic_filedata_ms:.4f}ms")
    
    # 4. Pydantic TextData creation
    times = []
    test_content = "test content"
    for _ in range(1000):
        start = time.perf_counter()
        text_data = DataSchema.TextData(
            content=test_content,
            source_file=test_file,
            encoding='utf-8',
            checksum='abc123',
            char_count=len(test_content),
            line_count=1
        )
        times.append(time.perf_counter() - start)
    pydantic_textdata_ms = statistics.mean(times) * 1000
    print(f"4. Pydantic TextData: {pydantic_textdata_ms:.4f}ms")
    
    # 5. Hash calculation
    import hashlib
    times = []
    content = "test content"
    for _ in range(1000):
        start = time.perf_counter()
        checksum = hashlib.md5(content.encode()).hexdigest()
        times.append(time.perf_counter() - start)
    hash_ms = statistics.mean(times) * 1000
    print(f"5. MD5 hash calculation: {hash_ms:.4f}ms")
    
    # 6. Time.time() calls
    times = []
    for _ in range(1000):
        start = time.perf_counter()
        start_time = time.time()
        end_time = time.time()
        duration = end_time - start_time
        times.append(time.perf_counter() - start)
    time_calls_ms = statistics.mean(times) * 1000
    print(f"6. Time tracking (2x time.time): {time_calls_ms:.4f}ms")
    
    # 7. isinstance checks
    times = []
    obj = file_data
    for _ in range(10000):
        start = time.perf_counter()
        _ = isinstance(obj, DataSchema.FileData)
        times.append(time.perf_counter() - start)
    isinstance_us = statistics.mean(times) * 1_000_000
    print(f"7. isinstance check: {isinstance_us:.3f}μs")
    
    # Total framework overhead estimate
    print("\n" + "="*60)
    print("OVERHEAD BREAKDOWN")
    print("="*60)
    
    total_framework = (
        file_read_ms +           # Actual work
        memory_overhead_ms +     # Memory tracking
        pydantic_filedata_ms +   # Input validation
        pydantic_textdata_ms +   # Output creation
        hash_ms +                # Checksum
        time_calls_ms            # Time tracking
    )
    
    print(f"\nEstimated framework total: {total_framework:.4f}ms")
    print(f"  File read:         {file_read_ms:.4f}ms ({file_read_ms/total_framework*100:.1f}%)")
    print(f"  Memory tracking:   {memory_overhead_ms:.4f}ms ({memory_overhead_ms/total_framework*100:.1f}%)")
    print(f"  Input validation:  {pydantic_filedata_ms:.4f}ms ({pydantic_filedata_ms/total_framework*100:.1f}%)")
    print(f"  Output creation:   {pydantic_textdata_ms:.4f}ms ({pydantic_textdata_ms/total_framework*100:.1f}%)")
    print(f"  Checksum:          {hash_ms:.4f}ms ({hash_ms/total_framework*100:.1f}%)")
    print(f"  Time tracking:     {time_calls_ms:.4f}ms ({time_calls_ms/total_framework*100:.1f}%)")
    
    print("\n📊 THE REAL ISSUE:")
    print(f"  Actual work (file read): {file_read_ms:.4f}ms")
    print(f"  Framework overhead:      {total_framework - file_read_ms:.4f}ms")
    print(f"  Overhead percentage:     {((total_framework - file_read_ms) / file_read_ms * 100):.0f}%")
    
    print("\n🔑 KEY FINDING:")
    print(f"  Memory tracking alone ({memory_overhead_ms:.4f}ms) is {memory_overhead_ms/file_read_ms:.0f}x the file read!")
    print("  This is because psutil.Process().memory_info() is expensive!")
    
    print("\n💡 SOLUTION:")
    print("  1. Remove memory tracking (saves ~{:.2f}ms)".format(memory_overhead_ms))
    print("  2. Make Pydantic validation optional (saves ~{:.2f}ms)".format(pydantic_filedata_ms + pydantic_textdata_ms))
    print("  3. Make checksums optional (saves ~{:.2f}ms)".format(hash_ms))
    print("  4. Result: ~{:.0f}% overhead instead of 1000%+".format(
        ((file_read_ms + time_calls_ms - file_read_ms) / file_read_ms * 100)))

if __name__ == "__main__":
    profile_operations()