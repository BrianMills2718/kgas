#!/usr/bin/env python3
"""
Fix Remaining ToolResult Interface Violations

Handles the remaining ToolResult(success=...) patterns that the first script missed.
"""

import sys
import re
from pathlib import Path
from typing import List, Dict, Any

def find_files_with_issues() -> List[Path]:
    """Find files that still have ToolResult interface issues"""
    files_with_issues = [
        "src/tools/phase2/t56_graph_metrics.py",
        "src/tools/phase2/t50_community_detection.py", 
        "src/tools/phase2/t53_network_motifs.py",
        "src/tools/phase2/t52_graph_clustering.py",
        "src/tools/phase2/t51_centrality_analysis.py",
        "src/tools/phase2/t57_path_analysis.py",
        "src/tools/phase2/t54_graph_visualization.py",
        "src/tools/phase2/t55_temporal_analysis.py"
    ]
    
    return [Path(f) for f in files_with_issues if Path(f).exists()]

def advanced_fix_toolresult(file_path: Path) -> Dict[str, Any]:
    """Advanced fixing of ToolResult interface issues"""
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        original_content = content
        fixes_applied = []
        
        # More comprehensive patterns for ToolResult(success=...)
        
        # Pattern 1: ToolResult(success=True/False with line breaks and spacing
        success_multiline_pattern = r'ToolResult\(\s*success\s*=\s*(True|False)\s*,([^)]*)\)'
        def replace_success_multiline(match):
            success_val = match.group(1)
            other_params = match.group(2).strip()
            status = "success" if success_val == "True" else "error"
            fixes_applied.append(f"ToolResult(success={success_val}, ...) -> ToolResult(status=\"{status}\", ...)")
            return f'ToolResult(status="{status}",{other_params})'
        
        content = re.sub(success_multiline_pattern, replace_success_multiline, content, flags=re.DOTALL)
        
        # Pattern 2: return ToolResult(success=... on multiple lines
        return_success_pattern = r'return\s+ToolResult\(\s*success\s*=\s*(True|False)\s*,([^)]*)\)'
        def replace_return_success(match):
            success_val = match.group(1)
            other_params = match.group(2).strip()
            status = "success" if success_val == "True" else "error"
            fixes_applied.append(f"return ToolResult(success={success_val}, ...) -> return ToolResult(status=\"{status}\", ...)")
            return f'return ToolResult(status="{status}",{other_params})'
        
        content = re.sub(return_success_pattern, replace_return_success, content, flags=re.DOTALL)
        
        # Pattern 3: Handle any remaining success= parameters
        remaining_success_pattern = r'(\w*ToolResult\([^)]*?)success\s*=\s*(True|False|[a-zA-Z_][a-zA-Z0-9_]*)\s*,?([^)]*?\))'
        def replace_remaining_success(match):
            before = match.group(1)
            success_val = match.group(2)
            after = match.group(3)
            
            if success_val in ["True", "False"]:
                status = "success" if success_val == "True" else "error"
                new_param = f'status="{status}"'
            else:
                new_param = f'status="success" if {success_val} else "error"'
            
            fixes_applied.append(f"success={success_val} -> {new_param}")
            
            # Clean up the before part and add the new parameter
            if before.endswith('('):
                return f'{before}{new_param}, {after}'
            else:
                return f'{before}, {new_param}, {after}'
        
        content = re.sub(remaining_success_pattern, replace_remaining_success, content, flags=re.DOTALL)
        
        # Clean up any double commas or spacing issues
        content = re.sub(r',\s*,', ',', content)
        content = re.sub(r'\(\s*,', '(', content)
        content = re.sub(r',\s*\)', ')', content)
        
        # Write back if changes were made
        if content != original_content:
            with open(file_path, 'w') as f:
                f.write(content)
            
            return {
                'file': file_path,
                'fixed': True,
                'fixes_applied': fixes_applied
            }
        else:
            return {
                'file': file_path,
                'fixed': False,
                'fixes_applied': []
            }
    
    except Exception as e:
        return {
            'file': file_path,
            'fixed': False,
            'fixes_applied': [],
            'error': str(e)
        }

def main():
    """Main fixing function"""
    print("🔧 FIXING REMAINING TOOLRESULT INTERFACE VIOLATIONS")
    print("=" * 80)
    
    # Find files with remaining issues
    problem_files = find_files_with_issues()
    print(f"📁 Found {len(problem_files)} files with remaining issues")
    print()
    
    # Fix each file
    total_fixes = 0
    files_fixed = 0
    
    for file_path in problem_files:
        print(f"🔧 Advanced fixing {file_path}...")
        result = advanced_fix_toolresult(file_path)
        
        if result['fixed']:
            files_fixed += 1
            total_fixes += len(result['fixes_applied'])
            print(f"   ✅ {len(result['fixes_applied'])} fixes applied:")
            for fix in result['fixes_applied']:
                print(f"      • {fix}")
        elif 'error' in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   ℹ️ No additional fixes needed")
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 ADVANCED FIXING SUMMARY")
    print("=" * 80)
    print(f"Files processed: {len(problem_files)}")
    print(f"Files fixed: {files_fixed}")
    print(f"Total fixes applied: {total_fixes}")
    
    print(f"\n🧪 RUNNING FINAL VALIDATION...")
    try:
        from validate_tool_interfaces import main as validate_main
        validation_passed = validate_main()
        
        if validation_passed:
            print(f"🎉 ALL INTERFACE VIOLATIONS FIXED!")
            return True
        else:
            print(f"⚠️ Some issues remain - manual inspection needed.")
            return False
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)