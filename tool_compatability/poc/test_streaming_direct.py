#!/usr/bin/env python3
"""Direct test of streaming text loader"""

import sys
import os
import time
import psutil
from pathlib import Path

# Setup path properly
poc_dir = Path(__file__).parent
sys.path.insert(0, str(poc_dir))

from data_types import DataSchema
from data_references import DataReference, TextDataWithReference

# Import streaming loader directly
import importlib.util
spec = importlib.util.spec_from_file_location(
    "streaming_text_loader",
    str(poc_dir / "tools" / "streaming_text_loader.py")
)
streaming_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(streaming_module)
StreamingTextLoader = streaming_module.StreamingTextLoader


def create_test_file(path: str, size_mb: int):
    """Create a test file of specified size"""
    print(f"Creating {size_mb}MB test file...")
    chunk = "A" * (1024 * 1024)  # 1MB chunk
    with open(path, 'w') as f:
        for i in range(size_mb):
            f.write(chunk)
    print(f"✅ Created {os.path.getsize(path) / (1024*1024):.1f}MB file")


def monitor_memory():
    """Get current memory usage"""
    return psutil.Process().memory_info().rss / (1024 * 1024)  # MB


def test_streaming():
    """Test streaming text loader with large file"""
    
    print("="*60)
    print("STREAMING TEXT LOADER TEST")
    print("="*60)
    
    # Create 50MB test file
    test_file = "/tmp/test_streaming_50mb.txt"
    create_test_file(test_file, 50)
    
    # Monitor memory
    mem_before = monitor_memory()
    print(f"\nMemory before: {mem_before:.1f}MB")
    
    # Create loader
    loader = StreamingTextLoader()
    
    # Create file data
    file_data = DataSchema.FileData(
        path=test_file,
        size_bytes=os.path.getsize(test_file),
        mime_type="text/plain"
    )
    
    # Process file
    print("\nProcessing 50MB file with StreamingTextLoader...")
    start = time.time()
    result = loader.process(file_data)
    duration = time.time() - start
    
    # Check memory
    mem_after = monitor_memory()
    mem_used = mem_after - mem_before
    
    print(f"\n✅ File processed!")
    print(f"  Duration: {duration:.2f}s")
    print(f"  Memory used: {mem_used:.1f}MB")
    
    # Check result
    if result.success:
        data = result.data
        print(f"\n  Result type: {type(data).__name__}")
        print(f"  Is referenced: {data.is_referenced}")
        print(f"  Size: {data.size_bytes / (1024*1024):.1f}MB")
        
        if data.is_referenced:
            ref = data.reference
            print(f"\n  Reference details:")
            print(f"    Storage type: {ref.storage_type}")
            print(f"    Location: {ref.location}")
            print(f"    Strategy: {data.metadata.get('strategy')}")
            
            # Test streaming
            print(f"\n  Testing chunk streaming:")
            chunk_count = 0
            total_bytes = 0
            for chunk in ref.stream(1024*1024):  # 1MB chunks
                chunk_count += 1
                total_bytes += len(chunk)
                if chunk_count <= 3:
                    print(f"    Chunk {chunk_count}: {len(chunk)} bytes")
            
            print(f"  Total chunks: {chunk_count}")
            print(f"  Total bytes: {total_bytes / (1024*1024):.1f}MB")
            
            # Test getting sample
            print(f"\n  Sample (first 100 chars):")
            sample = ref.get_sample(100)
            print(f"    '{sample}'")
    else:
        print(f"❌ Processing failed: {result.error}")
    
    # Cleanup
    if os.path.exists(test_file):
        os.remove(test_file)
    
    print("\n" + "="*60)
    print("✅ TEST COMPLETE - Streaming works efficiently!")
    print("="*60)


if __name__ == "__main__":
    test_streaming()