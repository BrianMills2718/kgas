#!/usr/bin/env python3
"""
Demonstration of Type-Based Tool Compatibility System

This shows how tools can be chained based on data type transformations,
creating a directed graph of valid tool sequences.
"""

import json
import logging
from typing import List, Dict, Any

from data_types import DataType
from transformation_matrix import TRANSFORMATION_MATRIX, register_kgas_tools
from type_based_tools import create_tool_registry, ToolResult

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def demonstrate_automatic_chaining():
    """Show how the system automatically finds valid tool chains"""
    
    print("\n" + "="*60)
    print("AUTOMATIC TOOL CHAINING")
    print("="*60)
    
    # Register all transformations
    register_kgas_tools()
    
    # Find all paths from raw text to different outputs
    start_type = DataType.RAW_TEXT
    end_types = [
        DataType.TABLE_FORMAT,
        DataType.ANALYZED_RESULTS,
        DataType.NEO4J_TRANSACTION,
        DataType.VECTOR_EMBEDDINGS
    ]
    
    for end_type in end_types:
        paths = TRANSFORMATION_MATRIX.find_all_paths(start_type, end_type)
        print(f"\nPaths from {start_type.value} to {end_type.value}:")
        
        if paths:
            for i, path in enumerate(paths, 1):
                # Describe what each step does
                descriptions = []
                for j in range(len(path)):
                    tool = TRANSFORMATION_MATRIX.transformations[path[j]]
                    descriptions.append(f"{tool.tool_name}")
                
                print(f"  Path {i}: {' → '.join(path)}")
                print(f"          {' → '.join(descriptions)}")
        else:
            print(f"  No paths found!")


def demonstrate_tool_execution_chain():
    """Execute an actual chain of tools with real data flow"""
    
    print("\n" + "="*60)
    print("TOOL EXECUTION CHAIN")
    print("="*60)
    
    # Create tool instances
    tools = create_tool_registry()
    
    # Start with raw text
    input_data = {
        "text": "Dr. Jane Smith from MIT published groundbreaking research on quantum computing. "
                "She collaborates with Prof. John Doe at Stanford University. "
                "Their work has been cited by researchers at Google and Microsoft."
    }
    
    # Define the chain we want to execute
    chain = ["T23C", "T31", "T68", "T91"]
    
    print(f"\nExecuting chain: {' → '.join(chain)}")
    print("-" * 40)
    
    current_data = input_data
    current_type = DataType.RAW_TEXT
    
    for tool_id in chain:
        tool = tools.get(tool_id)
        if not tool:
            print(f"✗ Tool {tool_id} not found!")
            break
        
        print(f"\n{tool_id}: {tool.tool_name}")
        print(f"  Input type: {tool.input_type.value}")
        print(f"  Output type: {tool.output_type.value}")
        
        # Execute the tool
        result = tool.execute(current_data)
        
        if result.success:
            print(f"  ✓ Success! Execution time: {result.execution_time:.3f}s")
            
            # Show what was produced
            if result.output_type == DataType.EXTRACTED_DATA:
                entities = result.output_data.get("entities", [])
                relationships = result.output_data.get("relationships", [])
                print(f"    Extracted: {len(entities)} entities, {len(relationships)} relationships")
                
            elif result.output_type == DataType.GRAPH_STRUCTURE:
                nodes = result.output_data.get("nodes", [])
                edges = result.output_data.get("edges", [])
                print(f"    Built graph: {len(nodes)} nodes, {len(edges)} edges")
                
            elif result.output_type == DataType.ENRICHED_GRAPH:
                metrics = result.output_data.get("metrics", {})
                print(f"    Enriched with metrics: {list(metrics.keys())}")
                
            elif result.output_type == DataType.TABLE_FORMAT:
                rows = result.output_data.get("rows", [])
                print(f"    Converted to table: {len(rows)} rows")
            
            # Update for next tool
            current_data = result.output_data
            current_type = result.output_type
            
        else:
            print(f"  ✗ Failed: {result.error}")
            break
    
    print("\n" + "-" * 40)
    print("Chain execution complete!")


def demonstrate_compatibility_discovery():
    """Show how tools discover what they're compatible with"""
    
    print("\n" + "="*60)
    print("COMPATIBILITY DISCOVERY")
    print("="*60)
    
    tools = create_tool_registry()
    
    print("\nTool Compatibility Map:")
    print("-" * 40)
    
    for tool_id, tool in tools.items():
        compatible = tool.get_compatible_tools()
        print(f"\n{tool_id} ({tool.input_type.value} → {tool.output_type.value})")
        
        if compatible:
            print(f"  Can connect to:")
            for next_tool in compatible:
                next_tool_obj = TRANSFORMATION_MATRIX.transformations.get(next_tool)
                if next_tool_obj:
                    print(f"    → {next_tool}: {next_tool_obj.tool_name}")
        else:
            print(f"  No compatible tools (end of chain)")


def demonstrate_matrix_visualization():
    """Visualize the transformation matrix"""
    
    print("\n" + "="*60)
    print("TRANSFORMATION MATRIX VISUALIZATION")
    print("="*60)
    
    register_kgas_tools()
    
    print("\n" + TRANSFORMATION_MATRIX.get_matrix_visualization())
    
    print("\n\nLegend:")
    print("  - : No transformation exists")
    print("  Tool ID: Single tool performs this transformation")
    print("  Number: Multiple tools can perform this transformation")


def demonstrate_dynamic_path_finding():
    """Show how the system finds optimal paths dynamically"""
    
    print("\n" + "="*60)
    print("DYNAMIC PATH FINDING")
    print("="*60)
    
    # User specifies what they have and what they want
    scenarios = [
        {
            "have": DataType.RAW_TEXT,
            "want": DataType.TABLE_FORMAT,
            "description": "Convert document to table"
        },
        {
            "have": DataType.RAW_TEXT,
            "want": DataType.NEO4J_TRANSACTION,
            "description": "Load document into Neo4j"
        },
        {
            "have": DataType.GRAPH_STRUCTURE,
            "want": DataType.SQLITE_RECORDS,
            "description": "Export graph to SQLite"
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['description']}:")
        print(f"  From: {scenario['have'].value}")
        print(f"  To: {scenario['want'].value}")
        
        # Find shortest path
        shortest = TRANSFORMATION_MATRIX.find_shortest_path(
            scenario['have'], 
            scenario['want']
        )
        
        if shortest:
            print(f"  Shortest path: {' → '.join(shortest)}")
            
            # Validate the path
            valid, error = TRANSFORMATION_MATRIX.validate_chain(shortest)
            print(f"  Validation: {'✓ Valid' if valid else f'✗ {error}'}")
        else:
            print(f"  No path found!")
        
        # Show all alternatives
        all_paths = TRANSFORMATION_MATRIX.find_all_paths(
            scenario['have'],
            scenario['want']
        )
        
        if len(all_paths) > 1:
            print(f"  Alternative paths ({len(all_paths) - 1} more):")
            for path in all_paths[1:3]:  # Show up to 2 alternatives
                print(f"    • {' → '.join(path)}")


def main():
    """Run all demonstrations"""
    
    print("╔" + "="*58 + "╗")
    print("║     TYPE-BASED TOOL COMPATIBILITY DEMONSTRATION         ║")
    print("╚" + "="*58 + "╝")
    
    print("\nThis demonstrates how tools can be chained based on")
    print("data type transformations, creating a directed graph")
    print("of valid tool sequences.")
    
    # Run demonstrations
    demonstrate_matrix_visualization()
    demonstrate_automatic_chaining()
    demonstrate_compatibility_discovery()
    demonstrate_tool_execution_chain()
    demonstrate_dynamic_path_finding()
    
    # Show statistics
    print("\n" + "="*60)
    print("SYSTEM STATISTICS")
    print("="*60)
    
    stats = TRANSFORMATION_MATRIX.get_statistics()
    print(f"\nTotal tools registered: {stats['total_tools']}")
    print(f"Total data types: {stats['total_types']}")
    print(f"\nReachability (number of paths):")
    for route, count in stats['reachability'].items():
        print(f"  {route}: {count} path(s)")
    
    print("\n" + "="*60)
    print("CONCLUSION")
    print("="*60)
    
    print("\n✅ The type-based transformation matrix enables:")
    print("  1. Automatic discovery of valid tool chains")
    print("  2. Multiple paths to achieve the same goal")
    print("  3. Clear compatibility based on data types")
    print("  4. No hardcoded tool sequences")
    print("  5. Easy addition of new tools")
    
    print("\n🎯 Any tool that transforms data from type A to type B")
    print("   can be part of a chain, regardless of implementation!")


if __name__ == "__main__":
    main()