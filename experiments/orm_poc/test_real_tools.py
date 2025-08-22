"""
Phase 0.5: Test semantic typing with REAL tools (not mocks)

This validates that our approach works with actual tool implementations
including their service dependencies.
"""

import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, '/home/brian/projects/Digimons')

from orm_wrapper import ORMWrapper
from role_definitions import Role, Cardinality
from semantic_types import SemanticType


def test_real_t03():
    """Test with real T03 implementation."""
    try:
        # Import the real T03 (correct class name)
        from src.tools.phase1.t03_text_loader_unified import T03TextLoaderUnified
        
        # Check what it actually needs
        tool = T03TextLoaderUnified()
        
        # Create test file
        test_file = Path("/tmp/test_doc.txt")
        test_file.write_text("This is a test document about artificial intelligence and machine learning.")
        
        # Test direct execution
        result = tool.execute({"file_path": str(test_file)})
        print(f"✅ Real T03 works: loaded {len(result.get('content', ''))} chars")
        print(f"   Output fields: {list(result.keys())}")
        
        return tool, result
        
    except ImportError as e:
        print(f"❌ Cannot import T03: {e}")
        return None, None
    except Exception as e:
        print(f"❌ T03 execution failed: {e}")
        print(f"   Tool might need ServiceManager or other dependencies")
        return None, None


def test_real_t15a():
    """Test with real T15A implementation."""
    try:
        from src.tools.phase1.t15a_text_chunker import T15ATextChunker
        
        tool = T15ATextChunker()
        
        # Test with sample text
        test_text = "This is sentence one. This is sentence two. This is sentence three."
        
        result = tool.execute({"text": test_text})
        print(f"✅ Real T15A works: created {len(result.get('chunks', []))} chunks")
        print(f"   Output fields: {list(result.keys())}")
        
        return tool, result
        
    except ImportError as e:
        print(f"❌ Cannot import T15A: {e}")
        # Try alternative import
        try:
            from src.tools.phase1.t15a_text_chunker import TextChunker
            print("   Found as TextChunker instead")
            return TextChunker(), None
        except:
            return None, None
    except Exception as e:
        print(f"❌ T15A execution failed: {e}")
        return None, None


def test_real_t23c():
    """Test with real T23C implementation."""
    try:
        from src.tools.phase2.t23c_ontology_aware_extractor import OntologyAwareExtractor
        
        # T23C likely needs ServiceManager
        from src.core.service_manager import ServiceManager
        
        service_manager = ServiceManager()
        tool = OntologyAwareExtractor(service_manager)
        
        # Test with sample text
        test_text = "John Smith works at OpenAI in San Francisco."
        
        result = tool.execute({"text": test_text})
        print(f"✅ Real T23C works: found {len(result.get('entities', []))} entities")
        print(f"   Output fields: {list(result.keys())}")
        
        return tool, result
        
    except ImportError as e:
        print(f"❌ Cannot import T23C: {e}")
        return None, None
    except Exception as e:
        print(f"❌ T23C execution failed: {e}")
        print(f"   Likely needs Neo4j or other services running")
        return None, None


def test_pipeline_with_real_tools():
    """Test the full pipeline with real tools."""
    print("\n" + "="*60)
    print("TESTING REAL TOOL PIPELINE")
    print("="*60)
    
    # Load real tools
    t03, t03_result = test_real_t03()
    t15a, t15a_result = test_real_t15a()
    t23c, t23c_result = test_real_t23c()
    
    if not all([t03, t15a, t23c]):
        print("\n⚠️ Cannot test full pipeline - some tools failed to load")
        print("This might be due to:")
        print("1. Missing service dependencies (Neo4j, etc.)")
        print("2. Different import paths or class names")
        print("3. Tools requiring initialization parameters")
        return
    
    # Now test semantic wrapping
    print("\n" + "="*60)
    print("TESTING SEMANTIC WRAPPING")
    print("="*60)
    
    # Wrap T03
    t03_wrapped = ORMWrapper(
        tool=t03,
        tool_id="T03_Real",
        input_roles=[
            Role("file_path", SemanticType.FILE_REFERENCE, Cardinality.ONE)
        ],
        output_roles=[
            Role("content", SemanticType.TEXT_CONTENT, Cardinality.ONE)
        ]
    )
    
    # Test wrapped execution
    test_file = Path("/tmp/test_wrapped.txt")
    test_file.write_text("Test document for wrapped execution.")
    
    result = t03_wrapped.execute({"file_path": str(test_file)})
    if result.success:
        print(f"✅ Wrapped T03 execution successful")
        print(f"   Execution time: {result.execution_time_ms:.2f}ms")
    else:
        print(f"❌ Wrapped execution failed: {result.error}")


def measure_real_performance():
    """Measure performance with real tools."""
    print("\n" + "="*60)
    print("PERFORMANCE MEASUREMENT")
    print("="*60)
    
    try:
        from src.tools.phase1.t03_text_loader_unified import T03TextLoaderUnified
        
        tool = T03TextLoaderUnified()
        test_file = Path("/tmp/perf_test.txt")
        test_file.write_text("Performance test document." * 100)
        
        # Direct execution
        times = []
        for _ in range(100):
            start = time.time()
            tool.execute({"file_path": str(test_file)})
            times.append((time.time() - start) * 1000)
        
        times.sort()
        print(f"Direct execution:")
        print(f"  p50: {times[50]:.2f}ms")
        print(f"  p95: {times[95]:.2f}ms")
        print(f"  p99: {times[99]:.2f}ms")
        
        # Wrapped execution
        wrapped = ORMWrapper(
            tool=tool,
            tool_id="T03_Perf",
            input_roles=[Role("file_path", SemanticType.FILE_REFERENCE)],
            output_roles=[Role("content", SemanticType.TEXT_CONTENT)]
        )
        
        wrapped_times = []
        for _ in range(100):
            start = time.time()
            wrapped.execute({"file_path": str(test_file)})
            wrapped_times.append((time.time() - start) * 1000)
        
        wrapped_times.sort()
        print(f"\nWrapped execution:")
        print(f"  p50: {wrapped_times[50]:.2f}ms")
        print(f"  p95: {wrapped_times[95]:.2f}ms")
        print(f"  p99: {wrapped_times[99]:.2f}ms")
        
        overhead_p50 = wrapped_times[50] - times[50]
        overhead_p95 = wrapped_times[95] - times[95]
        
        print(f"\nOverhead:")
        print(f"  p50: {overhead_p50:.2f}ms")
        print(f"  p95: {overhead_p95:.2f}ms")
        
        if overhead_p95 < 100:
            print("✅ Performance overhead acceptable")
        else:
            print("⚠️ Performance overhead may be too high")
            
    except Exception as e:
        print(f"❌ Performance test failed: {e}")


def main():
    """Run all real tool tests."""
    print("="*60)
    print("PHASE 0.5: REAL TOOL VALIDATION")
    print("="*60)
    
    # First, check what tools we can actually load
    print("\nStep 1: Checking tool availability...")
    test_real_t03()
    test_real_t15a()
    test_real_t23c()
    
    # Test pipeline if possible
    print("\nStep 2: Testing pipeline...")
    test_pipeline_with_real_tools()
    
    # Measure performance
    print("\nStep 3: Measuring performance...")
    measure_real_performance()
    
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("""
    If tools failed to load:
    1. Check service dependencies (Neo4j, etc.)
    2. Verify import paths and class names
    3. Check if tools need initialization parameters
    
    If tools loaded but execution failed:
    1. Tools might need ServiceManager properly configured
    2. Database connections might be required
    3. Check error messages for specific requirements
    
    If everything worked:
    1. Proceed with wrapping more tools
    2. Test complex scenarios (multi-input, state)
    3. Begin Phase 1 implementation
    """)


if __name__ == "__main__":
    main()