#!/usr/bin/env python3
"""Check what chains can be discovered"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from poc.registry import ToolRegistry
from poc.tools.text_loader import TextLoader
from poc.tools.entity_extractor import EntityExtractor
from poc.tools.graph_builder import GraphBuilder
from poc.data_types import DataType

# Also check if we can add more tools
class DummySentimentAnalyzer:
    """Mock sentiment analyzer to test chain discovery"""
    @property
    def tool_id(self):
        return "SentimentAnalyzer"
    
    @property
    def input_type(self):
        return DataType.TEXT
    
    @property
    def output_type(self):
        return DataType.SENTIMENT if hasattr(DataType, 'SENTIMENT') else DataType.METRICS
    
    def process(self, input_data):
        pass

def main():
    registry = ToolRegistry()
    
    # Register core tools
    registry.register(TextLoader())
    registry.register(EntityExtractor())
    registry.register(GraphBuilder())
    
    print("="*60)
    print("CURRENT TOOL REGISTRY")
    print("="*60)
    print("\nRegistered tools:")
    for tool_id, tool in registry.tools.items():
        print(f"  {tool_id}: {tool.input_type} → {tool.output_type}")
    
    print("\n" + "="*60)
    print("CHAIN DISCOVERY EXAMPLES")
    print("="*60)
    
    # Test various chain discoveries
    test_cases = [
        (DataType.FILE, DataType.TEXT),
        (DataType.FILE, DataType.ENTITIES),
        (DataType.FILE, DataType.GRAPH),
        (DataType.TEXT, DataType.GRAPH),
        (DataType.ENTITIES, DataType.GRAPH),
    ]
    
    for start, end in test_cases:
        chains = registry.find_chains(start, end)
        print(f"\n{start.value} → {end.value}:")
        if chains:
            for i, chain in enumerate(chains, 1):
                print(f"  {i}. {' → '.join(chain)}")
        else:
            print("  No chains found")
    
    print("\n" + "="*60)
    print("EXTENSIBILITY TEST")
    print("="*60)
    
    # What happens if we add a new tool?
    print("\nAdding hypothetical SentimentAnalyzer (TEXT → METRICS)...")
    
    # Check if we can create branching paths
    print("\nPotential branching paths from TEXT:")
    print("  - TEXT → ENTITIES → GRAPH (entity analysis)")
    print("  - TEXT → SENTIMENT (if we had SentimentAnalyzer)")
    print("  - TEXT → SUMMARY (if we had Summarizer)")
    
    print("\n" + "="*60)
    print("COMPATIBILITY MATRIX")
    print("="*60)
    
    tools = list(registry.tools.values())
    tool_names = [t.tool_id[:8] for t in tools]
    
    print("\n" + " "*12 + " | ".join(f"{name:^8}" for name in tool_names))
    print("-"*12 + "-+-" + "-+-".join("-"*8 for _ in tool_names))
    
    for i, tool1 in enumerate(tools):
        row = f"{tool1.tool_id[:11]:11} |"
        for j, tool2 in enumerate(tools):
            if tool1.output_type == tool2.input_type:
                row += "    ✓    |"
            else:
                row += "         |"
        print(row)
    
    print("\n" + "="*60)
    print("KEY FINDINGS")
    print("="*60)
    
    print("\n✅ What Works:")
    print("  - Automatic chain discovery")
    print("  - Type-based compatibility checking")
    print("  - Clear tool interfaces")
    
    print("\n⚠️  Current Limitations:")
    print("  - Only 3 tools implemented")
    print("  - No branching/merging support")
    print("  - No parallel execution")
    print("  - Fixed to specific data types")
    
    print("\n🎯 To Build Full System:")
    print("  1. Add remaining 35 tools")
    print("  2. Support branching workflows")
    print("  3. Add async/parallel execution")
    print("  4. Handle larger data (>10MB)")

if __name__ == "__main__":
    main()