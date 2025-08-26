#!/usr/bin/env python3
"""
Test integration of first real tool through CompositionService
"""

import sys
from pathlib import Path
sys.path.append('/home/brian/projects/Digimons')

from src.core.composition_service import CompositionService
from src.core.adapter_factory import UniversalAdapterFactory

# Import our simple real production tool
from src.tools.simple_text_loader import SimpleTextLoader

def test_first_integration():
    """Test TextLoader through composition service"""
    
    print("="*60)
    print("FIRST TOOL INTEGRATION TEST")
    print("="*60)
    
    # 1. Create composition service
    service = CompositionService()
    service.adapter_factory = UniversalAdapterFactory()
    print("✅ CompositionService created with adapter factory")
    
    # 2. Get a real production tool
    text_loader = SimpleTextLoader()
    print(f"✅ SimpleTextLoader instantiated: {text_loader.__class__.__name__}")
    
    # 3. Register it
    print("\n1. Registering TextLoader...")
    success = service.register_any_tool(text_loader)
    
    if success:
        print("   ✅ TextLoader registered successfully")
    else:
        print("   ❌ Registration failed")
        return False
    
    # 4. Check if discoverable
    print("\n2. Testing discovery...")
    # Import DataType for proper chain discovery
    from data_types import DataType
    chains = service.framework.find_chains(DataType.FILE, DataType.TEXT)
    
    if chains:
        print(f"   ✅ Found {len(chains)} chains")
        for chain in chains:
            print(f"      {' → '.join(chain)}")
    else:
        print("   ❌ No chains discovered")
    
    # Check if SimpleTextLoader is in the framework
    if "SimpleTextLoader" in service.framework.tools:
        print("   ✅ SimpleTextLoader found in framework registry")
    else:
        print("   ❌ SimpleTextLoader not in framework registry")
    
    # 5. Test with a real file
    test_file = Path("/home/brian/projects/Digimons/test_data/medical_article.txt")
    if test_file.exists():
        print(f"\n3. Testing with real file: {test_file.name}")
        print(f"   File size: {test_file.stat().st_size} bytes")
        # Note: Actual execution would need full implementation
        print("   ⚠️  Execution not yet fully implemented")
    else:
        # Create a test file
        test_dir = Path("/home/brian/projects/Digimons/test_data")
        test_dir.mkdir(exist_ok=True)
        test_file = test_dir / "sample.txt"
        test_file.write_text("This is a test file for tool composition framework.")
        print(f"\n3. Created test file: {test_file.name}")
        print(f"   File size: {test_file.stat().st_size} bytes")
    
    # 6. Show metrics
    print("\n4. Composition Metrics:")
    metrics = service.get_metrics()
    for key, value in metrics.items():
        print(f"   {key}: {value}")
    
    # 7. Verify adapter worked
    print("\n5. Adapter Verification:")
    adapted_tool = service.framework.tools.get("SimpleTextLoader")
    if adapted_tool:
        caps = adapted_tool.get_capabilities()
        print(f"   Tool ID: {caps.tool_id}")
        print(f"   Input Type: {caps.input_type}")
        print(f"   Output Type: {caps.output_type}")
        print("   ✅ Tool properly adapted with capabilities")
    else:
        print("   ❌ Tool not found in framework")
    
    print("\n" + "="*60)
    print("INTEGRATION TEST COMPLETE")
    return True

if __name__ == "__main__":
    success = test_first_integration()
    sys.exit(0 if success else 1)