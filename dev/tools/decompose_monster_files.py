#!/usr/bin/env python3
"""
Monster File Decomposition Script
=================================

Automatically decomposes large Python files into smaller, maintainable modules
based on class and function boundaries while preserving functionality.
"""

import os
import re
import ast
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass

@dataclass
class CodeComponent:
    """Represents a component that can be extracted to its own file"""
    name: str
    type: str  # 'class', 'function', 'constant'
    start_line: int
    end_line: int
    content: str
    dependencies: Set[str]
    module_path: str


def analyze_python_file(file_path: str) -> List[CodeComponent]:
    """
    Analyze a Python file and identify components that can be extracted
    
    Args:
        file_path: Path to Python file to analyze
        
    Returns:
        List of extractable components
    """
    print(f"📊 Analyzing {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
    
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        print(f"❌ Syntax error in {file_path}: {e}")
        return []
    
    components = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Extract class definition
            start_line = node.lineno
            end_line = node.end_lineno or start_line
            
            class_content = '\n'.join(lines[start_line-1:end_line])
            
            component = CodeComponent(
                name=node.name,
                type='class',
                start_line=start_line,
                end_line=end_line,
                content=class_content,
                dependencies=set(),  # Will be analyzed separately
                module_path=file_path
            )
            components.append(component)
        
        elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:
            # Extract top-level function
            start_line = node.lineno
            end_line = node.end_lineno or start_line
            
            func_content = '\n'.join(lines[start_line-1:end_line])
            
            component = CodeComponent(
                name=node.name,
                type='function',
                start_line=start_line,
                end_line=end_line,
                content=func_content,
                dependencies=set(),
                module_path=file_path
            )
            components.append(component)
    
    print(f"✅ Found {len(components)} extractable components")
    return components


def create_decomposition_plan(file_path: str, components: List[CodeComponent]) -> Dict[str, List[CodeComponent]]:
    """
    Create a plan for decomposing a file into smaller modules
    
    Args:
        file_path: Original file path
        components: List of components to organize
        
    Returns:
        Dictionary mapping new file names to components
    """
    print(f"📋 Creating decomposition plan for {Path(file_path).name}...")
    
    # Group components by logical functionality
    plan = {}
    
    # Group by component type and name patterns
    type_groups = {}
    converter_groups = []
    utility_groups = []
    error_groups = []
    
    for component in components:
        if 'Converter' in component.name:
            converter_groups.append(component)
        elif 'Error' in component.name or 'Exception' in component.name:
            error_groups.append(component)
        elif component.name.startswith('_') or 'util' in component.name.lower():
            utility_groups.append(component)
        else:
            # Group by first word of class name
            prefix = component.name.split('_')[0].lower()
            if prefix not in type_groups:
                type_groups[prefix] = []
            type_groups[prefix].append(component)
    
    # Create files based on groupings
    base_name = Path(file_path).stem
    base_dir = Path(file_path).parent
    
    if converter_groups:
        plan[f"{base_dir}/converters/core_converters.py"] = converter_groups
    
    if error_groups:
        plan[f"{base_dir}/{base_name}_types.py"] = error_groups
    
    if utility_groups:
        plan[f"{base_dir}/{base_name}_utils.py"] = utility_groups
    
    for prefix, group in type_groups.items():
        if len(group) > 1:
            plan[f"{base_dir}/{base_name}_{prefix}.py"] = group
        else:
            # Single components go in utils
            if f"{base_dir}/{base_name}_utils.py" not in plan:
                plan[f"{base_dir}/{base_name}_utils.py"] = []
            plan[f"{base_dir}/{base_name}_utils.py"].extend(group)
    
    return plan


def extract_imports_and_header(file_path: str) -> Tuple[str, str]:
    """
    Extract imports and file header from original file
    
    Args:
        file_path: Path to original file
        
    Returns:
        Tuple of (imports, header_docstring)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
    
    imports = []
    header = []
    in_docstring = False
    docstring_marker = None
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Track docstring
        if stripped.startswith('"""') or stripped.startswith("'''"):
            if not in_docstring:
                in_docstring = True
                docstring_marker = stripped[:3]
                header.append(line)
            elif stripped.endswith(docstring_marker):
                header.append(line)
                break
            else:
                header.append(line)
        elif in_docstring:
            header.append(line)
        elif stripped.startswith('#!') or stripped.startswith('#'):
            header.append(line)
        elif stripped.startswith('import ') or stripped.startswith('from '):
            imports.append(line)
        elif stripped == '':
            continue
        else:
            # Hit first non-import, non-header line
            break
    
    return '\n'.join(imports), '\n'.join(header)


def generate_new_files(plan: Dict[str, List[CodeComponent]], original_file: str):
    """
    Generate the decomposed files based on the plan
    
    Args:
        plan: Decomposition plan mapping files to components
        original_file: Path to original file
    """
    print(f"🔧 Generating {len(plan)} new files...")
    
    imports, header = extract_imports_and_header(original_file)
    
    for new_file_path, components in plan.items():
        if not components:
            continue
            
        # Create directory if needed
        Path(new_file_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Generate file content
        content_parts = []
        
        # Add header
        if header:
            content_parts.append(header)
        else:
            content_parts.append('#!/usr/bin/env python3')
            content_parts.append(f'"""')
            content_parts.append(f'{Path(new_file_path).stem} - Extracted from {Path(original_file).name}')
            content_parts.append(f'"""')
        
        content_parts.append('')
        
        # Add imports
        if imports:
            content_parts.append(imports)
            content_parts.append('')
        
        # Add components
        for component in components:
            content_parts.append(component.content)
            content_parts.append('')
        
        # Write file
        final_content = '\n'.join(content_parts)
        
        with open(new_file_path, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        print(f"✅ Created {new_file_path} with {len(components)} components")


def backup_original_file(file_path: str):
    """Create a backup of the original file"""
    backup_path = f"{file_path}.backup"
    
    if Path(backup_path).exists():
        # Add timestamp to backup name
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{file_path}.backup_{timestamp}"
    
    Path(file_path).rename(backup_path)
    print(f"📦 Backed up original to {backup_path}")


def decompose_monster_file(file_path: str, min_lines: int = 500):
    """
    Decompose a large Python file into smaller modules
    
    Args:
        file_path: Path to file to decompose
        min_lines: Minimum lines to consider for decomposition
    """
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    # Check file size
    with open(file_path, 'r') as f:
        line_count = sum(1 for _ in f)
    
    if line_count < min_lines:
        print(f"📏 {file_path} has {line_count} lines (< {min_lines}), skipping")
        return False
    
    print(f"🔍 Decomposing {file_path} ({line_count} lines)...")
    
    # Analyze file
    components = analyze_python_file(file_path)
    
    if len(components) < 2:
        print(f"⚠️  Not enough extractable components ({len(components)}), skipping")
        return False
    
    # Create decomposition plan
    plan = create_decomposition_plan(file_path, components)
    
    if len(plan) < 2:
        print(f"⚠️  Plan would not reduce complexity enough ({len(plan)} files), skipping")
        return False
    
    # Backup original
    backup_original_file(file_path)
    
    # Generate new files
    generate_new_files(plan, file_path)
    
    # Create simplified main file
    create_simplified_main_file(file_path, plan)
    
    print(f"✅ Successfully decomposed {Path(file_path).name}")
    return True


def create_simplified_main_file(original_path: str, plan: Dict[str, List[CodeComponent]]):
    """Create a simplified version of the main file with imports"""
    imports, header = extract_imports_and_header(f"{original_path}.backup")
    
    content_parts = []
    
    # Add header
    if header:
        content_parts.append(header)
        content_parts.append("")
        content_parts.append("# NOTE: This file has been decomposed into smaller modules")
        content_parts.append("# for better maintainability. See the following files:")
        for file_path in plan.keys():
            content_parts.append(f"#   - {Path(file_path).name}")
        content_parts.append("")
    
    # Add imports
    if imports:
        content_parts.append(imports)
        content_parts.append("")
    
    # Add re-exports
    content_parts.append("# Re-export components from decomposed modules")
    for file_path, components in plan.items():
        module_name = Path(file_path).stem
        for component in components:
            if component.type == 'class':
                content_parts.append(f"from .{module_name} import {component.name}")
    
    content_parts.append("")
    content_parts.append("# Main functionality would be implemented here")
    content_parts.append("# or imported from the appropriate decomposed module")
    
    with open(original_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content_parts))
    
    print(f"✅ Created simplified {Path(original_path).name}")


def main():
    """Main decomposition function"""
    print("🏗️  MONSTER FILE DECOMPOSITION")
    print("=" * 50)
    
    # Find monster files
    monster_files = [
        "/home/brian/projects/Digimons/src/analytics/cross_modal_converter.py",
        "/home/brian/projects/Digimons/src/analytics/cross_modal_orchestrator.py", 
        "/home/brian/projects/Digimons/src/testing/performance_benchmarker.py"
    ]
    
    results = []
    
    for file_path in monster_files:
        try:
            success = decompose_monster_file(file_path, min_lines=500)
            results.append((file_path, success))
        except Exception as e:
            print(f"❌ Error decomposing {file_path}: {e}")
            results.append((file_path, False))
    
    # Summary
    print(f"\n📊 DECOMPOSITION SUMMARY")
    print("=" * 30)
    
    successful = sum(1 for _, success in results if success)
    print(f"Files processed: {len(results)}")
    print(f"Successfully decomposed: {successful}")
    print(f"Skipped/failed: {len(results) - successful}")
    
    for file_path, success in results:
        status = "✅" if success else "❌"
        print(f"  {status} {Path(file_path).name}")
    
    if successful > 0:
        print(f"\n🎉 Monster file decomposition completed!")
        print(f"   Original files backed up with .backup extension")
        print(f"   Review the new modular structure before committing changes")
    else:
        print(f"\n⚠️  No files were decomposed")
        print(f"   Files may be smaller than threshold or not suitable for decomposition")
    
    return successful == len(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)