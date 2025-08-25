#!/usr/bin/env python3
"""
Tool Interface Audit - Phase 1 of CLAUDE.md implementation
Determines which ToolRequest interface each vertical slice tool uses
"""
import sys
import os
sys.path.append('/home/brian/projects/Digimons')

import ast
import importlib
import inspect
from pathlib import Path

def audit_tool_interfaces():
    """Audit all 8 vertical slice tools to determine their interface usage"""
    
    print("🔍 TOOL INTERFACE AUDIT - PHASE 1")
    print("=" * 60)
    
    tools = [
        ("T01", "src/tools/phase1/t01_pdf_loader_unified.py"),
        ("T15A", "src/tools/phase1/t15a_text_chunker_unified.py"),
        ("T23A", "src/tools/phase1/t23a_spacy_ner_unified.py"),
        ("T27", "src/tools/phase1/t27_relationship_extractor_unified.py"),
        ("T31", "src/tools/phase1/t31_entity_builder_unified.py"),
        ("T34", "src/tools/phase1/t34_edge_builder_unified.py"),
        ("T68", "src/tools/phase1/t68_pagerank_unified.py"),
        ("T49", "src/tools/phase1/t49_multihop_query_unified.py")
    ]
    
    audit_results = {}
    
    for tool_id, file_path in tools:
        print(f"\nAuditing {tool_id}...")
        audit_results[tool_id] = audit_single_tool(tool_id, file_path)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 AUDIT SUMMARY")
    print("=" * 60)
    
    # Count interface usage
    tool_contract_users = []
    base_tool_users = []
    mixed_users = []
    unknown_users = []
    
    for tool_id, result in audit_results.items():
        if result['uses_tool_contract'] and not result['uses_base_tool']:
            tool_contract_users.append(tool_id)
        elif result['uses_base_tool'] and not result['uses_tool_contract']:
            base_tool_users.append(tool_id)
        elif result['uses_tool_contract'] and result['uses_base_tool']:
            mixed_users.append(tool_id)
        else:
            unknown_users.append(tool_id)
    
    print(f"\n📌 Interface Usage:")
    print(f"   tool_contract.ToolRequest only: {tool_contract_users}")
    print(f"   base_tool.ToolRequest only: {base_tool_users}")
    print(f"   Mixed usage: {mixed_users}")
    print(f"   Unknown: {unknown_users}")
    
    # Detailed analysis
    print("\n📋 Detailed Analysis:")
    for tool_id, result in audit_results.items():
        print(f"\n{tool_id}:")
        print(f"   Imports from tool_contract: {result['uses_tool_contract']}")
        print(f"   Imports from base_tool: {result['uses_base_tool']}")
        print(f"   Inherits from BaseTool: {result['inherits_basetool']}")
        print(f"   Execute signature: {result['execute_signature']}")
        if result['execute_expectations']:
            print(f"   Execute expects: {', '.join(result['execute_expectations'])}")
    
    # Migration plan
    print("\n" + "=" * 60)
    print("🔧 MIGRATION PLAN")
    print("=" * 60)
    
    print("\n1. Current State:")
    print("   - Multiple incompatible ToolRequest definitions")
    print("   - Tools cannot pass data to each other")
    print("   - No consistent interface across pipeline")
    
    print("\n2. Target State:")
    print("   - All tools use base_tool.ToolRequest")
    print("   - Consistent execute() signatures")
    print("   - Data flows seamlessly through pipeline")
    
    print("\n3. Migration Steps:")
    for tool_id in tool_contract_users:
        print(f"   - {tool_id}: Remove tool_contract import, use base_tool.ToolRequest")
    for tool_id in mixed_users:
        print(f"   - {tool_id}: Consolidate to base_tool.ToolRequest only")
    
    return audit_results

def audit_single_tool(tool_id, file_path):
    """Audit a single tool's interface usage"""
    
    result = {
        'uses_tool_contract': False,
        'uses_base_tool': False,
        'inherits_basetool': False,
        'execute_signature': None,
        'execute_expectations': []
    }
    
    try:
        # Read file content
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Parse AST
        tree = ast.parse(content)
        
        # Check imports
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and 'tool_contract' in node.module:
                    result['uses_tool_contract'] = True
                if node.module and 'base_tool' in node.module:
                    result['uses_base_tool'] = True
        
        # Check class inheritance
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == 'BaseTool':
                        result['inherits_basetool'] = True
                
                # Check execute method
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == 'execute':
                        # Get signature
                        args = [arg.arg for arg in item.args.args]
                        result['execute_signature'] = f"execute({', '.join(args)})"
                        
                        # Analyze what execute expects from request
                        result['execute_expectations'] = analyze_execute_body(item)
        
        print(f"   ✅ Analyzed {tool_id}")
        
    except Exception as e:
        print(f"   ❌ Failed to analyze {tool_id}: {e}")
    
    return result

def analyze_execute_body(func_node):
    """Analyze execute method body to see what it expects from request"""
    expectations = set()
    
    for node in ast.walk(func_node):
        if isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name) and node.value.id == 'request':
                expectations.add(f"request.{node.attr}")
    
    return sorted(list(expectations))

if __name__ == "__main__":
    audit_results = audit_tool_interfaces()
    
    # Save results for next phase
    import json
    with open('/tmp/tool_interface_audit.json', 'w') as f:
        # Convert sets to lists for JSON serialization
        serializable_results = {}
        for tool_id, result in audit_results.items():
            serializable_results[tool_id] = {
                'uses_tool_contract': result['uses_tool_contract'],
                'uses_base_tool': result['uses_base_tool'],
                'inherits_basetool': result['inherits_basetool'],
                'execute_signature': result['execute_signature'],
                'execute_expectations': result['execute_expectations']
            }
        json.dump(serializable_results, f, indent=2)
    
    print("\n📁 Audit results saved to /tmp/tool_interface_audit.json")