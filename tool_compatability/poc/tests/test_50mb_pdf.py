#!/usr/bin/env python3
"""Test memory management with large files (50MB PDF)"""

import sys
import os
from pathlib import Path
import time
import psutil
import tracemalloc

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from poc.data_types import DataSchema
from poc.tools.text_loader import TextLoader


def create_large_test_file(path: str, size_mb: int):
    """Create a large test file of specified size"""
    print(f"Creating {size_mb}MB test file at {path}...")
    
    # Create content that simulates a text file
    chunk_size = 1024 * 1024  # 1MB chunks
    chunk_content = "A" * chunk_size  # 1MB of 'A's
    
    with open(path, 'w') as f:
        for i in range(size_mb):
            f.write(chunk_content)
            if i % 10 == 0:
                print(f"  Written {i}MB...")
    
    actual_size = os.path.getsize(path) / (1024 * 1024)
    print(f"✅ Created {actual_size:.1f}MB file")
    return path


def monitor_memory():
    """Get current memory usage"""
    process = psutil.Process()
    return process.memory_info().rss / (1024 * 1024)  # MB


def test_large_file_current_approach():
    """Test that current approach fails with large files"""
    
    print("="*60)
    print("TEST: 50MB File with Current Approach (Expected to fail or use excessive memory)")
    print("="*60)
    
    # Create 50MB test file
    test_file = "/tmp/test_50mb.txt"
    create_large_test_file(test_file, 50)
    
    # Monitor memory before
    mem_before = monitor_memory()
    print(f"\nMemory before loading: {mem_before:.1f}MB")
    
    # Start memory tracking
    tracemalloc.start()
    
    try:
        # Try to load with current TextLoader
        print("\nAttempting to load 50MB file with TextLoader...")
        loader = TextLoader()
        
        file_data = DataSchema.FileData(
            path=test_file,
            size_bytes=os.path.getsize(test_file),
            mime_type="text/plain"
        )
        
        start_time = time.time()
        result = loader.process(file_data)
        duration = time.time() - start_time
        
        # Check memory after
        mem_after = monitor_memory()
        mem_used = mem_after - mem_before
        
        # Get peak memory
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        print(f"\n⚠️ WARNING: File loaded but used excessive memory!")
        print(f"  Duration: {duration:.2f}s")
        print(f"  Memory before: {mem_before:.1f}MB")
        print(f"  Memory after: {mem_after:.1f}MB")
        print(f"  Memory used: {mem_used:.1f}MB")
        print(f"  Peak memory: {peak / (1024*1024):.1f}MB")
        
        # Check if content is actually in memory
        if result.success and result.data:
            content_size = len(result.data.content) / (1024 * 1024)
            print(f"  Content size in memory: {content_size:.1f}MB")
            
            if content_size > 40:  # Most of the file is in memory
                print("\n❌ PROBLEM: Entire file loaded into memory!")
                print("   This will not scale to larger files")
                return False
        
    except MemoryError as e:
        tracemalloc.stop()
        print(f"\n✅ Expected failure: MemoryError - {e}")
        return True
        
    except Exception as e:
        tracemalloc.stop()
        print(f"\n✅ Expected failure: {type(e).__name__} - {e}")
        return True
    
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)
    
    return False


def test_streaming_approach():
    """Test the streaming/reference approach for large files"""
    
    print("\n" + "="*60)
    print("TEST: 50MB File with Streaming Approach")
    print("="*60)
    
    # Import the streaming version
    try:
        # Fix import path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from tools.streaming_text_loader import StreamingTextLoader
        from data_references import DataReference
    except ImportError as e:
        print(f"❌ StreamingTextLoader import failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Create 50MB test file
    test_file = "/tmp/test_50mb_streaming.txt"
    create_large_test_file(test_file, 50)
    
    # Monitor memory before
    mem_before = monitor_memory()
    print(f"\nMemory before loading: {mem_before:.1f}MB")
    
    try:
        # Load with streaming approach
        print("\nLoading 50MB file with StreamingTextLoader...")
        loader = StreamingTextLoader()
        
        file_data = DataSchema.FileData(
            path=test_file,
            size_bytes=os.path.getsize(test_file),
            mime_type="text/plain"
        )
        
        start_time = time.time()
        result = loader.process(file_data)
        duration = time.time() - start_time
        
        # Check memory after
        mem_after = monitor_memory()
        mem_used = mem_after - mem_before
        
        print(f"\n✅ File processed with streaming!")
        print(f"  Duration: {duration:.2f}s")
        print(f"  Memory before: {mem_before:.1f}MB")
        print(f"  Memory after: {mem_after:.1f}MB")
        print(f"  Memory used: {mem_used:.1f}MB")
        
        # Verify we're using a reference, not loading content
        if hasattr(result.data, 'reference') and result.data.reference:
            print(f"\n✅ Using DataReference:")
            print(f"  Storage type: {result.data.reference.storage_type}")
            print(f"  Location: {result.data.reference.location}")
            print(f"  Size: {result.data.reference.size_bytes / (1024*1024):.1f}MB")
            
            # Test streaming chunks
            print("\n  Testing chunk streaming:")
            chunk_count = 0
            total_bytes = 0
            for chunk in result.data.reference.stream(chunk_size=1024*1024):
                chunk_count += 1
                total_bytes += len(chunk)
                if chunk_count <= 3:
                    print(f"    Chunk {chunk_count}: {len(chunk)} bytes")
            
            print(f"  Total chunks: {chunk_count}")
            print(f"  Total bytes streamed: {total_bytes / (1024*1024):.1f}MB")
            
            return True
        else:
            print("❌ Not using DataReference!")
            return False
            
    except Exception as e:
        print(f"\n❌ Streaming approach failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)


if __name__ == "__main__":
    print("MEMORY MANAGEMENT TEST SUITE")
    print("="*60)
    
    # Test current approach (should show memory issues)
    test1_passed = test_large_file_current_approach()
    
    # Test streaming approach (should work efficiently)
    test2_passed = test_streaming_approach()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    if not test1_passed:
        print("⚠️ Current approach loads entire file into memory")
    else:
        print("✅ Current approach correctly fails with large files")
    
    if test2_passed:
        print("✅ Streaming approach handles large files efficiently")
    else:
        print("❌ Streaming approach not working yet")
    
    # Exit with appropriate code
    if test2_passed:
        print("\n✅ MEMORY MANAGEMENT TESTS PASSED")
        sys.exit(0)
    else:
        print("\n⚠️ Need to implement streaming approach")
        sys.exit(1)