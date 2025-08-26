#!/usr/bin/env python3
"""
Test native tools with the framework
"""

import sys
import os
from pathlib import Path
import time

# Setup paths
poc_dir = Path(__file__).parent
sys.path.insert(0, str(poc_dir))

from framework import ToolFramework
from data_types import DataSchema, DataType
from tools.streaming_file_loader import StreamingFileLoader
from data_references import DataReference, ProcessingStrategy

def test_streaming_file_loader():
    """Test the StreamingFileLoader with various file sizes"""
    
    print("="*60)
    print("TESTING NATIVE STREAMING FILE LOADER")
    print("="*60)
    
    # Create test files
    small_file = "/tmp/test_small.txt"
    large_file = "/tmp/test_large.txt"
    
    # Create small file (1KB)
    with open(small_file, 'w') as f:
        f.write("Small file content.\n" * 50)
    
    # Create large file (15MB) - will trigger streaming
    with open(large_file, 'w') as f:
        for i in range(150000):
            f.write(f"Line {i}: This is a large file that will be streamed.\n")
    
    # Initialize loader
    loader = StreamingFileLoader()
    
    # Test 1: Small file (should load fully)
    print("\n📝 Test 1: Small file (<10MB)")
    print("-" * 40)
    
    small_data = DataSchema.FileData(
        path=small_file,
        size_bytes=os.path.getsize(small_file),
        mime_type="text/plain"
    )
    
    start = time.time()
    result = loader.process(small_data)
    duration = time.time() - start
    
    if result.success:
        if isinstance(result.data, DataSchema.TextData):
            print(f"✅ Loaded completely: {result.data.char_count} chars")
            print(f"   Time: {duration:.3f}s")
            print(f"   Lines: {result.data.line_count}")
        else:
            print("❌ Expected TextData, got:", type(result.data))
    else:
        print(f"❌ Failed: {result.error}")
    
    # Test 2: Large file (should return streaming reference)
    print("\n📚 Test 2: Large file (>10MB)")
    print("-" * 40)
    
    large_data = DataSchema.FileData(
        path=large_file,
        size_bytes=os.path.getsize(large_file),
        mime_type="text/plain"
    )
    
    start = time.time()
    result = loader.process(large_data)
    duration = time.time() - start
    
    if result.success:
        if isinstance(result.data, DataReference):
            print(f"✅ Returned streaming reference: {result.data.reference_id}")
            print(f"   Time: {duration:.3f}s")
            print(f"   Size: {result.data.size_bytes / (1024*1024):.1f}MB")
            print(f"   Strategy: {result.data.strategy}")
            
            # Test streaming
            print("\n   Testing streaming:")
            chunks_processed = 0
            total_chars = 0
            
            for chunk in loader.stream_chunks(result.data):
                chunks_processed += 1
                total_chars += len(chunk)
                if chunks_processed <= 3:
                    print(f"     Chunk {chunks_processed}: {len(chunk)} chars")
            
            print(f"   ✅ Streamed {chunks_processed} chunks, {total_chars} total chars")
            
        else:
            print("❌ Expected DataReference, got:", type(result.data))
    else:
        print(f"❌ Failed: {result.error}")
    
    # Test 3: Framework integration
    print("\n🔧 Test 3: Framework Integration")
    print("-" * 40)
    
    framework = ToolFramework()
    framework.register_tool(loader)
    
    print(f"✅ Tool registered: {loader.get_capabilities().tool_id}")
    
    # Check capabilities
    caps = framework.capabilities[loader.get_capabilities().tool_id]
    print(f"   Input: {caps.input_type}")
    print(f"   Output: {caps.output_type}")
    print(f"   Strategy: {caps.processing_strategy}")
    print(f"   Max size: {caps.max_input_size / (1024*1024):.0f}MB")
    
    # Test 4: Error handling (fail-fast)
    print("\n💥 Test 4: Fail-Fast Error Handling")
    print("-" * 40)
    
    # Non-existent file
    bad_data = DataSchema.FileData(
        path="/tmp/does_not_exist.txt",
        size_bytes=0,
        mime_type="text/plain"
    )
    
    try:
        result = loader.process(bad_data)
        print("❌ Should have failed fast!")
    except FileNotFoundError as e:
        print(f"✅ Failed fast with FileNotFoundError: {e}")
    
    # Suspicious path
    bad_data = DataSchema.FileData(
        path="../../../etc/passwd",
        size_bytes=0,
        mime_type="text/plain"
    )
    
    try:
        result = loader.process(bad_data)
        print("❌ Should have failed fast!")
    except ValueError as e:
        print(f"✅ Failed fast with ValueError: {e}")
    
    # Cleanup
    os.remove(small_file)
    os.remove(large_file)
    
    print("\n" + "="*60)
    print("STREAMING FILE LOADER TEST COMPLETE")
    print("="*60)
    
    return True


def test_framework_with_native_tools():
    """Test that native tools work perfectly with the framework"""
    
    print("\n" + "="*60)
    print("FRAMEWORK + NATIVE TOOLS TEST")
    print("="*60)
    
    framework = ToolFramework()
    
    # Register native tools
    loader = StreamingFileLoader()
    framework.register_tool(loader)
    
    print(f"\n✅ Registered {len(framework.tools)} native tool(s)")
    
    # Test chain discovery
    chains = framework.find_chains(DataType.FILE, DataType.TEXT)
    if chains:
        print(f"✅ Found chain: {' → '.join(chains[0])}")
    else:
        print("❌ No chains found")
    
    # Performance comparison
    print("\n📊 Performance Characteristics:")
    print("   Native tool advantages:")
    print("   - Zero adapter overhead")
    print("   - Direct DataSchema usage")
    print("   - No service dependencies")
    print("   - Streaming support built-in")
    print("   - Fail-fast error handling")
    
    return True


if __name__ == "__main__":
    print("Testing Native Tools Implementation\n")
    
    # Test individual tools
    success = test_streaming_file_loader()
    
    # Test framework integration
    if success:
        test_framework_with_native_tools()
    
    print("\n✨ Native tools are the way forward!")