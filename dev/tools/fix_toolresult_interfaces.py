#!/usr/bin/env python3
"""
Fix ToolResult Interface Violations

Automatically fixes the 53 ToolResult interface violations by:
1. Replacing ToolResult(success=...) with ToolResult(status="success"|"error")
2. Replacing ToolResult(error=...) with ToolResult(error_message=...)
3. Ensuring proper interface compliance
"""

import sys
import re
from pathlib import Path
from typing import List, Dict, Any
import ast

sys.path.append('src')

def find_tool_files() -> List[Path]:
    """Find all tool Python files that need fixing"""
    tool_files = []
    
    # Phase 1 tools
    phase1_dir = Path("src/tools/phase1")
    if phase1_dir.exists():
        tool_files.extend(phase1_dir.glob("t*.py"))
    
    # Phase 2 tools  
    phase2_dir = Path("src/tools/phase2")
    if phase2_dir.exists():
        tool_files.extend(phase2_dir.glob("t*.py"))
    
    # Phase 3 tools
    phase3_dir = Path("src/tools/phase3")
    if phase3_dir.exists():
        tool_files.extend(phase3_dir.glob("t*.py"))
    
    return tool_files

def fix_toolresult_interface(file_path: Path) -> Dict[str, Any]:
    """Fix ToolResult interface in a single file"""
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        original_content = content
        fixes_applied = []
        
        # Pattern 1: ToolResult(success=True, ...) -> ToolResult(status="success", ...)
        success_pattern = r'ToolResult\(\s*success\s*=\s*True\s*,\s*([^)]*)\)'
        def replace_success_true(match):
            other_params = match.group(1).strip()
            if other_params and not other_params.endswith(','):
                other_params = other_params + ','
            fixes_applied.append("ToolResult(success=True, ...) -> ToolResult(status=\"success\", ...)")
            return f'ToolResult(status="success", {other_params})'
        
        content = re.sub(success_pattern, replace_success_true, content)
        
        # Pattern 2: ToolResult(success=False, ...) -> ToolResult(status="error", ...)
        fail_pattern = r'ToolResult\(\s*success\s*=\s*False\s*,\s*([^)]*)\)'
        def replace_success_false(match):
            other_params = match.group(1).strip()
            if other_params and not other_params.endswith(','):
                other_params = other_params + ','
            fixes_applied.append("ToolResult(success=False, ...) -> ToolResult(status=\"error\", ...)")
            return f'ToolResult(status="error", {other_params})'
        
        content = re.sub(fail_pattern, replace_success_false, content)
        
        # Pattern 3: Replace error= with error_message=
        error_param_pattern = r'(\bToolResult\([^)]*)\berror\s*=\s*([^,)]+)([^)]*\))'
        def replace_error_param(match):
            before = match.group(1)
            error_value = match.group(2)
            after = match.group(3)
            fixes_applied.append("error=... -> error_message=...")
            return f'{before}error_message={error_value}{after}'
        
        content = re.sub(error_param_pattern, replace_error_param, content)
        
        # Pattern 4: Handle cases where success parameter exists without True/False
        success_var_pattern = r'ToolResult\(\s*success\s*=\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*,\s*([^)]*)\)'
        def replace_success_var(match):
            success_var = match.group(1)
            other_params = match.group(2).strip()
            if other_params and not other_params.endswith(','):
                other_params = other_params + ','
            fixes_applied.append(f"ToolResult(success={success_var}, ...) -> ToolResult(status=\"success\" if {success_var} else \"error\", ...)")
            return f'ToolResult(status="success" if {success_var} else "error", {other_params})'
        
        content = re.sub(success_var_pattern, replace_success_var, content)
        
        # Write back if changes were made
        if content != original_content:
            with open(file_path, 'w') as f:
                f.write(content)
            
            return {
                'file': file_path,
                'fixed': True,
                'fixes_applied': fixes_applied,
                'lines_changed': len(content.splitlines()) - len(original_content.splitlines())
            }
        else:
            return {
                'file': file_path,
                'fixed': False,
                'fixes_applied': [],
                'lines_changed': 0
            }
    
    except Exception as e:
        return {
            'file': file_path,
            'fixed': False,
            'fixes_applied': [],
            'lines_changed': 0,
            'error': str(e)
        }

def validate_fixes() -> bool:
    """Run validation to ensure fixes worked"""
    try:
        # Import and run the validation tool
        from validate_tool_interfaces import main as validate_main
        return validate_main()
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False

def main():
    """Main fixing function"""
    print("🔧 FIXING TOOLRESULT INTERFACE VIOLATIONS")
    print("=" * 80)
    
    # Find all tool files
    tool_files = find_tool_files()
    print(f"📁 Found {len(tool_files)} tool files to fix")
    print()
    
    # Fix each file
    total_fixes = 0
    files_fixed = 0
    all_results = []
    
    for tool_file in tool_files:
        print(f"🔧 Fixing {tool_file}...")
        result = fix_toolresult_interface(tool_file)
        all_results.append(result)
        
        if result['fixed']:
            files_fixed += 1
            total_fixes += len(result['fixes_applied'])
            print(f"   ✅ {len(result['fixes_applied'])} fixes applied:")
            for fix in result['fixes_applied']:
                print(f"      • {fix}")
        elif 'error' in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   ℹ️ No fixes needed")
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 FIXING SUMMARY")
    print("=" * 80)
    print(f"Files processed: {len(tool_files)}")
    print(f"Files fixed: {files_fixed}")
    print(f"Total fixes applied: {total_fixes}")
    
    if total_fixes > 0:
        print(f"\n🔧 FIXES APPLIED:")
        fix_counts = {}
        for result in all_results:
            for fix in result.get('fixes_applied', []):
                fix_counts[fix] = fix_counts.get(fix, 0) + 1
        
        for fix_type, count in fix_counts.items():
            print(f"  • {fix_type}: {count} times")
    
    print(f"\n🧪 RUNNING VALIDATION...")
    validation_passed = validate_fixes()
    
    if validation_passed:
        print(f"🎉 ALL FIXES SUCCESSFUL! Interface violations resolved.")
        return True
    else:
        print(f"⚠️ Some validation issues remain. Check validate_tool_interfaces.py output.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)