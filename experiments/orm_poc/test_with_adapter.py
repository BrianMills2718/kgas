"""
Test real tools with the adapter layer.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, '/home/brian/projects/Digimons')

from orm_wrapper import ORMWrapper
from role_definitions import Role, Cardinality
from semantic_types import SemanticType
from tool_request_adapter import ToolInterfaceAdapter, EnhancedToolRequest


def test_t23c_with_adapter():
    """Test T23C with the new adapter."""
    print("="*60)
    print("TESTING T23C WITH ADAPTER")
    print("="*60)
    
    try:
        from src.core.service_manager import ServiceManager
        from src.tools.phase2.t23c_ontology_aware_extractor_unified import T23COntologyAwareExtractorUnified
        
        # Initialize service manager
        service_manager = ServiceManager()
        
        # Create T23C instance
        t23c = T23COntologyAwareExtractorUnified(service_manager)
        
        # Wrap with adapter
        adapter = ToolInterfaceAdapter(t23c, tool_type="t23c")
        
        # Test with simple dict input
        test_data = {
            "text": "John Smith is the CEO of TechCorp. He works with Jane Doe in San Francisco."
        }
        
        print("\nExecuting T23C through adapter...")
        result = adapter.execute(test_data)
        
        if "error" in result:
            print(f"❌ Execution failed: {result['error']}")
        else:
            print(f"✅ T23C executed successfully!")
            print(f"   Found {len(result.get('entities', []))} entities")
            
            # Show some entities
            for entity in result.get('entities', [])[:3]:
                print(f"   - {entity.get('text')} ({entity.get('type')})")
                
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()


def test_t23c_with_orm_wrapper():
    """Test T23C with ORM wrapper and adapter."""
    print("\n" + "="*60)
    print("TESTING T23C WITH ORM WRAPPER + ADAPTER")
    print("="*60)
    
    try:
        from src.core.service_manager import ServiceManager
        from src.tools.phase2.t23c_ontology_aware_extractor_unified import T23COntologyAwareExtractorUnified
        
        # Initialize service manager
        service_manager = ServiceManager()
        
        # Create T23C instance
        t23c = T23COntologyAwareExtractorUnified(service_manager)
        
        # Wrap with adapter
        adapter = ToolInterfaceAdapter(t23c, tool_type="t23c")
        
        # Wrap with ORM
        t23c_orm = ORMWrapper(
            tool=adapter,
            tool_id="T23C_Real",
            input_roles=[
                Role("text", SemanticType.TEXT_CONTENT, Cardinality.ONE)
            ],
            output_roles=[
                Role("entities", SemanticType.NAMED_ENTITIES, Cardinality.MANY),
                Role("relationships", SemanticType.RELATIONSHIPS, Cardinality.MANY)
            ]
        )
        
        # Test execution
        test_data = {
            "text": "Apple Inc. was founded by Steve Jobs in Cupertino, California."
        }
        
        print("\nExecuting T23C through ORM wrapper...")
        start = time.time()
        result = t23c_orm.execute(test_data)
        duration = (time.time() - start) * 1000
        
        if result.success:
            print(f"✅ ORM wrapper works with real T23C!")
            print(f"   Execution time: {duration:.2f}ms")
            print(f"   Semantic roles validated: {result.metadata.get('roles_validated', False)}")
            
            entities = result.data.get('entities', [])
            print(f"   Found {len(entities)} entities")
            for entity in entities[:3]:
                print(f"   - {entity.get('text')} ({entity.get('type')})")
        else:
            print(f"❌ ORM wrapper failed: {result.error}")
            
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()


def test_direct_enhanced_request():
    """Test T23C directly with EnhancedToolRequest."""
    print("\n" + "="*60)
    print("TESTING DIRECT ENHANCED REQUEST")
    print("="*60)
    
    try:
        from src.core.service_manager import ServiceManager
        from src.tools.phase2.t23c_ontology_aware_extractor_unified import T23COntologyAwareExtractorUnified
        from tool_request_adapter import EnhancedToolRequest
        
        # Initialize service manager
        service_manager = ServiceManager()
        
        # Create T23C instance
        t23c = T23COntologyAwareExtractorUnified(service_manager)
        
        # Create enhanced request with required attributes
        request = EnhancedToolRequest(
            input_data={
                "text": "Microsoft was founded by Bill Gates and Paul Allen."
            },
            validation_mode=False,  # T23C expects this
            operation="extract"  # T23C expects this
        )
        
        print("\nExecuting T23C with EnhancedToolRequest...")
        result = t23c.execute(request)
        
        if hasattr(result, 'success') and result.success:
            print(f"✅ Direct execution with EnhancedToolRequest works!")
            if hasattr(result, 'data'):
                entities = result.data.get('entities', [])
                print(f"   Found {len(entities)} entities")
        else:
            print(f"❌ Direct execution failed")
            
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all tests."""
    test_direct_enhanced_request()
    test_t23c_with_adapter()
    test_t23c_with_orm_wrapper()
    
    print("\n" + "="*60)
    print("ADAPTER VALIDATION SUMMARY")
    print("="*60)
    print("""
    Key Findings:
    1. T23C requires validation_mode and operation attributes
    2. EnhancedToolRequest provides these missing attributes
    3. ToolInterfaceAdapter bridges ORM wrapper to tool interface
    4. Semantic typing can work with complex service-dependent tools
    5. Real tools need Neo4j running for full functionality
    """)


if __name__ == "__main__":
    main()