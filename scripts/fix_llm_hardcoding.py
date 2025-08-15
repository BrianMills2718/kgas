#!/usr/bin/env python3
"""
Systematic LLM Model Hardcoding Fix Script

This script automatically fixes hardcoded LLM models across the codebase
by replacing them with calls to the standard config system.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def find_files_with_llm_hardcoding() -> List[str]:
    """Find all Python files with LLM model hardcoding"""
    llm_files = []
    
    # Read from the generated inventory
    with open('/tmp/llm_hardcoding.txt', 'r') as f:
        for line in f:
            if line.strip():
                file_path = line.split(':')[0]
                if file_path not in llm_files:
                    llm_files.append(file_path)
    
    return llm_files

def analyze_file_patterns(file_path: str) -> Dict[str, List[str]]:
    """Analyze hardcoding patterns in a file"""
    patterns = {
        'function_defaults': [],  # def func(model="gpt-4"):
        'assignment_statements': [],  # self.model = "gpt-4"
        'api_calls': [],  # api.call(model="gpt-4")
        'method_calls': []  # method(model="gpt-4")
    }
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            lines = content.split('\n')
            
        for i, line in enumerate(lines):
            line_num = i + 1
            
            # Function parameter defaults
            if re.search(r'def.*model.*=.*["\'](?:gpt|claude|gemini)', line):
                patterns['function_defaults'].append(f"{line_num}: {line.strip()}")
                
            # Assignment statements
            elif re.search(r'model\s*=\s*["\'](?:gpt|claude|gemini)', line):
                patterns['assignment_statements'].append(f"{line_num}: {line.strip()}")
                
            # API calls with model parameter
            elif re.search(r'model\s*=\s*["\'](?:gpt|claude|gemini)', line) and '(' in line:
                patterns['api_calls'].append(f"{line_num}: {line.strip()}")
                
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
        
    return patterns

def fix_function_defaults(file_path: str) -> bool:
    """Fix function parameter defaults"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Pattern: def func(model: str = "gpt-4"):
        # Replace with: def func(model: Optional[str] = None):
        pattern = r'(def\s+\w+\([^)]*model:\s*str\s*=\s*)["\'](?:gpt|claude|gemini)[^"\']*["\']'
        replacement = r'\1None'
        
        new_content = re.sub(pattern, replacement, content)
        
        # Also fix without type hints
        pattern2 = r'(def\s+\w+\([^)]*model\s*=\s*)["\'](?:gpt|claude|gemini)[^"\']*["\']'
        replacement2 = r'\1None'
        
        new_content = re.sub(pattern2, replacement2, new_content)
        
        if new_content != content:
            # Add Optional import if needed
            if 'from typing import' in new_content and 'Optional' not in new_content:
                new_content = new_content.replace(
                    'from typing import',
                    'from typing import Optional,'
                )
            elif 'Optional' not in new_content:
                # Add import at top
                import_line = "from typing import Optional\n"
                lines = new_content.split('\n')
                
                # Find where to insert import
                insert_pos = 0
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        insert_pos = i + 1
                    elif line.strip() and not line.startswith('#'):
                        break
                
                lines.insert(insert_pos, import_line)
                new_content = '\n'.join(lines)
            
            with open(file_path, 'w') as f:
                f.write(new_content)
            return True
            
    except Exception as e:
        print(f"Error fixing function defaults in {file_path}: {e}")
        
    return False

def add_config_import_and_helper(file_path: str) -> bool:
    """Add standard config import and helper method"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Check if already has the import
        if 'from src.core.standard_config import get_model' in content:
            return False
            
        # Add import
        import_line = "from src.core.standard_config import get_model"
        
        lines = content.split('\n')
        
        # Find where to insert import (after other imports)
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                insert_pos = i + 1
            elif line.strip() and not line.startswith('#'):
                break
        
        lines.insert(insert_pos, import_line)
        
        # Find class definition and add helper method
        class_found = False
        for i, line in enumerate(lines):
            if re.match(r'class\s+\w+', line):
                class_found = True
                # Find __init__ method
                for j in range(i, min(i + 50, len(lines))):
                    if 'def __init__' in lines[j]:
                        # Find end of __init__ method
                        for k in range(j, min(j + 50, len(lines))):
                            if lines[k].strip() and not lines[k].startswith(' ') and k > j:
                                # Insert helper method before next method
                                helper_method = [
                                    "    def _get_default_model(self) -> str:",
                                    "        \"\"\"Get default model from standard config\"\"\"",
                                    "        return get_model()",
                                    ""
                                ]
                                for idx, helper_line in enumerate(helper_method):
                                    lines.insert(k + idx, helper_line)
                                break
                        break
                break
        
        if class_found:
            new_content = '\n'.join(lines)
            with open(file_path, 'w') as f:
                f.write(new_content)
            return True
            
    except Exception as e:
        print(f"Error adding config import to {file_path}: {e}")
        
    return False

def fix_hardcoded_assignments(file_path: str) -> bool:
    """Fix hardcoded model assignments"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Pattern: self.model = "gpt-4"
        # Replace with: self.model = self._get_default_model() if model is None else model
        # But need to handle context
        
        new_content = content
        
        # Simple replacements for common patterns
        patterns = [
            (r'model\s*=\s*"gpt-4[^"]*"', 'model = self._get_default_model()'),
            (r'model\s*=\s*"claude-[^"]*"', 'model = self._get_default_model()'),
            (r'model\s*=\s*"gemini-[^"]*"', 'model = self._get_default_model()'),
        ]
        
        for pattern, replacement in patterns:
            new_content = re.sub(pattern, replacement, new_content)
        
        if new_content != content:
            with open(file_path, 'w') as f:
                f.write(new_content)
            return True
            
    except Exception as e:
        print(f"Error fixing assignments in {file_path}: {e}")
        
    return False

def fix_single_file(file_path: str) -> Dict[str, bool]:
    """Fix a single file systematically"""
    print(f"\n🔧 Fixing {file_path}")
    
    results = {
        'config_import_added': False,
        'function_defaults_fixed': False,
        'assignments_fixed': False
    }
    
    # Analyze patterns first
    patterns = analyze_file_patterns(file_path)
    
    # Show what we found
    for pattern_type, occurrences in patterns.items():
        if occurrences:
            print(f"  Found {len(occurrences)} {pattern_type}")
    
    # Apply fixes
    results['config_import_added'] = add_config_import_and_helper(file_path)
    results['function_defaults_fixed'] = fix_function_defaults(file_path)
    results['assignments_fixed'] = fix_hardcoded_assignments(file_path)
    
    return results

def main():
    """Main execution"""
    print("🚀 Starting systematic LLM hardcoding fix")
    
    # Find files with hardcoding
    files_to_fix = find_files_with_llm_hardcoding()
    print(f"Found {len(files_to_fix)} files with LLM hardcoding")
    
    # Process priority files first (core modules)
    priority_files = [f for f in files_to_fix if '/core/' in f or '/theory_to_code/' in f]
    other_files = [f for f in files_to_fix if f not in priority_files]
    
    total_fixed = 0
    
    print(f"\n📋 Processing {len(priority_files)} priority files first")
    for file_path in priority_files:
        if os.path.exists(file_path):
            results = fix_single_file(file_path)
            if any(results.values()):
                total_fixed += 1
                print(f"  ✅ Fixed: {results}")
            else:
                print(f"  ⏭️  No changes needed")
    
    print(f"\n📋 Processing {len(other_files)} other files")
    for file_path in other_files[:10]:  # Limit to first 10 for testing
        if os.path.exists(file_path):
            results = fix_single_file(file_path)
            if any(results.values()):
                total_fixed += 1
                print(f"  ✅ Fixed: {results}")
            else:
                print(f"  ⏭️  No changes needed")
    
    print(f"\n🎉 Systematic fix complete!")
    print(f"   Files processed: {len(priority_files) + min(10, len(other_files))}")
    print(f"   Files modified: {total_fixed}")
    
    # Verify fixes
    print(f"\n🔍 Verifying fixes...")
    remaining_hardcoding = os.system("grep -r --include='*.py' -n 'model.*=' src/ | grep -E '(gpt|claude|gemini)' | grep -v -E '(test|example|verify_model)' | wc -l")
    
if __name__ == "__main__":
    main()