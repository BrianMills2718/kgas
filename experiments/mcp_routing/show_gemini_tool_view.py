#!/usr/bin/env python3
"""
Show exactly what Gemini sees when looking at available tools
"""

import json
from mock_tool_generator import MockToolGenerator

def show_gemini_tool_view():
    """Display the exact tool information that gets sent to Gemini"""
    
    print("=" * 80)
    print("🔍 WHAT GEMINI SEES: TOOL INFORMATION")
    print("=" * 80)
    
    # Generate tools
    tool_generator = MockToolGenerator()
    all_tools = tool_generator.generate_all_tools()
    
    # Format tools exactly as sent to Gemini
    formatted_tools = []
    for tool in all_tools:
        formatted_tools.append({
            "name": tool.tool_id,
            "description": tool.description,
            "category": tool.category.value,
            "inputs": tool.input_types,
            "outputs": tool.output_types,
            "complexity": tool.complexity_score
        })
    
    print(f"📊 TOTAL TOOLS AVAILABLE: {len(formatted_tools)}")
    print()
    
    # Show first 20 tools as example
    print("📋 SAMPLE TOOLS (first 20 of 100+):")
    print("-" * 80)
    
    for i, tool in enumerate(formatted_tools[:20]):
        print(f"\n{i+1:2d}. {tool['name']}")
        print(f"    Description: {tool['description']}")
        print(f"    Category: {tool['category']}")
        print(f"    Inputs: {', '.join(tool['inputs'])}")
        print(f"    Outputs: {', '.join(tool['outputs'])}")
        print(f"    Complexity: {tool['complexity']:.1f}")
    
    print(f"\n... and {len(formatted_tools) - 20} more tools")
    
    print("\n" + "=" * 80)
    print("📤 EXACT JSON SENT TO GEMINI (first 5 tools):")
    print("=" * 80)
    
    # Show exact JSON format
    sample_json = json.dumps(formatted_tools[:5], indent=2)
    print(sample_json)
    
    print("\n" + "=" * 80)
    print("🎯 TOOL CATEGORIES BREAKDOWN:")
    print("=" * 80)
    
    # Category breakdown
    category_counts = {}
    for tool in formatted_tools:
        category = tool['category']
        category_counts[category] = category_counts.get(category, 0) + 1
    
    for category, count in sorted(category_counts.items()):
        print(f"  {category}: {count} tools")
    
    print("\n" + "=" * 80)
    print("🔍 SAMPLE TOOLS BY CATEGORY:")
    print("=" * 80)
    
    # Show samples from each category
    for category in category_counts.keys():
        category_tools = [t for t in formatted_tools if t['category'] == category]
        print(f"\n📂 {category.upper()}:")
        for tool in category_tools[:3]:  # Show first 3 from each category
            print(f"  • {tool['name']}: {tool['description'][:80]}...")
        if len(category_tools) > 3:
            print(f"  ... and {len(category_tools) - 3} more {category} tools")
    
    print("\n" + "=" * 80)
    print("💡 WHAT GEMINI NEEDS TO FIGURE OUT:")
    print("=" * 80)
    
    print("Given this tool information, Gemini must:")
    print("1. 🎯 Understand what each tool actually does from description")
    print("2. 🔗 Figure out logical workflow sequences (inputs/outputs)")
    print("3. 🏗️  Design efficient pipelines for complex tasks")
    print("4. ⚖️  Balance between general vs specialized tools")
    print("5. 📊 Optimize for both completeness and efficiency")
    
    print(f"\nThis is a complex reverse-engineering task with {len(formatted_tools)} options!")
    
    return formatted_tools

if __name__ == "__main__":
    tools = show_gemini_tool_view()