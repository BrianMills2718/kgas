#!/usr/bin/env python3
"""Test script to verify cross-modal tools are registered and accessible."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from src.agents.register_tools_for_workflow import register_all_tools
from src.core.tool_contract import get_tool_registry

def test_cross_modal_registration():
    """Test that cross-modal tools are properly registered."""
    
    print("=" * 60)
    print("CROSS-MODAL TOOL REGISTRATION TEST")
    print("=" * 60)
    
    # Register all tools
    print("\n1. Registering all tools...")
    registered_tools = register_all_tools()
    
    # Get the registry
    registry = get_tool_registry()
    
    # Check for cross-modal tools
    print("\n2. Checking for cross-modal tools...")
    cross_modal_tools = registry.get_tools_by_category('cross_modal')
    
    print(f"\n✅ Found {len(cross_modal_tools)} cross-modal tools:")
    for tool in cross_modal_tools:
        print(f"   - {tool.tool_id}: {tool.tool_name}")
    
    # Check for specific expected tools
    print("\n3. Verifying expected cross-modal tools...")
    expected_tools = [
        "GRAPH_TABLE_EXPORTER",
        "MULTI_FORMAT_EXPORTER", 
        "CROSS_MODAL_ANALYZER",
        "VECTOR_EMBEDDER",
        "ASYNC_TEXT_EMBEDDER",
        "CROSS_MODAL_CONVERTER"
    ]
    
    all_tool_ids = registry.list_tools()
    found = []
    missing = []
    
    for tool_id in expected_tools:
        if tool_id in all_tool_ids:
            found.append(tool_id)
            print(f"   ✅ {tool_id} - FOUND")
        else:
            missing.append(tool_id)
            print(f"   ❌ {tool_id} - MISSING")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total tools registered: {len(all_tool_ids)}")
    print(f"Cross-modal tools found: {len(cross_modal_tools)}")
    print(f"Expected tools found: {len(found)}/{len(expected_tools)}")
    
    if missing:
        print(f"\n⚠️ Missing tools: {', '.join(missing)}")
        print("\nPossible reasons:")
        print("- Import errors (missing dependencies)")
        print("- Tools not implemented yet")
        print("- Registration errors")
    else:
        print("\n🎉 All expected cross-modal tools are registered!")
    
    # Test tool discovery
    print("\n4. Testing tool discovery...")
    print("\nTools by category:")
    for category in ['graph', 'table', 'vector', 'cross_modal']:
        category_tools = registry.get_tools_by_category(category)
        print(f"   {category}: {len(category_tools)} tools")
    
    return len(found) == len(expected_tools)

if __name__ == "__main__":
    success = test_cross_modal_registration()
    sys.exit(0 if success else 1)