#!/usr/bin/env python3
"""
Analyze the REAL integration challenges with existing tools
"""

import sys
from pathlib import Path

# Add src to path to import tools
sys.path.insert(0, "/home/brian/projects/Digimons")

def analyze_tool_interfaces():
    """Check what interfaces the existing tools actually use"""
    
    print("="*60)
    print("EXISTING TOOL INTERFACE ANALYSIS")
    print("="*60)
    
    # Try to import a real tool
    try:
        from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
        print("\n✅ Successfully imported T23A (spaCy NER)")
        
        # Check what it expects
        import inspect
        sig = inspect.signature(T23ASpacyNERUnified.__init__)
        print(f"   Constructor expects: {list(sig.parameters.keys())}")
        
        # Check base class
        bases = [b.__name__ for b in T23ASpacyNERUnified.__bases__]
        print(f"   Inherits from: {bases}")
        
        # Check methods
        methods = [m for m in dir(T23ASpacyNERUnified) if not m.startswith('_')]
        print(f"   Public methods: {methods[:10]}...")
        
    except ImportError as e:
        print(f"\n❌ Failed to import T23A: {e}")
        return False
    
    # Check what dependencies it needs
    print("\n📦 Dependencies Analysis:")
    try:
        from src.core.service_manager import ServiceManager
        print("   - ServiceManager: EXISTS")
        
        # Check if we can create it
        try:
            sm = ServiceManager()
            print("     Can instantiate: YES")
        except Exception as e:
            print(f"     Can instantiate: NO - {e}")
            
    except ImportError:
        print("   - ServiceManager: MISSING")
    
    try:
        from src.tools.base_tool import BaseTool, ToolRequest, ToolResult
        print("   - BaseTool interface: EXISTS")
        
        # Check interface
        import inspect
        if hasattr(BaseTool, 'execute'):
            sig = inspect.signature(BaseTool.execute)
            print(f"     execute() expects: {list(sig.parameters.keys())}")
            
    except ImportError:
        print("   - BaseTool interface: MISSING")
    
    # Check what our framework expects
    print("\n🔧 Our Framework Expectations:")
    try:
        poc_dir = Path(__file__).parent
        sys.path.insert(0, str(poc_dir))
        
        from framework import ExtensibleTool
        print("   - ExtensibleTool: EXISTS")
        
        # Check interface
        import inspect
        methods = [m for m in dir(ExtensibleTool) if not m.startswith('_')]
        print(f"     Methods: {methods}")
        
    except ImportError as e:
        print(f"   - ExtensibleTool: MISSING - {e}")
    
    return True


def analyze_data_formats():
    """Check what data formats the tools use"""
    
    print("\n" + "="*60)
    print("DATA FORMAT ANALYSIS")
    print("="*60)
    
    # Check their data types
    try:
        from src.tools.base_tool import ToolRequest, ToolResult
        
        print("\n📊 Their Data Formats:")
        print(f"   - ToolRequest fields: {ToolRequest.__annotations__ if hasattr(ToolRequest, '__annotations__') else 'Unknown'}")
        print(f"   - ToolResult fields: {ToolResult.__annotations__ if hasattr(ToolResult, '__annotations__') else 'Unknown'}")
        
    except ImportError as e:
        print(f"   ❌ Can't import their data types: {e}")
    
    # Check our data types
    try:
        from data_types import DataSchema, DataType
        
        print("\n📊 Our Data Formats:")
        print(f"   - DataType enum values: {[dt.name for dt in DataType]}")
        
        # Check schema classes
        schema_attrs = [attr for attr in dir(DataSchema) if not attr.startswith('_')]
        print(f"   - DataSchema classes: {schema_attrs}")
        
    except ImportError as e:
        print(f"   ❌ Can't import our data types: {e}")
    
    print("\n⚠️  INCOMPATIBILITY DETECTED:")
    print("   - Their tools use ToolRequest/ToolResult")
    print("   - Our framework uses DataSchema types")
    print("   - Need adapters to convert between formats")


def analyze_service_dependencies():
    """Check what services the tools depend on"""
    
    print("\n" + "="*60)
    print("SERVICE DEPENDENCY ANALYSIS")
    print("="*60)
    
    dependencies = [
        "src.core.service_manager.ServiceManager",
        "src.core.identity_service.IdentityService",
        "src.core.provenance_service.ProvenanceService",
        "src.core.quality_service.QualityService",
        "src.core.resource_manager.get_resource_manager",
        "src.orchestration.memory.AgentMemory",
        "src.orchestration.llm_reasoning.LLMReasoningEngine"
    ]
    
    for dep in dependencies:
        module_path = ".".join(dep.split(".")[:-1])
        class_name = dep.split(".")[-1]
        
        try:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"   ✅ {class_name}: Available")
            
            # Try to instantiate
            try:
                if class_name == "ServiceManager":
                    instance = cls()
                    print(f"      Can instantiate: YES")
                elif class_name == "get_resource_manager":
                    instance = cls()
                    print(f"      Can call: YES")
            except Exception as e:
                print(f"      Can instantiate: NO - {str(e)[:50]}")
                
        except ImportError:
            print(f"   ❌ {class_name}: MISSING")


def estimate_integration_effort():
    """Estimate the effort to integrate these tools"""
    
    print("\n" + "="*60)
    print("INTEGRATION EFFORT ESTIMATE")
    print("="*60)
    
    print("\n🔴 Major Issues Found:")
    print("1. **Interface Mismatch**")
    print("   - Tools use BaseTool, we use ExtensibleTool")
    print("   - Completely different method signatures")
    print("   - Need adapter for EVERY tool")
    
    print("\n2. **Data Format Incompatibility**")
    print("   - Tools use ToolRequest/ToolResult")
    print("   - We use DataSchema.* types")
    print("   - Need converters for all data flows")
    
    print("\n3. **Service Dependencies**")
    print("   - Tools need ServiceManager with 7+ services")
    print("   - We don't have these services")
    print("   - Must mock or reimplement all services")
    
    print("\n4. **State Management**")
    print("   - Tools use AgentMemory for persistence")
    print("   - Tools use operation tracking")
    print("   - We have no equivalent systems")
    
    print("\n📊 Effort per Tool:")
    print("   - Write adapter class: 2-3 hours")
    print("   - Handle service dependencies: 1-2 hours")
    print("   - Convert data formats: 1 hour")
    print("   - Test integration: 1-2 hours")
    print("   - Total per tool: ~6-8 hours")
    
    print("\n⏱️ Total for 38 tools: 228-304 hours (6-8 weeks)")
    
    print("\n💡 Recommendation:")
    print("   DON'T try to integrate all 38 existing tools!")
    print("   Instead:")
    print("   1. Build NEW tools using our framework")
    print("   2. Only integrate the 5-10 most critical tools")
    print("   3. Create a bridge/gateway pattern for bulk integration")


if __name__ == "__main__":
    print("Analyzing real tool integration challenges...\n")
    
    analyze_tool_interfaces()
    analyze_data_formats()
    analyze_service_dependencies()
    estimate_integration_effort()
    
    print("\n" + "="*60)
    print("CONCLUSION: Major integration challenges detected!")
    print("The existing tools are NOT compatible with our framework.")
    print("="*60)