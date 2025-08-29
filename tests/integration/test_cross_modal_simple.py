#!/usr/bin/env python3
"""Simple test to check if cross-modal tools can be imported and registered."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from src.core.tool_contract import get_tool_registry
from src.core.tool_adapter import LegacyToolAdapter
from src.core.service_manager import ServiceManager

def test_cross_modal_simple():
    """Test cross-modal tools directly."""
    
    print("=" * 60)
    print("CROSS-MODAL TOOL IMPORT TEST")
    print("=" * 60)
    
    registry = get_tool_registry()
    service_manager = ServiceManager()
    
    successful = []
    failed = []
    
    # Test each cross-modal tool individually
    print("\n1. Testing GraphTableExporter...")
    try:
        from src.tools.cross_modal.graph_table_exporter import GraphTableExporter
        tool = GraphTableExporter()
        tool.category = 'cross_modal'
        adapter = LegacyToolAdapter(tool, "GRAPH_TABLE_EXPORTER", "Graph to Table Exporter")
        registry.register_tool(adapter)
        successful.append("GRAPH_TABLE_EXPORTER")
        print("   ✅ GraphTableExporter registered")
    except Exception as e:
        failed.append(("GRAPH_TABLE_EXPORTER", str(e)))
        print(f"   ❌ GraphTableExporter failed: {e}")
    
    print("\n2. Testing MultiFormatExporter...")
    try:
        from src.tools.cross_modal.multi_format_exporter import MultiFormatExporter
        tool = MultiFormatExporter()
        tool.category = 'cross_modal'
        adapter = LegacyToolAdapter(tool, "MULTI_FORMAT_EXPORTER", "Multi-Format Exporter")
        registry.register_tool(adapter)
        successful.append("MULTI_FORMAT_EXPORTER")
        print("   ✅ MultiFormatExporter registered")
    except Exception as e:
        failed.append(("MULTI_FORMAT_EXPORTER", str(e)))
        print(f"   ❌ MultiFormatExporter failed: {e}")
    
    print("\n3. Testing CrossModalTool...")
    try:
        from src.tools.phase_c.cross_modal_tool import CrossModalTool
        tool = CrossModalTool()
        tool.category = 'cross_modal'
        adapter = LegacyToolAdapter(tool, "CROSS_MODAL_ANALYZER", "Cross-Modal Analyzer")
        registry.register_tool(adapter)
        successful.append("CROSS_MODAL_ANALYZER")
        print("   ✅ CrossModalTool registered")
    except Exception as e:
        failed.append(("CROSS_MODAL_ANALYZER", str(e)))
        print(f"   ❌ CrossModalTool failed: {e}")
    
    print("\n4. Testing T15B VectorEmbedderKGAS...")
    try:
        from src.tools.phase1.t15b_vector_embedder_kgas import T15BVectorEmbedderKGAS
        tool = T15BVectorEmbedderKGAS()
        tool.category = 'cross_modal'
        adapter = LegacyToolAdapter(tool, "VECTOR_EMBEDDER", "Vector Embedder KGAS")
        registry.register_tool(adapter)
        successful.append("VECTOR_EMBEDDER")
        print("   ✅ T15BVectorEmbedderKGAS registered")
    except Exception as e:
        failed.append(("VECTOR_EMBEDDER", str(e)))
        print(f"   ❌ T15BVectorEmbedderKGAS failed: {e}")
    
    print("\n5. Testing AsyncTextEmbedder...")
    try:
        from src.tools.phase1.t41_async_text_embedder import AsyncTextEmbedder
        tool = AsyncTextEmbedder()
        tool.category = 'cross_modal'
        adapter = LegacyToolAdapter(tool, "ASYNC_TEXT_EMBEDDER", "Async Text Embedder")
        registry.register_tool(adapter)
        successful.append("ASYNC_TEXT_EMBEDDER")
        print("   ✅ AsyncTextEmbedder registered")
    except Exception as e:
        failed.append(("ASYNC_TEXT_EMBEDDER", str(e)))
        print(f"   ❌ AsyncTextEmbedder failed: {e}")
    
    print("\n6. Testing CrossModalConverter...")
    try:
        from src.analytics.cross_modal_converter import CrossModalConverter
        tool = CrossModalConverter()
        tool.category = 'cross_modal'
        adapter = LegacyToolAdapter(tool, "CROSS_MODAL_CONVERTER", "Cross-Modal Converter")
        registry.register_tool(adapter)
        successful.append("CROSS_MODAL_CONVERTER")
        print("   ✅ CrossModalConverter registered")
    except Exception as e:
        failed.append(("CROSS_MODAL_CONVERTER", str(e)))
        print(f"   ❌ CrossModalConverter failed: {e}")
    
    # Check cross-modal category
    print("\n7. Checking cross-modal category...")
    cross_modal_tools = registry.get_tools_by_category('cross_modal')
    print(f"   Found {len(cross_modal_tools)} tools in cross_modal category")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Successfully registered: {len(successful)}/6 cross-modal tools")
    
    if successful:
        print("\n✅ Registered tools:")
        for tool_id in successful:
            print(f"   - {tool_id}")
    
    if failed:
        print("\n❌ Failed tools:")
        for tool_id, error in failed:
            print(f"   - {tool_id}: {error[:100]}...")
    
    all_tools = registry.list_tools()
    print(f"\nTotal tools in registry: {len(all_tools)}")
    
    return len(successful) == 6

if __name__ == "__main__":
    success = test_cross_modal_simple()
    sys.exit(0 if success else 1)