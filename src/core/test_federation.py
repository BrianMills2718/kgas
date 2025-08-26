#!/usr/bin/env python3
"""
Test Registry Federation - Both registries working together
"""

import sys
from pathlib import Path
sys.path.append('/home/brian/projects/Digimons')

from src.core.registry_federation import FederatedRegistry
from src.core.composition_service import CompositionService
from src.core.adapter_factory import UniversalAdapterFactory
from src.tools.simple_text_loader import SimpleTextLoader

def test_registry_federation():
    """Test that both registries can be queried"""
    
    print("="*60)
    print("REGISTRY FEDERATION TEST")
    print("="*60)
    
    # 1. Set up composition service with a tool
    service = CompositionService()
    service.adapter_factory = UniversalAdapterFactory()
    
    # Register a tool in framework
    tool = SimpleTextLoader()
    service.register_any_tool(tool)
    print("✅ Tool registered in framework via CompositionService")
    
    # 2. Create federated registry
    federation = FederatedRegistry(framework=service.framework)
    print("✅ FederatedRegistry created")
    
    # 3. List tools from both registries
    print("\n1. Tool Discovery:")
    all_tools = federation.list_all_tools()
    
    print(f"   Framework tools ({len(all_tools['framework'])}): {all_tools['framework'][:5]}")
    print(f"   Production tools ({len(all_tools['production'])}): {all_tools['production'][:5]}")
    print(f"   Total tools: {all_tools['total_count']}")
    
    # 4. Test chain discovery from both
    print("\n2. Chain Discovery:")
    chains = federation.discover_all_chains("file", "text")
    
    print(f"   Framework chains: {len(chains['framework'])} found")
    if chains['framework']:
        for chain in chains['framework'][:3]:
            print(f"      {' → '.join(chain)}")
    
    print(f"   Production chains: {len(chains['production'])} found")
    if chains['production']:
        for chain in chains['production'][:3]:
            print(f"      {' → '.join(chain)}")
            
    print(f"   Mixed chains: {len(chains['mixed'])} found")
    
    # 5. Test tool retrieval
    print("\n3. Tool Retrieval:")
    
    # Get from framework
    framework_tool = federation.get_tool("SimpleTextLoader")
    if framework_tool:
        print(f"   ✅ Retrieved from framework: {framework_tool.__class__.__name__}")
    else:
        print("   ❌ Not found in framework")
    
    # Try to get from production (if any registered)
    if all_tools['production']:
        prod_tool_id = all_tools['production'][0]
        prod_tool = federation.get_tool(prod_tool_id)
        if prod_tool:
            print(f"   ✅ Retrieved from production: {prod_tool_id}")
        else:
            print(f"   ⚠️  Could not retrieve {prod_tool_id} from production")
    
    # 6. Verify no interference
    print("\n4. Independence Verification:")
    
    # Count before
    counts_before = federation.get_tool_count()
    
    # Register another tool in framework only
    class AnotherTool:
        tool_id = "AnotherTool"
        def process(self, x): return x
    
    service.register_any_tool(AnotherTool())
    
    # Count after
    counts_after = federation.get_tool_count()
    
    print(f"   Framework before: {counts_before['framework']}, after: {counts_after['framework']}")
    print(f"   Production before: {counts_before['production']}, after: {counts_after['production']}")
    
    if counts_after['framework'] == counts_before['framework'] + 1:
        print("   ✅ Framework registry updated independently")
    
    if counts_after['production'] == counts_before['production']:
        print("   ✅ Production registry unchanged (no interference)")
    
    print("\n" + "="*60)
    print("FEDERATION TEST COMPLETE")
    print("="*60)
    
    # Summary
    success = (
        len(all_tools['framework']) > 0 and
        counts_after['framework'] > counts_before['framework'] and
        counts_after['production'] == counts_before['production']
    )
    
    if success:
        print("✅ Both registries accessible and independent")
    else:
        print("⚠️  Some issues with federation")
        
    return success

if __name__ == "__main__":
    success = test_registry_federation()
    sys.exit(0 if success else 1)