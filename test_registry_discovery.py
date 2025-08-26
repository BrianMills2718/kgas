#!/usr/bin/env python3
"""Test that cross-modal tools are discoverable in registry."""

import os
import sys
sys.path.append('/home/brian/projects/Digimons')

# Set environment variables
os.environ['NEO4J_PASSWORD'] = 'devpassword'
os.environ['NEO4J_URI'] = 'bolt://localhost:7687'
os.environ['NEO4J_USER'] = 'neo4j'

from src.core.tool_contract import get_tool_registry

registry = get_tool_registry()

# Check all tools
all_tools = registry.list_tools()
print(f"Total tools in registry: {len(all_tools)}")
print(f"Tool IDs: {sorted(all_tools)}")

# Check cross-modal category
cross_modal_tools = registry.get_tools_by_category('cross_modal')
print(f"\nCross-modal tools ({len(cross_modal_tools)}):")
for tool in cross_modal_tools:
    print(f"  - {tool.tool_id}: {tool.tool_name}")

# Verify expected tools
expected = ["GRAPH_TABLE_EXPORTER", "MULTI_FORMAT_EXPORTER", "CROSS_MODAL_ANALYZER", 
            "ASYNC_TEXT_EMBEDDER", "CROSS_MODAL_CONVERTER"]
found = [tool for tool in expected if tool in all_tools]
print(f"\nExpected tools found: {len(found)}/{len(expected)}")
for tool_id in found:
    print(f"  ✅ {tool_id}")