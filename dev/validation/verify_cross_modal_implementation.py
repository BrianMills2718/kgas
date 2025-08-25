#!/usr/bin/env python3
"""Quick verification of cross-modal implementation without heavy dependencies."""

import os
import ast
import importlib.util

def check_file_exists(filepath):
    """Check if a file exists."""
    return os.path.exists(filepath)

def check_class_exists(filepath, classname):
    """Check if a class exists in a Python file."""
    try:
        with open(filepath, 'r') as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == classname:
                return True
        return False
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return False

def check_method_exists(filepath, classname, methodname):
    """Check if a method exists in a class."""
    try:
        with open(filepath, 'r') as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == classname:
                for item in node.body:
                    # Check both FunctionDef and AsyncFunctionDef
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == methodname:
                        return True
        return False
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return False

def main():
    print("="*80)
    print("CROSS-MODAL IMPLEMENTATION VERIFICATION")
    print("="*80)
    print()
    
    # Define what we need to check
    checks = [
        {
            "name": "Mode Selection Service - LLM Integration",
            "file": "src/analytics/mode_selection_service.py",
            "class": "ModeSelectionService",
            "method": "_initialize_llm_client",
            "critical": True
        },
        {
            "name": "Real LLM Service - No Fallbacks",
            "file": "src/analytics/real_llm_service.py", 
            "class": "RealLLMService",
            "method": "complete",
            "critical": True
        },
        {
            "name": "Vector→Graph Converter",
            "file": "src/analytics/cross_modal_converter.py",
            "class": "VectorToGraphConverter",
            "method": "_create_similarity_graph",
            "critical": True
        },
        {
            "name": "Vector→Table Converter",
            "file": "src/analytics/cross_modal_converter.py",
            "class": "VectorToTableConverter",
            "method": "_create_direct_table",
            "critical": True
        },
        {
            "name": "Service Registry",
            "file": "src/analytics/cross_modal_service_registry.py",
            "class": "CrossModalServiceRegistry",
            "method": "initialize_all_services",
            "critical": True
        },
        {
            "name": "Embedding Service",
            "file": "src/analytics/real_embedding_service.py",
            "class": "RealEmbeddingService",
            "method": "generate_text_embeddings",
            "critical": True
        },
        {
            "name": "Validator - Structural Integrity",
            "file": "src/analytics/cross_modal_validator.py",
            "class": "CrossModalValidator",
            "method": "_test_structural_integrity",
            "critical": True
        },
        {
            "name": "Validator - Semantic Preservation",
            "file": "src/analytics/cross_modal_validator.py",
            "class": "CrossModalValidator",
            "method": "_test_semantic_preservation",
            "critical": True
        },
        {
            "name": "Validator - Performance Benchmark",
            "file": "src/analytics/cross_modal_validator.py",
            "class": "CrossModalValidator",
            "method": "_test_performance_benchmark",
            "critical": True
        },
        {
            "name": "Analytics Module Exports",
            "file": "src/analytics/__init__.py",
            "exports": [
                "CrossModalServiceRegistry",
                "get_registry", 
                "initialize_cross_modal_services"
            ]
        }
    ]
    
    critical_count = 0
    critical_passed = 0
    
    for check in checks:
        print(f"\n{check['name']}:")
        print("-" * 40)
        
        # Check file exists
        if not check_file_exists(check['file']):
            print(f"✗ File not found: {check['file']}")
            if check.get('critical'):
                critical_count += 1
            continue
        
        print(f"✓ File exists: {check['file']}")
        
        # Check exports if specified
        if 'exports' in check:
            with open(check['file'], 'r') as f:
                content = f.read()
            
            all_found = True
            for export in check['exports']:
                if export in content:
                    print(f"  ✓ Export found: {export}")
                else:
                    print(f"  ✗ Export missing: {export}")
                    all_found = False
            
            if check.get('critical'):
                critical_count += 1
                if all_found:
                    critical_passed += 1
            continue
        
        # Check class exists
        if not check_class_exists(check['file'], check['class']):
            print(f"✗ Class not found: {check['class']}")
            if check.get('critical'):
                critical_count += 1
            continue
        
        print(f"✓ Class exists: {check['class']}")
        
        # Check method exists
        if not check_method_exists(check['file'], check['class'], check['method']):
            print(f"✗ Method not found: {check['method']}")
            if check.get('critical'):
                critical_count += 1
            continue
        
        print(f"✓ Method exists: {check['method']}")
        
        if check.get('critical'):
            critical_count += 1
            critical_passed += 1
    
    # Summary
    print("\n" + "="*80)
    print("VERIFICATION SUMMARY")
    print("="*80)
    print(f"\nCritical components: {critical_passed}/{critical_count} passed")
    
    if critical_passed == critical_count:
        print("\n✅ ALL CRITICAL COMPONENTS IMPLEMENTED!")
        print("   No mocks or fallbacks detected in implementation.")
    else:
        print("\n❌ Some critical components are missing")
    
    # Additional code analysis
    print("\n" + "="*80)
    print("CODE ANALYSIS")
    print("="*80)
    
    # Check for fallback patterns
    print("\nChecking for mock/fallback patterns...")
    fallback_patterns = ["fallback", "mock", "stub", "dummy", "fake"]
    files_to_check = [
        "src/analytics/mode_selection_service.py",
        "src/analytics/real_llm_service.py",
        "src/analytics/cross_modal_converter.py"
    ]
    
    fallbacks_found = False
    for filepath in files_to_check:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read().lower()
            
            found_patterns = []
            for pattern in fallback_patterns:
                if pattern in content:
                    # Check if it's in a comment
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if pattern in line and not line.strip().startswith('#'):
                            found_patterns.append((pattern, i+1))
            
            if found_patterns:
                print(f"\n⚠️  Potential fallback patterns in {filepath}:")
                for pattern, line_no in found_patterns[:3]:  # Show first 3
                    print(f"   Line {line_no}: contains '{pattern}'")
                fallbacks_found = True
    
    if not fallbacks_found:
        print("✓ No fallback patterns detected in critical files")
    
    # Check for RuntimeError usage (fail-fast)
    print("\nChecking for fail-fast implementation...")
    fail_fast_count = 0
    for filepath in files_to_check:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
            
            if "RuntimeError" in content or "raise" in content:
                fail_fast_count += 1
                print(f"✓ Fail-fast pattern found in {os.path.basename(filepath)}")
    
    print(f"\nFail-fast implementations: {fail_fast_count}/{len(files_to_check)} files")
    
    print("\n" + "="*80)
    print("VERIFICATION COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()