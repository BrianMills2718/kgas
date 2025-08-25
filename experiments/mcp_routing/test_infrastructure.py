#!/usr/bin/env python3
"""
Test MCP Routing Infrastructure

Quick test to verify the mock tools and reference registry are working correctly.
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from mock_tool_generator import MockToolGenerator, ToolCategory
from reference_registry import MockReferenceRegistry, DataType
from test_framework import MockAgent, DirectExposureStrategy, TestScenario


def test_tool_generation():
    """Test mock tool generation"""
    print("🔧 Testing Tool Generation")
    print("-" * 30)
    
    generator = MockToolGenerator()
    tools = generator.generate_all_tools()
    
    print(f"✅ Generated {len(tools)} mock tools")
    
    # Test tool categories
    categories = {}
    for tool in tools:
        category = tool.category.value
        if category not in categories:
            categories[category] = 0
        categories[category] += 1
    
    print(f"\nTools by category:")
    for category, count in categories.items():
        print(f"  {category}: {count} tools")
    
    # Test MCP tool description generation
    sample_tool = tools[0]
    mcp_desc = sample_tool.to_mcp_tool_description()
    print(f"\nSample MCP tool description:")
    print(f"  Name: {mcp_desc['name']}")
    print(f"  Description: {mcp_desc['description'][:60]}...")
    print(f"  Input Schema: {list(mcp_desc['inputSchema']['properties'].keys())}")
    
    return tools


def test_reference_registry():
    """Test reference registry functionality"""
    print("\n🗂️  Testing Reference Registry")
    print("-" * 30)
    
    registry = MockReferenceRegistry()
    
    # Test basic reference creation
    doc_ref = registry.create_reference(
        DataType.DOCUMENT,
        "load_document_pdf",
        simulated_size_mb=2.0
    )
    print(f"✅ Created document reference: {doc_ref}")
    
    # Test operation tracking
    op_id = registry.start_operation("extract_entities_spacy", [doc_ref])
    print(f"✅ Started operation: {op_id}")
    
    # Create derived reference
    entities_ref = registry.create_reference(
        DataType.ENTITIES,
        "extract_entities_spacy",
        source_refs=[doc_ref],
        simulated_size_mb=0.5
    )
    print(f"✅ Created entities reference: {entities_ref}")
    
    # Complete operation
    registry.complete_operation(op_id, [entities_ref])
    print(f"✅ Completed operation")
    
    # Test data access simulation
    data = registry.simulate_data_access(entities_ref)
    print(f"\nSimulated data access:")
    print(f"  Data type: {data['data_type']}")
    print(f"  Quality score: {data['quality_score']:.2f}")
    print(f"  Lineage depth: {data['lineage_depth']}")
    
    # Test lineage tracking
    lineage = registry.get_lineage(entities_ref)
    print(f"  Lineage chain: {' → '.join(lineage)}")
    
    return registry


def test_mock_agent():
    """Test mock agent functionality"""
    print("\n🤖 Testing Mock Agent")
    print("-" * 30)
    
    # Create tools
    generator = MockToolGenerator()
    tools = generator.generate_all_tools()
    
    # Create agent
    agent = MockAgent("test_agent", decision_strategy="optimal")
    agent.set_available_tools(tools[:20])  # Limit to 20 tools for testing
    
    print(f"✅ Created agent with {len(agent.available_tools)} tools")
    print(f"Context usage: {agent.context_usage} characters")
    
    # Test tool selection
    selected_tool = agent.select_tool("load a PDF document")
    if selected_tool:
        print(f"✅ Selected tool: {selected_tool.tool_id}")
        print(f"Tool category: {selected_tool.category.value}")
    else:
        print("❌ No tool selected")
    
    # Test workflow execution
    registry = MockReferenceRegistry()
    
    workflow_steps = [
        {"task": "load document", "input_refs": []},
        {"task": "extract entities", "input_refs": ["doc_ref"]},
        {"task": "build graph", "input_refs": ["entities_ref"]}
    ]
    
    print(f"\n🔄 Executing workflow with {len(workflow_steps)} steps...")
    result = agent.execute_workflow(workflow_steps, registry)
    
    print(f"✅ Workflow execution completed")
    print(f"  Success: {result['success']}")
    print(f"  Completion rate: {result['completion_rate']:.1%}")
    print(f"  Total time: {result['total_time_ms']:.0f}ms")
    print(f"  Steps completed: {result['completed_steps']}/{len(workflow_steps)}")
    
    return agent, result


def test_organization_strategy():
    """Test tool organization strategy"""
    print("\n📊 Testing Organization Strategy")
    print("-" * 30)
    
    generator = MockToolGenerator() 
    all_tools = generator.generate_all_tools()
    
    # Test direct exposure strategy
    strategy = DirectExposureStrategy()
    organized_tools = strategy.organize_tools(all_tools, {"keywords": ["document", "extract"]})
    
    print(f"✅ Direct exposure strategy")
    print(f"  Input tools: {len(all_tools)}")
    print(f"  Output tools: {len(organized_tools)}")
    print(f"  Strategy: {strategy.get_strategy_name()}")
    
    return organized_tools


def run_infrastructure_tests():
    """Run all infrastructure tests"""
    print("🧪 MCP Routing Infrastructure Tests")
    print("=" * 50)
    
    try:
        # Test 1: Tool Generation
        tools = test_tool_generation()
        assert len(tools) > 90, f"Expected >90 tools, got {len(tools)}"
        
        # Test 2: Reference Registry
        registry = test_reference_registry()
        stats = registry.get_registry_stats()
        assert stats['total_references'] > 0, "No references created"
        assert stats['total_operations'] > 0, "No operations tracked"
        
        # Test 3: Mock Agent
        agent, workflow_result = test_mock_agent()
        assert workflow_result['completion_rate'] > 0, "No workflow steps completed"
        
        # Test 4: Organization Strategy
        organized_tools = test_organization_strategy()
        assert len(organized_tools) > 0, "No tools organized"
        
        print(f"\n✅ ALL INFRASTRUCTURE TESTS PASSED!")
        print(f"🎯 Ready to run comprehensive experiments")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Infrastructure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_infrastructure_tests()
    
    if success:
        print(f"\n🚀 Infrastructure is ready!")
        print(f"Next step: Run 'python run_experiments.py' for comprehensive testing")
    else:
        print(f"\n🛠️  Please fix infrastructure issues before running experiments")
        sys.exit(1)