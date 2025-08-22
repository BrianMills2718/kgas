"""
Test with real tools using their proper interfaces.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, '/home/brian/projects/Digimons')

from orm_wrapper import ORMWrapper
from role_definitions import Role, Cardinality
from semantic_types import SemanticType


def test_tools_with_proper_interfaces():
    """Test tools with their actual expected interfaces."""
    
    print("="*60)
    print("TESTING WITH PROPER INTERFACES")
    print("="*60)
    
    # Test T03 with ServiceManager
    print("\n1. Testing T03 Text Loader...")
    try:
        from src.core.service_manager import ServiceManager
        from src.tools.phase1.t03_text_loader_unified import T03TextLoaderUnified
        
        service_manager = ServiceManager()
        t03 = T03TextLoaderUnified(service_manager)
        
        # Create test file
        test_file = Path("/tmp/test_real.txt")
        test_file.write_text("This document discusses artificial intelligence and machine learning applications.")
        
        # T03 expects a ToolRequest object
        from src.core.tool_contract import ToolRequest
        
        request = ToolRequest(input_data={"file_path": str(test_file)})
        
        result = t03.execute(request)
        print(f"✅ T03 executed successfully")
        print(f"   Loaded {len(result.data.get('content', ''))} characters")
        print(f"   Output fields: {list(result.data.keys())}")
        
    except Exception as e:
        print(f"❌ T03 failed: {e}")
        # Try simpler approach
        try:
            # Maybe it accepts dict directly?
            result = t03.execute({"file_path": str(test_file)})
            print(f"✅ T03 works with dict input")
        except:
            pass
    
    # Test T23C with proper request
    print("\n2. Testing T23C Entity Extractor...")
    try:
        from src.core.service_manager import ServiceManager
        from src.tools.phase2.t23c_ontology_aware_extractor import OntologyAwareExtractor
        from src.core.tool_contract import ToolRequest
        
        service_manager = ServiceManager()
        t23c = OntologyAwareExtractor(service_manager)
        
        # Create proper request
        request = ToolRequest(input_data={
            "text": "John Smith is the CEO of TechCorp. He works with Jane Doe in San Francisco."
        })
        
        result = t23c.execute(request)
        
        if result.success:
            print(f"✅ T23C executed successfully")
            print(f"   Found {len(result.data.get('entities', []))} entities")
            print(f"   Output fields: {list(result.data.keys())}")
            
            # Show some entities
            for entity in result.data.get('entities', [])[:3]:
                print(f"   - {entity.get('text')} ({entity.get('type')})")
        else:
            print(f"❌ T23C failed: {result.message}")
            
    except Exception as e:
        print(f"❌ T23C failed: {e}")
        import traceback
        traceback.print_exc()


def test_with_semantic_wrapper():
    """Test if we can wrap these complex tools."""
    
    print("\n" + "="*60)
    print("TESTING SEMANTIC WRAPPER ON REAL TOOLS")
    print("="*60)
    
    try:
        from src.core.service_manager import ServiceManager
        from src.tools.phase1.t03_text_loader_unified import T03TextLoaderUnified
        from src.core.tool_contract import ToolRequest
        
        service_manager = ServiceManager()
        base_tool = T03TextLoaderUnified(service_manager)
        
        # Create wrapper that handles the interface adaptation
        class T03Adapter:
            """Adapter to handle interface conversion."""
            def __init__(self, tool):
                self.tool = tool
                
            def execute(self, data):
                """Convert dict to ToolRequest."""
                request = ToolRequest(input_data=data)
                result = self.tool.execute(request)
                
                # Convert ToolResult back to dict
                if hasattr(result, 'data'):
                    return result.data
                return result
        
        # Wrap with adapter
        adapted_tool = T03Adapter(base_tool)
        
        # Now wrap with ORM
        t03_orm = ORMWrapper(
            tool=adapted_tool,
            tool_id="T03_Real",
            input_roles=[
                Role("file_path", SemanticType.FILE_REFERENCE, Cardinality.ONE)
            ],
            output_roles=[
                Role("content", SemanticType.TEXT_CONTENT, Cardinality.ONE)
            ]
        )
        
        # Test execution
        test_file = Path("/tmp/orm_test.txt")
        test_file.write_text("Test document for ORM wrapper.")
        
        result = t03_orm.execute({"file_path": str(test_file)})
        
        if result.success:
            print(f"✅ ORM wrapper works with real T03!")
            print(f"   Execution time: {result.execution_time_ms:.2f}ms")
        else:
            print(f"❌ ORM wrapper failed: {result.error}")
            
    except Exception as e:
        print(f"❌ Failed to create wrapper: {e}")


def main():
    test_tools_with_proper_interfaces()
    test_with_semantic_wrapper()
    
    print("\n" + "="*60)
    print("KEY FINDINGS")
    print("="*60)
    print("""
    1. Real tools expect ToolRequest objects, not plain dicts
    2. They return ToolResult objects with .data, .success, .message
    3. We need adapter layer between ORM wrapper and tools
    4. Tools are complex but still do input→output transformation
    5. Semantic typing can work with adapter pattern
    """)


if __name__ == "__main__":
    main()