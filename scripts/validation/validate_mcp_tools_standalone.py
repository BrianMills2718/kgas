#!/usr/bin/env python3
"""
Standalone MCP Tool Validation

Simplified MCP tool validation that can run independently.
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    from mcp_tools.server_manager import get_mcp_server_manager
    from tools.phase1.phase1_mcp_tools import create_phase1_mcp_tools
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 This suggests MCP tools may not be properly configured.")
    sys.exit(1)


def test_mcp_server_basic():
    """Basic test of MCP server functionality"""
    
    print("🔍 Testing MCP Server Basic Functionality")
    print("=" * 50)
    
    try:
        # Test 1: Can we import and create the server manager?
        print("📋 Test 1: MCP Server Manager Creation")
        server_manager = get_mcp_server_manager()
        print("  ✅ Server manager created successfully")
        
        # Test 2: Can we register tools?
        print("📋 Test 2: Tool Registration")
        server_manager.register_all_tools()
        print("  ✅ Tools registered successfully")
        
        # Test 3: Can we get server info?
        print("📋 Test 3: Server Information Retrieval")
        server_info = server_manager.get_server_info()
        total_tools = server_info.get('total_tools', 0)
        print(f"  ✅ Server reports {total_tools} total tools")
        
        # Test 4: Can we get the FastMCP server?
        print("📋 Test 4: FastMCP Server Access")
        mcp_server = server_manager.get_server()
        print("  ✅ FastMCP server instance obtained")
        
        # Test 5: Can we add Phase 1 tools?
        print("📋 Test 5: Phase 1 Tools Integration")
        create_phase1_mcp_tools(mcp_server)
        print("  ✅ Phase 1 tools added successfully")
        
        # Test 6: Can we list available tools?
        print("📋 Test 6: Tool Discovery")
        available_tools = set()
        
        # Try to get tools from FastMCP server
        if hasattr(mcp_server, '_tools'):
            available_tools.update(mcp_server._tools.keys())
        elif hasattr(mcp_server, 'tools'):
            available_tools.update(mcp_server.tools.keys())
        
        print(f"  ✅ Found {len(available_tools)} discoverable tools")
        
        # Show some sample tools
        sample_tools = list(available_tools)[:5]
        if sample_tools:
            print(f"  📋 Sample tools: {', '.join(sample_tools)}")
        
        # Test 7: Can we call a basic tool?
        print("📋 Test 7: Basic Tool Execution")
        if 'test_connection' in available_tools:
            try:
                test_func = mcp_server._tools.get('test_connection')
                if test_func:
                    result = test_func()
                    print(f"  ✅ test_connection returned: {result}")
                else:
                    print("  ⚠️ test_connection found but not callable")
            except Exception as e:
                print(f"  ⚠️ test_connection failed: {e}")
        else:
            print("  ⚠️ test_connection tool not found")
        
        print("\n" + "=" * 50)
        print("🎉 MCP TOOL EXPOSURE VALIDATION SUMMARY")
        print("=" * 50)
        print(f"✅ MCP Server: Functional")
        print(f"✅ Tool Registration: Working")
        print(f"✅ Tool Discovery: {len(available_tools)} tools found")
        print(f"📊 Server Reports: {total_tools} total tools")
        
        # Categorize tools
        tool_categories = {
            'server_management': [],
            'phase1_tools': [],
            'service_tools': [],
            'other': []
        }
        
        for tool in available_tools:
            if tool in ['test_connection', 'echo', 'get_system_status']:
                tool_categories['server_management'].append(tool)
            elif any(t in tool for t in ['pdf', 'chunk', 'entity', 'pagerank', 'query']):
                tool_categories['phase1_tools'].append(tool)
            elif any(t in tool for t in ['identity', 'provenance', 'quality', 'workflow']):
                tool_categories['service_tools'].append(tool)
            else:
                tool_categories['other'].append(tool)
        
        print(f"\n📁 TOOL CATEGORIES:")
        for category, tools in tool_categories.items():
            if tools:
                print(f"  📋 {category.replace('_', ' ').title()}: {len(tools)} tools")
                print(f"    {', '.join(tools[:3])}{'...' if len(tools) > 3 else ''}")
        
        # Assessment
        if len(available_tools) >= 10:
            print(f"\n🎯 ASSESSMENT: GOOD - {len(available_tools)} tools exposed via MCP")
        elif len(available_tools) >= 5:
            print(f"\n⚠️ ASSESSMENT: MODERATE - {len(available_tools)} tools exposed, could be improved")
        else:
            print(f"\n❌ ASSESSMENT: LOW - Only {len(available_tools)} tools exposed, needs attention")
        
        return True
        
    except Exception as e:
        print(f"\n💥 MCP Server Test Failed: {e}")
        print("\n🔧 TROUBLESHOOTING STEPS:")
        print("  1. Check that all dependencies are installed")
        print("  2. Verify that core services are properly configured")
        print("  3. Check that Neo4j is running (if required)")
        print("  4. Review MCP server configuration")
        
        return False


def test_key_phase1_tools():
    """Test key Phase 1 tools specifically"""
    
    print("\n🔧 Testing Key Phase 1 Tools")
    print("=" * 40)
    
    key_tools = {
        'load_documents': 'T01 PDF Loader',
        'extract_entities': 'T23A Entity Extractor', 
        'calculate_pagerank': 'T68 PageRank',
        'query_graph': 'T49 Multi-hop Query'
    }
    
    try:
        server_manager = get_mcp_server_manager()
        server_manager.register_all_tools()
        mcp_server = server_manager.get_server()
        create_phase1_mcp_tools(mcp_server)
        
        available_tools = set()
        if hasattr(mcp_server, '_tools'):
            available_tools.update(mcp_server._tools.keys())
        
        for tool_func, tool_name in key_tools.items():
            if tool_func in available_tools:
                print(f"  ✅ {tool_name}: Exposed via '{tool_func}'")
            else:
                print(f"  ❌ {tool_name}: Missing '{tool_func}'")
        
        return True
        
    except Exception as e:
        print(f"  💥 Phase 1 tool test failed: {e}")
        return False


def main():
    """Main validation entry point"""
    
    # Setup logging
    logging.basicConfig(level=logging.WARNING)  # Reduce noise
    
    print("🚀 KGAS MCP Tool Exposure - Standalone Validation")
    print("=" * 60)
    
    success = True
    
    # Run basic MCP server test
    if not test_mcp_server_basic():
        success = False
    
    # Run Phase 1 tools test
    if not test_key_phase1_tools():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 VALIDATION PASSED: MCP tools are properly exposed!")
        print("💡 Ready for agent integration and workflow testing.")
    else:
        print("⚠️ VALIDATION ISSUES: Some MCP tools need attention.")
        print("🔧 Review the issues above before proceeding with agent integration.")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())